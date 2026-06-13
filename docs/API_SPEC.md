# API_SPEC.md

Base URL: `/api/v1`
Auth: Bearer JWT (multi-tenant; `tenant_id` derived from token claims).
Content-Type: `application/json`

## 1. Client Profiles

### `POST /profiles`
Create a client business profile.

**Request**:
```json
{
  "name": "Acme Foods Inc.",
  "naics_codes": ["311412"],
  "states_of_operation": ["CA", "TX"],
  "product_categories": ["frozen seafood", "ready-to-eat meals"],
  "supply_chain_jurisdictions": ["MX"]
}
```

**Response** `201`:
```json
{ "client_id": "uuid", "created_at": "2026-06-13T00:00:00Z", ...profile fields }
```

### `GET /profiles/{client_id}`
Returns the profile object.

### `PATCH /profiles/{client_id}`
Partial update (e.g., add a new state of operation). Triggers a re-evaluation job (queues a relevance re-check against recent changes, async).

### `GET /profiles`
List profiles for the authenticated tenant (paginated: `?page=1&page_size=20`).

---

## 2. Briefs

### `GET /briefs`
List briefs, filterable.

**Query params**: `client_id`, `severity`, `status` (`COMPLETE`, `LOW_CONFIDENCE`), `since` (ISO date), `page`, `page_size`.

**Response** `200`:
```json
{
  "items": [
    {
      "brief_id": "uuid",
      "client_id": "uuid",
      "title": "New FSMA Traceability Requirements for Frozen Seafood",
      "severity": "CRITICAL",
      "confidence": 0.97,
      "generated_at": "2026-06-10T08:00:00Z",
      "status": "COMPLETE"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 4
}
```

### `GET /briefs/{brief_id}`
Full brief, including obligations, recommended actions, citations (with verbatim excerpts + source URLs), and agent trace summary.

```json
{
  "brief_id": "uuid",
  "client_id": "uuid",
  "title": "...",
  "change_summary": "...",
  "severity": "CRITICAL",
  "obligations": [
    {
      "text": "Establish and maintain traceability records for frozen seafood SKUs as of 2026-09-01.",
      "deadline": "2026-09-01",
      "citations": ["ecfr:21:1:1450"]
    }
  ],
  "recommended_actions": ["Update SKU tracking system to capture lot codes per 21 CFR 1.1450", "..."],
  "citations": [
    {
      "clause_id": "ecfr:21:1:1450",
      "source_url": "https://ecfr.gov/...",
      "excerpt": "Each person who manufactures... shall establish and maintain records..."
    }
  ],
  "confidence": 0.97,
  "generated_at": "2026-06-10T08:00:00Z",
  "disclaimer": "RegIntel provides informational compliance intelligence and does not constitute legal advice..."
}
```

### `POST /briefs/{brief_id}/feedback`
```json
{ "rating": "NOT_RELEVANT", "comment": "We don't manufacture frozen seafood anymore" }
```
Stores feedback, triggers async relevance-weight update job.

---

## 3. Ad-hoc Q&A (Chat)

### `POST /query`
```json
{
  "client_id": "uuid",
  "question": "Does the new FSMA traceability rule apply to our Texas frozen seafood SKUs?"
}
```

**Response** `200`:
```json
{
  "answer": "Yes. The FSMA Food Traceability Rule (21 CFR 1.1305-1.1465) applies to foods on the Food Traceability List, which includes ready-to-eat deli salads and certain seafood... [ecfr:21:1:1310]",
  "citations": [{"clause_id": "ecfr:21:1:1310", "source_url": "...", "excerpt": "..."}],
  "confidence": 0.93,
  "status": "COMPLETE"
}
```

If `confidence < threshold`: `status: "LOW_CONFIDENCE"`, `answer` includes a note that the system could not fully verify the answer and recommends consulting a professional.

---

## 4. Changes Feed (internal/consultant view)

### `GET /changes`
List recently detected regulatory changes (not yet necessarily tied to a specific client).

**Query params**: `source`, `severity`, `since`, `jurisdiction`.

```json
{
  "items": [
    {
      "change_id": "uuid",
      "document_id": "ecfr-21-1-2026-06-01",
      "clause_id": "ecfr:21:1:1450",
      "change_type": "MODIFIED",
      "severity": "CRITICAL",
      "summary": "New traceability recordkeeping deadline of 2026-09-01 for FTL foods.",
      "affected_client_count": 4
    }
  ]
}
```

### `GET /changes/{change_id}`
Fetch a single regulatory change by ID. Returns the same shape as list items.

### `GET /changes/{change_id}/affected-profiles`
List of `AffectedProfile` objects (client_id, relevance_score, hop_path) — consultant triage view.

---

## 5. Admin / Internal

### `GET /admin/eval/latest`
Returns latest CI eval run summary (citation accuracy, hallucination rate, etc.) — for internal dashboards.

### `GET /admin/trends?days=7`
Daily eval accuracy and cost-per-brief series for admin charting.

```json
{
  "period_days": 7,
  "eval": [{ "date": "Mon", "accuracy": 0.93, "cases": 12 }],
  "cost": [{ "date": "Mon", "cost_per_brief": 0.42, "briefs": 3 }]
}
```

### `GET /admin/ingestion/status`
Per-source last-successful-run timestamp, document counts — staleness monitoring.

---

## 6. Error Format

```json
{ "error": { "code": "LOW_CONFIDENCE", "message": "...", "request_id": "uuid" } }
```

Standard HTTP codes: `400` (validation), `401`/`403` (auth), `404`, `429` (rate limit), `500`.

## 7. Rate Limits

- `/query`: 30 requests/min per tenant (cost control on Sonnet calls).
- Bulk endpoints (`/briefs`, `/changes`): 100 requests/min.
