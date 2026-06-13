"use client";

import { cn } from "@/lib/utils";

function toneForConfidence(score: number): {
  bar: string;
  text: string;
  label: string;
} {
  if (score >= 0.85) {
    return {
      bar: "from-emerald-500 to-brand-glow",
      text: "text-emerald-600 dark:text-emerald-400",
      label: "High",
    };
  }
  if (score >= 0.6) {
    return {
      bar: "from-amber-500 to-amber-400",
      text: "text-amber-600 dark:text-amber-400",
      label: "Moderate",
    };
  }
  return {
    bar: "from-red-500 to-red-400",
    text: "text-red-600 dark:text-red-400",
    label: "Low",
  };
}

export function ConfidenceGauge({
  score,
  size = "md",
  showLabel = true,
  compact = false,
  className,
}: {
  score: number;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  compact?: boolean;
  className?: string;
}) {
  const pct = Math.round(score * 100);
  const tone = toneForConfidence(score);
  const sizes = {
    sm: { value: "text-lg", bar: "h-1.5" },
    md: { value: "text-2xl", bar: "h-2" },
    lg: { value: "text-4xl", bar: "h-2.5" },
  };

  if (compact) {
    return (
      <div className={cn("flex min-w-[88px] items-center gap-2", className)}>
        <div className={cn("flex-1 overflow-hidden rounded-full bg-slate-200 dark:bg-white/[0.06]", sizes.sm.bar)}>
          <div
            className={cn("h-full rounded-full bg-gradient-to-r", tone.bar)}
            style={{ width: `${pct}%` }}
          />
        </div>
        <span className={cn("text-xs font-semibold tabular-nums", tone.text)}>{pct}%</span>
      </div>
    );
  }
  return (
    <div className={cn("space-y-2", className)} role="meter" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
      <div className="flex items-end justify-between gap-3">
        <p className="text-xs font-medium uppercase tracking-wider text-slate-500">Confidence</p>
        <div className="text-right">
          <p className={cn("font-display font-semibold tabular-nums", sizes[size].value, tone.text)}>
            {pct}%
          </p>
          {showLabel && <p className="text-[10px] uppercase tracking-wider text-slate-500">{tone.label}</p>}
        </div>
      </div>
      <div className={cn("overflow-hidden rounded-full bg-slate-200 dark:bg-white/[0.06]", sizes[size].bar)}>
        <div
          className={cn("h-full rounded-full bg-gradient-to-r transition-all duration-700", tone.bar)}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
