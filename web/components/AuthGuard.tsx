"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { Spinner } from "@/components/ui/skeleton";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { session, ready } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (ready && !session) router.replace("/login");
  }, [ready, session, router]);

  if (!ready || !session) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4">
        <Spinner className="h-6 w-6" />
        <p className="text-sm text-slate-500">Authenticating…</p>
      </div>
    );
  }
  return <>{children}</>;
}
