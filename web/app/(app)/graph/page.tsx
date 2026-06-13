"use client";

import { PageHeader } from "@/components/ui";
import { Badge } from "@/components/ui/badge";
import { GraphExplorerCanvas } from "@/components/features/graph-explorer-canvas";

export default function GraphExplorerPage() {
  return (
    <>
      <PageHeader
        title="Knowledge Graph Explorer"
        subtitle="Regulations, clauses, business categories, and client profiles — with multi-hop impact path highlighting."
        action={
          <Badge variant="warning" className="uppercase tracking-wide">
            Demo data
          </Badge>
        }
      />
      <GraphExplorerCanvas />
    </>
  );
}
