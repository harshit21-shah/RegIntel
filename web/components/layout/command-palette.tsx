"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Command } from "cmdk";
import {
  Briefcase,
  FileText,
  GitBranch,
  LayoutDashboard,
  MessageSquare,
  Radar,
  Search,
  Settings2,
  TrendingUp,
  Users,
} from "lucide-react";
import { cn } from "@/lib/utils";

const COMMANDS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, keywords: "home overview" },
  { href: "/query", label: "Compliance Query", icon: MessageSquare, keywords: "ask search chat" },
  { href: "/briefs", label: "Brief Inbox", icon: FileText, keywords: "reports compliance" },
  { href: "/changes", label: "Regulatory Changes", icon: TrendingUp, keywords: "diff updates" },
  { href: "/profiles", label: "Client Profiles", icon: Users, keywords: "clients naics" },
  { href: "/profiles/new", label: "New Profile", icon: Briefcase, keywords: "create client" },
  { href: "/graph", label: "Knowledge Graph", icon: GitBranch, keywords: "neo4j visualization" },
  { href: "/triage", label: "Cross-client Triage", icon: Radar, keywords: "matrix consultant" },
  { href: "/admin", label: "Admin Monitoring", icon: Settings2, keywords: "ingestion eval" },
];

export function CommandPalette() {
  const router = useRouter();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setOpen(false);
        return;
      }
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen((value) => !value);
      }
    }
    function onOpen() {
      setOpen(true);
    }
    document.addEventListener("keydown", onKeyDown);
    document.addEventListener("regintel:open-command-palette", onOpen);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.removeEventListener("regintel:open-command-palette", onOpen);
    };
  }, []);

  function navigate(href: string) {
    setOpen(false);
    router.push(href);
  }

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50">
      <button
        type="button"
        aria-label="Close command palette"
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={() => setOpen(false)}
      />
      <div className="absolute left-1/2 top-[20%] w-full max-w-lg -translate-x-1/2 px-4">
        <Command
          className="glass-panel overflow-hidden rounded-2xl border-white/10 shadow-glow-lg"
          loop
        >
          <div className="flex items-center gap-3 border-b border-white/[0.06] px-4">
            <Search className="h-4 w-4 shrink-0 text-slate-500" />
            <Command.Input
              placeholder="Search pages and actions…"
              className="h-12 flex-1 bg-transparent text-sm text-slate-900 outline-none placeholder:text-slate-400 dark:text-white dark:placeholder:text-slate-500"
            />
            <kbd className="hidden rounded border border-white/10 px-1.5 py-0.5 text-[10px] text-slate-500 sm:inline">
              ESC
            </kbd>
          </div>
          <Command.List className="max-h-72 overflow-y-auto p-2">
            <Command.Empty className="px-3 py-6 text-center text-sm text-slate-500">
              No results found.
            </Command.Empty>
            <Command.Group heading="Navigate" className="px-1 text-xs text-slate-500">
              {COMMANDS.map((item) => {
                const Icon = item.icon;
                return (
                  <Command.Item
                    key={item.href}
                    value={`${item.label} ${item.keywords}`}
                    onSelect={() => navigate(item.href)}
                    className={cn(
                      "flex cursor-pointer items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-slate-300",
                      "aria-selected:bg-brand/10 aria-selected:text-brand-glow",
                    )}
                  >
                    <Icon className="h-4 w-4 text-slate-500" />
                    {item.label}
                  </Command.Item>
                );
              })}
            </Command.Group>
          </Command.List>
        </Command>
      </div>
    </div>
  );
}
