import { type ReactNode } from "react";
import { Card as BaseCard } from "./ui/card";
import { Badge as BaseBadge, type BadgeProps } from "./ui/badge";

export * from "./ui/index";
export * from "./shared/page-chrome";

/** Legacy Card with optional padding */
export function Card({
  children,
  className = "",
  padding = "default",
}: {
  children: ReactNode;
  className?: string;
  padding?: "none" | "default" | "lg";
}) {
  const paddingClass = padding === "none" ? "p-0" : padding === "lg" ? "p-8" : "p-6";
  return <BaseCard className={`${paddingClass} ${className}`}>{children}</BaseCard>;
}

/** Legacy Badge with tone prop */
export function Badge({
  children,
  tone = "default",
  className,
}: {
  children: ReactNode;
  tone?: "default" | "critical" | "success" | "warning" | "brand";
  className?: string;
}) {
  return (
    <BaseBadge variant={tone as BadgeProps["variant"]} className={className}>
      {children}
    </BaseBadge>
  );
}
