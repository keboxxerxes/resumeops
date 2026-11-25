# Verification and repository cleanup

Canonical environment: GitHub-hosted Ubuntu 24.04, Terraform 1.17.2, AWS provider 6.74.0. Native Windows Terraform is **OUT OF SCOPE**. Website development/browser tests remain supported on Windows. There are no production Node dependencies; both locked devDependencies are used by Playwright and axe. Checkov is installed fresh for Linux verification only.

## Current operational workflow activation preparation

The existing main contains merged PR1. The maintainer reports post-merge CI, AWS bootstrap15resources, encrypted/versioned S3 state migration, website10resources, production state verification, CloudShell recovery, IAM resource rebinding and a no-change post-rebinding plan. These AWS outcomes are maintainer-reported, not independently asserted by this agent; no account identifiers or private deployment evidence are published.

The authorized local change moves the three existing operational templates into infrastructure/content/drift workflow definitions and adds an isolated protected GitHub-only preflight. Exactly five workflow roles are expected. CI remains credential-free for PRs/branch pushes. Credentialed jobs require allowed manual/drift-schedule events, current trusted main, the explicit operations flag, protected owner approval and API protection checks before OIDC. Plan encryption/review/explicit protected apply approval, rollback, state locks and typed site-only teardown remain. Preflight is manual protected main-only, reads all four environments with the restricted GH token, and cannot request OIDC/AWS credentials or run Terraform/backend/plan/deployment operations. It deliberately works with AWS operations disabled.

Independent read-only checks found ALLOW_AWS_OPERATIONS absent via specific repository/four-environment HTTP404 responses, not a literal configured false. The exact-true guards therefore remain off. The agent does not change that flag, IAM, resources, protection settings or content. Restricted-token execution is NOT RUN: owner CLI reads/mocks cannot prove the secret works; the protected preflight becomes a separate safe manual check after an authorized merge.

Before any push, independently review the exact public source/diff/privacy inventory and request human publication authorization. Full fresh Ubuntu CI must then check every declared workflow (all pins/role semantics/order), retain the original22records and all15exceptions, validate both real Terraform roots with readonly locks/backend disabled, and exercise preflight flag-off/API denial plus unsafe operational mutations. Verify latest remote branch SHA and actual PR synthetic checkout parents/tree, full logs/artifacts/all exits. No older successful revision is reused as a pass. Local/source handoff results and actual post-push status are separate; a restricted-token/live AWS result is never inferred from CI. Final verdict is for merging the activation source only; no merge or operational execution is authorized here.

Actual local results before publication: all5validroles and72unsafe semantic mutations accepted/rejected as expected;19integrity cases,26provenance resolver fixtures, six Windows-compatible Node cases and the API/preflight/plan negatives passed. Intended-source guardrails and graph checks exited0. A public-only70file snapshot secret scan found no leaks; no ignored deployment input/state was scanned. Full seven-case Node suite, actionlint and real Terraform validation remain mandatory in fresh Ubuntu CI, not claimed passed locally. Exact commands and the approved path mapping are retained in the existing [structured history](evidence/verification-history.json).

## Historical protection API compatibility correction

The user authorized a reviewed correction on the existing `single-maintainer-governance` branch/PR1, followed by credential-free Ubuntu verification and a final merge recommendation. Do not merge or change repository visibility/protections, operational workflows, AWS resources/credentials or IAM.

Current independent read-only API observations confirm exact repository ownership (`keboxxerxes/resumeops`, owner login `keboxxerxes`, owner type `User`), main required PR/strict verify/count0/stale false/no code-owner or last-push approval, absent bypass allowances, enforced administrators, disabled force pushes/deletion and required conversation resolution. All four production environment configurations are present with owner review, self-review permitted, administrator bypass false and exactly main/no tags. These are API configuration observations, not destructive bypass tests or live AWS/OIDC proofs.

The correction permits only genuinely absent allowances after independent personal-ownership verification, with missing/unknown/mismatched repository metadata, explicit null/malformed/nonempty allowances and organization omission rejected. It accepts boolean false or true for stale dismissal only under the zero-approval policy. Sanitized actual-response fixtures and unsafe variants exercise the real gate; no feature absence is inferred from the missing field itself. See [security](SECURITY.md#personal-repository-api-compatibility) and [specification](../SPEC.md).

Independent pure verification against fresh actual API responses passed all four environments, two compatible alternatives (present empty allowances and stale dismissal true) and rejected44unsafe variants. Local focused6Node tests, API/plan negatives, repository graph/19integrity cases and guardrails exited0. Exact current-observation semantics/results are retained in the existing [structured history](evidence/verification-history.json); raw API responses remain ignored.

At source handoff, new-revision hosted CI remains to execute. Final merge acceptance requires actual latest remote PR head and the tested synthetic merge commit's parents/tree, complete full job logs/artifacts, all22exit codes0, both real Terraform root init/validate and unchanged locks. Commit-linked GitHub runs and the independent final proof record those post-push results; no prior successful revision is treated as current proof. The agent stops after successful verification and the recommendation; no report-only commit loop or merge is required.

## Historical single-maintainer governance verification

The owner approved the source-policy change to mandatory PRs and successful strict CI with zero mandatory human PR approvals, retained manual required deployment approval including owner self-approval, no administrator bypass and exact main-only/no-tag environments. Independent AI review remains distinct from independent human approval. Actual GitHub protection settings, cloud authority and operational activation are unchanged.

**Single-maintainer source implementation and automatic branch/PR verification: GO at `bea382b362ce0e28aebbf5ccb3bb9141f51ee505`.** The earlier core-policy/provenance implementation below was independently verified at b63; the final trigger-repair results follow in their own section. The independently reviewed public feature branch and draft [PR1](https://github.com/keboxxerxes/resumeops/pull/1) passed fresh hosted Ubuntu verification:

| Actual run | Source identity | Observed result |
|---|---|---|
| [Dispatch45649850084](https://github.com/keboxxerxes/resumeops/actions/runs/45649850084), job139331062555 | Exact branch`b63f13b6` |22/22exit0 |
| [PR45649810776](https://github.com/keboxxerxes/resumeops/actions/runs/45649810776), job139330911926 | Actual checkout/artifact`76e521307b292d010a396fbd9e654e70b85af8d4` |22/22exit0 |

The independent AI reviewer inspected actual remote identities, full logs, artifact contents/digests and ordered21externalcommand/exitpairs plus internal lock-immutability0. The actual PR synthetic commit has parents`ad9ef109`/`b63f13b6` and tree`4de2ad88b1a172569fa1de0a7fd7fcd79570652d`, exactly the reviewed branch tree. GitHub earlier reported a different merge ref`950ba01e...`; its parents/tree also matched, but it was not substituted for the artifact's actual checkout identity.

Both runs executed six official anonymous Git action-pin lookups successfully,26resolverfixtures(2positive/24negative), both real backend-disabled readonly Terraform initializations/validations, unchanged17-hash locks, TFLint, provenance/secret/workflow/security/adversarial checks,19integrity cases,7Node cases and6browser/axe cases. Checkov67passed/0failed/15reviewed exceptions. No confirmed source-security finding remains. All exact commands, exits, SHAs, run/job/artifact identities and prior failed attempts are retained in [structured history](evidence/verification-history.json).

The user explicitly authorized this public feature branch, draft PR and credential-free CI after the earlier private-only preflight stopped. Main remains`ad9ef109`; visibility is public and unchanged; PR1 remains draft/unmerged. Actual GitHub protection settings are unmodified and their live enforcement remains NOT RUN. Source-policy fixtures are not proof of real repository configuration or independent human approval. No merge, visibility/protection change, AWS/IAM operation or operational activation is authorized. Every later evidence-only HEAD, including this report update, needs its own complete branch/PR CI and independent actual identity verification; this stored proof covers b63 only. Live release remains NO-GO.

Actual local governance checks: six explicitly selected Windows-compatible Node cases passed (exit0), `node tests/additional-security.mjs` passed (exit0), repository graph/19integrity cases/guardrails passed (exit0). A name-filter attempt ran all seven Node cases:6passed/1failed because the Linux Python path is unavailable on Windows; no full-suite pass is claimed. Complete Ubuntu verification was subsequently observed at b63 as recorded above; the Windows prerequisite failure is not relabeled as a local pass.

### Initial governance CI and confirmed availability blocker

At branch `a4cb7078497d16e43baeec4d642b6a6888d35d8a`, [exact-branch dispatch45647467358](https://github.com/keboxxerxes/resumeops/actions/runs/45647467358) passed22/22. [PR run45647476327](https://github.com/keboxxerxes/resumeops/actions/runs/45647476327) attempts1and2 each failed only `Official dependency and cross-platform lock provenance` (exit1): GitHub's anonymous REST action-tag lookup returned HTTP403 rate-limit exceeded. All other21records, both actual Terraform roots and lock immutability passed. This was not a dependency mismatch or a waived check; overall PR acceptance remained withheld. Attempt-specific logs and artifact IDs/digests were independently reconciled and preserved in [structured history](evidence/verification-history.json).

The PR artifact checked synthetic merge `e27d74341d3a3a592028c4f004e1915ed85c4d12`, parents main`ad9ef109`/branch`a4cb7078`, tree`358da9cee09937527c244cbaf3aa3b226b5fbbea` matching the reviewed branch. A branch API head SHA alone is not proof of PR checkout identity. No third blind retry or weakened provenance check is accepted. The repaired candidate verifies the same six official action tags/peeled commits via anonymous HTTPS Git, with all pins and other checks retained. It isolates Git configuration/URL rewrites, credential helpers, prompts, headers and inherited credential variables; runs without a shell with a bounded timeout; strictly rejects missing/malformed/duplicate/unexpected refs, wrong commits and process failures. TLS verification is not bypassed. `python tests/independent_checks.py --action-tag-fixtures-only` exited0 for26cases (2positive,24negative), including import-without-network and child-environment isolation assertions. Default Ubuntu integration still runs all original checks plus these cases; the mandatory runner remains22records. A native Windows Git query failed closed with TLS/CA error(exit128), so all-six live pin verification is not claimed locally and requires actual Ubuntu CI. [Git's documented tag/peeled-ref format](https://git-scm.com/docs/git-ls-remote) defines the authoritative output. The repaired b63 candidate subsequently passed fresh complete branch and PR CI as recorded above; both original failures remain failures, not rewritten as passes.

### Direct branch trigger availability repair

The evidence-only branch`3e03b165982eb90178b6839f8b0b6c1e8339c655` passed [PR45650899789](https://github.com/keboxxerxes/resumeops/actions/runs/45650899789), all22actualexits0. Actual PR checkout`2b2d7a332bd610f88faafc2b3ef18deb6c5d056e` has parents`ad9ef109`/`3e03b165` and exact reviewed tree`2054608133fb1e462837c0c3da2ace7d2c1e40a3`. Its separate exact-branch dispatch was **NOT RUN**: GitHub returned persistentHTTP500 before run creation through CLI and direct verified HTTPS; the browser access host was unavailable. Trigger failures are not failed tests or successful runs. Independent evidence preserves this distinction.

To obtain repeatable direct-HEAD verification without that dispatch service, the same credential-free CI now uses `push.branches: ['**']`. It retains PR and manual triggers, all22checks/pins and contents-read permissions, with no AWS/OIDC/custom secrets or operational path. [GitHub branch-filter semantics](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onpushbranchestagsbranches-ignoretags-ignore) exclude tag pushes when only branches are defined. Deployment environments still permit only main/no tags. This also supports future feature branches without a stale named-branch exception. Open PR pushes may run both direct-head and synthetic-merge CI, increasing runner usage; that is separate from the unchanged AWS cost target/budget. Planner and reviewer assessed this as verification availability remediation, not a security waiver or operational activation. **Trigger repair independently verified: GO at `bea382b362ce0e28aebbf5ccb3bb9141f51ee505`.** Earlier b63/3e successes were not substituted. Actual hosted Ubuntu runs:

| Run | Actual source identity | Observed |
|---|---|---|
| [Push45652201801](https://github.com/keboxxerxes/resumeops/actions/runs/45652201801), job139339385663 | Exact branch`bea382b362ce0e28aebbf5ccb3bb9141f51ee505` |22/22exit0 |
| [PR45652208906](https://github.com/keboxxerxes/resumeops/actions/runs/45652208906), job139339410589 | Artifact/checkout`1942e5cd2274765fa2de07be218fcf7ff8aab40a` |22/22exit0 |

The PR checked commit has parentsmain`ad9ef109`/branch`bea382b3` and exact reviewed tree`b45f58fc76667525e0714c7deb61f7214eafed39`. The independent AI reviewer reconciled both complete artifacts and21orderedexternalcommand/exitpairs plus lock-immutability0 with full logs. Both runs executed six live official Git action-pin checks,26resolver cases, both real Terraform root initializations/validations,17providerhash/IAM provenance,19integrity cases,7Node and6browser cases; Checkov67passed/0failed/15reviewedexceptions. All commands and identities/digests are retained in structured history. Fresh10-commit history/privacy scan found no leaks. No confirmed finding remains.

The implementation is GO for the authorized public feature branch/draft PR. This final report-only follow-up still requires its own automatic push+PRCI; consult the exact commit-linked runs/artifacts and independent final evidence, never infer a later HEAD pass from bea. Main remainsad9, PR1draft/unmerged, visibilitypublicunchanged; no protection setting, operational activation, AWS/IAM/resource or merge action was performed. Actual repository protection enforcement/live AWS remain NOT RUN and release NO-GO.

## Historical Linux-first cleanup verification

Human explicitly authorized the reviewed private push and credential-free Ubuntu verification, including reviewed evidence-only follow-ups. The cleanup implementation at `733730c42a1d49c9864585575ec71afda0d425a4` passed its own fresh [run 45635134136](https://github.com/keboxxerxes/resumeops/actions/runs/45635134136), job `139278425158`: **22/22 actual exit codes0**. The independent reviewer fetched actual remote HEAD, private-repository/workflow metadata, complete job logs and the sanitized artifact and reconciled the ordered commands/results. No previous run was substituted. Every later HEAD, including this evidence update, requires its own full CI; actual commit-linked Actions results/artifacts are the final identity proof. No AWS resource, credentials, IAM, operational activation, public visibility or history rewrite is authorized.

## Mandatory suite

Pinned CI installs official checksum-verified tools, exact npm dependencies and Chromium, then runs `scripts/run-checks.py`. Linux is checked before any Terraform/subprocess execution. Every command reports a status even after an earlier failure; any failure fails the job. Standard short-lived read-only GitHub checkout access is used, without custom/AWS/OIDC credentials or backend operations.

| Check | Coverage |
|---|---|
| Exact Terraform/version + recursive format | Both roots/module, exact1.17.2 |
| Each root readonly init + real validate | `-backend=false -input=false -lockfile=readonly`; provider-schema validation, not static substitution |
| TFLint both roots | Existing recommended rules |
| Checkov IaC | Complete graph and15individually reviewed resource-specific exceptions |
| Workflow syntax + guardrails | Five exact workflow roles; CI isolation, protected no-AWS preflight, trusted main/flag/environment gates and gate-before-OIDC ordering; pins/permissions/triggers |
| Source/privacy scans | Exact intended index/history; no contacts, secrets, state/plans/logs/keys |
| Dependency provenance | Official action pins/versions, all17providerhashes, runtime IAM action names |
| Negative/adversarial tests | Real publicS3/unsafe-workflow rejection, IAM mutations, failed approvals/API cases, AES-GCM age/integrity/source, typed teardown |
| Drift runner test | Actual template shell with synthetic0/1/2 function; no real plan |
| Browser/axe/local smoke | Desktop/mobile, keyboard/reduced motion/metadata, no remote requests/overflow |
| Repository integrity + negative tests | Docs/links, code/command/asset references, TFmoduleboundaries, artifactprivacy, isolated workflow roles andorphans |
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

Current intended source tree (70files; original cleanup snapshot was69; activation relocates3workflows and adds only1necessary preflight workflow):

```text
.codex/agents/builder.toml
.codex/agents/planner.toml
.codex/agents/reviewer.toml
.github/workflows/ci.yml
.github/workflows/preflight.yml
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
.github/workflows/content.yml
.github/workflows/drift.yml
.github/workflows/infrastructure.yml
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

These commands/results describe the historically reviewed implementation revision above, not the current activation candidate. The recursive format command covered both roots and their module. TFLint both roots, actionlint for the then-active CI and three then-inert templates, secret/provenance scans, actual negative scanner/adversarial cases and drift shell tests all exited0 at that recorded revision. Actionlint against the current five-workflow activation candidate is NOT RUN at local source handoff and requires fresh Ubuntu CI. Checkov observed67passed,0failed,15individually reviewed skips; repository-integrity19, Node security7 and browser/axe6 all passed. Both17-hash locks and all version constraints remain unchanged. Full22ordered commands/exits, run/job/artifact identities/digests and independent findings are retained in [structured history](evidence/verification-history.json). No raw job logs were published. Native Windows Terraform is **OUT OF SCOPE**, not PASS.

Remaining live checks are NOT RUN: GitHub protection availability, actual OIDC/least privilege, lock/recovery, origin denial, HTTPS/deploy/metadata, drift, rollback, budget delivery and authorized temporary teardown. Source/cleanup GO never authorizes account changes or public visibility.
