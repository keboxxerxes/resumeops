# Independent private GitHub verification review

Date: 2026-11-25. The user's latest SPEC.md amendment authorizes a **private** `resumeops` repository, reviewed sanitized commits/pushes and credential-free Ubuntu verification. It does not authorize public visibility, public resume publication, AWS credentials or account calls, IAM, infrastructure plans/applies/destroys, live deployment, merge or destructive operations. The reviewer performs read-only inspection and tests; the orchestrator owns authorized GitHub writes.

## Pre-push source/privacy assessment

The initial intended-source audit examined all 81 files then returned by Git's cached/untracked-but-not-ignored inventory. It found no committed-intent state/plan/PDF/key/certificate/log/archive/image/cache artifacts, binary payloads, recognizable credential patterns, private email candidates, literal AWS account IDs or absolute user-profile paths. The sanitized file inventory and SHA256s are in [private-prepush-working-audit.json](reviewer/private-prepush-working-audit.json). This is a working-tree snapshot, not an assertion that a later index/commit was already reviewed.

All original resume content is the approved baseline, with no invented achievements, private email/phone or PDF; LinkedIn and city are supplied baseline content. The website retains honest local-preview metadata and no invented public repository/deployment link. Reports contain sanitized commands, booleans, public dependency/pricing references and source hashes; raw diagnostic keys/certificates/handshake payloads/logs remain ignored. Existing scanner cache/dependency exclusions do not exclude intended source or workflow templates.

Initial Git history was empty. The configured default commit email was not a GitHub noreply identity; its value was neither printed nor copied into evidence. The orchestrator will use an explicit GitHub noreply identity for **both author and committer** without changing global Git configuration. Actual commit metadata, exact index/tree, history and credential-free remote URL must be independently checked before the first push. A private repository is not permission to leak credentials, contact data or local diagnostic material.

## Executable workflow boundary

The reviewed verification-stage source contains exactly one executable workflow: `.github/workflows/ci.yml`. Future content, drift and infrastructure/destroy implementations reside only in `workflow-templates/content.yml`, `workflow-templates/drift.yml` and `workflow-templates/infrastructure.yml`. GitHub discovers executable workflows from `.github/workflows`; YAML trigger keys in the inert directory do not create workflows. This is physical isolation, not reliance on an unset enable variable. [GitHub workflow discovery](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows)

The active CI triggers only pull-request, main push and manual verification, uses `ubuntu-24.04`, a finite timeout and explicit `contents: read`. It grants no OIDC write permission, references no user/cloud secrets, defines no deployment environment, requests no AWS role, initializes no remote backend, and has no plan/apply/destroy/deploy command or indirectly executed operational path. Checkout credentials are not persisted. The ordinary short-lived read-only GitHub job token is distinct from user/AWS credentials; actions can access that token, so minimal permissions and immutable action commits remain material controls. [GitHub token permissions](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token)

The independent call-graph review covered tool installation, the verification runner, every invoked test and their imported modules. Installers retrieve pinned public dependencies/checksums. Terraform uses only format/version, backend-disabled readonly init and validate. Operational modules imported by unit tests have guarded CLI entry points; API tests replace network fetch with a local stub, encryption bytes/keys are synthetic, and drift shell tests replace Terraform with a function returning synthetic statuses. No historical content script, cloud RPC, role assumption or deployment executes through this path.

The runner records 19 individual checks plus a provider-lockfile immutability check, continues recording later failures instead of hiding them and returns nonzero if any check fails. Exact Terraform version is asserted, both roots are checked, template syntax and provenance remain checked despite physical inertness, real unsafe scanner fixtures and adversarial tests run, and browser/accessibility tests use a loopback-only local server. Only sanitized results JSON is uploaded, for three days; no plans/state/raw diagnostics/browser screenshots are uploaded. Missing/incomplete evidence or a failed/cancelled run cannot establish readiness.

## Security, exception and cost preservation

The individually reviewed 15 exact Checkov resource/check exceptions remain documented in [EXCEPTION_REASSESSMENT.md](EXCEPTION_REASSESSMENT.md). This stage does not add a blanket skip, change the original threat model, waive a mandatory control, alter provider/tool pins or weaken TLS/mTLS. Required public blocks, encryption/versioning, OAC, exact OIDC trust, state separation and limited IAM remain source requirements even though operational workflows cannot execute now. Static IAM mutations do not substitute for provider-rendered or live IAM evaluation.

The low-traffic AWS target remains **below USD 1/month**. The Terraform-managed account-wide budget remains **USD 5/month**, with private operator-input **ACTUAL** notifications at USD 1/3/5. The budget is not a cap; no alert email is committed. Private GitHub verification does not prove AWS costs, budget delivery, GitHub protected-environment availability or any live deployed security control.

## Independent verification-stage runner execution

The reviewer executed `scripts/run-checks.py` using workspace-pinned Terraform 1.17.2, the verified provider mirror and local browser installation, within the normal sandbox and without AWS credentials. Actual runner exit: **1**. All **20** required records were emitted: **18 exit 0**, with only bootstrap and site `validate` returning **1** at the known native Windows provider startup boundary. Version, format, both backend-disabled readonly inits, both TFLints, Checkov, all four workflow syntax checks, secret scan, guardrails, official version/cross-platform lock provenance, actual negative scanners, IAM mutations, seven security tests, API/crypto negatives, drift runner-shell tests, six browser/accessibility/local-smoke tests and lock immutability completed. This proves the runner reports later checks after a failure; it does not establish an Ubuntu pass.

Exact sanitized current-run commands/exits are in [private-stage-windows-run.json](reviewer/private-stage-windows-run.json). Its source SHA is correctly null because this was an uncommitted local checkout. The original cost/security source was not modified. Additional phone-pattern review found only three fixed-precision public S3 price values in the pricing evidence, not contact data. No potential private values were printed. Hosted CI, repository visibility and exact-index/commit checks remain separate pending steps.

## Exact revision and remote gates

Before the orchestrator pushes, the reviewer must inspect the exact staged file inventory/modes/blobs, confirm the final active workflow boundary and privacy scan, verify noreply author/committer metadata and the complete commit history, and confirm the intended remote is actually private. No approval based only on working-tree files, an assumed private default, a 404 or an unset variable is sufficient. The exact index/commit/remote checks are recorded separately when performed; this report does not fabricate future SHA/run values.

After push, the reviewer independently reads the actual repository visibility, immutable commit/run identity, job statuses/logs and sanitized artifact results. A completed successful Ubuntu run must match the reviewed revision and cover every required check. Any evidence-only follow-up commit must be separately reviewed and verified; no report claims its own yet-unknown commit SHA.

## Current five verdicts

| Gate | Current status / precise limit |
|---|---|
| Native Windows validation readiness | **NO-GO**: the documented pinned provider mTLS/schema startup failure remains; a later Ubuntu pass cannot relabel Windows validation as passed. |
| Credential-free CI implementation readiness | **NOT RUN** on hosted Ubuntu at this report stage; only actual final reviewed run evidence can establish GO. |
| Private GitHub verification readiness | **PENDING** exact index/commit/remote privacy review and successful matching credential-free CI. Private verification is authorized, but authorization alone is not evidence. |
| Public publication readiness | **NO-GO**: no public publication authorization; private verification does not authorize changing visibility or publishing personal content. |
| Live AWS release readiness | **NO-GO**: no AWS/IAM/deployment authorization or mandatory live evidence; operational templates remain inert until a separately authorized reviewed enabling change. |
