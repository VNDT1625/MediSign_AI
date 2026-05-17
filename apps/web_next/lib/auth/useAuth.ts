"use client";

/**
 * `useAuth` — public hook for reading the auth state machine and
 * triggering transitions from any client component.
 *
 * Thin wrapper around `AuthContext` defined in `./AuthProvider.tsx`. The
 * hook intentionally exposes the exact shape designed in design.md
 * (`UseAuth` interface) so consuming components can destructure either
 * the granular `state` discriminator or the convenience boolean
 * `isAuthenticated`:
 *
 *     const { state, login, logout } = useAuth();
 *     if (state.status === "authenticated") {
 *       // state.user is now narrowed to AuthUserResponse
 *     }
 *
 *     const { isAuthenticated } = useAuth();
 *     if (isAuthenticated) { ... }
 *
 * Throws a developer-facing error when called outside of `AuthProvider`,
 * because a silent `null` return would mask a wiring bug (e.g. forgetting
 * to wrap a tree with `<Providers>`) until the user actually triggers
 * an action.
 *
 * @see Requirements 2.2.2 — provider exposes `useAuth()` with hydrate.
 * @see `lib/auth/AuthProvider.tsx` for state machine + action semantics.
 */

import { useContext } from "react";

import { AuthContext, type AuthContextValue } from "./AuthProvider";

/**
 * Read the current auth context. Must be called inside the subtree
 * wrapped by `<AuthProvider>` (mounted at `app/providers.tsx`).
 *
 * @throws Error when no `AuthProvider` ancestor is found. The error
 *   message points at the most likely cause to shorten triage time.
 */
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (ctx === null) {
    throw new Error(
      "useAuth() must be called inside <AuthProvider>. " +
        "Ensure app/providers.tsx wraps the tree (see app/layout.tsx).",
    );
  }
  return ctx;
}

// Re-export the value type so consumers can type their own helpers /
// HOCs without reaching into `AuthProvider.tsx` directly. Re-exporting
// `AuthState` is convenient for components that want to render
// presentational variants per state status (e.g. SiteHeader).
export type { AuthContextValue, AuthState } from "./AuthProvider";
