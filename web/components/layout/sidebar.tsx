"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Briefcase,
  FileText,
  GitBranch,
  LayoutDashboard,
  MessageSquare,
  Radar,
  Settings2,
  TrendingUp,
  Users,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { APP_NAV, type AppRole } from "@/lib/navigation";
import { Logo } from "@/components/Logo";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

const NAV_ICONS: Record<string, typeof LayoutDashboard> = {
  "/dashboard": LayoutDashboard,
  "/query": MessageSquare,
  "/briefs": FileText,
  "/changes": TrendingUp,
  "/profiles": Users,
  "/graph": GitBranch,
  "/triage": Radar,
  "/admin": Settings2,
};

export function Sidebar({
  role,
  email,
  onLogout,
}: {
  role?: string;
  email?: string;
  onLogout: () => void;
}) {
  const pathname = usePathname();
  const links = APP_NAV.filter(
    (item) => !role || item.roles.includes(role as AppRole),
  );

  return (
    <aside className="hidden lg:flex lg:w-[17rem] lg:flex-col lg:fixed lg:inset-y-0 border-r border-slate-200/80 bg-white/95 backdrop-blur-xl dark:border-white/[0.06] dark:bg-surface/95">
      <div className="flex h-full flex-col">
        <div className="px-5 py-6">
          <Link href="/dashboard" className="no-underline">
            <Logo />
          </Link>
        </div>

        <ScrollArea className="flex-1 px-3">
          <nav className="space-y-1 pb-4">
            {links.map((item) => {
              const active = pathname.startsWith(item.href);
              const Icon = NAV_ICONS[item.href] ?? LayoutDashboard;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn("nav-link", active && "nav-link-active")}
                >
                  <Icon className={cn("h-4 w-4", active ? "text-brand dark:text-brand-glow" : "text-slate-500")} />
                  <span className="flex flex-1 items-center justify-between gap-2">
                    {item.label}
                    {item.demo ? (
                      <Badge variant="warning" className="px-1.5 py-0 text-[9px] uppercase tracking-wide">
                        Demo
                      </Badge>
                    ) : null}
                  </span>
                </Link>
              );
            })}
          </nav>
        </ScrollArea>

        <div className="p-4">
          <Separator className="mb-4" />
          <div className="rounded-2xl border border-slate-200/80 bg-slate-50/80 p-4 dark:border-white/[0.06] dark:bg-surface-overlay/60">
            <div className="flex items-start gap-3">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-brand/10 text-brand-glow">
                <Briefcase className="h-4 w-4" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-slate-900 dark:text-white">{email}</p>
                <p className="mt-0.5 text-xs capitalize text-slate-500">{role} account</p>
              </div>
            </div>
            <button
              type="button"
              onClick={onLogout}
              className="mt-3 w-full rounded-lg px-3 py-2 text-left text-xs text-slate-500 transition hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-white/[0.04] dark:hover:text-white"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>
    </aside>
  );
}

export function MobileNav({ role }: { role?: string }) {
  const pathname = usePathname();
  const links = APP_NAV.filter(
    (item) => !role || item.roles.includes(role as AppRole),
  );

  return (
    <nav className="flex gap-1 overflow-x-auto px-4 pb-3 lg:hidden">
      {links.map((item) => {
        const active = pathname.startsWith(item.href);
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "whitespace-nowrap rounded-lg px-3 py-1.5 text-xs font-medium no-underline transition",
              active
                ? "bg-brand/15 text-brand-glow"
                : "text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white",
            )}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
