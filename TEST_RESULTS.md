# Test results

Existing SDD cycle, private Ubuntu verification, 2026-11-25. No unexecuted test is passed and no deployment is implied.

Verified implementation commit: [`48f21a8f78f8d968dbf87d451b050492558bb4e4`](https://github.com/keboxxerxes/resumeops/commit/48f21a8f78f8d968dbf87d451b050492558bb4e4). Actual [Ubuntu run 45613932613](https://github.com/keboxxerxes/resumeops/actions/runs/45613932613) / [verify job 139204326432](https://github.com/keboxxerxes/resumeops/actions/runs/45613932613/job/139204326432) completed **successfully**. The independent reviewer fetched the actual job metadata, full logs and artifact, matched the exact SHA/runner and confirmed all 19 command exits plus the lockfile immutability check were 0. This is actual Terraform validation, not a static-scanner substitute. Sanitized evidence: [successful-ci-run.json](docs/github/successful-ci-run.json) and [independent run record](docs/reviewer/github/run-45613932613.json).

## Successful hosted checks

| Actual command/check | Result |
|---|---|
| `terraform version -json` | PASS, exit 0; exact 1.17.2 |
| `terraform fmt -check -recursive infra` | PASS, exit 0; both roots and reusable module |
| `terraform -chdir=infra/bootstrap init -backend=false -input=false -lockfile=readonly` | PASS, exit 0; official hashicorp/aws 6.74.0, no remote backend |
| `terraform -chdir=infra/bootstrap validate -no-color` | PASS, exit 0; actual log: configuration valid |
| `terraform -chdir=infra/site init -backend=false -input=false -lockfile=readonly` | PASS, exit 0; same pins/isolation |
| `terraform -chdir=infra/site validate -no-color` | PASS, exit 0; actual log: configuration valid |
| TFLint each root, existing recommended rules | PASS, exit 0 each |
| Checkov 3.4.11 IaC | PASS, exit 0; 67 passed, 0 failed, 15 individually justified resource-specific skips, 0 parsing errors |
| actionlint, active CI plus three inert templates | PASS, exit 0 |
| Gitleaks source secret scan | PASS, exit 0; hidden/tracked source included, only documented local dependency/cache exclusions |
| Workflow/IaC and verification-stage guardrails | PASS, exit 0; only CI executable; no operational credentials/execution path |
| Official dependency and cross-platform lock provenance | PASS, exit 0; action SHA pins, registries, both reviewed content hashes and all 15 original official archive hashes |
| Actual public-S3 negative scanner | PASS, harness exit 0; actual Checkov CKV_AWS_20 rejects fixture |
| Independent IAM/unsafe-workflow scanner cases | PASS, exit 0; five source mutations, actual CKV_GHA_2 and malformed-workflow actionlint rejection |
| Node security/negative suite | PASS, exit 0; 7 tests |
| Independent API and plan-crypto adversarial cases | PASS, exit 0; local dummy bytes only, no Terraform plan produced |
| Actual archived drift shell with synthetic Terraform function | PASS, exit 0; synthetic 0/1/2 captured distinctly; no real plan/apply or AWS operation |
| Browser, axe, keyboard, reduced motion, metadata/local HTTP smoke | PASS, exit 0; 6 desktop/mobile cases |
| SHA256 of both lockfiles before versus after all checks | PASS, internal exit 0; readonly CI did not mutate either lock |

The artifact contains all 20 ordered records (19 subprocess commands and one internal immutability assertion), source SHA and Linux runner OS. Job setup identifies the GitHub Actions runner group/Ubuntu 24.04; the reviewer matched the remote commit/workflow and inspected actual full logs, not builder reports or a green badge alone. GitHub token permissions are narrowly read-only for source checkout; no AWS/OIDC/custom secret credentials were supplied. Only CI is registered and repository secrets count is 0.

## First-run failure and explicitly reviewed repair

[Run 45611385516](https://github.com/keboxxerxes/resumeops/actions/runs/45611385516), exact source `ce7394c1e1e4df2378558adc36bbbda9af1256da`, actually **FAILED**: both readonly initializations exited 0, but both validates exited 1 because the unpacked Linux provider matched no recorded content hash. Its other 18 records were 0. This was a cross-platform lock correctness gap, distinct from Windows TLS substitution. [Actual failure artifact](docs/github/first-ci-run.json).

Both original locks trusted the official Linux archive through `zh`, but contained only the Windows unpacked-content `h1`. Builder and independent reviewer separately verified official archives and canonical Hash1, reproducing the original Windows hash; the pinned official Terraform CLI independently produced the same Linux hash in an ignored copied fixture. The reviewed source repair adds exactly one Linux `h1` per lock and preserves every original hash, exact provider/Terraform versions and constraint. Provenance now rejects missing/unreviewed content hashes and removal of any original archive hash. The successful rerun above verifies the actual repaired roots with readonly locks; no checksum/verification bypass was used. [Compatibility evidence](docs/github/LOCKFILE_COMPATIBILITY.md).

## Windows and unexecuted live checks

Native Windows initialization still passes and actual validation remains failed at provider mTLS because a verified direct client observes a substituted peer certificate. The responsible local component remains unidentified. Existing WSL launch timed out before Terraform ran, so WSL target verification is NOT RUN. The approved CI alternative establishes implementation readiness without relabeling either environment result. No security control was weakened. Historical native evidence remains under `docs/continuation/` and `docs/reviewer/private-stage-windows-run.json`.

**NOT RUN:** AWS/OIDC/account-side least privilege, remote state locking/recovery, origin privacy against actual S3, live HTTPS/deployment metadata, actual drift/rollback, budget delivery and authorized temporary teardown. Hosted protected environments/live-release protections were not configured or assumed. No AWS credentials, resources or IAM were configured; no Terraform plan/apply/destroy or public publication occurred.

| Gate | Verdict | Evidence / limit |
|---|---|---|
| Local Windows environment | **NO-GO** | Provider certificate substitution remains; native validation is not relabeled successful. |
| Implementation based on independently verified CI | **GO** | Exact reviewed source passed all 20 checks on GitHub-hosted Ubuntu, including both real root validations. |
| Private repository verification | **GO** | Private visibility, reviewed history/source, credential-free CI, sole active verification workflow and zero repository secrets independently verified. |
| Public repository publication | **NO-GO** | Not authorized; private verification does not approve public resume/repository exposure. |
| Live AWS release | **NO-GO** | Not authorized; AWS credentials, IAM, resources, plan/apply/destroy remain prohibited and mandatory live proofs are NOT RUN. |
