"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

export type AuthSession = {
  accessToken: string;
  refreshToken: string;
  role: string;
  email: string;
  tenantId: string;
  expiresAt: number;
};

type AuthState = {
  session: AuthSession | null;
  ready: boolean;
  setSession: (session: AuthSession) => void;
  clear: () => void;
};

const AuthContext = createContext<AuthState | null>(null);
const STORAGE_KEY = "regintel_auth";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSessionState] = useState<AuthSession | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      try {
        setSessionState(JSON.parse(raw) as AuthSession);
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    }
    setReady(true);
  }, []);

  const setSession = useCallback((next: AuthSession) => {
    setSessionState(next);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  }, []);

  const clear = useCallback(() => {
    setSessionState(null);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const value = useMemo(
    () => ({ session, ready, setSession, clear }),
    [session, ready, setSession, clear],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export function loadSession(): AuthSession | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthSession;
  } catch {
    return null;
  }
}

export function saveSession(session: AuthSession) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}
