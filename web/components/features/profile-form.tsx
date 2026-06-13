"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const profileSchema = z.object({
  name: z.string().min(1, "Company name is required"),
  naics: z.string().min(1, "At least one NAICS code"),
  states: z.string(),
  products: z.string(),
  jurisdictions: z.string().min(1, "At least one jurisdiction"),
});

export type ProfileFormValues = z.infer<typeof profileSchema>;

export function splitList(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export function joinList(values: string[]): string {
  return values.join(", ");
}

export function ProfileForm({
  defaultValues,
  submitLabel,
  loading,
  onSubmit,
  onCancel,
}: {
  defaultValues: ProfileFormValues;
  submitLabel: string;
  loading?: boolean;
  onSubmit: (values: ProfileFormValues) => Promise<void>;
  onCancel: () => void;
}) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues,
  });

  return (
    <Card className="max-w-2xl border-slate-200/80 dark:border-white/10">
      <CardHeader>
        <CardTitle>Business profile</CardTitle>
        <CardDescription>
          NAICS codes, jurisdictions, and product categories drive graph-based relevance matching.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <div>
            <Label htmlFor="name">Company name</Label>
            <Input id="name" {...register("name")} />
            {errors.name && <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.name.message}</p>}
          </div>
          <div className="grid gap-5 sm:grid-cols-2">
            <div>
              <Label htmlFor="naics">NAICS codes</Label>
              <Input id="naics" placeholder="311412, 311999" {...register("naics")} />
              {errors.naics && <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.naics.message}</p>}
            </div>
            <div>
              <Label htmlFor="jurisdictions">Supply chain jurisdictions</Label>
              <Input id="jurisdictions" placeholder="US, MX" {...register("jurisdictions")} />
              {errors.jurisdictions && (
                <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.jurisdictions.message}</p>
              )}
            </div>
          </div>
          <div>
            <Label htmlFor="states">States of operation</Label>
            <Input id="states" placeholder="CA, TX, NY" {...register("states")} />
          </div>
          <div>
            <Label htmlFor="products">Product categories</Label>
            <Input id="products" placeholder="frozen seafood, ready-to-eat meals" {...register("products")} />
          </div>
          <div className="flex flex-wrap gap-2 pt-2">
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Saving…
                </>
              ) : (
                submitLabel
              )}
            </Button>
            <Button type="button" variant="secondary" onClick={onCancel}>
              Cancel
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
