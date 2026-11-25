# Dependency provenance

Exact action release tags and immutable commit pins are recorded in `requirements/action-pins.json`. `python scripts/verify-provenance.py` compares official upstream GitHub tag objects (including annotated tag peeling) against every workflow pin, then verifies AWS provider, Checkov and browser dependency versions against official registries. Network failures fail this check; never assume verification from a plausible SHA.

| Dependency | Pin / source |
|---|---|
| Terraform | 1.17.2, official HashiCorp release API / SHA256SUMS |
| hashicorp/aws | 6.74.0, Terraform Registry / official HashiCorp signed release checksum manifest; both roots lock same version with official zh archive hashes |
| Node | 24.22.2, official Node distribution (CI setup-node) |
| TFLint | 0.66.0, terraform-linters/tflint GitHub release + checksums.txt |
| actionlint | 1.7.12, rhysd/actionlint GitHub release + SHA256 checksum manifest |
| Gitleaks | 8.30.1, gitleaks/gitleaks GitHub release + SHA256 checksum manifest |
| Checkov | 3.4.11, PyPI, isolated venv |
| Playwright | @playwright/test 1.65.1, npm registry + package-lock integrity |
| axe | @axe-core/playwright 4.14.1, npm registry + package-lock integrity |

Direct npm dependencies are exact and transitive npm integrity is locked. Python scanner transitives are resolved by Checkov's metadata and installed in an isolated verification-only venv; they never ship to the site or obtain AWS credentials in CI. Official CLI checksums are fetched over verified TLS from the same official release source; independent cryptographic publisher-signature verification was not performed and is not claimed. Provider locks contain archive hashes for cross-platform CI, including Linux amd64.

References: [Terraform releases](https://releases.hashicorp.com/terraform/1.17.2/), [AWS provider releases](https://releases.hashicorp.com/terraform-provider-aws/6.74.0/), [Checkov](https://pypi.org/project/checkov/3.4.11/), [Node releases](https://nodejs.org/dist/v24.22.2/). Reverify before live release, and review dependency update PRs through the same unprivileged CI process.

## Provider refresh permissions

AWS provider 6.74.0 `resourceBucketRead` unconditionally reads ACL, CORS, website, acceleration, request payment, logging, replication and object-lock subconfigurations even when those are not configured. Runtime plan/apply roles therefore include those read actions on the **exact site bucket ARN only**, without write rights to those optional features. Names were verified against the [official S3 IAM action reference](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3.html) and [version-pinned provider source](https://github.com/hashicorp/terraform-provider-aws/blob/v6.74.0/internal/service/s3/bucket.go) on 2026-11-25. Actual AWS allow/deny testing remains NOT RUN.


Cross-platform content hashes were explicitly reviewed after first Ubuntu readonly init succeeded but cached validation failed. Both locks retain every original Windows h1/15 official archive zh and add the same independently computed official Linux h1. The pinned official Terraform providers-lock fixture agrees. The stronger provenance guard requires both content hashes/all original archive hashes, and successful Ubuntu CI confirms readonly init, validate and no per-run lock changes. See [compatibility review](github/LOCKFILE_COMPATIBILITY.md). Manual standalone publisher-signature verification was not performed; actual normal-registry CI installation reported the provider signed by HashiCorp, in addition to the recorded release-checksum and content-hash verification.
