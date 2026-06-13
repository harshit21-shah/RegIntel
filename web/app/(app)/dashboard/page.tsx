"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import {
  AlertTriangle,
  ArrowRight,
  FileText,
  MessageSquare,
  TrendingUp,
  Users,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { useAuth } from "@/lib/auth";
import type { BriefSummary, ConsultantDashboard } from "@/lib/types";
import { formatRelativeTime, severityVariant, statusVariant } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState, PageHeader, Skeleton, StatCard } from "@/components/ui";
import { ChangesFeedWidget } from "@/components/features/changes-feed-widget";

const QUICK_ACTIONS = [
  {
    href: "/query",
    label: "New query",
    description: "Ask a regulatory question",
    icon: MessageSquare,
    accent: "brand" as const,
  },
  {
    href: "/briefs",
    label: "Brief inbox",
    description: "Review compliance briefs",
    icon: FileText,
    accent: "default" as const,
  },
  {
    href: "/changes",
    label: "Changes",
    description: "Clause-level diffs",
    icon: TrendingUp,
    accent: "default" as const,
  },
  {
    href: "/profiles",
    label: "Profiles",
    description: "Client context",
    icon: Users,
    accent: "default" as const,
  },
];

export default function DashboardPage() {
  const { session } = useAuth();

  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: () => apiFetch<ConsultantDashboard>("/api/v1/consultant/dashboard"),
    enabled: session?.role !== "viewer",
  });

  if (session?.role === "viewer") {
    return (
      <>
        <PageHeader
          title={`Welcome${session.email ? `, ${session.email.split("@")[0]}` : ""}`}
          subtitle="Review briefs, track regulatory changes, and query indexed sources."
        />
        <div className="grid gap-4 sm:grid-cols-2">
          {QUICK_ACTIONS.slice(0, 2).map((item) => {
            const Icon = item.icon;
            return (
              <Link key={item.href} href={item.href} className="group no-underline">
                <Card className="h-full transition duration-300 hover:-translate-y-0.5 hover:border-brand/30 hover:shadow-glow">
                  <CardHeader>
                    <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-brand/10 text-brand dark:text-brand-glow">
                      <Icon className="h-5 w-5" />
                    </div>
                    <CardTitle className="text-lg text-slate-900 dark:text-white">{item.label}</CardTitle>
                    <CardDescription>{item.description}</CardDescription>
                  </CardHeader>
                </Card>
              </Link>
            );
          })}
        </div>
      </>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-red-700 dark:border-red-900/40 dark:bg-red-950/20 dark:text-red-300">
        {error instanceof Error ? error.message : "Failed to load dashboard"}
      </div>
    );
  }

  if (isLoading || !data) {
    return (
      <>
        <PageHeader title="Dashboard" subtitle="Cross-client regulatory intelligence at a glance." />
        <div className="mb-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
        <div className="mb-10 grid gap-4 sm:grid-cols-3">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
      </>
    );
  }

  return (
    <>
      <PageHeader
        title={`Good ${getGreeting()}${session?.email ? `, ${session.email.split("@")[0]}` : ""}`}
        subtitle="Cross-client regulatory intelligence at a glance."
      />

      <div className="mb-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {QUICK_ACTIONS.map((item) => {
          const Icon = item.icon;
          return (
            <Link key={item.href} href={item.href} className="group no-underline">
              <Card className="flex h-full items-center gap-3 p-4 transition duration-300 hover:border-brand/25 hover:shadow-glow">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand/10 text-brand dark:text-brand-glow">
                  <Icon className="h-5 w-5" />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-slate-900 group-hover:text-brand dark:text-white dark:group-hover:text-brand-glow">
                    {item.label}
                  </p>
                  <p className="truncate text-xs text-muted">{item.description}</p>
                </div>
                <ArrowRight className="ml-auto h-4 w-4 shrink-0 text-slate-300 transition group-hover:text-brand-glow" />
              </Card>
            </Link>
          );
        })}
      </div>

      <div className="mb-10 grid gap-4 sm:grid-cols-3">
        <StatCard
          label="Client profiles"
          value={data.client_count}
          hint="Active tenant profiles"
          accent="brand"
          icon={<Users className="h-4 w-4 text-brand-glow" />}
        />
        <StatCard
          label="Changes tracked"
          value={data.total_changes}
          hint="Clause-level diffs detected"
          icon={<TrendingUp className="h-4 w-4 text-slate-400" />}
        />
        <StatCard
          label="Needs review"
          value={data.low_confidence_briefs}
          hint="Low-confidence briefs"
          accent="warning"
          icon={<AlertTriangle className="h-4 w-4 text-amber-500" />}
        />
      </div>

      <div className="grid gap-8 lg:grid-cols-[1fr_380px]">
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-lg font-semibold text-slate-900 dark:text-white">Recent briefs</h2>
            <Link href="/briefs" className="text-sm text-brand no-underline hover:text-brand-glow">
              View all →
            </Link>
          </div>

          {data.recent_briefs.length === 0 ? (
            <EmptyState
              title="No briefs yet"
              message="Run ingestion and wait for regulatory changes to generate your first compliance brief."
            />
          ) : (
            <ul className="space-y-3">
              {data.recent_briefs.map((brief: BriefSummary) => (
                <li key={brief.brief_id}>
                  <Link href={`/briefs/${brief.brief_id}`} className="group block no-underline">
                    <Card className="p-5 transition duration-300 hover:border-brand/25 hover:shadow-glow">
                      <div className="flex items-start justify-between gap-4">
                        <div className="min-w-0">
                          <p className="truncate font-medium text-slate-900 group-hover:text-brand dark:text-white dark:group-hover:text-brand-glow">
                            {brief.title}
                          </p>
                          <p className="mt-1.5 text-xs text-muted">
                            {formatRelativeTime(brief.generated_at)} · {(brief.confidence * 100).toFixed(0)}% confidence
                          </p>
                        </div>
                        <div className="flex shrink-0 gap-2">
                          <Badge variant={severityVariant(brief.severity)}>{brief.severity}</Badge>
                          <Badge variant={statusVariant(brief.status)}>{brief.status}</Badge>
                        </div>
                      </div>
                    </Card>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>

        <ChangesFeedWidget />
      </div>
    </>
  );
}

function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "morning";
  if (hour < 17) return "afternoon";
  return "evening";
}
