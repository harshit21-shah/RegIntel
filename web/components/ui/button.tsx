import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/40 disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]",
  {
    variants: {
      variant: {
        primary:
          "bg-gradient-to-r from-brand to-teal-600 text-slate-950 shadow-glow border border-brand/30 hover:from-brand-glow hover:to-teal-500",
        secondary:
          "bg-slate-100 text-slate-700 border border-slate-200 hover:bg-slate-200/80 dark:bg-surface-overlay dark:text-slate-200 dark:border-white/[0.08] dark:hover:bg-white/[0.06]",
        ghost:
          "text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-white/[0.04] dark:hover:text-white",
        danger: "bg-red-950/80 text-red-200 border border-red-900/60 hover:bg-red-900/40",
        outline: "border border-white/10 bg-transparent text-slate-200 hover:bg-white/[0.04]",
      },
      size: {
        sm: "h-8 px-3 text-xs rounded-lg",
        md: "h-10 px-4",
        lg: "h-11 px-6",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />;
  },
);
Button.displayName = "Button";

export { buttonVariants };
