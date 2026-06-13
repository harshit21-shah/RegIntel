"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Loader2, ShieldCheck } from "lucide-react";
import { apiFetch, sessionFromToken } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { TokenResponse } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function LoginPage() {
  const router = useRouter();
  const { setSession } = useAuth();
  const demoMode = process.env.NEXT_PUBLIC_DEMO_MODE === "true";
  const [email, setEmail] = useState(demoMode ? "admin@regintel.dev" : "");
  const [password, setPassword] = useState(demoMode ? "RegIntel-Demo-2025!" : "");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      const data = await apiFetch<TokenResponse>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      setSession(sessionFromToken(data, email));
      toast.success("Welcome back");
      router.push("/dashboard");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="border-slate-200/80 p-8 shadow-card-light dark:border-white/10 dark:shadow-card">
      <CardHeader className="mb-2">
        <CardTitle className="text-2xl">Welcome back</CardTitle>
        <CardDescription>Sign in to your compliance workspace</CardDescription>
      </CardHeader>
      <CardContent>
        {demoMode && (
          <div className="mb-6 flex gap-3 rounded-xl border border-brand/20 bg-brand/5 px-4 py-3">
            <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-brand dark:text-brand-glow" />
            <div className="text-xs leading-relaxed text-slate-600 dark:text-slate-400">
              <span className="font-medium text-slate-900 dark:text-white">Demo mode</span> — credentials are
              pre-filled. Use{" "}
              <span className="font-mono text-brand dark:text-brand-glow">admin@regintel.dev</span>
            </div>
          </div>
        )}
        <form onSubmit={onSubmit} className="space-y-5">
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
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <Button type="submit" className="w-full" size="lg" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Signing in…
              </>
            ) : (
              "Continue to RegIntel"
            )}
          </Button>
        </form>
        <p className="mt-8 text-center text-sm text-slate-500">
          New tenant?{" "}
          <Link href="/register" className="font-medium text-brand no-underline hover:text-brand-glow">
            Create an account
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}
