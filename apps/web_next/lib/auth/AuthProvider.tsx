"use client";

/**
 * `AuthProvider` — client-side auth state machine and action surface.
 *
 * Wraps the app under `app/providers.tsx` so every client component can
 * read the current authentication state via `useAuth()` (in `./useAuth.ts`)
 * and trigger transitions through the exposed actions.
 *
 * State machine (mirrors design.md → "AuthProvider (client)"):
 *
 *     loading ──► anonymous       (no refresh cookie / refresh failed)
 *             └─► authenticated   (refresh success + /auth/me success)
 *
 *     authenticated ──► anonymous (logout)
 *     anonymous     ──► authenticated (login)
 *
 * The `loading` state is only entered (a) once on mount and (b) explicitly
 * via `hydrate()` (used by the `?session=expired` flow to re-bootstrap
 * after the user logs back in via the modal). It must NEVER flash back
 * during normal page navigation, otherwise the `/app/*` shell would show
 * skeletons every time a route changes — instead, transitions are driven
 * by explicit actions only.
 *
 * Hydration sequence (on mount):
 *   1. Call `refreshOnce()` from the fetcher. If a `medisign_rt` cookie
 *      is present and valid, the proxy mints a fresh access token and
 *      writes it into `tokenStore`. If the cookie is missing or rejected,
 *      `refreshOnce()` clears the store, fires a best-effort logout, and
 *      throws `ApiError("AUTH_SESSION_EXPIRED")`.
 *   2. On refresh success, call `GET /auth/me` to fetch the user profile
 *      (the fetcher attaches the freshly minted bearer automatically).
 *   3. On any failure (network, 401 from `/auth/me`, refresh rejection)
 *      collapse to `anonymous` — never throw out of the hook.
 *
 * Refresh single-flight is owned by the fetcher (`refreshOnce()` collapses
 * concurrent callers onto a single `POST /api/auth/refresh`), so the
 * provider does not need its own mutex even if multiple components call
 * `hydrate()` in quick succession.
 *
 * Refresh tokens never reach this module — they live in the `medisign_rt`
 * httpOnly cookie set by the Next.js Route Handler proxies. Access tokens
 * live in `tokenStore` (in-memory, per-tab) which is updated automatically
 * by `login()` and `refreshOnce()`.
 *
 * @see Requirements 2.2.2 (auth context + hydrate), 2.1.1 (register),
 *   2.1.2 (login), 2.1.5 (logout), 2.1.6 (refresh + expiry),
 *   2.3.3 (change password / force re-login).
 * @see Design — "AuthProvider (client)" interface in design.md.
 */

import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import type {
  AuthUserResponse,
  ChangePasswordRequest,
  LoginInput,
  RegisterInput,
} from "@medisign/shared-contracts";

import * as authApi from "../api/auth";
import { refreshOnce } from "../api/fetcher";
import { tokenStore } from "./tokenStore";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/**
 * Discriminated union describing the three states the auth machine can
 * occupy. Components destructure `state.status` to render the right UI:
 *
 *   - `"loading"`        — initial hydrate in flight; render skeletons.
 *   - `"anonymous"`      — no session; render public CTAs / `LoginModal`.
 *   - `"authenticated"`  — session live; `state.user` is the profile.
 */
export type AuthState =
  | { status: "loading" }
  | { status: "anonymous" }
  | { status: "authenticated"; user: AuthUserResponse };

/**
 * Public surface returned by `useAuth()`. Kept as an explicit interface so
 * the hook file (`./useAuth.ts`) can re-import it without pulling in the
 * provider implementation, and so consumer components stay loosely
 * coupled to this module.
 */
export interface AuthContextValue {
  /** Current state. Components should narrow on `state.status`. */
  state: AuthState;
  /** Convenience predicate; equivalent to `state.status === "authenticated"`. */
  isAuthenticated: boolean;
  /**
   * Sign in via the `/api/auth/login` Route Handler proxy. On success the
   * access token is written to `tokenStore` and the state transitions to
   * `authenticated`. Errors propagate untouched so the caller can map
   * `ApiError.code` to inline form errors (see `LoginModal` task 8.3).
   */
  login(input: LoginInput): Promise<void>;
  /**
   * Create a new account via FastAPI `/auth/register`. Phase 1 has no
   * register proxy, so the response's refresh token cannot be persisted
   * as an httpOnly cookie. The provider therefore deliberately leaves
   * `state` untouched — the caller is expected to chain `login()` with
   * the same credentials immediately after to seed the cookie.
   */
  register(input: RegisterInput): Promise<void>;
  /**
   * Sign out via the `/api/auth/logout` Route Handler proxy and clear
   * client-side state. Best-effort: even if the proxy call fails, the
   * in-memory token is cleared and the state collapses to `anonymous`.
   */
  logout(): Promise<void>;
  /**
   * Change the current user's password via FastAPI
   * `/auth/change-password`. State is intentionally NOT changed — the
   * caller is responsible for the force-re-login flow (toast → logout →
   * redirect to `/?session=changed-password`), per design.md.
   */
  changePassword(input: ChangePasswordRequest): Promise<void>;
  /**
   * Re-run the mount-time bootstrap. Used by the `?session=expired`
   * landing flow (after the user re-authenticates inside the modal) to
   * re-attach the new session without a full page reload.
   */
  hydrate(): Promise<void>;
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

/**
 * Internal context carrying the `AuthContextValue`. Default is `null` so
 * `useAuth()` can detect a missing provider and throw a clear developer
 * error instead of silently returning a stub.
 *
 * Exported so `useAuth.ts` can read it; consumer code should import the
 * `useAuth` hook instead of touching the context directly.
 */
export const AuthContext = createContext<AuthContextValue | null>(null);

// ---------------------------------------------------------------------------
// Provider
// ---------------------------------------------------------------------------

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Root provider. Mounted exactly once under `app/providers.tsx`; nesting
 * it elsewhere would create a second auth state machine and is not
 * supported.
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [state, setState] = useState<AuthState>({ status: "loading" });

  /**
   * Tracks whether the component is still mounted so async callbacks can
   * skip `setState` after unmount. React strict mode invokes effects
   * twice in development — guarding via a ref keeps the second invocation
   * from racing the cleanup of the first.
   */
  const isMountedRef = useRef(true);

  /**
   * Core hydration routine. Pulled out as a stable callback so it can be
   * exposed via `hydrate()` AND used as the mount-time bootstrap without
   * duplicating the try/catch envelope.
   *
   * Strategy:
   *   - Try `refreshOnce()` first. This is cheap (one round-trip to the
   *     same-origin proxy) and avoids a wasted 401 against `/auth/me`
   *     when there's no token in the in-memory store yet.
   *   - On success, fetch the user profile. The fetcher will attach the
   *     freshly written bearer; a 401 here would re-trigger the same
   *     `refreshOnce()` (which is now idle, so it runs again) and we
   *     treat a second failure as "session unrecoverable".
   *   - On any failure, collapse to `anonymous`. We never propagate the
   *     error out of `hydrate()` because the only sensible UX is to
   *     show the public landing page and let the user sign in again.
   */
  const hydrate = useCallback(async (): Promise<void> => {
    if (isMountedRef.current) {
      setState({ status: "loading" });
    }

    try {
      // Bootstraps `tokenStore` from the `medisign_rt` cookie. Throws
      // `AUTH_SESSION_EXPIRED` if the cookie is missing or rejected; any
      // such throw lands in the catch below and we go anonymous.
      await refreshOnce();

      // Fetch the user profile with the freshly-minted bearer. Any error
      // here (network, 5xx, second 401) is also treated as "no session".
      const user = await authApi.me();

      if (!isMountedRef.current) return;
      setState({ status: "authenticated", user });
    } catch (err) {
      // Defensive cleanup: `refreshOnce` on failure already clears the
      // token store and fires a best-effort logout, but if `me()` fails
      // *after* a successful refresh we still want the in-memory token
      // gone before we drop to anonymous.
      //
      // We also swallow the error here intentionally — the only sensible
      // UX when hydration fails (no cookie, expired session, network
      // blip) is to show the public landing page. Letting the error
      // propagate would crash the entire React tree and show the error
      // boundary instead of the normal homepage.
      try {
        tokenStore.clear();
      } catch {
        // ignore — tokenStore.clear() should never throw, but be safe
      }
      // Log for debugging without crashing
      if (process.env.NODE_ENV === "development") {
        // eslint-disable-next-line no-console
        console.debug("[AuthProvider] hydration failed (going anonymous):", err);
      }
      if (!isMountedRef.current) return;
      setState({ status: "anonymous" });
    }
  }, []);

  // Run the bootstrap exactly once on mount. Strict mode's double-invoke
  // is harmless here: `refreshOnce()` is single-flight, so the second
  // call piggybacks on the first promise; the only observable side effect
  // is one extra `setState({status:"loading"})` which is idempotent.
  useEffect(() => {
    isMountedRef.current = true;
    void hydrate();
    return () => {
      isMountedRef.current = false;
    };
  }, [hydrate]);

  /**
   * Sign-in action. Lets `ApiError` propagate so the form layer can
   * map error codes (`AUTH_INVALID_CREDENTIALS`, `VALIDATION_ERROR`, …)
   * to inline UX per design.md → "Mapping `code` → UX".
   */
  const login = useCallback<AuthContextValue["login"]>(async (input) => {
    const response = await authApi.login(input);
    tokenStore.set(response.access_token, response.expires_in);
    if (!isMountedRef.current) return;
    setState({ status: "authenticated", user: response.user });
  }, []);

  /**
   * Register action. Phase 1: only creates the backend account; the web
   * client cannot durably persist the refresh token from the response
   * (no `/api/auth/register` proxy yet — see design.md "Open Questions").
   * The state stays put so the caller can chain `login()` to seed the
   * cookie and transition to `authenticated`.
   */
  const register = useCallback<AuthContextValue["register"]>(async (input) => {
    await authApi.register(input);
    // Intentionally NO state mutation here; the caller is expected to
    // immediately call `login()` with the same credentials.
  }, []);

  /**
   * Sign-out action. Best-effort: even if the proxy round-trip throws
   * (network, 5xx, etc.) we still clear local state, because leaving the
   * tab "authenticated" while the cookie is gone server-side would leave
   * the user stuck on a stale shell.
   */
  const logout = useCallback<AuthContextValue["logout"]>(async () => {
    try {
      await authApi.logout();
    } catch {
      // Swallow: design.md → A5 says "best-effort logout".
    }
    tokenStore.clear();
    if (!isMountedRef.current) return;
    setState({ status: "anonymous" });
  }, []);

  /**
   * Change-password action. The backend revokes existing sessions on
   * success, so the access token still in `tokenStore` is now invalid —
   * but we deliberately do NOT clear it here. The caller (the profile
   * page's change-password card) is responsible for the force-re-login
   * flow: toast → `logout()` → redirect to `/?session=changed-password`.
   * Letting the caller drive that sequence keeps the state machine
   * predictable and avoids racing UI feedback.
   */
  const changePassword = useCallback<AuthContextValue["changePassword"]>(
    async (input) => {
      await authApi.changePassword(input);
      // No state mutation by design.
    },
    [],
  );

  /**
   * Memoize the context value so consumers re-render only when something
   * actually changed. `useMemo` cares about reference identity of the
   * action callbacks (which are stable via `useCallback`) and the
   * primitive `state` object — so a re-render of `AuthProvider` does
   * not cascade through every consumer when nothing relevant changed.
   */
  const value = useMemo<AuthContextValue>(
    () => ({
      state,
      isAuthenticated: state.status === "authenticated",
      login,
      register,
      logout,
      changePassword,
      hydrate,
    }),
    [state, login, register, logout, changePassword, hydrate],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
