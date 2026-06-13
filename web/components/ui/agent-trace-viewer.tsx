"use client";

import { useState } from "react";
import { ChevronDown, Cpu } from "lucide-react";
import type { AgentTraceSummary } from "@/lib/types";
import { cn } from "@/lib/utils";

export function AgentTraceViewer({ trace }: { trace: AgentTraceSummary[] }) {
  const [open, setOpen] = useState(false);

  if (trace.length === 0) return null;

  const totalTokens = trace.reduce((sum, row) => sum + row.tokens_in + row.tokens_out, 0);
  const totalLatency = trace.reduce((sum, row) => sum + row.latency_ms, 0);

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200/80 dark:border-white/[0.08]">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex w-full items-center justify-between gap-3 px-5 py-4 text-left transition hover:bg-slate-50/80 dark:hover:bg-white/[0.02]"
        aria-expanded={open}
      >
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-indigo-500/20 bg-indigo-500/10 text-indigo-500">
            <Cpu className="h-4 w-4" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-900 dark:text-white">Agent trace</p>
            <p className="text-xs text-slate-500">
              {trace.length} agents · {totalTokens.toLocaleString()} tokens · {totalLatency}ms total
            </p>
          </div>
        </div>
        <ChevronDown className={cn("h-4 w-4 text-slate-400 transition-transform", open && "rotate-180")} />
      </button>

      {open && (
        <div className="border-t border-slate-200/80 dark:border-white/[0.06]">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[520px] text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase tracking-wider text-slate-500 dark:bg-surface/80">
                <tr>
                  <th className="px-4 py-3 font-medium">Agent</th>
                  <th className="px-4 py-3 font-medium">Model</th>
                  <th className="px-4 py-3 font-medium">Tokens in/out</th>
                  <th className="px-4 py-3 font-medium">Latency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-white/[0.06]">
                {trace.map((row, index) => (
                  <tr key={index} className="hover:bg-slate-50 dark:hover:bg-white/[0.02]">
                    <td className="px-4 py-3 font-medium text-slate-900 dark:text-white">{row.agent_name}</td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-500">{row.model_used}</td>
                    <td className="px-4 py-3 tabular-nums text-slate-600 dark:text-slate-300">
                      {row.tokens_in} / {row.tokens_out}
                    </td>
                    <td className="px-4 py-3 tabular-nums text-slate-600 dark:text-slate-300">
                      {row.latency_ms}ms
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
