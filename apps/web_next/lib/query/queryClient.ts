/**
 * React Query client factory.
 *
 * We expose a factory (`makeQueryClient`) instead of a module-level singleton
 * so the client can be lazily instantiated inside `<Providers>` via
 * `useState(() => makeQueryClient())`. That guarantees:
 *
 *  - One client per browser tab (component tree), never reinstantiated on
 *    re-render — preserves cache across navigations.
 *  - SSR safety: each server render gets its own isolated client (no leak
 *    between requests).
 *
 * Defaults match the design (see design.md → "State (React Query)"):
 *  - `staleTime: 5 * 60_000` (5 minutes) — endpoints like `/auth/me`,
 *    `/consult/triage/history`, `/api/drug/*` are cheap to keep fresh.
 *  - `retry: 1` — single retry to absorb transient network blips, but
 *    never storm the backend on real 4xx/5xx.
 *  - `refetchOnWindowFocus: false` — UX preference; refocus refetch causes
 *    visible flicker on auth-protected pages.
 *  - `mutations.retry: 0` — mutations are user-driven side effects; never
 *    auto-retry (idempotency cannot be assumed).
 */

import { QueryClient } from "@tanstack/react-query";

/**
 * Build a fresh `QueryClient` configured with MediSign defaults.
 *
 * Call this once per render tree (typically inside `<Providers>` via
 * `useState(() => makeQueryClient())`).
 */
export function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60_000, // 5 minutes
        retry: 1,
        refetchOnWindowFocus: false
      },
      mutations: {
        retry: 0
      }
    }
  });
}
