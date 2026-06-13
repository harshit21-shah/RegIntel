"use client";

import { memo, useMemo } from "react";
import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";
import type { GraphNodeKind } from "@/lib/types";
import { cn } from "@/lib/utils";

export type RegIntelFlowNode = Node<
  {
    kind: GraphNodeKind;
    label: string;
    subtitle?: string;
    highlighted?: boolean;
    dimmed?: boolean;
    selected?: boolean;
  },
  "regintel"
>;

const KIND_STYLES: Record<
  GraphNodeKind,
  { border: string; bg: string; dot: string }
> = {
  Regulation: {
    border: "border-indigo-400/40",
    bg: "bg-indigo-500/10",
    dot: "bg-indigo-400",
  },
  Clause: {
    border: "border-brand/40",
    bg: "bg-brand/10",
    dot: "bg-brand-glow",
  },
  BusinessCategory: {
    border: "border-amber-400/40",
    bg: "bg-amber-500/10",
    dot: "bg-amber-400",
  },
  ClientProfile: {
    border: "border-emerald-400/40",
    bg: "bg-emerald-500/10",
    dot: "bg-emerald-400",
  },
};

function RegIntelNodeComponent({ data }: NodeProps<RegIntelFlowNode>) {
  const styles = KIND_STYLES[data.kind];

  return (
    <div
      className={cn(
        "min-w-[160px] max-w-[220px] cursor-pointer rounded-xl border px-3 py-2.5 shadow-sm backdrop-blur-sm transition duration-300",
        styles.border,
        styles.bg,
        "bg-white/95 dark:bg-surface-raised/90",
        data.highlighted && "ring-2 ring-brand/60 shadow-glow",
        data.selected && "ring-2 ring-indigo-400/60 shadow-glow scale-[1.02]",
        data.dimmed && "opacity-30 grayscale-[0.2]",
        !data.dimmed && "hover:shadow-md hover:-translate-y-0.5",
      )}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!h-2 !w-2 !border-brand/50 !bg-brand opacity-0 transition group-hover:opacity-100"
      />
      <div className="flex items-center gap-2">
        <span className={cn("h-2 w-2 shrink-0 rounded-full", styles.dot)} />
        <p className="truncate text-xs font-semibold text-slate-900 dark:text-white">{data.label}</p>
      </div>
      {data.subtitle && (
        <p className="mt-1 truncate text-[10px] text-slate-500">{data.subtitle}</p>
      )}
      <p className="mt-1 text-[9px] uppercase tracking-wider text-slate-400">{data.kind}</p>
      <Handle
        type="source"
        position={Position.Right}
        className="!h-2 !w-2 !border-brand/50 !bg-brand opacity-0 transition group-hover:opacity-100"
      />
    </div>
  );
}

export const RegIntelNode = memo(RegIntelNodeComponent);

export function useRegIntelNodeTypes() {
  return useMemo(() => ({ regintel: RegIntelNode }), []);
}

const LEGEND_ITEMS: { kind: GraphNodeKind; label: string; color: string }[] = [
  { kind: "Regulation", label: "Regulation", color: "bg-indigo-400" },
  { kind: "Clause", label: "Clause", color: "bg-brand-glow" },
  { kind: "BusinessCategory", label: "Category", color: "bg-amber-400" },
  { kind: "ClientProfile", label: "Client", color: "bg-emerald-400" },
];

export function GraphLegend({ className }: { className?: string }) {
  return (
    <div className={cn("flex flex-wrap items-center gap-3", className)}>
      {LEGEND_ITEMS.map((item) => (
        <span key={item.kind} className="inline-flex items-center gap-1.5 text-[10px] text-slate-500">
          <span className={cn("h-2 w-2 rounded-full", item.color)} />
          {item.label}
        </span>
      ))}
    </div>
  );
}
