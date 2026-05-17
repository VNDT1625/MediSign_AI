/**
 * Integration tests for `ChangePasswordCard` — change password flows.
 *
 * Validates: Requirements 2.3.3 (change password / force re-login).
 *
 * Scenarios covered:
 *   1. Wrong current password (401 AUTH_INVALID_CREDENTIALS) → inline field
 *      error on `current_password` field
 *   2. Success → shows "Đổi mật khẩu thành công" banner → calls `logout()`
 *      → redirects to `/?session=changed-password`
 *   3. Validation: empty fields → inline validation errors shown
 *   4. Confirm password mismatch → inline error on confirm field
 *
 * Strategy:
 *   - Render `ChangePasswordCard` inside `AuthProvider` so the real auth
 *     state machine is exercised end-to-end.
 *   - Mock `next/navigation` (useRouter) to capture navigation calls
 *     without a real Next.js runtime.
 *   - Mock `lib/api/auth` directly to control `changePassword` and
 *     `logout` responses without MSW URL matching complexity.
 *   - Mock `refreshOnce` from the fetcher so the AuthProvider's mount-time
 *     hydration resolves immediately to `anonymous`.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, waitFor, fireEvent, act } from "@testing-library/react";

// ---------------------------------------------------------------------------
// Mock next/navigation — must be hoisted before any component imports
// ---------------------------------------------------------------------------

const mockPush = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
    replace: vi.fn(),
    prefetch: vi.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => "/app/profile",
}));

// ---------------------------------------------------------------------------
// Mock refreshOnce so AuthProvider hydration resolves to `anonymous`
// immediately (no real cookie in jsdom).
// ---------------------------------------------------------------------------

vi.mock("../../lib/api/fetcher", async () => {
  const actual = await vi.importActual<typeof import("../../lib/api/fetcher")>(
    "../../lib/api/fetcher",
  );
  return {
    ...actual,
    refreshOnce: vi.fn(() =>
      Promise.reject(
        Object.assign(new Error("no cookie"), {
          code: "AUTH_SESSION_EXPIRED",
          status: 401,
        }),
      ),
    ),
  };
});

// ---------------------------------------------------------------------------
// Mock lib/api/auth to control changePassword and logout responses
// ---------------------------------------------------------------------------

vi.mock("../../lib/api/auth", async () => {
  const actual = await vi.importActual<typeof import("../../lib/api/auth")>(
    "../../lib/api/auth",
  );
  return {
    ...actual,
    changePassword: vi.fn(),
    logout: vi.fn(() => Promise.resolve()),
    me: vi.fn(() => Promise.reject(new Error("me not stubbed"))),
  };
});

// ---------------------------------------------------------------------------
// Component imports (after mocks)
// ---------------------------------------------------------------------------

import { AuthProvider } from "../../lib/auth/AuthProvider";
import { ChangePasswordCard } from "../profile/ChangePasswordCard";
import * as authApi from "../../lib/api/auth";
import { ApiError } from "../../lib/api/errors";

const changePasswordMock = authApi.changePassword as ReturnType<typeof vi.fn>;
const logoutMock = authApi.logout as ReturnType<typeof vi.fn>;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Render `ChangePasswordCard` inside `AuthProvider` and wait for the
 * component to settle (hydration completes to `anonymous`).
 */
async function renderCard() {
  render(
    <AuthProvider>
      <ChangePasswordCard />
    </AuthProvider>,
  );

  // Wait for the card heading to appear — confirms the component mounted.
  await waitFor(() => {
    expect(screen.getByRole("heading", { name: /đổi mật khẩu/i })).toBeInTheDocument();
  });
}

/**
 * Fill all three password fields and click the submit button.
 *
 * We query by `id` for the new-password and confirm-password fields because
 * `getByLabelText(/mật khẩu mới/i)` would match both "Mật khẩu mới" and
 * "Xác nhận mật khẩu mới" (the confirm label contains the same substring).
 */
function fillAndSubmit(
  currentPassword: string,
  newPassword: string,
  confirmPassword: string,
) {
  fireEvent.change(screen.getByLabelText(/mật khẩu hiện tại/i), {
    target: { value: currentPassword },
  });
  // Use exact id to avoid ambiguity with "Xác nhận mật khẩu mới"
  fireEvent.change(document.getElementById("change-new-password")!, {
    target: { value: newPassword },
  });
  fireEvent.change(document.getElementById("change-confirm-password")!, {
    target: { value: confirmPassword },
  });

  const submitButton = screen.getByRole("button", { name: /^đổi mật khẩu$/i });
  fireEvent.click(submitButton);
}

/**
 * Query the success banner specifically (the `role="status"` div, not the
 * static paragraph that also contains "thành công").
 */
function querySuccessBanner() {
  return screen.queryByRole("status");
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("ChangePasswordCard — integration flows", () => {
  beforeEach(() => {
    mockPush.mockReset();
    changePasswordMock.mockReset();
    logoutMock.mockReset();
    logoutMock.mockResolvedValue(undefined);
  });

  afterEach(() => {
    // Restore real timers if a test used fake timers.
    vi.useRealTimers();
  });

  // -------------------------------------------------------------------------
  // 1. Wrong current password → inline field error on current_password
  // -------------------------------------------------------------------------

  it("wrong current password (401 AUTH_INVALID_CREDENTIALS) → inline error on current_password field", async () => {
    changePasswordMock.mockRejectedValueOnce(
      new ApiError({
        code: "AUTH_INVALID_CREDENTIALS",
        message: "Mật khẩu hiện tại không đúng",
        status: 401,
      }),
    );

    await renderCard();

    fillAndSubmit("WrongCurrent1", "NewPassword1", "NewPassword1");

    // Inline error under the current_password field should appear.
    await waitFor(() => {
      expect(
        screen.getByText(/mật khẩu hiện tại không đúng/i),
      ).toBeInTheDocument();
    });

    // No success banner (role="status"), no navigation.
    expect(querySuccessBanner()).not.toBeInTheDocument();
    expect(mockPush).not.toHaveBeenCalled();
    expect(logoutMock).not.toHaveBeenCalled();
  });

  // -------------------------------------------------------------------------
  // 2. Success → banner → logout → redirect
  // -------------------------------------------------------------------------

  it("success → shows success banner → calls logout() → redirects to /?session=changed-password", async () => {
    changePasswordMock.mockResolvedValueOnce(undefined);

    await renderCard();

    // Switch to fake timers BEFORE submitting so the setTimeout(1500ms)
    // inside onSubmit is captured by the fake scheduler.
    vi.useFakeTimers({ shouldAdvanceTime: true });

    fillAndSubmit("CurrentPass1", "NewPassword1", "NewPassword1");

    // Success banner (role="status") should appear after the API call resolves.
    // Use real-time waitFor by temporarily restoring real timers for the poll.
    await act(async () => {
      // Flush all pending microtasks (the changePassword promise resolution).
      await Promise.resolve();
    });

    // The banner should now be visible.
    await waitFor(() => {
      expect(querySuccessBanner()).toBeInTheDocument();
    });

    // Advance past the 1500ms delay to trigger logout + redirect.
    await act(async () => {
      vi.advanceTimersByTime(2000);
    });

    // Restore real timers so waitFor works normally.
    vi.useRealTimers();

    await waitFor(() => {
      expect(logoutMock).toHaveBeenCalledTimes(1);
    });

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/?session=changed-password");
    });
  }, 10000);

  // -------------------------------------------------------------------------
  // 3. Validation: empty fields → inline validation errors shown
  // -------------------------------------------------------------------------

  it("empty fields → inline validation errors shown, no API call made", async () => {
    await renderCard();

    // Submit without filling any fields.
    const submitButton = screen.getByRole("button", { name: /^đổi mật khẩu$/i });
    fireEvent.click(submitButton);

    // Inline validation errors should appear for required fields.
    await waitFor(() => {
      expect(
        screen.getByText(/vui lòng nhập mật khẩu hiện tại/i),
      ).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(
        screen.getByText(/mật khẩu phải có ít nhất 8 ký tự/i),
      ).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(
        screen.getByText(/vui lòng xác nhận mật khẩu mới/i),
      ).toBeInTheDocument();
    });

    // No API call should have been made.
    expect(changePasswordMock).not.toHaveBeenCalled();
    expect(mockPush).not.toHaveBeenCalled();
  });

  // -------------------------------------------------------------------------
  // 4. Confirm password mismatch → inline error on confirm field
  // -------------------------------------------------------------------------

  it("confirm password mismatch → inline error on confirm_password field", async () => {
    await renderCard();

    fillAndSubmit("CurrentPass1", "NewPassword1", "DifferentPass1");

    // Inline error on the confirm field should appear.
    await waitFor(() => {
      expect(
        screen.getByText(/mật khẩu xác nhận không khớp/i),
      ).toBeInTheDocument();
    });

    // No API call should have been made.
    expect(changePasswordMock).not.toHaveBeenCalled();
    expect(mockPush).not.toHaveBeenCalled();
  });

  // -------------------------------------------------------------------------
  // 5. Other API error → inline alert banner (not field error)
  // -------------------------------------------------------------------------

  it("other API error (non-401) → inline alert banner shown", async () => {
    changePasswordMock.mockRejectedValueOnce(
      new ApiError({
        code: "INTERNAL_SERVER_ERROR",
        message: "Hệ thống đang bận, vui lòng thử lại sau",
        status: 500,
      }),
    );

    await renderCard();

    fillAndSubmit("CurrentPass1", "NewPassword1", "NewPassword1");

    // Generic error banner should appear (role="alert").
    await waitFor(() => {
      expect(
        screen.getByText(/hệ thống đang bận, vui lòng thử lại sau/i),
      ).toBeInTheDocument();
    });

    // No success banner (role="status"), no navigation.
    expect(querySuccessBanner()).not.toBeInTheDocument();
    expect(mockPush).not.toHaveBeenCalled();
    expect(logoutMock).not.toHaveBeenCalled();
  });

  // -------------------------------------------------------------------------
  // 6. Submit button disabled while request is in flight
  // -------------------------------------------------------------------------

  it("submit button is disabled while request is in flight", async () => {
    let resolveChange!: () => void;
    const changePromise = new Promise<void>((resolve) => {
      resolveChange = resolve;
    });

    changePasswordMock.mockImplementationOnce(() => changePromise);

    await renderCard();

    fireEvent.change(screen.getByLabelText(/mật khẩu hiện tại/i), {
      target: { value: "CurrentPass1" },
    });
    fireEvent.change(document.getElementById("change-new-password")!, {
      target: { value: "NewPassword1" },
    });
    fireEvent.change(document.getElementById("change-confirm-password")!, {
      target: { value: "NewPassword1" },
    });

    const submitButton = screen.getByRole("button", { name: /^đổi mật khẩu$/i });
    fireEvent.click(submitButton);

    // Button should be disabled while the request is in flight.
    await waitFor(() => {
      expect(submitButton).toBeDisabled();
    });

    // Resolve the request.
    await act(async () => {
      resolveChange();
    });

    // Success banner (role="status") should appear.
    await waitFor(() => {
      expect(querySuccessBanner()).toBeInTheDocument();
    });
  });
});
