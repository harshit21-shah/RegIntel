"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { MobileNav, Sidebar } from "@/components/layout/sidebar";
import { CommandPalette } from "@/components/layout/command-palette";
import { MobileHeaderBar, TopBar } from "@/components/layout/top-bar";
import { PageTitleProvider } from "@/providers/page-title-provider";
import { DocumentTitle } from "@/components/layout/document-title";

export function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { session, clear } = useAuth();

  function logout() {
    clear();
    router.push("/login");
  }

  return (
    <PageTitleProvider>
      <DocumentTitle />
      <div className="min-h-screen lg:flex">
        <Sidebar role={session?.role} email={session?.email} onLogout={logout} />
        <CommandPalette />

        <div className="flex min-h-screen flex-1 flex-col lg:pl-[17rem]">
          <TopBar email={session?.email} role={session?.role} onLogout={logout} />

          <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/80 backdrop-blur-xl dark:border-white/[0.06] dark:bg-surface/80 lg:hidden">
            <MobileHeaderBar onLogout={logout} />
            <MobileNav role={session?.role} />
          </header>

          <main className="flex-1 px-4 py-8 sm:px-8 lg:px-10 lg:py-8">
            <div className="mx-auto max-w-6xl animate-in fade-in-0">{children}</div>
          </main>

          <footer className="border-t border-slate-200/80 px-8 py-5 text-center text-xs text-slate-500 dark:border-white/[0.06]">
            RegIntel provides informational compliance intelligence — not legal advice. Every claim requires a
            source citation.
          </footer>
        </div>
      </div>
    </PageTitleProvider>
  );
}
