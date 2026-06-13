"use client";

import Link from "next/link";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Breadcrumbs } from "@/components/layout/breadcrumbs";
import { ThemeToggle } from "@/components/layout/theme-toggle";

function openCommandPalette() {
  document.dispatchEvent(new CustomEvent("regintel:open-command-palette"));
}

export function TopBar({
  email,
  role,
  onLogout,
}: {
  email?: string;
  role?: string;
  onLogout: () => void;
}) {
  return (
    <header className="sticky top-0 z-20 hidden border-b border-slate-200/80 bg-white/80 backdrop-blur-xl dark:border-white/[0.06] dark:bg-surface/80 lg:block">
      <div className="flex h-14 items-center justify-between gap-4 px-8">
        <Breadcrumbs />

        <div className="flex shrink-0 items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            className="hidden text-slate-500 xl:inline-flex"
            onClick={openCommandPalette}
          >
            <Search className="h-3.5 w-3.5" />
            Search
            <kbd className="ml-1 rounded border border-slate-200 bg-slate-100 px-1.5 py-0.5 text-[10px] dark:border-white/10 dark:bg-white/5">
              Ctrl K
            </kbd>
          </Button>

          <ThemeToggle compact />

          <div className="hidden h-6 w-px bg-slate-200 dark:bg-white/10 sm:block" />

          <div className="hidden min-w-0 sm:block">
            <p className="truncate text-right text-xs font-medium text-slate-900 dark:text-white">{email}</p>
            <p className="truncate text-right text-[10px] capitalize text-slate-500">{role}</p>
          </div>

          <Button variant="ghost" size="sm" onClick={onLogout} className="text-slate-500">
            Sign out
          </Button>
        </div>
      </div>
    </header>
  );
}

export function MobileHeaderBar({
  onLogout,
}: {
  onLogout: () => void;
}) {
  return (
    <>
      <div className="flex items-center justify-between gap-4 px-4 py-3 lg:hidden">
        <Link href="/dashboard" className="shrink-0 no-underline">
          <span className="font-display text-sm font-semibold text-slate-900 dark:text-white">RegIntel</span>
        </Link>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" onClick={openCommandPalette} aria-label="Search">
            <Search className="h-4 w-4" />
          </Button>
          <ThemeToggle compact />
          <Button variant="ghost" size="sm" onClick={onLogout}>
            Sign out
          </Button>
        </div>
      </div>
      <Breadcrumbs compact />
    </>
  );
}
