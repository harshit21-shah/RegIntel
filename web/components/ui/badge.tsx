import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide",
  {
    variants: {
      variant: {
        default:
          "border-slate-200 bg-slate-100 text-slate-600 dark:border-white/[0.08] dark:bg-surface-overlay dark:text-slate-300",
        critical:
          "border-red-200 bg-red-50 text-red-700 dark:border-red-800/50 dark:bg-red-950/60 dark:text-red-300",
        success:
          "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-800/50 dark:bg-emerald-950/60 dark:text-emerald-300",
        warning:
          "border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-800/50 dark:bg-amber-950/60 dark:text-amber-300",
        brand: "border-brand/25 bg-brand/10 text-brand dark:text-brand-glow",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}

/** @deprecated use variant prop */
export function BadgeLegacy({
  tone = "default",
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & {
  tone?: "default" | "critical" | "success" | "warning" | "brand";
}) {
  return <Badge variant={tone} {...props} />;
}
