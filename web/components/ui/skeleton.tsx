import { cn } from "@/lib/utils";

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-xl bg-slate-200 dark:bg-white/[0.06]", className)} />;
}

export function Spinner({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "h-4 w-4 animate-spin rounded-full border-2 border-brand/30 border-t-brand-glow",
        className,
      )}
    />
  );
}

export function Loading({ label = "Loading" }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 py-8 text-sm text-slate-500 dark:text-slate-400">
      <Spinner />
      {label}…
    </div>
  );
}
