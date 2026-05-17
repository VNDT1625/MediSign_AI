/**
 * Unit tests for `lib/api/{auth,consult,medicine,profile}.ts` — the
 * thin typed wrappers added in task 4.7.
 *
 * These tests assert the only behaviour those modules add on top of
 * `apiFetch`: the URL string, HTTP method, body, and `authRequired`
 * flag each function passes. We mock `apiFetch` directly (rather than
 * intercepting at the network layer) so that the tests exercise the
 * wrappers' pure call-shape regardless of the surrounding fetch /
 * interceptor / MSW infrastructure.
 *
 * The fetcher itself (refresh single-flight, error normalization,
 * timeouts, URL resolution) is covered by `fetcher.property.test.ts`
 * and `errors.*.test.ts` and is deliberately not duplicated here.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Mock the fetcher module so every API wrapper invocation is a recorded
// call against `apiFetch`. The mock factory returns minimal values that
// satisfy the wrappers' return-type unwrapping (an empty object cast to
// the relevant response shape). Tests assert on `mock.calls`, not the
// return value.
vi.mock("../fetcher", () => ({
  apiFetch: vi.fn(async () => ({})),
  __resetRefreshForTests: vi.fn(),
}));

import { apiFetch } from "../fetcher";
import * as auth from "../auth";
import * as consult from "../consult";
import * as medicine from "../medicine";
import * as profile from "../profile";

const mockApiFetch = vi.mocked(apiFetch);

beforeEach(() => {
  mockApiFetch.mockClear();
  mockApiFetch.mockResolvedValue({} as never);
});

afterEach(() => {
  mockApiFetch.mockReset();
});

// ---------------------------------------------------------------------------
// auth.ts
// ---------------------------------------------------------------------------

describe("auth module", () => {
  it("login() POSTs to the same-origin /api/auth/login proxy without auth", async () => {
    await auth.login({ email: "user@example.com", password: "supersecret1" });

    expect(mockApiFetch).toHaveBeenCalledTimes(1);
    const [path, opts] = mockApiFetch.mock.calls[0]!;
    expect(path).toBe("/api/auth/login");
    expect(opts?.method).toBe("POST");
    expect(opts?.body).toEqual({
      email: "user@example.com",
      password: "supersecret1",
    });
    // Cookie bridge proxy is anonymous — no bearer attached.
    expect(opts?.authRequired).toBe(false);
  });

  it("login() forwards a phone+password credential pair untouched", async () => {
    await auth.login({ phone: "+84900000001", password: "supersecret1" });
    const [, opts] = mockApiFetch.mock.calls[0]!;
    expect(opts?.body).toEqual({
      phone: "+84900000001",
      password: "supersecret1",
    });
  });

  it("register() POSTs to FastAPI /auth/register without bearer", async () => {
    await auth.register({
      email: "new@example.com",
      phone: "+84900000002",
      username: "new_user",
      full_name: "New User",
      password: "supersecret1",
    });

    const [path, opts] = mockApiFetch.mock.calls[0]!;
    // Backend path — fetcher will prefix with NEXT_PUBLIC_API_BASE_URL.
    expect(path).toBe("/auth/register");
    expect(opts?.method).toBe("POST");
    expect(opts?.authRequired).toBe(false);
    expect(opts?.body).toMatchObject({
      email: "new@example.com",
      username: "new_user",
    });
  });

  it("me() GETs FastAPI /auth/me with default (auth-required) options", async () => {
    await auth.me();

    const [path, opts] = mockApiFetch.mock.calls[0]!;
    expect(path).toBe("/auth/me");
    expect(opts?.method).toBe("GET");
    // Default `authRequired` (`undefined`) maps to `true` in the fetcher.
    expect(opts?.authRequired).toBeUndefined();
  });

  it("logout() POSTs to the same-origin /api/auth/logout proxy without auth", async () => {
    await auth.logout();

    const [path, opts] = mockApiFetch.mock.calls[0]!;
    expect(path).toBe("/api/auth/logout");
    expect(opts?.method).toBe("POST");
    expect(opts?.authRequired).toBe(false);
  });

  it("changePassword() POSTs to FastAPI /auth/change-password (auth required)", async () => {
    await auth.changePassword({
      current_password: "oldpassword1",
      new_password: "newpassword1",
    });

    const [path, opts] = mockApiFetch.mock.calls[0]!;
    expect(path).toBe("/auth/change-password");
    expect(opts?.method).toBe("POST");
    expect(opts?.authRequired).toBeUndefined(); // → bearer attached by default
    expect(opts?.body).toEqual({
      current_password: "oldpassword1",
      new_password: "newpassword1",
    });
  });
});

// ---------------------------------------------------------------------------
// consult.ts
// ---------------------------------------------------------------------------

describe("consult module", () => {
  it("triage() POSTs to /consult/triage without bearer (anonymous-friendly)", async () => {
    await consult.triage({
      symptom_text: "Đau đầu liên tục",
      locale: "vi-VN",
    });

    const [path, opts] = mockApiFetch.mock.calls[0]!;
    expect(path).toBe("/consult/triage");
    expect(opts?.method).toBe("POST");
    expect(opts?.body).toEqual({
      symptom_text: "Đau đầu liên tục",
      locale: "vi-VN",
    });
    // Backend triage endpoint is anonymous-friendly per design.md;
    // wrapper opts out of the bearer attachment.
    expect(opts?.authRequired).toBe(false);
  });

  it("triageHistory() GETs /consult/triage/history with default (auth-required) options", async () => {
    await consult.triageHistory();

    const [path, opts] = mockApiFetch.mock.calls[0]!;
    expect(path).toBe("/consult/triage/history");
    expect(opts?.method).toBe("GET");
    expect(opts?.authRequired).toBeUndefined();
  });
});

// ---------------------------------------------------------------------------
// medicine.ts
// ---------------------------------------------------------------------------

describe("medicine module", () => {
  it("scan() POSTs to /medicine/scan with bearer (default)", async () => {
    await medicine.scan({
      extracted_text: "Paracetamol 500mg",
      current_medications: [],
    });

    const [path, opts] = mockApiFetch.mock.calls[0]!;
    expect(path).toBe("/medicine/scan");
    expect(opts?.method).toBe("POST");
    expect(opts?.authRequired).toBeUndefined();
    expect(opts?.body).toEqual({
      extracted_text: "Paracetamol 500mg",
      current_medications: [],
    });
  });

  it("drugSuggestions() targets /api/drug/suggestions/<encoded keyword>", async () => {
    await medicine.drugSuggestions("para cetamol");

    const [path, opts] = mockApiFetch.mock.calls[0]!;
    // Keyword is percent-encoded for safe path interpolation.
    expect(path).toBe("/api/drug/suggestions/para%20cetamol");
    expect(opts?.method).toBe("GET");
  });

  it("drugSuggestions() encodes URI-unsafe characters in the keyword", async () => {
    await medicine.drugSuggestions("a/b?c");
    const [path] = mockApiFetch.mock.calls[0]!;
    expect(path).toBe("/api/drug/suggestions/a%2Fb%3Fc");
  });

  it("drugSearch() POSTs to /api/drug/search (FastAPI, NOT a same-origin proxy)", async () => {
    await medicine.drugSearch({ drug_name: "Paracetamol", language: "vi" });

    const [path, opts] = mockApiFetch.mock.calls[0]!;
    expect(path).toBe("/api/drug/search");
    expect(opts?.method).toBe("POST");
    expect(opts?.body).toEqual({ drug_name: "Paracetamol", language: "vi" });
    // Crucial: this path must NOT begin with `/api/auth/`, which is
    // the only same-origin allow-list in `fetcher.resolveUrl()`. All
    // other `/api/...` paths fall through to the FastAPI base URL.
    expect(path.startsWith("/api/auth/")).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// profile.ts
// ---------------------------------------------------------------------------

describe("profile module", () => {
  it("re-exports me() from auth", () => {
    expect(profile.me).toBe(auth.me);
  });

  it("re-exports changePassword() from auth", () => {
    expect(profile.changePassword).toBe(auth.changePassword);
  });

  it("getInitials() collapses common name shapes to up to 2 uppercase letters", () => {
    expect(profile.getInitials("Nguyễn Văn A")).toBe("NA");
    expect(profile.getInitials("Trần Thị Bình")).toBe("TB");
    expect(profile.getInitials("Madonna")).toBe("M");
    expect(profile.getInitials("  ")).toBe("?");
    expect(profile.getInitials("")).toBe("?");
    expect(profile.getInitials(null)).toBe("?");
    expect(profile.getInitials(undefined)).toBe("?");
  });

  it("getDisplayName() prefers full_name, falls back to username then email", () => {
    const baseUser = {
      id: "id",
      email: "an@example.com",
      phone: null,
      username: "an_n",
      full_name: "An Nguyen",
      is_email_verified: true,
      is_phone_verified: false,
      account_type: "user" as const,
      created_at: "2024-01-01T00:00:00Z",
    };

    expect(profile.getDisplayName(baseUser)).toBe("An Nguyen");
    expect(
      profile.getDisplayName({ ...baseUser, full_name: "  " }),
    ).toBe("an_n");
    expect(
      profile.getDisplayName({ ...baseUser, full_name: "", username: "" }),
    ).toBe("an@example.com");
    expect(
      profile.getDisplayName({
        ...baseUser,
        full_name: "",
        username: "",
        email: "",
      }),
    ).toBe("Người dùng");
    expect(profile.getDisplayName(null)).toBe("Người dùng");
    expect(profile.getDisplayName(undefined)).toBe("Người dùng");
  });
});
