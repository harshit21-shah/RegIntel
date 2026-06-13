import type { GraphExplorerPayload } from "@/lib/types";

/** Demo graph illustrating multi-hop regulatory → client impact paths. */
export const DEMO_GRAPH: GraphExplorerPayload = {
  nodes: [
    {
      id: "reg-fda",
      kind: "Regulation",
      label: "FDA Food Safety",
      subtitle: "21 CFR Parts 1, 101, 117",
      effectiveDate: "2026-01-01",
    },
    {
      id: "reg-sec",
      kind: "Regulation",
      label: "SEC Disclosure",
      subtitle: "Exchange Act · EDGAR",
      effectiveDate: "2026-01-01",
    },
    {
      id: "clause-fda-overview",
      kind: "Clause",
      label: "fda:glossary:overview",
      subtitle: "FDA mission & jurisdiction",
      clauseText:
        "The FDA is responsible for protecting public health by assuring the safety, efficacy, and security of drugs, devices, and the food supply.",
      sourceUrl: "https://www.fda.gov/about-fda",
    },
    {
      id: "clause-sec-edgar",
      kind: "Clause",
      label: "sec:edgar:overview",
      subtitle: "EDGAR filing system",
      clauseText:
        "EDGAR is the Electronic Data Gathering, Analysis, and Retrieval system used for SEC filings.",
      sourceUrl: "https://www.sec.gov/edgar",
    },
    {
      id: "clause-ecfr-101",
      kind: "Clause",
      label: "ecfr:21:101:1",
      subtitle: "Food labeling — principal display panel",
      clauseText:
        "The principal display panel of a food package shall bear the statement of identity and net quantity of contents.",
      sourceUrl: "https://www.ecfr.gov/current/title-21/section-101.1",
      effectiveDate: "2026-06-01",
    },
    {
      id: "cat-seafood",
      kind: "BusinessCategory",
      label: "Frozen seafood",
      subtitle: "NAICS 311412",
    },
    {
      id: "cat-filings",
      kind: "BusinessCategory",
      label: "Public company filings",
      subtitle: "NAICS 551112",
    },
    {
      id: "client-acme",
      kind: "ClientProfile",
      label: "Acme Foods Inc.",
      subtitle: "CA · TX · frozen seafood",
    },
    {
      id: "client-holdco",
      kind: "ClientProfile",
      label: "Meridian Holdings",
      subtitle: "SEC registrant · multi-state",
    },
  ],
  edges: [
    { id: "e1", source: "clause-fda-overview", target: "reg-fda", type: "PART_OF" },
    { id: "e2", source: "clause-ecfr-101", target: "reg-fda", type: "PART_OF" },
    { id: "e3", source: "clause-sec-edgar", target: "reg-sec", type: "PART_OF" },
    { id: "e4", source: "reg-fda", target: "clause-ecfr-101", type: "AMENDS" },
    { id: "e5", source: "clause-ecfr-101", target: "clause-fda-overview", type: "REFERENCES" },
    { id: "e6", source: "cat-seafood", target: "clause-ecfr-101", type: "APPLIES_TO" },
    { id: "e7", source: "cat-seafood", target: "clause-fda-overview", type: "APPLIES_TO" },
    { id: "e8", source: "cat-filings", target: "clause-sec-edgar", type: "APPLIES_TO" },
    { id: "e9", source: "client-acme", target: "cat-seafood", type: "AFFECTED_BY" },
    { id: "e10", source: "client-holdco", target: "cat-filings", type: "AFFECTED_BY" },
  ],
  paths: {
    "sec:edgar:overview:client-holdco": [
      "clause-sec-edgar",
      "cat-filings",
      "client-holdco",
    ],
    "fda:glossary:overview:client-acme": [
      "clause-fda-overview",
      "cat-seafood",
      "client-acme",
    ],
    "ecfr:21:101:1:client-acme": [
      "clause-ecfr-101",
      "cat-seafood",
      "client-acme",
    ],
  },
};

export function pathKey(clauseId: string, clientNodeId: string): string {
  return `${clauseId}:${clientNodeId}`;
}

export function resolvePath(
  graph: GraphExplorerPayload,
  clauseId: string,
  clientId: string,
): string[] {
  const clientNode = graph.nodes.find(
    (n) => n.kind === "ClientProfile" && (n.id === clientId || n.label.toLowerCase().includes(clientId.slice(0, 4))),
  );
  if (!clientNode) return graph.paths[`${clauseId}:${clientId}`] ?? [];

  for (const [key, path] of Object.entries(graph.paths)) {
    if (key.startsWith(clauseId) && path.includes(clientNode.id)) return path;
  }

  const clauseNode = graph.nodes.find((n) => n.label === clauseId || n.id.includes(clauseId.replace(/:/g, "-")));
  if (!clauseNode) return [];

  return graph.paths[`${clauseId}:${clientNode.id}`] ?? graph.paths[pathKey(clauseNode.label, clientNode.id)] ?? [];
}

export function getNodeById(graph: GraphExplorerPayload, id: string) {
  return graph.nodes.find((n) => n.id === id);
}
