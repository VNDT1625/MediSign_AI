/**
 * `app/api/auth/logout/route.ts` — Next.js Route Handler proxy that ends
 * the current web session.
 *
 * Phase 1 design: the refresh token lives in the `medisign_rt` httpOnly
 * cookie set by `/api/auth/login`. Logout is **best-effort**:
 *
 *   1. If the cookie is present, forward `{refresh_token}` to FastAPI
 *      `POST /auth/logout` so the server can revoke the session. Any
 *      upstream failure (network error, 401, 5xx, malformed JSON) is
 *      swallowed — we never let it block step 2.
 *   2. Always respond `200 { message: "Đã đăng xuất" }` to the client,
 *      with `Set-Cookie: medisign_rt=; Max-Age=0` so the browser drops
 *      the cookie regardless of upstream outcome.
 *
 * This guarantees the client-side logout flow (`tokenStore.clear()` +
 * redirect to `/`) always succeeds — matching A5 in requirements.md
 * ("IF API logout fail, THEN THE web SHALL vẫn xoá token client").
 *
 * @see Requirements 2.1.5 (đăng xuất) — best-effort logout contract.
 * @see Design — "Auth Subsystem" / logout proxy in design.md.
 * @see `apps/backend_fastapi/app/api/routes/auth.py` for the upstream
 *   endpoint shape.
 */

import { NextResponse, type NextRequest } from "next/server";

// Cookie write requires Node APIs (`Set-Cookie`) — Edge runtime is not
// needed and would force us to drop the convenient `cookies.set()` API.
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

/** Hard cap on the upstream call so a slow/dead backend cannot stall us. */
const UPSTREAM_TIMEOUT_MS = 5_000;

/** vi-VN copy returned to the client on every logout. */
const LOGOUT_MESSAGE = "Đã đăng xuất";

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
 *   - `AUTH_COOKIE_DOMAIN` — explicit cookie domain; omitted when blank
 *     (browser defaults to the current host, which is what localhost
 *     wants).
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
 * Best-effort fire-and-forget call to FastAPI `/auth/logout`. Wraps every
 * failure mode (network, timeout, non-2xx, malformed body) and returns
 * silently — the client outcome must not depend on upstream success.
 */
async function forwardLogoutUpstream(
  refreshToken: string,
  requestId: string | null,
): Promise<void> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), UPSTREAM_TIMEOUT_MS);

  try {
    const headers: Record<string, string> = {
      "content-type": "application/json",
    };
    if (requestId) {
      headers[REQUEST_ID_HEADER] = requestId;
    }

    await fetch(`${getApiBaseUrl()}/auth/logout`, {
      method: "POST",
      headers,
      body: JSON.stringify({ refresh_token: refreshToken }),
      signal: controller.signal,
      // Server-to-server hop — never expose browser cookies upstream.
      cache: "no-store",
    });
    // Intentionally ignore the response — best-effort logout means the
    // client-visible result is identical whether this returned 200 or 500.
  } catch {
    // Swallow network errors / timeouts / aborts. Cookie clearing in the
    // caller still runs.
  } finally {
    clearTimeout(timer);
  }
}

// ---------------------------------------------------------------------------
// Route handler
// ---------------------------------------------------------------------------

export async function POST(request: NextRequest): Promise<NextResponse> {
  const refreshToken = request.cookies.get(COOKIE_NAME)?.value;
  const requestId = request.headers.get(REQUEST_ID_HEADER);

  // Step 1 — best-effort upstream revocation. Only attempt when we
  // actually have a refresh token to revoke; an anonymous logout (cookie
  // already missing) should not waste an upstream round-trip.
  if (refreshToken) {
    await forwardLogoutUpstream(refreshToken, requestId);
  }

  // Step 2 — always respond 200 + clear the cookie.
  const response = NextResponse.json(
    { message: LOGOUT_MESSAGE },
    { status: 200 },
  );

  if (requestId) {
    response.headers.set(REQUEST_ID_HEADER, requestId);
  }

  const { secure, domain } = getCookieAttrs();
  response.cookies.set(COOKIE_NAME, "", {
    maxAge: 0,
    path: "/",
    httpOnly: true,
    sameSite: "lax",
    secure,
    ...(domain ? { domain } : {}),
  });

  return response;
}
