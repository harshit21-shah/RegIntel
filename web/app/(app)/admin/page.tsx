"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle, CheckCircle2, Database, DollarSign } from "lucide-react";
import { api } from "@/lib/api-client";
import type { EvalLatestResponse } from "@/lib/types";
import { formatSource } from "@/lib/utils";
import { PageHeader, Skeleton, StatCard } from "@/components/ui";
import { ErrorState } from "@/components/ui/error-state";
import { Card } from "@/components/ui/card";
import {
  CostPerBriefChart,
  EvalAccuracyChart,
  IngestionStalenessChart,
} from "@/components/features/admin-charts";

function isEvalRun(
  data: EvalLatestResponse,
): data is Extract<EvalLatestResponse, { accuracy: number }> {
  return "accuracy" in data;
}

export default function AdminMonitoringPage() {
  const ingestion = useQuery({
    queryKey: ["admin", "ingestion"],
    queryFn: () => api.admin.ingestionStatus(),
  });

  const evalLatest = useQuery({
    queryKey: ["admin", "eval"],
    queryFn: () => api.admin.evalLatest(),
  });

  const cost = useQuery({
    queryKey: ["admin", "cost"],
    queryFn: () => api.admin.costSummary(7),
  });

  const trends = useQuery({
    queryKey: ["admin", "trends"],
    queryFn: () => api.admin.trends(7),
  });

  const loading = ingestion.isLoading || evalLatest.isLoading || cost.isLoading || trends.isLoading;
  const error = ingestion.error || evalLatest.error || cost.error || trends.error;
  const evalData = evalLatest.data;

  if (error) {
    return (
      <>
        <PageHeader title="Ingestion & eval monitoring" subtitle="Admin-only operational dashboard." />
        <ErrorState
          message={error instanceof Error ? error.message : "Failed to load admin metrics"}
          onRetry={() => {
            void ingestion.refetch();
            void evalLatest.refetch();
            void cost.refetch();
            void trends.refetch();
          }}
        />
      </>
    );
  }

  return (
    <>
      <PageHeader
        title="Ingestion & eval monitoring"
        subtitle="Source staleness, citation accuracy, and pipeline cost (admin only)."
      />

      {loading ? (
        <div className="mb-8 grid gap-4 sm:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      ) : (
        <div className="mb-8 grid gap-4 sm:grid-cols-3">
          <StatCard
            label="Sources tracked"
            value={ingestion.data?.sources.length ?? 0}
            hint={`Stale after ${ingestion.data?.staleness_threshold_hours ?? "—"}h`}
            accent="brand"
            icon={<Database className="h-4 w-4 text-brand dark:text-brand-glow" />}
          />
          <StatCard
            label="Citation accuracy"
            value={
              evalData && isEvalRun(evalData) ? `${(evalData.accuracy * 100).toFixed(1)}%` : "—"
            }
            hint={
              evalData && isEvalRun(evalData)
                ? `${evalData.suite} · ${evalData.cases} cases`
                : "No eval runs yet"
            }
            accent={evalData && isEvalRun(evalData) && evalData.passed ? "brand" : "warning"}
            icon={
              evalData && isEvalRun(evalData) && evalData.passed ? (
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              ) : (
                <AlertTriangle className="h-4 w-4 text-amber-500" />
              )
            }
          />
          <StatCard
            label="Cost / brief (7d)"
            value={`$${cost.data?.cost_per_brief_usd.toFixed(3) ?? "—"}`}
            hint={`Target $${cost.data?.target_cost_per_brief_usd.toFixed(2) ?? "0.50"} · ${cost.data?.briefs_generated ?? 0} briefs`}
            icon={<DollarSign className="h-4 w-4 text-indigo-500" />}
          />
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        {loading ? (
          <>
            <Skeleton className="h-72" />
            <Skeleton className="h-72" />
          </>
        ) : (
          <>
            {ingestion.data && <IngestionStalenessChart sources={ingestion.data.sources} />}
            <EvalAccuracyChart
              points={trends.data?.eval ?? []}
              threshold={evalData && isEvalRun(evalData) ? evalData.threshold : 0.9}
            />
            <CostPerBriefChart
              points={trends.data?.cost ?? []}
              target={cost.data?.target_cost_per_brief_usd ?? 0.5}
            />
          </>
        )}

        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2">
            <Activity className="h-4 w-4 text-brand dark:text-brand-glow" />
            <p className="text-sm font-medium text-slate-900 dark:text-white">Ingestion detail</p>
          </div>
          {loading ? (
            <div className="space-y-2">
              <Skeleton className="h-12" />
              <Skeleton className="h-12" />
            </div>
          ) : (
            <ul className="space-y-2">
              {(ingestion.data?.sources ?? []).map((source) => (
                <li
                  key={source.source}
                  className="flex items-center justify-between rounded-xl border border-slate-200/80 px-3 py-2.5 transition hover:border-slate-300 dark:border-white/[0.06] dark:hover:border-white/[0.1]"
                >
                  <div>
                    <p className="text-sm font-medium text-slate-900 dark:text-white">
                      {formatSource(source.source)}
                    </p>
                    <p className="text-xs text-muted">
                      {source.document_count} docs · {source.status} · {source.age_hours.toFixed(0)}h ago
                    </p>
                  </div>
                  <span
                    className={
                      source.stale
                        ? "rounded-full bg-amber-500/15 px-2 py-0.5 text-[10px] font-semibold uppercase text-amber-600 dark:text-amber-400"
                        : "rounded-full bg-emerald-500/15 px-2 py-0.5 text-[10px] font-semibold uppercase text-emerald-600 dark:text-emerald-400"
                    }
                  >
                    {source.stale ? "Stale" : "Fresh"}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </>
  );
}
