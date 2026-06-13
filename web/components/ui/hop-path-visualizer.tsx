import { ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

export function HopPathVisualizer({
  path,
  className,
}: {
  path: string[];
  className?: string;
}) {
  if (path.length === 0) {
    return (
      <span className={cn("text-xs text-slate-500", className)}>Direct graph match</span>
    );
  }

  return (
    <div className={cn("flex flex-wrap items-center gap-1.5", className)}>
      {path.map((node, index) => (
        <span key={`${node}-${index}`} className="inline-flex items-center gap-1.5">
          <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 font-mono text-[10px] text-slate-600 dark:border-white/[0.08] dark:bg-surface-overlay dark:text-slate-300">
            {node}
          </span>
          {index < path.length - 1 && <ArrowRight className="h-3 w-3 text-brand-glow" aria-hidden />}
        </span>
      ))}
    </div>
  );
}
