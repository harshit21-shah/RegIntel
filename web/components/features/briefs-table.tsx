"use client";

import Link from "next/link";
import type { BriefSummary } from "@/lib/types";
import { formatRelativeTime } from "@/lib/utils";
import { SeverityBadge } from "@/components/ui/severity-badge";
import { Badge } from "@/components/ui/badge";
import { statusVariant } from "@/lib/utils";
import { ConfidenceGauge } from "@/components/ui/confidence-gauge";
import { Skeleton } from "@/components/ui/skeleton";

export function BriefsTableSkeleton() {
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200/80 dark:border-white/[0.08]">
      <div className="hidden bg-slate-50 px-4 py-3 dark:bg-surface/80 md:grid md:grid-cols-[1fr_120px_120px_100px_140px] md:gap-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <Skeleton key={i} className="h-3 w-20" />
        ))}
      </div>
      <div className="divide-y divide-slate-200 dark:divide-white/[0.06]">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="px-4 py-4">
            <Skeleton className="mb-2 h-4 w-2/3" />
            <Skeleton className="h-3 w-1/3" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function BriefsTable({
  items,
  clientNames,
}: {
  items: BriefSummary[];
  clientNames?: Record<string, string>;
}) {
  return (
    <>
      {/* Desktop table */}
      <div className="hidden overflow-hidden rounded-2xl border border-slate-200/80 dark:border-white/[0.08] md:block">
        <table className="w-full text-left text-sm">
          <thead className="sticky top-0 z-10 bg-slate-50/95 text-xs uppercase tracking-wider text-slate-500 backdrop-blur dark:bg-surface/95">
            <tr>
              <th className="px-4 py-3 font-medium">Brief</th>
              <th className="px-4 py-3 font-medium">Client</th>
              <th className="px-4 py-3 font-medium">Severity</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Confidence</th>
              <th className="px-4 py-3 font-medium">Generated</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-white/[0.06]">
            {items.map((brief) => (
              <tr
                key={brief.brief_id}
                className="group transition hover:bg-slate-50/80 dark:hover:bg-white/[0.02]"
              >
                <td className="max-w-md px-4 py-4">
                  <Link
                    href={`/briefs/${brief.brief_id}`}
                    className="block no-underline"
                  >
                    <p className="truncate font-medium text-slate-900 group-hover:text-brand dark:text-white dark:group-hover:text-brand-glow">
                      {brief.title}
                    </p>
                  </Link>
                </td>
                <td className="px-4 py-4 text-slate-600 dark:text-slate-400">
                  {clientNames?.[brief.client_id] ?? brief.client_id.slice(0, 8)}
                </td>
                <td className="px-4 py-4">
                  <SeverityBadge severity={brief.severity} />
                </td>
                <td className="px-4 py-4">
                  <Badge variant={statusVariant(brief.status)}>{brief.status}</Badge>
                </td>
                <td className="px-4 py-4">
                  <ConfidenceGauge score={brief.confidence} compact />
                </td>
                <td className="px-4 py-4 text-xs text-slate-500">
                  {formatRelativeTime(brief.generated_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile cards */}
      <ul className="space-y-3 md:hidden">
        {items.map((brief) => (
          <li key={brief.brief_id}>
            <Link href={`/briefs/${brief.brief_id}`} className="group block no-underline">
              <div className="glass-panel p-4 transition hover:border-brand/25 hover:shadow-glow">
                <p className="font-medium text-slate-900 group-hover:text-brand dark:text-white">
                  {brief.title}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <SeverityBadge severity={brief.severity} />
                  <Badge variant={statusVariant(brief.status)}>{brief.status}</Badge>
                </div>
                <p className="mt-2 text-xs text-slate-500">
                  {(brief.confidence * 100).toFixed(0)}% · {formatRelativeTime(brief.generated_at)}
                </p>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </>
  );
}
