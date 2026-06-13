# Design Partner Program

RegIntel's design partner program validates relevance accuracy and false-positive rates with one real SMB over four weeks.

## Partner selection

- 10–200 employee regulated business (food manufacturing preferred)
- Part-time compliance owner willing to review briefs weekly
- Willing to mark every brief as HELPFUL, NOT_RELEVANT, or INACCURATE

## Onboarding

```bash
make migrate
make seed-graph
make ingest-demo
python scripts/seed_partner.py \
  --tenant-name "Sunrise Snacks" \
  --admin-email partner@example.com \
  --profile-json scripts/partner_profile.example.json
```

Share UI URL (`http://localhost:3000`) and credentials with the partner.

## Weekly cadence

| Week | Partner activity | Internal activity |
|---|---|---|
| 0 | Profile intake call; walk through UI | Run seed + ingest |
| 1–3 | Review every brief; mandatory comment on NOT_RELEVANT | Monday: `python scripts/weekly_fp_report.py` |
| 4 | Final feedback survey | Export labels; `make train-relevance` |

## Success metrics

- False-positive rate < 10% (PRD target)
- Partner reviews ≥ 80% of generated briefs
- At least 10 NOT_RELEVANT or HELPFUL labels for LightGBM training

## Admin endpoints

- `GET /api/v1/admin/feedback/summary?days=7`
- `GET /api/v1/admin/relevance/weights`

## Exit criteria

After Week 4, partner graduates when FP rate < 15% for two consecutive weeks and citation eval remains ≥ 95%.
