"use client";

/**
 * `ChangePasswordCard` — profile page card for changing the user's password.
 *
 * Three fields: current password, new password, confirm new password.
 * Validation via `zod` matches the backend policy (min 8 chars, at least
 * 1 uppercase letter, at least 1 digit). Confirm field must match new password.
 *
 * On success:
 *   1. Show a success banner "Đổi mật khẩu thành công"
 *   2. Call `useAuth().logout()` (clears cookie + in-memory token)
 *   3. Redirect to `/?session=changed-password` (force re-login)
 *
 * On error:
 *   - Wrong current password (AUTH_INVALID_CREDENTIALS) → inline field error
 *   - Other API errors → inline alert banner (not toast)
 *
 * @see Requirements 2.3.3 (change password / force re-login)
 */

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { z } from "zod";

import { useAuth } from "@/lib/auth/useAuth";
import { ApiError } from "@/lib/api/errors";

// ---------------------------------------------------------------------------
// Zod schema
// ---------------------------------------------------------------------------

/**
 * Password policy mirrors the backend:
 *   - min 8 chars, max 128 chars
 *   - at least 1 uppercase letter
 *   - at least 1 digit
 *
 * Confirm field must match new_password (superRefine cross-field check).
 */
const changePasswordSchema = z
  .object({
    current_password: z
      .string({ message: "Vui lòng nhập mật khẩu hiện tại" })
      .min(1, { message: "Vui lòng nhập mật khẩu hiện tại" }),
    new_password: z
      .string({ message: "Vui lòng nhập mật khẩu mới" })
      .min(8, { message: "Mật khẩu phải có ít nhất 8 ký tự" })
      .max(128, { message: "Mật khẩu không được vượt quá 128 ký tự" })
      .regex(/[A-Z]/, { message: "Mật khẩu phải có ít nhất 1 chữ in hoa" })
      .regex(/\d/, { message: "Mật khẩu phải có ít nhất 1 chữ số" }),
    confirm_password: z
      .string({ message: "Vui lòng xác nhận mật khẩu mới" })
      .min(1, { message: "Vui lòng xác nhận mật khẩu mới" }),
  })
  .superRefine(({ new_password, confirm_password }, ctx) => {
    if (confirm_password !== new_password) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Mật khẩu xác nhận không khớp",
        path: ["confirm_password"],
      });
    }
  });

type ChangePasswordFormValues = z.infer<typeof changePasswordSchema>;

// ---------------------------------------------------------------------------
// Style tokens (consistent with LoginForm)
// ---------------------------------------------------------------------------

const labelClasses =
  "mb-1.5 block text-[13px] font-semibold text-slate-700";

const inputBaseClasses =
  "h-11 w-full rounded-xl border border-slate-200 bg-white/90 pl-10 pr-10 text-[14px] text-slate-900 placeholder:text-slate-400 shadow-sm transition-all duration-200 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:shadow-md";

const inputErrorClasses =
  "h-11 w-full rounded-xl border border-red-400 bg-white/90 pl-10 pr-10 text-[14px] text-slate-900 placeholder:text-slate-400 shadow-sm transition-all duration-200 focus:border-red-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-500/20";

const iconLeftClasses =
  "pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400";

const errorClasses =
  "mt-1.5 flex items-center gap-1 text-[12px] font-medium text-red-600";

const submitClasses =
  "inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 text-[14px] font-semibold text-white shadow-md transition-all duration-200 hover:bg-blue-700 hover:shadow-lg active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 cursor-pointer disabled:cursor-not-allowed disabled:opacity-60 disabled:shadow-none";

// ---------------------------------------------------------------------------
// Icons (Heroicons-style SVGs, no emoji)
// ---------------------------------------------------------------------------

function IconLock() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <rect
        x="5"
        y="11"
        width="14"
        height="10"
        rx="2"
        stroke="currentColor"
        strokeWidth="1.8"
      />
      <path
        d="M8 11V7a4 4 0 0 1 8 0v4"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
      <circle cx="12" cy="16" r="1.5" fill="currentColor" />
    </svg>
  );
}

function IconEye({ open }: { open: boolean }) {
  return open ? (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"
        stroke="currentColor"
        strokeWidth="1.8"
      />
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.8" />
    </svg>
  ) : (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
      <line
        x1="1"
        y1="1"
        x2="23"
        y2="23"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

function IconError() {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
      <path
        d="M12 8v4m0 4h.01"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function IconCheck() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M20 6L9 17l-5-5"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconSpinner() {
  return (
    <svg
      width="16"
      height="16"
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
  );
}

// ---------------------------------------------------------------------------
// Password field sub-component
// ---------------------------------------------------------------------------

interface PasswordFieldProps {
  id: string;
  label: string;
  autoComplete: string;
  placeholder: string;
  hasError: boolean;
  errorId: string;
  errorMessage?: string;
  showPassword: boolean;
  onToggleShow: () => void;
  registration: ReturnType<ReturnType<typeof useForm<ChangePasswordFormValues>>["register"]>;
}

function PasswordField({
  id,
  label,
  autoComplete,
  placeholder,
  hasError,
  errorId,
  errorMessage,
  showPassword,
  onToggleShow,
  registration,
}: PasswordFieldProps) {
  return (
    <div>
      <label htmlFor={id} className={labelClasses}>
        {label}
        <span className="ml-1 text-red-500" aria-hidden="true">
          *
        </span>
      </label>
      <div className="relative flex items-center">
        <span className={iconLeftClasses}>
          <IconLock />
        </span>
        <input
          id={id}
          type={showPassword ? "text" : "password"}
          autoComplete={autoComplete}
          placeholder={placeholder}
          aria-invalid={hasError ? "true" : "false"}
          aria-describedby={hasError ? errorId : undefined}
          className={hasError ? inputErrorClasses : inputBaseClasses}
          {...registration}
        />
        <button
          type="button"
          onClick={onToggleShow}
          aria-label={showPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
          className="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer text-slate-400 transition-colors hover:text-slate-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-1 rounded"
        >
          <IconEye open={showPassword} />
        </button>
      </div>
      {hasError && errorMessage && (
        <p id={errorId} className={errorClasses} role="alert">
          <IconError />
          {errorMessage}
        </p>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function ChangePasswordCard() {
  const { changePassword, logout } = useAuth();
  const router = useRouter();

  // Show/hide toggles per field
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  // Submission state
  const [isPending, setIsPending] = useState(false);
  const [successVisible, setSuccessVisible] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    setError,
    reset,
    formState: { errors },
  } = useForm<ChangePasswordFormValues>({
    resolver: zodResolver(changePasswordSchema),
    mode: "onSubmit",
  });

  async function onSubmit(values: ChangePasswordFormValues) {
    setIsPending(true);
    setApiError(null);

    try {
      await changePassword({
        current_password: values.current_password,
        new_password: values.new_password,
      });

      // Success path:
      // 1. Show success banner
      setSuccessVisible(true);
      reset();

      // 2. Short delay so the user sees the success message, then logout + redirect
      await new Promise<void>((resolve) => setTimeout(resolve, 1500));
      await logout();
      router.push("/?session=changed-password");
    } catch (err) {
      if (err instanceof ApiError) {
        // Wrong current password → inline field error
        if (
          err.code === "AUTH_INVALID_CREDENTIALS" ||
          err.status === 401
        ) {
          setError("current_password", {
            type: "server",
            message: "Mật khẩu hiện tại không đúng",
          });
        } else {
          // Other API errors → inline alert
          setApiError(err.message || "Đã xảy ra lỗi, vui lòng thử lại.");
        }
      } else {
        setApiError("Mất kết nối, vui lòng thử lại.");
      }
    } finally {
      setIsPending(false);
    }
  }

  return (
    <section
      aria-labelledby="change-password-heading"
      className="rounded-xl border border-gray-200 bg-white/80 px-6 py-6 shadow-sm"
    >
      <h2
        id="change-password-heading"
        className="mb-1 text-base font-bold text-slate-900"
      >
        Đổi mật khẩu
      </h2>
      <p className="mb-5 text-sm text-slate-600">
        Sau khi đổi mật khẩu thành công, bạn sẽ được đăng xuất và cần đăng nhập lại.
      </p>

      {/* Success banner */}
      {successVisible && (
        <div
          role="status"
          aria-live="polite"
          className="mb-5 flex items-center gap-2 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm font-semibold text-green-700"
        >
          <IconCheck />
          Đổi mật khẩu thành công. Đang đăng xuất…
        </div>
      )}

      {/* API error banner */}
      {apiError && (
        <div
          role="alert"
          aria-live="assertive"
          className="mb-5 flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700"
        >
          <IconError />
          {apiError}
        </div>
      )}

      <form
        noValidate
        onSubmit={handleSubmit(onSubmit)}
        className="space-y-4"
      >
        {/* Current password */}
        <PasswordField
          id="change-current-password"
          label="Mật khẩu hiện tại"
          autoComplete="current-password"
          placeholder="••••••••"
          hasError={!!errors.current_password}
          errorId="change-current-password-error"
          errorMessage={errors.current_password?.message}
          showPassword={showCurrent}
          onToggleShow={() => setShowCurrent((v) => !v)}
          registration={register("current_password")}
        />

        {/* New password */}
        <PasswordField
          id="change-new-password"
          label="Mật khẩu mới"
          autoComplete="new-password"
          placeholder="Ít nhất 8 ký tự, 1 chữ hoa, 1 số"
          hasError={!!errors.new_password}
          errorId="change-new-password-error"
          errorMessage={errors.new_password?.message}
          showPassword={showNew}
          onToggleShow={() => setShowNew((v) => !v)}
          registration={register("new_password")}
        />

        {/* Confirm new password */}
        <PasswordField
          id="change-confirm-password"
          label="Xác nhận mật khẩu mới"
          autoComplete="new-password"
          placeholder="Nhập lại mật khẩu mới"
          hasError={!!errors.confirm_password}
          errorId="change-confirm-password-error"
          errorMessage={errors.confirm_password?.message}
          showPassword={showConfirm}
          onToggleShow={() => setShowConfirm((v) => !v)}
          registration={register("confirm_password")}
        />

        {/* Submit */}
        <div className="pt-1">
          <button
            type="submit"
            disabled={isPending || successVisible}
            className={submitClasses}
            aria-busy={isPending ? "true" : "false"}
          >
            {isPending ? (
              <>
                <IconSpinner />
                Đang xử lý…
              </>
            ) : (
              "Đổi mật khẩu"
            )}
          </button>
        </div>
      </form>
    </section>
  );
}
