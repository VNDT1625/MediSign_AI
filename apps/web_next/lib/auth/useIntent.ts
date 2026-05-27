"use client";

/**
 * `useIntent` — client hook for the post-authentication smart redirect.
 *
 * The intent describes "where the user actually wanted to go" before the
 * `LoginModal` interrupted them. It can be set from three places:
 *   1. Header CTAs / SiteHeader buttons (`set("home")`).
 *   2. HeroVideo question prefill (`set("chat", message)`).
 *   3. Edge middleware bouncing a protected `/app/...` URL via
 *      `?intent=<original_path>` query string.
 *
 * After a successful login flow the caller invokes `consume()` and
 * `router.push(result.redirectPath)`.
 *
 * Two backing stores are read, in this order of precedence:
 *   - URL query (`?intent=...&prefill=...`) — wins because middleware /
 *     deep-link redirects always carry the freshest intent.
 *   - `sessionStorage["medisign:intent"]` — survives the modal lifecycle
 *     and full page reloads inside the same tab.
 *
 * Both stores are cleared by `consume()` so a subsequent navigation can
 * never replay a stale intent (defence-in-depth against accidental loops
 * and second-tab leakage).
 *
 * Open-redirect defence is centralized in `lib/utils/intent.ts`: any value
 * that is not `"home"`, `"chat"`, or a path starting with `/app/` collapses
 * to the safe fallback `"chat"` — which `consume()` then maps to
 * `/app/chat`. See Requirements 2.1.4 and 3.1.
 *
 * SSR-safe: every `sessionStorage` / `window` access is guarded so the hook
 * may be referenced from server components that bail out before mount.
 */

import { useCallback } from "react";
import { useSearchParams } from "next/navigation";
import type { ReadonlyURLSearchParams } from "next/navigation";

import {
  decodeIntent,
  encodeIntent,
  type DecodedIntent,
  type Intent,
} from "../utils/intent";

/** Storage key for the cross-page intent payload. */
const STORAGE_KEY = "medisign:intent";

/** Default destination whenever the intent is missing or disallowed. */
const FALLBACK_REDIRECT = "/chat";

/** Query parameter names — kept in sync with `lib/utils/intent.ts`. */
const INTENT_PARAM = "intent";
const PREFILL_PARAM = "prefill";

export interface ConsumeResult {
  /** Path that the caller should pass to `router.push`. */
  redirectPath: string;
  /** Prefill payload to feed into the destination page (e.g. chat input). */
  prefilledMessage?: string;
}

export interface UseIntent {
  /**
   * Persist an intent + optional prefill message for replay after auth.
   * The value is normalized through `encodeIntent`, so disallowed inputs
   * are silently downgraded to the safe fallback before being stored.
   */
  set(intent: Intent | string, prefilledMessage?: string): void;
  /**
   * Read the current intent without consuming it. Returns `null` only
   * when neither the URL nor `sessionStorage` carries an intent value.
   */
  peek(): DecodedIntent | null;
  /**
   * Read the current intent, clear it from both stores, and return the
   * resolved `redirectPath`. Always returns a usable redirect — falls
   * back to `/app/chat` when no intent is present.
   */
  consume(): ConsumeResult;
}

/** Read the JSON-ish intent payload out of `sessionStorage`, SSR-safe. */
function readFromSessionStorage(): DecodedIntent | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY);
    if (raw === null) return null;
    // The payload is the same query-string format produced by
    // `encodeIntent`, which keeps the on-the-wire and on-disk shapes
    // identical and lets us reuse the same decoder for both sources.
    return decodeIntent(raw);
  } catch {
    // Private mode / disabled storage / quota — treat as absent.
    return null;
  }
}

function writeToSessionStorage(params: URLSearchParams): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.setItem(STORAGE_KEY, params.toString());
  } catch {
    // Silent: storage may be disabled (private browsing, quota exceeded).
  }
}

function clearSessionStorage(): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
}

/** Decode the URL-side intent only when the `intent` param is actually set. */
function readFromUrl(
  searchParams: ReadonlyURLSearchParams | null,
): DecodedIntent | null {
  if (!searchParams) return null;
  if (!searchParams.has(INTENT_PARAM)) return null;
  // `ReadonlyURLSearchParams` from `next/navigation` is API-compatible with
  // `URLSearchParams` for read access; serialize and re-parse so we hand
  // `decodeIntent` a value matching its declared input type exactly.
  return decodeIntent(searchParams.toString());
}

/**
 * Strip `intent` / `prefill` from the visible URL without triggering a
 * navigation. Other query params (e.g. `login=1`) are preserved.
 */
function clearUrlIntent(): void {
  if (typeof window === "undefined") return;
  try {
    const url = new URL(window.location.href);
    const hadIntent = url.searchParams.has(INTENT_PARAM);
    const hadPrefill = url.searchParams.has(PREFILL_PARAM);
    if (!hadIntent && !hadPrefill) return;
    url.searchParams.delete(INTENT_PARAM);
    url.searchParams.delete(PREFILL_PARAM);
    window.history.replaceState(window.history.state, "", url.toString());
  } catch {
    // ignore — URL or History may be unavailable in test environments.
  }
}

/**
 * Map a decoded intent to a concrete redirect path.
 *
 * Web hiện tại đã chuyển sang public route `/chat`, `/profile`. Các giá
 * trị intent legacy `/app/...` được normalise lại để không 404.
 *
 * - `"home"`            → `/chat`
 * - `"chat"`            → `/chat` (+ `?prefill=...` when present)
 * - `/app/chat...`      → `/chat...`
 * - `/app/profile...`   → `/profile...`
 * - `/app/...` khác     → `/`
 * - missing / invalid   → `/chat`
 */
function buildRedirectPath(decoded: DecodedIntent | null): ConsumeResult {
  if (!decoded) return { redirectPath: FALLBACK_REDIRECT };

  const { intent, prefilledMessage } = decoded;

  if (intent === "home") {
    return prefilledMessage !== undefined
      ? { redirectPath: "/chat", prefilledMessage }
      : { redirectPath: "/chat" };
  }

  if (intent === "chat") {
    if (prefilledMessage !== undefined) {
      const qs = new URLSearchParams();
      qs.set(PREFILL_PARAM, prefilledMessage);
      return {
        redirectPath: `/chat?${qs.toString()}`,
        prefilledMessage,
      };
    }
    return { redirectPath: "/chat" };
  }

  // `intent` là path `/app/...` từ decodeIntent — map về public route.
  let redirectPath: string;
  if (intent === "/app/chat" || intent.startsWith("/app/chat/")) {
    redirectPath = intent.replace(/^\/app\/chat/, "/chat");
  } else if (
    intent === "/app/profile" ||
    intent.startsWith("/app/profile/")
  ) {
    redirectPath = intent.replace(/^\/app\/profile/, "/profile");
  } else {
    redirectPath = "/";
  }

  return prefilledMessage !== undefined
    ? { redirectPath, prefilledMessage }
    : { redirectPath };
}

export function useIntent(): UseIntent {
  const searchParams = useSearchParams();

  const set = useCallback<UseIntent["set"]>((intent, prefilledMessage) => {
    // `encodeIntent` performs the open-redirect normalization for us, so
    // anything written to sessionStorage is already inside the allowlist.
    const params = encodeIntent(intent, prefilledMessage);
    writeToSessionStorage(params);
  }, []);

  const peek = useCallback<UseIntent["peek"]>(() => {
    return readFromUrl(searchParams) ?? readFromSessionStorage();
  }, [searchParams]);

  const consume = useCallback<UseIntent["consume"]>(() => {
    // Snapshot both sources before clearing, then resolve precedence.
    const fromUrl = readFromUrl(searchParams);
    const fromStorage = readFromSessionStorage();
    const decoded = fromUrl ?? fromStorage;

    clearSessionStorage();
    clearUrlIntent();

    return buildRedirectPath(decoded);
  }, [searchParams]);

  return { set, peek, consume };
}
