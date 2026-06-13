"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Background,
  Controls,
  MiniMap,
  Panel,
  ReactFlow,
  type Edge,
  type Node,
  useEdgesState,
  useNodesState,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { ExternalLink, Route } from "lucide-react";
import { DEMO_GRAPH, getNodeById, resolvePath } from "@/lib/graph-data";
import type { GraphNodeData, GraphNodeKind } from "@/lib/types";
import { GraphLegend, useRegIntelNodeTypes } from "@/components/features/graph-node";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/input";
import { HopPathVisualizer } from "@/components/ui/hop-path-visualizer";
import { Badge } from "@/components/ui/badge";

const LAYOUT: Record<string, { x: number; y: number }> = {
  "reg-fda": { x: 40, y: 80 },
  "reg-sec": { x: 40, y: 320 },
  "clause-fda-overview": { x: 280, y: 40 },
  "clause-ecfr-101": { x: 280, y: 160 },
  "clause-sec-edgar": { x: 280, y: 320 },
  "cat-seafood": { x: 540, y: 100 },
  "cat-filings": { x: 540, y: 320 },
  "client-acme": { x: 800, y: 80 },
  "client-holdco": { x: 800, y: 320 },
};

function toFlowNodes(
  nodes: GraphNodeData[],
  highlightSet: Set<string>,
  hasHighlight: boolean,
  selectedNodeId: string | null,
): Node[] {
  return nodes.map((node) => ({
    id: node.id,
    type: "regintel",
    position: LAYOUT[node.id] ?? { x: 0, y: 0 },
    data: {
      kind: node.kind,
      label: node.label,
      subtitle: node.subtitle,
      highlighted: highlightSet.has(node.id),
      dimmed: hasHighlight && !highlightSet.has(node.id),
      selected: selectedNodeId === node.id,
    },
  }));
}

function toFlowEdges(
  edges: typeof DEMO_GRAPH.edges,
  highlightSet: Set<string>,
  pathIds: string[],
): Edge[] {
  return edges.map((edge) => {
    const pathEdge = pathIds.some(
      (nodeId, i) => i < pathIds.length - 1 && edge.source === pathIds[i] && edge.target === pathIds[i + 1],
    );

    return {
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.type,
      labelStyle: { fill: "#64748b", fontSize: 9, fontWeight: 500 },
      labelBgStyle: { fill: "transparent" },
      animated: pathEdge,
      style: {
        stroke: pathEdge ? "#2dd4bf" : highlightSet.size > 0 ? "#475569" : "#64748b",
        strokeWidth: pathEdge ? 2.5 : 1.5,
        opacity: highlightSet.size > 0 && !pathEdge ? 0.2 : 0.85,
      },
    };
  });
}

const SCENARIOS = [
  { clause: "sec:edgar:overview", client: "client-holdco", label: "SEC EDGAR → Meridian Holdings" },
  { clause: "fda:glossary:overview", client: "client-acme", label: "FDA overview → Acme Foods" },
  { clause: "ecfr:21:101:1", client: "client-acme", label: "21 CFR 101 → Acme Foods" },
];

export function GraphExplorerCanvas() {
  const [scenario, setScenario] = useState(SCENARIOS[0].label);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  const active = SCENARIOS.find((s) => s.label === scenario) ?? SCENARIOS[0];
  const pathIds = useMemo(
    () => resolvePath(DEMO_GRAPH, active.clause, active.client),
    [active.clause, active.client],
  );
  const highlightSet = useMemo(() => new Set(pathIds), [pathIds]);

  const buildGraph = useCallback(
    (path: string[], selectedId: string | null) => {
      const set = new Set(path);
      return {
        nodes: toFlowNodes(DEMO_GRAPH.nodes, set, path.length > 0, selectedId),
        edges: toFlowEdges(DEMO_GRAPH.edges, set, path),
      };
    },
    [],
  );

  const initial = useMemo(() => buildGraph(pathIds, pathIds[0] ?? null), [buildGraph, pathIds]);
  const [nodes, setNodes, onNodesChange] = useNodesState(initial.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initial.edges);
  const nodeTypes = useRegIntelNodeTypes();

  useEffect(() => {
    const first = pathIds[0] ?? null;
    setSelectedNodeId(first);
    const graph = buildGraph(pathIds, first);
    setNodes(graph.nodes);
    setEdges(graph.edges);
  }, [pathIds, buildGraph, setNodes, setEdges]);

  const onScenarioChange = (label: string) => {
    setScenario(label);
  };

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      setSelectedNodeId(node.id);
      const graph = buildGraph(pathIds, node.id);
      setNodes(graph.nodes);
    },
    [buildGraph, pathIds, setNodes],
  );

  const selected = selectedNodeId ? getNodeById(DEMO_GRAPH, selectedNodeId) : null;
  const pathLabels = pathIds.map((id) => getNodeById(DEMO_GRAPH, id)?.label ?? id);

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
      <Card className="overflow-hidden p-0" style={{ height: "min(72vh, 640px)" }}>
        <div className="flex flex-col gap-3 border-b border-slate-200/80 px-4 py-3 dark:border-white/[0.06] sm:flex-row sm:items-end sm:justify-between">
          <div className="min-w-[240px] flex-1">
            <Label className="text-[10px]">Impact path scenario</Label>
            <Select value={scenario} onChange={(e) => onScenarioChange(e.target.value)} className="mt-1">
              {SCENARIOS.map((s) => (
                <option key={s.label} value={s.label}>
                  {s.label}
                </option>
              ))}
            </Select>
          </div>
          <GraphLegend className="sm:pb-2" />
        </div>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.25 }}
          minZoom={0.4}
          maxZoom={1.5}
          proOptions={{ hideAttribution: true }}
          className="bg-slate-100/50 dark:bg-surface"
        >
          <Panel position="top-left" className="!m-3">
            <div className="rounded-xl border border-amber-200/80 bg-amber-50/95 px-3 py-2 text-xs text-amber-900 shadow-sm dark:border-amber-800/40 dark:bg-amber-950/80 dark:text-amber-200">
              Demo graph — live Neo4j explorer API coming soon.
            </div>
          </Panel>
          <Background gap={24} size={1} color="#475569" className="opacity-[0.15] dark:opacity-25" />
          <Controls
            showInteractive={false}
            className="!overflow-hidden !rounded-xl !border-slate-200 !shadow-sm dark:!border-white/10"
          />
          <MiniMap
            pannable
            zoomable
            className="!overflow-hidden !rounded-xl !border-slate-200 !shadow-sm dark:!border-white/10"
            nodeColor={(node) => {
              const kind = (node.data as { kind: GraphNodeKind }).kind;
              if (kind === "Clause") return "#14b8a6";
              if (kind === "ClientProfile") return "#34d399";
              if (kind === "Regulation") return "#818cf8";
              return "#fbbf24";
            }}
          />
          <Panel position="top-right" className="!m-3">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-brand/20 bg-brand/10 px-2.5 py-1 text-[10px] font-medium text-brand dark:text-brand-glow">
              <Route className="h-3 w-3" />
              {pathIds.length} hops
            </span>
          </Panel>
        </ReactFlow>
      </Card>

      <aside className="space-y-4 lg:sticky lg:top-24 lg:self-start">
        <Card className="border-brand/15 bg-gradient-to-br from-brand/5 to-transparent p-5">
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">Active path</p>
          <div className="mt-3">
            <HopPathVisualizer path={pathLabels} />
          </div>
          <p className="mt-3 text-xs text-muted">
            Clause → category → client profile. Animated edges show the verified hop sequence.
          </p>
        </Card>

        <Card className="p-5">
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">Selected node</p>
          {selected ? (
            <div className="mt-3 space-y-3 animate-fade-up">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <p className="font-display text-lg font-semibold text-slate-900 dark:text-white">
                    {selected.label}
                  </p>
                  <p className="text-xs capitalize text-muted">{selected.kind}</p>
                </div>
                {selected.kind === "Clause" && (
                  <Badge variant="brand" className="shrink-0 capitalize">
                    Source clause
                  </Badge>
                )}
              </div>
              {selected.subtitle && (
                <p className="text-sm text-slate-600 dark:text-slate-400">{selected.subtitle}</p>
              )}
              {selected.clauseText && (
                <blockquote className="rounded-xl border border-slate-200/80 bg-slate-50/80 px-3 py-3 text-sm italic leading-relaxed text-slate-600 dark:border-white/[0.06] dark:bg-surface-overlay/50 dark:text-slate-300">
                  &ldquo;{selected.clauseText}&rdquo;
                </blockquote>
              )}
              {selected.effectiveDate && (
                <p className="text-xs text-muted">Effective {selected.effectiveDate}</p>
              )}
              {selected.sourceUrl && (
                <Button variant="secondary" size="sm" asChild>
                  <a href={selected.sourceUrl} target="_blank" rel="noreferrer" className="no-underline">
                    View source
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                </Button>
              )}
            </div>
          ) : (
            <p className="mt-3 text-sm text-muted">Click a node to inspect clause text and metadata.</p>
          )}
        </Card>
      </aside>
    </div>
  );
}
