"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

type PageTitleContextValue = {
  pageTitle: string | null;
  setPageTitle: (title: string | null) => void;
};

const PageTitleContext = createContext<PageTitleContextValue | null>(null);

export function PageTitleProvider({ children }: { children: ReactNode }) {
  const [pageTitle, setPageTitleState] = useState<string | null>(null);

  const setPageTitle = useCallback((title: string | null) => {
    setPageTitleState(title);
  }, []);

  const value = useMemo(() => ({ pageTitle, setPageTitle }), [pageTitle, setPageTitle]);

  return <PageTitleContext.Provider value={value}>{children}</PageTitleContext.Provider>;
}

export function usePageTitle(title: string | null | undefined) {
  const { setPageTitle } = usePageTitleContext();

  useEffect(() => {
    if (title) setPageTitle(title);
    return () => setPageTitle(null);
  }, [title, setPageTitle]);
}

export function usePageTitleContext() {
  const ctx = useContext(PageTitleContext);
  if (!ctx) throw new Error("usePageTitleContext must be used within PageTitleProvider");
  return ctx;
}
