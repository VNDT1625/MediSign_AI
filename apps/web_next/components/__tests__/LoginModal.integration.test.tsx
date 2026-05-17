/**
 * Integration tests for `LoginModal` — wired auth flows.
 *
 * Validates: Requirements 2.1.1 (register), 2.1.2 (login), 2.4.1 (error UX).
 *
 * Scenarios covered:
 *   1. Happy path — email login → success → intent consumed → router.push
 *   2. Happy path — phone login → success
 *   3. 401 error → inline field error shown (not toast/banner)
 *   4. 409/422 duplicate → inline field error on identifier field
 *   5. Network failure → banner error message shown with retry option
 *
 * Strategy:
 *   - Render `LoginModal` inside `AuthProvider` so the real auth state
 *     machine is exercised end-to-end.
 *   - Mock `next/navigation` (useRouter, useSearchParams) to capture
 *     navigation calls without a real Next.js runtime.
 *   - Mock `lib/api/auth` directly (same pattern as AuthProvider.test.tsx)
 *     to control login responses without MSW URL matching complexity.
 *   - Mock `refreshOnce` from the fetcher so the AuthProvider's mount-time
 *     hydration resolves immediately to `anonymous`.
 *   - Trigger the `videoEnded` state by firing the video element's `ended`
 *     event so the form surface becomes visible and interactive.
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor, fireEvent, act } from "@testing-library/react";

// ---------------------------------------------------------------------------
// Mock next/navigation — must be hoisted before any component imports
// ---------------------------------------------------------------------------

const mockPush = vi.fn();
const mockSearchParams = new URLSearchParams();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush, replace: vi.fn(), prefetch: vi.fn() }),
  useSearchParams: () => mockSearchParams,
  usePathname: () => "/",
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
// Mock lib/api/auth to control login responses without MSW URL matching
// ---------------------------------------------------------------------------

vi.mock("../../lib/api/auth", async () => {
  const actual = await vi.importActual<typeof import("../../lib/api/auth")>(
    "../../lib/api/auth",
  );
  return {
    ...actual,
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(() => Promise.resolve()),
    me: vi.fn(() => Promise.reject(new Error("me not stubbed"))),
  };
});

// ---------------------------------------------------------------------------
// Component imports (after mocks)
// ---------------------------------------------------------------------------

import { AuthProvider } from "../../lib/auth/AuthProvider";
import { LoginModal } from "../LoginModal";
import * as authApi from "../../lib/api/auth";
import { ApiError } from "../../lib/api/errors";
import { buildAuthUserResponse } from "../../test/msw/handlers";

const loginMock = authApi.login as ReturnType<typeof vi.fn>;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Successful login proxy response shape (see `LoginProxyResponse`). */
function buildLoginProxyResponse(overrides: Record<string, unknown> = {}) {
  return {
    user: buildAuthUserResponse(),
    access_token: "test-access-token",
    expires_in: 3600,
    ...overrides,
  };
}

/**
 * Render the modal inside AuthProvider and wait for it to settle.
 * Returns the `onClose` spy.
 */
async function renderModal(props: {
  open?: boolean;
  prefilledMessage?: string;
} = {}) {
  const onClose = vi.fn();
  const { open = true, prefilledMessage } = props;

  render(
    <AuthProvider>
      <LoginModal open={open} onClose={onClose} prefilledMessage={prefilledMessage} />
    </AuthProvider>,
  );

  // Wait for the dialog to be in the DOM.
  await waitFor(() => {
    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });

  return { onClose };
}

/**
 * Trigger the video `ended` event so the form surface fades in and
 * becomes interactive. The modal renders the form only after `videoEnded`
 * is true (opacity-100 + pointer-events-auto).
 */
function triggerVideoEnded() {
  const video = document.querySelector("video");
  if (video) {
    fireEvent(video, new Event("ended"));
  }
}

/**
 * Fill and submit the login form with the given identifier and password.
 *
 * Note: We query the password input by placeholder text because
 * `getByLabelText(/mật khẩu/i)` also matches the "Hiện mật khẩu" toggle button.
 * We query the submit button by type="submit" to avoid matching the tab switcher.
 */
function fillAndSubmitLoginForm(identifier: string, password: string) {
  const identifierInput = screen.getByLabelText(/email hoặc số điện thoại/i);
  const passwordInput = screen.getByPlaceholderText("••••••••");

  fireEvent.change(identifierInput, { target: { value: identifier } });
  fireEvent.change(passwordInput, { target: { value: password } });

  const submitButton = document.querySelector('button[type="submit"]') as HTMLButtonElement;
  fireEvent.click(submitButton);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("LoginModal — integration flows", () => {
  beforeEach(() => {
    mockPush.mockReset();
    loginMock.mockReset();
    // Clear sessionStorage between tests so intent state doesn't leak.
    if (typeof window !== "undefined") {
      window.sessionStorage.clear();
    }
  });

  // -------------------------------------------------------------------------
  // 1. Happy path — email login
  // -------------------------------------------------------------------------

  it("happy path: email login → success → router.push to /app/chat", async () => {
    loginMock.mockResolvedValueOnce(buildLoginProxyResponse());

    const { onClose } = await renderModal();
    triggerVideoEnded();

    fillAndSubmitLoginForm("user@example.com", "Password1");

    // After success: modal closes and router navigates.
    await waitFor(() => {
      expect(onClose).toHaveBeenCalledTimes(1);
    });

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledTimes(1);
    });

    // No intent set → fallback to /app/chat.
    expect(mockPush).toHaveBeenCalledWith("/app/chat");
  });

  // -------------------------------------------------------------------------
  // 2. Happy path — phone login
  // -------------------------------------------------------------------------

  it("happy path: phone login → success → router.push to /app/chat", async () => {
    loginMock.mockResolvedValueOnce(buildLoginProxyResponse());

    const { onClose } = await renderModal();
    triggerVideoEnded();

    // Vietnamese phone number format
    fillAndSubmitLoginForm("0901234567", "Password1");

    await waitFor(() => {
      expect(onClose).toHaveBeenCalledTimes(1);
    });

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledTimes(1);
    });

    expect(mockPush).toHaveBeenCalledWith("/app/chat");
  });

  // -------------------------------------------------------------------------
  // 3. 401 error → inline field error (not banner)
  // -------------------------------------------------------------------------

  it("401 invalid credentials → inline password error, no generic banner", async () => {
    loginMock.mockRejectedValueOnce(
      new ApiError({
        code: "AUTH_INVALID_CREDENTIALS",
        message: "Email/SĐT hoặc mật khẩu không đúng",
        status: 401,
      }),
    );

    await renderModal();
    triggerVideoEnded();

    fillAndSubmitLoginForm("user@example.com", "WrongPass1");

    // Inline error under the password field should appear.
    await waitFor(() => {
      expect(
        screen.getByText(/email\/sđt hoặc mật khẩu không đúng/i),
      ).toBeInTheDocument();
    });

    // Generic server/network banner messages should NOT be shown.
    expect(screen.queryByText(/hệ thống đang bận/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/mất kết nối/i)).not.toBeInTheDocument();

    // Modal stays open — no navigation.
    expect(mockPush).not.toHaveBeenCalled();
  });

  // -------------------------------------------------------------------------
  // 4. 422 validation error with duplicate email → inline identifier error
  // -------------------------------------------------------------------------

  it("422 VALIDATION_ERROR with email field → inline identifier error shown", async () => {
    // The login modal maps VALIDATION_ERROR with email field to the
    // identifier input (since the form has one merged identifier field).
    loginMock.mockRejectedValueOnce(
      new ApiError({
        code: "VALIDATION_ERROR",
        message: "Dữ liệu không hợp lệ",
        status: 422,
        details: {
          errors: [
            {
              loc: ["body", "email"],
              msg: "Email này đã được sử dụng",
              type: "value_error",
            },
          ],
        },
      }),
    );

    await renderModal();
    triggerVideoEnded();

    fillAndSubmitLoginForm("duplicate@example.com", "Password1");

    // The identifier field should show the email error.
    await waitFor(() => {
      expect(
        screen.getByText(/email này đã được sử dụng/i),
      ).toBeInTheDocument();
    });

    expect(mockPush).not.toHaveBeenCalled();
  });

  // -------------------------------------------------------------------------
  // 5. Network failure → banner error message shown
  // -------------------------------------------------------------------------

  it("network failure → banner error message shown", async () => {
    loginMock.mockRejectedValueOnce(
      new ApiError({
        code: "NETWORK_ERROR",
        message: "Mất kết nối. Kiểm tra mạng và thử lại.",
        status: 0,
      }),
    );

    await renderModal();
    triggerVideoEnded();

    fillAndSubmitLoginForm("user@example.com", "Password1");

    // The top-of-form banner should show the network error message.
    await waitFor(() => {
      expect(screen.getByText(/mất kết nối/i)).toBeInTheDocument();
    });

    // Modal stays open — no navigation.
    expect(mockPush).not.toHaveBeenCalled();
  });

  // -------------------------------------------------------------------------
  // 6. Network failure → retry by resubmitting the form
  // -------------------------------------------------------------------------

  it("network failure → user can retry by resubmitting", async () => {
    // First call: network error; second call: success.
    loginMock
      .mockRejectedValueOnce(
        new ApiError({
          code: "NETWORK_ERROR",
          message: "Mất kết nối. Kiểm tra mạng và thử lại.",
          status: 0,
        }),
      )
      .mockResolvedValueOnce(buildLoginProxyResponse());

    const { onClose } = await renderModal();
    triggerVideoEnded();

    const identifierInput = screen.getByLabelText(/email hoặc số điện thoại/i);
    const passwordInput = screen.getByPlaceholderText("••••••••");
    const submitButton = document.querySelector('button[type="submit"]') as HTMLButtonElement;

    fireEvent.change(identifierInput, { target: { value: "user@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "Password1" } });
    fireEvent.click(submitButton);

    // First attempt: network error banner appears.
    await waitFor(() => {
      expect(screen.getByText(/mất kết nối/i)).toBeInTheDocument();
    });

    // Retry: click submit again (form values are preserved).
    fireEvent.click(submitButton);

    // Second attempt: success → modal closes.
    await waitFor(() => {
      expect(onClose).toHaveBeenCalledTimes(1);
    });

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/app/chat");
    });

    expect(loginMock).toHaveBeenCalledTimes(2);
  });

  // -------------------------------------------------------------------------
  // 7. Intent consumed on success
  // -------------------------------------------------------------------------

  it("intent from sessionStorage is consumed and used for redirect", async () => {
    loginMock.mockResolvedValueOnce(buildLoginProxyResponse());

    // Set an intent in sessionStorage before rendering.
    const intentParams = new URLSearchParams();
    intentParams.set("intent", "/app/medicine");
    window.sessionStorage.setItem("medisign:intent", intentParams.toString());

    const { onClose } = await renderModal();
    triggerVideoEnded();

    fillAndSubmitLoginForm("user@example.com", "Password1");

    await waitFor(() => {
      expect(onClose).toHaveBeenCalledTimes(1);
    });

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/app/medicine");
    });
  });

  // -------------------------------------------------------------------------
  // 8. Submit button disabled while pending
  // -------------------------------------------------------------------------

  it("submit button is disabled while request is in flight", async () => {
    // Use a delayed response to observe the pending state.
    let resolveLogin!: (value: unknown) => void;
    const loginPromise = new Promise((resolve) => {
      resolveLogin = resolve;
    });

    loginMock.mockImplementationOnce(() => loginPromise);

    await renderModal();
    triggerVideoEnded();

    const identifierInput = screen.getByLabelText(/email hoặc số điện thoại/i);
    const passwordInput = screen.getByPlaceholderText("••••••••");
    const submitButton = document.querySelector('button[type="submit"]') as HTMLButtonElement;

    fireEvent.change(identifierInput, { target: { value: "user@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "Password1" } });

    // Click submit — the request is now in flight.
    fireEvent.click(submitButton);

    // The button should be disabled while pending.
    await waitFor(() => {
      expect(submitButton).toBeDisabled();
    });

    // Resolve the login and let the modal close.
    await act(async () => {
      resolveLogin(buildLoginProxyResponse());
    });

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalled();
    });
  });
});
