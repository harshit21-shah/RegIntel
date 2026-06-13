import { loadSession, saveSession, type AuthSession } from "./auth";
import type { TokenResponse } from "./types";

type ApiError = { error?: { message?: string; code?: string } };

async function refreshAccessToken(refreshToken: string): Promise<AuthSession | null> {
  const response = await fetch("/api/v1/auth/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!response.ok) return null;
  const data = (await response.json()) as TokenResponse;
  const existing = loadSession();
  const session: AuthSession = {
    accessToken: data.access_token,
    refreshToken: data.refresh_token,
    role: data.role,
    email: existing?.email ?? "",
    tenantId: data.tenant_id,
    expiresAt: Date.now() + data.expires_in * 1000,
  };
  saveSession(session);
  return session;
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  let session = loadSession();

  if (session && session.expiresAt - Date.now() < 60_000) {
    const refreshed = await refreshAccessToken(session.refreshToken);
    session = refreshed ?? session;
  }

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };
  if (session?.accessToken) headers.Authorization = `Bearer ${session.accessToken}`;

  let response = await fetch(path, { ...options, headers });

  if (response.status === 401 && session?.refreshToken) {
    const refreshed = await refreshAccessToken(session.refreshToken);
    if (refreshed) {
      headers.Authorization = `Bearer ${refreshed.accessToken}`;
      response = await fetch(path, { ...options, headers });
    }
  }

  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as ApiError;
    throw new Error(body.error?.message || `Request failed (${response.status})`);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export function sessionFromToken(data: TokenResponse, email: string): AuthSession {
  return {
    accessToken: data.access_token,
    refreshToken: data.refresh_token,
    role: data.role,
    email,
    tenantId: data.tenant_id,
    expiresAt: Date.now() + data.expires_in * 1000,
  };
}
