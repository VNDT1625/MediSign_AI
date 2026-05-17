// @vitest-environment node
/**
 * Integration test for the Edge route guard middleware.
 *
 * Validates: Requirements 2.2.1 (route guard for `/app/*`).
 *
 * The guard MUST:
 *   1. Redirect anonymous traffic (no `medisign_rt` cookie) to
 *      `/?login=1&intent=<original_path_and_search>` with a 307 status.
 *   2. Allow traffic carrying the `medisign_rt` cookie to pass through
 *      via `NextResponse.next()` (no Location header, status 200).
 *   3. Preserve the original `pathname + search` verbatim inside the
 *      `intent` query parameter so the LoginModal can replay it
 *      post-login (smart redirect, Requirement 2.1.4).
 *
 * This is a node-environment test because Next.js's edge primitives
 * (`NextRequest`, `NextResponse`) need the Web Fetch globals that ship
 * with Node 18+, and jsdom's URL/Request shims are incomplete.
 */
import { describe, it, expect } from "vitest";
import { NextRequest } from "next/server";
import { middleware } from "../middleware";

describe("middleware /app/* guard", () => {
  it("redirects anonymous request to /?login=1&intent=<path> with 307", () => {
    const req = new NextRequest("http://localhost:3000/app/medicine");
    const res = middleware(req);

    expect(res.status).toBe(307);

    const location = res.headers.get("location");
    expect(location).not.toBeNull();

    const url = new URL(location!);
    expect(url.pathname).toBe("/");
    expect(url.searchParams.get("login")).toBe("1");
    expect(url.searchParams.get("intent")).toBe("/app/medicine");
  });

  it("passes through when medisign_rt cookie is present", () => {
    const req = new NextRequest("http://localhost:3000/app/medicine", {
      headers: {
        cookie: "medisign_rt=abc123",
      },
    });
    const res = middleware(req);

    // NextResponse.next() returns a 200 response with no Location header.
    expect(res.status).toBe(200);
    expect(res.headers.get("location")).toBeNull();
  });

  it("preserves search params in intent", () => {
    const req = new NextRequest("http://localhost:3000/app/chat?prefill=hi");
    const res = middleware(req);

    expect(res.status).toBe(307);

    const location = res.headers.get("location");
    expect(location).not.toBeNull();

    const url = new URL(location!);
    // intent should include the original pathname + search verbatim.
    expect(url.searchParams.get("intent")).toBe("/app/chat?prefill=hi");
  });
});
