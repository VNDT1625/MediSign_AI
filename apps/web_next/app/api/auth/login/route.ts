/**
 * `app/api/auth/login/route.ts` — Next.js Route Handler proxy that
 * bridges the FastAPI login response into a same-origin `medisign_rt`
 * httpOnly cookie.
 *
 * Phase 1 design (see "Auth Subsystem" in design.md):
 *
 *   1. Read the client's JSON body. The `remember` flag is consumed
 *      locally to decide cookie persistence and is **stripped before
 *      forwarding** so FastAPI only sees the fields its schema
 *      declares (`email` / `phone` / `password`). The remaining body
 *      goes upstream untouched.
 *   2. On a 200 response, strip `tokens.refresh_token` out of the body
 *      and stash it in the `medisign_rt` cookie (`httpOnly`, `Secure`
 *      per env, `SameSite=Lax`, `Path=/`). The cookie persists 30 days
 *      when the client opted into "remember me", otherwise it is a
 *      session cookie (no `Max-Age`/`Expires`). The client only sees
 *      `{ user, access_token, expires_in }`.
 *   3. On any non-2xx upstream response, forward status + body
 *      verbatim and set NO cookie — the client's session is unchanged.
 *   4. On network errors, timeouts, or unparseable upstream JSON,
 *      synthesize a `502 PROXY_UPSTREAM_ERROR` envelope so the UI can
 *      show a "can't reach server" toast without leaking proxy state.
 *
 * `x-request-id` is propagated both upstream (so backend logs can be
 * correlated) and back to the client (so error toasts can surface a
 * support reference). When the upstream sends its own request id we
 * prefer that — it is the canonical id stamped by FastAPI middleware.
 *
 * @see Requirements 2.1.2 (login flow), 2.1.6 (token storage / refresh),
 *   3.1 (no JS-readable refresh token; httpOnly cookie bridge).
 * @see `lib/api/auth.ts#login` for the typed client wrapper.
 * @see `apps/backend_fastapi/app/api/routes/auth.py` for the upstream
 *   endpoint shape (`AuthLoginRequest` -> `AuthLoginResponse`).
 */

import { NextResponse, type NextRequest } from "next/server";

import type { AuthLoginResponse } from "@medisign/shared-contracts";

// Cookie writes require Node APIs (`Set-Cookie`) — Edge runtime would
// force us to drop the convenient `response.cookies.set()` API.
export const runtime = "nodejs";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Name of the httpOnly cookie that stores the refresh token. */
const COOKIE_NAME = "medisign_rt";

/** Fallback API base URL — mirrors `lib/api/fetcher.ts`. */
const DEFAULT_API_BASE_URL = "http://localhost:8000/api/v1";

/** Correlation id header forwarded both upstream and back to the client. */
const REQUEST_ID_HEADER = "x-request-id";

/**
 * Cookie lifetime for "remember me" — 30 days, matching the backend's
 * `BACKEND_JWT_REFRESH_TOKEN_DAYS` default. Without this option the
 * cookie is a session cookie that dies with the browser tab.
 */
const REMEMBER_MAX_AGE_SECONDS = 30 * 24 * 60 * 60; // 2_592_000

/**
 * Hard cap on the upstream call so a slow/dead backend cannot stall us.
 * 10s is intentionally a touch more generous than the refresh proxy's
 * budget — the login path runs Argon2/bcrypt password verification on
 * the backend which can spike under load, but well under the global
 * `apiFetch` 15s ceiling so the browser-side AbortController stays in
 * charge of the user-visible deadline.
 */
const UPSTREAM_TIMEOUT_MS = 10_000;

/** Sentinel code used when we cannot reach FastAPI or its body is junk. */
const PROXY_UPSTREAM_ERROR_CODE = "PROXY_UPSTREAM_ERROR";
/** vi-VN copy returned when the proxy synthesizes an upstream error. */
const PROXY_UPSTREAM_ERROR_MESSAGE = "Không thể kết nối đến máy chủ";

/** Sentinel code used when the client body is not valid JSON. */
const VALIDATION_ERROR_CODE = "VALIDATION_ERROR";
/** vi-VN copy returned when the client body is not valid JSON. */
const VALIDATION_ERROR_MESSAGE = "Yêu cầu không hợp lệ";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Read `NEXT_PUBLIC_API_BASE_URL` at request time, trimming trailing `/`. */
function getApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_BASE_URL || DEFAULT_API_BASE_URL;
  return raw.replace(/\/+$/, "");
}

/**
 * Resolve cookie attributes from env so dev (HTTP, no domain) and prod
 * (HTTPS, optional shared domain) both work without code changes.
 *
 *   - `AUTH_COOKIE_SECURE` — `"true"` to set the `Secure` flag.
 *   - `AUTH_COOKIE_DOMAIN` — explicit cookie domain; omitted when blank
 *     (browser defaults to the current host, which is what localhost
 *     wants).
 *
 * Mirrors `app/api/auth/logout/route.ts` so the same cookie shape is
 * written and cleared symmetrically.
 */
function getCookieAttrs(): { secure: boolean; domain?: string } {
  const secure = process.env.AUTH_COOKIE_SECURE === "true";
  const rawDomain = process.env.AUTH_COOKIE_DOMAIN?.trim();
  const attrs: { secure: boolean; domain?: string } = { secure };
  if (rawDomain) {
    attrs.domain = rawDomain;
  }
  return attrs;
}

/**
 * Build the canonical 502 envelope we return when FastAPI is unreachable
 * or its response body is not what we expect. Shape matches
 * `ApiErrorBody` from `@medisign/shared-contracts` so the client's
 * `normalizeError` can decode it without special-casing.
 */
function buildProxyUpstreamError(requestId: string | null): NextResponse {
  const response = NextResponse.json(
    { code: PROXY_UPSTREAM_ERROR_CODE, message: PROXY_UPSTREAM_ERROR_MESSAGE },
    { status: 502 },
  );
  if (requestId) {
    response.headers.set(REQUEST_ID_HEADER, requestId);
  }
  return response;
}

/**
 * Build a 400 envelope when the client body is not parseable JSON. Same
 * shape as `ApiErrorBody` so the UI layer renders it uniformly.
 */
function buildClientValidationError(requestId: string | null): NextResponse {
  const response = NextResponse.json(
    { code: VALIDATION_ERROR_CODE, message: VALIDATION_ERROR_MESSAGE },
    { status: 400 },
  );
  if (requestId) {
    response.headers.set(REQUEST_ID_HEADER, requestId);
  }
  return response;
}

/**
 * Narrow guard: returns true only when the upstream JSON body has the
 * minimum shape we need to extract a refresh token and respond to the
 * client. We deliberately validate just enough — full schema validation
 * is the backend's job, and extra fields are forwarded untouched.
 */
function isWellFormedLoginResponse(value: unknown): value is AuthLoginResponse {
  if (!value || typeof value !== "object") return false;
  const v = value as Record<string, unknown>;
  if (!v.user || typeof v.user !== "object") return false;
  if (!v.tokens || typeof v.tokens !== "object") return false;
  const tokens = v.tokens as Record<string, unknown>;
  if (typeof tokens.access_token !== "string" || tokens.access_token.length === 0) {
    return false;
  }
  if (typeof tokens.refresh_token !== "string" || tokens.refresh_token.length === 0) {
    return false;
  }
  return true;
}

// ---------------------------------------------------------------------------
// Route handler
// ---------------------------------------------------------------------------

export async function POST(request: NextRequest): Promise<NextResponse> {
  const incomingRequestId = request.headers.get(REQUEST_ID_HEADER);

  // Step 1 — read the client body. We need to peek at `remember` to
  // decide cookie lifetime, and we re-stringify before forwarding so
  // the upstream sees a clean `application/json` payload regardless of
  // how the browser framed the original request.
  let parsedBody: unknown;
  try {
    parsedBody = await request.json();
  } catch {
    return buildClientValidationError(incomingRequestId);
  }

  const remember =
    typeof parsedBody === "object" &&
    parsedBody !== null &&
    (parsedBody as Record<string, unknown>).remember === true;

  // Strip `remember` (and any other purely-local fields) before
  // forwarding so the upstream sees only the schema FastAPI expects.
  // We rebuild the payload from a known whitelist rather than mutating
  // the parsed body — this keeps the proxy resilient to future client
  // additions and to schema drift on the backend side.
  const upstreamPayload: Record<string, unknown> = {};
  if (typeof parsedBody === "object" && parsedBody !== null) {
    const incoming = parsedBody as Record<string, unknown>;
    for (const key of ["email", "phone", "password"] as const) {
      if (incoming[key] !== undefined) {
        upstreamPayload[key] = incoming[key];
      }
    }
  }

  // Step 2 — forward to FastAPI with a hard timeout so a wedged backend
  // cannot stall the request indefinitely.
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), UPSTREAM_TIMEOUT_MS);

  let upstreamResponse: Response;
  try {
    const upstreamHeaders: Record<string, string> = {
      "content-type": "application/json",
    };
    if (incomingRequestId) {
      upstreamHeaders[REQUEST_ID_HEADER] = incomingRequestId;
    }

    upstreamResponse = await fetch(`${getApiBaseUrl()}/auth/login`, {
      method: "POST",
      headers: upstreamHeaders,
      body: JSON.stringify(upstreamPayload),
      signal: controller.signal,
      // Server-to-server hop — never reuse a cached response, never
      // forward browser cookies upstream.
      cache: "no-store",
    });
  } catch {
    return buildProxyUpstreamError(incomingRequestId);
  } finally {
    clearTimeout(timer);
  }

  // Prefer the upstream's request id (canonical FastAPI middleware id)
  // when present; otherwise echo back what the client sent.
  const effectiveRequestId =
    upstreamResponse.headers.get(REQUEST_ID_HEADER) ?? incomingRequestId;

  // Step 3 — non-2xx: forward status + body verbatim, do NOT touch the
  // cookie (the client's session, if any, is unchanged).
  if (!upstreamResponse.ok) {
    const upstreamText = await upstreamResponse.text();
    const passthroughHeaders = new Headers();
    const upstreamContentType = upstreamResponse.headers.get("content-type");
    if (upstreamContentType) {
      passthroughHeaders.set("content-type", upstreamContentType);
    }
    if (effectiveRequestId) {
      passthroughHeaders.set(REQUEST_ID_HEADER, effectiveRequestId);
    }
    return new NextResponse(upstreamText, {
      status: upstreamResponse.status,
      headers: passthroughHeaders,
    });
  }

  // Step 4 — 200: parse, validate, set cookie, return trimmed body.
  let upstreamBody: unknown;
  try {
    upstreamBody = await upstreamResponse.json();
  } catch {
    return buildProxyUpstreamError(effectiveRequestId);
  }

  if (!isWellFormedLoginResponse(upstreamBody)) {
    return buildProxyUpstreamError(effectiveRequestId);
  }

  const { user, tokens } = upstreamBody;

  const response = NextResponse.json(
    {
      user,
      access_token: tokens.access_token,
      expires_in: tokens.expires_in,
    },
    { status: 200 },
  );

  if (effectiveRequestId) {
    response.headers.set(REQUEST_ID_HEADER, effectiveRequestId);
  }

  const { secure, domain } = getCookieAttrs();
  // Build cookie options progressively: when `remember` is false we
  // omit `maxAge` entirely so the browser writes a session cookie.
  const cookieOptions: {
    httpOnly: boolean;
    sameSite: "lax";
    secure: boolean;
    path: string;
    maxAge?: number;
    domain?: string;
  } = {
    httpOnly: true,
    sameSite: "lax",
    secure,
    path: "/",
  };
  if (remember) {
    cookieOptions.maxAge = REMEMBER_MAX_AGE_SECONDS;
  }
  if (domain) {
    cookieOptions.domain = domain;
  }

  response.cookies.set(COOKIE_NAME, tokens.refresh_token, cookieOptions);

  return response;
}
