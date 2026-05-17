/**
 * Integration tests for `SiteHeader` — anonymous vs authenticated state.
 *
 * Validates: Requirements 2.1.5 (logout from avatar menu redirects to "/"),
 *            Requirements 2.2.2 (auth context drives header controls).
 *
 * Scenarios covered:
 *   1. Anonymous state: renders "Đăng nhập" and "Tạo tài khoản" buttons,
 *      does NOT render AvatarMenu.
 *   2. Authenticated state: renders AvatarMenu with user initials,
 *      does NOT render the login/register buttons.
 *   3. Clicking "Đăng xuất" in the AvatarMenu calls `logout` and
 *      redirects to `/`.
 *
 * Strategy:
 *   - Render `SiteHeader` inside a thin wrapper that provides a controlled
 *     `AuthContext` value so we can drive the three auth states
 *     (loading / anonymous / authenticated) without spinning up the real
 *     `AuthProvider` (which would try to call `refreshOnce` on mount).
 *   - Mock `next/navigation` to capture `router.push` calls.
 *   - Mock `useIntent` so `set()` is a no-op (SiteHeader calls it on CTA
 *     clicks; we don't need to test intent logic here).
 *   - The `onLogout` prop on `AvatarMenu` is used to inject a spy so we
 *     can assert the logout action was invoked without needing the real
 *     `authApi.logout` round-trip.
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor, fireEvent, act } from "@testing-library/react";

// ---------------------------------------------------------------------------
// Mock next/navigation — must be hoisted before component imports
// ---------------------------------------------------------------------------

const mockPush = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush, replace: vi.fn(), prefetch: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => "/",
}));

// ---------------------------------------------------------------------------
// Mock useIntent so SiteHeader's `set("home")` call is a no-op
// ---------------------------------------------------------------------------

vi.mock("../../lib/auth/useIntent", () => ({
  useIntent: () => ({
    set: vi.fn(),
    peek: vi.fn(() => null),
    consume: vi.fn(() => ({ redirectPath: "/app/chat" })),
  }),
}));

// ---------------------------------------------------------------------------
// Component + context imports (after mocks)
// ---------------------------------------------------------------------------

import { AuthContext, type AuthContextValue, type AuthState } from "../../lib/auth/AuthProvider";
import { SiteHeader } from "../SiteHeader";
import { buildAuthUserResponse } from "../../test/msw/handlers";

// ---------------------------------------------------------------------------
// Test helpers
// ---------------------------------------------------------------------------

/**
 * Build a minimal `AuthContextValue` for the given state. Actions that
 * are not under test are stubbed with `vi.fn()` returning resolved promises.
 */
function buildAuthContextValue(
  state: AuthState,
  overrides: Partial<AuthContextValue> = {},
): AuthContextValue {
  return {
    state,
    isAuthenticated: state.status === "authenticated",
    login: vi.fn(() => Promise.resolve()),
    register: vi.fn(() => Promise.resolve()),
    logout: vi.fn(() => Promise.resolve()),
    changePassword: vi.fn(() => Promise.resolve()),
    hydrate: vi.fn(() => Promise.resolve()),
    ...overrides,
  };
}

/**
 * Render `SiteHeader` with a controlled auth context value.
 * Returns the context value so tests can assert on its methods.
 */
function renderWithAuth(
  authValue: AuthContextValue,
  props: { onLoginClick?: () => void } = {},
) {
  render(
    <AuthContext.Provider value={authValue}>
      <SiteHeader {...props} />
    </AuthContext.Provider>,
  );
  return authValue;
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("SiteHeader — anonymous vs authenticated", () => {
  beforeEach(() => {
    mockPush.mockReset();
  });

  // -------------------------------------------------------------------------
  // 1. Anonymous state
  // -------------------------------------------------------------------------

  describe("anonymous state", () => {
    it("renders 'Đăng nhập' button", () => {
      renderWithAuth(buildAuthContextValue({ status: "anonymous" }));

      expect(
        screen.getByRole("button", { name: /đăng nhập/i }),
      ).toBeInTheDocument();
    });

    it("renders 'Tạo tài khoản' button", () => {
      renderWithAuth(buildAuthContextValue({ status: "anonymous" }));

      expect(
        screen.getByRole("button", { name: /tạo tài khoản/i }),
      ).toBeInTheDocument();
    });

    it("does NOT render AvatarMenu (no initials button)", () => {
      const user = buildAuthUserResponse({ full_name: "Nguyễn Văn A" });
      renderWithAuth(buildAuthContextValue({ status: "anonymous" }));

      // AvatarMenu renders a button with aria-label "Tài khoản của <name>".
      // Since we're anonymous, no such button should exist.
      expect(
        screen.queryByRole("button", { name: /tài khoản của/i }),
      ).not.toBeInTheDocument();
    });

    it("calls onLoginClick when 'Đăng nhập' is clicked", () => {
      const onLoginClick = vi.fn();
      renderWithAuth(buildAuthContextValue({ status: "anonymous" }), {
        onLoginClick,
      });

      fireEvent.click(screen.getByRole("button", { name: /đăng nhập/i }));

      expect(onLoginClick).toHaveBeenCalledTimes(1);
    });

    it("calls onLoginClick when 'Tạo tài khoản' is clicked", () => {
      const onLoginClick = vi.fn();
      renderWithAuth(buildAuthContextValue({ status: "anonymous" }), {
        onLoginClick,
      });

      fireEvent.click(screen.getByRole("button", { name: /tạo tài khoản/i }));

      expect(onLoginClick).toHaveBeenCalledTimes(1);
    });
  });

  // -------------------------------------------------------------------------
  // 2. Authenticated state
  // -------------------------------------------------------------------------

  describe("authenticated state", () => {
    it("renders AvatarMenu with user initials", () => {
      const user = buildAuthUserResponse({ full_name: "Nguyễn Văn A" });
      renderWithAuth(
        buildAuthContextValue({ status: "authenticated", user }),
      );

      // AvatarMenu renders a button with aria-label "Tài khoản của <full_name>".
      expect(
        screen.getByRole("button", { name: /tài khoản của nguyễn văn a/i }),
      ).toBeInTheDocument();
    });

    it("shows correct initials in the avatar button (first + last word)", () => {
      // "Nguyễn Văn A" → strip diacritics → "Nguyen Van A" → "N" + "A" = "NA"
      const user = buildAuthUserResponse({ full_name: "Nguyễn Văn A" });
      renderWithAuth(
        buildAuthContextValue({ status: "authenticated", user }),
      );

      const avatarButton = screen.getByRole("button", {
        name: /tài khoản của nguyễn văn a/i,
      });
      // The initials are rendered inside a <span aria-hidden="true"> inside
      // the button. We check the button's text content.
      expect(avatarButton.textContent).toBe("NA");
    });

    it("does NOT render 'Đăng nhập' button when authenticated", () => {
      const user = buildAuthUserResponse();
      renderWithAuth(
        buildAuthContextValue({ status: "authenticated", user }),
      );

      expect(
        screen.queryByRole("button", { name: /đăng nhập/i }),
      ).not.toBeInTheDocument();
    });

    it("does NOT render 'Tạo tài khoản' button when authenticated", () => {
      const user = buildAuthUserResponse();
      renderWithAuth(
        buildAuthContextValue({ status: "authenticated", user }),
      );

      expect(
        screen.queryByRole("button", { name: /tạo tài khoản/i }),
      ).not.toBeInTheDocument();
    });
  });

  // -------------------------------------------------------------------------
  // 3. Loading state
  // -------------------------------------------------------------------------

  describe("loading state", () => {
    it("renders neither login buttons nor AvatarMenu while loading", () => {
      renderWithAuth(buildAuthContextValue({ status: "loading" }));

      expect(
        screen.queryByRole("button", { name: /đăng nhập/i }),
      ).not.toBeInTheDocument();
      expect(
        screen.queryByRole("button", { name: /tạo tài khoản/i }),
      ).not.toBeInTheDocument();
      expect(
        screen.queryByRole("button", { name: /tài khoản của/i }),
      ).not.toBeInTheDocument();
    });
  });

  // -------------------------------------------------------------------------
  // 4. Logout flow — clicking "Đăng xuất" calls logout and redirects to "/"
  // -------------------------------------------------------------------------

  describe("logout flow", () => {
    it("clicking 'Đăng xuất' calls logout and redirects to '/'", async () => {
      const logoutSpy = vi.fn(() => Promise.resolve());
      const user = buildAuthUserResponse({ full_name: "Test User" });

      renderWithAuth(
        buildAuthContextValue({ status: "authenticated", user }, {
          logout: logoutSpy,
        }),
      );

      // Open the AvatarMenu dropdown by clicking the avatar button.
      const avatarButton = screen.getByRole("button", {
        name: /tài khoản của test user/i,
      });
      fireEvent.click(avatarButton);

      // The dropdown should now be visible with the logout button.
      const logoutButton = await screen.findByRole("menuitem", {
        name: /đăng xuất/i,
      });
      expect(logoutButton).toBeInTheDocument();

      // Click "Đăng xuất".
      fireEvent.click(logoutButton);

      // logout() should be called.
      await waitFor(() => {
        expect(logoutSpy).toHaveBeenCalledTimes(1);
      });

      // router.push("/") should be called after logout.
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith("/");
      });
    });

    it("redirects to '/' even if logout throws (best-effort logout)", async () => {
      // AvatarMenu's handleLogout wraps the action in try/finally, so
      // router.push("/") is always called regardless of whether logout throws.
      // Use an async function that throws rather than Promise.reject() to avoid
      // an unhandled rejection before the component's try/finally catches it.
      const logoutSpy = vi.fn(async () => {
        throw new Error("network error");
      });
      const user = buildAuthUserResponse({ full_name: "Test User" });

      renderWithAuth(
        buildAuthContextValue({ status: "authenticated", user }, {
          logout: logoutSpy,
        }),
      );

      // Open dropdown.
      fireEvent.click(
        screen.getByRole("button", { name: /tài khoản của test user/i }),
      );

      // Click logout.
      const logoutButton = await screen.findByRole("menuitem", {
        name: /đăng xuất/i,
      });
      fireEvent.click(logoutButton);

      // Even though logout threw, router.push("/") must still be called.
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith("/");
      });
    });

    it("logout button shows 'Đang đăng xuất...' while in flight", async () => {
      // Use a never-resolving promise to freeze the logout in-flight state.
      let resolveLogout!: () => void;
      const logoutPromise = new Promise<void>((resolve) => {
        resolveLogout = resolve;
      });
      const logoutSpy = vi.fn(() => logoutPromise);
      const user = buildAuthUserResponse({ full_name: "Test User" });

      renderWithAuth(
        buildAuthContextValue({ status: "authenticated", user }, {
          logout: logoutSpy,
        }),
      );

      // Open dropdown.
      fireEvent.click(
        screen.getByRole("button", { name: /tài khoản của test user/i }),
      );

      const logoutButton = await screen.findByRole("menuitem", {
        name: /đăng xuất/i,
      });
      fireEvent.click(logoutButton);

      // While in flight, the button text changes to "Đang đăng xuất...".
      await waitFor(() => {
        expect(screen.getByText(/đang đăng xuất/i)).toBeInTheDocument();
      });

      // Clean up: resolve the promise so the component can unmount cleanly.
      await act(async () => {
        resolveLogout();
      });
    });
  });
});
