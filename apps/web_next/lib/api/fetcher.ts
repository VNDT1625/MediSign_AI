/**
 * `lib/api/fetcher.ts` — the single browser → backend HTTP entry point used
 * by every API module under `apps/web_next/lib/api/*`.
 *
 * Responsibilities (mirrors design.md "Fetcher" section):
 *   - Resolve relative paths against `NEXT_PUBLIC_API_BASE_URL`
 *     (default `http://localhost:8000/api/v1`); pass absolute URLs through
 *     unchanged.
 *   - Auto-serialize plain-object bodies as JSON and set
 *     `Content-Type: application/json` (callers can still pass `FormData`,
 *     `Blob`, etc. without interference).
 *   - Attach `Authorization: Bearer <token>` from the in-memory
 *     `tokenStore` whenever `authRequired !== false` (the default).
 *   - Enforce a 15s default timeout via `AbortController`; compose with the
 *     caller's `signal` so user-driven aborts still propagate.
 *   - Normalize every non-2xx response through `normalizeError` so the UI
 *     layer always sees an `ApiError` with `code` + `message` + `status`.
 *   - On 401 (and not `skipRefresh` and not already an
 *     `AUTH_SESSION_EXPIRED` error), wait on the shared `refreshOnce()`
 *     promise to swap in a new access token and retry the request exactly
 *     once. If the retry still 401s, the new error is thrown verbatim.
 *
 * The internal `refreshOnce()` scheduler is module-level and singleton:
 * concurrent 401s from any number of in-flight requests collapse onto one
 * `POST /api/auth/refresh` call (Property 3 — "Refresh single-flight
 * idempotence" in design.md). After the in-flight promise settles, the
 * holder is reset to `null` so a later 401 can trigger a fresh refresh.
 *
 * Failure modes the fetcher synthesizes (not from the backend body):
 *   - `NETWORK_ERROR`  status=0 — `fetch` threw `TypeError` (DNS, offline,
 *     CORS preflight failure, etc.).
 *   - `TIMEOUT_ERROR`  status=0 — our 15s timeout fired before the response
 *     headers arrived.
 *   - `AUTH_SESSION_EXPIRED` status=401 — refresh failed; tokens have been
 *     cleared and a best-effort `POST /api/auth/logout` has been sent.
 *
 * Note on environments: `/api/auth/refresh` is a same-origin Next.js Route
 * Handler proxy (created in task 6.2). In the browser, `fetch` would
 * resolve a leading `/` against `document.location.origin`. To keep the
 * fetcher portable across browser, jsdom, and bare-node test runners
 * (where undici rejects relative URLs because there is no realm origin),
 * `resolveUrl` always returns an absolute URL — same-origin paths are
 * resolved against `globalThis.location.origin` when available, with a
 * deterministic `http://localhost:3000` fallback that matches Next.js
 * dev defaults. MSW handlers register against the wildcard pattern
 * `* /api/auth/refresh` (without the inline space — written here with a
 * space so this JSDoc block does not terminate prematurely), so they
 * intercept regardless of which origin we synthesized.
 *
 * @see Requirements 2.1.6 (refresh + expiry), 2.4.1 (loading & error UX),
 *   3.1 (no localStorage for the access token), 3.2 (request-id surfacing).
 */

import { tokenStore } from "../auth/tokenStore";
import { ApiError, normalizeError } from "./errors";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

/** Fallback base URL used when `NEXT_PUBLIC_API_BASE_URL` is unset. */
const DEFAULT_API_BASE_URL = "http://localhost:8000/api/v1";
/** Same-origin Next.js Route Handler that bridges the refresh cookie. */
const REFRESH_PROXY_PATH = "/api/auth/refresh";
/** Same-origin Next.js Route Handler that clears the refresh cookie. */
const LOGOUT_PROXY_PATH = "/api/auth/logout";
/** Default per-request timeout — covers the slow-network P95 we target. */
const DEFAULT_TIMEOUT_MS = 15_000;

/** Sentinel code thrown when the refresh proxy itself rejects. */
const SESSION_EXPIRED_CODE = "AUTH_SESSION_EXPIRED";
/** vi-VN literal shown when the user must log in again. */
const SESSION_EXPIRED_MESSAGE = "Phiên đã hết hạn, vui lòng đăng nhập lại";

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

/**
 * Options accepted by `apiFetch`. Extends `RequestInit` so callers can use
 * any standard fetch option (`method`, `headers`, `cache`, …) plus a few
 * client-specific knobs.
 *
 * The `body` field is widened: callers may pass any `BodyInit` value
 * (string, FormData, Blob, ArrayBuffer view, URLSearchParams, ReadableStream)
 * which is forwarded untouched, OR a plain object / array which is
 * auto-serialized as JSON (with `Content-Type: application/json` set
 * automatically when the caller has not supplied one). `null` clears the
 * body entirely.
 */
export interface FetchOptions extends Omit<RequestInit, "body"> {
  /** Auto-JSON for plain objects/arrays; passthrough for `BodyInit` shapes. */
  body?: BodyInit | object | null;
  /** Attach `Authorization: Bearer <token>` when truthy (default `true`). */
  authRequired?: boolean;
  /**
   * When `true`, a 401 response is NOT translated into a refresh+retry. This
   * is required for the refresh proxy call itself (to avoid recursion) and
   * is convenient for tests that want to assert raw 401 envelopes.
   */
  skipRefresh?: boolean;
  /**
   * Abort signal supplied by the caller (e.g. React Query's). Composed with
   * the internal timeout signal: aborting either cancels the request.
   */
  signal?: AbortSignal;
  /** Override the default 15s timeout (milliseconds). */
  timeoutMs?: number;
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Read the API base URL at call time so test setups that mutate
 * `process.env` between tests are honoured. Trailing slashes are trimmed so
 * that `${base}${tail}` never produces `//`.
 */
function getApiBaseUrl(): string {
  // `process.env.NEXT_PUBLIC_*` is statically inlined by Next.js at build
  // time in the browser bundle, but at module-eval time in Node tests it
  // is a normal lookup — both modes work with this single expression.
  const raw =
    (typeof process !== "undefined" && process.env?.NEXT_PUBLIC_API_BASE_URL) ||
    DEFAULT_API_BASE_URL;
  return raw.replace(/\/+$/, "");
}

/**
 * Resolve the same-origin base used for Next.js Route Handler paths
 * (`/api/auth/...`). In a browser or jsdom realm, `globalThis.location`
 * exposes the page origin and we honour it. In a bare-node Vitest run
 * there is no `location`, so we fall back to `http://localhost:3000`
 * (the Next.js dev default). MSW's `* /api/auth/...` wildcard pattern
 * (without the inline space — written here with a space so this JSDoc
 * block does not terminate prematurely) matches either origin
 * identically, and production traffic always has a real
 * `location.origin` — so this fallback is test-only in practice.
 */
function getSameOriginBase(): string {
  const loc = (globalThis as { location?: { origin?: string } }).location;
  if (loc && typeof loc.origin === "string" && loc.origin.length > 0) {
    return loc.origin;
  }
  return "http://localhost:3000";
}

/**
 * Resolve a path against the configured API base URL.
 *
 * Routing rules (in order):
 *   1. Absolute URLs (`http://…` / `https://…`) pass through untouched —
 *      callers occasionally construct full URLs for external services or
 *      preview environments.
 *   2. **Same-origin Next.js Route Handlers**: only the `/api/auth/...`
 *      family is mounted in `apps/web_next/app/api/auth/[action]/route.ts`
 *      (login / refresh / logout — see Auth Subsystem in design.md).
 *      Those paths must NOT be prefixed with the FastAPI base URL,
 *      otherwise the request would skip the cookie bridge entirely.
 *      We resolve them against `globalThis.location.origin` (with a
 *      deterministic localhost fallback) so the URL passed to `fetch`
 *      is always absolute — undici (Node 18+) rejects relative URLs
 *      when no realm origin is available.
 *   3. Everything else — including `/api/drug/...` (which belongs to
 *      FastAPI's drug router, mounted at `/api/v1/api/drug/...`),
 *      `/auth/me`, `/consult/triage`, `/medicine/scan`, etc. — is
 *      treated as a backend path and resolved against
 *      `NEXT_PUBLIC_API_BASE_URL`.
 *
 * The narrow `/api/auth/` allow-list (instead of a broader `/api/` one)
 * is deliberate: the only Next.js Route Handlers in this app are auth
 * proxies, and we want a backend route that happens to live under
 * `/api/...` (like the drug catalog) to reach the backend, not be
 * intercepted as same-origin.
 */
function resolveUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) return path;
  // Same-origin Next.js Route Handlers (auth proxies only).
  if (path.startsWith("/api/auth/") || path === "/api/auth") {
    return `${getSameOriginBase()}${path}`;
  }
  const tail = path.startsWith("/") ? path : `/${path}`;
  return `${getApiBaseUrl()}${tail}`;
}

/**
 * Detect bodies that should be serialized as JSON. We forward any
 * `BodyInit`-compatible value (string, FormData, Blob, ArrayBuffer view,
 * URLSearchParams, ReadableStream) untouched and JSON-stringify everything
 * else (typically plain objects / arrays from API modules).
 */
function isPlainJsonBody(body: unknown): boolean {
  if (body === undefined || body === null) return false;
  if (typeof body !== "object") return false;
  if (typeof FormData !== "undefined" && body instanceof FormData) return false;
  if (typeof Blob !== "undefined" && body instanceof Blob) return false;
  if (typeof ArrayBuffer !== "undefined" && body instanceof ArrayBuffer) return false;
  if (typeof ArrayBuffer !== "undefined" && ArrayBuffer.isView(body as ArrayBufferView)) {
    return false;
  }
  if (typeof URLSearchParams !== "undefined" && body instanceof URLSearchParams) {
    return false;
  }
  if (typeof ReadableStream !== "undefined" && body instanceof ReadableStream) {
    return false;
  }
  return true;
}

/**
 * Build the outgoing `Headers` object: clone caller headers, add the JSON
 * `Content-Type` when we serialized the body, and attach the bearer token
 * when authentication is required and a token is available.
 */
function buildHeaders(args: {
  callerHeaders: HeadersInit | undefined;
  hasJsonBody: boolean;
  requireAuth: boolean;
  bearerOverride?: string | null;
}): Headers {
  const headers = new Headers(args.callerHeaders);
  if (args.hasJsonBody && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (args.requireAuth) {
    const token =
      args.bearerOverride !== undefined ? args.bearerOverride : tokenStore.get();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }
  return headers;
}

/**
 * Wrap an outgoing fetch with the timeout `AbortController` and forward
 * caller-supplied aborts. Returns the composed signal plus a `cleanup`
 * function that must always run (in both success and failure paths) to
 * clear the timer and release the listener.
 */
function composeSignal(
  timeoutMs: number,
  userSignal?: AbortSignal,
): { signal: AbortSignal; isTimedOut: () => boolean; cleanup: () => void } {
  const controller = new AbortController();
  let timedOut = false;

  const timer = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, timeoutMs);

  let onUserAbort: (() => void) | null = null;
  if (userSignal) {
    if (userSignal.aborted) {
      controller.abort();
    } else {
      onUserAbort = () => controller.abort();
      userSignal.addEventListener("abort", onUserAbort, { once: true });
    }
  }

  return {
    signal: controller.signal,
    isTimedOut: () => timedOut,
    cleanup: () => {
      clearTimeout(timer);
      if (userSignal && onUserAbort) {
        userSignal.removeEventListener("abort", onUserAbort);
      }
    },
  };
}

/**
 * Decode a non-2xx response body. Tries JSON first (the FastAPI envelope
 * `ApiErrorBody` is JSON), falls back to text for HTML / plain-text errors
 * from upstream proxies. Always returns; never throws.
 */
async function readErrorBody(response: Response): Promise<unknown> {
  try {
    // Clone so callers can re-read if needed; cheap on small error bodies.
    return await response.clone().json();
  } catch {
    try {
      return await response.text();
    } catch {
      return undefined;
    }
  }
}

/**
 * Decode a 2xx response body as JSON. Empty bodies (`204 No Content`, or a
 * 200 with no payload) resolve to `null` cast to `T` — callers that don't
 * expect a payload typically declare `T = void`.
 */
async function readSuccessBody<T>(response: Response): Promise<T> {
  if (response.status === 204) return null as T;
  const text = await response.text();
  if (text.length === 0) return null as T;
  try {
    return JSON.parse(text) as T;
  } catch {
    // Non-JSON 2xx responses are unusual but harmless — surface as-is so
    // callers expecting `string` (e.g. plain-text health checks) work.
    return text as unknown as T;
  }
}

/**
 * Execute a single `fetch` with the composed signal, translating low-level
 * failures (timeout, network error) into the synthesized `ApiError` codes
 * the UI layer expects.
 */
async function executeFetch(
  url: string,
  init: RequestInit,
  timeoutMs: number,
  userSignal?: AbortSignal,
): Promise<Response> {
  const composed = composeSignal(timeoutMs, userSignal);
  try {
    return await fetch(url, { ...init, signal: composed.signal });
  } catch (err) {
    // Our timeout fired before the network responded.
    if (composed.isTimedOut()) {
      throw new ApiError({
        code: "TIMEOUT_ERROR",
        status: 0,
        message: "Yêu cầu hết thời gian chờ.",
      });
    }
    // Caller aborted on purpose — propagate the original AbortError so
    // React Query / caller code can detect it via `signal.aborted`.
    if (userSignal?.aborted) throw err;
    // `fetch` throws `TypeError` for network-layer failures (DNS, offline,
    // CORS preflight, etc.). These have no HTTP status.
    if (err instanceof TypeError) {
      throw new ApiError({
        code: "NETWORK_ERROR",
        status: 0,
        message: "Mất kết nối. Kiểm tra mạng và thử lại.",
      });
    }
    throw err;
  } finally {
    composed.cleanup();
  }
}

// ---------------------------------------------------------------------------
// Single-flight refresh scheduler
// ---------------------------------------------------------------------------

/**
 * Module-level holder for the in-flight refresh promise. `null` means "no
 * refresh in progress" — the next 401 will trigger a new one. While set,
 * concurrent callers `await` the same promise, satisfying Property 3
 * (single-flight idempotence): n concurrent 401s → exactly one
 * `POST /api/auth/refresh` call.
 */
let _refreshPromise: Promise<string> | null = null;

/**
 * Body returned by the Next.js refresh proxy after rotating the cookie.
 * Refresh tokens never reach JS — they live in the `medisign_rt` httpOnly
 * cookie, which is set by the proxy and sent back to it automatically.
 */
interface RefreshProxyResponse {
  access_token: string;
  expires_in: number;
}

/**
 * Begin (or join) a refresh round-trip. Resolves with the new access token,
 * which is also written into `tokenStore`. On any failure the store is
 * cleared, a best-effort `POST /api/auth/logout` is fired, and an
 * `ApiError("AUTH_SESSION_EXPIRED", 401)` is thrown — the sentinel UI code
 * uses to redirect the user to `/?session=expired`.
 *
 * Exported for the property test (task 4.6) which exercises the
 * single-flight behaviour with concurrent callers.
 */
export function refreshOnce(): Promise<string> {
  if (_refreshPromise) return _refreshPromise;

  _refreshPromise = (async () => {
    let response: Response;
    try {
      response = await executeFetch(
        resolveUrl(REFRESH_PROXY_PATH),
        { method: "POST" },
        DEFAULT_TIMEOUT_MS,
      );
    } catch (err) {
      // Network/timeout failures bubble up as ApiError already. Treat them
      // as a refresh failure so the user is forced to re-authenticate.
      throw await failRefresh(err);
    }

    if (!response.ok) {
      const body = await readErrorBody(response);
      throw await failRefresh(normalizeError(response, body));
    }

    const body = (await readSuccessBody<RefreshProxyResponse>(response)) as
      | RefreshProxyResponse
      | null;

    if (!body || typeof body.access_token !== "string" || body.access_token.length === 0) {
      throw await failRefresh(
        new ApiError({
          code: SESSION_EXPIRED_CODE,
          status: 401,
          message: SESSION_EXPIRED_MESSAGE,
        }),
      );
    }

    const expiresIn =
      typeof body.expires_in === "number" && body.expires_in > 0
        ? body.expires_in
        : 0;
    tokenStore.set(body.access_token, expiresIn);
    return body.access_token;
  })();

  // Reset the holder once the promise settles (success OR failure) so the
  // next 401 can start a fresh refresh round-trip. We do NOT swallow the
  // rejection — `_refreshPromise` is the same reference returned to all
  // concurrent callers, and they each `await` it for the rejection.
  //
  // IMPORTANT: `.finally()` returns a NEW derived promise that also rejects
  // when the parent rejects. That derived promise is not returned to any
  // caller, so it would become an unhandled rejection and trigger the
  // Next.js dev overlay (and crash the app in production). We attach a
  // no-op `.catch()` to silence it — the actual rejection is still
  // propagated through `_refreshPromise` which every caller awaits.
  _refreshPromise.finally(() => {
    _refreshPromise = null;
  }).catch(() => {
    // Intentionally empty: the rejection is already handled by every
    // caller that awaits `_refreshPromise` directly. This .catch() only
    // exists to prevent the derived `.finally()` promise from becoming
    // an unhandled rejection.
  });

  return _refreshPromise;
}

/**
 * Handle the refresh-failed path: clear the in-memory token, fire-and-forget
 * the logout proxy (so the cookie is cleared even if the user navigates
 * away), and return the canonical `AUTH_SESSION_EXPIRED` error to throw.
 *
 * Accepts the original failure cause for diagnostic chaining. The returned
 * `ApiError` always wins — we never propagate the underlying cause to the
 * UI, since the user-visible action is always "log in again".
 */
async function failRefresh(_cause: unknown): Promise<ApiError> {
  tokenStore.clear();
  // Best-effort logout: a network failure here is fine, the cookie will
  // be re-cleared on the next refresh attempt. We deliberately swallow.
  // Use `resolveUrl` so the same-origin proxy works in node test runners
  // that lack a realm origin (matches the `refreshOnce` codepath above).
  try {
    await fetch(resolveUrl(LOGOUT_PROXY_PATH), {
      method: "POST",
      credentials: "same-origin",
    });
  } catch {
    // ignore
  }
  return new ApiError({
    code: SESSION_EXPIRED_CODE,
    status: 401,
    message: SESSION_EXPIRED_MESSAGE,
  });
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Make a typed HTTP request to the MediSign backend (or one of the Next.js
 * auth proxies). Returns the parsed JSON body cast to `T` on 2xx, throws an
 * `ApiError` on every other outcome.
 *
 * @example
 *   const me = await apiFetch<AuthUserResponse>("/auth/me");
 *
 *   await apiFetch("/auth/change-password", {
 *     method: "POST",
 *     body: { current_password, new_password },
 *   });
 *
 *   // Skip the bearer header for public endpoints:
 *   await apiFetch("/consult/triage", {
 *     method: "POST",
 *     body: { symptom_text, locale: "vi-VN" },
 *     authRequired: false,
 *   });
 */
export async function apiFetch<T>(
  path: string,
  opts: FetchOptions = {},
): Promise<T> {
  const {
    authRequired = true,
    skipRefresh = false,
    signal: userSignal,
    timeoutMs = DEFAULT_TIMEOUT_MS,
    body: rawBody,
    headers: callerHeaders,
    ...rest
  } = opts;

  const url = resolveUrl(path);

  const hasJsonBody = isPlainJsonBody(rawBody);
  const requestBody: BodyInit | null | undefined = hasJsonBody
    ? JSON.stringify(rawBody)
    : (rawBody as BodyInit | null | undefined);

  const headers = buildHeaders({
    callerHeaders,
    hasJsonBody,
    requireAuth: authRequired,
  });

  const init: RequestInit = {
    ...rest,
    headers,
    body: requestBody,
  };

  const response = await executeFetch(url, init, timeoutMs, userSignal);

  if (response.ok) {
    return readSuccessBody<T>(response);
  }

  const errorBody = await readErrorBody(response);
  const apiError = normalizeError(response, errorBody);

  // Single-flight refresh on 401 unless the caller opted out, or the error
  // is already the terminal AUTH_SESSION_EXPIRED (which we never retry).
  if (
    response.status === 401 &&
    authRequired &&
    !skipRefresh &&
    apiError.code !== SESSION_EXPIRED_CODE
  ) {
    // `refreshOnce` either resolves with a new bearer or throws
    // AUTH_SESSION_EXPIRED — we let that throw propagate untouched.
    const newToken = await refreshOnce();

    const retryHeaders = buildHeaders({
      callerHeaders,
      hasJsonBody,
      requireAuth: true,
      bearerOverride: newToken,
    });

    const retryInit: RequestInit = {
      ...rest,
      headers: retryHeaders,
      body: requestBody,
    };

    const retryResponse = await executeFetch(url, retryInit, timeoutMs, userSignal);
    if (retryResponse.ok) {
      return readSuccessBody<T>(retryResponse);
    }

    // Retry still came back 401 → the new access token was already invalid
    // (token revoked server-side, account disabled, etc.). Treat the same
    // as a refresh failure: clear the session, best-effort logout, and
    // surface the canonical AUTH_SESSION_EXPIRED so the UI redirects to
    // `/?session=expired`.
    if (retryResponse.status === 401) {
      const retryErrorBody = await readErrorBody(retryResponse);
      throw await failRefresh(normalizeError(retryResponse, retryErrorBody));
    }

    const retryErrorBody = await readErrorBody(retryResponse);
    throw normalizeError(retryResponse, retryErrorBody);
  }

  throw apiError;
}

// ---------------------------------------------------------------------------
// Test-only escape hatch
// ---------------------------------------------------------------------------

/**
 * Reset the single-flight refresh holder. Tests use this between cases to
 * isolate scheduler state; production code never calls it.
 *
 * @internal
 */
export function __resetRefreshForTests(): void {
  _refreshPromise = null;
}
