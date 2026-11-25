# Independent security review

Private-verification amendment review: 2026-11-25. The latest user-approved SPEC.md amendment authorizes only private `resumeops` source creation/commit/push and credential-free Ubuntu verification. The orchestrator owns those writes; the reviewer remains read-only except assigned local evidence. All source, privacy, original cost/budget and authorization boundaries remain in force. Previous continuation evidence below is preserved history, not an assertion that private push is still forbidden or that Ubuntu CI already ran.

| Gate | Current verdict | Evidence boundary |
|---|---|---|
| Native Windows validation readiness | **NO-GO** | Current independent full runner emits all 20 records; bootstrap and site validate still exit 1. Prior mutually authenticated loopback certificate-substitution diagnosis remains visible. |
| Credential-free CI implementation readiness | **NOT RUN** | No actual hosted Ubuntu run at the reviewed revision has yet been independently inspected. A verified successful run is the approved implementation alternative; Windows remains separately failed. |
| Private GitHub verification readiness | **PENDING** | Working-tree source/privacy and workflow safety review passed, but exact index/commit, actual private remote and matching successful hosted CI still require evidence. Authorized does not mean performed or passed. |
| Public publication readiness | **NO-GO** | No authorization for public visibility or public personal-content publication. Private verification cannot confer it. |
| Live AWS release readiness | **NO-GO** | No authorization for AWS credentials/IAM/resources or operational workflow enabling, and all original mandatory live evidence is absent. |

## Independent private pre-push assessment

[PRIVATE_PUBLICATION_REVIEW.md](docs/PRIVATE_PUBLICATION_REVIEW.md) records the comprehensive intended-file privacy audit, physical workflow isolation, executable-path inspection, commit-identity/remote gates and current limitations. The active tree has exactly `ci.yml`; content/drift/infrastructure templates are outside `.github/workflows`. No active/direct/indirect path requests AWS/OIDC credentials, a remote backend, plan/apply/destroy or deployment. Immutable dependency pins, all 15 individually justified exceptions and the original below-USD-1 target/USD-5 budget/private actual alerts at USD 1/3/5 are preserved.

The reviewer independently ran the new complete verification runner on Windows. It correctly returned **1**, retaining **18 zero exits and 2 validation failures** across all 20 records rather than hiding later checks. Current evidence is [private-stage-windows-run.json](docs/reviewer/private-stage-windows-run.json); no Ubuntu success or immutable commit identity is fabricated. Exact index/commit/history and remote/run verification will be added only when actually inspected.

All confirmed source security findings remain closed in reviewed working source. The earlier conditional publication blocker is now superseded only for the explicitly authorized private verification path; public/AWS boundaries remain unchanged. No reviewer GitHub mutation, commit, push, AWS account API, role assumption, resource creation, deployment or destruction occurred.

## Final continuation evidence

Exact commands, working directory, exits, versions and sanitized outcomes are in [continuation-commands.json](docs/reviewer/continuation-commands.json). Initial evidence remains preserved separately. Raw diagnostics stay ignored; no certificates, ephemeral keys, credentials, state, plans or private contacts appear in committed evidence.

| Final independent check | Actual result |
|---|---|
| Pinned Terraform version / recursive fmt | PASS, exit 0 each; Terraform 1.17.2 Windows amd64 |
| Bootstrap init / site init | PASS, exit 0 each, backend disabled and provider lockfile readonly |
| Bootstrap validate / site validate | FAIL, exit 1 each, provider schema startup failed; no source-validity conclusion from these failures |
| TFLint bootstrap/site; actionlint | PASS, exit 0 for all three |
| Checkov after all exception-comment corrections | PASS, exit 0: 67 passed, 0 failed, 15 resource-local skips, 0 parsing errors |
| Source secret scan / guardrails / official provenance | PASS, exit 0 each |
| Browser/local HTTP/accessibility and Node security suite | PASS, exit 0 each, 6 browser tests and 6 security tests |
| Actual negative scanners and independent adversarial checks | PASS, exit 0 wrappers requiring actual Checkov rejection of public S3 and unsafe workflow; invalid workflow actionlint rejection; five IAM source mutations, API-gate/crypto negatives and actual drift runner-shell 0/1/2 capture all passed |
| Official runtime IAM action names | PASS, 30 S3 and 15 CloudFront names match public official metadata |
| Public S3 price-list recheck | PASS, exit 0, official us-east-1 rates independently retrieved; no account API |
| Original direct-provider mTLS diagnostic | Process exit 0 means structured failure capture only: required TLS verification failed, offered certificate did not match advertised pin |
| New tracked `scripts/diagnose-provider-mtls.py` | Actual exit **1**: checksum/binary match verified; advertised certificate self-signature valid; stdlib hostname/pinned-root TLS failed; independent callback observed a different non-self-issued depth-0 certificate and validation error 20. No failed verification was overridden. |

The tracked helper was independently inspected before execution. It trusts only the process-advertised certificate, enforces hostname/pin verification, returns the original PyOpenSSL verification result, bounds waits, strips cloud/provider credential environment variables from its child, sends no provider RPC, removes temporary certificate/key files, and terminates the provider. Its public protocol cookie is not a credential. The independently observed certificate substitution explains the failed pinned TLS channel; **the responsible component and exact host/sandbox policy cause are not established**. Importing another CA or accepting the substituted certificate would weaken process-specific trust and was not used as a fix.

The orchestrator separately records freshly authorized outside-sandbox Terraform comparisons. Both real root validations still failed there. An existing Ubuntu distribution was listed, but WSL launch timed out before the validation script started; **Linux target validation is NOT RUN**, not a failed Linux configuration validation. No WSL/service restart, security-product change, disabled TLS/mTLS, insecure reattach or cloud action was used. See [MTLS_DIAGNOSTICS.md](docs/MTLS_DIAGNOSTICS.md).

Provider-backed rendered-policy tests and every mandatory live test remain **NOT RUN**. Core-only checks, successful init, a zero-failure security scan, and a successful diagnostic wrapper do not substitute for the two mandatory validations.

## All 15 exceptions independently reassessed

[EXCEPTION_REASSESSMENT.md](docs/EXCEPTION_REASSESSMENT.md) contains **15 separate exact resource/check rows** with the actual omitted control, original-spec basis, inspected source controls, residual risk and disposition. [continuation-exceptions.json](docs/reviewer/continuation-exceptions.json) independently inventories all 15 final scanner skips. Eleven are narrow architecture/API residuals, four are inapplicable controls for the required workload/hostname. None is a blanket waiver or evidence that the absent control exists.

Confirmed rationale deficiencies are **CLOSED**: inline comments, README and scanner documentation now distinguish free S3 log delivery from storage/access fees; access auditing from IAM/versioning/locks/smoke tests; event monitoring from concurrency; regional recovery from same-region versioning; future backup prerequisites from verified backup evidence; AWS-managed KMS key storage from customer-key pricing; and this unenrolled pay-as-you-go distribution from free CloudFront flat-rate WAF offerings. No resource, IAM permission, mandatory control, cost target or budget was weakened to obtain this result. Final affected Checkov rerun passed with the same 15 precisely justified skips.

The original below-USD-1 low-traffic target and USD-5 account-wide budget/actual alerts at USD 1/3/5 are unchanged. Public pricing was independently rechecked and recorded in [continuation-pricing.json](docs/reviewer/continuation-pricing.json); account eligibility, future traffic, alert confirmation/delivery and live charges remain unverified. The target is not a cap. No newly unjustified suppression or unresolved source security finding remains in the reviewed scope; the validation and live-evidence blockers remain explicit.

## Initial independent checks (retained history)


Exact commands, exit codes and timings are in [commands.json](docs/reviewer/commands.json). Raw tool logs remain ignored under `.local/reviewer/`; no plans, state, private contacts or account details are included in this report.

| Check | Actual result |
|---|---|
| Terraform recursive format | PASS, exit 0; final affected recheck also 0 |
| Bootstrap and site init, backend disabled, lockfile readonly | PASS, exit 0 each; no backend access |
| Bootstrap and site validate | FAIL, exit 1 each: provider schema startup did not respond; orchestrator diagnostic establishes local automatic mTLS certificate verification failure. No successful schema validation claimed. |
| TFLint both roots | PASS, exit 0 each; bootstrap affected recheck also 0 |
| actionlint | PASS, exit 0; final affected recheck also 0 |
| Checkov 3.4.11 Terraform | PASS, exit 0: 67 passed, 0 failed, 15 resource-specific skips, 0 parsing errors; final affected recheck also 0 |
| Gitleaks intended source, including untracked source | PASS, exit 0, redacted; dependencies/caches excluded through documented configuration |
| Repository guardrail script | PASS, exit 0; complementary checks, not comprehensive policy proof |
| Node security suite | PASS, exit 0, 6 tests; independently repeated after gate correction |
| Official action/dependency provenance script | PASS, exit 0; immutable action commits match official upstream release tags, provider/scanner/browser versions match official registries |
| Browser, local HTTP, axe accessibility | PASS, exit 0, 6 tests across desktop/mobile; no remote requests, no horizontal overflow, keyboard skip link, reduced motion and safe metadata |
| Desktop/mobile screenshots | Independently inspected; readable layout, complete timeline/skills/education/architecture, no clipping observed |
| Real negative S3 scanner fixture | PASS: `tests/negative-scans.py` exit 0, requiring actual Checkov exit 1 and CKV_AWS_20 detection |
| Independent real unsafe-workflow scanner fixture | PASS: Checkov exit 1 and CKV_GHA_2 for generated shell injection; invalid workflow independently rejected by actionlint |
| Independent IAM source invariants | PASS: exact environment trust, STS audience, plan read-only state, exact lock rights, exact CloudFront IDs and fixed content assets; five adversarial source mutations rejected |
| Independent API/crypto negatives | PASS: fork ref, stale main, unavailable API, disabled operations, missing token, missing reviewer count, wrong/missing encryption key and future candidate timestamp rejected |
| Actual drift shell step under bash errexit | PASS for synthetic Terraform 0/1/2: outputs/statuses remain distinct; final workflow status 0/1/1. Terraform was a shell stub, so no cloud or plan operation ran. |
| Official AWS runtime IAM action names | PASS: 30 S3 and 15 CloudFront action names match official AWS service metadata after removal of invalid action |

Additional reproducible reviewer commands from the repository root (Windows):

```powershell
.tools/venv/Scripts/python tests/negative-scans.py
.tools/venv/Scripts/python docs/reviewer/independent_checks.py
node docs/reviewer/additional.mjs
.tools/venv/Scripts/python docs/reviewer/drift-execution.py
python docs/reviewer/action-names.py
```

The independent IAM tests inspect parsed source invariants; they are not rendered-policy evaluation, IAM simulation or live authorization tests. Native provider-backed rendered IAM testing was NOT RUN because provider startup already failed. No TLS check was disabled. Initial reviewer harness development included an overbroad matcher that also rejected allowed CreateInvalidation; that harness was corrected and rerun successfully, without changing implementation policy to satisfy it.

## Findings and closure evidence

| Finding | Disposition / independently verified closure |
|---|---|
| Drift result capture inherited GitHub runner errexit and could exit before classifying 1/2 | CLOSED: conditional command capture; actual workflow shell block tested under bash `-e -o pipefail` for all three statuses |
| CloudFront create permission used an API operation name; broad dependent tagging could authorize retagging unrelated resources | CLOSED: runtime CloudFront creation removed; authorized local operator first creates the exact privately reviewed saved plan, then bootstrap binds exact distribution/OAC/header-policy IDs. No wildcard retag or mutation targets remain. |
| Unhandled AWS subprocess exceptions could expose captured command output | CLOSED: content/deploy/smoke/drift CLI failures use sanitized exception handling; Terraform stdout/stderr remain private/suppressed in credentialed workflows |
| Branch PR bypass actors were not rejected | CLOSED: gate rejects bypass users/teams/apps, requires current independent review and administrator enforcement; negative test passes |
| Missing reviewer-count API field could pass numeric comparison | CLOSED: integer minimum and strict protection booleans enforced; independent malformed-count negative passes |
| Hidden ciphertext artifact path could be excluded by upload-artifact defaults | CLOSED: exact single ciphertext path plus explicit `include-hidden-files: true`; one-day retention. No plaintext plan/state upload path. |
| Exact site-bucket refresh lacked provider-required read operations | CLOSED at source: required read actions added only to the exact site bucket and checked against official service metadata/provider source. Actual role/refresh verification remains NOT RUN. |
| `s3:DeleteBucketOwnershipControls` was not an IAM permission | CLOSED: removed; valid `s3:PutBucketOwnershipControls` retained. All final runtime action names independently checked against official AWS metadata. |

No confirmed unresolved source security finding remains in the reviewed scope. Provider startup and unperformed live checks remain release blockers, not findings silently marked fixed.

## Controls and residual constraints

- OIDC trust uses exact repository/environment subjects and `sts.amazonaws.com`; environment subjects do not encode a branch. The gate independently requires actual main-only environment policies, independent required reviewers, no administrator bypass and protected main/current SHA before OIDC. Missing API access or unsupported GitHub plan features fail closed. This API behavior has local negative tests; actual repository configuration is NOT RUN.
- Plan/drift can read only site state and modify only its exact lockfile. Apply can write that state but cannot delete state, administer IAM or modify bootstrap. Content can upload only four explicit site keys and invalidate the exact distribution. CloudFront reads/mutations use exact configured IDs, with impossible unconfigured targets. First creation/recreation/rebinding requires separately authorized local operator work.
- Private S3 origins enforce encryption, versioning, public blocks, HTTPS and distribution-scoped OAC access. State is separate, protected against Terraform destruction and has a distinct key. Native lock contention, recovery and account-side denials remain NOT RUN.
- Apply uses a fresh private binary candidate, authenticated AES-GCM ciphertext only, same-run artifact, exact digest/revision/operation checks and 24-hour age limit. Human privately reviews the substantive decrypted plan before approving apply. No payload-derived file paths are extracted. Local cryptographic tests are not a live GitHub artifact/approval test.
- Credential-free PR CI never receives OIDC. Privileged workflows are current-main only, protected, timed out, share non-cancelling production concurrency and pass user inputs through validated variables. Rollback reads regular allowlisted historical assets using current trusted tooling; no historical scripts execute. Uploaded assets are not atomic; smoke failure requires deliberate rollback.
- Resume content follows the supplied baseline, labels Kubernetes/Helm/Argo CD as in progress, omits private email/phone/PDF and unknown repository links, and displays honest preview metadata. No trackers or external fonts. Current screenshots remain local ignored artifacts.
- All 15 scanner exceptions were individually inspected against [SCANNER_EXCEPTIONS.md](docs/SCANNER_EXCEPTIONS.md): omitted visitor logging/replication/event consumers/WAF/failover/geo restrictions/customer KMS/custom certificates follow the specified small static design. Required public blocks, encryption, versioning, OAC and exact role controls are not suppressed. Default CloudFront certificate legacy viewer TLS support is explicitly documented; no unsupported TLS1.2 minimum claim is made.
- Cost model remains below USD 1 only under stated low-traffic assumptions. Account-wide actual-spend alerts at USD 1/3/5 are Terraform-managed, use private input and do not cap spending. Official pricing sources and date are recorded in README; live price/eligibility/recipient delivery must be reverified before authorization.

Official permission references independently consulted: [CloudFront action mapping](https://docs.aws.amazon.com/service-authorization/latest/reference/list_cloudfront.html), [S3 machine-readable service metadata](https://servicereference.us-east-1.amazonaws.com/v1/s3/s3.json), [CloudFront machine-readable service metadata](https://servicereference.us-east-1.amazonaws.com/v1/cloudfront/cloudfront.json). Publisher signature verification was not performed; exact official TLS-delivered checksums, lockfile integrity and upstream tag provenance are the recorded evidence.

## Remaining release gates

Repair local provider mTLS startup without disabling certificate verification, then pass Terraform validate for both roots. Obtain separate explicit authorization before AWS/IAM/billing operations or publishing. Verify the actual GitHub plan and protections, OIDC allowed/denied subjects, state locking/recovery, origin anonymity denial, HTTPS deployment/headers/metadata, budget delivery, drift, rollback and authorized temporary teardown. All those live checks are **NOT RUN**. Until evidence exists, live release remains **NO-GO**.
