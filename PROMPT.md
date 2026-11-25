# Run ResumeOps in one SDD cycle
Read AGENTS.md, SPEC.md and requirements/RESUME_CONTENT.md. Inspect repository and branch; preserve existing work. Use configured planner, builder and reviewer subagents; if unavailable, report that limitation rather than claiming orchestration.
1. Spawn planner to produce docs/PLAN.md, traceable acceptance criteria, threat model, architecture, cost and verification plan. Resolve ambiguities conservatively within SPEC.md; stop for material scope changes.
2. Spawn builder to implement the complete project in one cycle, following the plan. Reviewer may identify test cases in parallel but must not edit builder files.
3. After implementation spawn reviewer to independently inspect code and execute available checks. Verify exact action SHAs, Terraform versions, IAM/OIDC trust, state and workflow safety, accessibility, privacy, cost and operations.
4. Remediate all confirmed findings, repeat independent checks until clean or report blockers. Do not bypass tests. Record actual commands, exit codes and sanitized evidence.
5. Produce all reports and README; summarize acceptance criteria, local readiness and live-release GO/NO-GO separately. Stop before cloud deployment, publishing, push/merge or destructive operations until explicitly authorized. Provide exact human bootstrap and deployment instructions. Never claim live verification if not performed.
Complete the entire scope without milestone releases. Do not add backend, Kubernetes, containers or AI runtime. Keep application simple. Target <$1 USD/month; $5 budget alerts are not a cap.
