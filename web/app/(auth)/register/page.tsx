"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import { apiFetch, sessionFromToken } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { TokenResponse } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Select } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function RegisterPage() {
  const router = useRouter();
  const { setSession } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [tenantName, setTenantName] = useState("");
  const [role, setRole] = useState("consultant");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      const data = await apiFetch<TokenResponse>("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password, tenant_name: tenantName, role }),
      });
      setSession(sessionFromToken(data, email));
      toast.success("Workspace created");
      router.push("/dashboard");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="border-slate-200/80 p-8 shadow-card-light dark:border-white/10 dark:shadow-card">
      <CardHeader className="mb-2">
        <CardTitle className="text-2xl">Create your workspace</CardTitle>
        <CardDescription>Start monitoring regulatory change for your clients</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="space-y-5">
          <div className="space-y-2">
            <Label htmlFor="tenant">Organization name</Label>
            <Input id="tenant" value={tenantName} onChange={(e) => setTenantName(e.target.value)} required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Work email</Label>
            <Input
              id="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={8}
              required
            />
            <p className="text-[11px] text-slate-500">Minimum 8 characters</p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="role">Role</Label>
            <Select id="role" value={role} onChange={(e) => setRole(e.target.value)}>
              <option value="consultant">Consultant</option>
              <option value="admin">Admin</option>
              <option value="viewer">Viewer</option>
            </Select>
          </div>
          <Button type="submit" className="w-full" size="lg" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Creating account…
              </>
            ) : (
              "Create account"
            )}
          </Button>
        </form>
        <p className="mt-8 text-center text-sm text-slate-500">
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-brand no-underline hover:text-brand-glow">
            Sign in
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}
