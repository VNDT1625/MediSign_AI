import { NextResponse, type NextRequest } from "next/server";

/**
 * Edge middleware route guard for the protected `/app/*` shell.
 *
 * Behavior (Requirements 2.2.1):
 * - If the `medisign_rt` refresh-token cookie is missing, the user is
 *   considered anonymous and is redirected to `/?login=1&intent=<path>`,
 *   which causes the landing page to auto-open the LoginModal and replay
 *   the original destination after a successful login (smart redirect,
 *   Requirements 2.1.4).
 * - If the cookie is present, the request passes through. The cookie's
 *   *cryptographic* validity is not checked here — the Edge runtime has
 *   no DB access and verifying a JWT inline would add latency on every
 *   navigation. Real verification happens once in the server layout via
 *   `GET /auth/me`; this guard only suppresses the public-UI flash.
 *
 * Open-redirect guarantee:
 * - The `intent` query value placed on the redirect URL is the literal
 *   `pathname + search` of the original request (e.g. `"/app/medicine"`
 *   or `"/app/chat?prefill=hi"`). The middleware deliberately does NOT
 *   sanitize this value — that responsibility lives entirely with the
 *   consumer in `lib/utils/intent.ts`, whose `decodeIntent` runs every
 *   captured intent through an explicit allowlist:
 *     - `"home"`, `"chat"`, or any path starting with `"/app/"` is kept,
 *     - everything else (external URLs, protocol-relative `//evil.com`,
 *       arbitrary strings, missing values) collapses to the safe
 *       fallback `"chat"`.
 *   Because this matcher only fires for `/app/:path*`, the path written
 *   here is already inside the allowlist domain, so the round-trip is
 *   lossless. If a future refactor ever stuffs a non-`/app` value into
 *   this param, the consumer-side allowlist is the single line of
 *   defense and will neutralize it. See Requirements 3.1 (open redirect
 *   defense).
 *
 * Tests for this guard live in task 7.4 (integration) and task 15.4 (E2E).
 */

export const config = {
  matcher: ["/app/:path*"],
};

export function middleware(req: NextRequest) {
  const refreshToken = req.cookies.get("medisign_rt");
  if (!refreshToken) {
    const redirectUrl = new URL("/", req.url);
    redirectUrl.searchParams.set("login", "1");
    redirectUrl.searchParams.set(
      "intent",
      req.nextUrl.pathname + req.nextUrl.search,
    );
    return NextResponse.redirect(redirectUrl);
  }
  return NextResponse.next();
}
