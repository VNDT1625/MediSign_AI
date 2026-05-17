"use client";

/**
 * `/app/profile` — authenticated user profile view.
 *
 * Fetches the current user via `GET /auth/me` using React Query and
 * renders: initials avatar, full_name, username, email, phone,
 * account_type, and created_at (formatted vi-VN).
 *
 * "Cập nhật họ tên" is rendered disabled with a "Phase 2" tooltip —
 * the PATCH /auth/me endpoint is not yet available.
 *
 * @see Requirements 2.3.3 (profile view + change password).
 */

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";

import { DesktopAppHeader } from "@/components/desktop/DesktopAppHeader";
import { ChangePasswordCard } from "@/components/profile/ChangePasswordCard";
import { useAuth } from "@/lib/auth/useAuth";
import * as api from "@/lib/api/auth";
import type { AuthUserResponse } from "@medisign/shared-contracts";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Compute initials from a full name.
 * "Nguyen Van A" → "NVA" (first letter of each word, max 3)
 * "Nguyen A"     → "NA"
 * ""             → "U"
 */
function getInitials(fullName: string): string {
  const parts = fullName.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "U";
  return parts
    .slice(0, 3)
    .map((p) => p[0]?.toUpperCase() ?? "")
    .join("");
}

/**
 * Format an ISO-8601 timestamp as Vietnamese long date.
 * e.g. "2024-01-15T10:30:00Z" → "15 tháng 1, 2024"
 */
function formatDateVN(isoString: string): string {
  try {
    const date = new Date(isoString);
    return date.toLocaleDateString("vi-VN", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  } catch {
    return isoString;
  }
}

/** Human-readable label for account_type. */
function accountTypeLabel(type: AuthUserResponse["account_type"]): string {
  switch (type) {
    case "doctor":
      return "Bác sĩ";
    case "admin":
      return "Quản trị viên";
    default:
      return "Người dùng";
  }
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

/** Gradient initials avatar — matches the DesktopAppHeader Avatar style. */
function InitialsAvatar({ name, size = "lg" }: { name: string; size?: "lg" | "sm" }) {
  const initials = getInitials(name);
  const sizeClass =
    size === "lg"
      ? "h-20 w-20 text-2xl ring-4"
      : "h-12 w-12 text-base ring-2";
  return (
    <span
      aria-hidden="true"
      className={`grid flex-none place-items-center rounded-full bg-gradient-to-br from-brand to-brand-700 font-bold text-white ring-white ${sizeClass}`}
    >
      {initials}
    </span>
  );
}

/** A single labelled info row. */
function InfoRow({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div className="flex flex-col gap-0.5 py-3 sm:flex-row sm:items-center sm:gap-4">
      <dt className="w-full text-sm font-medium text-slate-500 sm:w-40 sm:flex-none">{label}</dt>
      <dd className="text-sm font-semibold text-slate-900">
        {value ?? <span className="font-normal italic text-slate-400">Chưa cập nhật</span>}
      </dd>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Loading skeleton
// ---------------------------------------------------------------------------

function ProfileSkeleton() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true" aria-label="Đang tải hồ sơ…">
      {/* Avatar + name block */}
      <div className="flex items-center gap-5">
        <div className="h-20 w-20 flex-none rounded-full bg-slate-200" />
        <div className="space-y-2">
          <div className="h-5 w-40 rounded bg-slate-200" />
          <div className="h-4 w-28 rounded bg-slate-200" />
        </div>
      </div>
      {/* Info rows */}
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex gap-4">
          <div className="h-4 w-32 rounded bg-slate-200" />
          <div className="h-4 w-48 rounded bg-slate-200" />
        </div>
      ))}
      {/* Button */}
      <div className="h-10 w-48 rounded-lg bg-slate-200" />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Error state
// ---------------------------------------------------------------------------

function ProfileError({ onRetry }: { onRetry: () => void }) {
  return (
    <div
      role="alert"
      className="flex flex-col items-center gap-4 rounded-xl border border-red-200 bg-red-50 px-6 py-10 text-center"
    >
      {/* Heroicons: exclamation-circle */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-10 w-10 text-red-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={1.6}
        aria-hidden="true"
      >
        <circle cx="12" cy="12" r="9" />
        <path strokeLinecap="round" d="M12 8v4M12 16h.01" />
      </svg>
      <p className="text-sm font-semibold text-red-700">
        Không thể tải thông tin hồ sơ. Vui lòng thử lại.
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="rounded-lg bg-red-600 px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-red-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2 cursor-pointer"
      >
        Thử lại
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Profile content
// ---------------------------------------------------------------------------

function ProfileContent({ user }: { user: AuthUserResponse }) {
  return (
    <div className="space-y-6">
      {/* Avatar + name header */}
      <div className="flex items-center gap-5">
        <InitialsAvatar name={user.full_name} size="lg" />
        <div>
          <h1 className="text-xl font-bold text-slate-900">{user.full_name}</h1>
          <p className="text-sm text-slate-500">@{user.username}</p>
        </div>
      </div>

      {/* Info card */}
      <div className="rounded-xl border border-gray-200 bg-white/80 px-6 shadow-sm">
        <dl className="divide-y divide-gray-100">
          <InfoRow label="Họ và tên" value={user.full_name} />
          <InfoRow label="Tên đăng nhập" value={user.username} />
          <InfoRow label="Email" value={user.email} />
          <InfoRow label="Số điện thoại" value={user.phone} />
          <InfoRow label="Loại tài khoản" value={accountTypeLabel(user.account_type)} />
          <InfoRow label="Ngày tạo tài khoản" value={formatDateVN(user.created_at)} />
        </dl>
      </div>

      {/* "Cập nhật họ tên" — disabled, Phase 2 tooltip */}
      <div className="group relative inline-block">
        <button
          type="button"
          disabled
          aria-disabled="true"
          aria-describedby="update-name-tooltip"
          className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-100 px-5 py-2.5 text-sm font-semibold text-slate-400 cursor-not-allowed select-none"
        >
          {/* Heroicons: pencil-square */}
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.8}
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M16.862 3.487a2.25 2.25 0 1 1 3.182 3.182L7.5 19.213l-4 1 1-4 12.362-12.726z"
            />
          </svg>
          Cập nhật họ tên
        </button>

        {/* Tooltip */}
        <span
          id="update-name-tooltip"
          role="tooltip"
          className="pointer-events-none absolute bottom-full left-1/2 mb-2 -translate-x-1/2 whitespace-nowrap rounded-md bg-slate-800 px-3 py-1.5 text-xs font-medium text-white opacity-0 shadow-lg transition-opacity duration-150 group-hover:opacity-100 group-focus-within:opacity-100"
        >
          Phase 2
          {/* Tooltip arrow */}
          <span
            aria-hidden="true"
            className="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent border-t-slate-800"
          />
        </span>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function ProfilePage() {
  const { state, logout } = useAuth();
  const router = useRouter();

  const {
    data: user,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["me"],
    queryFn: () => api.me(),
    // Keep the profile fresh for 5 min (matches queryClient default).
    // If the auth state is not yet authenticated, skip the query to
    // avoid a 401 before the token is seeded.
    enabled: state.status === "authenticated",
  });

  // Derive the display name for the header: prefer query data, fall back
  // to the auth state user, then a generic placeholder.
  const displayName =
    user?.full_name ??
    (state.status === "authenticated" ? state.user.full_name : "Người dùng");

  async function handleLogout() {
    await logout();
    router.push("/");
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <DesktopAppHeader
        pathname="/app/profile"
        user={{ name: displayName }}
        onLogout={handleLogout}
      />

      <main id="main" className="mx-auto max-w-2xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-slate-900">Hồ sơ cá nhân</h2>
          <p className="mt-1 text-sm text-slate-600">
            Thông tin tài khoản của bạn trên MediSign AI.
          </p>
        </div>

        {isLoading && <ProfileSkeleton />}

        {isError && !isLoading && (
          <ProfileError onRetry={() => void refetch()} />
        )}

        {user && !isLoading && (
          <div className="space-y-6">
            <ProfileContent user={user} />
            <ChangePasswordCard />
          </div>
        )}
      </main>
    </div>
  );
}
