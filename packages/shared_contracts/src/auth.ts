// @medisign/shared-contracts/auth
//
// Auth request/response shapes. Maps 1-1 to
// apps/backend_fastapi/app/schemas/auth.py.
//
// The backend accepts either email OR phone for login (both fields are
// Optional in `AuthLoginRequest`); the web client decides which to send
// after auto-detecting the identifier. Refresh tokens travel in the JSON
// body from FastAPI but are bridged to an httpOnly cookie by the
// `/api/auth/*` Route Handler proxies in apps/web_next.

/**
 * Body sent to `POST /api/v1/auth/login`. Exactly one of `email` or
 * `phone` should be populated by the web client.
 */
export interface LoginInput {
  email?: string;
  phone?: string;
  /** 8..128 chars (validated server-side). */
  password: string;
}

/**
 * Body sent to `POST /api/v1/auth/register`. All fields are required;
 * length constraints match the Pydantic Field validators on the backend.
 */
export interface RegisterInput {
  email: string;
  /** 10..20 chars. */
  phone: string;
  /** 3..50 chars. */
  username: string;
  /** 2..255 chars. */
  full_name: string;
  /** 8..128 chars. */
  password: string;
}

/**
 * Token pair returned by login / register / refresh. Mirrors the
 * `AuthTokenPair` Pydantic model.
 *
 * NOTE: the web client never reads `refresh_token` from this body
 * directly. The Next.js Route Handler proxies strip it and store it in
 * the `medisign_rt` httpOnly cookie before forwarding the rest to the
 * browser.
 */
export interface AuthTokenPair {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  /** Lifetime of `access_token` in seconds. Backend default: 3600. */
  expires_in: number;
}

/**
 * User profile returned by `GET /api/v1/auth/me` and embedded in
 * `AuthLoginResponse` / `AuthRegisterResponse`. Mirrors
 * `AuthUserResponse` from the backend.
 */
export interface AuthUserResponse {
  /** Server-generated user id (UUID string). */
  id: string;
  email: string;
  /** Phone may be null when not registered yet. */
  phone: string | null;
  username: string;
  full_name: string;
  is_email_verified: boolean;
  is_phone_verified: boolean;
  /** Backend default is `"user"`; doctor/admin reserved for future roles. */
  account_type: "user" | "doctor" | "admin";
  /** ISO-8601 timestamp serialized from `datetime`. */
  created_at: string;
}

/**
 * Body returned by `POST /api/v1/auth/login` (and by the
 * `/api/auth/login` Route Handler proxy after stripping the refresh
 * token into a cookie).
 */
export interface AuthLoginResponse {
  user: AuthUserResponse;
  tokens: AuthTokenPair;
}

/**
 * Body sent to `POST /api/v1/auth/change-password`. Requires the current
 * password for confirmation; the backend revokes existing sessions on
 * success so the web client must force a re-login.
 */
export interface ChangePasswordRequest {
  /** 8..128 chars. */
  current_password: string;
  /** 8..128 chars. */
  new_password: string;
}
