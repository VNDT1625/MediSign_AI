"use client";

/**
 * LoginModal — wired entry point for authentication flows.
 *
 * Phase-1 wiring (task 8.3 of the web-app-functional-integration spec):
 *
 * 1. Mounts one of three sub-forms based on the current mode tab —
 *    `LoginForm`, `RegisterForm`, or `ForgotForm` — each owning its own
 *    react-hook-form / zod schema (`lib/validation/auth.ts`).
 * 2. On a successful login the access token is written to `tokenStore` by
 *    `useAuth().login()`. The modal then asks `useIntent().consume()` for
 *    the redirect path (Requirements 2.1.4 — "smart redirect"), routes via
 *    `next/navigation` `useRouter`, and closes itself.
 * 3. Register chains into login because the FastAPI `/auth/register`
 *    response cannot be persisted as a `medisign_rt` cookie (Phase 1 has
 *    no register proxy — see `lib/api/auth.ts`). After `useAuth().register`
 *    we immediately call `useAuth().login` with the same email + password
 *    to seed the cookie and transition the auth state machine.
 * 4. Forgot password is intentionally inert — `ForgotForm` keeps its
 *    submit button disabled because the backend route ships in Phase 2
 *    (see Requirements 2.1.3).
 * 5. The submit button stays disabled while a request is in flight to
 *    prevent double submits (Requirements 2.1.6 — single-flight). On top
 *    of that, a sliding-window client rate-limiter (5 failed login
 *    attempts inside 60s) locks the submit button per Requirements 3.1.
 * 6. `ApiError.code` is mapped to inline field errors per the table in
 *    `design.md` → "Mapping `code` → UX". Codes the form can't surface
 *    inline (network/timeout, generic 5xx) fall back to a top-of-form
 *    banner that includes `request_id` so support can correlate logs.
 *
 * The cinematic video intro and crossfade UX from the original mock are
 * preserved verbatim — the only changes here are wiring + a few a11y
 * polish items called out in the Pre-Delivery Checklist.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import type {
  LoginInput,
  RegisterInput,
} from "@medisign/shared-contracts";

import { ForgotForm } from "@/components/auth/ForgotForm";
import {
  LoginForm,
  type LoginFormServerErrors,
} from "@/components/auth/LoginForm";
import {
  RegisterForm,
  type RegisterFormServerErrors,
} from "@/components/auth/RegisterForm";
import { ApiError } from "@/lib/api/errors";
import * as authApi from "@/lib/api/auth";
import { useAuth } from "@/lib/auth/useAuth";
import { useIntent } from "@/lib/auth/useIntent";
import { classifyIdentifier } from "@/lib/utils/classifyIdentifier";
import type { LoginFormValues, RegisterFormValues, ForgotFormValues } from "@/lib/validation/auth";

const LOGIN_VIDEO =
  "https://pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev/kling_20260516_%E4%BD%9C%E5%93%81_The_camera_4212_0%20(1).mp4";

const FADE_MS = 600;

/** Number of failed login attempts within the window that triggers lockout. */
const RATE_LIMIT_THRESHOLD = 5;
/** Sliding window length (ms) for the failed-login counter. */
const RATE_LIMIT_WINDOW_MS = 60_000;

type Mode = "login" | "register" | "forgot";

interface BannerState {
  message: string;
  requestId?: string;
}

/**
 * vi-VN message used for `AUTH_INVALID_CREDENTIALS` — design.md mandates we
 * deliberately do NOT reveal which of {identifier, password} is wrong, so
 * the same string is surfaced under the password field whether the user
 * fat-fingered the email or the password.
 */
const INVALID_CREDENTIALS_MESSAGE =
  "Email/SĐT hoặc mật khẩu không đúng";

const NETWORK_BANNER_MESSAGE = "Mất kết nối. Kiểm tra mạng và thử lại.";
const TIMEOUT_BANNER_MESSAGE =
  "Yêu cầu hết thời gian chờ. Vui lòng thử lại.";
const SERVER_BANNER_MESSAGE =
  "Hệ thống đang bận, vui lòng thử lại sau.";
const VALIDATION_FALLBACK_MESSAGE = "Dữ liệu không hợp lệ";

/**
 * Map zod-style backend validation errors (from FastAPI `RequestValidationError`)
 * onto sub-form field names. The backend emits each entry as
 * `{ loc: ["body", "<field>"], msg, type }`; we read the last segment of `loc`
 * because the first one is always the body marker.
 *
 * Returns an object keyed by the *form* field name. Caller decides which
 * sub-form's setter to feed it into.
 */
function extractValidationFieldErrors(
  err: ApiError,
): Record<string, string> {
  const details = err.details;
  if (!details || typeof details !== "object") return {};
  const errors = (details as { errors?: unknown }).errors;
  if (!Array.isArray(errors)) return {};

  const out: Record<string, string> = {};
  for (const entry of errors) {
    if (!entry || typeof entry !== "object") continue;
    const loc = (entry as { loc?: unknown }).loc;
    const msg = (entry as { msg?: unknown }).msg;
    if (!Array.isArray(loc) || loc.length === 0) continue;
    if (typeof msg !== "string" || msg.length === 0) continue;
    const field = loc[loc.length - 1];
    if (typeof field !== "string" || field.length === 0) continue;
    // First error per field wins — matches what the user sees as "the"
    // problem on that input.
    if (!(field in out)) {
      out[field] = msg;
    }
  }
  return out;
}

export function LoginModal({
  open,
  onClose,
  prefilledMessage,
}: {
  open: boolean;
  onClose: () => void;
  prefilledMessage?: string;
}) {
  const router = useRouter();
  const { login, register } = useAuth();
  const { consume } = useIntent();

  const [mode, setMode] = useState<Mode>("login");
  const [videoEnded, setVideoEnded] = useState(false);
  const [closing, setClosing] = useState(false);
  const [pending, setPending] = useState(false);

  // Per-sub-form server error maps. Always assign a fresh object so the
  // sub-form's effect re-runs and the previous mapping is cleared.
  const [loginServerErrors, setLoginServerErrors] =
    useState<LoginFormServerErrors>({});
  const [registerServerErrors, setRegisterServerErrors] =
    useState<RegisterFormServerErrors>({});
  const [forgotServerError, setForgotServerError] = useState<string | undefined>(undefined);

  // Top-of-form banner for errors that don't belong to a single field
  // (network failures, timeouts, generic 5xx). `request_id` is rendered
  // small-and-muted so support can correlate without dominating the UI.
  const [banner, setBanner] = useState<BannerState | null>(null);

  // Sliding-window timestamps of recent failed login attempts. Stored as
  // `Date.now()` numbers — a function-local ref would also work but
  // keeping it in state lets the rate-limit countdown re-render naturally
  // every time we tick the timer below.
  const [failedAttempts, setFailedAttempts] = useState<number[]>([]);
  // `now` is a ticking value used purely to recompute the rate-limit
  // countdown each second while the user is locked out.
  const [now, setNow] = useState<number>(() => Date.now());

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const closeBtnRef = useRef<HTMLButtonElement | null>(null);
  // Container for the focus trap — points at the outer dialog div so the
  // Tab cycle is bounded by the modal surface (header controls + form).
  const dialogRef = useRef<HTMLDivElement | null>(null);

  // ---------------------------------------------------------------------
  // Rate-limit derived state
  // ---------------------------------------------------------------------

  const recentAttempts = useMemo(
    () =>
      failedAttempts.filter((t) => now - t < RATE_LIMIT_WINDOW_MS),
    [failedAttempts, now],
  );

  const isRateLimited = recentAttempts.length >= RATE_LIMIT_THRESHOLD;
  const rateLimitSecondsLeft = isRateLimited
    ? Math.max(
        1,
        Math.ceil(
          (RATE_LIMIT_WINDOW_MS - (now - recentAttempts[0])) / 1000,
        ),
      )
    : 0;

  // Tick once per second only while the lockout banner is showing — no
  // global timer leaks into the rest of the app.
  useEffect(() => {
    if (!isRateLimited || !open) return;
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, [isRateLimited, open]);

  // ---------------------------------------------------------------------
  // Modal open/close lifecycle (preserved from the original mock)
  // ---------------------------------------------------------------------

  const handleRequestClose = useCallback(() => {
    if (closing || pending) return;
    setClosing(true);
    setVideoEnded(false);
    const v = videoRef.current;
    try {
      v?.pause();
    } catch {
      /* ignore */
    }
    onClose();
  }, [closing, pending, onClose]);

  // Reset transient state every time the modal toggles open. We deliberately
  // do NOT clear `failedAttempts` on close — the rate-limit must survive
  // closing/reopening the modal within the same tab, otherwise the lockout
  // is trivially bypassable.
  useEffect(() => {
    const v = videoRef.current;
    if (open) {
      setVideoEnded(false);
      setClosing(false);
      setMode("login");
      setLoginServerErrors({});
      setRegisterServerErrors({});
      setForgotServerError(undefined);
      setBanner(null);
      setNow(Date.now());
      if (v) {
        try {
          v.currentTime = 0;
          const p = v.play();
          if (p && typeof p.catch === "function") p.catch(() => {});
        } catch {
          /* ignore */
        }
      }
    } else if (v) {
      try {
        v.pause();
        v.currentTime = 0;
      } catch {
        /* ignore */
      }
    }
  }, [open]);

  // ESC + scroll lock + initial focus + Tab focus trap.
  useEffect(() => {
    if (!open) return;

    /**
     * Collects every focusable descendant inside the dialog at the moment
     * a Tab is pressed. We re-query each keystroke instead of caching so
     * the trap stays correct as the visible mode swaps (login ↔ register
     * ↔ forgot) — different sub-forms expose different inputs.
     *
     * The selector covers anchor links, buttons, inputs, textareas,
     * selects, and anything explicitly opted-in via `tabIndex`. Disabled
     * controls and `tabIndex="-1"` are excluded so the cycle skips them.
     */
    const getFocusable = (): HTMLElement[] => {
      const root = dialogRef.current;
      if (!root) return [];
      const selector =
        'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
      return Array.from(root.querySelectorAll<HTMLElement>(selector)).filter(
        // Hidden via `display:none` / `visibility:hidden` produces a zero
        // bounding rect — skip those so the trap doesn't cycle into the
        // backdrop button (which we explicitly mark `tabIndex={-1}` already)
        // or into form fields that haven't faded in yet.
        (el) =>
          el.offsetWidth > 0 || el.offsetHeight > 0 || el === document.activeElement,
      );
    };

    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        handleRequestClose();
        return;
      }
      if (e.key !== "Tab") return;

      const focusable = getFocusable();
      if (focusable.length === 0) {
        e.preventDefault();
        return;
      }
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      const active = document.activeElement as HTMLElement | null;

      // Wrap the cycle. If focus has somehow escaped the dialog (e.g. the
      // user clicked outside via assistive tech), pull it back to the
      // first/last element on the next Tab.
      const insideDialog =
        !!active && !!dialogRef.current && dialogRef.current.contains(active);

      if (e.shiftKey) {
        if (!insideDialog || active === first) {
          e.preventDefault();
          last.focus();
        }
      } else {
        if (!insideDialog || active === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };
    window.addEventListener("keydown", onKey);

    const scrollbarWidth =
      window.innerWidth - document.documentElement.clientWidth;
    const prevOverflow = document.body.style.overflow;
    const prevPaddingRight = document.body.style.paddingRight;
    document.body.style.overflow = "hidden";
    if (scrollbarWidth > 0) {
      document.body.style.paddingRight = `${scrollbarWidth}px`;
    }

    closeBtnRef.current?.focus();
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prevOverflow;
      document.body.style.paddingRight = prevPaddingRight;
    };
  }, [open, handleRequestClose]);

  function skipIntro() {
    const v = videoRef.current;
    if (!v) {
      setVideoEnded(true);
      return;
    }
    try {
      v.currentTime = Math.max(0, (v.duration || 0) - 0.05);
    } catch {
      /* ignore */
    }
    setVideoEnded(true);
  }

  // ---------------------------------------------------------------------
  // Error → UX mapping (per design.md "Mapping `code` → UX" table)
  // ---------------------------------------------------------------------

  const handleLoginError = useCallback(
    (err: unknown) => {
      // Always surface a usable error: anything that's not an `ApiError`
      // (programmer error, DOMException, etc.) collapses to the generic
      // server banner so the user is never stuck without feedback.
      if (!(err instanceof ApiError)) {
        setBanner({ message: SERVER_BANNER_MESSAGE });
        return;
      }

      switch (err.code) {
        case "AUTH_INVALID_CREDENTIALS":
          setLoginServerErrors({
            password: INVALID_CREDENTIALS_MESSAGE,
          });
          break;

        case "VALIDATION_ERROR": {
          const fieldErrors = extractValidationFieldErrors(err);
          // Map known backend field names onto the form's `identifier`
          // input (since the form has one merged field instead of email
          // + phone). Any unmapped fields fall through to the banner.
          const next: LoginFormServerErrors = {};
          if (fieldErrors.email) next.identifier = fieldErrors.email;
          else if (fieldErrors.phone) next.identifier = fieldErrors.phone;
          if (fieldErrors.password) next.password = fieldErrors.password;
          if (Object.keys(next).length > 0) {
            setLoginServerErrors(next);
          } else {
            setBanner({
              message: err.message || VALIDATION_FALLBACK_MESSAGE,
              requestId: err.requestId,
            });
          }
          break;
        }

        case "NETWORK_ERROR":
          setBanner({ message: NETWORK_BANNER_MESSAGE });
          break;

        case "TIMEOUT_ERROR":
          setBanner({
            message: TIMEOUT_BANNER_MESSAGE,
            requestId: err.requestId,
          });
          break;

        default:
          setBanner({
            message:
              err.status >= 500
                ? SERVER_BANNER_MESSAGE
                : err.message || SERVER_BANNER_MESSAGE,
            requestId: err.requestId,
          });
      }
    },
    [],
  );

  const handleRegisterError = useCallback(
    (err: unknown, attemptedEmail?: string) => {
      if (!(err instanceof ApiError)) {
        setBanner({ message: SERVER_BANNER_MESSAGE });
        return;
      }

      switch (err.code) {
        // Backend (`auth_service.py`) emits the `_EXISTS` variants today;
        // the design.md table standardised on `_TAKEN`. Accept both so the
        // mapping survives a future backend rename without UI churn.
        case "AUTH_EMAIL_EXISTS":
        case "AUTH_EMAIL_TAKEN":
          setRegisterServerErrors({
            email: "Email này đã được sử dụng",
          });
          break;

        case "AUTH_PHONE_EXISTS":
        case "AUTH_PHONE_TAKEN":
          setRegisterServerErrors({
            phone: "Số điện thoại này đã được sử dụng",
          });
          break;

        case "AUTH_USERNAME_EXISTS":
        case "AUTH_USERNAME_TAKEN":
          setRegisterServerErrors({
            username: "Tên đăng nhập này đã được sử dụng",
          });
          break;

        case "VALIDATION_ERROR": {
          const fieldErrors = extractValidationFieldErrors(err);
          const next: RegisterFormServerErrors = {};
          (
            [
              "full_name",
              "username",
              "email",
              "phone",
              "password",
            ] as const
          ).forEach((field) => {
            if (fieldErrors[field]) next[field] = fieldErrors[field];
          });
          if (Object.keys(next).length > 0) {
            setRegisterServerErrors(next);
          } else {
            setBanner({
              message: err.message || VALIDATION_FALLBACK_MESSAGE,
              requestId: err.requestId,
            });
          }
          break;
        }

        case "NETWORK_ERROR":
          setBanner({ message: NETWORK_BANNER_MESSAGE });
          break;

        case "TIMEOUT_ERROR":
          setBanner({
            message: TIMEOUT_BANNER_MESSAGE,
            requestId: err.requestId,
          });
          break;

        default:
          setBanner({
            message:
              err.status >= 500
                ? SERVER_BANNER_MESSAGE
                : err.message || SERVER_BANNER_MESSAGE,
            requestId: err.requestId,
          });
      }
      // `attemptedEmail` is reserved for future analytics — referenced
      // here only so the unused-parameter lint stays satisfied without
      // changing the public signature.
      void attemptedEmail;
    },
    [],
  );

  // ---------------------------------------------------------------------
  // Post-success routing
  // ---------------------------------------------------------------------

  const handleAuthSuccess = useCallback(() => {
    const { redirectPath } = consume();
    setPending(false);
    onClose();
    // Defer navigation until the close transition kicks off so the
    // `/app/...` shell isn't paint-blocked by the modal's exit fade.
    router.push(redirectPath);
  }, [consume, onClose, router]);

  // ---------------------------------------------------------------------
  // Submit handlers
  // ---------------------------------------------------------------------

  const onLoginSubmit = useCallback(
    async (values: LoginFormValues) => {
      // Defensive: the form button is also disabled when locked, but a
      // savvy user could re-enable it via devtools. Keep the guard.
      if (isRateLimited || pending) return;

      setPending(true);
      setBanner(null);
      setLoginServerErrors({});

      const identifier = values.identifier.trim();
      const kind = classifyIdentifier(identifier);
      const credentials: LoginInput =
        kind === "email"
          ? { email: identifier, password: values.password }
          : kind === "phone"
            ? { phone: identifier, password: values.password }
            : // Should be unreachable — `loginSchema.refine` already rejects
              // anything that isn't email or phone — but mirror the
              // server's expected shape so the request fails fast on the
              // backend instead of the client throwing.
              { email: identifier, password: values.password };

      try {
        await login(credentials);
        // Success → reset the failed-attempts counter so a future bad
        // session doesn't inherit prior failures.
        setFailedAttempts([]);
        handleAuthSuccess();
      } catch (err) {
        // Only `AUTH_INVALID_CREDENTIALS` should count toward the
        // rate-limit; counting validation / network errors would punish
        // the user for the network's flakiness, not their guesses.
        if (err instanceof ApiError && err.code === "AUTH_INVALID_CREDENTIALS") {
          setFailedAttempts((prev) => {
            const cutoff = Date.now() - RATE_LIMIT_WINDOW_MS;
            return [...prev.filter((t) => t > cutoff), Date.now()];
          });
        }
        handleLoginError(err);
        setPending(false);
      }
    },
    [isRateLimited, pending, login, handleAuthSuccess, handleLoginError],
  );

  const onRegisterSubmit = useCallback(
    async (values: RegisterFormValues) => {
      if (pending) return;

      setPending(true);
      setBanner(null);
      setRegisterServerErrors({});

      const payload: RegisterInput = {
        email: values.email.trim(),
        phone: values.phone.trim(),
        username: values.username.trim(),
        full_name: values.full_name.trim(),
        password: values.password,
      };

      try {
        await register(payload);
      } catch (err) {
        handleRegisterError(err, payload.email);
        setPending(false);
        return;
      }

      // Account exists — chain into login so the `medisign_rt` cookie
      // gets seeded by the proxy and the auth state machine flips to
      // `authenticated`. We use the same email + password the user just
      // typed; the backend will not reject duplicate logins because we
      // just successfully created the account.
      try {
        await login({ email: payload.email, password: payload.password });
        handleAuthSuccess();
      } catch (err) {
        // Edge case: account was created but auto-login fails (network
        // hiccup, race against rate-limiter on the backend, etc.). Drop
        // the user back to the login tab with the email pre-filled, so
        // they can retry without re-typing everything.
        handleLoginError(err);
        setMode("login");
        setPending(false);
      }
    },
    [
      pending,
      register,
      login,
      handleAuthSuccess,
      handleRegisterError,
      handleLoginError,
    ],
  );

  // ---------------------------------------------------------------------
  // Forgot password submit handler
  // ---------------------------------------------------------------------

  const onForgotSubmit = useCallback(
    async (values: ForgotFormValues) => {
      if (pending) return;
      setPending(true);
      setForgotServerError(undefined);
      try {
        await authApi.forgotPassword(values.email.trim());
        // ForgotForm tự chuyển sang trạng thái "đã gửi" sau khi promise resolve
      } catch (err) {
        // Chỉ hiện lỗi network/server — không lộ thông tin email có tồn tại không
        if (err instanceof ApiError) {
          if (err.code === "NETWORK_ERROR") {
            setForgotServerError("Mất kết nối. Kiểm tra mạng và thử lại.");
          } else if (err.code === "TIMEOUT_ERROR") {
            setForgotServerError("Yêu cầu hết thời gian chờ. Vui lòng thử lại.");
          } else {
            setForgotServerError("Hệ thống đang bận, vui lòng thử lại sau.");
          }
        } else {
          setForgotServerError("Hệ thống đang bận, vui lòng thử lại sau.");
        }
        // Ném lại để ForgotForm KHÔNG chuyển sang trạng thái "đã gửi"
        throw err;
      } finally {
        setPending(false);
      }
    },
    [pending],
  );

  // ---------------------------------------------------------------------
  // Banner / rate-limit clearance helpers passed to sub-forms
  // ---------------------------------------------------------------------

  const clearBanner = useCallback(() => {
    if (banner !== null) setBanner(null);
  }, [banner]);

  // ---------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------

  const submitLabelLogin = isRateLimited
    ? `Thử lại sau ${rateLimitSecondsLeft}s`
    : undefined;

  const titleByMode: Record<Mode, string> = {
    login: "Chào mừng quay lại",
    register: "Tạo tài khoản mới",
    forgot: "Khôi phục tài khoản",
  };

  const eyebrowByMode: Record<Mode, string> = {
    login: "Phiếu đăng ký",
    register: "Phiếu đăng ký",
    forgot: "Quên mật khẩu",
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="login-title"
      aria-hidden={!open}
      style={{ transitionDuration: `${FADE_MS}ms` }}
      className={`fixed inset-0 z-40 motion-safe:transition-opacity motion-safe:ease-out ${
        open ? "opacity-100" : "pointer-events-none opacity-0"
      }`}
    >
      {/* Backdrop video — preload="auto" + always mounted */}
      <button
        type="button"
        aria-label="Đóng"
        onClick={handleRequestClose}
        disabled={closing || pending}
        className="absolute inset-0 -z-10 cursor-default overflow-hidden bg-ink-900 focus:outline-none"
        tabIndex={-1}
      >
        <video
          ref={videoRef}
          src={LOGIN_VIDEO}
          muted
          playsInline
          preload="auto"
          aria-hidden="true"
          onEnded={() => setVideoEnded(true)}
          className="pointer-events-none h-full w-full object-cover"
        />
        <span
          aria-hidden="true"
          style={{ transitionDuration: `${FADE_MS}ms` }}
          className={`pointer-events-none absolute inset-0 motion-safe:transition-opacity ${
            videoEnded ? "bg-black/0" : "bg-black/10"
          }`}
        />
      </button>

      {/* Header controls */}
      <div className="absolute top-4 left-4 right-4 flex items-center justify-between gap-3 sm:top-6 sm:left-6 sm:right-6">
        <div className="min-h-[40px]">
          {!videoEnded && !closing && (
            <button
              type="button"
              onClick={skipIntro}
              className="cursor-pointer rounded-pill bg-white/90 px-4 py-2 text-sm font-medium text-ink-800 shadow-soft transition-colors duration-200 hover:bg-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2"
            >
              Bỏ qua intro
            </button>
          )}
        </div>

        <button
          ref={closeBtnRef}
          type="button"
          aria-label={closing ? "Đang quay về trang chủ" : "Quay về trang chủ"}
          title="Quay về trang chủ"
          onClick={handleRequestClose}
          disabled={closing || pending}
          className="grid h-10 w-10 cursor-pointer place-items-center rounded-pill bg-white/95 text-ink-800 shadow-soft transition-colors duration-200 hover:bg-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 disabled:cursor-wait disabled:opacity-70"
        >
          {closing ? (
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden="true"
              className="motion-safe:animate-spin"
            >
              <path
                d="M12 3a9 9 0 1 0 9 9"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          ) : (
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden="true"
            >
              <path
                d="M6 6l12 12M6 18L18 6"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          )}
        </button>
      </div>

      {/* "Đang chuẩn bị" caption while the video runs */}
      {!videoEnded && !closing && (
        <div className="pointer-events-none absolute bottom-10 left-1/2 -translate-x-1/2">
          <div className="flex items-center gap-2.5 rounded-pill bg-white/95 px-5 py-2.5 text-sm font-medium text-ink-800 shadow-card backdrop-blur">
            <span className="grid h-6 w-6 place-items-center rounded-full bg-brand text-white">
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                aria-hidden="true"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="9"
                  stroke="currentColor"
                  strokeWidth="2"
                />
                <path
                  d="M12 7v5l3 2"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
            </span>
            <span>Bác sĩ đang chuẩn bị phiếu đăng ký cho bạn...</span>
          </div>
        </div>
      )}

      {/* Form surface — fades in once the video ends */}
      <div
        className={`pointer-events-none absolute inset-0 grid place-items-center px-4 motion-safe:transition-opacity motion-safe:ease-out ${
          videoEnded ? "opacity-100" : "opacity-0"
        }`}
        style={{ transitionDuration: `${FADE_MS}ms` }}
        aria-hidden={!videoEnded}
      >
        <div className="relative w-full max-w-[340px] translate-y-[calc(18%+5px)] motion-safe:animate-fade-up">
          {/*
            Form surface intentionally fully transparent — sits directly on
            the clipboard area of the background video so the doctor avatar
            keeps reading as a single illustration. No bg / no shadow / no
            ring. Inputs and the submit button carry their own surface
            (white inputs + brand-colored CTA) so contrast is preserved
            even though the wrapper is invisible.
          */}
          <div
            className={`mt-[64px] px-4 py-4 ${
              videoEnded ? "pointer-events-auto" : "pointer-events-none"
            }`}
          >
            {/* Header */}
            <div className="mb-4 text-center">
              <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-blue-600">
                MediSign AI
              </p>
              <h2
                id="login-title"
                className="mt-1 text-[24px] font-extrabold leading-tight text-slate-900"
              >
                {titleByMode[mode]}
              </h2>
            </div>

            {/* Tab switcher — chỉ hiện khi không phải forgot */}
            {mode !== "forgot" && (
              <div className="mb-4 flex rounded-xl border border-slate-900/15 bg-slate-200/70 p-1 backdrop-blur-sm">
                <button
                  type="button"
                  onClick={() => { setMode("login"); setBanner(null); setLoginServerErrors({}); setRegisterServerErrors({}); }}
                  disabled={pending}
                  className={`flex-1 cursor-pointer rounded-lg py-2 text-[13px] font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
                    mode === "login"
                      ? "bg-white text-slate-900 shadow-sm"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  Đăng nhập
                </button>
                <button
                  type="button"
                  onClick={() => { setMode("register"); setBanner(null); setLoginServerErrors({}); setRegisterServerErrors({}); }}
                  disabled={pending}
                  className={`flex-1 cursor-pointer rounded-lg py-2 text-[13px] font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
                    mode === "register"
                      ? "bg-white text-slate-900 shadow-sm"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  Đăng ký
                </button>
              </div>
            )}

            {prefilledMessage && mode !== "forgot" && (
              <div className="mb-3 rounded-xl border border-blue-100 bg-blue-50/80 px-3 py-2 text-[12px] text-slate-700 backdrop-blur-sm">
                <strong className="font-semibold text-slate-900">
                  &quot;{prefilledMessage}&quot;
                </strong>
              </div>
            )}

            {/* Top-of-form error banner */}
            {banner && (
              <div
                role="alert"
                className="mb-3 flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-[13px] text-red-700"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true" className="mt-0.5 shrink-0">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
                  <path d="M12 8v4m0 4h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
                <span className="flex-1">
                  <span className="block font-semibold leading-snug">{banner.message}</span>
                  {banner.requestId && (
                    <span className="mt-0.5 block text-[11px] font-normal text-red-500">
                      Mã hỗ trợ: {banner.requestId}
                    </span>
                  )}
                </span>
              </div>
            )}

            {/* Rate-limit banner */}
            {mode === "login" && isRateLimited && (
              <div
                role="status"
                aria-live="polite"
                className="mb-3 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2.5 text-[13px] font-semibold text-amber-700"
              >
                Quá nhiều lần thử. Vui lòng thử lại sau {rateLimitSecondsLeft}s.
              </div>
            )}

            {mode === "login" && (
              <div className="mt-[5px]">
              <LoginForm
                onSubmit={onLoginSubmit}
                isPending={pending}
                rateLimited={isRateLimited}
                submitLabel={submitLabelLogin}
                serverErrors={loginServerErrors}
                onFieldChange={clearBanner}
              />
              </div>
            )}

            {mode === "register" && (
              <RegisterForm
                onSubmit={onRegisterSubmit}
                isPending={pending}
                serverErrors={registerServerErrors}
                onFieldChange={clearBanner}
              />
            )}

            {mode === "forgot" && (
              <ForgotForm
                onSubmit={onForgotSubmit}
                isPending={pending}
                serverError={forgotServerError}
                onBackToLogin={() => { setMode("login"); setBanner(null); setForgotServerError(undefined); }}
              />
            )}

            {/* Footer links */}
            <div className="mt-4 text-center text-[12px] text-slate-500">
              {mode === "login" && (
                <button
                  type="button"
                  onClick={() => { setMode("forgot"); setBanner(null); setLoginServerErrors({}); setForgotServerError(undefined); }}
                  className="cursor-pointer font-semibold text-blue-600 transition-colors hover:text-blue-800 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-1 rounded"
                  disabled={pending}
                >
                  Quên mật khẩu?
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
