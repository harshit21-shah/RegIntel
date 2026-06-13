import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatRelativeTime(iso: string): string {
  const date = new Date(iso);
  const diff = Date.now() - date.getTime();
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

export function severityVariant(severity: string): "critical" | "warning" | "default" {
  if (severity === "CRITICAL") return "critical";
  if (severity === "SUBSTANTIVE") return "warning";
  return "default";
}

export function statusVariant(status: string): "success" | "warning" | "default" {
  if (status === "COMPLETE") return "success";
  if (status === "LOW_CONFIDENCE") return "warning";
  return "default";
}

export function formatSource(source: string): string {
  const labels: Record<string, string> = {
    ecfr: "eCFR",
    federal_register: "Federal Register",
    ca_food_code: "CA Food Code",
    sec_edgar: "SEC EDGAR",
  };
  return labels[source] ?? source.replace(/_/g, " ");
}

export function formatChangeType(changeType: string): string {
  return changeType.replace(/_/g, " ").toLowerCase();
}
