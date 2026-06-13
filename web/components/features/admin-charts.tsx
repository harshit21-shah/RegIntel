"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { IngestionSourceStatus } from "@/lib/types";
import { formatSource } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function IngestionStalenessChart({ sources }: { sources: IngestionSourceStatus[] }) {
  const data = sources.map((s) => ({
    name: formatSource(s.source),
    age: s.age_hours,
    stale: s.stale,
    docs: s.document_count,
  }));

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Ingestion staleness (hours)</CardTitle>
        <p className="text-xs text-muted">Amber bars exceed staleness threshold</p>
      </CardHeader>
      <CardContent className="h-64">
        {data.length === 0 ? (
          <p className="text-sm text-slate-500">No ingestion runs recorded.</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} />
              <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  background: "#111827",
                  border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: 12,
                  fontSize: 12,
                }}
              />
              <Bar dataKey="age" radius={[6, 6, 0, 0]}>
                {data.map((entry, index) => (
                  <Cell key={index} fill={entry.stale ? "#f59e0b" : "#14b8a6"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}

export function EvalAccuracyChart({
  points,
  threshold,
}: {
  points: Array<{ date: string; accuracy: number }>;
  threshold: number;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Citation accuracy trend</CardTitle>
        <p className="text-xs text-muted">7-day trend · dashed line = pass threshold</p>
      </CardHeader>
      <CardContent className="h-64">
        {points.length === 0 ? (
          <p className="text-sm text-slate-500">No eval runs in this period.</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={points} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} />
              <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis domain={[0.7, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  background: "#111827",
                  border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: 12,
                  fontSize: 12,
                }}
              />
              <Line
                type="monotone"
                dataKey="accuracy"
                stroke="#2dd4bf"
                strokeWidth={2}
                dot={{ fill: "#14b8a6", r: 3 }}
              />
              <ReferenceLine y={threshold} stroke="#64748b" strokeDasharray="4 4" label="Threshold" />
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}

export function CostPerBriefChart({
  points,
  target,
}: {
  points: Array<{ date: string; cost_per_brief: number }>;
  target: number;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Cost per brief (USD)</CardTitle>
        <p className="text-xs text-muted">7-day trend · dashed line = target cap</p>
      </CardHeader>
      <CardContent className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} />
            <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <Tooltip
              contentStyle={{
                background: "#111827",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: 12,
                fontSize: 12,
              }}
            />
            <Line
              type="monotone"
              dataKey="cost_per_brief"
              stroke="#818cf8"
              strokeWidth={2}
              dot={{ fill: "#6366f1", r: 3 }}
            />
            <ReferenceLine y={target} stroke="#64748b" strokeDasharray="4 4" label="Target" />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
