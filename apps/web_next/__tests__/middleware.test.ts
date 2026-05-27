// @vitest-environment node
/**
 * Integration test cho middleware dọn dẹp legacy `/app/*`.
 *
 * Web hiện tại không còn shell `/app/*`. Các trang chat / profile thật
 * sống ở public route `/chat`, `/profile`. Bất kỳ link cũ nào dạng
 * `/app/...` đều phải được middleware redirect về public route đúng.
 *
 *   - `/app/chat[?...]`     → `/chat[?...]`
 *   - `/app/profile[?...]`  → `/profile[?...]`
 *   - `/app/<other>`        → `/`
 *
 * Search / hash phải được giữ nguyên để link sâu không mất prefill.
 */
import { describe, it, expect } from "vitest";
import { NextRequest } from "next/server";
import { middleware } from "../middleware";

describe("middleware legacy `/app/*` cleanup", () => {
  it("redirects /app/chat → /chat", () => {
    const req = new NextRequest("http://localhost:3000/app/chat");
    const res = middleware(req);

    expect(res.status).toBeGreaterThanOrEqual(300);
    expect(res.status).toBeLessThan(400);

    const location = res.headers.get("location");
    expect(location).not.toBeNull();

    const url = new URL(location!);
    expect(url.pathname).toBe("/chat");
  });

  it("redirects /app/profile → /profile", () => {
    const req = new NextRequest("http://localhost:3000/app/profile");
    const res = middleware(req);

    const location = res.headers.get("location");
    const url = new URL(location!);
    expect(url.pathname).toBe("/profile");
  });

  it("redirects unknown /app/<path> → /", () => {
    const req = new NextRequest("http://localhost:3000/app/medicine");
    const res = middleware(req);

    const location = res.headers.get("location");
    const url = new URL(location!);
    expect(url.pathname).toBe("/");
  });

  it("preserves search params on /app/chat → /chat", () => {
    const req = new NextRequest("http://localhost:3000/app/chat?prefill=hi");
    const res = middleware(req);

    const location = res.headers.get("location");
    const url = new URL(location!);
    expect(url.pathname).toBe("/chat");
    expect(url.searchParams.get("prefill")).toBe("hi");
  });
});
