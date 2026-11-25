# Verification and repository cleanup

Canonical environment: GitHub-hosted Ubuntu 24.04, Terraform 1.17.2, AWS provider 6.74.0. Native Windows Terraform is **OUT OF SCOPE**. Website development/browser tests remain supported on Windows. There are no production Node dependencies; both locked devDependencies are used by Playwright and axe. Checkov is installed fresh for Linux verification only.

## Current candidate and authority

Human explicitly authorized the reviewed private push and credential-free Ubuntu verification, including reviewed evidence-only follow-ups. The cleanup implementation at `733730c42a1d49c9864585575ec71afda0d425a4` passed its own fresh [run 45635134136](https://github.com/keboxxerxes/resumeops/actions/runs/45635134136), job `139278425158`: **22/22 actual exit codes0**. The independent reviewer fetched actual remote HEAD, private-repository/workflow metadata, complete job logs and the sanitized artifact and reconciled the ordered commands/results. No previous run was substituted. Every later HEAD, including this evidence update, requires its own full CI; actual commit-linked Actions results/artifacts are the final identity proof. No AWS resource, credentials, IAM, operational activation, public visibility or history rewrite is authorized.

## Mandatory suite

Pinned CI installs official checksum-verified tools, exact npm dependencies and Chromium, then runs `scripts/run-checks.py`. Linux is checked before any Terraform/subprocess execution. Every command reports a status even after an earlier failure; any failure fails the job. Standard short-lived read-only GitHub checkout access is used, without custom/AWS/OIDC credentials or backend operations.

| Check | Coverage |
|---|---|
| Exact Terraform/version + recursive format | Both roots/module, exact1.17.2 |
| Each root readonly init + real validate | `-backend=false -input=false -lockfile=readonly`; provider-schema validation, not static substitution |
| TFLint both roots | Existing recommended rules |
| Checkov IaC | Complete graph and15individually reviewed resource-specific exceptions |
| Workflow syntax + guardrails | OnlyCIactive;3exactinerttemplates; pins/permissions/triggers |
| Source/privacy scans | Exact intended index/history; no contacts, secrets, state/plans/logs/keys |
| Dependency provenance | Official action pins/versions, all17providerhashes, runtime IAM action names |
| Negative/adversarial tests | Real publicS3/unsafe-workflow rejection, IAM mutations, failed approvals/API cases, AES-GCM age/integrity/source, typed teardown |
| Drift runner test | Actual template shell with synthetic0/1/2 function; no real plan |
| Browser/axe/local smoke | Desktop/mobile, keyboard/reduced motion/metadata, no remote requests/overflow |
| Repository integrity + negative tests | Docs/links, code/command/asset references, TFmoduleboundaries, artifactprivacy, inertoperations andorphans |
| Lock immutability | Both locks SHA256 before/after; changes fail |

Current runner emits **22** records: the original20 plus repository integrity and its negative cases. Unit counts are7security,19repository-integrity and6browser, plus scanner/IAM/API/crypto/drift cases. All these counts were observed in the new implementation run; earlier Windows security prerequisite failure remains historical and is not relabeled as a pass.

On trusted Linux amd64 with the pinned verified Terraform binary:

```sh
python3 scripts/install-tools.py
python3 -m venv .tools/venv
.tools/venv/bin/python -m pip install -r requirements-tools.txt
npm ci --ignore-scripts
npx playwright install --with-deps chromium
.tools/venv/bin/python scripts/run-checks.py
```

Only sanitized command/status/source/runner JSON is uploaded, three-day retention, under ignored `.local/verification/results.json`. No plans/state/raw diagnostics. The independent reviewer checks actual remote HEAD/run/job/logs/artifact and source, not a builder assertion or green badge. Evidence-only follow-up commits also need review/CI without inventing a future self-referential SHA.

## Historical actual outcomes

[Structured history](evidence/verification-history.json) retains three independent runs and exact ordered command records:

| Source | Run | Observed |
|---|---|---|
| `ce7394c` | [45611385516](https://github.com/keboxxerxes/resumeops/actions/runs/45611385516) | FAIL: two Linux cached-provider validates1; other18records0 |
| `48f21a8` | [45613932613](https://github.com/keboxxerxes/resumeops/actions/runs/45613932613) | PASS: all20records0, both actual roots valid |
| `61967de` | [45622176904](https://github.com/keboxxerxes/resumeops/actions/runs/45622176904) | PASS: all20records0, exact prior final HEAD inspected |

[Linux-first decision](decisions/001-linux-first-terraform.md) preserves concise native failures and the separate lock repair. [Provider proof](evidence/provider-integrity.json) retains independent content/archive derivation and official CLI confirmation. This cleanup changes no hash, constraint or lock.

Material closed findings: broad/invalid CloudFront create/retag scope; inherited drift errexit; subprocess output privacy; PR bypass/malformed reviewer counts; hidden artifact omission; provider reads/invalid IAM action; encoding; Linux content hash; inaccurate waiver audit/DR/cost descriptions. Structured history retains remediation/verified commits. All15rationales remain in [security](SECURITY.md); account-side policies remain untested.

## Inventory and retained purpose

Baseline:100tracked files at `61967de`,19166physical files excluding `.git`. The private exhaustive inventory classified each file. The compact [source/generated-target manifest](evidence/cleanup-inventory.json) records KEEP/CONSOLIDATE/ARCHIVE/REMOVE reasons, replacements, original blob IDs and counts. Complete originals remain available with `git show 61967de:<original-path>` after fetching history; no rewriting.

Approved baseline classifications:57KEEP,14CONSOLIDATE,25ARCHIVE,4REMOVE;42original paths retire only after material consolidation/reviewer approval. Generated tools/caches/raw intermediates/bytecode may be removed only under approved exact repository targets. Preserve Git and original user files, do not traverse reparse points or remove outside files. Retain installed Node/browser dependencies for Windows website work and local Gitleaks for final privacy review. Unknown untracked files defaultKEEPpendingreview.

Independent path-specific approval preceded deletion:42 archived/consolidated donor files and126 exact generated targets removed; all4 listed donor directories were removed only after verified empty. Immediate predelete verification checked all donor bytes against immutable baseline blobs, manifest binding, generated member digests/counts/bytes, in-root containment and ancestor/subtree reparse rejection. No unknown/outside files or Git history were removed.

Observed source count **100 ->69**; physical snapshot excluding Git **19166 ->945** (installed Windows website/browser dependencies and ignored private audit evidence retained). Later ignored audit records can grow; these are timestamped snapshot counts. No empty directories or reparse points remain in this snapshot. Full per-file classifications and removed/retained tree are in the manifest; complete private audit snapshots stay ignored.

Actual post-cleanup commands all exit0: `python scripts/check-repository.py`, `python tests/repository-integrity.py` (19tests), `python scripts/security.py`, `git diff --check`, `.tools/gitleaks.exe dir . --redact --no-banner`, `.tools/gitleaks.exe git . --redact --no-banner` (3commits, no leaks). Reviewer browser run `npm.cmd test` passed6tests. The Linux-only Node security command was attempted on Windows:6/7 passed,1failed for missing `.tools/venv/bin/python`; this is not reported as a passed suite. `python scripts/verify-provenance.py` also exited0: official action pins/dependency registries/all17lockhashes and30S3/15CloudFront action names verified via public metadata, without account calls. The fresh Ubuntu suite subsequently passed all22records at `733730c`; this resolves implementation acceptance without changing the historical Windows observation. The dependency checker verifies retained source purpose/entrypoints and rejection cases; ignored installed dependencies are not public source assets.

## Final tree and readiness

Actual retained source tree (69files;11canonicalMarkdownfiles and3essentialJSON records):

```text
.codex/agents/builder.toml
.codex/agents/planner.toml
.codex/agents/reviewer.toml
.github/workflows/ci.yml
.gitignore
.gitleaks.toml
.tflint.hcl
AGENTS.md
PROMPT.md
README.md
SPEC.md
docs/ARCHITECTURE.md
docs/DEPLOYMENT.md
docs/SDD_WORKFLOW.md
docs/SECURITY.md
docs/VERIFICATION.md
docs/decisions/001-linux-first-terraform.md
docs/evidence/cleanup-inventory.json
docs/evidence/provider-integrity.json
docs/evidence/verification-history.json
infra/bootstrap/.terraform.lock.hcl
infra/bootstrap/bootstrap.example.tfvars
infra/bootstrap/bootstrap.s3.tfbackend.example
infra/bootstrap/iam.tf
infra/bootstrap/main.tf
infra/bootstrap/variables.tf
infra/bootstrap/versions.tf
infra/modules/website/main.tf
infra/modules/website/outputs.tf
infra/modules/website/variables.tf
infra/modules/website/versions.tf
infra/site/.terraform.lock.hcl
infra/site/main.tf
infra/site/production.example.tfvars
infra/site/production.s3.tfbackend.example
infra/site/versions.tf
package-lock.json
package.json
playwright.config.mjs
requirements-tools.txt
requirements/RESUME_CONTENT.md
requirements/action-pins.json
scripts/check-repository.py
scripts/confirm.mjs
scripts/content.mjs
scripts/deploy-content.mjs
scripts/drift.mjs
scripts/gate.mjs
scripts/install-tools.py
scripts/plan-crypto.mjs
scripts/run-checks.py
scripts/security.py
scripts/smoke.mjs
scripts/verify-provenance.py
site/app.js
site/deployment.json
site/index.html
site/styles.css
tests/additional-security.mjs
tests/drift-execution.py
tests/independent_checks.py
tests/negative-scans.py
tests/repository-integrity.py
tests/security.test.mjs
tests/serve.mjs
tests/site.spec.mjs
workflow-templates/content.yml
workflow-templates/drift.yml
workflow-templates/infrastructure.yml
```

The separately authorized private push and fresh implementation run succeeded. Subsequent evidence-only HEADs require their own full CI and independent review; consult that exact commit's Actions run/artifact rather than inferring a pass from this document.

| Readiness | Independently observed implementation revision `733730c` |
|---|---|
| Repository cleanliness | GO: approved exact cleanup,69purpose-checked source files, clean worktree, full diff/privacy/history review |
| Latest reviewed HEAD verification | GO for733730c: actual22/22; each subsequent HEAD requires its own CI/artifact review |
| Canonical Linux Terraform | GO: hostedUbuntu24.04, both readonly/backend-disabled init and real schema validates0 |
| Source implementation | GO: full mandatory suite22/22, no confirmed open source finding |
| Public repository technical | GO for reviewed source; public visibility/personal publication remains NOT AUTHORIZED |
| AWS bootstrap | PROCEDURE PREPARED; execution NO-GO pending authority/account/session/key/recovery prerequisites |
| Live AWS release | NO-GO: authority and mandatory live proofs absent |

Actual Terraform commands from the sanitized artifact (all exit0):

```sh
terraform version -json
terraform fmt -check -recursive infra
terraform -chdir=infra/bootstrap init -backend=false -input=false -lockfile=readonly
terraform -chdir=infra/bootstrap validate -no-color
terraform -chdir=infra/site init -backend=false -input=false -lockfile=readonly
terraform -chdir=infra/site validate -no-color
```

The recursive format command covers both roots and their module. TFLint both roots, actionlint active/inert workflows, secret/provenance scans, actual negative scanner/adversarial cases and drift shell tests all exited0. Checkov observed67passed,0failed,15individually reviewed skips; repository-integrity19, Node security7 and browser/axe6 all passed. Both17-hash locks and all version constraints remain unchanged. Full22ordered commands/exits, run/job/artifact identities/digests and independent findings are retained in [structured history](evidence/verification-history.json). No raw job logs were published. Native Windows Terraform is **OUT OF SCOPE**, not PASS.

Remaining live checks are NOT RUN: GitHub protection availability, actual OIDC/least privilege, lock/recovery, origin denial, HTTPS/deploy/metadata, drift, rollback, budget delivery and authorized temporary teardown. Source/cleanup GO never authorizes account changes or public visibility.
