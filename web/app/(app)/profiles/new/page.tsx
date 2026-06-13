"use client";

import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { apiFetch } from "@/lib/api";
import type { Profile } from "@/lib/types";
import { usePageTitle } from "@/providers/page-title-provider";
import {
  ProfileForm,
  splitList,
  type ProfileFormValues,
} from "@/components/features/profile-form";
import { PageHeader } from "@/components/ui";
import { useState } from "react";

export default function NewProfilePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  usePageTitle("New profile");

  async function onSubmit(values: ProfileFormValues) {
    setLoading(true);
    try {
      await apiFetch<Profile>("/api/v1/profiles", {
        method: "POST",
        body: JSON.stringify({
          name: values.name,
          naics_codes: splitList(values.naics),
          states_of_operation: splitList(values.states),
          product_categories: splitList(values.products),
          supply_chain_jurisdictions: splitList(values.jurisdictions),
        }),
      });
      toast.success("Profile created");
      router.push("/profiles");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to create profile");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <PageHeader title="New client profile" subtitle="Define the business context for relevance matching" />
      <ProfileForm
        defaultValues={{
          name: "",
          naics: "311412",
          states: "CA, TX",
          products: "frozen seafood, ready-to-eat meals",
          jurisdictions: "US",
        }}
        submitLabel="Create profile"
        loading={loading}
        onSubmit={onSubmit}
        onCancel={() => router.back()}
      />
    </>
  );
}
