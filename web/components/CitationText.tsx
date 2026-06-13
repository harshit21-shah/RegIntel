"use client";

import type { CitationDetail } from "@/lib/types";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

function CitationChip({
  clauseId,
  url,
  excerpt,
}: {
  clauseId: string;
  url: string;
  excerpt?: string;
}) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <a
          href={url}
          target="_blank"
          rel="noreferrer"
          className="mx-0.5 inline-flex max-w-full items-center rounded-md border border-brand/25 bg-brand/10 px-1.5 py-0.5 font-mono text-xs text-brand no-underline transition hover:border-brand/40 hover:bg-brand/20 dark:text-brand-glow"
          onClick={(e) => e.stopPropagation()}
        >
          {clauseId}
        </a>
      </TooltipTrigger>
      {excerpt && (
        <TooltipContent side="top" className="max-w-sm leading-relaxed">
          <p className="mb-1 font-mono text-[10px] text-brand dark:text-brand-glow">{clauseId}</p>
          <p className="italic">&ldquo;{excerpt.length > 220 ? `${excerpt.slice(0, 220)}…` : excerpt}&rdquo;</p>
        </TooltipContent>
      )}
    </Tooltip>
  );
}

export function CitationText({
  text,
  citations,
}: {
  text: string;
  citations: CitationDetail[];
}) {
  const byId = Object.fromEntries(citations.map((item) => [item.clause_id, item]));

  const parts = text.split(/(\[[^\]]+\])/g);

  return (
    <div className="prose-answer whitespace-pre-wrap">
      {parts.map((part, index) => {
        const match = part.match(/^\[(.+)\]$/);
        if (!match) return <span key={index}>{part}</span>;
        const clauseId = match[1];
        const citation = byId[clauseId];
        return citation ? (
          <CitationChip
            key={index}
            clauseId={clauseId}
            url={citation.source_url}
            excerpt={citation.excerpt}
          />
        ) : (
          <span key={index} className="font-mono text-xs text-amber-600 dark:text-amber-400">
            {part}
          </span>
        );
      })}
    </div>
  );
}
