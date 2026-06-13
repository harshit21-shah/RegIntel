/**
 * Typed REST client for RegIntel API (see docs/API_SPEC.md).
 * Regenerate from OpenAPI when spec export is available: npm run generate:api
 */
import { apiFetch } from "@/lib/api";
import type {
  BriefDetail,
  BriefList,
  ChangeList,
  ChangeSummary,
  ConsultantDashboard,
  AdminTrendsResponse,
  CostSummaryResponse,
  EvalLatestResponse,
  IngestionStatusResponse,
  Profile,
  ProfileList,
  QueryResponse,
  TokenResponse,
  TriageItem,
} from "@/lib/types";

export type BriefListParams = {
  page?: number;
  page_size?: number;
  client_id?: string;
  severity?: string;
  status?: string;
  since?: string;
};

export type ChangeListParams = {
  page?: number;
  page_size?: number;
  source?: string;
  severity?: string;
  since?: string;
};

function toSearchParams(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") search.set(key, String(value));
  }
  const query = search.toString();
  return query ? `?${query}` : "";
}

export const api = {
  auth: {
    login: (email: string, password: string) =>
      apiFetch<TokenResponse>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),
    register: (payload: {
      email: string;
      password: string;
      tenant_name: string;
      role: string;
    }) =>
      apiFetch<TokenResponse>("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  },

  profiles: {
    list: (page = 1, page_size = 20) =>
      apiFetch<ProfileList>(`/api/v1/profiles${toSearchParams({ page, page_size })}`),
    get: (clientId: string) => apiFetch<Profile>(`/api/v1/profiles/${clientId}`),
    create: (payload: Omit<Profile, "client_id" | "created_at" | "updated_at">) =>
      apiFetch<Profile>("/api/v1/profiles", { method: "POST", body: JSON.stringify(payload) }),
    update: (clientId: string, payload: Partial<Profile>) =>
      apiFetch<Profile>(`/api/v1/profiles/${clientId}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      }),
  },

  briefs: {
    list: (params: BriefListParams = {}) =>
      apiFetch<BriefList>(`/api/v1/briefs${toSearchParams(params)}`),
    get: (briefId: string) => apiFetch<BriefDetail>(`/api/v1/briefs/${briefId}`),
    feedback: (briefId: string, rating: string, comment?: string) =>
      apiFetch<void>(`/api/v1/briefs/${briefId}/feedback`, {
        method: "POST",
        body: JSON.stringify({ rating, comment }),
      }),
  },

  changes: {
    list: (params: ChangeListParams = {}) =>
      apiFetch<ChangeList>(`/api/v1/changes${toSearchParams(params)}`),
    get: (changeId: string) => apiFetch<ChangeSummary>(`/api/v1/changes/${changeId}`),
    triage: (changeId: string) =>
      apiFetch<{ items: TriageItem[] }>(`/api/v1/consultant/changes/${changeId}/triage`),
  },

  query: {
    ask: (question: string, client_id?: string | null) =>
      apiFetch<QueryResponse>("/api/v1/query", {
        method: "POST",
        body: JSON.stringify({ question, client_id: client_id ?? null }),
      }),
  },

  dashboard: {
    consultant: () => apiFetch<ConsultantDashboard>("/api/v1/consultant/dashboard"),
  },

  admin: {
    ingestionStatus: () => apiFetch<IngestionStatusResponse>("/api/v1/admin/ingestion/status"),
    evalLatest: () => apiFetch<EvalLatestResponse>("/api/v1/admin/eval/latest"),
    costSummary: (days = 7) =>
      apiFetch<CostSummaryResponse>(`/api/v1/admin/cost/summary${toSearchParams({ days })}`),
    trends: (days = 7) =>
      apiFetch<AdminTrendsResponse>(`/api/v1/admin/trends${toSearchParams({ days })}`),
  },
};
