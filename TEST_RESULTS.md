# Test results

> Private Ubuntu CI verification is now explicitly authorized by the user (2026-11-25), including creation of a private `resumeops` repository and reviewed source commits/pushes. Public publication, AWS credentials/resources/IAM and Terraform apply/destroy remain prohibited. The approved SPEC amendment permits independently inspected successful credential-free CI validation of both pinned roots as the implementation gate; Windows remains a separate environment verdict. At this preparation point no hosted CI success is claimed. Only `ci.yml` is executable; the three operational workflows are inert source under `workflow-templates/` and cannot be dispatched or scheduled. Restoration requires a separately authorized enabling change.

Continuation of the existing SDD cycle, 2026-11-25. Results below are observed, not planned. Exact commands, working directories, exit codes and scanner summaries: [independent continuation evidence](docs/reviewer/continuation-commands.json) and [authorized orchestrator diagnostics](docs/continuation/orchestrator-diagnostics.json). Earlier-cycle evidence remains in `docs/reviewer/commands.json` and `docs/orchestrator-checks.json`.

| Applicable verification | Actual current result | Boundary |
|---|---|---|
| Terraform 1.17.2 recursive formatting | **PASS**, exit 0 | Both roots and reusable module. |
| Bootstrap init, `-backend=false -input=false -lockfile=readonly` | **PASS**, exit 0 | Independent sandbox and authorized outside-sandbox attempts; no remote backend. Readonly mirror warning recorded, no lockfile change. |
| Site init, same flags | **PASS**, exit 0 | Same isolation and preservation. |
| Bootstrap `validate -no-color` | **FAIL**, exit 1 | Provider schema unavailable at mTLS startup; successful source validation NOT established. |
| Site `validate -no-color` | **FAIL**, exit 1 | Same actual failure; no static substitute. |
| TFLint each root | **PASS**, exit 0 each | Existing recommended rules unchanged. |
| GitHub Actions/actionlint | **PASS**, exit 0 | Existing four SHA-pinned workflows. Actual hosted CI NOT RUN. |
| Checkov 3.4.11 final source | **PASS**, exit 0 | 67 passed, 0 failed, 15 individually assessed resource-specific exceptions, 0 parsing errors, 25 resources. Skipped controls remain absent. |
| Individual exception review | **COMPLETE**, all 15 retained with precise justification/residual | 11 scoped architecture/API residuals and 4 not-applicable controls; rationale defects corrected, no mandatory control suppressed. See `docs/EXCEPTION_REASSESSMENT.md`. |
| Source secret scanning | **PASS**, exit 0 | Redacted Gitleaks includes hidden/untracked intended source and excludes only local dependencies/caches. Final post-report result is in continuation final-sanitization evidence. |
| Browser/local HTTP/accessibility | **PASS**, exit 0, 6 cases | Desktop/mobile, axe, keyboard skip, reduced motion, metadata, no remote requests/overflow; screenshots independently inspected. |
| Security tests | **PASS**, exit 0, 6 cases | Protection gates, exact-plan crypto, typed destroy, drift classification, allowlisted content and guardrail negatives. |
| Dependency/provenance verification | **PASS**, exit 0 | Official upstream action tags/commit pins and provider/scanner/browser versions. Three version-constraint files and both lockfiles unchanged: `docs/continuation/dependency-preservation.json`. |
| Real negative scanners | **PASS**, harness exit 0 | Public S3 rejected by Checkov CKV_AWS_20; unsafe workflow rejected by CKV_GHA_2; malformed workflow rejected by actionlint. Nested scanner failures are expected, not waived positive results. |
| Independent IAM/API/crypto adversarial tests | **PASS**, exit 0 | Five static IAM mutations plus missing/bypass/stale/fork/API/key/date cases. Not live IAM simulation or rendered provider-backed evaluation. |
| Actual drift shell under runner-style errexit | **PASS**, exit 0 | Synthetic Terraform statuses 0/1/2 classified distinctly; resulting workflow statuses 0/1/1. Stub only, no cloud operation. |
| Official runtime IAM action names | **PASS**, exit 0 | 30 S3 and 15 CloudFront actions independently checked against public official metadata. |
| Public pricing and cost/budget inspection | **PASS** for source/estimate | Official S3 us-east-1 prices retrieved; CloudFront pay-as-you-go/Budgets sources rechecked. Approximately USD 0.1063 illustrative low-traffic usage before allowances/overhead/tax; below-USD-1 target and USD-5 budget/actual USD-1/3/5 thresholds preserved. Account eligibility and alert delivery NOT RUN. |

## Provider diagnosis and execution environments

Pinned provider binary matches the official archive member. A minimal AWS-only configuration and direct provider client reproduce the failure; a pinned Terraform core/builtin-only control initializes and validates with exit 0. That control is diagnostic isolation, not validation of ResumeOps. The provider-advertised self-issued CA certificate has a valid self-signature; a verified client instead observes a different, non-self-issued peer certificate with a different issuer and rejects it (verification error 20). Independent reviewer corroborated the certificate substitution. The responsible component and exact sandbox/endpoint boundary are not established. [Detailed reproduction](docs/MTLS_DIAGNOSTICS.md).

The user explicitly authorized narrow local diagnostics outside the sandbox. Both real root initializations exited 0 there; both validations exited 1. Existing Ubuntu WSL was listed successfully, but the authorized Linux validation launch exited 1 with `Wsl/Service/WSAETIMEDOUT` before the script ran. Exact Linux Terraform/provider archives were checksum-verified, but **Linux target init/validate are NOT RUN**. No new OS environment was installed, no service restarted and no security control disabled.

The tracked `scripts/diagnose-provider-mtls.py` returns 1 for this observed TLS failure, 2 if diagnosis cannot complete and 0 only for verified pinned TLS. The earlier ignored collection harness returned 0 for capturing a failed handshake; that is not a successful connection or Terraform validation. Reproduction does not send provider configuration RPCs or use cloud credentials.

## Unexecuted mandatory live verification

**NOT RUN:** actual hosted protection/plan availability and CI; real OIDC allow/deny/least privilege; state lock contention/recovery; origin anonymous-denial; HTTPS/default-root/headers/deployment metadata; real drift/no-change/error; prior-content rollback; budget recipient/delivery; authorized temporary teardown with bootstrap retention. Provider-rendered IAM testing is also NOT RUN because schema retrieval remains blocked. No deployed URL or CI link exists.

**Verdicts:** local implementation **NO-GO**; GitHub publication **NO-GO**; live AWS release **NO-GO**. Successful non-Terraform tests and justified exceptions do not override the missing successful root validations.
