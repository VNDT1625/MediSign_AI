/**
 * Error normalization for the FastAPI backend envelope.
 *
 * The backend's exception handlers in `apps/backend_fastapi/app/main.py`
 * (`validation_exception_handler`, `http_exception_handler`,
 * `unhandled_exception_handler`) always emit a JSON body shaped like
 * `ApiErrorBody` from `@medisign/shared-contracts`:
 *
 *     { code, message, details?, request_id? }
 *
 * Real-world responses can deviate from that contract: the body may be
 * empty (e.g. some 5xx pages, network proxies), it may be HTML, the JSON
 * may be valid but missing `code`/`message`, or the parser upstream may
 * have failed before we got here. `normalizeError` collapses all of those
 * cases into a single `ApiError` instance the UI layer can display
 * uniformly.
 *
 * Contract (Property 4 in design — "Error normalization preserves shape"):
 *   - Returns an `ApiError` with `code`, `message`, and `status` always
 *     present, non-empty (for the strings) and numeric (for the status).
 *   - On a parseable `ApiErrorBody` (both `code` and `message` are
 *     non-empty strings), those fields are forwarded verbatim along with
 *     `details`.
 *   - Otherwise, `code` collapses to `"UNKNOWN_ERROR"` and `message`
 *     falls back to `response.statusText` (when non-empty) or the
 *     vi-VN literal `"Yêu cầu thất bại"`.
 *   - The `x-request-id` response header is preserved on `requestId`
 *     whenever the header is present and non-empty. When the header is
 *     missing, the body's `request_id` field (if any) is used as a
 *     secondary fallback so existing correlation ids survive proxies
 *     that strip the header.
 *   - Never throws.
 *
 * @see Requirements 2.4.1 (loading & error UX), 3.2 (observability via
 *   `x-request-id`).
 * @see Design — "Error Handling" section in
 *   `.kiro/specs/web-app-functional-integration/design.md`.
 */

import type { ApiErrorBody } from "@medisign/shared-contracts";

/** Sentinel code used when the backend body is missing or unparseable. */
const UNKNOWN_CODE = "UNKNOWN_ERROR";
/** vi-VN literal used as the last-resort error message. Keep non-empty. */
const FALLBACK_MESSAGE = "Yêu cầu thất bại";
/** Correlation id header emitted by FastAPI middleware. */
const REQUEST_ID_HEADER = "x-request-id";

/** Shape of `ApiError` constructor input. Mirrors the public fields. */
export interface ApiErrorOptions {
  code: string;
  message: string;
  status: number;
  requestId?: string;
  details?: ApiErrorBody["details"];
}

/**
 * Normalized client-side error raised for any non-2xx response (or
 * synthesized for network/timeout failures by the fetcher in
 * `lib/api/fetcher.ts`).
 *
 * `Error.message` mirrors `message` so existing error-display utilities
 * that read `err.message` keep working unchanged. The remaining fields
 * are exposed as readonly own properties.
 */
export class ApiError extends Error {
  /** Machine-readable code (e.g. `"AUTH_INVALID_TOKEN"`). Always non-empty. */
  readonly code: string;
  /** HTTP status code at the time the error was produced. */
  readonly status: number;
  /** Optional `x-request-id` correlation id for support diagnostics. */
  readonly requestId?: string;
  /** Optional structured details (mirrors `ApiErrorBody.details`). */
  readonly details?: ApiErrorBody["details"];

  constructor(options: ApiErrorOptions) {
    super(options.message);
    this.name = "ApiError";
    this.code = options.code;
    this.status = options.status;
    if (options.requestId !== undefined) {
      this.requestId = options.requestId;
    }
    if (options.details !== undefined) {
      this.details = options.details;
    }
    // Restore the prototype chain when transpiled to ES5-style targets
    // (without this, `instanceof ApiError` can fail across realms).
    Object.setPrototypeOf(this, ApiError.prototype);
  }
}

/** Type guard: true only for non-empty strings (rejects `""`, non-strings). */
function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.length > 0;
}

/**
 * Returns the body cast to `ApiErrorBody` when both `code` and `message`
 * are present as non-empty strings, otherwise `null`. We intentionally do
 * NOT validate `details` / `request_id` here — they are best-effort and
 * propagated as-is when present.
 */
function parseErrorBody(body: unknown): ApiErrorBody | null {
  if (body === null || typeof body !== "object") return null;
  const candidate = body as Record<string, unknown>;
  if (!isNonEmptyString(candidate.code)) return null;
  if (!isNonEmptyString(candidate.message)) return null;
  return candidate as unknown as ApiErrorBody;
}

/**
 * Safely read the `x-request-id` header. Defends against host objects
 * that lack a `get` method (some test doubles, malformed `Headers`-like
 * shims) by returning `null` on any throw.
 */
function readRequestIdHeader(headers: Headers | undefined | null): string | null {
  if (!headers || typeof headers.get !== "function") return null;
  try {
    return headers.get(REQUEST_ID_HEADER);
  } catch {
    return null;
  }
}

/**
 * Convert a backend response (with optionally pre-parsed body and
 * pre-extracted headers) into a stable `ApiError` instance.
 *
 * The fetcher in `lib/api/fetcher.ts` is responsible for awaiting
 * `response.json()` (or `response.text()`) before calling this, since
 * `Response` body consumption is async. Both `body` and `headers` are
 * optional so callers that only have the raw `Response` can still get a
 * usable error envelope (headers default to `response.headers`, body
 * defaults to "missing").
 *
 * Never throws. Always returns an `ApiError` with `code`, `message`, and
 * `status` defined.
 */
export function normalizeError(
  response: Response,
  body?: unknown,
  headers?: Headers,
): ApiError {
  const effectiveHeaders = headers ?? response.headers;
  const headerRequestId = readRequestIdHeader(effectiveHeaders);
  const status = typeof response.status === "number" ? response.status : 0;

  const parsed = parseErrorBody(body);

  if (parsed) {
    // Header takes precedence over body for correlation id (the header
    // is the canonical FastAPI source); the body's `request_id` is only
    // used when proxies strip the header on the way back to the client.
    const requestId = isNonEmptyString(headerRequestId)
      ? headerRequestId
      : isNonEmptyString(parsed.request_id)
        ? parsed.request_id
        : undefined;

    const options: ApiErrorOptions = {
      code: parsed.code,
      message: parsed.message,
      status,
    };
    if (requestId !== undefined) options.requestId = requestId;
    if (parsed.details !== undefined && parsed.details !== null) {
      options.details = parsed.details;
    }
    return new ApiError(options);
  }

  // Fallback path: body is missing, malformed, or doesn't conform to
  // `ApiErrorBody`. Build a guaranteed-valid envelope so the UI never
  // has to deal with empty `code`/`message`.
  const fallbackMessage = isNonEmptyString(response.statusText)
    ? response.statusText
    : FALLBACK_MESSAGE;

  const options: ApiErrorOptions = {
    code: UNKNOWN_CODE,
    message: fallbackMessage,
    status,
  };
  if (isNonEmptyString(headerRequestId)) {
    options.requestId = headerRequestId;
  }
  return new ApiError(options);
}
