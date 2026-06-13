"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, FileDiff } from "lucide-react";
import { api } from "@/lib/api-client";
import { queryKeys } from "@/lib/query-keys";
import type { ChangeSummary } from "@/lib/types";
import { formatRelativeTime } from "@/lib/utils";
import { SeverityBadge } from "@/components/ui/severity-badge";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function ChangesFeedWidget() {
  const { data, isLoading } = useQuery({
    queryKey: queryKeys.changes({ page: 1, severity: "", source: "" }),
    queryFn: () => api.changes.list({ page: 1, page_size: 5 }),
  });

  if (isLoading) {
    return (
      <Card className="p-5">
        <Skeleton className="mb-4 h-5 w-40" />
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-14" />
          ))}
        </div>
      </Card>
    );
  }

  const items = data?.items ?? [];

  return (
    <Card className="p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-lg font-semibold text-slate-900 dark:text-white">Changes feed</h2>
        <Link href="/changes" className="text-sm text-brand no-underline hover:text-brand-glow">
          View all →
        </Link>
      </div>
      {items.length === 0 ? (
        <p className="text-sm text-slate-500">No regulatory changes detected yet.</p>
      ) : (
        <ul className="space-y-2">
          {items.map((change: ChangeSummary) => (
            <li key={change.change_id}>
              <Link href={`/changes/${change.change_id}`} className="group block no-underline">
                <div className="flex items-start gap-3 rounded-xl border border-transparent px-3 py-3 transition hover:border-slate-200 hover:bg-slate-50 dark:hover:border-white/[0.06] dark:hover:bg-white/[0.02]">
                  <FileDiff className="mt-0.5 h-4 w-4 shrink-0 text-brand dark:text-brand-glow" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-mono text-xs text-brand dark:text-brand-glow">
                      {change.clause_id}
                    </p>
                    <p className="mt-1 line-clamp-1 text-sm text-slate-600 dark:text-slate-400">
                      {change.summary ?? change.change_type}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">
                      {change.affected_client_count} clients · {formatRelativeTime(change.detected_at)}
                    </p>
                  </div>
                  <SeverityBadge severity={change.severity} className="shrink-0" />
                  <ArrowRight className="mt-1 h-4 w-4 shrink-0 text-slate-300 opacity-0 transition group-hover:opacity-100" />
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
