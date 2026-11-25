# 001 - Linux-first Terraform

Status: accepted by the user's Linux-first cleanup instruction, 2026-11-25. This continues the existing end-to-end SDD cycle, without another milestone.

## Decision

GitHub-hosted Ubuntu is canonical for Terraform execution and acceptance. A separately authorized trusted Linux amd64 session, including CloudShell, may perform the one-time privileged bootstrap in [deployment](../DEPLOYMENT.md). Windows supports the website, VS Code and Codex. **Native Windows Terraform is OUT OF SCOPE**, not PASS and no longer an acceptance blocker. Stop investigating it; retire its executable diagnostics and active instructions. Do not weaken mTLS, OS protections, package authentication or state controls.

## Material history

| Observation / revision | Actual outcome and disposition |
|---|---|
| Initial Windows Terraform 1.17.2 / AWS 6.74.0 | Both real root init commands passed; validate1 before schema retrieval. Isolated core/builtin-only init/validate0. |
| Direct pinned provider certificate checks | Official archive/binary matched; advertised self-issued certificate verified offline. Fully verifying clients received a different certificate/issuer and rejected it with verification error20. Callback never overrode failure. Responsible component unidentified. |
| Authorized native outside-sandbox comparison | Both init0 and both validate1. Did not prove the sandbox alone responsible; no security control disabled. |
| Existing Ubuntu WSL launch | Service timeout before Terraform; target verification NOT RUN. No service restart. |
| `ce7394c1e1e4df2378558adc36bbbda9af1256da`, [first Ubuntu run](https://github.com/keboxxerxes/resumeops/actions/runs/45611385516) | Both readonly init0, both validate1; other18records0. Missing Linux content hash, distinct from Windows TLS. |
| `48f21a8f78f8d968dbf87d451b050492558bb4e4`, [corrected run](https://github.com/keboxxerxes/resumeops/actions/runs/45613932613) | All20records0, both actual validations and lock immutability independently inspected. |
| `61967de46dd5845c82853d07736f02545bd71ffb`, [prior final-head run](https://github.com/keboxxerxes/resumeops/actions/runs/45622176904) | All20records0 on actual hosted Ubuntu, exact SHA/logs/artifact independently inspected. Historical evidence, not a pass for the cleanup revision. |
| `733730c42a1d49c9864585575ec71afda0d425a4`, [Linux-first cleanup run](https://github.com/keboxxerxes/resumeops/actions/runs/45635134136) | Fresh22/22records0 on hostedUbuntu24.04, both real validates0 and unchanged locks. Exact remoteSHA/job/fulllogs/artifact independently reconciled after separately authorized private push. |

The original locks trusted the official Linux archive through `zh`, but had only the Windows unpacked `h1`. Readonly init could authenticate the ZIP and refuse lock mutation; later directory validation could not use a ZIP hash. Builder/reviewer separately derived canonical content hashes and reproduced the existing Windows hash. The pinned official Terraform CLI agreed in an ignored copied fixture. The approved repair added one Linux `h1` per lock, retaining every original Windows/15 archive hash and exact versions/constraints. No unchecked-cache or mutable-init workaround. [Provider proof](../evidence/provider-integrity.json).

## Consequences and evidence

Implementation acceptance uses real independent Ubuntu verification without claiming Windows was fixed. The cleanup needs a fresh complete suite at the exact reviewed revision after any separately authorized private push. Prior runs do not substitute. Operational workflows remain inert; public and live AWS authority remain separate.

Duplicate reports and diagnostics retire only after approved inventory/consolidation. All original tracked material remains at immutable baseline commit `61967de46dd5845c82853d07736f02545bd71ffb`; [inventory](../evidence/cleanup-inventory.json) records each original path/blob. Retrieve a full original with `git show 61967de:<original-path>` after fetching history. Essential actual commands/exits/SHAs/run references, native observations, finding closures and costs remain in [structured history](../evidence/verification-history.json). Raw keys/certificates/logs are not source evidence. Git history is not rewritten; diagnostic retirement does not conceal or resolve the historical limitation.

All mandatory controls/tests, 15 [exception rationales](../SECURITY.md), state separation/locking, OIDC/IAM, action/provider pins, dependency integrity and cost/budget definitions remain. The Windows checksum stays as historical integrity metadata, not an execution target.
