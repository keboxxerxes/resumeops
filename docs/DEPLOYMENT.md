# Deployment and operations

**Procedure prepared, not executed.** Current authorization excludes AWS resource creation, IAM changes, public visibility, plan/apply/destroy and operational-workflow activation. Obtain separate explicit approval before any account-side command or launching AWS CloudShell: launching CloudShell creates a compute environment. Verification GO is not deployment authority.

Terraform execution is Linux-first: GitHub-hosted Ubuntu is canonical for CI; one-time bootstrap may use an approved AWS CloudShell session or another trusted Linux amd64 host with the same pins. Native Windows Terraform is out of scope. Windows remains supported for website/VS Code/Codex work.

## One-time bootstrap prerequisites

The human operator must approve the account, region, short-lived federated identity, IAM/bootstrap permissions, expected resources, cost estimate, exact source revision and private budget recipient. Use no long-lived AWS keys, repository credentials or shared terminal capture. CloudShell uses the console identity's existing credentials; do not run `aws configure` or copy credentials into files. Verify identity privately only after authorization. Check for a pre-existing GitHub OIDC provider; set private `existing_oidc_provider_arn` rather than changing/importing a shared provider silently.

Actual GitHub plan/protection availability is a release prerequisite: strict reviewed main, independent current PR approval including administrators, no bypass actors and required CI. Before operational workflows are later enabled, configure all four exact production environments with independent required reviewers, no self-review/admin bypass and exactly main/no tags. The gate API must prove these controls; unavailable private-repository features are a blocker, not a reason to publish or weaken approval. No settings are presumed configured now.

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

Create ignored private `.local/bootstrap.tfvars` from the [bootstrap example](../infra/bootstrap/bootstrap.example.tfvars). Choose a unique name and actual exact repository; supply any existing OIDC ARN privately. Never commit account identifiers, role ARNs, backend details or recipient address. Read the budget email without echoing it or placing its value in history:

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

Do not copy templates into `.github/workflows` in this procedure. Activation is a separately authorized/reviewed change, including actual GitHub protections and fresh CI. Only then may scoped environment configuration and exact OIDC roles be enabled; never static AWS keys. Hold the same random protected AES-GCM handoff key separately from ciphertext artifacts. Recipient email remains private state data. Public repository/content publication needs another approval.

## Future approved operations

Infrastructure: current reviewed main, real protection API checks before OIDC, fresh private binary plan, authenticated ciphertext only, substantive private review/digest comparison before post-plan protected approval, same-run/SHA/operation/digest/24-hour age checks and exact reviewed apply. A digest alone is not plan review. Non-cancelling `resumeops-production` concurrency covers infrastructure/content/drift/destroy; operators coordinate local sessions and native state locks too.

Rollback: approve exact main-ancestor content SHA; run current trusted tooling; extract only regular allowlisted assets; regenerate metadata; upload explicit types/cache settings; invalidate `/`, `/index.html`, `/styles.css`, `/app.js`, `/deployment.json`; wait and verify HTTPS/headers/revision. Never execute historical runner scripts. Non-atomic uploads require deliberate recovery after smoke failure.

Drift: scheduled/manual read-only plan role, Terraform 0 = no drift, 2 = drift requiring review, 1/other = error; never apply. Tests use only a synthetic shell function, no real infrastructure plan.

Teardown: separate human authorization, exact typed `DESTROY production SITE ONLY`, protected post-plan approval, shared concurrency and site-only root. Versioned site `force_destroy=false` rejects nonempty deletion; separately authorize review/removal of only its exact object versions/delete markers if required. Dependencies remove CloudFront before origin. Retain bootstrap/state/roles/budget unless separately authorized; preserve recovery evidence first. Do not remove a shared OIDC provider.

Recovery: disable operations, coordinate operators, confirm no active lock, preserve current state privately, restore only an explicitly approved prior version and inspect a fresh private plan before apply. Never force-unlock without investigating ownership or restore state blindly. Never erase the only state copy when cleaning scratch files.

## Cost and outstanding prerequisites

Target below USD 1/month at low traffic, not a guarantee. The 2026-11-25 illustrative estimate was USD 0.1063 before allowances/state/tax: 0.1 GB S3 at USD 0.023/GB-month; 1,000 PUTs at USD 0.005/1,000; 10,000 GETs at USD 0.004/10,000; 1 GB North American CloudFront at USD 0.085/GB; 10,000 HTTPS requests at USD 0.0100/10,000. Recheck [S3](https://aws.amazon.com/s3/pricing/), [CloudFront pay-as-you-go](https://aws.amazon.com/cloudfront/pricing/pay-as-you-go/) and [Budgets](https://aws.amazon.com/aws-cost-management/aws-budgets/pricing/) before authorization. Flat-rate plans and account-specific allowances are distinct. GitHub plan/runner eligibility is separate from AWS operating cost.

The account-wide USD 5 monthly budget defines private ACTUAL USD 1/3/5 alerts. Other account spend counts; delayed alerts never cap charges. Verify recipient/delivery live. Bounded versions, limited invalidations and no unnecessary compute/domain/customer-key resources preserve the small design.

Outstanding: explicit AWS/IAM/cost/recipient authority; approved short-lived operator/trusted Linux session; source/signing-key verification; actual account/region/provider ownership; private recovery storage; GitHub protection availability; real OIDC denials/least privilege, lock/recovery, origin privacy, HTTPS/deploy/metadata, drift, rollback, alerts and authorized temporary teardown. These are **NOT RUN**. [CloudShell identity/storage](https://docs.aws.amazon.com/cloudshell/latest/userguide/welcome.html) and [security](https://docs.aws.amazon.com/cloudshell/latest/userguide/security.html) were consulted; the agent did not launch CloudShell.
