# Incident Response Runbook

## Severity Levels

| Level | Example | Response time |
|---|---|---|
| SEV-1 | Production down, data breach suspected | 15 min |
| SEV-2 | Ingestion stale >48h, citation accuracy drop | 1 hour |
| SEV-3 | Elevated LOW_CONFIDENCE rate, non-critical bug | Next business day |

## SEV-1: Credential Leak

1. Rotate all affected secrets (see `secret_rotation.md`).
2. Review CloudWatch and Langfuse logs for anomalous LLM usage.
3. Notify affected tenants within 72 hours if client data exposure is confirmed.
4. File post-incident report within 5 business days.

## SEV-1/2: Bad Deployment

1. Identify failing ECS revision in AWS Console or via:
   ```bash
   aws ecs describe-services --cluster regintel-production \
     --services regintel-production-api
   ```
2. Roll back to previous task definition revision:
   ```bash
   gh workflow run deploy-prod.yml -f image_tag=<previous-sha>
   ```
3. If a migration caused the issue, do **not** run destructive downgrades — revert code and apply forward fix.

## SEV-2: Ingestion Staleness

1. Check CloudWatch alarm `regintel-*-sqs-backlog` and ingestion scheduler logs.
2. Verify source API availability (eCFR, Federal Register, SEC EDGAR).
3. Manually trigger ingestion:
   ```bash
   aws ecs run-task --cluster regintel-production \
     --task-definition regintel-production-ingestion --launch-type FARGATE ...
   ```

## SEV-2: Citation Accuracy Regression

1. Run eval suite locally: `python -m services.eval.entailment.harness`
2. Compare Langfuse traces for the failing prompt version.
3. Roll back agent prompt changes or model routing if regression confirmed.

## Communication

- Internal: `#regintel-ops` Slack channel
- External: tenant email via SES template `incident-notification`
