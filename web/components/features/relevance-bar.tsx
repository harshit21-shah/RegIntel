import { cn } from "@/lib/utils";

export function RelevanceBar({ score, className }: { score: number; className?: string }) {
  const pct = Math.round(score * 100);
  const tone =
    score >= 0.7 ? "bg-emerald-500" : score >= 0.4 ? "bg-amber-500" : "bg-slate-400 dark:bg-slate-500";
  const textTone =
    score >= 0.7
      ? "text-emerald-600 dark:text-emerald-400"
      : score >= 0.4
        ? "text-amber-600 dark:text-amber-400"
        : "text-slate-600 dark:text-slate-400";

  return (
    <div className={cn("space-y-1.5", className)}>
      <div className="flex items-center justify-between text-xs">
        <span className="text-slate-500">Relevance</span>
        <span className={cn("font-semibold tabular-nums", textTone)}>{pct}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-white/[0.06]">
        <div
          className={cn("h-full rounded-full transition-all duration-500", tone)}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
