import { AlertCircle, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function ErrorState({
  title = "Something went wrong",
  message,
  onRetry,
  className,
}: {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "glass-panel flex flex-col items-center justify-center px-8 py-12 text-center",
        className,
      )}
      role="alert"
    >
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl border border-red-200 bg-red-50 dark:border-red-900/40 dark:bg-red-950/20">
        <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
      </div>
      <p className="font-display text-lg font-medium text-slate-900 dark:text-white">{title}</p>
      <p className="mt-2 max-w-md text-sm text-slate-500">{message}</p>
      {onRetry && (
        <Button variant="secondary" className="mt-6" onClick={onRetry}>
          <RotateCcw className="h-4 w-4" />
          Try again
        </Button>
      )}
    </div>
  );
}
