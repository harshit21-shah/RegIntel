# Staging Burn-In Checklist

Run this checklist for **2 consecutive weeks** before production launch.

## Automated (nightly)

GitHub workflow `.github/workflows/staging-burn-in.yml` runs:

1. `GET /readyz` — all dependencies healthy
2. `make eval-pipeline --persist` — citation accuracy ≥ 95%
3. `GET /admin/ingestion/status` — no source stale > 48h
4. Slack summary to ops webhook

## Manual daily

- Review CloudWatch alarms (SQS backlog, RDS CPU, API tasks, worker tasks)
- Check Langfuse for query p95 latency < 15s
- Scan logs for LOW_CONFIDENCE spikes

## Pass criteria

| SLO | Target |
|---|---|
| Citation accuracy | ≥ 95% sustained |
| Ingestion staleness | < 48h all sources |
| Query latency p95 | < 15s |
| LOW_CONFIDENCE rate | < 20% |
| CRITICAL alert delivery | Zero unresolved failures |
| False-positive rate | < 15% (7-day rolling) |

## Sign-off

Record burn-in start/end dates and final metrics in the deployment PR before enabling production approval gate.
