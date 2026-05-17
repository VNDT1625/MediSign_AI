/**
 * `app/app/layout.tsx` — server-rendered auth boundary for the protected
 * `/app/*` shell.
 *
 * This is the second layer of the defense-in-depth auth guard described in
 * design.md → "Edge middleware + Route Handler proxy" rationale:
 *
 *   1. **Edge middleware** (`apps/web_next/middleware.ts`) — fast cookie
 *      presence check; redirects to `/?login=1&intent=<path>` when the
 *      `medisign_rt` cookie is missing. Suppresses public-UI flash but
 *      cannot tell whether the cookie is still cryptographically valid.
 *
 *   2. **This server layout** — runs on every protected navigation. With
 *      access to the Node runtime, it actually validates the refresh
 *      token by exchanging it for an access token and fetching the user
 *      profile. On any failure (cookie expired / revoked / backend
 *      unreachable / malformed body) it redirects to
 *      `/?login=1&session=expired`, which the landing page consumes to
 *      auto-open `LoginModal` with a "Phiên đã hết hạn" banner.
 *
 *   3. **Client `AuthProvider`** (`lib/auth/AuthProvider.tsx`) — re-runs
 *      the same refresh + me sequence in the browser to populate the
 *      reactive auth state machine that `useAuth()` exposes to every
 *      client component. Each `/app/*` page independently mounts
 *      `<DesktopAppHeader>` and consumes that state, so this layout
 *      deliberately renders **no chrome**: stacking another header here
 *      would duplicate the per-page one.
 *
 *      Likewise, this layout deliberately does **not** mount `<Providers>`
 *      — that is already done once in the root `app/layout.tsx`. Mounting
 *      it again would create a second `QueryClient` and a second
 *      `AuthProvider`, halving cache hit rates and racing two parallel
 *      hydration cycles against `/auth/me`.
 *
 * ## Refresh-token rotation caveat (Phase 1, accepted downside)
 *
 * The server-side validation here calls FastAPI `POST /auth/refresh`
 * **directly**, NOT via the same-origin `/api/auth/refresh` Next.js Route
 * Handler proxy. Two reasons make the proxy detour unworkable for an SSR
 * boundary:
 *
 *   - Server Components cannot mutate response cookies. Even if we
 *     fetched the proxy from here, the `Set-Cookie` header in its
 *     response would never reach the browser — it lands on the proxy's
 *     response object, which we receive via `fetch()` and discard.
 *   - The proxy's primary purpose is to bridge the JSON-body refresh
 *     token into an httpOnly cookie for the browser. On the server we
 *     already hold the refresh token in our hand (read from the request
 *     cookie); the proxy adds nothing.
 *
 * Calling FastAPI directly means **the rotated refresh token returned
 * by this hop is discarded**. The `medisign_rt` cookie in the user's
 * browser still holds the *previous* refresh token. Two consequences:
 *
 *   - If the backend's `auth_service.refresh_tokens` revokes the old
 *     refresh token on every successful rotation (current behaviour —
 *     see `apps/backend_fastapi/app/services/auth_service.py`), the next
 *     time the browser-side fetcher's `refreshOnce()` calls
 *     `/api/auth/refresh`, that proxy will forward the now-stale token
 *     and receive a 401. The user is then logged out and bounced to
 *     `/?session=expired` — the same failure mode as a naturally
 *     expired token, just triggered earlier.
 *   - In practice this means each protected SSR navigation costs the
 *     user one client-side refresh cycle on the next 401. Functional,
 *     but suboptimal.
 *
 * **Phase 2 fix** (out of scope here): expose a Server Action that
 * issues `Set-Cookie` itself, or move this validation into a Route
 * Handler that the layout fetches (where we *can* propagate cookies via
 * `cookies().set()` because Route Handlers run in a writable cookie
 * context). For now we document the trade-off and accept it.
 *
 * @see Requirements 2.2.1 (route guard) and 2.2.2 (auth context).
 * @see design.md — "Auth Subsystem" and "Edge middleware + Route
 *   Handler proxy" rationale.
 */

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import type { ReactNode } from "react";

import type { AuthUserResponse } from "@medisign/shared-contracts";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/**
 * Fallback API base URL — kept identical to the proxy routes
 * (`app/api/auth/*`) and the client-side `lib/api/fetcher.ts` so the entire
 * web layer points at the same backend instance in dev.
 */
const DEFAULT_API_BASE_URL = "http://localhost:8000/api/v1";

/** Name of the httpOnly cookie that carries the refresh token. */
const COOKIE_NAME = "medisign_rt";

/**
 * Hard cap on the upstream calls (refresh + me) so a slow / dead backend
 * cannot stall navigation indefinitely. 5s mirrors the refresh proxy.
 */
const UPSTREAM_TIMEOUT_MS = 5_000;

/**
 * Destination when the session cannot be re-established. The landing
 * page reads `session=expired` and auto-opens `LoginModal` with a
 * "Phiên đã hết hạn, vui lòng đăng nhập lại" banner (Requirements 2.1.6).
 */
const SESSION_EXPIRED_REDIRECT = "/?login=1&session=expired";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Read `NEXT_PUBLIC_API_BASE_URL` at request time, trimming trailing `/`. */
function getApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_BASE_URL || DEFAULT_API_BASE_URL;
  return raw.replace(/\/+$/, "");
}

/**
 * Server-side session validation. Returns the authenticated user on
 * success, or `null` on any failure (no cookie, refresh rejected, /me
 * rejected, network/timeout/parse error). Never throws — the caller
 * simply branches on the nullable result.
 *
 * Failure modes deliberately collapse to a single `null`:
 *   - missing `medisign_rt` cookie (defence-in-depth — middleware
 *     already redirects, but a same-origin direct render could theoretically
 *     reach here without going through middleware);
 *   - upstream `/auth/refresh` non-2xx (token expired / revoked /
 *     account disabled / backend 5xx);
 *   - upstream returned 200 but with a malformed body (no
 *     `access_token`);
 *   - upstream `/auth/me` non-2xx (the access token we just minted is
 *     somehow invalid — e.g. account just disabled between the two
 *     calls);
 *   - any thrown error (network, timeout, JSON parse).
 *
 * The shared 5s `AbortController` is passed to both `fetch` calls so a
 * slow refresh response cannot cause us to exceed the budget when the
 * subsequent /me request also drags.
 */
async function getCurrentUser(): Promise<AuthUserResponse | null> {
  const cookieStore = cookies();
  const refreshToken = cookieStore.get(COOKIE_NAME)?.value;
  if (!refreshToken || refreshToken.length === 0) {
    return null;
  }

  const apiBase = getApiBaseUrl();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), UPSTREAM_TIMEOUT_MS);

  try {
    // -----------------------------------------------------------------
    // 1. Exchange refresh token for an access token (NOT via the
    //    same-origin proxy — see file-header caveat).
    // -----------------------------------------------------------------
    const refreshResponse = await fetch(`${apiBase}/auth/refresh`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        accept: "application/json",
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
      // SSR boundary: never cache, never share across users.
      cache: "no-store",
      signal: controller.signal,
    });

    if (!refreshResponse.ok) {
      return null;
    }

    let tokenBody: { access_token?: unknown };
    try {
      tokenBody = (await refreshResponse.json()) as { access_token?: unknown };
    } catch {
      return null;
    }

    const accessToken = tokenBody.access_token;
    if (typeof accessToken !== "string" || accessToken.length === 0) {
      return null;
    }

    // -----------------------------------------------------------------
    // 2. Fetch the user profile with the freshly minted bearer.
    // -----------------------------------------------------------------
    const meResponse = await fetch(`${apiBase}/auth/me`, {
      method: "GET",
      headers: {
        accept: "application/json",
        authorization: `Bearer ${accessToken}`,
      },
      cache: "no-store",
      signal: controller.signal,
    });

    if (!meResponse.ok) {
      return null;
    }

    try {
      return (await meResponse.json()) as AuthUserResponse;
    } catch {
      return null;
    }
  } catch {
    // Network failure, timeout, AbortError — treat as unrecoverable.
    return null;
  } finally {
    clearTimeout(timer);
  }
}

// ---------------------------------------------------------------------------
// Layout
// ---------------------------------------------------------------------------

/**
 * Server component layout for the `/app/*` shell. Validates the session
 * before rendering and `redirect()`s anonymous / expired requests to the
 * landing page with the `session=expired` flag set so `LoginModal`
 * auto-opens.
 *
 * Renders `{children}` directly — no chrome, no providers, no header.
 * See the file-header for the rationale ("each /app page mounts its own
 * `DesktopAppHeader`; root layout already wraps `<Providers>`").
 */
export default async function AppLayout({
  children,
}: {
  children: ReactNode;
}) {
  const user = await getCurrentUser();
  if (!user) {
    // `redirect()` throws a special signal that Next.js intercepts; it
    // never returns. No further code in this function runs.
    redirect(SESSION_EXPIRED_REDIRECT);
  }

  return <main className="pt-20">{children}</main>;
}
