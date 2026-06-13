"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api-client";
import { queryKeys } from "@/lib/query-keys";
import { useAppStore } from "@/stores/app-store";
import { BriefsTable, BriefsTableSkeleton } from "@/components/features/briefs-table";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/input";
import { EmptyState, PageHeader, Pagination } from "@/components/ui";
import { ErrorState } from "@/components/ui/error-state";

export default function BriefsPage() {
  const [page, setPage] = useState(1);
  const { briefFilters, setBriefFilters, resetBriefFilters } = useAppStore();
  const { severity, status, clientId } = briefFilters;
  const filters = { page, severity, status, clientId };

  const { data: profiles } = useQuery({
    queryKey: queryKeys.profiles(1),
    queryFn: () => api.profiles.list(1, 100),
  });

  const clientNames = Object.fromEntries((profiles?.items ?? []).map((p) => [p.client_id, p.name]));

  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey: queryKeys.briefs(filters),
    queryFn: () =>
      api.briefs.list({
        page,
        page_size: 20,
        severity: severity || undefined,
        status: status || undefined,
        client_id: clientId || undefined,
      }),
  });

  const totalPages = Math.max(1, Math.ceil((data?.total ?? 0) / 20));

  return (
    <>
      <PageHeader
        title="Brief Inbox"
        subtitle="AI-generated compliance briefs with verified source citations."
      />

      <div className="sticky top-14 z-10 -mx-4 mb-6 border-b border-slate-200/80 bg-white/90 px-4 py-4 backdrop-blur-xl dark:border-white/[0.06] dark:bg-surface/90 sm:-mx-8 sm:px-8 lg:top-[3.5rem]">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <Label>Severity</Label>
            <Select
              value={severity}
              onChange={(e) => {
                setPage(1);
                setBriefFilters({ severity: e.target.value });
              }}
            >
              <option value="">All severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="SUBSTANTIVE">Substantive</option>
              <option value="COSMETIC">Cosmetic</option>
            </Select>
          </div>
          <div>
            <Label>Status</Label>
            <Select
              value={status}
              onChange={(e) => {
                setPage(1);
                setBriefFilters({ status: e.target.value });
              }}
            >
              <option value="">All statuses</option>
              <option value="COMPLETE">Complete</option>
              <option value="LOW_CONFIDENCE">Low confidence</option>
            </Select>
          </div>
          <div>
            <Label>Client</Label>
            <Select
              value={clientId}
              onChange={(e) => {
                setPage(1);
                setBriefFilters({ clientId: e.target.value });
              }}
            >
              <option value="">All clients</option>
              {(profiles?.items ?? []).map((p) => (
                <option key={p.client_id} value={p.client_id}>
                  {p.name}
                </option>
              ))}
            </Select>
          </div>
          <div className="flex items-end gap-2">
            <Button
              variant="secondary"
              className="w-full sm:w-auto"
              onClick={() => {
                resetBriefFilters();
                setPage(1);
              }}
            >
              Clear filters
            </Button>
            {isFetching && !isLoading && (
              <span className="pb-2 text-xs text-slate-500">Updating…</span>
            )}
          </div>
        </div>
      </div>

      {error && (
        <ErrorState
          message={error instanceof Error ? error.message : "Failed to load briefs"}
          onRetry={() => void refetch()}
        />
      )}

      {!error && isLoading ? (
        <BriefsTableSkeleton />
      ) : !error && !data?.items.length ? (
        <EmptyState
          title="No briefs found"
          message="No briefs match your filters. Try clearing filters or run ingestion."
          action={
            <Button variant="secondary" onClick={() => { resetBriefFilters(); setPage(1); }}>
              Clear filters
            </Button>
          }
        />
      ) : !error && data ? (
        <BriefsTable items={data.items} clientNames={clientNames} />
      ) : null}

      <Pagination page={page} totalPages={totalPages} total={data?.total} onPageChange={setPage} />
    </>
  );
}
