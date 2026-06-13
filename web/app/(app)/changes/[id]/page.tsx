"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, GitBranch, Users } from "lucide-react";
import { api } from "@/lib/api-client";
import { apiFetch } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { useAuth } from "@/lib/auth";
import type { ProfileList, TriageItem } from "@/lib/types";
import { severityVariant } from "@/lib/utils";
import { usePageTitle } from "@/providers/page-title-provider";
import { RelevanceBar } from "@/components/features/relevance-bar";
import { HopPathVisualizer } from "@/components/ui/hop-path-visualizer";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { BackLink, EmptyState, ListCard, Loading, PageHeader, Skeleton } from "@/components/ui";

export default function ChangeDetailPage() {
  const params = useParams<{ id: string }>();
  const { session } = useAuth();
  const canTriage = session?.role === "admin" || session?.role === "consultant";

  const { data: change, isLoading: changeLoading } = useQuery({
    queryKey: queryKeys.change(params.id),
    queryFn: () => api.changes.get(params.id),
  });

  const { data: profiles } = useQuery({
    queryKey: queryKeys.profiles(1),
    queryFn: () => apiFetch<ProfileList>("/api/v1/profiles?page_size=100"),
  });

  const profileNames = Object.fromEntries(
    (profiles?.items ?? []).map((p) => [p.client_id, p.name]),
  );

  const {
    data: triage,
    isLoading: triageLoading,
    error,
  } = useQuery({
    queryKey: ["triage", params.id],
    queryFn: () =>
      apiFetch<{ items: TriageItem[] }>(`/api/v1/consultant/changes/${params.id}/triage`),
    enabled: canTriage,
  });

  const items = [...(triage?.items ?? [])].sort((a, b) => b.relevance_score - a.relevance_score);

  usePageTitle(change?.clause_id ?? "Client triage");

  return (
    <>
      <BackLink href="/changes">Back to changes</BackLink>

      {changeLoading ? (
        <Skeleton className="mb-8 h-24" />
      ) : change ? (
        <Card className="mb-8 p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="font-mono text-sm text-brand-glow">{change.clause_id}</p>
              <p className="mt-2 max-w-2xl text-slate-600 dark:text-slate-300">
                {change.summary || change.change_type}
              </p>
              <p className="mt-3 text-xs text-slate-500">
                {change.document_id} · {change.change_type} ·{" "}
                {new Date(change.detected_at).toLocaleString()}
              </p>
            </div>
            <Badge variant={severityVariant(change.severity)}>{change.severity}</Badge>
          </div>
        </Card>
      ) : null}

      <PageHeader
        title="Client triage"
        subtitle="Profiles ranked by graph relevance to this regulatory change."
      />

      {!canTriage && (
        <EmptyState message="Consultant or admin role required to view client triage." />
      )}

      {canTriage && error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-red-700 dark:border-red-900/40 dark:bg-red-950/20 dark:text-red-300">
          {error instanceof Error ? error.message : "Failed to load triage"}
        </div>
      )}

      {canTriage && triageLoading && <Loading label="Running relevance analysis" />}

      {canTriage && !triageLoading && !error && items.length === 0 && (
        <EmptyState message="No affected client profiles for this change." />
      )}

      {canTriage && items.length > 0 && (
        <>
          <div className="mb-6 grid gap-4 sm:grid-cols-3">
            <Card className="p-4">
              <div className="flex items-center gap-2 text-slate-500">
                <Users className="h-4 w-4" />
                <span className="text-xs uppercase tracking-wider">Affected clients</span>
              </div>
              <p className="mt-2 font-display text-3xl font-semibold text-slate-900 dark:text-white">
                {items.length}
              </p>
            </Card>
            <Card className="p-4">
              <div className="flex items-center gap-2 text-slate-500">
                <GitBranch className="h-4 w-4" />
                <span className="text-xs uppercase tracking-wider">High relevance</span>
              </div>
              <p className="mt-2 font-display text-3xl font-semibold text-emerald-500">
                {items.filter((i) => i.relevance_score >= 0.7).length}
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-xs uppercase tracking-wider text-slate-500">Top match</p>
              <p className="mt-2 truncate font-medium text-slate-900 dark:text-white">
                {profileNames[items[0].client_id] ?? items[0].client_id.slice(0, 8)}
              </p>
              <p className="text-sm text-brand-glow">{(items[0].relevance_score * 100).toFixed(0)}% relevant</p>
            </Card>
          </div>

          <ul className="space-y-3">
            {items.map((item) => (
              <li key={item.client_id}>
                <ListCard>
                  <div className="grid gap-4 lg:grid-cols-[1fr_200px_auto] lg:items-center">
                    <div>
                      <p className="font-display text-lg font-semibold text-slate-900 dark:text-white">
                        {profileNames[item.client_id] ?? "Unknown client"}
                      </p>
                      <p className="mt-1 font-mono text-xs text-slate-500">{item.client_id}</p>
                      <p className="mt-3 text-sm text-slate-500">
                        Categories: {item.matched_categories.join(", ") || "—"}
                      </p>
                      <div className="mt-2">
                        <p className="mb-1.5 text-xs text-slate-500">Graph path</p>
                        <HopPathVisualizer path={item.hop_path} />
                      </div>
                    </div>
                    <RelevanceBar score={item.relevance_score} />
                    <Link href={`/profiles/${item.client_id}/edit`} className="no-underline">
                      <Button variant="secondary" size="sm">
                        View profile
                        <ArrowRight className="h-3.5 w-3.5" />
                      </Button>
                    </Link>
                  </div>
                </ListCard>
              </li>
            ))}
          </ul>
        </>
      )}
    </>
  );
}
