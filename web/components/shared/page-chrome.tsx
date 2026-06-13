import Link from "next/link";
import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

export function PageHeader({
  title,
  subtitle,
  action,
  className,
}: {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between", className)}>
      <div>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-slate-900 dark:text-white">{title}</h1>
        {subtitle && <p className="mt-2 max-w-2xl text-base text-muted">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

export function SectionTitle({ children }: { children: ReactNode }) {
  return (
    <h2 className="mb-4 font-display text-lg font-semibold tracking-tight text-slate-900 dark:text-white">
      {children}
    </h2>
  );
}

export function EmptyState({
  title,
  message,
  action,
}: {
  title?: string;
  message: string;
  action?: ReactNode;
}) {
  return (
    <div className="glass-panel flex flex-col items-center justify-center px-8 py-16 text-center">
      <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-slate-200 bg-slate-50 dark:border-white/[0.06] dark:bg-surface-overlay">
        <svg className="h-6 w-6 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      </div>
      {title && <p className="font-display text-lg font-medium text-slate-900 dark:text-white">{title}</p>}
      <p className="mt-2 max-w-md text-sm text-slate-400">{message}</p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}

export function BackLink({ href, children }: { href: string; children: ReactNode }) {
  return (
    <Link
      href={href}
      className="mb-6 inline-flex items-center gap-2 text-sm text-slate-400 no-underline transition-colors hover:text-brand-glow"
    >
      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
      </svg>
      {children}
    </Link>
  );
}

export function StatCard({
  label,
  value,
  hint,
  accent = "default",
  icon,
}: {
  label: string;
  value: string | number;
  hint?: string;
  accent?: "default" | "warning" | "brand";
  icon?: ReactNode;
}) {
  const accents = {
    default: "text-slate-900 dark:text-white",
    warning: "text-amber-600 dark:text-amber-400",
    brand: "text-brand dark:text-brand-glow",
  };
  return (
    <div className="glass-panel relative overflow-hidden rounded-2xl p-6">
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/[0.03] to-transparent" />
      <div className="relative flex items-start justify-between gap-3">
        <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{label}</p>
        {icon}
      </div>
      <p className={`relative mt-3 font-display text-4xl font-semibold tracking-tight ${accents[accent]}`}>
        {value}
      </p>
      {hint && <p className="relative mt-2 text-sm text-slate-500">{hint}</p>}
    </div>
  );
}

export function ListCard({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "glass-panel rounded-2xl p-5 transition-all duration-200 hover:border-brand/25 hover:shadow-glow",
        className,
      )}
    >
      {children}
    </div>
  );
}

export function DataTable({
  headers,
  children,
}: {
  headers: string[];
  children: ReactNode;
}) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 dark:border-white/[0.06]">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase tracking-wider text-slate-500 dark:bg-surface/80">
          <tr>
            {headers.map((header) => (
              <th key={header} className="px-4 py-3 font-medium">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 text-slate-700 dark:divide-white/[0.06] dark:text-slate-300">
          {children}
        </tbody>
      </table>
    </div>
  );
}

export function FilterBar({ children }: { children: ReactNode }) {
  return <div className="glass-panel mb-8 rounded-2xl p-6">{children}</div>;
}

export function Pagination({
  page,
  totalPages,
  total,
  onPageChange,
}: {
  page: number;
  totalPages: number;
  total?: number;
  onPageChange: (page: number) => void;
}) {
  if (totalPages <= 1) return null;
  return (
    <div className="mt-8 flex items-center justify-between">
      <p className="text-sm text-slate-500">
        Page {page} of {totalPages}
        {total !== undefined ? ` · ${total} total` : ""}
      </p>
      <div className="flex gap-2">
        <button
          type="button"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm text-slate-700 transition hover:bg-slate-50 disabled:opacity-40 dark:border-white/[0.08] dark:bg-surface-overlay dark:text-slate-300 dark:hover:bg-white/[0.04]"
        >
          Previous
        </button>
        <button
          type="button"
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
          className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm text-slate-700 transition hover:bg-slate-50 disabled:opacity-40 dark:border-white/[0.08] dark:bg-surface-overlay dark:text-slate-300 dark:hover:bg-white/[0.04]"
        >
          Next
        </button>
      </div>
    </div>
  );
}
