"use client";

import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { loginSchema, type LoginFormValues } from "@/lib/validation/auth";

export type LoginFormServerErrors = Partial<
  Record<keyof LoginFormValues, string>
>;

// ---------------------------------------------------------------------------
// Shared style tokens
// ---------------------------------------------------------------------------

const inputWrapClasses =
  "relative flex items-center";

const inputClasses =
  "h-11 w-full border-0 border-b-2 border-slate-300 bg-transparent pl-8 pr-3 text-[14px] text-slate-900 placeholder:text-slate-400 transition-all duration-200 focus:border-brand focus:outline-none focus:ring-0";

const inputErrorClasses =
  "h-11 w-full border-0 border-b-2 border-red-400 bg-transparent pl-8 pr-3 text-[14px] text-slate-900 placeholder:text-slate-400 transition-all duration-200 focus:border-red-500 focus:outline-none focus:ring-0";

const iconClasses =
  "pointer-events-none absolute left-0 top-1/2 -translate-y-1/2 text-slate-400";

const labelClasses =
  "mb-1.5 block text-[13px] font-semibold text-slate-700";

const errorClasses =
  "mt-1.5 flex items-center gap-1 text-[12px] font-medium text-red-600";

const submitClasses =
  "relative mt-1 inline-flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-blue-600 text-[14px] font-semibold text-white shadow-md transition-all duration-200 hover:bg-blue-700 hover:shadow-lg active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 cursor-pointer disabled:cursor-not-allowed disabled:opacity-60 disabled:shadow-none";

// ---------------------------------------------------------------------------
// Icons
// ---------------------------------------------------------------------------

function IconUser() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="1.8" />
      <path d="M4 20c1.5-4 4.5-6 8-6s6.5 2 8 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function IconLock() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="5" y="11" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.8" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <circle cx="12" cy="16" r="1.5" fill="currentColor" />
    </svg>
  );
}

function IconEye({ open }: { open: boolean }) {
  return open ? (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" strokeWidth="1.8" />
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.8" />
    </svg>
  ) : (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <line x1="1" y1="1" x2="23" y2="23" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function IconError() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
      <path d="M12 8v4m0 4h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface LoginFormProps {
  onSubmit: (values: LoginFormValues) => void | Promise<void>;
  isPending?: boolean;
  defaultValues?: Partial<LoginFormValues>;
  serverErrors?: LoginFormServerErrors;
  onFieldChange?: () => void;
  rateLimited?: boolean;
  submitLabel?: string;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function LoginForm({
  onSubmit,
  isPending = false,
  defaultValues,
  serverErrors,
  onFieldChange,
  rateLimited = false,
  submitLabel,
}: LoginFormProps) {
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    setError,
    clearErrors,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      identifier: defaultValues?.identifier ?? "",
      password: defaultValues?.password ?? "",
      remember: defaultValues?.remember ?? false,
    },
    mode: "onSubmit",
  });

  const lastServerFieldsRef = useRef<Array<keyof LoginFormValues>>([]);

  useEffect(() => {
    const next = serverErrors ?? {};
    const previous = lastServerFieldsRef.current;
    const nextFields: Array<keyof LoginFormValues> = [];

    (Object.keys(next) as Array<keyof LoginFormValues>).forEach((field) => {
      const message = next[field];
      if (typeof message === "string" && message.length > 0) {
        setError(field, { type: "server", message });
        nextFields.push(field);
      }
    });

    previous.forEach((field) => {
      if (!nextFields.includes(field)) clearErrors(field);
    });

    lastServerFieldsRef.current = nextFields;
  }, [serverErrors, setError, clearErrors]);

  return (
    <form
      noValidate
      onSubmit={handleSubmit(onSubmit)}
      onChange={onFieldChange}
      className="space-y-4"
    >
      {/* Identifier */}
      <div>
        <label htmlFor="login-identifier" className={labelClasses}>
          Email hoặc số điện thoại
          <span className="ml-1 text-red-500" aria-hidden="true">*</span>
        </label>
        <div className={inputWrapClasses}>
          <span className={iconClasses}><IconUser /></span>
          <input
            id="login-identifier"
            type="text"
            inputMode="email"
            autoComplete="username"
            placeholder="ban@example.com hoặc 0901234567"
            aria-invalid={errors.identifier ? "true" : "false"}
            aria-describedby={errors.identifier ? "login-identifier-error" : undefined}
            className={errors.identifier ? inputErrorClasses : inputClasses}
            {...register("identifier")}
          />
        </div>
        {errors.identifier && (
          <p id="login-identifier-error" className={errorClasses} role="alert">
            <IconError />{errors.identifier.message}
          </p>
        )}
      </div>

      {/* Password */}
      <div>
        <label htmlFor="login-password" className={labelClasses}>
          Mật khẩu
          <span className="ml-1 text-red-500" aria-hidden="true">*</span>
        </label>
        <div className={inputWrapClasses}>
          <span className={iconClasses}><IconLock /></span>
          <input
            id="login-password"
            type={showPassword ? "text" : "password"}
            autoComplete="current-password"
            placeholder="••••••••"
            aria-invalid={errors.password ? "true" : "false"}
            aria-describedby={errors.password ? "login-password-error" : undefined}
            className={`${errors.password ? inputErrorClasses : inputClasses} pr-10`}
            {...register("password")}
          />
          <button
            type="button"
            onClick={() => setShowPassword((v) => !v)}
            aria-label={showPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
            className="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer text-slate-400 transition-colors hover:text-slate-600 focus-visible:outline-none"
          >
            <IconEye open={showPassword} />
          </button>
        </div>
        {errors.password && (
          <p id="login-password-error" className={errorClasses} role="alert">
            <IconError />{errors.password.message}
          </p>
        )}
      </div>

      {/* Remember me */}
      <div className="flex items-center gap-2">
        <input
          id="login-remember"
          type="checkbox"
          className="h-4 w-4 cursor-pointer rounded border-slate-300 bg-white text-blue-600 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-1"
          {...register("remember")}
        />
        <label
          htmlFor="login-remember"
          className="cursor-pointer select-none text-[13px] text-slate-600"
        >
          Ghi nhớ tôi
        </label>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={isPending || rateLimited}
        className={submitClasses}
        aria-busy={isPending ? "true" : "false"}
      >
        {isPending ? (
          <>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true" className="motion-safe:animate-spin">
              <path d="M12 3a9 9 0 1 0 9 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
            Đang đăng nhập...
          </>
        ) : (
          submitLabel ?? "Đăng nhập"
        )}
      </button>
    </form>
  );
}
