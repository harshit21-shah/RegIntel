# Secret Rotation Runbook

## Scope

Rotate credentials stored in AWS Secrets Manager under `regintel/{environment}/`.

## Schedule

Quarterly, or immediately after a suspected leak.

## Steps

1. **Announce maintenance window** — notify ops channel; agent pipeline may fail briefly during rotation.
2. **Generate new credentials** at each provider (Anthropic, OpenAI, Voyage, Neo4j Aura, Qdrant Cloud).
3. **Update Secrets Manager** values via AWS Console or CLI:
   ```bash
   aws secretsmanager put-secret-value \
     --secret-id regintel/production/anthropic-api-key \
     --secret-string "sk-ant-..."
   ```
4. **Force ECS service redeploy** so tasks pick up new secrets:
   ```bash
   aws ecs update-service --cluster regintel-production \
     --service regintel-production-api --force-new-deployment
   aws ecs update-service --cluster regintel-production \
     --service regintel-production-worker --force-new-deployment
   ```
5. **Revoke old API keys** at each provider after confirming healthy `/readyz` and a sample pipeline run.
6. **Document** rotation date in the change log.

## Verification

- `/healthz` and `/readyz` return 200 on staging and production.
- Run `pytest tests/e2e` against staging URL.
- Check Langfuse for successful agent traces post-rotation.
