"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, Plus } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { useAuth } from "@/lib/auth";
import type { ProfileList } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EmptyState, ListCard, PageHeader, Skeleton } from "@/components/ui";

function profileInitial(name: string): string {
  return (name.trim()[0] ?? "?").toUpperCase();
}

export default function ProfilesPage() {
  const { session } = useAuth();
  const canEdit = session?.role === "admin" || session?.role === "consultant";

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.profiles(1),
    queryFn: () => apiFetch<ProfileList>("/api/v1/profiles?page_size=100"),
  });

  return (
    <>
      <PageHeader
        title="Client Profiles"
        subtitle="Business profiles mapped to regulatory graph nodes for impact analysis."
        action={
          canEdit ? (
            <Link href="/profiles/new" className="no-underline">
              <Button>
                <Plus className="h-4 w-4" />
                Add profile
              </Button>
            </Link>
          ) : undefined
        }
      />

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2">
          <Skeleton className="h-40" />
          <Skeleton className="h-40" />
        </div>
      ) : !data?.items.length ? (
        <EmptyState
          title="No profiles yet"
          message="Create a client profile to enable relevance matching and scoped queries."
          action={
            canEdit ? (
              <Link href="/profiles/new" className="no-underline">
                <Button>Create first profile</Button>
              </Link>
            ) : undefined
          }
        />
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2">
          {data.items.map((profile) => {
            const card = (
              <ListCard className="h-full group-hover:-translate-y-0.5">
                <div className="flex items-start gap-4">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-brand/20 bg-brand/10 font-display text-lg font-semibold text-brand dark:text-brand-glow">
                    {profileInitial(profile.name)}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="font-display text-lg font-semibold text-slate-900 group-hover:text-brand dark:text-white dark:group-hover:text-brand-glow">
                        {profile.name}
                      </h2>
                      <Badge variant="brand">{profile.naics_codes[0] || "—"}</Badge>
                    </div>
                    <dl className="mt-4 space-y-2 text-sm">
                      <div className="flex gap-2">
                        <dt className="w-20 shrink-0 text-slate-500">States</dt>
                        <dd className="text-slate-700 dark:text-slate-300">
                          {profile.states_of_operation.join(", ") || "—"}
                        </dd>
                      </div>
                      <div className="flex gap-2">
                        <dt className="w-20 shrink-0 text-slate-500">Products</dt>
                        <dd className="line-clamp-2 text-slate-700 dark:text-slate-300">
                          {profile.product_categories.join(", ") || "—"}
                        </dd>
                      </div>
                    </dl>
                  </div>
                  {canEdit && (
                    <ArrowRight className="mt-1 h-4 w-4 shrink-0 text-slate-300 transition group-hover:translate-x-0.5 group-hover:text-brand-glow" />
                  )}
                </div>
              </ListCard>
            );

            return (
              <li key={profile.client_id}>
                {canEdit ? (
                  <Link href={`/profiles/${profile.client_id}/edit`} className="group block no-underline">
                    {card}
                  </Link>
                ) : (
                  card
                )}
              </li>
            );
          })}
        </ul>
      )}
    </>
  );
}
