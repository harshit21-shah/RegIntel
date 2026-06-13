"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight } from "lucide-react";
import { api } from "@/lib/api-client";
import { queryKeys } from "@/lib/query-keys";
import { formatRelativeTime } from "@/lib/utils";
import { SeverityBadge } from "@/components/ui/severity-badge";
import { EmptyState, PageHeader, Skeleton } from "@/components/ui";
import { ErrorState } from "@/components/ui/error-state";
import { Card } from "@/components/ui/card";

export default function TriagePage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: queryKeys.changes({ page: 1, severity: "", source: "" }),
    queryFn: () => api.changes.list({ page: 1, page_size: 50 }),
  });

  return (
    <>
      <PageHeader
        title="Cross-client triage"
        subtitle="Regulatory changes ranked by affected client count — open a change to run relevance triage."
      />

      {error && (
        <ErrorState
          message={error instanceof Error ? error.message : "Failed to load changes"}
          onRetry={() => void refetch()}
        />
      )}

      {isLoading && (
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-16" />
          ))}
        </div>
      )}

      {!error && !isLoading && (
        <div className="overflow-hidden rounded-2xl border border-slate-200/80 dark:border-white/[0.08]">
          <table className="w-full text-left text-sm">
            <thead className="sticky top-0 z-10 bg-slate-50/95 text-xs uppercase tracking-wider text-muted backdrop-blur dark:bg-surface/95">
              <tr>
                <th className="px-4 py-3 font-medium">Clause</th>
                <th className="px-4 py-3 font-medium">Summary</th>
                <th className="px-4 py-3 font-medium">Severity</th>
                <th className="px-4 py-3 font-medium">Affected clients</th>
                <th className="px-4 py-3 font-medium">Detected</th>
                <th className="px-4 py-3 font-medium" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-white/[0.06]">
              {(data?.items ?? []).map((change) => (
                <tr key={change.change_id} className="group transition hover:bg-slate-50 dark:hover:bg-white/[0.02]">
                  <td className="px-4 py-3 font-mono text-xs text-brand dark:text-brand-glow">
                    {change.clause_id}
                  </td>
                  <td className="max-w-md px-4 py-3 text-slate-600 dark:text-slate-300">
                    {change.summary ?? change.change_type}
                  </td>
                  <td className="px-4 py-3">
                    <SeverityBadge severity={change.severity} />
                  </td>
                  <td className="px-4 py-3 tabular-nums">{change.affected_client_count}</td>
                  <td className="px-4 py-3 text-xs text-slate-500">
                    {formatRelativeTime(change.detected_at)}
                  </td>
                  <td className="px-4 py-3">
                    <Link
                      href={`/changes/${change.change_id}`}
                      className="inline-flex items-center gap-1 text-xs font-medium text-brand no-underline hover:text-brand-glow"
                    >
                      Triage
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!error && !isLoading && (data?.items.length ?? 0) === 0 && (
        <EmptyState title="Nothing to triage" message="Run ingestion to populate the regulatory change feed." />
      )}
    </>
  );
}
