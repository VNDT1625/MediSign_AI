"use client";

/**
 * RegisterForm — multi-step (3 bước) để form gọn trong tờ giấy clipboard.
 *
 * Bước 1: Họ tên + Tên đăng nhập
 * Bước 2: Email + Số điện thoại
 * Bước 3: Mật khẩu + Đồng ý điều khoản
 *
 * Mỗi bước validate riêng trước khi cho qua bước tiếp theo.
 * Submit thật chỉ xảy ra ở bước 3.
 */

import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { registerSchema, type RegisterFormValues } from "@/lib/validation/auth";

export type RegisterFormServerErrors = Partial<
  Record<keyof RegisterFormValues, string>
>;

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

const label = "mb-1.5 block text-[13px] font-semibold text-slate-700";

const errMsg =
  "mt-1.5 flex items-center gap-1 text-[12px] font-medium text-red-600";

const btnPrimary =
  "inline-flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-blue-600 text-[14px] font-semibold text-white shadow-md transition-all duration-200 hover:bg-blue-700 hover:shadow-lg active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 cursor-pointer disabled:cursor-not-allowed disabled:opacity-60";

const btnSecondary =
  "inline-flex h-11 w-full items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white text-[14px] font-semibold text-slate-700 shadow-sm transition-all duration-200 hover:bg-slate-50 hover:border-slate-300 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400 focus-visible:ring-offset-2 cursor-pointer";

// ---------------------------------------------------------------------------
// Icons
// ---------------------------------------------------------------------------

function IUser() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="1.8" />
      <path d="M4 20c1.5-4 4.5-6 8-6s6.5 2 8 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function IId() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="2" y="5" width="20" height="14" rx="2" stroke="currentColor" strokeWidth="1.8" />
      <path d="M8 10h8M8 14h5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function IAt() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="1.8" />
      <path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-3.92 7.94" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function IPhone() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.6 1.27h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.91a16 16 0 0 0 6 6l.91-.91a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 21.73 16.92z" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function ILock() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="5" y="11" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.8" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <circle cx="12" cy="16" r="1.5" fill="currentColor" />
    </svg>
  );
}

function IEye({ open }: { open: boolean }) {
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

function IErr() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
      <path d="M12 8v4m0 4h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function ICheck() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M20 6L9 17l-5-5" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function IArrow() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Step schemas — validate từng bước riêng
// ---------------------------------------------------------------------------

const step1Schema = registerSchema.pick({ full_name: true, username: true });
const step2Schema = registerSchema.pick({ email: true, phone: true });
const step3Schema = registerSchema.pick({ password: true, terms_accepted: true });

type Step1 = z.infer<typeof step1Schema>;
type Step2 = z.infer<typeof step2Schema>;
type Step3 = z.infer<typeof step3Schema>;

// ---------------------------------------------------------------------------
// Step indicator
// ---------------------------------------------------------------------------

function StepDots({ current, total }: { current: number; total: number }) {
  return (
    <div className="mb-5 flex items-center justify-center gap-2" aria-label={`Bước ${current} trong ${total}`}>
      {Array.from({ length: total }, (_, i) => {
        const step = i + 1;
        const done = step < current;
        const active = step === current;
        return (
          <div key={step} className="flex items-center gap-2">
            <div
              className={`flex h-7 w-7 items-center justify-center rounded-full text-[12px] font-bold transition-all duration-300 ${
                done
                  ? "bg-blue-600 text-white"
                  : active
                    ? "bg-blue-600 text-white ring-4 ring-blue-100"
                    : "bg-slate-100 text-slate-400"
              }`}
            >
              {done ? <ICheck /> : step}
            </div>
            {step < total && (
              <div
                className={`h-0.5 w-8 rounded-full transition-all duration-300 ${
                  done ? "bg-blue-600" : "bg-slate-200"
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface RegisterFormProps {
  onSubmit: (values: RegisterFormValues) => void | Promise<void>;
  isPending?: boolean;
  defaultValues?: Partial<RegisterFormValues>;
  serverErrors?: RegisterFormServerErrors;
  onFieldChange?: () => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function RegisterForm({
  onSubmit,
  isPending = false,
  defaultValues,
  serverErrors,
  onFieldChange,
}: RegisterFormProps) {
  const [step, setStep] = useState(1);
  const [showPassword, setShowPassword] = useState(false);

  // Lưu dữ liệu đã nhập qua các bước
  const [saved, setSaved] = useState<Partial<RegisterFormValues>>({
    full_name: defaultValues?.full_name ?? "",
    username: defaultValues?.username ?? "",
    email: defaultValues?.email ?? "",
    phone: defaultValues?.phone ?? "",
    password: defaultValues?.password ?? "",
    terms_accepted: defaultValues?.terms_accepted ?? false,
  });

  // ---------------------------------------------------------------------------
  // Step 1 form
  // ---------------------------------------------------------------------------
  const form1 = useForm<Step1>({
    resolver: zodResolver(step1Schema),
    defaultValues: { full_name: saved.full_name ?? "", username: saved.username ?? "" },
    mode: "onSubmit",
  });

  // ---------------------------------------------------------------------------
  // Step 2 form
  // ---------------------------------------------------------------------------
  const form2 = useForm<Step2>({
    resolver: zodResolver(step2Schema),
    defaultValues: { email: saved.email ?? "", phone: saved.phone ?? "" },
    mode: "onSubmit",
  });

  // ---------------------------------------------------------------------------
  // Step 3 form (full — submit thật)
  // ---------------------------------------------------------------------------
  const form3 = useForm<Step3>({
    resolver: zodResolver(step3Schema),
    defaultValues: { password: saved.password ?? "", terms_accepted: saved.terms_accepted ?? false },
    mode: "onSubmit",
  });

  // Apply server errors vào đúng step
  const lastServerFieldsRef = useRef<Array<keyof RegisterFormValues>>([]);
  useEffect(() => {
    const next = serverErrors ?? {};
    const previous = lastServerFieldsRef.current;
    const nextFields: Array<keyof RegisterFormValues> = [];

    (Object.keys(next) as Array<keyof RegisterFormValues>).forEach((field) => {
      const message = next[field];
      if (typeof message !== "string" || message.length === 0) return;
      nextFields.push(field);

      if (field === "full_name" || field === "username") {
        form1.setError(field, { type: "server", message });
        setStep(1);
      } else if (field === "email" || field === "phone") {
        form2.setError(field, { type: "server", message });
        setStep(2);
      } else if (field === "password" || field === "terms_accepted") {
        form3.setError(field, { type: "server", message });
        setStep(3);
      }
    });

    previous.forEach((field) => {
      if (!nextFields.includes(field)) {
        if (field === "full_name" || field === "username") form1.clearErrors(field);
        else if (field === "email" || field === "phone") form2.clearErrors(field);
        else if (field === "password" || field === "terms_accepted") form3.clearErrors(field);
      }
    });

    lastServerFieldsRef.current = nextFields;
  }, [serverErrors, form1, form2, form3]);

  // ---------------------------------------------------------------------------
  // Handlers
  // ---------------------------------------------------------------------------

  const handleStep1 = form1.handleSubmit((values) => {
    setSaved((prev) => ({ ...prev, ...values }));
    setStep(2);
  });

  const handleStep2 = form2.handleSubmit((values) => {
    setSaved((prev) => ({ ...prev, ...values }));
    setStep(3);
  });

  const handleStep3 = form3.handleSubmit(async (values) => {
    const full: RegisterFormValues = {
      full_name: saved.full_name ?? "",
      username: saved.username ?? "",
      email: saved.email ?? "",
      phone: saved.phone ?? "",
      password: values.password,
      terms_accepted: values.terms_accepted,
    };
    await onSubmit(full);
  });

  const goBack = () => setStep((s) => Math.max(1, s - 1));

  // ---------------------------------------------------------------------------
  // Render helpers
  // ---------------------------------------------------------------------------

  function FieldError({ message }: { message?: string }) {
    if (!message) return null;
    return (
      <p className={errMsg} role="alert">
        <IErr />{message}
      </p>
    );
  }

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <div onChange={onFieldChange}>
      <StepDots current={step} total={3} />

      {/* ── Bước 1: Thông tin cá nhân ── */}
      {step === 1 && (
        <form noValidate onSubmit={handleStep1} className="space-y-4">
          <p className="mb-3 text-center text-[12px] font-medium text-slate-500">
            Bước 1 · Thông tin cá nhân
          </p>

          <div>
            <label htmlFor="r-full-name" className={label}>
              Họ và tên
              <span className="ml-1 text-red-500" aria-hidden="true">*</span>
            </label>
            <div className={inputWrap}>
              <span className={iconPos}><IUser /></span>
              <input
                id="r-full-name"
                type="text"
                autoComplete="name"
                autoFocus
                placeholder="Nguyễn Văn A"
                className={form1.formState.errors.full_name ? inputErr : input}
                {...form1.register("full_name")}
              />
            </div>
            <FieldError message={form1.formState.errors.full_name?.message} />
          </div>

          <div>
            <label htmlFor="r-username" className={label}>
              Tên đăng nhập
              <span className="ml-1 text-red-500" aria-hidden="true">*</span>
            </label>
            <div className={inputWrap}>
              <span className={iconPos}><IId /></span>
              <input
                id="r-username"
                type="text"
                autoComplete="username"
                placeholder="vd: nguyenvana"
                className={form1.formState.errors.username ? inputErr : input}
                {...form1.register("username")}
              />
            </div>
            <FieldError message={form1.formState.errors.username?.message} />
          </div>

          <button type="submit" className={btnPrimary}>
            Tiếp theo <IArrow />
          </button>
        </form>
      )}

      {/* ── Bước 2: Liên hệ ── */}
      {step === 2 && (
        <form noValidate onSubmit={handleStep2} className="space-y-4">
          <p className="mb-3 text-center text-[12px] font-medium text-slate-500">
            Bước 2 · Thông tin liên hệ
          </p>

          <div>
            <label htmlFor="r-email" className={label}>
              Email
              <span className="ml-1 text-red-500" aria-hidden="true">*</span>
            </label>
            <div className={inputWrap}>
              <span className={iconPos}><IAt /></span>
              <input
                id="r-email"
                type="email"
                inputMode="email"
                autoComplete="email"
                autoFocus
                placeholder="ban@example.com"
                className={form2.formState.errors.email ? inputErr : input}
                {...form2.register("email")}
              />
            </div>
            <FieldError message={form2.formState.errors.email?.message} />
          </div>

          <div>
            <label htmlFor="r-phone" className={label}>
              Số điện thoại
              <span className="ml-1 text-red-500" aria-hidden="true">*</span>
            </label>
            <div className={inputWrap}>
              <span className={iconPos}><IPhone /></span>
              <input
                id="r-phone"
                type="tel"
                inputMode="tel"
                autoComplete="tel"
                placeholder="0901234567"
                className={form2.formState.errors.phone ? inputErr : input}
                {...form2.register("phone")}
              />
            </div>
            <FieldError message={form2.formState.errors.phone?.message} />
          </div>

          <div className="flex gap-2">
            <button type="button" onClick={goBack} className={btnSecondary}>
              ← Quay lại
            </button>
            <button type="submit" className={btnPrimary}>
              Tiếp theo <IArrow />
            </button>
          </div>
        </form>
      )}

      {/* ── Bước 3: Mật khẩu ── */}
      {step === 3 && (
        <form noValidate onSubmit={handleStep3} className="space-y-4">
          <p className="mb-3 text-center text-[12px] font-medium text-slate-500">
            Bước 3 · Đặt mật khẩu
          </p>

          <div>
            <label htmlFor="r-password" className={label}>
              Mật khẩu
              <span className="ml-1 text-red-500" aria-hidden="true">*</span>
            </label>
            <div className={inputWrap}>
              <span className={iconPos}><ILock /></span>
              <input
                id="r-password"
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                autoFocus
                placeholder="Tối thiểu 8 ký tự, 1 chữ hoa, 1 số"
                className={`${form3.formState.errors.password ? inputErr : input} pr-10`}
                {...form3.register("password")}
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                aria-label={showPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
                className="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer text-slate-400 transition-colors hover:text-slate-600 focus-visible:outline-none"
              >
                <IEye open={showPassword} />
              </button>
            </div>
            <FieldError message={form3.formState.errors.password?.message} />
          </div>

          {/* Điều khoản */}
          <div>
            <label
              htmlFor="r-terms"
              className="flex cursor-pointer items-start gap-2.5 text-[12.5px] text-slate-600"
            >
              <input
                id="r-terms"
                type="checkbox"
                className="mt-0.5 h-4 w-4 cursor-pointer rounded border-slate-300 bg-white text-blue-600 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-1"
                {...form3.register("terms_accepted")}
              />
              <span>
                Tôi đồng ý với{" "}
                <a href="/terms" target="_blank" rel="noopener noreferrer"
                  className="font-semibold text-blue-600 underline-offset-2 hover:underline">
                  Điều khoản
                </a>{" "}
                và{" "}
                <a href="/privacy" target="_blank" rel="noopener noreferrer"
                  className="font-semibold text-blue-600 underline-offset-2 hover:underline">
                  Chính sách bảo mật
                </a>
              </span>
            </label>
            <FieldError message={form3.formState.errors.terms_accepted?.message} />
          </div>

          <div className="flex gap-2">
            <button type="button" onClick={goBack} className={btnSecondary} disabled={isPending}>
              ← Quay lại
            </button>
            <button
              type="submit"
              disabled={isPending}
              className={btnPrimary}
              aria-busy={isPending ? "true" : "false"}
            >
              {isPending ? (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true" className="motion-safe:animate-spin">
                    <path d="M12 3a9 9 0 1 0 9 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  </svg>
                  Đang tạo...
                </>
              ) : (
                "Tạo tài khoản"
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
