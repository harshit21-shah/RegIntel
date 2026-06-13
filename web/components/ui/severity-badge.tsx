import { Badge } from "@/components/ui/badge";
import { severityVariant } from "@/lib/utils";
import { cn } from "@/lib/utils";

const SEVERITY_LABELS: Record<string, string> = {
  CRITICAL: "Critical",
  SUBSTANTIVE: "Substantive",
  COSMETIC: "Cosmetic",
};

export function SeverityBadge({
  severity,
  className,
}: {
  severity: string;
  className?: string;
}) {
  return (
    <Badge variant={severityVariant(severity)} className={cn(className)}>
      {SEVERITY_LABELS[severity] ?? severity}
    </Badge>
  );
}
