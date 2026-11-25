/** Fail-closed checks before any OIDC request. Never prints API response bodies. */
export function verifyProtection(environment, policies, branch) {
  const rules = environment.protection_rules ?? [];
  const reviewer = rules.find(r => r.type === 'required_reviewers');
  if (!reviewer?.reviewers?.length || reviewer.prevent_self_review !== true || environment.can_admins_bypass !== false)
    throw new Error('Required independent approval and no bypass must be enabled');
  const policy = environment.deployment_branch_policy;
  if (policy?.custom_branch_policies !== true || policy.protected_branches !== false)
    throw new Error('Environment must use an exact custom main branch policy');
  if (policies.branch_policies?.length !== 1 || policies.branch_policies[0].name !== 'main' || policies.branch_policies[0].type !== 'branch')
    throw new Error('Environment must permit main branch only, no tags');
  const pr = branch.required_pull_request_reviews;
  if (pr && Object.values(pr.bypass_pull_request_allowances ?? {}).some(v => v.length)) throw new Error('PR approval bypass allowances forbidden');
  if (branch.enforce_admins?.enabled !== true || !pr || !Number.isInteger(pr.required_approving_review_count) || pr.required_approving_review_count < 1 || pr.dismiss_stale_reviews !== true || pr.require_last_push_approval !== true)
    throw new Error('main requires independent current PR approval including administrators');
  if (branch.required_status_checks?.strict !== true || !(branch.required_status_checks.contexts ?? []).includes('verify'))
    throw new Error('main must require strict verify status check');
}
export async function github(path) {
  const response = await fetch(`https://api.github.com/repos/${process.env.GITHUB_REPOSITORY}/${path}`, {
    headers: {Authorization: `Bearer ${process.env.GH_PROTECTION_TOKEN}`, Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
  });
  if (!response.ok) throw new Error('Cannot prove repository protection: API access failed');
  return response.json();
}
export async function gate(envs) {
  if (process.env.ALLOW_AWS_OPERATIONS !== 'true' || process.env.GITHUB_REF !== 'refs/heads/main' || !/^[a-f0-9]{40}$/.test(process.env.GITHUB_SHA ?? ''))
    throw new Error('Live operations disabled or revision is not trusted main');
  if (!process.env.GH_PROTECTION_TOKEN) throw new Error('Missing read-only repository protection API token');
  const head = await github('git/ref/heads/main');
  if (head.object.sha !== process.env.GITHUB_SHA) throw new Error('Workflow revision is no longer current main');
  const branch = await github('branches/main/protection');
  for (const env of envs) verifyProtection(await github(`environments/${env}`), await github(`environments/${env}/deployment-branch-policies`), branch);
}
if (process.argv[1]?.endsWith('gate.mjs')) gate(process.argv.slice(2)).then(() => console.log('Protection and trusted revision verified')).catch(() => { console.error('Protection gate failed; no AWS access permitted'); process.exitCode = 1; });
