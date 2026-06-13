"use client";

import { useParams } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  BookOpen,
  CheckCircle2,
  ListChecks,
  ShieldCheck,
  Sparkles,
  ThumbsDown,
  ThumbsUp,
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api-client";
import { queryKeys } from "@/lib/query-keys";
import { useAuth } from "@/lib/auth";
import { usePageTitle } from "@/providers/page-title-provider";
import { statusVariant } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { SeverityBadge } from "@/components/ui/severity-badge";
import { ConfidenceGauge } from "@/components/ui/confidence-gauge";
import { CitationCard } from "@/components/ui/citation-card";
import { ObligationTimeline } from "@/components/ui/obligation-timeline";
import { AgentTraceViewer } from "@/components/ui/agent-trace-viewer";
import { BackLink, EmptyState, PageHeader, Skeleton } from "@/components/ui";
import { ErrorState } from "@/components/ui/error-state";
import { useState } from "react";

export default function BriefDetailPage() {
  const params = useParams<{ id: string }>();
  const { session } = useAuth();
  const [comment, setComment] = useState("");

  const { data: brief, isLoading, error, refetch } = useQuery({
    queryKey: queryKeys.brief(params.id),
    queryFn: () => api.briefs.get(params.id),
  });

  usePageTitle(brief?.title);

  const feedbackMutation = useMutation({
    mutationFn: (rating: string) => api.briefs.feedback(params.id, rating, comment || undefined),
    onSuccess: (_, rating) => {
      toast.success(`Feedback recorded: ${rating.replace(/_/g, " ").toLowerCase()}`);
      setComment("");
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : "Feedback failed"),
  });

  const canFeedback = session?.role === "admin" || session?.role === "consultant";

  if (error) {
    return (
      <ErrorState
        message={error instanceof Error ? error.message : "Failed to load brief"}
        onRetry={() => void refetch()}
      />
    );
  }

  if (isLoading || !brief) {
    return (
      <>
        <Skeleton className="mb-6 h-4 w-32" />
        <Skeleton className="mb-4 h-10 w-2/3" />
        <Skeleton className="mb-8 h-6 w-48" />
        <div className="grid gap-8 lg:grid-cols-[1fr_340px]">
          <Skeleton className="h-96" />
          <Skeleton className="h-96" />
        </div>
      </>
    );
  }

  const isLowConfidence = brief.status === "LOW_CONFIDENCE";

  return (
    <>
      <BackLink href="/briefs">Back to brief inbox</BackLink>

      {isLowConfidence && (
        <div
          className="mb-6 flex gap-3 rounded-2xl border border-amber-300/80 bg-amber-50 px-4 py-4 dark:border-amber-500/30 dark:bg-amber-950/20"
          role="alert"
        >
          <AlertTriangle className="h-5 w-5 shrink-0 text-amber-600 dark:text-amber-400" />
          <div>
            <p className="text-sm font-semibold text-amber-900 dark:text-amber-200">
              Low confidence — manual review required
            </p>
            <p className="mt-1 text-sm text-amber-800/80 dark:text-amber-300/80">
              Verification could not confirm all citations. Do not rely on this brief without consulting
              source documents and qualified counsel.
            </p>
          </div>
        </div>
      )}

      <div className="grid gap-8 xl:grid-cols-[1fr_360px]">
        <div className="min-w-0">
          <PageHeader
            title={brief.title}
            subtitle={new Date(brief.generated_at).toLocaleString()}
            action={
              <div className="flex flex-wrap gap-2">
                <SeverityBadge severity={brief.severity} />
                <Badge variant={statusVariant(brief.status)}>{brief.status}</Badge>
              </div>
            }
          />

          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <BookOpen className="h-4 w-4 text-brand dark:text-brand-glow" />
                Change summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="prose-answer">{brief.change_summary}</p>
            </CardContent>
          </Card>

          {brief.obligations.length > 0 && (
            <section className="mb-6">
              <h2 className="mb-4 font-display text-lg font-semibold text-slate-900 dark:text-white">
                Obligations & deadlines
              </h2>
              <ObligationTimeline obligations={brief.obligations} />
            </section>
          )}

          {brief.recommended_actions.length > 0 && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <ListChecks className="h-4 w-4 text-brand dark:text-brand-glow" />
                  Recommended actions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {brief.recommended_actions.map((action, index) => (
                    <li key={index} className="flex gap-3 text-sm text-slate-600 dark:text-slate-300">
                      <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-brand" />
                      {action}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          <div className="mb-6">
            <AgentTraceViewer trace={brief.agent_trace} />
          </div>

          {canFeedback && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="text-base">Your feedback</CardTitle>
                <CardDescription>
                  Help improve relevance and citation accuracy for this client.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-4">
                  <Label htmlFor="comment">Comment (required for not relevant)</Label>
                  <Textarea
                    id="comment"
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    placeholder="Why is this brief not relevant to this client?"
                    rows={3}
                    className="mt-2"
                  />
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button
                    onClick={() => feedbackMutation.mutate("HELPFUL")}
                    disabled={feedbackMutation.isPending}
                  >
                    <ThumbsUp className="h-4 w-4" />
                    Relevant
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={() => feedbackMutation.mutate("PARTIALLY_RELEVANT")}
                    disabled={feedbackMutation.isPending}
                  >
                    Partially relevant
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={() => feedbackMutation.mutate("NOT_RELEVANT")}
                    disabled={feedbackMutation.isPending}
                  >
                    Not relevant
                  </Button>
                  <Button
                    variant="danger"
                    onClick={() => feedbackMutation.mutate("INACCURATE")}
                    disabled={feedbackMutation.isPending}
                  >
                    <ThumbsDown className="h-4 w-4" />
                    Inaccurate
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          <p className="border-t border-slate-200 pt-6 text-xs leading-relaxed text-slate-500 dark:border-white/[0.06]">
            {brief.disclaimer}
          </p>
        </div>

        <aside className="space-y-4 xl:sticky xl:top-24 xl:self-start">
          <Card className="p-5">
            <ConfidenceGauge score={brief.confidence} size="lg" />
            <div className="mt-5 grid grid-cols-2 gap-4 border-t border-slate-200/80 pt-4 dark:border-white/[0.06]">
              <div>
                <p className="text-xs text-slate-500">Citations</p>
                <p className="mt-1 text-xl font-semibold tabular-nums text-slate-900 dark:text-white">
                  {brief.citations.length}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Obligations</p>
                <p className="mt-1 text-xl font-semibold tabular-nums text-slate-900 dark:text-white">
                  {brief.obligations.length}
                </p>
              </div>
            </div>
          </Card>

          <Card className="overflow-hidden p-0">
            <div className="flex items-center gap-2 border-b border-slate-200/80 bg-slate-50/80 px-5 py-4 dark:border-white/[0.06] dark:bg-surface-overlay/40">
              <ShieldCheck className="h-4 w-4 text-brand dark:text-brand-glow" />
              <div>
                <p className="text-sm font-semibold text-slate-900 dark:text-white">Source citations</p>
                <p className="text-xs text-slate-500">Every claim must trace to a verbatim clause</p>
              </div>
            </div>
            <div className="max-h-[min(70vh,640px)] space-y-3 overflow-y-auto p-4">
              {brief.citations.length === 0 ? (
                <EmptyState message="No citations attached to this brief." />
              ) : (
                brief.citations.map((citation, index) => (
                  <CitationCard
                    key={citation.clause_id}
                    citation={citation}
                    prominent={index === 0}
                    defaultExpanded={index === 0}
                  />
                ))
              )}
            </div>
          </Card>

          <Card className="p-5">
            <div className="flex items-center gap-2 text-brand dark:text-brand-glow">
              <Sparkles className="h-4 w-4" />
              <p className="text-xs font-medium uppercase tracking-wider">Verified pipeline</p>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-slate-500">
              Impact analysis → obligation extraction → citation verification → brief synthesis.
            </p>
          </Card>
        </aside>
      </div>
    </>
  );
}
