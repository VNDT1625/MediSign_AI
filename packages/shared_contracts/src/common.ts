// @medisign/shared-contracts/common
//
// Generic envelopes and primitives shared across all API modules.
// Maps 1-1 to apps/backend_fastapi/app/schemas/common.py (`ErrorResponse`).
//
// Backend exception handlers in apps/backend_fastapi/app/main.py
// (`validation_exception_handler`, `http_exception_handler`,
// `unhandled_exception_handler`) always emit this envelope on 4xx/5xx.

/**
 * Standard error envelope returned by the FastAPI backend on any non-2xx
 * response. Field names match the Pydantic `ErrorResponse` model verbatim
 * (snake_case on the wire) so the web client can decode with no remapping.
 */
export interface ApiErrorBody {
  /** Machine-readable error code, e.g. `AUTH_INVALID_TOKEN`, `VALIDATION_ERROR`. */
  code: string;
  /** Human-readable message, already localized (vi-VN) by the backend. */
  message: string;
  /**
   * Optional structured details. For `VALIDATION_ERROR` this is typically
   * `{ errors: [...] }` mirroring Pydantic validation error entries.
   */
  details?: { errors?: unknown[] } | Record<string, unknown> | null;
  /**
   * Correlation id propagated from the `x-request-id` response header. Used
   * by the client to surface a support reference in error toasts.
   */
  request_id?: string | null;
}
