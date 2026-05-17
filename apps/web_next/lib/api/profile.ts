/**
 * `lib/api/profile.ts` — Phase-1 façade for the `/app/profile` page.
 *
 * The backend currently only exposes read access (`GET /auth/me`) and
 * password change (`POST /auth/change-password`) — both of which live on
 * the auth surface. This module re-exports them under `profile.*` names
 * so callers can write `profile.me()` / `profile.changePassword()` in a
 * domain-appropriate idiom, plus a couple of small UI helpers (avatar
 * initials, display-name fallback) that don't deserve their own file.
 *
 * Phase 2 will add a real `PATCH /auth/me` endpoint for editing fields
 * beyond password (full_name, phone, …); the `updateProfile()` wrapper
 * is intentionally omitted here so callers fail at compile time when
 * they reach for the not-yet-built capability.
 *
 * @see Requirements 2.3.3 (profile page wiring), 2.5.1 (shared contracts).
 * @see Design — "Page-by-Page Wiring → /app/profile" in design.md.
 */

import type { AuthUserResponse } from "@medisign/shared-contracts";

// Re-exports: `profile.me()` is the canonical name on this page even
// though the implementation lives on the auth router.
export { changePassword, me } from "./auth";

// ---------------------------------------------------------------------------
// UI helpers
// ---------------------------------------------------------------------------

/**
 * Compute initials for an avatar fallback from a user's `full_name`.
 *
 * Returns up to 2 uppercase characters drawn from the first and last
 * "words" (whitespace-separated) of the name. Empty / whitespace-only
 * inputs collapse to `"?"` so the avatar bubble is never blank.
 *
 * Examples:
 *   getInitials("Nguyễn Văn A")    → "NA"
 *   getInitials("Trần Thị Bình")   → "TB"
 *   getInitials("Madonna")          → "M"
 *   getInitials("  ")               → "?"
 */
export function getInitials(fullName: string | null | undefined): string {
  if (typeof fullName !== "string") return "?";
  const parts = fullName.trim().split(/\s+/).filter((p) => p.length > 0);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0]!.charAt(0).toUpperCase();
  const first = parts[0]!.charAt(0);
  const last = parts[parts.length - 1]!.charAt(0);
  return (first + last).toUpperCase();
}

/**
 * Pick the best human-readable label for a user. Prefers `full_name`,
 * falls back to `username`, then `email`, then a generic fallback so
 * UI components never render `undefined`.
 */
export function getDisplayName(user: AuthUserResponse | null | undefined): string {
  if (!user) return "Người dùng";
  const fullName = user.full_name?.trim();
  if (fullName) return fullName;
  const username = user.username?.trim();
  if (username) return username;
  const email = user.email?.trim();
  if (email) return email;
  return "Người dùng";
}

// ---------------------------------------------------------------------------
// Phase 2 placeholder
// ---------------------------------------------------------------------------

// TODO(phase-2): wire `updateProfile()` once `PATCH /auth/me` exists on
// the backend. The UI in `/app/profile` currently renders the
// "Cập nhật full_name" control as disabled with a "Phase 2" tooltip.
