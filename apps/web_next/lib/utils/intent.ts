/**
 * Intent codec for smart redirects after authentication.
 *
 * The intent value is captured before the user authenticates (e.g. when a
 * gated CTA opens the LoginModal) and replayed after login to send the user
 * to the right place. To prevent open redirects, only an explicit allowlist
 * of values is honored; anything else collapses to the safe fallback
 * `"chat"` — see Requirements 2.1.4, 2.2.1, and the open-redirect defense
 * in 3.1.
 *
 * Allowed intents:
 *   - `"home"`            — shorthand for `/app`
 *   - `"chat"`            — shorthand for `/app/chat` (also the fallback)
 *   - `"/app/<anything>"` — absolute path inside the protected app shell
 *
 * Anything else (external URL, protocol-relative URL like `//evil.com`,
 * `"/"`, `"/login"`, arbitrary string, `null`/`undefined`, non-string)
 * is rejected and collapsed to the fallback intent `"chat"`.
 *
 * Both functions are pure: no DOM access, no `window`, no side effects.
 * They MUST NEVER throw — every failure mode collapses to a safe value.
 *
 * Round-trip property (validated by `intent.property.test.ts`):
 *   For any allowed intent `i` and any string `p`,
 *   `decodeIntent(encodeIntent(i, p))` returns `{ intent: i, prefilledMessage: p }`.
 */

/** The narrow set of values that survive open-redirect defense. */
export type Intent = "home" | "chat" | `/app/${string}`;

/** Decoded representation of intent + optional prefill payload. */
export interface DecodedIntent {
  intent: Intent;
  prefilledMessage?: string;
}

const FALLBACK_INTENT: Intent = "chat";
const APP_PATH_PREFIX = "/app/";
const INTENT_PARAM = "intent";
const PREFILL_PARAM = "prefill";

/**
 * Returns true only for values in the explicit allowlist. The allowlist is
 * the single source of truth for the open-redirect defense; anything not
 * in this set collapses to the fallback intent.
 */
function isAllowedIntent(value: unknown): value is Intent {
  if (typeof value !== "string") return false;
  if (value === "home" || value === "chat") return true;
  // Absolute path inside the protected app shell. The leading `/app/`
  // requirement excludes `/`, `/app`, `/login`, `//evil.com`, `http://...`,
  // and any other off-shell destination.
  return value.startsWith(APP_PATH_PREFIX);
}

/**
 * Coerce any input to a safe `Intent`. Inputs failing the allowlist
 * (including `null`, `undefined`, numbers, objects, or external URLs)
 * collapse to the fallback `"chat"`.
 */
function normalizeIntent(value: unknown): Intent {
  return isAllowedIntent(value) ? value : FALLBACK_INTENT;
}

/**
 * Encode an intent (and optional prefill message) as `URLSearchParams`.
 *
 * The result can be appended to any URL with `url.search = params.toString()`
 * or passed straight back to `decodeIntent`. Special characters (unicode,
 * `?`, `&`, `=`, `+`, spaces, etc.) are URL-encoded by `URLSearchParams`
 * and round-trip cleanly through `decodeIntent`.
 *
 * Always returns a fresh `URLSearchParams`. Never throws — invalid intents
 * silently collapse to the fallback.
 */
export function encodeIntent(
  intent: Intent | string | null | undefined,
  prefilledMessage?: string,
): URLSearchParams {
  const params = new URLSearchParams();
  try {
    params.set(INTENT_PARAM, normalizeIntent(intent));
    // Distinguish "no prefill provided" (undefined) from "prefill is empty
    // string" (""). The former omits the param; the latter sets it to "".
    if (typeof prefilledMessage === "string") {
      params.set(PREFILL_PARAM, prefilledMessage);
    }
    return params;
  } catch {
    // `URLSearchParams.set` is spec-defined to never throw for string args,
    // but defend against unusual host environments / monkey-patching.
    const safe = new URLSearchParams();
    safe.set(INTENT_PARAM, FALLBACK_INTENT);
    return safe;
  }
}

/**
 * Decode intent + prefill from `URLSearchParams`, a query string (with or
 * without leading `"?"`), or `null`/`undefined`.
 *
 * Always returns a `DecodedIntent`. Missing or disallowed intents collapse
 * to the fallback `"chat"`. `prefilledMessage` is included only when the
 * `prefill` parameter is present (preserved as-is, including empty string).
 *
 * Never throws — malformed inputs collapse to `{ intent: "chat" }`.
 */
export function decodeIntent(
  searchParams: URLSearchParams | string | null | undefined,
): DecodedIntent {
  let params: URLSearchParams;
  try {
    if (searchParams instanceof URLSearchParams) {
      params = searchParams;
    } else if (typeof searchParams === "string") {
      // Allow callers to pass `location.search` directly (which includes
      // the leading "?") or a bare query string.
      const raw = searchParams.startsWith("?")
        ? searchParams.slice(1)
        : searchParams;
      params = new URLSearchParams(raw);
    } else {
      return { intent: FALLBACK_INTENT };
    }
  } catch {
    return { intent: FALLBACK_INTENT };
  }

  const rawIntent = params.get(INTENT_PARAM);
  const intent = normalizeIntent(rawIntent);

  const rawPrefill = params.get(PREFILL_PARAM);
  if (rawPrefill === null) {
    return { intent };
  }
  return { intent, prefilledMessage: rawPrefill };
}
