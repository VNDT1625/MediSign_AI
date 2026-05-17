/**
 * Unit tests for `lib/api/errors.ts` — `ApiError` class and `normalizeError`.
 *
 * These cover specific examples and edge cases. The universal "shape is
 * preserved across all responses" property test lives separately in
 * `errors.property.test.ts` (task 4.4) and validates Property 4 against
 * arbitrary status codes and JSON bodies.
 */

import { describe, expect, it } from "vitest";

import { ApiError, normalizeError } from "../errors";

function makeResponse(init: {
  status?: number;
  statusText?: string;
  headers?: Record<string, string>;
}): Response {
  return new Response(null, {
    status: init.status ?? 200,
    statusText: init.statusText ?? "",
    headers: init.headers,
  });
}

describe("ApiError", () => {
  it("exposes required fields and mirrors message into Error.message", () => {
    const err = new ApiError({
      code: "AUTH_INVALID_TOKEN",
      message: "Token khong hop le",
      status: 401,
      requestId: "rid-1",
      details: { errors: [] },
    });

    expect(err).toBeInstanceOf(Error);
    expect(err).toBeInstanceOf(ApiError);
    expect(err.name).toBe("ApiError");
    expect(err.code).toBe("AUTH_INVALID_TOKEN");
    expect(err.message).toBe("Token khong hop le");
    expect(err.status).toBe(401);
    expect(err.requestId).toBe("rid-1");
    expect(err.details).toEqual({ errors: [] });
  });

  it("omits optional fields when not provided", () => {
    const err = new ApiError({
      code: "VALIDATION_ERROR",
      message: "Du lieu khong hop le",
      status: 422,
    });

    expect(err.requestId).toBeUndefined();
    expect(err.details).toBeUndefined();
  });
});

describe("normalizeError — parseable ApiErrorBody", () => {
  it("forwards code/message/details from a well-formed body", () => {
    const response = makeResponse({
      status: 401,
      headers: { "x-request-id": "rid-abc" },
    });

    const err = normalizeError(response, {
      code: "AUTH_INVALID_CREDENTIALS",
      message: "Email/SDT hoac mat khau khong dung",
      details: { errors: [{ loc: ["password"] }] },
    });

    expect(err.code).toBe("AUTH_INVALID_CREDENTIALS");
    expect(err.message).toBe("Email/SDT hoac mat khau khong dung");
    expect(err.status).toBe(401);
    expect(err.requestId).toBe("rid-abc");
    expect(err.details).toEqual({ errors: [{ loc: ["password"] }] });
  });

  it("prefers x-request-id header over the body's request_id field", () => {
    const response = makeResponse({
      status: 500,
      headers: { "x-request-id": "header-rid" },
    });

    const err = normalizeError(response, {
      code: "INTERNAL_SERVER_ERROR",
      message: "He thong dang ban",
      request_id: "body-rid",
    });

    expect(err.requestId).toBe("header-rid");
  });

  it("falls back to body.request_id when header is missing", () => {
    const response = makeResponse({ status: 500 });

    const err = normalizeError(response, {
      code: "INTERNAL_SERVER_ERROR",
      message: "He thong dang ban",
      request_id: "body-rid",
    });

    expect(err.requestId).toBe("body-rid");
  });

  it("leaves requestId undefined when neither header nor body provides one", () => {
    const response = makeResponse({ status: 500 });

    const err = normalizeError(response, {
      code: "INTERNAL_SERVER_ERROR",
      message: "He thong dang ban",
    });

    expect(err.requestId).toBeUndefined();
  });

  it("accepts an explicit headers argument overriding response.headers", () => {
    const response = makeResponse({
      status: 401,
      headers: { "x-request-id": "from-response" },
    });
    const overrideHeaders = new Headers({ "x-request-id": "from-override" });

    const err = normalizeError(
      response,
      { code: "AUTH_INVALID_TOKEN", message: "Token khong hop le" },
      overrideHeaders,
    );

    expect(err.requestId).toBe("from-override");
  });
});

describe("normalizeError — fallback path", () => {
  it("collapses missing body to UNKNOWN_ERROR with statusText fallback", () => {
    const response = makeResponse({ status: 502, statusText: "Bad Gateway" });

    const err = normalizeError(response);

    expect(err.code).toBe("UNKNOWN_ERROR");
    expect(err.message).toBe("Bad Gateway");
    expect(err.status).toBe(502);
  });

  it("falls back to vi-VN literal when statusText is empty", () => {
    const response = makeResponse({ status: 500, statusText: "" });

    const err = normalizeError(response);

    expect(err.code).toBe("UNKNOWN_ERROR");
    expect(err.message).toBe("Yêu cầu thất bại");
    expect(err.message.length).toBeGreaterThan(0);
  });

  it("uses fallback when body is present but missing required fields", () => {
    const response = makeResponse({
      status: 500,
      statusText: "Internal Server Error",
    });

    const err = normalizeError(response, { code: "" });

    expect(err.code).toBe("UNKNOWN_ERROR");
    expect(err.message).toBe("Internal Server Error");
  });

  it("uses fallback when body is not an object (e.g. HTML string)", () => {
    const response = makeResponse({
      status: 504,
      statusText: "Gateway Timeout",
    });

    const err = normalizeError(response, "<html>upstream timed out</html>");

    expect(err.code).toBe("UNKNOWN_ERROR");
    expect(err.message).toBe("Gateway Timeout");
  });

  it("preserves x-request-id header on the fallback envelope", () => {
    const response = makeResponse({
      status: 500,
      statusText: "Internal Server Error",
      headers: { "x-request-id": "rid-fallback" },
    });

    const err = normalizeError(response);

    expect(err.code).toBe("UNKNOWN_ERROR");
    expect(err.requestId).toBe("rid-fallback");
  });

  it("ignores empty x-request-id header", () => {
    const response = makeResponse({
      status: 500,
      statusText: "Internal Server Error",
      headers: { "x-request-id": "" },
    });

    const err = normalizeError(response);

    expect(err.requestId).toBeUndefined();
  });
});
