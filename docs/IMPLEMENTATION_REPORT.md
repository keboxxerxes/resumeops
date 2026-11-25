# Implementation report

> Private Ubuntu CI verification is now explicitly authorized by the user (2026-11-25), including creation of a private `resumeops` repository and reviewed source commits/pushes. Public publication, AWS credentials/resources/IAM and Terraform apply/destroy remain prohibited. The approved SPEC amendment permits independently inspected successful credential-free CI validation of both pinned roots as the implementation gate; Windows remains a separate environment verdict. At this preparation point no hosted CI success is claimed. Only `ci.yml` is executable; the three operational workflows are inert source under `workflow-templates/` and cannot be dispatched or scheduled. Restoration requires a separately authorized enabling change.

Implementation date: 2026-11-25. Scope: complete local ResumeOps specification, one SDD cycle. No AWS resources, role assumptions, IAM changes, content publication, repository push/merge or destructive cloud operations were performed.

## Delivered

- `site/`: responsive semantic resume, four-role career timeline, supplied competencies/education, architecture, local CSS/JS, honest deployment metadata. No personal phone/email, PDF, tracker or external font.
- `infra/modules/website`: private versioned SSE-S3 origin, public-access blocks/ownership, HTTPS transport deny, distribution-scoped OAC policy, default CloudFront hostname/root document, HTTPS redirect/security headers and bounded history.
- `infra/bootstrap`: separate protected encrypted/versioned state, native S3 locking permissions by exact key, exact OIDC repository/environment subjects, distinct plan/apply/content roles, private account-wide USD 5 budget with actual USD 1/3/5 notifications.
- `infra/site`: explicit production root/backend example, reusable module, sensitive outputs, pinned Terraform/AWS provider and lockfile.
- `.github/workflows`: credential-free PR CI, trusted current-main encrypted exact-plan infrastructure approval/apply, typed site-only destroy, approved fixed-asset content/rollback and read-only scheduled drift. All live jobs disabled without operator configuration/authorization and fail-closed API proof of actual repository/environment protections.
- `scripts/` and `tests/`: protection API checks, authenticated plan integrity/freshness, safe revision/asset handling, deploy/HTTPS smoke tooling, drift and destroy controls, CLI checksum installer, upstream provenance, negative guardrails and real scanner fixture, browser/accessibility tests.
- README and supporting documents: precise authorized bootstrap/state migration/first deployment, private substantive plan review, rollback, lock/state recovery, bounded history, teardown and cost caveats.

## Security design decisions

A GitHub environment subject cannot also encode branch identity; actual main-only environment branch policies and strict reviewed-main controls are verified through the GitHub API before OIDC. Unavailable protection/API access fails closed. No credentialed PR workflow exists. Production operations share one concurrency group and native S3 state locking.

To avoid broad CloudFront create/tag escalation, first site creation is a separately authorized local operator exact saved-plan operation. The operator then binds exact distribution/OAC/header IDs through bootstrap before enabling runtime changes. Runtime roles cannot create CloudFront resources or administer IAM/bootstrap. Replacements require new authorization/local creation and rebinding. Read and mutate scopes use exact IDs; defaults cannot match deployed resources.

Only authenticated ciphertext plans cross jobs; plaintext remains temporary/private and trap-cleaned. The reviewer must decrypt and inspect the actual candidate privately before approving the post-plan apply environment. Source SHA, operation, digest and age are rechecked; main movement blocks application. AWS subprocess output is captured and errors sanitized. GitHub account masking is enabled.

Resource-local scanner exceptions match specified architecture and are documented in `docs/SCANNER_EXCEPTIONS.md`; no blanket scanner bypass is used. The AWS default certificate's legacy viewer TLS support is an explicit residual inherent in the default-hostname requirement. No custom TLS policy is falsely claimed.

## Validation and limitations

See `TEST_RESULTS.md` and independent `SECURITY_REVIEW.md`. Builder checks passed for format, TFLint, actionlint, guardrails, security helper/negative tests, secret scan and upstream action/dependency provenance. Site worker ran and visually checked desktop/mobile browser cases. Terraform provider initialization succeeded through a checksum-verified workspace mirror, but provider schema startup for validate failed because the local Terraform/provider mTLS connection rejects its certificate chain; no checks were disabled. Thus full local readiness is withheld. All cloud verification remains NOT RUN because authorization is intentionally absent.

No CI run URL exists: the repository has no commits or publication. Evidence records sanitized local commands/results; no live result is implied.

Independent review is complete: all confirmed source findings were remediated and rechecked. Six browser and six security tests independently passed; real negative scanner fixtures, additional API/crypto/IAM mutations, drift shell execution and official IAM action-name checks passed. Both provider-backed Terraform validation attempts remain failed environmental checks. Exact commands and sanitized evidence are in `docs/reviewer/commands.json` and `docs/orchestrator-checks.json`; no complete local or live GO is claimed.


## Existing-cycle continuation: local readiness remediation

No implementation restart or additional milestone. Added a tracked, fail-closed Windows provider diagnostic (`scripts/diagnose-provider-mtls.py`) and independently reproduced certificate substitution on the local provider channel. The helper verifies the exact archive/binary, requires certificate validation and a client certificate, sends no provider RPC, sanitizes output and removes ephemeral keys. The responsible substitution component remains unidentified. The native outside-sandbox comparison was explicitly authorized by the human: init passed both roots, validate failed both. The existing Ubuntu WSL attempt timed out before Terraform ran. A core-only control passes but is not a ResumeOps validation substitute. See `MTLS_DIAGNOSTICS.md` and `continuation/orchestrator-diagnostics.json`.

Independent reviewer reassessed each of the 15 Checkov resource/check pairs. All remain scoped and justified by the unchanged specification, with explicit audit, recovery, availability, TLS and abuse-cost residuals. Corrected inline/document rationale for logging, KMS, event monitoring, regional recovery and WAF pricing; no infrastructure resources, IAM behavior, required controls, constraints or locks changed. Current Checkov reports 67 pass / 0 fail / 15 exceptions / 0 parse errors. Complete non-Terraform suite independently rerun: browser/accessibility6, security6, lint, actionlint, secret scan, provenance, actual scanner negatives and independent adversarial cases passed. Exact continuation command evidence is in `reviewer/continuation-commands.json`.

Official public pricing rechecked. Below-USD-1 low-traffic target and USD-5 budget with private actual USD-1/3/5 alerts remain unchanged. No live price eligibility, alert delivery or deployed behavior is claimed.

Current verdicts are separately **local NO-GO**, **GitHub publication NO-GO**, **live AWS release NO-GO**. Both mandatory root validations still lack success. README, TEST_RESULTS, SECURITY_REVIEW and FINAL_ASSESSMENT distinguish PASS/FAIL/NOT RUN and contain the remaining handoff. No AWS creation/IAM changes/publication/push/merge occurred and no security control was bypassed.
