import { cn } from "@/lib/utils";
import { AlertTriangle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { CitationDetail } from "@/lib/types";
import { statusVariant } from "@/lib/utils";
import { CitationText } from "@/components/CitationText";

export type ChatMessageData = {
  role: "user" | "assistant";
  content: string;
  citations?: CitationDetail[];
  status?: string;
  confidence?: number;
};

export function ChatMessage({ message }: { message: ChatMessageData }) {
  const isUser = message.role === "user";
  const isLowConfidence = message.status === "LOW_CONFIDENCE";

  return (
    <div className={cn("flex gap-3 animate-fade-up", isUser ? "flex-row-reverse" : "flex-row")}>
      <div
        className={cn(
          "flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border shadow-sm",
          isUser
            ? "border-brand/20 bg-brand/10 text-brand dark:text-brand-glow"
            : isLowConfidence
              ? "border-amber-300/80 bg-amber-50 text-amber-600 dark:border-amber-500/30 dark:bg-amber-950/30 dark:text-amber-400"
              : "border-slate-200 bg-white text-brand dark:border-white/10 dark:bg-surface-overlay",
        )}
      >
        {isUser ? (
          <span className="text-xs font-semibold">You</span>
        ) : (
          <span className="text-[10px] font-bold tracking-tight">RI</span>
        )}
      </div>

      <div className={cn("min-w-0 max-w-[85%] sm:max-w-[75%]", isUser ? "text-right" : "text-left")}>
        <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted">
          {isUser ? "Your question" : "RegIntel answer"}
        </p>
        <div
          className={cn(
            "rounded-2xl px-4 py-3.5 text-left shadow-sm",
            isUser
              ? "border border-brand/20 bg-gradient-to-br from-brand/15 to-teal-500/10 dark:from-brand/20 dark:to-teal-900/20"
              : isLowConfidence
                ? "border border-amber-300/80 bg-amber-50/90 dark:border-amber-500/30 dark:bg-amber-950/20"
                : "glass-panel border-slate-200/80 dark:border-white/[0.08]",
          )}
        >
          {isLowConfidence && !isUser && (
            <div className="mb-3 flex gap-2 rounded-lg border border-amber-200/80 bg-amber-100/50 px-3 py-2 dark:border-amber-500/20 dark:bg-amber-950/30">
              <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-600 dark:text-amber-400" />
              <p className="text-xs leading-relaxed text-amber-900/90 dark:text-amber-200/90">
                Could not fully verify all citations. Treat this answer as preliminary and consult source
                documents.
              </p>
            </div>
          )}

          {message.role === "assistant" && message.citations?.length ? (
            <>
              <CitationText text={message.content} citations={message.citations} />
              <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-slate-200/80 pt-3 dark:border-white/[0.06]">
                <Badge variant={statusVariant(message.status ?? "")}>{message.status}</Badge>
                <span className="text-xs text-muted">
                  {((message.confidence ?? 0) * 100).toFixed(0)}% confidence
                </span>
                <span className="text-xs text-muted">
                  · {message.citations.length} citation{message.citations.length !== 1 ? "s" : ""}
                </span>
              </div>
            </>
          ) : (
            <p className="prose-answer whitespace-pre-wrap">{message.content}</p>
          )}
        </div>
      </div>
    </div>
  );
}

export function TypingIndicator() {
  return (
    <div className="flex gap-3 animate-fade-up">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-slate-200 bg-white dark:border-white/10 dark:bg-surface-overlay">
        <span className="text-[10px] font-bold tracking-tight text-brand dark:text-brand-glow">RI</span>
      </div>
      <div className="glass-panel px-5 py-4">
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className="h-2 w-2 rounded-full bg-brand/60 animate-pulse"
                style={{ animationDelay: `${i * 150}ms` }}
              />
            ))}
          </div>
          <span className="text-sm text-muted">Searching regulations…</span>
        </div>
      </div>
    </div>
  );
}
