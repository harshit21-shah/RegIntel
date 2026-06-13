export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  tenant_id: string;
  role: "admin" | "consultant" | "viewer";
};

export type UserResponse = {
  user_id: string;
  email: string;
  role: string;
  tenant_id: string;
};

export type BriefSummary = {
  brief_id: string;
  client_id: string;
  title: string;
  severity: string;
  confidence: number;
  generated_at: string;
  status: string;
};

export type BriefList = {
  items: BriefSummary[];
  page: number;
  page_size: number;
  total: number;
};

export type CitationDetail = {
  clause_id: string;
  source_url: string;
  excerpt: string;
};

export type AgentTraceSummary = {
  agent_name: string;
  model_used: string;
  tokens_in: number;
  tokens_out: number;
  latency_ms: number;
};

export type BriefDetail = {
  brief_id: string;
  client_id: string;
  title: string;
  change_summary: string;
  severity: string;
  obligations: Array<{ text: string; deadline?: string | null; citations?: string[] }>;
  recommended_actions: string[];
  citations: CitationDetail[];
  confidence: number;
  generated_at: string;
  status: string;
  disclaimer: string;
  agent_trace: AgentTraceSummary[];
};

export type Profile = {
  client_id: string;
  name: string;
  naics_codes: string[];
  states_of_operation: string[];
  product_categories: string[];
  supply_chain_jurisdictions: string[];
  created_at: string;
  updated_at: string;
};

export type ProfileList = {
  items: Profile[];
  page: number;
  page_size: number;
  total: number;
};

export type QueryResponse = {
  answer: string;
  citations: CitationDetail[];
  confidence: number;
  status: string;
  disclaimer: string;
};

export type ChangeSummary = {
  change_id: string;
  document_id: string;
  clause_id: string;
  change_type: string;
  severity: string;
  summary: string | null;
  detected_at: string;
  affected_client_count: number;
};

export type ChangeList = {
  items: ChangeSummary[];
  page: number;
  page_size: number;
  total: number;
};

export type ConsultantDashboard = {
  tenant_id: string;
  client_count: number;
  recent_briefs: BriefSummary[];
  total_changes: number;
  low_confidence_briefs: number;
};

export type TriageItem = {
  client_id: string;
  relevance_score: number;
  hop_path: string[];
  matched_categories: string[];
};

export type GraphNodeKind = "Regulation" | "Clause" | "BusinessCategory" | "ClientProfile";

export type GraphNodeData = {
  id: string;
  kind: GraphNodeKind;
  label: string;
  subtitle?: string;
  clauseText?: string;
  effectiveDate?: string;
  sourceUrl?: string;
};

export type GraphEdgeData = {
  id: string;
  source: string;
  target: string;
  type: "AMENDS" | "REFERENCES" | "APPLIES_TO" | "PART_OF" | "AFFECTED_BY";
};

export type GraphExplorerPayload = {
  nodes: GraphNodeData[];
  edges: GraphEdgeData[];
  paths: Record<string, string[]>;
};

export type IngestionSourceStatus = {
  source: string;
  status: string;
  document_count: number;
  last_success_at: string;
  age_hours: number;
  stale: boolean;
  error_message: string | null;
};

export type IngestionStatusResponse = {
  staleness_threshold_hours: number;
  sources: IngestionSourceStatus[];
};

export type EvalLatestResponse =
  | {
      status: "no_runs";
      message: string;
    }
  | {
      suite: string;
      cases: number;
      accuracy: number;
      threshold: number;
      passed: boolean;
      created_at: string;
      failures: Array<Record<string, unknown>>;
    };

export type CostSummaryResponse = {
  period_days: number;
  total_cost_usd: number;
  briefs_generated: number;
  cost_per_brief_usd: number;
  target_cost_per_brief_usd: number;
  tenant_daily_cap_usd: number;
  global_daily_cap_usd: number;
};

export type EvalTrendPoint = {
  date: string;
  accuracy: number;
  cases: number;
};

export type CostTrendPoint = {
  date: string;
  cost_per_brief: number;
  briefs: number;
};

export type AdminTrendsResponse = {
  period_days: number;
  eval: EvalTrendPoint[];
  cost: CostTrendPoint[];
};
