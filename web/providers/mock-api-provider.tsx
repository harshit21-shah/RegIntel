"use client";

import { useEffect, useState, type ReactNode } from "react";

export function MockApiProvider({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(process.env.NEXT_PUBLIC_MOCK_API !== "true");

  useEffect(() => {
    if (process.env.NEXT_PUBLIC_MOCK_API !== "true") return;

    void import("@/mocks/browser").then(({ startMockWorker }) => {
      startMockWorker().then(() => setReady(true));
    });
  }, []);

  if (!ready) {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-slate-500">
        Starting demo API…
      </div>
    );
  }

  return children;
}
