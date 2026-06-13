# Security Review Checklist (Phase 4)

Completion status for production readiness per [SECURITY.md](./SECURITY.md).

| # | Control | Status | Evidence |
|---|---|---|---|
| 1 | JWT auth + tenant scoping on all API routes | Done | `services/api/routers/auth.py`, `services/api/deps.py` |
| 2 | Postgres RLS on tenant tables | Done | `services/api/migrations/versions/003_rls.py` |
| 3 | Secrets in AWS Secrets Manager (not in repo) | Done | `infra/terraform/modules/secrets/` |
| 4 | No secrets in logs | Done | `services/api/middleware/security.py` |
| 5 | Prompt injection defenses | Done | `services/agents/prompts/sanitize.py`, eval at 100% |
| 6 | Disclaimer on all briefs | Done | `services/agents/prompts/disclaimers.py` + unit tests |
| 7 | VPC private subnets for RDS/ECS | Done | `infra/terraform/modules/network/` |
| 8 | Least-privilege IAM per ECS service | Done | Separate task roles for API vs worker |
| 9 | S3 bucket encryption + public access block | Done | `infra/terraform/modules/storage/` |
| 10 | Container image scanning (Trivy) | Done | `.github/workflows/build.yml` |
| 11 | Dependency audit in CI | Done | `pip-audit` in `ci.yml` |
| 12 | Dependabot enabled | Done | `.github/dependabot.yml` |
| 13 | CloudWatch alarms + SNS alerting | Done | `infra/terraform/modules/monitoring/` |
| 14 | Slack webhook alerts | Done | SNS HTTPS subscription in monitoring module |
| 15 | Langfuse tracing (self-hosted) | Done | `services/api/tracing/langfuse.py`, compose stack |
| 16 | WAF on ALB | Done | `infra/terraform/modules/waf/` |
| 17 | Incident response runbook | Done | `infra/runbooks/incident_response.md` |
| 18 | Secret rotation runbook | Done | `infra/runbooks/secret_rotation.md` |
| 19 | 50-case citation eval at ≥95% | Done | `services/eval/datasets/pipeline_v1.json` |
| 20 | Load test harness (100 profiles, 3 sources) | Done | `scripts/load_test.py` |

## Pre-Launch Gate

Before opening production to external tenants:

- [ ] Apply Terraform to staging AWS account and verify deploy pipeline
- [ ] Run `make migrate` including migration `003_rls`
- [ ] Run load test against staging: `python scripts/load_test.py --base-url $STAGING_URL`
- [ ] Confirm 2-week SLO burn-in on staging (citation accuracy, latency, staleness)
- [ ] Record demo video (REG-4-09)
