// Integration tests for `lib/auth/AuthProvider.tsx` — verifies the three
// hydration paths (no cookie, valid cookie, expired/invalid cookie) drive
// the auth state machine through the expected transitions.
//
// Validates: Requirements 2.2.2 (auth context + hydrate), 2.1.6
//   (refresh + expiry handling).
//
// Strategy: instead of routing through MSW for the same-origin
// `/api/auth/refresh` proxy AND the FastAPI `/auth/me` endpoint, we mock
// `refreshOnce()` (from `lib/api/fetcher`) and the `authApi.me()` call
// directly. This is the cleanest seam: the provider's contract is "call
// refreshOnce, then call me, react to outcomes" — exercising the
// fetcher's transport layer here would only re-test what
// `fetcher.property.test.ts` already covers, while introducing the
// undici/jsdom AbortSignal-mismatch hazard documented at the top of
// that file.
//
// State machine under test (mirrors AuthProvider.tsx docs):
//
//   loading ──► anonymous       (refresh fails → no session)
//           └─► authenticated   (refresh succeeds + me succeeds)
//
//   anonymous     ──► authenticated   (login)
//   authenticated ──► anonymous       (logout)

import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor, act } from "@testing-library/react";

// Mock the fetcher's `refreshOnce` and the auth API surface BEFORE
// importing the provider. Vitest hoists `vi.mock` to the top of the
// file, so the module the provider imports will resolve to these mocks.
vi.mock("../../api/fetcher", async () => {
  const actual = await vi.importActual<typeof import("../../api/fetcher")>(
    "../../api/fetcher",
  );
  return {
    ...actual,
    // Replaced per-test below. The default rejects so that any test
    // forgetting to set up its case fails loudly rather than silently
    // hydrating to anonymous on a no-op resolve.
    refreshOnce: vi.fn(() => Promise.reject(new Error("refreshOnce not stubbed"))),
  };
});

vi.mock("../../api/auth", async () => {
  const actual = await vi.importActual<typeof import("../../api/auth")>(
    "../../api/auth",
  );
  return {
    ...actual,
    me: vi.fn(() => Promise.reject(new Error("me() not stubbed"))),
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(() => Promise.resolve()),
    changePassword: vi.fn(),
  };
});

// Imports must come AFTER `vi.mock` calls — they are hoisted, but it is
// clearer to the reader that the imports resolve to the mocked modules.
import { AuthProvider } from "../AuthProvider";
import { useAuth } from "../useAuth";
import { tokenStore } from "../tokenStore";
import * as fetcher from "../../api/fetcher";
import * as authApi from "../../api/auth";
import { buildAuthUserResponse } from "../../../test/msw/handlers";

const refreshOnceMock = fetcher.refreshOnce as ReturnType<typeof vi.fn>;
const meMock = authApi.me as ReturnType<typeof vi.fn>;
const loginMock = authApi.login as ReturnType<typeof vi.fn>;
const logoutMock = authApi.logout as ReturnType<typeof vi.fn>;

/** Tiny consumer that surfaces the current auth state for assertions. */
function StateProbe() {
  const { state } = useAuth();
  return (
    <div>
      <span data-testid="status">{state.status}</span>
      {state.status === "authenticated" ? (
        <span data-testid="user-email">{state.user.email}</span>
      ) : null}
    </div>
  );
}

function renderProvider() {
  return render(
    <AuthProvider>
      <StateProbe />
    </AuthProvider>,
  );
}

describe("AuthProvider — hydration state machine", () => {
  beforeEach(() => {
    refreshOnceMock.mockReset();
    meMock.mockReset();
    loginMock.mockReset();
    logoutMock.mockReset();
    tokenStore.clear();
  });

  it("hydrates to `anonymous` when no cookie is present (refresh proxy throws AUTH_SESSION_EXPIRED)", async () => {
    // The fetcher's `refreshOnce` raises a synthesized
    // `AUTH_SESSION_EXPIRED` when the proxy returns 401 (no cookie or
    // invalid cookie). The provider catches and goes anonymous.
    const sessionExpired = Object.assign(new Error("session expired"), {
      code: "AUTH_SESSION_EXPIRED",
      status: 401,
    });
    refreshOnceMock.mockRejectedValueOnce(sessionExpired);

    renderProvider();

    // First paint: still in the loading state (provider initializes
    // with `{status: "loading"}` and the effect has not flushed yet).
    expect(screen.getByTestId("status")).toHaveTextContent(/loading|anonymous/);

    await waitFor(() =>
      expect(screen.getByTestId("status")).toHaveTextContent("anonymous"),
    );

    // me() must NOT be called when refresh fails — it would burn a
    // request against an obviously-anonymous tab.
    expect(meMock).not.toHaveBeenCalled();
    expect(refreshOnceMock).toHaveBeenCalledTimes(1);
  });

  it("hydrates to `authenticated` when refresh succeeds and /auth/me returns the user", async () => {
    refreshOnceMock.mockResolvedValueOnce("FRESH_ACCESS_TOKEN");
    meMock.mockResolvedValueOnce(
      buildAuthUserResponse({ email: "alice@medisign.ai" }),
    );

    renderProvider();

    await waitFor(() =>
      expect(screen.getByTestId("status")).toHaveTextContent("authenticated"),
    );
    expect(screen.getByTestId("user-email")).toHaveTextContent(
      "alice@medisign.ai",
    );

    expect(refreshOnceMock).toHaveBeenCalledTimes(1);
    expect(meMock).toHaveBeenCalledTimes(1);
  });

  it("hydrates to `anonymous` when the cookie is expired/invalid (refresh proxy 401 → fetcher throws)", async () => {
    // Same shape as the no-cookie case from the provider's perspective:
    // it does not need to distinguish "cookie missing" from "cookie
    // rejected" — both collapse to AUTH_SESSION_EXPIRED. We assert it
    // here as a separate test because the design.md hydration list calls
    // these out as three distinct scenarios.
    refreshOnceMock.mockRejectedValueOnce(
      Object.assign(new Error("expired"), {
        code: "AUTH_SESSION_EXPIRED",
        status: 401,
      }),
    );

    renderProvider();

    await waitFor(() =>
      expect(screen.getByTestId("status")).toHaveTextContent("anonymous"),
    );
    expect(meMock).not.toHaveBeenCalled();
    // Defensive: even if some upstream code wrote a stale token, the
    // provider's catch path clears the in-memory store.
    expect(tokenStore.get()).toBeNull();
  });

  it("hydrates to `anonymous` when refresh succeeds but /auth/me fails", async () => {
    refreshOnceMock.mockResolvedValueOnce("FRESH_ACCESS_TOKEN");
    meMock.mockRejectedValueOnce(new Error("network blip"));

    renderProvider();

    await waitFor(() =>
      expect(screen.getByTestId("status")).toHaveTextContent("anonymous"),
    );

    // The provider's catch path clears the token even if `refreshOnce`
    // had populated it before `me()` failed.
    expect(tokenStore.get()).toBeNull();
  });
});

describe("AuthProvider — actions", () => {
  beforeEach(() => {
    refreshOnceMock.mockReset();
    meMock.mockReset();
    loginMock.mockReset();
    logoutMock.mockReset();
    tokenStore.clear();
  });

  it("login() transitions `anonymous → authenticated` and seeds tokenStore", async () => {
    // Bootstrap to anonymous first.
    refreshOnceMock.mockRejectedValueOnce(
      Object.assign(new Error("no cookie"), {
        code: "AUTH_SESSION_EXPIRED",
        status: 401,
      }),
    );

    // Capture the `login` and `state` from a probe.
    type Captured = {
      state: { status: string };
      login: (input: unknown) => Promise<void>;
    } | null;
    const captured: { current: Captured } = { current: null };
    function ActionProbe() {
      const { state, login } = useAuth();
      captured.current = { state, login };
      return <span data-testid="status">{state.status}</span>;
    }

    render(
      <AuthProvider>
        <ActionProbe />
      </AuthProvider>,
    );

    await waitFor(() =>
      expect(screen.getByTestId("status")).toHaveTextContent("anonymous"),
    );

    loginMock.mockResolvedValueOnce({
      user: buildAuthUserResponse({ email: "bob@medisign.ai" }),
      access_token: "BOB_ACCESS",
      expires_in: 3600,
    });

    await act(async () => {
      await captured.current!.login({
        email: "bob@medisign.ai",
        password: "Hunter2!",
      });
    });

    await waitFor(() =>
      expect(screen.getByTestId("status")).toHaveTextContent("authenticated"),
    );
    expect(tokenStore.get()).toBe("BOB_ACCESS");
    expect(loginMock).toHaveBeenCalledTimes(1);
  });

  it("logout() transitions `authenticated → anonymous` even when the proxy throws", async () => {
    // Bootstrap to authenticated.
    refreshOnceMock.mockResolvedValueOnce("FRESH");
    meMock.mockResolvedValueOnce(buildAuthUserResponse());
    tokenStore.set("FRESH", 3600);

    type Captured = {
      state: { status: string };
      logout: () => Promise<void>;
    } | null;
    const captured: { current: Captured } = { current: null };
    function ActionProbe() {
      const { state, logout } = useAuth();
      captured.current = { state, logout };
      return <span data-testid="status">{state.status}</span>;
    }

    render(
      <AuthProvider>
        <ActionProbe />
      </AuthProvider>,
    );

    await waitFor(() =>
      expect(screen.getByTestId("status")).toHaveTextContent("authenticated"),
    );

    // Best-effort logout: even when the proxy throws, the provider must
    // still clear local state and transition to anonymous.
    logoutMock.mockRejectedValueOnce(new Error("network blip"));

    await act(async () => {
      await captured.current!.logout();
    });

    await waitFor(() =>
      expect(screen.getByTestId("status")).toHaveTextContent("anonymous"),
    );
    expect(tokenStore.get()).toBeNull();
  });
});
