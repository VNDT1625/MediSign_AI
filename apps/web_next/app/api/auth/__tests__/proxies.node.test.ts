// @vitest-environment node
//
// Integration tests for the auth Route Handler proxies under
// `app/api/auth/{login,refresh,logout}/route.ts`.
//
// Validates: Requirements 2.1.2 (login flow + cookie bridge),
//   2.1.5 (logout best-effort + cookie clearing),
//   2.1.6 (refresh rotates the cookie / clears on failure).
//
// Environment note: this file forces the Vitest `node` environment via
// the `@vitest-environment node` directive at the top. The Route
// Handlers under test are server-side modules that import `next/server`
// (`NextRequest` / `NextResponse`), and they call `fetch` with an
// `AbortSignal` produced by Node's `AbortController`. Under the default
// jsdom env, jsdom installs its own `AbortSignal` on `globalThis`; Node
// 24's undici-backed `fetch` then brand-checks the signal against
// Node's class and throws "Expected signal to be an instance of
// AbortSignal", which would make every upstream call synthesize a
// spurious network failure. Running this file under the `node` env
// keeps `globalThis.fetch` and `globalThis.AbortController` consistent
// with one another and matches the runtime the proxies actually run
// in (`export const runtime = "nodejs"`).
//
// Strategy: invoke the exported `POST` handler directly with a
// synthetic `NextRequest`. MSW (registered in `test/msw/server.ts`)
// intercepts the proxy's outbound `fetch` to FastAPI, so each test can
// override individual upstream routes with `server.use(...)` to drive
// the relevant scenario (200, 401, network failure, etc.).
//
// We assert on three observable surfaces:
//   - HTTP status of the proxy response,
//   - JSON body of the proxy response,
//   - `Set-Cookie` header (presence, attributes, value).

import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { http, HttpResponse } from "msw";
import { NextRequest } from "next/server";

import { server } from "../../../../test/msw/server";
import { POST as loginPost } from "../login/route";
import { POST as refreshPost } from "../refresh/route";
import { POST as logoutPost } from "../logout/route";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const COOKIE_NAME = "medisign_rt";
const ROUTE_ORIGIN = "http://localhost:3000";

/** Build a `NextRequest` for `POST /api/auth/<action>`. */
function makeRequest(
  action: "login" | "refresh" | "logout",
  init: { body?: unknown; cookie?: string; headers?: Record<string, string> } = {},
): NextRequest {
  const headers = new Headers(init.headers ?? {});
  if (init.body !== undefined && !headers.has("content-type")) {
    headers.set("content-type", "application/json");
  }
  if (init.cookie) {
    headers.set("cookie", init.cookie);
  }
  const body =
    init.body === undefined ? undefined : JSON.stringify(init.body);

  return new NextRequest(`${ROUTE_ORIGIN}/api/auth/${action}`, {
    method: "POST",
    headers,
    body,
  });
}

/** Parse a `Set-Cookie` header into its name=value pair plus attributes
 *  (lowercased keys, values left untouched). Tolerant of MSW/Next's
 *  formatting quirks: trims whitespace and ignores empty segments. */
function parseSetCookie(raw: string | null): {
  name: string;
  value: string;
  attrs: Record<string, string | true>;
} | null {
  if (!raw) return null;
  const parts = raw.split(";").map((p) => p.trim()).filter((p) => p.length > 0);
  if (parts.length === 0) return null;
  const [first, ...rest] = parts;
  const eq = first!.indexOf("=");
  const name = eq === -1 ? first! : first!.slice(0, eq);
  const value = eq === -1 ? "" : first!.slice(eq + 1);
  const attrs: Record<string, string | true> = {};
  for (const seg of rest) {
    const segEq = seg.indexOf("=");
    if (segEq === -1) {
      attrs[seg.toLowerCase()] = true;
    } else {
      attrs[seg.slice(0, segEq).toLowerCase()] = seg.slice(segEq + 1);
    }
  }
  return { name, value, attrs };
}

// Default API base used by the proxies (mirrors `getApiBaseUrl()` in
// each route file). MSW handlers built around this constant will match
// the upstream calls without needing to mutate `process.env`.
const API = "*/api/v1";

// ---------------------------------------------------------------------------
// Login proxy
// ---------------------------------------------------------------------------

describe("POST /api/auth/login", () => {
  it("happy path (remember=false): forwards Set-Cookie httpOnly+SameSite=Lax, omits Max-Age (session cookie), strips refresh_token from body", async () => {
    server.use(
      http.post(`${API}/auth/login`, async ({ request }) => {
        const body = (await request.json()) as Record<string, unknown>;
        // `remember` is local-only and must NOT reach FastAPI.
        expect(body).not.toHaveProperty("remember");
        return HttpResponse.json({
          user: {
            id: "00000000-0000-0000-0000-000000000001",
            email: "user@example.com",
            phone: null,
            username: "user_one",
            full_name: "User One",
            is_email_verified: true,
            is_phone_verified: false,
            account_type: "user",
            created_at: "2024-01-01T00:00:00Z",
          },
          tokens: {
            access_token: "access-1",
            refresh_token: "refresh-cookie-1",
            token_type: "bearer",
            expires_in: 3600,
          },
        });
      }),
    );

    const req = makeRequest("login", {
      body: {
        email: "user@example.com",
        password: "supersecret1",
        remember: false,
      },
    });
    const res = await loginPost(req);

    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body).toMatchObject({
      access_token: "access-1",
      expires_in: 3600,
      user: { email: "user@example.com" },
    });
    // Refresh token is for the cookie only; never echoed in body.
    expect(body).not.toHaveProperty("refresh_token");
    expect(body).not.toHaveProperty("tokens");

    const setCookie = parseSetCookie(res.headers.get("set-cookie"));
    expect(setCookie).not.toBeNull();
    expect(setCookie!.name).toBe(COOKIE_NAME);
    expect(setCookie!.value).toBe("refresh-cookie-1");
    expect(setCookie!.attrs.httponly).toBe(true);
    expect(String(setCookie!.attrs.samesite).toLowerCase()).toBe("lax");
    expect(setCookie!.attrs.path).toBe("/");
    // remember=false → session cookie, no Max-Age / no Expires.
    expect(setCookie!.attrs["max-age"]).toBeUndefined();
  });

  it("remember=true: cookie carries Max-Age=2592000 (30 days)", async () => {
    server.use(
      http.post(`${API}/auth/login`, () =>
        HttpResponse.json({
          user: {
            id: "00000000-0000-0000-0000-000000000001",
            email: "user@example.com",
            phone: null,
            username: "user_one",
            full_name: "User One",
            is_email_verified: true,
            is_phone_verified: false,
            account_type: "user",
            created_at: "2024-01-01T00:00:00Z",
          },
          tokens: {
            access_token: "access-r",
            refresh_token: "refresh-cookie-r",
            token_type: "bearer",
            expires_in: 3600,
          },
        }),
      ),
    );

    const req = makeRequest("login", {
      body: {
        email: "user@example.com",
        password: "supersecret1",
        remember: true,
      },
    });
    const res = await loginPost(req);

    expect(res.status).toBe(200);
    const setCookie = parseSetCookie(res.headers.get("set-cookie"));
    expect(setCookie).not.toBeNull();
    // 30 days in seconds.
    expect(setCookie!.attrs["max-age"]).toBe("2592000");
  });

  it("upstream 401: forwards status + body verbatim, sets NO cookie", async () => {
    server.use(
      http.post(`${API}/auth/login`, () =>
        HttpResponse.json(
          {
            code: "AUTH_INVALID_CREDENTIALS",
            message: "Email/SDT hoac mat khau khong dung",
          },
          { status: 401 },
        ),
      ),
    );

    const req = makeRequest("login", {
      body: {
        email: "user@example.com",
        password: "wrong",
      },
    });
    const res = await loginPost(req);

    expect(res.status).toBe(401);
    const body = await res.json();
    expect(body).toEqual({
      code: "AUTH_INVALID_CREDENTIALS",
      message: "Email/SDT hoac mat khau khong dung",
    });
    // Failure path must not touch the cookie — the user's session, if
    // any, is unchanged.
    expect(res.headers.get("set-cookie")).toBeNull();
  });

  it("upstream network failure: 502 PROXY_UPSTREAM_ERROR with no cookie", async () => {
    server.use(
      http.post(`${API}/auth/login`, () => HttpResponse.error()),
    );

    const req = makeRequest("login", {
      body: {
        email: "user@example.com",
        password: "supersecret1",
      },
    });
    const res = await loginPost(req);

    expect(res.status).toBe(502);
    const body = await res.json();
    expect(body.code).toBe("PROXY_UPSTREAM_ERROR");
    expect(typeof body.message).toBe("string");
    expect(body.message.length).toBeGreaterThan(0);
    expect(res.headers.get("set-cookie")).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// Refresh proxy
// ---------------------------------------------------------------------------

describe("POST /api/auth/refresh", () => {
  it("with cookie + upstream 200: forwards refresh_token to FastAPI, rotates cookie, returns {access_token, expires_in}", async () => {
    let capturedBody: unknown = null;
    server.use(
      http.post(`${API}/auth/refresh`, async ({ request }) => {
        capturedBody = await request.json();
        return HttpResponse.json({
          access_token: "access-rotated",
          refresh_token: "refresh-rotated",
          token_type: "bearer",
          expires_in: 3600,
        });
      }),
    );

    const req = makeRequest("refresh", {
      cookie: `${COOKIE_NAME}=refresh-original`,
    });
    const res = await refreshPost(req);

    expect(res.status).toBe(200);
    // Upstream received the cookie value as `refresh_token` body field.
    expect(capturedBody).toEqual({ refresh_token: "refresh-original" });

    const body = await res.json();
    expect(body).toEqual({
      access_token: "access-rotated",
      expires_in: 3600,
    });
    // Crucially, the rotated refresh_token is NOT exposed to JS.
    expect(body).not.toHaveProperty("refresh_token");

    // Cookie was rotated to the new value.
    const setCookie = parseSetCookie(res.headers.get("set-cookie"));
    expect(setCookie).not.toBeNull();
    expect(setCookie!.name).toBe(COOKIE_NAME);
    expect(setCookie!.value).toBe("refresh-rotated");
    expect(setCookie!.attrs.httponly).toBe(true);
    expect(String(setCookie!.attrs.samesite).toLowerCase()).toBe("lax");
    expect(setCookie!.attrs.path).toBe("/");
    // Rotation always sets a 30-day window.
    expect(setCookie!.attrs["max-age"]).toBe("2592000");
  });

  it("without cookie: 401 AUTH_INVALID_TOKEN, no upstream call", async () => {
    let upstreamCalled = false;
    server.use(
      http.post(`${API}/auth/refresh`, () => {
        upstreamCalled = true;
        return HttpResponse.json(
          { code: "ANY", message: "should not be called" },
          { status: 200 },
        );
      }),
    );

    const req = makeRequest("refresh"); // no cookie
    const res = await refreshPost(req);

    expect(res.status).toBe(401);
    const body = await res.json();
    expect(body.code).toBe("AUTH_INVALID_TOKEN");
    expect(typeof body.message).toBe("string");
    expect(body.message.length).toBeGreaterThan(0);
    // No cookie ⇒ short-circuit, never touch the upstream.
    expect(upstreamCalled).toBe(false);

    // Cookie is cleared defensively (Max-Age=0).
    const setCookie = parseSetCookie(res.headers.get("set-cookie"));
    expect(setCookie).not.toBeNull();
    expect(setCookie!.name).toBe(COOKIE_NAME);
    expect(setCookie!.value).toBe("");
    expect(setCookie!.attrs["max-age"]).toBe("0");
  });

  it("upstream 4xx: responds 401 + clears cookie", async () => {
    server.use(
      http.post(`${API}/auth/refresh`, () =>
        HttpResponse.json(
          {
            code: "AUTH_INVALID_TOKEN",
            message: "Refresh token het han",
          },
          { status: 401 },
        ),
      ),
    );

    const req = makeRequest("refresh", {
      cookie: `${COOKIE_NAME}=refresh-stale`,
    });
    const res = await refreshPost(req);

    expect(res.status).toBe(401);
    const body = await res.json();
    expect(body.code).toBe("AUTH_INVALID_TOKEN");

    const setCookie = parseSetCookie(res.headers.get("set-cookie"));
    expect(setCookie).not.toBeNull();
    expect(setCookie!.name).toBe(COOKIE_NAME);
    expect(setCookie!.value).toBe("");
    expect(setCookie!.attrs["max-age"]).toBe("0");
  });
});

// ---------------------------------------------------------------------------
// Logout proxy
// ---------------------------------------------------------------------------

describe("POST /api/auth/logout", () => {
  it("with cookie + upstream 200: returns 200 and clears cookie", async () => {
    let upstreamCalled = false;
    server.use(
      http.post(`${API}/auth/logout`, () => {
        upstreamCalled = true;
        return HttpResponse.json({ message: "ok" });
      }),
    );

    const req = makeRequest("logout", {
      cookie: `${COOKIE_NAME}=refresh-current`,
    });
    const res = await logoutPost(req);

    expect(res.status).toBe(200);
    expect(upstreamCalled).toBe(true);

    const setCookie = parseSetCookie(res.headers.get("set-cookie"));
    expect(setCookie).not.toBeNull();
    expect(setCookie!.name).toBe(COOKIE_NAME);
    expect(setCookie!.value).toBe("");
    expect(setCookie!.attrs["max-age"]).toBe("0");
  });

  it("with cookie + upstream 500: still returns 200 + clears cookie (best-effort)", async () => {
    server.use(
      http.post(`${API}/auth/logout`, () =>
        HttpResponse.json(
          { code: "INTERNAL_SERVER_ERROR", message: "He thong dang ban" },
          { status: 500 },
        ),
      ),
    );

    const req = makeRequest("logout", {
      cookie: `${COOKIE_NAME}=refresh-current`,
    });
    const res = await logoutPost(req);

    expect(res.status).toBe(200);
    const body = await res.json();
    expect(typeof body.message).toBe("string");

    const setCookie = parseSetCookie(res.headers.get("set-cookie"));
    expect(setCookie).not.toBeNull();
    expect(setCookie!.value).toBe("");
    expect(setCookie!.attrs["max-age"]).toBe("0");
  });

  it("with cookie + upstream network failure: still returns 200 + clears cookie", async () => {
    server.use(
      http.post(`${API}/auth/logout`, () => HttpResponse.error()),
    );

    const req = makeRequest("logout", {
      cookie: `${COOKIE_NAME}=refresh-current`,
    });
    const res = await logoutPost(req);

    expect(res.status).toBe(200);
    const setCookie = parseSetCookie(res.headers.get("set-cookie"));
    expect(setCookie).not.toBeNull();
    expect(setCookie!.value).toBe("");
    expect(setCookie!.attrs["max-age"]).toBe("0");
  });

  it("without cookie: returns 200 + clears cookie without calling upstream", async () => {
    let upstreamCalled = false;
    server.use(
      http.post(`${API}/auth/logout`, () => {
        upstreamCalled = true;
        return HttpResponse.json({ message: "ok" });
      }),
    );

    const req = makeRequest("logout"); // no cookie
    const res = await logoutPost(req);

    expect(res.status).toBe(200);
    // No cookie ⇒ no upstream round-trip.
    expect(upstreamCalled).toBe(false);

    const setCookie = parseSetCookie(res.headers.get("set-cookie"));
    expect(setCookie).not.toBeNull();
    expect(setCookie!.value).toBe("");
    expect(setCookie!.attrs["max-age"]).toBe("0");
  });
});

// ---------------------------------------------------------------------------
// Cleanup
// ---------------------------------------------------------------------------

beforeEach(() => {
  // Each test registers its own MSW handlers via `server.use(...)`.
  // The global `afterEach` in `test/setup.ts` calls `server.resetHandlers()`
  // so the per-test overrides do not leak.
});

afterEach(() => {
  // No additional cleanup required — MSW reset is handled globally.
});
