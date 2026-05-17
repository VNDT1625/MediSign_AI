"use client";

/**
 * `/reset-password?token=<hex>` — trang đặt lại mật khẩu.
 *
 * User đến đây từ link trong email. Token được đọc từ query string,
 * validate ở backend khi submit. Sau khi thành công, chuyển về trang
 * chủ và mở LoginModal.
 */

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import * as authApi from "@/lib/api/auth";
import { ApiError } from "@/lib/api/errors";

// ---------------------------------------------------------------------------
// Schema
// ---------------------------------------------------------------------------

const resetSchema = z
  .object({
    new_password: z
      .string({ message: "Vui lòng nhập mật khẩu mới" })
      .min(8, { message: "Mật khẩu phải có ít nhất 8 ký tự" })
      .max(128, { message: "Mật khẩu không được vượt quá 128 ký tự" })
      .regex(/[A-Z]/, { message: "Mật khẩu phải có ít nhất 1 chữ in hoa" })
      .regex(/\d/, { message: "Mật khẩu phải có ít nhất 1 chữ số" }),
    confirm_password: z.string({ message: "Vui lòng xác nhận mật khẩu" }),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Mật khẩu xác nhận không khớp",
    path: ["confirm_password"],
  });

type ResetFormValues = z.infer<typeof resetSchema>;

// ---------------------------------------------------------------------------
// Style tokens
// ---------------------------------------------------------------------------

const inputWrap = "relative flex items-center";
const input =
  "h-11 w-full rounded-xl border border-slate-200 bg-white pl-10 pr-10 text-[14px] text-slate-900 placeholder:text-slate-400 shadow-sm transition-all duration-200 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20";
const inputErr =
  "h-11 w-full rounded-xl border border-red-400 bg-white pl-10 pr-10 text-[14px] text-slate-900 placeholder:text-slate-400 shadow-sm transition-all duration-200 focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/20";
const iconPos =
  "pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400";
const labelCls = "mb-1.5 block text-[13px] font-semibold text-slate-700";
const errMsg = "mt-1.5 flex items-center gap-1 text-[12px] font-medium text-red-600";
const btnPrimary =
  "inline-flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-blue-600 text-[14px] font-semibold text-white shadow-md transition-all duration-200 hover:bg-blue-700 hover:shadow-lg active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 cursor-pointer disabled:cursor-not-allowed disabled:opacity-60";

// ---------------------------------------------------------------------------
// Icons
// ---------------------------------------------------------------------------

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
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="10" stroke="#22c55e" strokeWidth="1.8" />
      <path d="M8 12l3 3 5-5" stroke="#22c55e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Inner component (needs useSearchParams — must be inside Suspense)
// ---------------------------------------------------------------------------

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";

  const [pending, setPending] = useState(false);
  const [success, setSuccess] = useState(false);
  const [serverError, setServerError] = useState<string | undefined>();
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetFormValues>({
    resolver: zodResolver(resetSchema),
    mode: "onSubmit",
  });

  // Token missing — link không hợp lệ
  if (!token) {
    return (
      <div className="text-center space-y-4">
        <div className="rounded-xl border border-red-200 bg-red-50 px-5 py-4">
          <p className="text-[14px] font-semibold text-red-700">Liên kết không hợp lệ</p>
          <p className="mt-1 text-[13px] text-red-600">
            Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.
          </p>
        </div>
        <button
          type="button"
          onClick={() => router.push("/?login=1")}
          className={btnPrimary}
        >
          Yêu cầu liên kết mới
        </button>
      </div>
    );
  }

  if (success) {
    return (
      <div className="text-center space-y-5">
        <div className="flex justify-center"><ICheck /></div>
        <div>
          <p className="text-[16px] font-bold text-slate-900">Đặt lại mật khẩu thành công</p>
          <p className="mt-1.5 text-[13px] text-slate-500">
            Mật khẩu của bạn đã được cập nhật. Vui lòng đăng nhập lại.
          </p>
        </div>
        <button
          type="button"
          onClick={() => router.push("/?login=1")}
          className={btnPrimary}
        >
          Đăng nhập ngay
        </button>
      </div>
    );
  }

  const onSubmit = handleSubmit(async (values) => {
    if (pending) return;
    setPending(true);
    setServerError(undefined);
    try {
      await authApi.resetPassword(token, values.new_password);
      setSuccess(true);
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.code === "AUTH_INVALID_RESET_TOKEN") {
          setServerError("Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn. Vui lòng yêu cầu liên kết mới.");
        } else if (err.code === "NETWORK_ERROR") {
          setServerError("Mất kết nối. Kiểm tra mạng và thử lại.");
        } else {
          setServerError("Hệ thống đang bận, vui lòng thử lại sau.");
        }
      } else {
        setServerError("Hệ thống đang bận, vui lòng thử lại sau.");
      }
    } finally {
      setPending(false);
    }
  });

  return (
    <form noValidate onSubmit={onSubmit} className="space-y-4">
      <p className="text-center text-[13px] text-slate-500">
        Nhập mật khẩu mới cho tài khoản của bạn.
      </p>

      {serverError && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3" role="alert">
          <p className="text-[13px] font-medium text-red-700">{serverError}</p>
          {serverError.includes("hết hạn") && (
            <button
              type="button"
              onClick={() => router.push("/?login=1&forgot=1")}
              className="mt-2 text-[12px] font-semibold text-red-700 underline cursor-pointer"
            >
              Yêu cầu liên kết mới →
            </button>
          )}
        </div>
      )}

      {/* Mật khẩu mới */}
      <div>
        <label htmlFor="rp-new" className={labelCls}>
          Mật khẩu mới
          <span className="ml-1 text-red-500" aria-hidden="true">*</span>
        </label>
        <div className={inputWrap}>
          <span className={iconPos}><ILock /></span>
          <input
            id="rp-new"
            type={showNew ? "text" : "password"}
            autoComplete="new-password"
            autoFocus
            placeholder="Tối thiểu 8 ký tự, 1 chữ hoa, 1 số"
            aria-invalid={errors.new_password ? "true" : "false"}
            aria-describedby={errors.new_password ? "rp-new-error" : undefined}
            className={errors.new_password ? inputErr : input}
            {...register("new_password")}
          />
          <button
            type="button"
            onClick={() => setShowNew((v) => !v)}
            aria-label={showNew ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
            className="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer text-slate-400 transition-colors hover:text-slate-600 focus-visible:outline-none"
          >
            <IEye open={showNew} />
          </button>
        </div>
        {errors.new_password && (
          <p id="rp-new-error" className={errMsg} role="alert">
            <IErr />{errors.new_password.message}
          </p>
        )}
      </div>

      {/* Xác nhận mật khẩu */}
      <div>
        <label htmlFor="rp-confirm" className={labelCls}>
          Xác nhận mật khẩu
          <span className="ml-1 text-red-500" aria-hidden="true">*</span>
        </label>
        <div className={inputWrap}>
          <span className={iconPos}><ILock /></span>
          <input
            id="rp-confirm"
            type={showConfirm ? "text" : "password"}
            autoComplete="new-password"
            placeholder="Nhập lại mật khẩu mới"
            aria-invalid={errors.confirm_password ? "true" : "false"}
            aria-describedby={errors.confirm_password ? "rp-confirm-error" : undefined}
            className={errors.confirm_password ? inputErr : input}
            {...register("confirm_password")}
          />
          <button
            type="button"
            onClick={() => setShowConfirm((v) => !v)}
            aria-label={showConfirm ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
            className="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer text-slate-400 transition-colors hover:text-slate-600 focus-visible:outline-none"
          >
            <IEye open={showConfirm} />
          </button>
        </div>
        {errors.confirm_password && (
          <p id="rp-confirm-error" className={errMsg} role="alert">
            <IErr />{errors.confirm_password.message}
          </p>
        )}
      </div>

      <button type="submit" disabled={pending} className={btnPrimary} aria-busy={pending ? "true" : "false"}>
        {pending ? (
          <>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true" className="motion-safe:animate-spin">
              <path d="M12 3a9 9 0 1 0 9 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
            Đang cập nhật...
          </>
        ) : (
          "Đặt lại mật khẩu"
        )}
      </button>

      <div className="text-center">
        <button
          type="button"
          onClick={() => router.push("/?login=1")}
          disabled={pending}
          className="text-[13px] font-medium text-slate-500 transition-colors hover:text-slate-700 cursor-pointer focus-visible:outline-none"
        >
          ← Quay lại đăng nhập
        </button>
      </div>
    </form>
  );
}

// ---------------------------------------------------------------------------
// Page wrapper
// ---------------------------------------------------------------------------

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-[400px]">
        {/* Logo / brand */}
        <div className="mb-8 text-center">
          <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-blue-600">MediSign AI</p>
          <h1 className="mt-2 text-[26px] font-extrabold text-slate-900">Đặt lại mật khẩu</h1>
          <p className="mt-1 text-[13px] text-slate-500">Chăm sóc sức khỏe thông minh</p>
        </div>

        {/* Card */}
        <div className="rounded-2xl border border-slate-200 bg-white px-8 py-8 shadow-lg">
          <Suspense fallback={
            <div className="flex justify-center py-8">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true" className="animate-spin text-blue-600">
                <path d="M12 3a9 9 0 1 0 9 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </div>
          }>
            <ResetPasswordForm />
          </Suspense>
        </div>
      </div>
    </div>
  );
}
