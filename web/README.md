# RegIntel Web

Production-grade Next.js frontend for the RegIntel regulatory compliance intelligence platform.

## Stack

- **Next.js 15** (App Router) + TypeScript strict
- **Tailwind CSS** + internal design system (`components/ui`)
- **TanStack Query** — server state, caching, retries
- **Zustand** — persisted client filters & active client context
- **Framer Motion** — landing page transitions
- **MSW** — optional mock API for offline demos

## Quick start

```bash
cd web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). API calls proxy to FastAPI via `app/api/[...path]/route.ts` (default `http://localhost:8000`).

### Environment

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_DEMO_MODE=true` | Pre-fill login credentials |
| `NEXT_PUBLIC_MOCK_API=true` | Enable MSW mock handlers (dev only) |
| `API_URL` | Backend URL for Next.js proxy (required in Docker/ECS) |

**Production:** leave `NEXT_PUBLIC_MOCK_API` unset. Set `API_URL` to the internal FastAPI service URL.

### Docker

```bash
docker build -t regintel-web -f web/Dockerfile web
docker run -p 3000:3000 -e API_URL=http://host.docker.internal:8000 regintel-web
```

Staging deploy pushes `regintel/web:{sha}` to ECR and rolls ECS service `regintel-staging-web` (requires `STAGING_WEB_TASK_DEF` GitHub variable).

### Demo without backend

```bash
# .env.local
NEXT_PUBLIC_MOCK_API=true
NEXT_PUBLIC_DEMO_MODE=true
npm run dev
```

## Design system (`components/ui/`)

| Component | Purpose |
|-----------|---------|
| `SeverityBadge` | CRITICAL / SUBSTANTIVE / COSMETIC |
| `ConfidenceGauge` | Score bar with tone thresholds |
| `CitationCard` | Expandable verbatim source quote |
| `ObligationTimeline` | Deadline-sorted obligations |
| `AgentTraceViewer` | Collapsible agent pipeline trace |
| `HopPathVisualizer` | Graph path chips |
| `ErrorState` | Error UI with retry |

## API client

Typed REST: `lib/api-client.ts` (see `docs/API_SPEC.md`).

## Scripts

```bash
npm run dev
npm run build
npm run typecheck
npm run lint
npm run test:e2e
```
