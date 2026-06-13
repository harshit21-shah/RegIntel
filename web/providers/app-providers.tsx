"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";
import { Toaster } from "sonner";
import { AuthProvider } from "@/lib/auth";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "@/providers/theme-provider";
import { MockApiProvider } from "@/providers/mock-api-provider";

export function AppProviders({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      }),
  );

  return (
    <ThemeProvider>
      <MockApiProvider>
      <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <TooltipProvider delayDuration={200}>
          {children}
          <Toaster
            theme="system"
            position="bottom-right"
            toastOptions={{
              classNames: {
                toast:
                  "glass-panel border-white/10 bg-surface-raised/95 text-slate-200 shadow-glow",
              },
            }}
          />
        </TooltipProvider>
      </AuthProvider>
      </QueryClientProvider>
      </MockApiProvider>
    </ThemeProvider>
  );
}
