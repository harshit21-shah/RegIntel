import { http, HttpResponse } from "msw";
import {
  getMockBrief,
  mockAdminTrends,
  mockBriefList,
  mockChanges,
  mockCostSummary,
  mockDashboard,
  mockEvalLatest,
  mockIngestionStatus,
  mockProfiles,
  mockQueryResponse,
} from "./data";

export const handlers = [
  http.get("/api/v1/consultant/dashboard", () => HttpResponse.json(mockDashboard)),
  http.get("/api/v1/briefs", () => HttpResponse.json(mockBriefList)),
  http.get("/api/v1/briefs/:id", ({ params }) => {
    const brief = getMockBrief(String(params.id));
    if (!brief) return HttpResponse.json({ error: { message: "Not found" } }, { status: 404 });
    return HttpResponse.json(brief);
  }),
  http.get("/api/v1/changes", () => HttpResponse.json(mockChanges)),
  http.get("/api/v1/changes/:id", ({ params }) => {
    const change = mockChanges.items.find((item) => item.change_id === String(params.id));
    if (!change) return HttpResponse.json({ error: { message: "Not found" } }, { status: 404 });
    return HttpResponse.json(change);
  }),
  http.get("/api/v1/profiles", () => HttpResponse.json(mockProfiles)),
  http.post("/api/v1/query", () => HttpResponse.json(mockQueryResponse)),
  http.post("/api/v1/auth/login", () =>
    HttpResponse.json({
      access_token: "mock-access",
      refresh_token: "mock-refresh",
      token_type: "bearer",
      expires_in: 3600,
      tenant_id: "demo-tenant",
      role: "admin",
    }),
  ),
  http.get("/api/v1/admin/ingestion/status", () => HttpResponse.json(mockIngestionStatus)),
  http.get("/api/v1/admin/eval/latest", () => HttpResponse.json(mockEvalLatest)),
  http.get("/api/v1/admin/cost/summary", () => HttpResponse.json(mockCostSummary)),
  http.get("/api/v1/admin/trends", () => {
    const trends = mockAdminTrends(mockEvalLatest.accuracy, mockCostSummary.cost_per_brief_usd);
    return HttpResponse.json({ period_days: 7, ...trends });
  }),
];
