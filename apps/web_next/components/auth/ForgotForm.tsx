"use client";

/**
 * ForgotForm — Phase 1 placeholder.
 *
 * The backend `/auth/forgot-password` endpoint ships in Phase 2.
 * Per Requirements 2.1.3: the submit button is permanently disabled with
 * a tooltip "Sẽ ra mắt sau" so users understand the feature is coming.
 *
 * The email field is rendered (not disabled) so users can see what the
 * form will look like, but submission is intentionally blocked.
 *
 * @see Requirements 2.1.3 (forgot password — Phase 2 placeholder)
 * @see Requirements 2.4.2 (form validation)
 */

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { forgotSchema, type ForgotFormValues } from "@/lib/validation/auth";

// ---------------------------------------------------------------------------
// Style tokens
// ---------------------------------------------------------------------------

const inputWrap = "relative flex items-center";

const input =
  "h-11 w-full rounded-xl border border-slate-200 bg-white/90 pl-10 pr-3 text-[14px] text-slate-900 placeholder:text-slate-400 shadow-sm transition-all duration-200 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:shadow-md";

const inputErr =
  "h-11 w-full rounded-xl border border-red-400 bg-white/90 pl-10 pr-3 text-[14px] text-slate-900 placeholder:text-slate-400 shadow-sm transition-all duration-200 focus:border-red-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-red-500/20";

const iconPos =
  "pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400";

const labelCls = "mb-1.5 block text-[13px] font-semibold text-slate-700";

const errMsg =
  "mt-1.5 flex items-center gap-1 text-[12px] font-medium text-red-600";

// ---------------------------------------------------------------------------
// Icons (Heroicons-style SVGs — no emoji)
// ---------------------------------------------------------------------------

function IAt() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-3.92 7.94"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

function IErr() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
      <path d="M12 8v4m0 4h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

/** Clock icon — used to signal "coming soon" on the disabled button. */
function IClock() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
      <path d="M12 7v5l3 2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

/** Info icon — used in the Phase 2 notice banner. */
function IInfo() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.8" />
      <path d="M12 8h.01M12 12v4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface ForgotFormProps {
  /**
   * Called when the form is submitted. In Phase 1 this is never invoked
   * because the submit button is permanently disabled.
   */
  onSubmit: (values: ForgotFormValues) => void | Promise<void>;
  /** Unused in Phase 1 — kept for API compatibility with LoginModal. */
  isPending?: boolean;
  defaultValues?: Partial<ForgotFormValues>;
  /** Unused in Phase 1 — kept for API compatibility with LoginModal. */
  serverError?: string;
  onBackToLogin?: () => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function ForgotForm({
  onSubmit,
  isPending = false,
  defaultValues,
  onBackToLogin,
}: ForgotFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotFormValues>({
    resolver: zodResolver(forgotSchema),
    defaultValues: { email: defaultValues?.email ?? "" },
    mode: "onSubmit",
  });

  // The handler is wired so the form is structurally correct, but the
  // disabled submit button prevents it from ever being called in Phase 1.
  const handler = handleSubmit(onSubmit);

  return (
    <form noValidate onSubmit={handler} className="space-y-4">
      {/* Phase 2 notice banner */}
      <div
        className="flex items-start gap-2.5 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3"
        role="note"
        aria-label="Thông báo tính năng"
      >
        <span className="mt-0.5 shrink-0 text-blue-500">
          <IInfo />
        </span>
        <p className="text-[13px] leading-relaxed text-blue-700">
          Tính năng khôi phục mật khẩu sẽ ra mắt trong phiên bản tiếp theo.
          Vui lòng liên hệ hỗ trợ nếu cần trợ giúp ngay bây giờ.
        </p>
      </div>

      {/* Email field — rendered but submission is blocked */}
      <div>
        <label htmlFor="forgot-email" className={labelCls}>
          Email
          <span className="ml-1 text-red-500" aria-hidden="true">*</span>
        </label>
        <div className={inputWrap}>
          <span className={iconPos}>
            <IAt />
          </span>
          <input
            id="forgot-email"
            type="email"
            inputMode="email"
            autoComplete="email"
            autoFocus
            placeholder="ban@example.com"
            aria-invalid={errors.email ? "true" : "false"}
            aria-describedby={errors.email ? "forgot-email-error" : undefined}
            className={errors.email ? inputErr : input}
            {...register("email")}
          />
        </div>
        {errors.email && (
          <p id="forgot-email-error" className={errMsg} role="alert">
            <IErr />
            {errors.email.message}
          </p>
        )}
      </div>

      {/*
        Submit button — permanently disabled in Phase 1.
        Wrapped in a <div> with `title` so the tooltip is visible even
        when the button itself is disabled (browsers suppress `title` on
        disabled form elements in some engines).
      */}
      <div
        title="Sẽ ra mắt sau"
        className="relative"
        aria-label="Sẽ ra mắt sau"
      >
        <button
          type="submit"
          disabled
          aria-disabled="true"
          aria-describedby="forgot-phase2-hint"
          className="inline-flex h-11 w-full cursor-not-allowed items-center justify-center gap-2 rounded-xl bg-slate-300 text-[14px] font-semibold text-slate-500 shadow-none transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400 focus-visible:ring-offset-2"
        >
          <IClock />
          Gửi liên kết khôi phục
        </button>
        <p
          id="forgot-phase2-hint"
          className="mt-1.5 text-center text-[12px] text-slate-400"
        >
          Sẽ ra mắt sau
        </p>
      </div>

      {onBackToLogin && (
        <button
          type="button"
          onClick={onBackToLogin}
          disabled={isPending}
          className="inline-flex h-10 w-full cursor-pointer items-center justify-center text-[13px] font-medium text-slate-500 transition-colors hover:text-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400 focus-visible:ring-offset-2 disabled:opacity-50"
        >
          ← Quay lại đăng nhập
        </button>
      )}
    </form>
  );
}
