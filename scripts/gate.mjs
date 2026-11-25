/** Fail-closed checks before any OIDC request. Never prints API response bodies. */
const isRecord = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const validOwner = value => typeof value === 'string' && /^[a-z0-9](?:[a-z0-9-]{0,37}[a-z0-9])?$/i.test(value) && !value.includes('--');
const validReviewer = entry => {
  if (!isRecord(entry) || !isRecord(entry.reviewer) || !Number.isSafeInteger(entry.reviewer.id) || entry.reviewer.id <= 0) return false;
  if (entry.type === 'User') return validOwner(entry.reviewer.login);
  return entry.type === 'Team' && typeof entry.reviewer.slug === 'string' && /^[a-z0-9_-]+$/i.test(entry.reviewer.slug);
};
const productionEnvironments = new Set(['production-plan','production-apply','production-content','production-drift']);
function validateRepository(metadata,expectedRepository) {
  const expected=typeof expectedRepository==='string'?expectedRepository.split('/'):[];
  if (expected.length!==2 || !validOwner(expected[0]) || !/^[a-z0-9_.-]{1,100}$/i.test(expected[1]) || ['.','..'].includes(expected[1])
      || !isRecord(metadata) || !['id','name','full_name','owner'].every(key=>Object.hasOwn(metadata,key)) || !Number.isSafeInteger(metadata.id) || metadata.id<=0 || !isRecord(metadata.owner)
      || !['id','login','type'].every(key=>Object.hasOwn(metadata.owner,key)) || metadata.owner.type!=='User' || !Number.isSafeInteger(metadata.owner.id) || metadata.owner.id<=0 || !validOwner(metadata.owner.login)
      || typeof metadata.full_name!=='string' || metadata.full_name.toLowerCase()!==expectedRepository.toLowerCase()
      || typeof metadata.name!=='string' || metadata.name.toLowerCase()!==expected[1].toLowerCase()
      || metadata.owner.login.toLowerCase()!==expected[0].toLowerCase())
    throw new Error('Independent repository metadata must prove the exact personal User-owned repository');
  return metadata.owner;
}
export function verifyProtection(environment, policies, branch, repositoryMetadata, expectedRepository) {
  const owner=validateRepository(repositoryMetadata,expectedRepository);
  if (!isRecord(environment) || !isRecord(policies) || !isRecord(branch))
    throw new Error('Actual repository protection responses are required');
  const rules = environment.protection_rules;
  if (!Array.isArray(rules) || !rules.every(rule => isRecord(rule) && typeof rule.type === 'string'))
    throw new Error('Malformed environment protection rules');
  const reviewers = rules.filter(rule => rule.type === 'required_reviewers');
  const reviewer = reviewers[0];
  if (reviewers.length !== 1 || !Array.isArray(reviewer.reviewers) || reviewer.reviewers.length === 0 || !reviewer.reviewers.every(validReviewer)
      || reviewer.prevent_self_review !== false || environment.can_admins_bypass !== false)
    throw new Error('Required owner-eligible approval, self-approval permission and no administrator bypass are required');
  if (!reviewer.reviewers.some(entry => entry.type === 'User' && entry.reviewer.login.toLowerCase() === owner.login.toLowerCase() && entry.reviewer.id === owner.id))
    throw new Error('Repository owner must be an eligible environment reviewer');
  const policy = environment.deployment_branch_policy;
  if (!isRecord(policy) || policy.custom_branch_policies !== true || policy.protected_branches !== false)
    throw new Error('Environment must use an exact custom main branch policy');
  if (policies.total_count !== 1 || !Array.isArray(policies.branch_policies) || policies.branch_policies.length !== 1
      || !isRecord(policies.branch_policies[0]) || policies.branch_policies[0].name !== 'main' || policies.branch_policies[0].type !== 'branch')
    throw new Error('Environment must permit exactly main branch only, no tags');
  const pr = branch.required_pull_request_reviews;
  if (branch.enforce_admins?.enabled !== true || !isRecord(pr) || !Number.isInteger(pr.required_approving_review_count)
      || pr.required_approving_review_count !== 0 || typeof pr.dismiss_stale_reviews !== 'boolean'
      || pr.require_last_push_approval !== false || pr.require_code_owner_reviews !== false)
    throw new Error('main must require PRs with zero mandatory human approvals, no code-owner/last-push approval and enforced administrators');
  // Bypass actors are documented as organization-only. True field absence is
  // compatible only after independent metadata proves this personal User model.
  // https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
  if (!Object.hasOwn(pr,'bypass_pull_request_allowances') && 'bypass_pull_request_allowances' in pr)
    throw new Error('Inherited bypass fields are not a genuine API omission');
  if (Object.hasOwn(pr,'bypass_pull_request_allowances')) {
    const allowances=pr.bypass_pull_request_allowances;
    if (!isRecord(allowances) || Object.keys(allowances).length !== 3
        || !['users','teams','apps'].every(kind => Array.isArray(allowances[kind]) && allowances[kind].length === 0))
      throw new Error('Present PR bypass allowances must be explicitly empty for users, teams and apps');
  }
  if (!isRecord(branch.allow_force_pushes) || branch.allow_force_pushes.enabled !== false
      || !isRecord(branch.allow_deletions) || branch.allow_deletions.enabled !== false
      || !isRecord(branch.required_conversation_resolution) || branch.required_conversation_resolution.enabled !== true)
    throw new Error('Force pushes/deletions must be disabled and conversation resolution required');
  const statuses = branch.required_status_checks;
  if (!isRecord(statuses) || statuses.strict !== true || !Array.isArray(statuses.contexts)
      || !statuses.contexts.every(context => typeof context === 'string' && context.length > 0) || !statuses.contexts.includes('verify'))
    throw new Error('main must require strict verify status check');
}
export async function github(path) {
  const response = await fetch(`https://api.github.com/repos/${process.env.GITHUB_REPOSITORY}${path?'/'+path:''}`, {
    headers: {Authorization: `Bearer ${process.env.GH_PROTECTION_TOKEN}`, Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
  });
  if (!response.ok) throw new Error('Cannot prove repository protection: API access failed');
  return response.json();
}
async function verifyTrustedMain(envs) {
  if (process.env.GITHUB_REF !== 'refs/heads/main' || !/^[a-f0-9]{40}$/.test(process.env.GITHUB_SHA ?? ''))
    throw new Error('Revision is not trusted main');
  const repository = (process.env.GITHUB_REPOSITORY ?? '').split('/');
  if (repository.length !== 2 || !validOwner(repository[0]) || !/^[a-z0-9_.-]{1,100}$/i.test(repository[1]) || ['.','..'].includes(repository[1]))
    throw new Error('Exact valid repository owner/name required');
  if (!Array.isArray(envs) || envs.length === 0 || new Set(envs).size !== envs.length || !envs.every(env => productionEnvironments.has(env)))
    throw new Error('Explicit production environment protection checks required');
  if (!process.env.GH_PROTECTION_TOKEN) throw new Error('Missing read-only repository protection API token');
  const repositoryMetadata=await github('');
  validateRepository(repositoryMetadata,process.env.GITHUB_REPOSITORY);
  const head = await github('git/ref/heads/main');
  if (head.object.sha !== process.env.GITHUB_SHA) throw new Error('Workflow revision is no longer current main');
  const branch = await github('branches/main/protection');
  for (const env of envs) verifyProtection(await github(`environments/${env}`), await github(`environments/${env}/deployment-branch-policies`), branch, repositoryMetadata, process.env.GITHUB_REPOSITORY);
}
export async function gate(envs) {
  if (process.env.ALLOW_AWS_OPERATIONS !== 'true') throw new Error('Live operations disabled');
  const allowedEvent=process.env.GITHUB_EVENT_NAME==='workflow_dispatch'
    || (process.env.GITHUB_EVENT_NAME==='schedule' && Array.isArray(envs) && envs.length===1 && envs[0]==='production-drift');
  if (!allowedEvent) throw new Error('Operational execution requires its approved manual or drift-schedule event');
  await verifyTrustedMain(envs);
}
export async function preflight() {
  if (arguments.length!==0 || process.env.GITHUB_EVENT_NAME!=='workflow_dispatch') throw new Error('Read-only preflight requires a manual event');
  await verifyTrustedMain([...productionEnvironments]);
}
if (process.argv[1]?.endsWith('gate.mjs')) gate(process.argv.slice(2)).then(() => console.log('Protection and trusted revision verified')).catch(() => { console.error('Protection gate failed; no AWS access permitted'); process.exitCode = 1; });
