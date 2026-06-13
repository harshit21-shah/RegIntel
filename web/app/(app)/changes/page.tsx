"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { ArrowRight, FileDiff, Users } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import type { ChangeList } from "@/lib/types";
import {
  formatChangeType,
  formatRelativeTime,
  formatSource,
  severityVariant,
} from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/input";
import { EmptyState, FilterBar, ListCard, Loading, PageHeader, Pagination } from "@/components/ui";

function sourceFromDocumentId(documentId: string): string {
  const prefix = documentId.split(":")[0] ?? documentId.split("/")[0] ?? "";
  return formatSource(prefix);
}

export default function ChangesPage() {
  const [page, setPage] = useState(1);
  const [severity, setSeverity] = useState("");
  const [source, setSource] = useState("");

  const filters = { page, severity, source };

  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.changes(filters),
    queryFn: () => {
      const params = new URLSearchParams({ page: String(page), page_size: "20" });
      if (severity) params.set("severity", severity);
      if (source) params.set("source", source);
      return apiFetch<ChangeList>(`/api/v1/changes?${params}`);
    },
  });

  const totalPages = Math.max(1, Math.ceil((data?.total ?? 0) / 20));

  return (
    <>
      <PageHeader
        title="Regulatory Changes"
        subtitle="Clause-level diffs detected across ingested regulatory sources."
      />

      <FilterBar>
        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <Label>Severity</Label>
            <Select value={severity} onChange={(e) => { setPage(1); setSeverity(e.target.value); }}>
              <option value="">All severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="SUBSTANTIVE">Substantive</option>
              <option value="COSMETIC">Cosmetic</option>
            </Select>
          </div>
          <div>
            <Label>Source</Label>
            <Select value={source} onChange={(e) => { setPage(1); setSource(e.target.value); }}>
              <option value="">All sources</option>
              <option value="ecfr">eCFR</option>
              <option value="federal_register">Federal Register</option>
              <option value="ca_food_code">CA Food Code</option>
              <option value="sec_edgar">SEC EDGAR</option>
            </Select>
          </div>
          <div className="flex items-end">
            <Button variant="secondary" onClick={() => { setSeverity(""); setSource(""); setPage(1); }}>
              Clear filters
            </Button>
          </div>
        </div>
      </FilterBar>

      {error && (
        <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900/40 dark:bg-red-950/20 dark:text-red-300">
          {error instanceof Error ? error.message : "Failed to load changes"}
        </div>
      )}

      {isLoading ? (
        <Loading label="Loading changes" />
      ) : !data?.items.length ? (
        <EmptyState title="No changes yet" message="Run ingestion to populate the regulatory change feed." />
      ) : (
        <ul className="space-y-3">
          {data.items.map((change) => (
            <li key={change.change_id}>
              <Link href={`/changes/${change.change_id}`} className="group block no-underline">
                <ListCard className="group-hover:-translate-y-0.5">
                  <div className="flex items-start gap-4">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-slate-200 bg-slate-50 text-brand dark:border-white/[0.08] dark:bg-surface-overlay dark:text-brand-glow">
                      <FileDiff className="h-4 w-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="truncate font-mono text-sm text-brand dark:text-brand-glow">
                          {change.clause_id}
                        </p>
                        <Badge variant="default">{formatChangeType(change.change_type)}</Badge>
                      </div>
                      <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-slate-600 dark:text-slate-300">
                        {change.summary || "No summary available for this change."}
                      </p>
                      <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-500">
                        <span>{sourceFromDocumentId(change.document_id)}</span>
                        <span aria-hidden>·</span>
                        <span>{formatRelativeTime(change.detected_at)}</span>
                        <span aria-hidden>·</span>
                        <span className="inline-flex items-center gap-1">
                          <Users className="h-3 w-3" />
                          {change.affected_client_count} brief
                          {change.affected_client_count !== 1 ? "s" : ""}
                        </span>
                      </div>
                    </div>
                    <div className="flex shrink-0 flex-col items-end gap-2">
                      <Badge variant={severityVariant(change.severity)}>{change.severity}</Badge>
                      <ArrowRight className="h-4 w-4 text-slate-300 transition group-hover:translate-x-0.5 group-hover:text-brand-glow" />
                    </div>
                  </div>
                </ListCard>
              </Link>
            </li>
          ))}
        </ul>
      )}

      <Pagination page={page} totalPages={totalPages} total={data?.total} onPageChange={setPage} />
    </>
  );
}
