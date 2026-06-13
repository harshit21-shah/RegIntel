"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight } from "lucide-react";
import { breadcrumbsFromPath, type BreadcrumbItem } from "@/lib/navigation";
import { usePageTitleContext } from "@/providers/page-title-provider";
import { cn } from "@/lib/utils";

export function Breadcrumbs({ compact = false }: { compact?: boolean }) {
  const pathname = usePathname();
  const { pageTitle } = usePageTitleContext();
  const crumbs = breadcrumbsFromPath(pathname);

  const items: BreadcrumbItem[] = crumbs.map((crumb, index) =>
    index === crumbs.length - 1 && pageTitle ? { ...crumb, label: pageTitle } : crumb,
  );

  return (
    <nav aria-label="Breadcrumb" className={cn("min-w-0", compact ? "px-4 pb-2 lg:hidden" : "")}>
      <ol className={cn("flex items-center gap-1.5", compact ? "text-xs" : "text-sm")}>
        {items.map((crumb, index) => (
          <li key={`${crumb.label}-${index}`} className="flex min-w-0 items-center gap-1.5">
            {index > 0 && <ChevronRight className="h-3 w-3 shrink-0 text-slate-400" />}
            {crumb.href ? (
              <Link
                href={crumb.href}
                className="truncate text-slate-500 no-underline transition hover:text-brand-glow"
              >
                {crumb.label}
              </Link>
            ) : (
              <span
                className={cn(
                  "truncate",
                  index === items.length - 1
                    ? "font-medium text-slate-900 dark:text-white"
                    : "text-slate-500",
                )}
              >
                {crumb.label}
              </span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
