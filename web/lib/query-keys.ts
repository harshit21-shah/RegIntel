export const queryKeys = {
  profiles: (page = 1) => ["profiles", page] as const,
  profile: (id: string) => ["profile", id] as const,
  briefs: (filters: Record<string, string | number>) => ["briefs", filters] as const,
  brief: (id: string) => ["brief", id] as const,
  changes: (filters: Record<string, string | number>) => ["changes", filters] as const,
  change: (id: string) => ["change", id] as const,
  dashboard: ["dashboard"] as const,
};
