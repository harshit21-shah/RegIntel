"use client";

import { useState } from "react";
import { ChevronDown, ExternalLink, Quote } from "lucide-react";
import type { CitationDetail } from "@/lib/types";
import { cn } from "@/lib/utils";

export function CitationCard({
  citation,
  defaultExpanded = false,
  prominent = false,
}: {
  citation: CitationDetail;
  defaultExpanded?: boolean;
  prominent?: boolean;
}) {
  const [expanded, setExpanded] = useState(defaultExpanded || prominent);

  return (
    <article
      className={cn(
        "overflow-hidden rounded-2xl border transition duration-200",
        prominent
          ? "border-brand/30 bg-gradient-to-br from-brand/5 via-white to-indigo-500/5 shadow-glow dark:from-brand/10 dark:via-surface-raised dark:to-indigo-500/5"
          : "border-slate-200/80 bg-white/90 dark:border-white/[0.08] dark:bg-surface-raised/85",
        expanded && "ring-1 ring-brand/20",
      )}
    >
      <button
        type="button"
        onClick={() => setExpanded((value) => !value)}
        className="flex w-full items-start gap-3 px-4 py-4 text-left transition hover:bg-slate-50/80 dark:hover:bg-white/[0.02]"
        aria-expanded={expanded}
      >
        <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-brand/20 bg-brand/10 text-brand dark:text-brand-glow">
          <Quote className="h-4 w-4" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="font-mono text-sm text-brand dark:text-brand-glow">{citation.clause_id}</p>
          <p className="mt-1 line-clamp-2 text-xs text-slate-500">
            {expanded ? "Verbatim source excerpt" : citation.excerpt.slice(0, 120)}
            {!expanded && citation.excerpt.length > 120 ? "…" : ""}
          </p>
        </div>
        <ChevronDown
          className={cn(
            "mt-1 h-4 w-4 shrink-0 text-slate-400 transition-transform",
            expanded && "rotate-180",
          )}
        />
      </button>

      {expanded && (
        <div className="border-t border-slate-200/80 px-4 pb-4 pt-3 dark:border-white/[0.06]">
          <blockquote className="border-l-4 border-brand/40 pl-4 text-sm italic leading-relaxed text-slate-600 dark:text-slate-300">
            &ldquo;{citation.excerpt}&rdquo;
          </blockquote>
          <a
            href={citation.source_url}
            target="_blank"
            rel="noreferrer"
            className="mt-4 inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-medium text-slate-700 no-underline transition hover:border-brand/30 hover:text-brand dark:border-white/[0.08] dark:bg-surface-overlay dark:text-slate-300 dark:hover:text-brand-glow"
          >
            View source document
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        </div>
      )}
    </article>
  );
}
