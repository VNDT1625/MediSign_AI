/**
 * In-memory access token store.
 *
 * Holds the current short-lived access token and its absolute expiry instant
 * (ms since epoch). Refresh tokens are intentionally NOT stored here — they
 * live in the `medisign_rt` httpOnly cookie set by the Next.js Route Handler
 * proxy. The access token is kept in memory (not localStorage/sessionStorage)
 * to reduce the XSS attack surface; each browser tab has its own instance and
 * bootstraps via `/api/auth/refresh` when needed.
 *
 * Behaviour:
 * - `get()` returns the current access token, or `null` before any `set()`
 *   call (or after `clear()`).
 * - `set(t, expiresInSec)` records the token and pre-computes an absolute
 *   expiry instant. A 30-second safety margin is subtracted so callers refresh
 *   slightly before the backend-side TTL elapses, avoiding clock-skew 401s.
 * - `isExpired()` is true whenever the current time has reached or passed the
 *   recorded expiry. With the default expiry of `0`, this returns `true` until
 *   the first `set()` call — matching the expected "no usable token yet"
 *   behaviour for unauthenticated tabs.
 * - `clear()` resets both the token and the expiry, putting the store back
 *   into the unauthenticated state.
 *
 * The store is a module-level singleton: importing this module multiple times
 * yields the same `tokenStore` reference (per JS realm/tab).
 *
 * @see Design — "State (client)" section in
 *   `.kiro/specs/web-app-functional-integration/design.md`
 * @see Requirements 2.1.6 (refresh + expiry handling), 3.1 (no localStorage
 *   for the access token).
 */

/** Safety margin (in seconds) subtracted from the backend-reported TTL so that
 *  the client refreshes slightly before the real expiry. */
const EXPIRY_SAFETY_SECONDS = 30;

/** Browser custom event fired whenever the access token changes (set/clear).
 *
 *  Listeners (e.g. CabinetTab's sync banner) subscribe via
 *    `window.addEventListener("medisign:token-changed", handler)`.
 *  No detail is included on purpose — listeners must read the current state
 *  via `tokenStore.get()` to avoid stale-data bugs. */
const TOKEN_CHANGED_EVENT = "medisign:token-changed";

function emitTokenChanged(): void {
  // Guard against SSR (no `window`) and very old browsers without
  // `CustomEvent`. Listeners are best-effort and never block the store.
  if (typeof window === "undefined" || typeof CustomEvent === "undefined") {
    return;
  }
  try {
    window.dispatchEvent(new CustomEvent(TOKEN_CHANGED_EVENT));
  } catch {
    // ignore — synthetic event dispatch failures are non-fatal.
  }
}

let _accessToken: string | null = null;
/** Absolute expiry instant in ms since epoch. `0` means "no token" / expired. */
let _expiresAt = 0;

export interface TokenStore {
  /** Current access token, or `null` when unauthenticated. */
  get(): string | null;
  /**
   * Record a freshly issued access token along with its TTL in seconds.
   *
   * The recorded expiry is `Date.now() + (expiresInSec - 30) * 1000`. Callers
   * should pass the raw `expires_in` value returned by the backend; the 30s
   * safety margin is applied here so callers do not need to remember it.
   */
  set(t: string, expiresInSec: number): void;
  /** `true` whenever the wall-clock time has reached the recorded expiry. */
  isExpired(): boolean;
  /** Reset to the unauthenticated state. */
  clear(): void;
}

export const tokenStore: TokenStore = {
  get: () => _accessToken,
  set: (t: string, expiresInSec: number) => {
    _accessToken = t;
    _expiresAt = Date.now() + (expiresInSec - EXPIRY_SAFETY_SECONDS) * 1000;
    emitTokenChanged();
  },
  isExpired: () => Date.now() >= _expiresAt,
  clear: () => {
    _accessToken = null;
    _expiresAt = 0;
    emitTokenChanged();
  },
};
