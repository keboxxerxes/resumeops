# Deployment and operations

**Immutable OIDC remediation; no account-side execution authorized.** Activation PR2 was merged. The first content run passed the repository protection gate but failed STS authentication before asset preparation/upload. The correction below changes source for the three existing role trust policies; it does not change deployed IAM, enable operations or retry content deployment. Bootstrap/site provisioning and recovery remain maintainer-reported progress. Obtain separate explicit approval before any account-side command or launching AWS CloudShell: launching CloudShell creates a compute environment. Verification GO is not deployment authority.

Terraform execution is Linux-first: GitHub-hosted Ubuntu is canonical for CI; one-time bootstrap may use an approved AWS CloudShell session or another trusted Linux amd64 host with the same pins. Native Windows Terraform is out of scope. Windows remains supported for website/VS Code/Codex work.

## Existing production: immutable OIDC trust correction

GitHub's [immutable subject reference](https://docs.github.com/en/actions/reference/security/oidc#immutable-subject-claims) documents the default for repositories created after July 15, 2026. ResumeOps accepts only `repo:OWNER@OWNER_ID/REPOSITORY@REPOSITORY_ID:environment:ENVIRONMENT`; names alone are not accepted. Required `repository_owner_id` and `repository_id` are canonical positive decimal strings, with no defaults. Terraform string inputs may coerce caller numbers to strings; quote IDs and preserve their exact metadata spelling. A valid-looking wrong ID will deny authentication, so syntactic validation never proves identity.

The following is a **future authorized human procedure**, not verification performed here. Do not edit IAM in the console, change GitHub OIDC settings, use `-target`, import/recreate roles, migrate state again or rerun bootstrap from empty local state to work around this defect.

1. Obtain approval for the exact reviewed remediation revision, existing bootstrap backend/state and three in-place trust-policy changes. Transfer only its Git archive to a trusted pinned Linux environment as described below. Use the existing short-lived federated operator identity with authorized bootstrap access, never GitHub OIDC to repair its own broken trust and never static credentials.
2. Privately verify `full_name`, `owner.login`, `owner.id` and `id` from `GET /repos/OWNER/REPOSITORY` (for example `gh api repos/OWNER/REPOSITORY --jq '{repository: .full_name, owner: .owner.login, repository_owner_id: (.owner.id|tostring), repository_id: (.id|tostring)}'` on the trusted operator terminal). Cross-check the exact names/IDs against the maintainer's private authenticated OIDC/CloudTrail evidence. Do not publish tokens, raw events or response dumps. Do not infer IDs from names, author IDs or an unrelated repository.
3. Add only the two verified quoted ID values to the **existing ignored private bootstrap variables**, using the updated [example](../infra/bootstrap/bootstrap.example.tfvars). Preserve the deployed name/region, provider ARN, distribution/OAC/header-policy bindings, budget recipient and all prior values. Do not overwrite the private configuration from the example. Preserve the existing ignored partial backend and backend file, the bootstrap key, encryption and native locking. Retain approved encrypted recovery copies; do not download state into public evidence.
4. Run the following only after the separate account-side authorization. Use a private terminal without log streaming, shell tracing or session capture; plan files/JSON contain sensitive values. Never upload them to GitHub.

```sh
set -euo pipefail
umask 077
mkdir -p .local
# Existing backend.tf must be present; never initialize empty local state.
test -f infra/bootstrap/backend.tf
test -f .local/bootstrap.s3.tfbackend
test -f .local/bootstrap.tfvars
terraform -chdir=infra/bootstrap init -input=false -lockfile=readonly -backend-config=../../.local/bootstrap.s3.tfbackend
terraform -chdir=infra/bootstrap validate -no-color
# Do not use -upgrade, -migrate-state, -reconfigure, -refresh=false, -lock=false or -target.
terraform -chdir=infra/bootstrap plan -input=false -lock-timeout=5m -var-file=../../.local/bootstrap.tfvars -out=../../.local/immutable-oidc.tfplan
terraform -chdir=infra/bootstrap show -json ../../.local/immutable-oidc.tfplan > .local/immutable-oidc.plan.json
```

Privately inspect the exact saved plan and JSON. It must show **0 to add, 3 to change, 0 to destroy**, with only `aws_iam_role.github["plan"]`, `aws_iam_role.github["apply"]` and `aws_iam_role.github["content"]` using `actions: ["update"]`; no replacement/import/move, output change, unknown trust values or other resource changes. Compare each role's before/after attributes: only `assume_role_policy` may change. Decode its JSON and verify only the legacy subject list becomes the exact immutable list below, keeping the original principal ARN, `Version`, `Effect`, `Action`, audience and `StringEquals` unchanged. Order-only JSON encoding differences are not permission changes. Existing role names/ARNs, inline policies, CloudFront bindings, state/budget/provider/resources must remain identical. An unexpected diff is **STOP/NO-GO**; investigate configuration/state drift rather than hiding it with targeting. No production plan was executed by this remediation, so the expected shape is not an observed result.

| Existing role | Only permitted immutable environment subjects |
|---|---|
| plan | `production-plan`, `production-drift` |
| apply | `production-apply` |
| content | `production-content` |

Each suffix is attached to the same exact `repo:OWNER@OWNER_ID/REPOSITORY@REPOSITORY_ID:environment:` prefix. No legacy subjects, wildcard, `StringLike`, alternate audience or additional provider is acceptable. Record a private digest of the reviewed saved plan and obtain explicit approval for **that file**. Only after separate IAM/apply authorization may the human run `terraform -chdir=infra/bootstrap apply ../../.local/immutable-oidc.tfplan`; this SDD execution does not perform it. No state editing or migration is required for in-place role trust updates.

After that separately authorized update, obtain a fresh bootstrap plan expecting no changes. Separately authorize protected main-only GitHub OIDC authentication checks for all four environments: plan/drift use the plan role, apply uses apply, content uses content. A mocked CI success is not proof of deployed trust or STS. Do not retry content/apply/destroy workflows just to test authentication: they have additional effects. A successful read-only identity check must not disclose account details. Keep the operations flag unchanged here; enabling it, content deployment, apply and teardown require their own decisions. Retain private sanitized outcomes and stop if any role can assume another role's environment.

## One-time bootstrap prerequisites

The human operator must approve the account, region, short-lived federated identity, IAM/bootstrap permissions, expected resources, cost estimate, exact source revision and private budget recipient. Use no long-lived AWS keys, repository credentials or shared terminal capture. CloudShell uses the console identity's existing credentials; do not run `aws configure` or copy credentials into files. Verify identity privately only after authorization. Check for a pre-existing GitHub OIDC provider; set private `existing_oidc_provider_arn` rather than changing/importing a shared provider silently.

Actual GitHub plan/protection availability is a release prerequisite. ResumeOps uses single-maintainer governance: require a pull request and successful strict `verify` CI before merging to main, including administrators; require zero human PR approvals. Preserve the non-null `required_pull_request_reviews` object with `required_approving_review_count: 0`, `require_last_push_approval: false`, `require_code_owner_reviews: false` and a boolean `dismiss_stale_reviews` value (`false` matches the configured zero-approval policy; `true` is also compatible). Keep `enforce_admins.enabled: true`, no PR bypass actors, strict required `verify` status, disabled force pushes/deletion and required conversation resolution. The gate checks required protection configuration; GitHub enforces the PR/CI merge rule. Do not replace the PR object with null or allow direct administrator bypass. Fetch repository metadata independently from the GitHub API and bind its full name, owner login/type and repository name to the requested repository. Only an actually absent `bypass_pull_request_allowances` property may be accepted for a verified personal (`owner.type: User`) repository, because bypass lists are organization-only. This is a narrow compatibility interpretation of documented feature availability, not a guarantee that every personal-repository response omits the field. The current gate supports only independently verified User ownership; Organization/unknown metadata is rejected even with empty allowances. If present, the field must contain exactly empty users/teams/apps arrays; null, malformed/nonempty values and omission for organization/unknown/unverified ownership fail closed. [Official bypass scope](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) and [REST review fields](https://docs.github.com/en/rest/branches/branch-protection) define the boundary.

Before operational workflows are separately authorized, configure all four exact production environments with required reviewers including the personal repository owner as a User, `prevent_self_review: false`, `can_admins_bypass: false`, and the exact custom branch policy `name: main`, `type: branch` only. Set `custom_branch_policies: true`, `protected_branches: false`; remove every tag policy and any additional/wildcard branch policy. The owner must explicitly use the protected-environment approval action; self-approval permission does not make approval automatic. The gate validates owner eligibility and these protections before requesting OIDC. Missing/invalid API fields or unavailable required-reviewer features fail closed. The user manually configured these four environments. Current read-only API checks observed owner review, self-review permitted, no administrator bypass and exactly main/no tags. The agent did not change settings; revalidate them before each future authorized operation. API configuration observation does not prove deployed OIDC/IAM behavior or authorize activation.

The owner may author the PR, merge it after CI succeeds, substantively review the exact private Terraform plan and approve their own protected apply deployment. Review the exact saved plan and its source/digest before explicitly approving the post-plan `production-apply` job; do not regenerate or approve a different plan. Encrypted same-run handoff, operation/freshness checks, typed destroy confirmation and all other controls remain. Independent AI SDD review verifies source/tests/evidence; it is not an independent human reviewer or separation of duties. Owner mistakes or account compromise can affect both change and approval, so this model accepts that residual risk. See [security](SECURITY.md).

GitHub documents [zero required PR reviewers](https://docs.github.com/en/rest/branches/branch-protection) and [environment self-review/reviewer policies](https://docs.github.com/en/rest/deployments/environments). Current API feature availability was observed; future account/plan support must still be rechecked before live release. Do not bypass unavailable protections.

### 1. Transfer only the approved source

Choose an immutable revision with current independently reviewed Ubuntu CI. On a trusted checkout, create a Git archive under ignored `.local/` (Git is supported on Windows). It contains tracked source, not local caches, credentials or Git metadata. Record the archive SHA256 in the private operator handoff, upload to the approved Linux session and compare SHA256 before extraction. Do not upload state, plans, raw diagnostics or a whole working directory. The archive and revision/hash record must correspond to the same approved commit. No GitHub token needs to be installed in CloudShell.

CloudShell home persistence is currently limited to 1 GB per region; the large provider and two roots can exceed it. Use a private scratch directory in `/tmp`, check free space and share only a verified provider cache. Do not automatically delete scratch state or rely on an ephemeral session as the only bootstrap-state copy.

```sh
set -euo pipefail
umask 077
test "$(uname -s)" = Linux
test "$(uname -m)" = x86_64
SESSION_ROOT=$(mktemp -d /tmp/resumeops-bootstrap.XXXXXX)
chmod 700 "$SESSION_ROOT"
mkdir -m 700 "$SESSION_ROOT/provider-cache" "$SESSION_ROOT/source"
export TF_PLUGIN_CACHE_DIR="$SESSION_ROOT/provider-cache"
```

Verify/extract the approved archive into `source`, then work there. Do not use `TF_PLUGIN_CACHE_MAY_BREAK_DEPENDENCY_LOCK_FILE`, development overrides or unverified packages. Do not share the cache with other users/untrusted jobs. Each root keeps its own `.terraform` data/backend configuration; never point both at a shared `TF_DATA_DIR`.

### 2. Verify the pinned Terraform binary

Use Terraform **1.17.2 linux_amd64** and provider **6.74.0**, preserving both lockfiles/all 17 hashes. Download the exact Terraform ZIP, `SHA256SUMS` and detached signature from the [official version directory](https://releases.hashicorp.com/terraform/1.17.2/). In a temporary private `GNUPGHOME`, import only the official release-signing public key. Independently confirm its full fingerprint using the current HashiCorp security/key-rotation notice before accepting it. Verify the signature, then exact ZIP checksum; stop on mismatch. Do not generate a new signing key, mark an unchecked key trusted, or disable TLS.

```sh
export GNUPGHOME="$SESSION_ROOT/gnupg"
mkdir -m 700 "$GNUPGHOME"
TF_RELEASE_URL=https://releases.hashicorp.com/terraform/1.17.2
for file in terraform_1.17.2_linux_amd64.zip terraform_1.17.2_SHA256SUMS terraform_1.17.2_SHA256SUMS.sig; do
  curl --fail --silent --show-error --location --output "$file" "$TF_RELEASE_URL/$file"
done
curl --fail --silent --show-error --location --output hashicorp-key.asc https://www.hashicorp.com/.well-known/pgp-key.txt
gpg --show-keys --with-fingerprint hashicorp-key.asc
# STOP: independently compare the full fingerprint with the approved current signer.
gpg --import hashicorp-key.asc
gpg --verify terraform_1.17.2_SHA256SUMS.sig terraform_1.17.2_SHA256SUMS
grep ' terraform_1.17.2_linux_amd64.zip$' terraform_1.17.2_SHA256SUMS | sha256sum --check --strict
unzip -j terraform_1.17.2_linux_amd64.zip terraform -d "$SESSION_ROOT/bin"
export PATH="$SESSION_ROOT/bin:$PATH"
terraform version
```

The operator must supply the authenticated key/files, not copy an unreviewed fingerprint from chat. [HashiCorp verification guidance](https://developer.hashicorp.com/well-architected-framework/verify-hashicorp-binary) describes the chain. Proceed only after exact version/architecture confirmation. Run backend-disabled readonly initialization and validation for both roots before planning; canonical CI runs these real checks on approved source. Do not regenerate locks to bypass an error.

### 3. Bootstrap separate state/IAM/budget

Create ignored private `.local/bootstrap.tfvars` from the [bootstrap example](../infra/bootstrap/bootstrap.example.tfvars). Choose a unique name and actual exact repository; supply verified quoted `repository_owner_id` and `repository_id` from that repository metadata, plus any existing OIDC ARN privately. Never commit account identifiers, role ARNs, backend details or recipient address. Read the budget email without echoing it or placing its value in history:

```sh
mkdir -p .local
read -rsp 'Private budget recipient: ' TF_VAR_alert_email
printf '\n'
export TF_VAR_alert_email
terraform -chdir=infra/bootstrap init -input=false -lockfile=readonly
terraform -chdir=infra/bootstrap plan -input=false -var-file=../../.local/bootstrap.tfvars -out=../../.local/bootstrap.tfplan
terraform -chdir=infra/bootstrap show ../../.local/bootstrap.tfplan
# STOP: human privately reviews this exact saved plan and authorizes IAM/resources/cost.
terraform -chdir=infra/bootstrap apply ../../.local/bootstrap.tfplan
```

These are future authorized-human instructions, not actions performed by this SDD execution. Treat plan/state/output as sensitive even when variables redact. The committed bootstrap root has no remote backend initially. Inspect any generated backend configuration in another operator checkout rather than accidentally using the wrong state.

Immediately preserve initial local state/backup in approved encrypted private recovery storage, before the ephemeral session can disappear. Then create ignored `infra/bootstrap/backend.tf` with a partial S3 backend. Build private `.local/bootstrap.s3.tfbackend` from the [backend example](../infra/bootstrap/bootstrap.s3.tfbackend.example): created state bucket, `bootstrap/terraform.tfstate`, correct region, encryption and `use_lockfile=true`.

```sh
terraform -chdir=infra/bootstrap init -migrate-state -lockfile=readonly -backend-config=../../.local/bootstrap.s3.tfbackend
```

Privately verify remote object/version and authorized lock contention/recovery before retiring local copies. Keep private bootstrap backend configuration for subsequent trusted Linux sessions; Git ignores it. State destruction protection, public blocks, encryption and versioning must stay intact.

### 4. First site creation and exact-ID rebinding

After separately approving site plan/cost, create private site variables/backend files from [production variables](../infra/site/production.example.tfvars) and the [backend example](../infra/site/production.s3.tfbackend.example). Site bucket must match the bootstrap name plus `-production`; state key is `site/production/terraform.tfstate`, distinct from bootstrap. No workspaces.

```sh
terraform -chdir=infra/site init -input=false -lockfile=readonly -backend-config=../../.local/production.s3.tfbackend
terraform -chdir=infra/site plan -input=false -var-file=../../.local/production.tfvars -out=../../.local/first-site.tfplan
terraform -chdir=infra/site show ../../.local/first-site.tfplan
# STOP: approve this exact private site plan before apply.
terraform -chdir=infra/site apply ../../.local/first-site.tfplan
```

The Linux operator creates CloudFront first because runtime wildcard creation/retag is deliberately absent. Privately obtain exact distribution/OAC/header IDs from state. Set `content_distribution_id`, `origin_access_control_id`, `response_headers_policy_id` in private bootstrap inputs; generate/review/apply a fresh exact bootstrap plan. Before rebinding, runtime scopes use nonmatching `NOTCONFIGURED` IDs. Replacement/recreation needs new authorization and rebinding.

### 5. Stop at the activation boundary

The current activation PR moves the three existing workflow definitions into `.github/workflows` with independent review and fresh CI; it does not merge or enable execution. Keep the operations flag disabled. After a separately approved merge, verify the restricted token through the protected preflight below before seeking authority to enable any operational job. Only then may scoped environment configuration and exact OIDC roles be enabled; never static AWS keys. Hold the same random protected AES-GCM handoff key separately from ciphertext artifacts. Recipient email remains private state data. Public repository/content publication needs another approval.

## Future separately authorized operations

Infrastructure: current reviewed main, real protection API checks before OIDC, fresh private binary plan, authenticated ciphertext only, substantive private review/digest comparison before post-plan protected approval, same-run/SHA/operation/digest/24-hour age checks and exact reviewed apply. A digest alone is not plan review. Non-cancelling `resumeops-production` concurrency covers infrastructure/content/drift/destroy; operators coordinate local sessions and native state locks too.

Rollback: approve exact main-ancestor content SHA; run current trusted tooling; extract only regular allowlisted assets; regenerate metadata; upload explicit types/cache settings; invalidate `/`, `/index.html`, `/styles.css`, `/app.js`, `/deployment.json`; wait and verify HTTPS/headers/revision. Never execute historical runner scripts. Non-atomic uploads require deliberate recovery after smoke failure.

Drift: scheduled/manual read-only plan role, Terraform 0 = no drift, 2 = drift requiring review, 1/other = error; never apply. Tests use only a synthetic shell function, no real infrastructure plan.

Teardown: separate human authorization, exact typed `DESTROY production SITE ONLY`, protected post-plan approval, shared concurrency and site-only root. Versioned site `force_destroy=false` rejects nonempty deletion; separately authorize review/removal of only its exact object versions/delete markers if required. Dependencies remove CloudFront before origin. Retain bootstrap/state/roles/budget unless separately authorized; preserve recovery evidence first. Do not remove a shared OIDC provider.

Recovery: disable operations, coordinate operators, confirm no active lock, preserve current state privately, restore only an explicitly approved prior version and inspect a fresh private plan before apply. Never force-unlock without investigating ownership or restore state blindly. Never erase the only state copy when cleaning scratch files.

## Cost and outstanding prerequisites

Target below USD 1/month at low traffic, not a guarantee. The 2026-11-25 illustrative estimate was USD 0.1063 before allowances/state/tax: 0.1 GB S3 at USD 0.023/GB-month; 1,000 PUTs at USD 0.005/1,000; 10,000 GETs at USD 0.004/10,000; 1 GB North American CloudFront at USD 0.085/GB; 10,000 HTTPS requests at USD 0.0100/10,000. Recheck [S3](https://aws.amazon.com/s3/pricing/), [CloudFront pay-as-you-go](https://aws.amazon.com/cloudfront/pricing/pay-as-you-go/) and [Budgets](https://aws.amazon.com/aws-cost-management/aws-budgets/pricing/) before authorization. Flat-rate plans and account-specific allowances are distinct. GitHub plan/runner eligibility is separate from AWS operating cost.

The account-wide USD 5 monthly budget defines private ACTUAL USD 1/3/5 alerts. Other account spend counts; delayed alerts never cap charges. Verify recipient/delivery live. Bounded versions, limited invalidations and no unnecessary compute/domain/customer-key resources preserve the small design.

Outstanding: explicit AWS/IAM/cost/recipient authority; approved short-lived operator/trusted Linux session; source/signing-key verification; actual account/region/provider ownership; private recovery storage; GitHub protection availability; real OIDC denials/least privilege, lock/recovery, origin privacy, HTTPS/deploy/metadata, drift, rollback, alerts and authorized temporary teardown. These are **NOT RUN**. [CloudShell identity/storage](https://docs.aws.amazon.com/cloudshell/latest/userguide/welcome.html) and [security](https://docs.aws.amazon.com/cloudshell/latest/userguide/security.html) were consulted; the agent did not launch CloudShell.

## Protected GitHub-only token preflight

The activation PR adds `.github/workflows/preflight.yml`. After its separately approved merge, an authorized owner can manually select trusted current main, dispatch this preflight and explicitly approve production-plan. It deliberately works with the operations flag off. It reads exact repository/User ownership, main protection and all four production environment/policy APIs using the restricted GH_PROTECTION_TOKEN, then emits only generic pass/fail. It has no id-token permission, AWS action/credentials, Terraform/provider/backend/plan step, private state or plan artifact. Do not substitute a broad owner CLI token or a successful mock test for proof of the restricted token. This execution does not dispatch that preflight or read/copy its secret value.

Use a fine-grained token selected only for this repository with Metadata read, Administration read and Actions read. Administration read covers branch protection; Actions read covers environment and deployment branch policy reads. Store it privately in the intended protected secret scope; never paste it into chat, shell history, source or logs. No write permission or AWS key is required. API403/404, missing/malformed protections, wrong owner/repository, stale main, missing required reviewers, bypass or tag policies fail closed. Do not widen permissions just to obtain a pass; privately confirm endpoint-specific requirements. [Official environments permission](https://docs.github.com/en/rest/deployments/environments#get-an-environment), [official policies permission](https://docs.github.com/en/rest/deployments/branch-policies#list-deployment-branch-policies).

A successful preflight proves that the supplied token can read and validate the required current APIs; it does not introspect or prove that the token has no extra scopes. The owner must independently keep its selection and grants restricted. Public endpoint readability is not a scope audit. A successful GitHub-only preflight is not approval for AWS operations. Keep ALLOW_AWS_OPERATIONS disabled until a separate explicit decision. For a future authorized infrastructure operation, approve the plan job, privately download only its encrypted same-run artifact, use trusted Linux tooling and the separately held key to authenticate/decrypt and inspect the exact saved plan/source/digest within24hours, then explicitly approve production-apply. A digest alone is not substantive review; never upload the plaintext plan/state/key. Preserve state locking, exact saved-plan apply, shared non-cancelling concurrency and typed site-only teardown. No operation in this paragraph is executed by activation-PR preparation.
