"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { apiFetch } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import type { Profile } from "@/lib/types";
import { usePageTitle } from "@/providers/page-title-provider";
import {
  ProfileForm,
  joinList,
  splitList,
  type ProfileFormValues,
} from "@/components/features/profile-form";
import { Loading, PageHeader } from "@/components/ui";
import { useState } from "react";

export default function EditProfilePage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [saving, setSaving] = useState(false);

  const { data: profile, isLoading, error } = useQuery({
    queryKey: queryKeys.profile(params.id),
    queryFn: () => apiFetch<Profile>(`/api/v1/profiles/${params.id}`),
  });

  usePageTitle(profile?.name);

  async function onSubmit(values: ProfileFormValues) {
    setSaving(true);
    try {
      await apiFetch<Profile>(`/api/v1/profiles/${params.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          name: values.name,
          naics_codes: splitList(values.naics),
          states_of_operation: splitList(values.states),
          product_categories: splitList(values.products),
          supply_chain_jurisdictions: splitList(values.jurisdictions),
        }),
      });
      toast.success("Profile updated — relevance re-check queued");
      router.push("/profiles");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to update profile");
    } finally {
      setSaving(false);
    }
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-900/40 bg-red-950/20 px-4 py-3 text-red-300">
        {error instanceof Error ? error.message : "Failed to load profile"}
      </div>
    );
  }

  if (isLoading || !profile) return <Loading label="Loading profile" />;

  return (
    <>
      <PageHeader title="Edit profile" subtitle="Changes trigger a relevance re-check in the background" />
      <ProfileForm
        defaultValues={{
          name: profile.name,
          naics: joinList(profile.naics_codes),
          states: joinList(profile.states_of_operation),
          products: joinList(profile.product_categories),
          jurisdictions: joinList(profile.supply_chain_jurisdictions),
        }}
        submitLabel="Save changes"
        loading={saving}
        onSubmit={onSubmit}
        onCancel={() => router.back()}
      />
    </>
  );
}
