/**
 * `lib/api/auth.ts` — typed wrappers around the auth surface used by the
 * web client. Mixes two transport strategies:
 *
 * 1. **Next.js Route Handler proxies** (`/api/auth/login`, `/api/auth/logout`,
 *    and the internal `/api/auth/refresh` used by the fetcher). These are
 *    same-origin endpoints that bridge the FastAPI JSON-body refresh token
 *    into a `medisign_rt` httpOnly cookie so JS never sees it.
 *
 * 2. **Direct FastAPI calls** (`/auth/register`, `/auth/me`,
 *    `/auth/change-password`) for endpoints where the cookie bridge is not
 *    needed. These travel with the bearer access token in `Authorization`,
 *    matching the mobile client's contract.
 *
 * Phase-1 design.md only specifies proxies for login / refresh / logout
 * (see "Auth Subsystem" section). Register therefore goes straight to
 * FastAPI; the refresh token in its response body is currently dropped —
 * the new account is expected to log in via `login()` immediately so the
 * cookie gets seeded. A future task (Phase 2) will add a proxy for
 * register if we decide to auto-login on account creation.
 *
 * @see Requirements 2.1.1 (register), 2.1.2 (login), 2.1.5 (logout),
 *   2.3.3 (profile / change-password).
 * @see `apps/backend_fastapi/app/api/routes/auth.py` for the canonical
 *   request / response shapes.
 */

import type {
  AuthUserResponse,
  ChangePasswordRequest,
  LoginInput,
  RegisterInput,
} from "@medisign/shared-contracts";

import { apiFetch } from "./fetcher";

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

/**
 * Body returned by the `/api/auth/login` Next.js Route Handler proxy.
 *
 * The upstream FastAPI response is `AuthLoginResponse` (`{ user, tokens }`)
 * but the proxy strips `tokens.refresh_token` into the `medisign_rt`
 * httpOnly cookie before forwarding the rest. The web layer therefore
 * only ever observes the access token here — the refresh token is
 * invisible to JS.
 *
 * @see Design — "Auth Subsystem" / login proxy in design.md.
 */
export interface LoginProxyResponse {
  user: AuthUserResponse;
  access_token: string;
  /** Lifetime of `access_token` in seconds (mirrors backend default 3600). */
  expires_in: number;
}

/**
 * Body returned by `POST /api/v1/auth/register`. Mirrors
 * `AuthRegisterResponse` in `apps/backend_fastapi/app/schemas/auth.py`.
 *
 * NOTE: `tokens.refresh_token` arrives in the JSON body but Phase 1 has
 * no proxy for register, so the web client cannot durably persist it as
 * an httpOnly cookie. Callers should treat `register()` as "create the
 * account" only and follow up with `login()` to establish the session.
 */
export interface AuthRegisterResponse {
  message: string;
  user: AuthUserResponse;
  tokens: {
    access_token: string;
    refresh_token: string;
    token_type: "bearer";
    expires_in: number;
  };
}

// ---------------------------------------------------------------------------
// Endpoints
// ---------------------------------------------------------------------------

/**
 * Sign in via the same-origin Next.js Route Handler proxy. The proxy
 * forwards `input` to FastAPI `/auth/login`, sets the `medisign_rt`
 * cookie from `tokens.refresh_token`, and returns the trimmed
 * `LoginProxyResponse` body.
 *
 * The caller (typically `LoginModal` / `AuthProvider`) is responsible for
 * pushing `access_token` into `tokenStore` and hydrating the user state.
 *
 * @param input Either `email` + `password` or `phone` + `password`.
 * @throws ApiError with `code = "AUTH_INVALID_CREDENTIALS"` on 401, etc.
 */
export function login(input: LoginInput): Promise<LoginProxyResponse> {
  return apiFetch<LoginProxyResponse>("/api/auth/login", {
    method: "POST",
    body: input,
    // The proxy itself is anonymous — no bearer required. The cookie is
    // seeded by the proxy's `Set-Cookie` header on success.
    authRequired: false,
  });
}

/**
 * Create a new user account via FastAPI `/auth/register` (direct, no proxy).
 *
 * The backend returns the freshly issued token pair, but Phase 1 has no
 * `/api/auth/register` proxy to bridge `refresh_token` into a cookie.
 * Callers should immediately invoke `login()` with the same credentials
 * after a successful register so the cookie gets set.
 *
 * @throws ApiError on validation (`VALIDATION_ERROR`) or duplicate field
 *   conflicts (`AUTH_EMAIL_TAKEN`, `AUTH_PHONE_TAKEN`,
 *   `AUTH_USERNAME_TAKEN`).
 */
export function register(input: RegisterInput): Promise<AuthRegisterResponse> {
  return apiFetch<AuthRegisterResponse>("/auth/register", {
    method: "POST",
    body: input,
    authRequired: false,
  });
}

/**
 * Fetch the currently authenticated user's profile from FastAPI
 * `/auth/me`. Requires a valid bearer token; on 401 the fetcher will
 * single-flight-refresh and retry exactly once before surfacing
 * `AUTH_SESSION_EXPIRED`.
 */
export function me(): Promise<AuthUserResponse> {
  return apiFetch<AuthUserResponse>("/auth/me", { method: "GET" });
}

/**
 * Sign out via the same-origin Next.js Route Handler proxy. The proxy
 * best-effort forwards to FastAPI `/auth/logout` and always clears the
 * `medisign_rt` cookie (`Max-Age=0`).
 *
 * The caller is responsible for calling `tokenStore.clear()` and
 * resetting React Query / Auth context state after this resolves.
 */
export function logout(): Promise<void> {
  return apiFetch<void>("/api/auth/logout", {
    method: "POST",
    // The proxy reads the cookie itself; no bearer is required.
    authRequired: false,
  });
}

/**
 * Change the current user's password via FastAPI `/auth/change-password`.
 *
 * On success the backend revokes existing sessions, so the caller must
 * subsequently call `logout()` and force a re-login (see `/app/profile`
 * change-password card in design.md).
 *
 * @throws ApiError with `code = "AUTH_INVALID_CREDENTIALS"` if
 *   `current_password` does not match.
 */
export function changePassword(input: ChangePasswordRequest): Promise<void> {
  return apiFetch<void>("/auth/change-password", {
    method: "POST",
    body: input,
  });
}

/**
 * Request a password reset email via FastAPI `/auth/forgot-password`.
 * Always resolves successfully (backend never reveals if email exists).
 */
export function forgotPassword(email: string): Promise<{ message: string }> {
  return apiFetch<{ message: string }>("/auth/forgot-password", {
    method: "POST",
    body: { email },
    authRequired: false,
  });
}

/**
 * Confirm password reset with token from email link via FastAPI `/auth/reset-password`.
 *
 * @throws ApiError with `code = "AUTH_INVALID_RESET_TOKEN"` if token is
 *   invalid or expired.
 */
export function resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
  return apiFetch<{ message: string }>("/auth/reset-password", {
    method: "POST",
    body: { token, new_password: newPassword },
    authRequired: false,
  });
}
