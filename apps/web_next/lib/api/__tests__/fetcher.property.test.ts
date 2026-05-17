// @vitest-environment node
//
// Feature: web-app-functional-integration, Property 3: Refresh single-flight idempotence
//
// Property tests for `lib/api/fetcher.ts` — single-flight refresh scheduler.
//
// Feature: web-app-functional-integration, Property 3: Refresh single-flight idempotence
//
// Validates: Requirements 2.1.6 (refresh + expiry handling, no refresh storm).
//
// Environment note: this file forces the Vitest `node` environment via the
// `@vitest-environment node` directive at the top. The default jsdom env
// (set in `vitest.config.ts`) installs jsdom's own `AbortController` /
// `AbortSignal` on `globalThis`, but Node 24's undici-backed `fetch`
// brand-checks the signal against Node's own `AbortSignal` class and
// throws `TypeError: RequestInit: Expected signal (...) to be an instance
// of AbortSignal` for jsdom signals. The fetcher's `composeSignal` always
// passes one, so under jsdom every `apiFetch` call would synthesize a
// spurious `NETWORK_ERROR`. Running this file under the `node` env keeps
// `globalThis.fetch` and `globalThis.AbortController` consistent with one
// another, which is also closer to the real browser execution model the
// fetcher targets in production. The properties under test are pure HTTP
// concurrency semantics — there is no DOM dependency to lose.
//
// Universal claim under test:
//   For any n in [2, 16] concurrent `apiFetch` calls that all observe a 401
//   from a protected endpoint, the fetcher SHALL:
//     (a) issue exactly ONE `POST /api/auth/refresh` round-trip — every
//         concurrent caller awaits the same in-flight promise and is retried
//         with the same rotated access token;
//     (b) resolve every one of the n calls with the protected endpoint's
//         success body (proving the retry happened with the new bearer);
//     (c) leave `tokenStore` populated with the rotated access token after
//         settle;
//     (d) re-arm so that a subsequent fresh 401 (after clearing the token
//         store) triggers a NEW refresh — the counter must increment to 2.
//
// Why this matters: the refresh scheduler is the only place in the client
// that mutates module-level state (`_refreshPromise`) under concurrency. A
// regression here would manifest as a refresh storm (every 401 fires its own
// `/api/auth/refresh`), which the design explicitly forbids.
//
// Test environment notes:
//   - Vitest runs this file under the `node` env (see directive above).
//     The fetcher's `resolveUrl` resolves same-origin auth-proxy paths
//     (`/api/auth/refresh`, `/api/auth/logout`) against
//     `globalThis.location.origin` when present and a deterministic
//     `http://localhost:3000` fallback otherwise — so the URL handed to
//     undici's `fetch` is always absolute, which is required when
//     running under bare node (no realm origin to resolve against).
//     MSW's wildcard prefix pattern matches identically.
//   - The default MSW handlers (in `test/msw/handlers.ts`) cover the
//     FastAPI-prefixed routes `/api/v1/auth/me` and `/api/v1/auth/refresh`,
//     but NOT the same-origin Next.js proxy path `/api/auth/refresh`. We
//     register a per-iteration handler for the proxy so the counter is
//     correctly scoped.
//   - `onUnhandledRequest: "error"` is enabled in `test/setup.ts`, so we
//     also stub the same-origin logout proxy defensively, even though the
//     happy path under test never hits the failure branch that fires it.

import { beforeEach, describe, expect, it } from "vitest";
import * as fc from "fast-check";
import { http, HttpResponse } from "msw";

import { server } from "../../../test/msw/server";
import { apiFetch, __resetRefreshForTests } from "../fetcher";
import { tokenStore } from "../../auth/tokenStore";

/** Prefix used by the MSW refresh handler when minting rotated tokens.
 *  The protected endpoint accepts any `Authorization: Bearer <prefix>...`
 *  as proof that the retry happened post-rotation. */
const ROTATED_TOKEN_PREFIX = "rotated-access-token-";

/** Tiny await inside the refresh handler so all `n` concurrent 401s have
 *  unambiguously reached the `await refreshOnce()` join point before the
 *  refresh promise settles. Without this delay, the test would still pass
 *  in practice (microtask interleaving lets concurrent apiFetch calls
 *  join before the refresh fetch returns), but the explicit delay
 *  removes any scheduling-flakiness risk under different runtimes. */
const REFRESH_DELAY_MS = 15;

describe("Property 3: Refresh single-flight idempotence", () => {
  beforeEach(() => {
    // Each test starts with a clean scheduler holder and an empty
    // token store so the very first `apiFetch` necessarily issues a
    // request without an `Authorization` header — guaranteeing 401.
    __resetRefreshForTests();
    tokenStore.clear();
  });

  it(
    "collapses n concurrent 401s onto a single /api/auth/refresh call and re-arms after settle",
    async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.integer({ min: 2, max: 16 }),
          async (n) => {
            // Reset between fast-check iterations: previous runs leave
            // `tokenStore` populated with a rotated token (assertion (c)),
            // which would cause the next iteration's first `apiFetch` to
            // succeed on the first try and bypass the refresh path.
            __resetRefreshForTests();
            tokenStore.clear();

            let refreshCounter = 0;

            server.use(
              // Same-origin Next.js proxy. Each invocation increments
              // the counter and mints a unique rotated token, so the
              // round-1 vs round-2 assertions can distinguish them.
              http.post("*/api/auth/refresh", async () => {
                await new Promise((r) => setTimeout(r, REFRESH_DELAY_MS));
                refreshCounter += 1;
                return HttpResponse.json({
                  access_token: `${ROTATED_TOKEN_PREFIX}${refreshCounter}`,
                  expires_in: 3600,
                });
              }),

              // Protected endpoint behind FastAPI's `/api/v1` prefix.
              // Returns 200 only when the caller presents a bearer that
              // starts with our rotated-token prefix (i.e. the post-
              // refresh retry). Otherwise returns 401, which is what
              // forces the fetcher into the refresh-and-retry branch.
              http.get("*/api/v1/auth/me", ({ request }) => {
                const auth = request.headers.get("authorization") ?? "";
                if (auth.startsWith(`Bearer ${ROTATED_TOKEN_PREFIX}`)) {
                  return HttpResponse.json({
                    id: "00000000-0000-0000-0000-000000000001",
                    email: "test.user@medisign.ai",
                    phone: null,
                    username: "test_user",
                    full_name: "Người Dùng Thử",
                    is_email_verified: true,
                    is_phone_verified: false,
                    account_type: "user",
                    created_at: "2024-01-01T00:00:00Z",
                  });
                }
                return HttpResponse.json(
                  {
                    code: "AUTH_INVALID_TOKEN",
                    message: "Token không hợp lệ",
                  },
                  { status: 401 },
                );
              }),

              // Defensive: the fetcher only hits the logout proxy on the
              // refresh-failure branch (which this test never enters).
              // Stubbed so MSW's `onUnhandledRequest: "error"` policy
              // never trips even if a regression flips the branch.
              http.post("*/api/auth/logout", () =>
                HttpResponse.json({ message: "ok" }),
              ),
            );

            // ------------------------------------------------------------------
            // Round 1: n concurrent calls, all observe 401, all join the
            // shared refresh promise.
            // ------------------------------------------------------------------

            const calls: Promise<{ id: string }>[] = Array.from(
              { length: n },
              () => apiFetch<{ id: string }>("/auth/me"),
            );
            const settled = await Promise.allSettled(calls);
            const results: { id: string }[] = [];
            for (const s of settled) {
              if (s.status === "rejected") {
                // Surface the rejection with diagnostic context so a
                // counter-example points us at the failing call rather
                // than the bare `Promise.all` first-rejection error.
                throw new Error(
                  `apiFetch round-1 rejection: ${String((s.reason as Error)?.message ?? s.reason)} (refreshCounter=${refreshCounter}, n=${n}, token=${tokenStore.get()})`,
                );
              }
              results.push(s.value);
            }

            // (a) Exactly one POST /api/auth/refresh was issued.
            expect(refreshCounter).toBe(1);

            // (b) Every concurrent call resolved with the protected
            //     endpoint's success body — proving each was retried
            //     with the rotated bearer.
            expect(results).toHaveLength(n);
            for (const r of results) {
              expect(r.id).toBe("00000000-0000-0000-0000-000000000001");
            }

            // (c) Token store now holds the round-1 rotated access
            //     token (set by `refreshOnce`).
            expect(tokenStore.get()).toBe(`${ROTATED_TOKEN_PREFIX}1`);

            // ------------------------------------------------------------------
            // Round 2: after the in-flight promise has settled,
            // `_refreshPromise` should be back to `null`. Clear the
            // token store so the next call's first attempt 401s, and
            // verify that triggers a SECOND, fresh refresh round-trip.
            // ------------------------------------------------------------------

            __resetRefreshForTests();
            tokenStore.clear();

            const after = await apiFetch<{ id: string }>("/auth/me");

            expect(after.id).toBe("00000000-0000-0000-0000-000000000001");
            // (d) Counter increments — the scheduler did not memoize
            //     the previous round's promise.
            expect(refreshCounter).toBe(2);
            expect(tokenStore.get()).toBe(`${ROTATED_TOKEN_PREFIX}2`);
          },
        ),
        { numRuns: 5 },
      );
    },
    30_000,
  );
});
