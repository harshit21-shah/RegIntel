import type { BriefDetail, BriefList, ChangeList, ConsultantDashboard, ProfileList, QueryResponse } from "@/lib/types";

const DEMO_BRIEF: BriefDetail = {
  brief_id: "demo-brief-1",
  client_id: "demo-client-1",
  title: "FDA Glossary Overview — Reference Brief",
  change_summary:
    "Reference corpus update covering FDA mission and regulatory scope for onboarding queries.",
  severity: "SUBSTANTIVE",
  obligations: [
    {
      text: "Review FDA jurisdiction over your product categories before labeling or marketing claims.",
      deadline: "2026-09-01",
      citations: ["fda:glossary:overview"],
    },
  ],
  recommended_actions: [
    "Map product SKUs to FDA product centers",
    "Validate labeling against 21 CFR Part 101 where applicable",
  ],
  citations: [
    {
      clause_id: "fda:glossary:overview",
      source_url: "https://www.fda.gov/about-fda",
      excerpt:
        "The FDA is responsible for protecting public health by assuring the safety, efficacy, and security of drugs, devices, and the food supply.",
    },
  ],
  confidence: 0.98,
  generated_at: new Date().toISOString(),
  status: "COMPLETE",
  disclaimer: "RegIntel provides informational compliance intelligence and does not constitute legal advice.",
  agent_trace: [
    {
      agent_name: "Retrieval",
      model_used: "text-embedding-3-small",
      tokens_in: 120,
      tokens_out: 0,
      latency_ms: 45,
    },
    {
      agent_name: "Verification",
      model_used: "llama-3.3-70b",
      tokens_in: 890,
      tokens_out: 210,
      latency_ms: 820,
    },
  ],
};

export const mockBriefList: BriefList = {
  items: [
    {
      brief_id: DEMO_BRIEF.brief_id,
      client_id: DEMO_BRIEF.client_id,
      title: DEMO_BRIEF.title,
      severity: DEMO_BRIEF.severity,
      confidence: DEMO_BRIEF.confidence,
      generated_at: DEMO_BRIEF.generated_at,
      status: DEMO_BRIEF.status,
    },
  ],
  page: 1,
  page_size: 20,
  total: 1,
};

export const mockDashboard: ConsultantDashboard = {
  tenant_id: "demo-tenant",
  client_count: 2,
  recent_briefs: mockBriefList.items,
  total_changes: 3,
  low_confidence_briefs: 0,
};

export const mockChanges: ChangeList = {
  items: [
    {
      change_id: "demo-change-1",
      document_id: "sec_edgar:demo",
      clause_id: "sec:edgar:overview",
      change_type: "MODIFIED",
      severity: "SUBSTANTIVE",
      summary: "SEC EDGAR filing requirements reference update.",
      detected_at: new Date().toISOString(),
      affected_client_count: 2,
    },
  ],
  page: 1,
  page_size: 20,
  total: 1,
};

export const mockProfiles: ProfileList = {
  items: [
    {
      client_id: "demo-client-1",
      name: "Acme Foods Inc.",
      naics_codes: ["311412"],
      states_of_operation: ["CA", "TX"],
      product_categories: ["frozen seafood"],
      supply_chain_jurisdictions: ["US", "MX"],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ],
  page: 1,
  page_size: 20,
  total: 1,
};

export const mockQueryResponse: QueryResponse = {
  answer:
    "SEC filings are periodic and event-driven disclosures submitted to the SEC via EDGAR. [sec:edgar:overview]",
  citations: [
    {
      clause_id: "sec:edgar:overview",
      source_url: "https://www.sec.gov/edgar",
      excerpt: "EDGAR is the Electronic Data Gathering, Analysis, and Retrieval system.",
    },
  ],
  confidence: 0.93,
  status: "COMPLETE",
  disclaimer: "RegIntel provides informational compliance intelligence and does not constitute legal advice.",
};

export function getMockBrief(id: string): BriefDetail | undefined {
  if (id === DEMO_BRIEF.brief_id) return DEMO_BRIEF;
  return undefined;
}

export const mockIngestionStatus = {
  staleness_threshold_hours: 48,
  sources: [
    {
      source: "sec_edgar",
      status: "SUCCESS",
      document_count: 5,
      last_success_at: new Date(Date.now() - 6 * 3600_000).toISOString(),
      age_hours: 6,
      stale: false,
      error_message: null,
    },
    {
      source: "reference",
      status: "SUCCESS",
      document_count: 3,
      last_success_at: new Date(Date.now() - 72 * 3600_000).toISOString(),
      age_hours: 72,
      stale: true,
      error_message: null,
    },
  ],
};

export const mockEvalLatest = {
  suite: "citation-accuracy",
  cases: 24,
  accuracy: 0.94,
  threshold: 0.9,
  passed: true,
  created_at: new Date().toISOString(),
  failures: [],
};

export const mockCostSummary = {
  period_days: 7,
  total_cost_usd: 2.1,
  briefs_generated: 5,
  cost_per_brief_usd: 0.42,
  target_cost_per_brief_usd: 0.5,
  tenant_daily_cap_usd: 25,
  global_daily_cap_usd: 100,
};

/** Synthetic 7-day trend anchored to latest metrics when history API is unavailable. */
export function mockAdminTrends(latestAccuracy: number, latestCost: number) {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  return {
    eval: days.map((date, i) => ({
      date,
      accuracy: Math.min(0.99, Math.max(0.85, latestAccuracy - (6 - i) * 0.008 + i * 0.003)),
    })),
    cost: days.map((date, i) => ({
      date,
      cost_per_brief: Math.max(0.2, latestCost + (3 - i) * 0.02 - i * 0.01),
    })),
  };
}
