# Provider lockfile cross-platform compatibility

Date: 2026-11-25. Scope: exact Terraform 1.17.2 and hashicorp/aws 6.74.0, credential-free Ubuntu verification. This investigation creates no AWS resources and does not relax provider authentication, checksum enforcement or readonly initialization.

## Actual first Ubuntu result

GitHub Actions run `45611385516` verified source `ce7394c1e1e4df2378558adc36bbbda9af1256da` on Linux. Its sanitized machine evidence contains twenty checks: eighteen exit 0, and only the two root `terraform validate` commands exit 1. Both `init -backend=false -input=false -lockfile=readonly` commands exit 0 and report provider installation **signed by HashiCorp**, followed by a warning that provider selections were detected but not saved because the lockfile is readonly. Validation then rejects the cached unpacked provider because its content does not match a recorded checksum.

This is a different failure from the earlier Windows local provider mTLS certificate substitution. Ubuntu did not reach successful provider-schema validation on this first run, so no conclusion about Ubuntu's provider TLS behavior can yet be drawn.

## Cause

Both source lockfiles contain fifteen official archive `zh:` hashes and one Windows content `h1:` hash. The Linux archive's official SHA256 is already present, so downloaded-archive verification succeeds. After unpacking, `validate` authenticates the installed directory. Terraform's version-pinned implementation explicitly skips `zh:` for directories because an archive hash cannot match an unpacked directory. The sole existing content hash describes Windows files, and cannot match Linux files. Readonly init correctly refuses to write the newly calculated Linux content hash.

The existing provenance check correctly verifies archive hashes, but archive authentication alone is insufficient to authenticate this subsequent unpacked cache. Mandatory real `validate` checks exposed that gap; neither the checks nor readonly mode should be weakened.

Primary sources: [Terraform 1.17.2 hash implementation](https://github.com/hashicorp/terraform/blob/v1.17.2/internal/getproviders/hash.go), [Go content hash definition](https://github.com/golang/mod/blob/master/sumdb/dirhash/hash.go), [Terraform multi-platform provider locking](https://developer.hashicorp.com/terraform/cli/commands/providers/lock).

## Independently reviewable proposed correction

**Status: independently reviewed and approved additive correction applied; corrected Ubuntu validation still requires its own actual CI result.**

Download source: [official AWS 6.74.0 release archives and SHA256SUMS](https://releases.hashicorp.com/terraform-provider-aws/6.74.0/). Builder rechecked each local archive's SHA256 against a freshly fetched official manifest over verified TLS before calculating content hashes.

| Platform | Official archive `zh:` already committed | Derived content `h1:` |
|---|---|---|
| Windows amd64 | `zh:97b47a55644fc2ca4f53d0e277f6d8d3a3bb7279734185740580aba7de28ff29` | `h1:BT+sqgXa/XnH4zgVgG2ZEda3WVr6wSJyJbcv64hBTtg=` |
| Linux amd64 | `zh:2ede1946c7da024987f949000b07c274f81b387f994ab694f788721f338dd345` | `h1:GX7SKlV247NJ8PMuI3qvO//dcXb6UZYTXxJhLB4Yx/g=` |

Builder implements the published Hash1 algorithm: sort archive entry names, SHA256 each file's bytes, append lowercase file hash, two spaces, name and LF to a summary, then base64-encode the SHA256 of that summary with the `h1:` prefix. Both official archives contain only `LICENSE.txt` and their platform's provider executable. The algorithm reproduces the original committed Windows hash exactly, providing a positive control. Private derivation helper/proposal are ignored under `.tools/`; no provider was executed for this calculation.

The applied patch adds **only** the derived Linux `h1:` entry to each root. It preserves the original Windows `h1:`, all fifteen original `zh:` entries, provider source/version/constraints, exact Terraform pin and all validation/readonly controls. Each root changes from sixteen to seventeen allowed hashes. Original Windows working-file SHA256 for both roots: `68a32465876f8a19742c2a00fca6d62ab488d232430496c5efd6a0fc7d271fc6`. Git stores the initial LF-normalized content with SHA256 `02e7415cb302e5a6eccdd51225091be2c4985c06e6e278807d077bde17e2b259`. This working-file versus stored-content difference is CRLF/LF normalization, not different provider/hash semantics; exact source diffs must compare like line-ending representations.

This authenticates the unpacked form of the same already-authorized official Linux archive; it does not accept unverified bytes, change provider version or remove an original hash. Do not delete the Windows content hash or run unreviewed mutable init as a workaround.

## Review and verification gates

The independent reviewer separately recomputed both archive/content hashes from the official release manifest and verified both positive controls. The orchestrator ran pinned official Terraform 1.17.2 `providers lock` in an **ignored fixture** for Linux and Windows amd64: exit 0, exactly the same Linux `h1:` addition, no original hash removed. See [canonical command comparison](canonical-lock-verification.json). The planner assessed this as a routine cross-platform repair within the authorized version/checksum constraints; the orchestrator explicitly approved the exact addition before source modification.

Applied-source checks: each original sixteen-hash set is an exact subset of the new seventeen-hash set; no original version/constraint or source line changed beyond the one addition. Both new lockfile SHA256 values are `77e7d3b80c14195d19b4ef287e7705b97274be2028da593dab07f84ba545da1f`. Terraform fmt-check exits 0. The provenance guard now requires exactly the two reviewed content hashes and all fifteen original official archive hashes, so deleting the Windows hash, omitting the Linux hash or adding an unreviewed content hash fails verification.

Next gate: review the exact two-lock diff, rerun credential-free Ubuntu CI on the exact correction commit, retain readonly init for both roots, require both actual `validate` exits 0 and all other required checks/unchanged-lock check 0. Do not claim this first-run diagnosis or a calculated content hash as a successful validation result. Final CI findings and release verdicts belong in the orchestrator's reports; AWS deployment remains unauthorized.
