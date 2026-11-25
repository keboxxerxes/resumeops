# ResumeOps

A professional resume and a small AWS delivery design: semantic HTML, CSS and vanilla JavaScript, reusable Terraform, and reviewed GitHub Actions.

The website is intentionally simple. Infrastructure uses a private S3 origin, CloudFront OAC and HTTPS, separate protected Terraform state, GitHub OIDC roles and cost alerts. There is no backend, database, container platform, custom domain or application AI runtime.

## Verification and deployment

**Terraform runs on GitHub-hosted Ubuntu.** Native Windows Terraform is out of scope. Windows supports website development, VS Code and Codex. The repository is public. The maintainer reports AWS infrastructure/state bootstrap and resource rebinding completed; those live outcomes are not independently asserted by this source review. CI remains credential-free. This branch prepares infrastructure, content/rollback and drift workflows with trusted-main, protected-approval and explicit enable-flag gates, plus a protected GitHub-only token preflight. No AWS operation or website deployment is performed by this activation preparation.

The single-maintainer implementation passed fresh Ubuntu branch and PR CI: all 22 checks, including both real Terraform root validations and exact dependency provenance. Each later revision must pass its own CI; a previous green run is not accepted as current proof. See [verification and readiness](docs/VERIFICATION.md) for exact commit/run evidence, cleanup counts and current gates.

Single-maintainer governance requires PRs and passing CI before merge, while protected deployments retain explicit owner approval with no administrator bypass. AI review verifies implementation evidence; it is not independent human approval. See the [governance trade-off](docs/SECURITY.md#single-maintainer-governance-trade-off).

## Website development

Node 24 is used in CI; development dependencies are locked.

```sh
npm ci --ignore-scripts
npx playwright install chromium
npm run preview
```

Run `npm test` for desktop/mobile browser and accessibility checks. In this Windows workspace the existing pinned browser cache can be reused by setting `PLAYWRIGHT_BROWSERS_PATH` to `.tools/browsers` using an absolute path. No native Terraform or Python environment is required for the website preview.

## Project guide

- [Architecture](docs/ARCHITECTURE.md): boundaries, modules and delivery design.
- [Deployment](docs/DEPLOYMENT.md): future authorized Linux bootstrap, state migration, rollback and teardown.
- [Security](docs/SECURITY.md): trust boundaries, all 15 Checkov exceptions and release controls.
- [SDD workflow](docs/SDD_WORKFLOW.md): specification, agent responsibilities and acceptance mapping.
- [Verification](docs/VERIFICATION.md): current checks, cleanup inventory, evidence and prerequisites.
- [Linux-first decision](docs/decisions/001-linux-first-terraform.md): concise history and platform decision.

The AWS target is **below USD 1/month at low traffic**. A USD 5 account-wide monthly budget defines private ACTUAL alerts at USD 1/3/5; alerts do not cap spending. No AWS resources, IAM changes or public publication are authorized by verification results.
