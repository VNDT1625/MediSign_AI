/**
 * Zod schemas for the LoginModal forms (login / register / forgot password).
 *
 * Field constraints are kept in lockstep with the FastAPI backend
 * (`apps/backend_fastapi/app/schemas/auth.py`):
 *   - email           → EmailStr
 *   - phone           → 10..20 chars, VN format `^(\+84|0)\d{9,10}$`
 *   - username        → 3..50
 *   - full_name       → 2..255
 *   - password        → 8..128
 *
 * Password complexity (uppercase letter + digit) is layered on top in the
 * client per Requirements 2.1.1 — backend currently accepts any 8..128 string,
 * but the spec wants the client to nudge users toward strong passwords.
 *
 * All error messages are vi-VN to match the rest of the UI.
 *
 * @see Requirements 2.4.2 (form validation, regex contracts)
 * @see Requirements 2.1.1 (register form fields and password policy)
 * @see Requirements 2.1.2 (login identifier auto-detection)
 * @see Requirements 2.1.3 (forgot password — email only)
 */

import { z } from "zod";

import { isEmail } from "@/lib/utils/isEmail";
import { isPhoneVN } from "@/lib/utils/isPhoneVN";

// ---------------------------------------------------------------------------
// Shared field schemas
// ---------------------------------------------------------------------------

/**
 * Vietnamese phone regex, mirrored from `lib/utils/isPhoneVN.ts`.
 *
 * Anchored at both ends so internal whitespace and stray characters are
 * rejected. Backend accepts 10..20 characters; this regex constrains the
 * digits-after-prefix count to {9,10}, which fits in that range.
 */
const PHONE_VN_REGEX = /^(\+84|0)\d{9,10}$/;

/**
 * Password constraint: 8..128 chars (matches backend `Field(min_length=8,
 * max_length=128)`) + at least one uppercase letter and one digit.
 */
const passwordField = z
  .string({ message: "Vui lòng nhập mật khẩu" })
  .min(8, { message: "Mật khẩu phải có ít nhất 8 ký tự" })
  .max(128, { message: "Mật khẩu không được vượt quá 128 ký tự" })
  .regex(/[A-Z]/, { message: "Mật khẩu phải có ít nhất 1 chữ in hoa" })
  .regex(/\d/, { message: "Mật khẩu phải có ít nhất 1 chữ số" });

/**
 * Email constraint: non-empty + RFC-ish email shape via zod's built-in.
 * Backend uses `EmailStr` which is stricter; we rely on the server as the
 * source of truth and keep the client check pragmatic.
 */
const emailField = z
  .string({ message: "Vui lòng nhập email" })
  .trim()
  .min(1, { message: "Vui lòng nhập email" })
  .email({ message: "Email không hợp lệ" });

// ---------------------------------------------------------------------------
// Login
// ---------------------------------------------------------------------------

/**
 * Login form schema.
 *
 * The form uses a single `identifier` field that auto-detects email vs phone
 * (see `lib/utils/classifyIdentifier.ts`). Either format is accepted; the
 * caller is responsible for routing the value into `{email}` or `{phone}` on
 * the backend payload.
 *
 * `remember` toggles a 30-day refresh-token cookie vs a session cookie
 * (handled by the `/api/auth/login` proxy — see Requirements 2.1.2 / 2.1.6).
 */
export const loginSchema = z.object({
  identifier: z
    .string({ message: "Vui lòng nhập email hoặc số điện thoại" })
    .trim()
    .min(1, { message: "Vui lòng nhập email hoặc số điện thoại" })
    .refine((value) => isEmail(value) || isPhoneVN(value), {
      message: "Vui lòng nhập email hoặc số điện thoại hợp lệ",
    }),
  password: z
    .string({ message: "Vui lòng nhập mật khẩu" })
    .min(8, { message: "Mật khẩu phải có ít nhất 8 ký tự" })
    .max(128, { message: "Mật khẩu không được vượt quá 128 ký tự" }),
  remember: z.boolean().optional(),
});

export type LoginFormValues = z.infer<typeof loginSchema>;

// ---------------------------------------------------------------------------
// Register
// ---------------------------------------------------------------------------

/**
 * Registration form schema.
 *
 * Field lengths mirror the backend `AuthRegisterRequest`. The `terms_accepted`
 * checkbox is enforced client-side only (no backend field) per Requirements
 * 2.1.1: "có checkbox đồng ý điều khoản".
 */
export const registerSchema = z.object({
  full_name: z
    .string({ message: "Vui lòng nhập họ và tên" })
    .trim()
    .min(2, { message: "Họ và tên phải có ít nhất 2 ký tự" })
    .max(255, { message: "Họ và tên không được vượt quá 255 ký tự" }),
  username: z
    .string({ message: "Vui lòng nhập tên đăng nhập" })
    .trim()
    .min(3, { message: "Tên đăng nhập phải có ít nhất 3 ký tự" })
    .max(50, { message: "Tên đăng nhập không được vượt quá 50 ký tự" }),
  email: emailField,
  phone: z
    .string({ message: "Vui lòng nhập số điện thoại" })
    .trim()
    .min(1, { message: "Vui lòng nhập số điện thoại" })
    .regex(PHONE_VN_REGEX, {
      message: "Số điện thoại không hợp lệ (vd: 0901234567 hoặc +84901234567)",
    }),
  password: passwordField,
  terms_accepted: z
    .boolean()
    .refine((value) => value === true, {
      message: "Bạn cần đồng ý với điều khoản để tiếp tục",
    }),
});

export type RegisterFormValues = z.infer<typeof registerSchema>;

// ---------------------------------------------------------------------------
// Forgot password
// ---------------------------------------------------------------------------

/**
 * Forgot-password form schema.
 *
 * Backend currently exposes only the `PasswordResetRequest` shape (email-only)
 * — Requirements 2.1.3. The UI is disabled in Phase 1 with a "Sẽ ra mắt sau"
 * tooltip; the schema is wired ahead of time so task 8.2 can bind it without
 * extra work.
 */
export const forgotSchema = z.object({
  email: emailField,
});

export type ForgotFormValues = z.infer<typeof forgotSchema>;
