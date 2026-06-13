export type AppRole = "admin" | "consultant" | "viewer";

export const APP_NAV: ReadonlyArray<{
  href: string;
  label: string;
  roles: readonly AppRole[];
  demo?: boolean;
}> = [
  { href: "/dashboard", label: "Dashboard", roles: ["admin", "consultant", "viewer"] },
  { href: "/query", label: "Query", roles: ["admin", "consultant", "viewer"] },
  { href: "/briefs", label: "Briefs", roles: ["admin", "consultant", "viewer"] },
  { href: "/changes", label: "Changes", roles: ["admin", "consultant", "viewer"] },
  { href: "/profiles", label: "Profiles", roles: ["admin", "consultant", "viewer"] },
  { href: "/graph", label: "Graph", roles: ["admin", "consultant"], demo: true },
  { href: "/triage", label: "Triage", roles: ["admin", "consultant"] },
  { href: "/admin", label: "Admin", roles: ["admin"] },
] as const satisfies ReadonlyArray<{
  href: string;
  label: string;
  roles: readonly AppRole[];
  demo?: boolean;
}>;

const SEGMENT_LABELS: Record<string, string> = {
  dashboard: "Dashboard",
  query: "Query",
  briefs: "Briefs",
  changes: "Changes",
  profiles: "Profiles",
  graph: "Knowledge graph",
  triage: "Cross-client triage",
  admin: "Monitoring",
  new: "New",
  edit: "Edit",
};

export type BreadcrumbItem = { label: string; href?: string };

export function breadcrumbsFromPath(pathname: string): BreadcrumbItem[] {
  const segments = pathname.split("/").filter(Boolean);
  if (segments.length === 0) return [{ label: "Dashboard", href: "/dashboard" }];

  const items: BreadcrumbItem[] = [];
  let path = "";

  for (let i = 0; i < segments.length; i++) {
    const segment = segments[i];
    path += `/${segment}`;
    const isLast = i === segments.length - 1;
    const prev = segments[i - 1];

    let label = SEGMENT_LABELS[segment];

    if (!label) {
      if (prev === "briefs") label = "Brief detail";
      else if (prev === "changes") label = "Client triage";
      else if (prev === "profiles") label = "Profile";
      else label = segment.slice(0, 8);
    }

    if (prev === "changes" && segment !== "new" && segment !== "edit" && !SEGMENT_LABELS[segment]) {
      label = "Client triage";
    }

    items.push({
      label,
      href: isLast ? undefined : path,
    });
  }

  return items;
}
