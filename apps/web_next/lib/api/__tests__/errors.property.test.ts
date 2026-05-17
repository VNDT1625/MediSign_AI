// Feature: web-app-functional-integration, Property 4: Error normalization preserves shape
/**
 * Property tests for `lib/api/errors.ts` — `normalizeError` shape preservation.
 *
 * Feature: web-app-functional-integration, Property 4: Error normalization preserves shape
 *
 * Validates: Requirements 2.4.1 (loading & error UX), 3.2 (observability
 * via `x-request-id`).
 *
 * Universal claim under test:
 *   For any backend `Response` — with any status code in `[0, 600]`, any
 *   `statusText`, any optional `x-request-id` header (absent / empty /
 *   present), and any body shape (including malformed bodies, partial
 *   `ApiErrorBody` shapes, non-objects, `null`, and `undefined`) —
 *   `normalizeError(response, body)` SHALL return an `ApiError` with:
 *     • `code`:      non-empty string
 *     • `message`:   non-empty string
 *     • `status`:    finite number, equal to `response.status`
 *     • `requestId`: equal to the `x-request-id` header value whenever
 *                    that header is present and non-empty after WHATWG
 *                    header-value normalization (leading/trailing
 *                    whitespace is stripped before storage)
 *   And `normalizeError` SHALL never throw.
 *
 * Note on status range: WHATWG Fetch (enforced by jsdom and the Node 18+
 * `undici` runtime) restricts the `Response` constructor to status codes
 * in [200, 599]. The design's spec input space is [0, 600] but those
 * values cannot be realized through a real `Response`, so we sample the
 * constructible range and assert `normalizeError` echoes whatever
 * `response.status` reports.
 */

import { describe, expect, it } from "vitest";
import * as fc from "fast-check";

import { ApiError, normalizeError } from "../errors";

const REQUEST_ID_HEADER = "x-request-id";

/**
 * Status codes constructable by `new Response(...)` per WHATWG fetch.
 * `normalizeError` does not branch on the value of `status` — it forwards
 * it verbatim — so this range exercises the full code path.
 */
const statusArb = fc.integer({ min: 200, max: 599 });

/** Arbitrary `statusText` (HTTP reason phrase). May be empty. */
const statusTextArb = fc.string({ maxLength: 64 });

/**
 * Body arbitrary: union of `undefined` (no body parsed), arbitrary JSON
 * values (`fc.jsonValue()` covers null, primitives, arrays, nested
 * objects with arbitrary keys/values), and biased `ApiErrorBody`-shaped
 * objects — sometimes well-formed (`code` + `message` both non-empty),
 * sometimes missing one or both fields, sometimes with `details` /
 * `request_id` populated.
 *
 * The biased branch ensures we exercise the happy path of
 * `parseErrorBody` densely, while the freeform `fc.jsonValue()` branch
 * stresses the malformed/non-conforming fallback.
 */
const apiErrorShapedArb = fc.record(
  {
    code: fc.option(fc.string(), { nil: undefined }),
    message: fc.option(fc.string(), { nil: undefined }),
    details: fc.option(fc.jsonValue(), { nil: undefined }),
    request_id: fc.option(fc.string(), { nil: undefined }),
  },
  { requiredKeys: [] },
) as fc.Arbitrary<unknown>;

const bodyArb: fc.Arbitrary<unknown> = fc.oneof(
  { weight: 1, arbitrary: fc.constant(undefined) },
  { weight: 4, arbitrary: fc.jsonValue() as fc.Arbitrary<unknown> },
  { weight: 2, arbitrary: apiErrorShapedArb },
);

/**
 * Header arbitrary: `undefined` means absent, `""` means present-but-
 * empty, otherwise any string (which the WHATWG `Headers` API will
 * normalize by trimming surrounding whitespace before storing).
 */
const requestIdHeaderArb = fc.option(fc.string({ maxLength: 64 }), {
  nil: undefined,
});

interface BuiltResponse {
  response: Response;
  /**
   * The header value as actually stored after WHATWG normalization, or
   * `null` when the header was never set. This is the canonical source
   * of truth for assertions — `headers.set(name, " ")` stores `""`, so
   * the input arbitrary alone is not a reliable oracle.
   */
  storedRequestId: string | null;
}

function buildResponse(
  status: number,
  statusText: string,
  requestId: string | undefined,
): BuiltResponse {
  const headers = new Headers();
  if (requestId !== undefined) {
    headers.set(REQUEST_ID_HEADER, requestId);
  }
  const response = new Response(null, { status, statusText, headers });
  return {
    response,
    storedRequestId: response.headers.get(REQUEST_ID_HEADER),
  };
}

describe("Property 4: Error normalization preserves shape", () => {
  it("returns an ApiError with non-empty code, non-empty message, and numeric status for any input", () => {
    fc.assert(
      fc.property(
        statusArb,
        statusTextArb,
        bodyArb,
        requestIdHeaderArb,
        (status, statusText, body, ridHeader) => {
          const { response } = buildResponse(status, statusText, ridHeader);

          const err = normalizeError(response, body);

          expect(err).toBeInstanceOf(ApiError);

          expect(typeof err.code).toBe("string");
          expect(err.code.length).toBeGreaterThan(0);

          expect(typeof err.message).toBe("string");
          expect(err.message.length).toBeGreaterThan(0);

          expect(typeof err.status).toBe("number");
          expect(Number.isFinite(err.status)).toBe(true);
          expect(err.status).toBe(status);
        },
      ),
      { numRuns: 25 },
    );
  });

  it("propagates the x-request-id header onto requestId whenever the header is present and non-empty after normalization", () => {
    fc.assert(
      fc.property(
        statusArb,
        statusTextArb,
        bodyArb,
        requestIdHeaderArb,
        (status, statusText, body, ridHeader) => {
          const { response, storedRequestId } = buildResponse(
            status,
            statusText,
            ridHeader,
          );

          const err = normalizeError(response, body);

          // `Headers.set("x-request-id", " ")` stores `""` per WHATWG
          // normalization, so we read the *stored* value as the oracle.
          // The contract — header takes precedence over any `request_id`
          // field inside `body` — only kicks in when the stored value is
          // a non-empty string.
          if (
            typeof storedRequestId === "string" &&
            storedRequestId.length > 0
          ) {
            expect(err.requestId).toBe(storedRequestId);
          }
        },
      ),
      { numRuns: 25 },
    );
  });

  it("never throws for any combination of status, statusText, body, and headers", () => {
    fc.assert(
      fc.property(
        statusArb,
        statusTextArb,
        bodyArb,
        requestIdHeaderArb,
        (status, statusText, body, ridHeader) => {
          const { response } = buildResponse(status, statusText, ridHeader);
          // No expectation needed: the property holds iff the call
          // returns without throwing. fast-check will surface any thrown
          // error as a counter-example.
          normalizeError(response, body);
        },
      ),
      { numRuns: 25 },
    );
  });
});
