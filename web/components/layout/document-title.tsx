"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import { breadcrumbsFromPath } from "@/lib/navigation";
import { usePageTitleContext } from "@/providers/page-title-provider";

const BASE = "RegIntel";

export function DocumentTitle() {
  const pathname = usePathname();
  const { pageTitle } = usePageTitleContext();

  useEffect(() => {
    const crumbs = breadcrumbsFromPath(pathname);
    const last = crumbs[crumbs.length - 1];
    const segment = pageTitle ?? last?.label ?? "RegIntel";
    document.title = segment === BASE ? BASE : `${segment} · ${BASE}`;
  }, [pathname, pageTitle]);

  return null;
}
