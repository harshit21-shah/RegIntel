import { CalendarClock } from "lucide-react";
import type { BriefDetail } from "@/lib/types";
import { cn } from "@/lib/utils";

type Obligation = BriefDetail["obligations"][number];

function formatDeadline(deadline: string): string {
  const date = new Date(deadline);
  if (Number.isNaN(date.getTime())) return deadline;
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

function deadlineTone(deadline?: string | null): string {
  if (!deadline) return "border-slate-300 bg-slate-100 dark:border-white/10 dark:bg-surface-overlay";
  const days = Math.ceil((new Date(deadline).getTime() - Date.now()) / 86_400_000);
  if (days < 0) return "border-red-300 bg-red-50 dark:border-red-900/40 dark:bg-red-950/20";
  if (days <= 90) return "border-amber-300 bg-amber-50 dark:border-amber-900/40 dark:bg-amber-950/20";
  return "border-brand/30 bg-brand/5";
}

export function ObligationTimeline({ obligations }: { obligations: Obligation[] }) {
  if (obligations.length === 0) return null;

  const sorted = [...obligations].sort((a, b) => {
    if (!a.deadline) return 1;
    if (!b.deadline) return -1;
    return new Date(a.deadline).getTime() - new Date(b.deadline).getTime();
  });

  return (
    <ol className="relative space-y-0">
      {sorted.map((obligation, index) => (
        <li key={index} className="relative flex gap-4 pb-8 last:pb-0">
          {index < sorted.length - 1 && (
            <span
              className="absolute left-[15px] top-8 h-[calc(100%-1rem)] w-px bg-slate-200 dark:bg-white/10"
              aria-hidden
            />
          )}
          <div
            className={cn(
              "relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2",
              deadlineTone(obligation.deadline),
            )}
          >
            <CalendarClock className="h-3.5 w-3.5 text-brand dark:text-brand-glow" />
          </div>
          <div className="min-w-0 flex-1 rounded-2xl border border-slate-200/80 bg-white/80 p-4 dark:border-white/[0.08] dark:bg-surface-raised/60">
            <p className="prose-answer">{obligation.text}</p>
            {obligation.deadline && (
              <p className="mt-3 inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-600 dark:border-white/[0.08] dark:bg-surface-overlay dark:text-slate-400">
                <CalendarClock className="h-3 w-3" />
                Due {formatDeadline(obligation.deadline)}
              </p>
            )}
            {obligation.citations && obligation.citations.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1.5">
                {obligation.citations.map((id) => (
                  <span
                    key={id}
                    className="rounded-md border border-brand/20 bg-brand/5 px-2 py-0.5 font-mono text-[10px] text-brand dark:text-brand-glow"
                  >
                    {id}
                  </span>
                ))}
              </div>
            )}
          </div>
        </li>
      ))}
    </ol>
  );
}
