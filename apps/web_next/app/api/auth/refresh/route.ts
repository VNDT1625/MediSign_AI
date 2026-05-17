/**
 * `app/api/auth/refresh/route.ts` — Next.js Route Handler proxy that
 * rotates the short-lived access token using the refresh token stored
 * in the `medisign_rt` httpOnly cookie.
 *
 * Phase 1 design (see "Auth Subsystem" + 401-refresh-retry sequence in
 * design.md): the FastAPI backend returns refresh tokens in the JSON
 * body of `POST /auth/refresh`. JS in the browser must never see them,
 * so this same-origin proxy:
 *
 *   1. Reads `medisign_rt` from the incoming request cookies. If the
 *      cookie is missing, responds `401` with the canonical envelope
 *      `{code: "AUTH_INVALID_TOKEN", message: "Phiên đăng nhập không
 *      hợp lệ"}` so the fetcher can short-circuit to "log in again" UX
 *      without touching the upstream.
 *   2. Forwards `{refresh_token: <cookie value>}` to FastAPI
 *      `POST ${API_BASE}/auth/refresh` (schema `AuthRefreshRequest` in
 *      `apps/backend_fastapi/app/schemas/auth.py`).
 *   3. On upstream `200`: rotates the cookie with the new
 *      `refresh_token` (httpOnly, SameSite=Lax, Secure per env, Path=/,
 *      Max-Age=2592000 — 30 days, matching login `remember=true`) and
 *      returns `{access_token, expires_in}` to the client. The new
 *      `refresh_token` is intentionally NOT echoed in the response
 *      body — the cookie is the only durable holder.
 *   4. On any upstream failure (non-2xx response, network error, body
 *      that is not valid JSON, malformed `AuthTokenPair`): clears the
 *      cookie and responds with HTTP `401`. The body is the upstream
 *      `ApiErrorBody` envelope when one is parseable, otherwise a
 *      synthesized `{code: "AUTH_INVALID_TOKEN", message: "..."}`. The
 *      fetcher's `failRefresh` path then surfaces the canonical
 *      `AUTH_SESSION_EXPIRED` UX regardless of the inner code.
 *
 * `x-request-id` is propagated both upstream (so backend logs correlate)
 * and back to the browser (so the toast can surface a support ref).
 *
 * @see Requirements 2.1.6 (refresh + storage + single-flight retry).
 * @see `apps/backend_fastapi/app/api/routes/auth.py` (`refresh_route`).
 * @see `apps/web_next/lib/api/fetcher.ts` (`refreshOnce`) for the caller.
 */

import { NextResponse, type NextRequest } from "next/server";

import type { ApiErrorBody } from "@medisign/shared-contracts";

// Cookie writes need Node APIs (`Set-Cookie` via NextResponse.cookies); the
// Edge runtime would force us to drop the convenient typed cookie API and
// is unnecessary for this server-to-server hop.
export const runtime = "nodejs";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Name of the httpOnly cookie that stores the refresh token. */
const COOKIE_NAME = "medisign_rt";

/** Fallback API base URL — mirrors `lib/api/fetcher.ts` and the login proxy. */
const DEFAULT_API_BASE_URL = "http://localhost:8000/api/v1";

/** Correlation id header forwarded both upstream and back to the client. */
const REQUEST_ID_HEADER = "x-request-id";

/** Hard cap on the upstream call so a slow/dead backend cannot stall us. */
const UPSTREAM_TIMEOUT_MS = 5_000;

/**
 * Cookie lifetime on rotation (seconds). 30 days mirrors the login proxy's
 * `remember=true` default — the original cookie's `Max-Age` is not
 * recoverable from the incoming request (Next.js `cookies.get` only
 * exposes name + value), so we standardise on the longest sensible
 * window. Refresh tokens themselves carry their own expiry server-side.
 */
const COOKIE_MAX_AGE_SECONDS = 60 * 60 * 24 * 30;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/**
 * Body returned by the FastAPI `/auth/refresh` endpoint. Mirrors
 * `AuthTokenPair` in `apps/backend_fastapi/app/schemas/auth.py`.
 *
 * Defined locally rather than imported because the rotation logic only
 * cares about three fields and the proxy is the boundary that strips
 * the refresh token before it reaches JS.
 */
interface UpstreamRefreshResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Read `NEXT_PUBLIC_API_BASE_URL` at request time, trimming trailing `/`. */
function getApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_BASE_URL || DEFAULT_API_BASE_URL;
  return raw.replace(/\/+$/, "");
}

/**
 * Resolve the cookie attributes from env so dev (HTTP, no domain) and
 * prod (HTTPS, optional shared domain) both work without code changes.
 *
 *   - `AUTH_COOKIE_SECURE` — `"true"` to set the `Secure` flag.
 *   - `AUTH_COOKIE_DOMAIN` — explicit cookie domain; omitted when blank.
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
 * Apply the canonical "clear refresh cookie" mutation to a response.
 * Used in every failure path so the browser drops `medisign_rt` and the
 * user is forced through `LoginModal` on the next protected navigation.
 */
function clearRefreshCookie(response: NextResponse): void {
  const { secure, domain } = getCookieAttrs();
  response.cookies.set(COOKIE_NAME, "", {
    maxAge: 0,
    path: "/",
    httpOnly: true,
    sameSite: "lax",
    secure,
    ...(domain ? { domain } : {}),
  });
}

/**
 * Apply a freshly issued refresh token to the response cookie.
 * Mirrors the flags used by `/api/auth/login` so the rotated cookie
 * is indistinguishable from the original to the browser.
 */
function setRefreshCookie(response: NextResponse, refreshToken: string): void {
  const { secure, domain } = getCookieAttrs();
  response.cookies.set(COOKIE_NAME, refreshToken, {
    maxAge: COOKIE_MAX_AGE_SECONDS,
    path: "/",
    httpOnly: true,
    sameSite: "lax",
    secure,
    ...(domain ? { domain } : {}),
  });
}

/** Helper: copy `x-request-id` from request → response when present. */
function propagateRequestId(
  response: NextResponse,
  requestId: string | null,
): void {
  if (requestId) {
    response.headers.set(REQUEST_ID_HEADER, requestId);
  }
}

/**
 * Build the canonical "session is no good — log in again" envelope. Used
 * for every failure path (missing cookie, upstream error, malformed
 * response, network/parse failure) so the fetcher's `failRefresh` path
 * sees a uniform 401 + `ApiErrorBody` shape regardless of the
 * underlying cause. Always pairs with `clearRefreshCookie` so the
 * browser drops `medisign_rt`.
 */
function buildInvalidTokenResponse(
  requestId: string | null,
  message = "Phiên đăng nhập không hợp lệ",
): NextResponse {
  const body: ApiErrorBody = {
    code: "AUTH_INVALID_TOKEN",
    message,
    request_id: requestId ?? null,
  };
  const response = NextResponse.json(body, { status: 401 });
  propagateRequestId(response, requestId);
  clearRefreshCookie(response);
  return response;
}

/**
 * Detect whether an arbitrary upstream JSON body matches the FastAPI
 * `ApiErrorBody` envelope shape. We only require `code` + `message` to
 * be non-empty strings; `details` and `request_id` are optional and
 * forwarded as-is. Returning `true` means the body can be safely echoed
 * back to the client without leaking proxy state.
 */
function isApiErrorBody(value: unknown): value is ApiErrorBody {
  if (!value || typeof value !== "object") return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.code === "string" &&
    v.code.length > 0 &&
    typeof v.message === "string" &&
    v.message.length > 0
  );
}

// ---------------------------------------------------------------------------
// Route handler
// ---------------------------------------------------------------------------

export async function POST(request: NextRequest): Promise<NextResponse> {
  const refreshToken = request.cookies.get(COOKIE_NAME)?.value;
  const requestId = request.headers.get(REQUEST_ID_HEADER);

  // -------------------------------------------------------------------------
  // 1. No cookie → short-circuit 401. Do not even try the upstream.
  // -------------------------------------------------------------------------
  if (!refreshToken) {
    return buildInvalidTokenResponse(requestId);
  }

  // -------------------------------------------------------------------------
  // 2. Forward to FastAPI /auth/refresh.
  // -------------------------------------------------------------------------
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), UPSTREAM_TIMEOUT_MS);

  let upstream: Response;
  try {
    const upstreamHeaders: Record<string, string> = {
      "content-type": "application/json",
      accept: "application/json",
    };
    if (requestId) {
      upstreamHeaders[REQUEST_ID_HEADER] = requestId;
    }

    upstream = await fetch(`${getApiBaseUrl()}/auth/refresh`, {
      method: "POST",
      headers: upstreamHeaders,
      body: JSON.stringify({ refresh_token: refreshToken }),
      signal: controller.signal,
      // Server-to-server hop: never expose browser cookies upstream
      // and never cache rotated tokens.
      cache: "no-store",
    });
  } catch {
    // Network / timeout / abort failure — backend unreachable. Treat
    // the session as untrusted: clear the cookie and surface 401 so
    // the fetcher's `failRefresh` path runs the canonical
    // AUTH_SESSION_EXPIRED redirect.
    return buildInvalidTokenResponse(requestId);
  } finally {
    clearTimeout(timer);
  }

  // -------------------------------------------------------------------------
  // 3. Upstream non-2xx → clear cookie and respond 401 with the upstream
  //    `ApiErrorBody` when present, otherwise the canonical envelope.
  //    The HTTP status is normalized to 401 regardless of the upstream
  //    status (per task contract): the only signal the client needs is
  //    "your refresh token did not work — log in again".
  // -------------------------------------------------------------------------
  if (!upstream.ok) {
    let upstreamBody: unknown = null;
    try {
      upstreamBody = await upstream.clone().json();
    } catch {
      // Non-JSON bodies (HTML from a misconfigured proxy, plain text,
      // empty) collapse onto the synthesized envelope below.
      upstreamBody = null;
    }

    if (isApiErrorBody(upstreamBody)) {
      const response = NextResponse.json(upstreamBody, { status: 401 });
      propagateRequestId(response, requestId);
      clearRefreshCookie(response);
      return response;
    }
    return buildInvalidTokenResponse(requestId);
  }

  // -------------------------------------------------------------------------
  // 4. Upstream 200 → rotate cookie, return access token only.
  // -------------------------------------------------------------------------
  let upstreamBody: UpstreamRefreshResponse;
  try {
    upstreamBody = (await upstream.json()) as UpstreamRefreshResponse;
  } catch {
    // Upstream lied about its content-type or returned malformed JSON —
    // we cannot trust the rotated session, fail closed.
    return buildInvalidTokenResponse(requestId);
  }

  // Defensive: if the backend ever returned 200 without the expected
  // fields (refactor regression, schema drift), fail closed rather than
  // silently writing an empty cookie or undefined token into the store.
  if (
    typeof upstreamBody.access_token !== "string" ||
    upstreamBody.access_token.length === 0 ||
    typeof upstreamBody.refresh_token !== "string" ||
    upstreamBody.refresh_token.length === 0 ||
    typeof upstreamBody.expires_in !== "number"
  ) {
    return buildInvalidTokenResponse(requestId);
  }

  // Strip refresh_token from the body — the cookie is the only durable
  // holder. The client only needs `access_token` + `expires_in` to
  // populate `tokenStore`.
  const response = NextResponse.json(
    {
      access_token: upstreamBody.access_token,
      expires_in: upstreamBody.expires_in,
    },
    { status: 200 },
  );

  propagateRequestId(response, requestId);
  setRefreshCookie(response, upstreamBody.refresh_token);

  return response;
}
