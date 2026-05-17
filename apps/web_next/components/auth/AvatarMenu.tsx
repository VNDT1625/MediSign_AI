"use client";

/**
 * AvatarMenu — circular initials avatar that opens a dropdown panel with
 * navigation shortcuts and a sign-out action for the authenticated user.
 *
 * Mounted by `components/SiteHeader.tsx` whenever `useAuth().isAuthenticated`
 * is true (replacing the anonymous "Đăng nhập / Tạo tài khoản" pair). Owns
 * its own open/close state, keyboard handling, and click-outside detection
 * so the surrounding header layout stays presentational.
 *
 * UX contract (per `.kiro/steering/ui-ux-pro-max/SKILL.md` Pre-Delivery
 * Checklist + design.md → "SiteHeader: thay đổi"):
 *   - Avatar shows initials computed from `user.full_name` (Vietnamese
 *     diacritics stripped before extracting letters so "Nguyễn Văn A"
 *     correctly renders as "NA", not "NẾ" or similar).
 *   - Glass-surface dropdown panel: `bg-white/95` + `ring-1 ring-ink-900/5`
 *     + soft shadow — visible in both light and dark backdrops.
 *   - Body text is `text-ink-900`; muted helper text is `text-ink-600`
 *     (4.5:1 minimum contrast in light mode).
 *   - All clickable elements get `cursor-pointer`. Focusable elements get
 *     a visible `focus-visible:ring-2 ring-brand ring-offset-1` so keyboard
 *     users can see where they are.
 *   - Icons are inline Heroicons SVGs (no emoji). They sit in fixed-size
 *     boxes (`h-5 w-5`) so the menu rows don't shift on hover.
 *   - All transitions are scoped under `motion-safe:` so users with
 *     `prefers-reduced-motion: reduce` get instant state changes.
 *
 * Keyboard model:
 *   - `Esc` closes the menu and returns focus to the avatar button.
 *   - `Tab` from the last menu item wraps to the first (and vice versa
 *     for Shift+Tab) so focus is trapped while the menu is open. This
 *     mirrors the focus trap used by `LoginModal` and matches WAI-ARIA
 *     authoring practice for menu widgets.
 *   - A click on the document outside the menu (and outside the avatar
 *     button) closes the menu. Touch and pointer events both surface as
 *     `mousedown` here — using `mousedown` instead of `click` ensures we
 *     close before a focused control loses its native click handling.
 *
 * Logout flow:
 *   1. Call `onLogout` if the parent provided one (lets tests inject a
 *      stub without spinning up `AuthProvider`); otherwise call
 *      `useAuth().logout()` which clears the in-memory access token,
 *      best-effort hits `/api/auth/logout`, and transitions the auth
 *      state machine to `anonymous`.
 *   2. Redirect to `/` via `router.push("/")` so the user lands on the
 *      public landing page. We never use `router.replace` here because
 *      the back button should still take them to whatever public page
 *      they came from before signing in.
 *
 * @see Requirements 2.1.5 (logout from avatar menu redirects to "/").
 * @see Requirements 2.4.3 (cursor-pointer, focus rings, no emoji icons,
 *   keyboard navigability per Pre-Delivery Checklist).
 */

import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  useCallback,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent as ReactKeyboardEvent,
} from "react";
import type { AuthUserResponse } from "@medisign/shared-contracts";

import { useAuth } from "@/lib/auth/useAuth";

// ---------------------------------------------------------------------------
// Initials computation
// ---------------------------------------------------------------------------

/**
 * Strip Vietnamese diacritics (and any other Unicode combining marks) so
 * we can extract reliable initial letters from names like "Nguyễn Văn A".
 *
 * `String.prototype.normalize("NFD")` decomposes combined characters into
 * a base + a sequence of combining marks; the regex then deletes every
 * code point in the "Combining Diacritical Marks" range (U+0300..U+036F).
 * The Vietnamese-specific letter `đ`/`Đ` is NOT a combining form, so we
 * map it explicitly to its ASCII counterpart.
 *
 * The function never throws and returns an empty string for an empty
 * input — both behaviors are relied on by `computeInitials` below.
 */
function stripDiacritics(input: string): string {
  return input
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/đ/g, "d")
    .replace(/Đ/g, "D");
}

/**
 * Derive a 1-2 character avatar label from a full name.
 *
 * Rules (matching task 9.2 spec):
 *   - Trim whitespace and split on runs of whitespace.
 *   - Multi-word names → first letter of the first word + first letter
 *     of the last word, both uppercased ("Nguyễn Văn A" → "NA").
 *   - Single-word names → first 2 characters uppercased
 *     ("Hoa" → "HO"). If the single word has a single character we
 *     return just that character; we never pad with placeholders.
 *   - Empty / whitespace-only input → "?" so the avatar still renders
 *     a recognizable shape rather than collapsing to an empty button.
 *
 * Diacritics are stripped *only* for the purpose of picking initials so
 * the visible label stays in plain ASCII (which keeps the circle visually
 * clean and avoids issues with combining marks rendering twice).
 */
export function computeInitials(fullName: string): string {
  const cleaned = stripDiacritics((fullName ?? "").trim());
  if (cleaned.length === 0) return "?";

  const parts = cleaned.split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";

  if (parts.length === 1) {
    const sole = parts[0];
    return sole.slice(0, 2).toUpperCase();
  }

  const first = parts[0]!.charAt(0);
  const last = parts[parts.length - 1]!.charAt(0);
  return (first + last).toUpperCase();
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export interface AvatarMenuProps {
  /**
   * Authenticated user profile, used to compute initials and to render
   * the header card inside the dropdown. The full `AuthUserResponse`
   * shape is required so `email` and `account_type` are available for
   * future extensions (e.g. role badges) without breaking the prop API.
   */
  user: AuthUserResponse;
  /**
   * Optional override for the logout action. When omitted, the component
   * falls back to `useAuth().logout()`. Tests use this to stub the action
   * without mounting `AuthProvider`.
   */
  onLogout?: () => void | Promise<void>;
}

/**
 * Inline Heroicons used by the menu rows. They live as small components
 * so the JSX in `AvatarMenu` stays focused on layout. All icons share a
 * 24×24 viewBox + 1.5 stroke width so they read as a single set.
 */
const HomeIcon = (props: { className?: string }) => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={1.5}
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    className={props.className}
  >
    <path d="M2.25 12 12 3l9.75 9" />
    <path d="M4.5 10.5V21h15V10.5" />
    <path d="M9.75 21v-6h4.5v6" />
  </svg>
);

const UserCircleIcon = (props: { className?: string }) => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={1.5}
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    className={props.className}
  >
    <circle cx="12" cy="12" r="9" />
    <circle cx="12" cy="10" r="3.25" />
    <path d="M5.5 19.25c1.5-2.75 4-4.25 6.5-4.25s5 1.5 6.5 4.25" />
  </svg>
);

const LogoutIcon = (props: { className?: string }) => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={1.5}
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    className={props.className}
  >
    <path d="M15.75 9V6.75A2.25 2.25 0 0 0 13.5 4.5h-6A2.25 2.25 0 0 0 5.25 6.75v10.5a2.25 2.25 0 0 0 2.25 2.25h6a2.25 2.25 0 0 0 2.25-2.25V15" />
    <path d="M9 12h12" />
    <path d="m18 8.5 3.5 3.5L18 15.5" />
  </svg>
);

export function AvatarMenu({ user, onLogout }: AvatarMenuProps) {
  const auth = useAuth();
  const router = useRouter();
  const menuId = useId();

  const [open, setOpen] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  // Refs to (a) detect outside clicks and (b) implement the focus trap.
  // `containerRef` wraps both the avatar button and the dropdown so a
  // single ref can answer "did the click happen inside our widget?".
  const containerRef = useRef<HTMLDivElement | null>(null);
  const buttonRef = useRef<HTMLButtonElement | null>(null);
  const menuRef = useRef<HTMLDivElement | null>(null);
  const firstItemRef = useRef<HTMLAnchorElement | null>(null);
  const logoutItemRef = useRef<HTMLButtonElement | null>(null);

  const initials = useMemo(() => computeInitials(user.full_name), [
    user.full_name,
  ]);

  const close = useCallback(() => {
    setOpen(false);
  }, []);

  // Close on Esc + return focus to the avatar button so screen reader
  // users don't get stranded after dismiss. We listen on `document` (not
  // on the menu itself) because focus may legitimately leave the menu
  // root during the trap unwind.
  useEffect(() => {
    if (!open) return;

    function onKeyDown(event: globalThis.KeyboardEvent) {
      if (event.key === "Escape") {
        event.stopPropagation();
        close();
        // Defer the focus restore so React commits the close state
        // before the focus call hits a now-detached element.
        requestAnimationFrame(() => buttonRef.current?.focus());
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, close]);

  // Click-outside-to-close. Use `mousedown` so we close before any focus
  // race with a freshly-clicked external control.
  useEffect(() => {
    if (!open) return;

    function onPointerDown(event: MouseEvent) {
      const target = event.target as Node | null;
      if (!target) return;
      if (!containerRef.current) return;
      if (containerRef.current.contains(target)) return;
      close();
    }

    document.addEventListener("mousedown", onPointerDown);
    return () => document.removeEventListener("mousedown", onPointerDown);
  }, [open, close]);

  // When the menu opens, move keyboard focus to the first menu item so
  // arrow-key / Tab navigation has a sensible starting point. Skip this
  // for pointer-driven opens? Per WAI-ARIA Authoring Practices for menus
  // it's idiomatic to focus the first item on open regardless of input
  // modality, so we do it unconditionally.
  useEffect(() => {
    if (!open) return;
    // `requestAnimationFrame` waits for the panel to actually mount.
    const rAF = requestAnimationFrame(() => {
      firstItemRef.current?.focus();
    });
    return () => cancelAnimationFrame(rAF);
  }, [open]);

  // Tab-cycle focus trap inside the open menu. Implemented via a single
  // `keydown` handler attached to the menu container so we only intercept
  // Tab when the user is already inside the widget.
  const handleMenuKeyDown = useCallback(
    (event: ReactKeyboardEvent<HTMLDivElement>) => {
      if (event.key !== "Tab") return;
      const root = menuRef.current;
      if (!root) return;

      const focusables = root.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])',
      );
      if (focusables.length === 0) return;

      const first = focusables[0]!;
      const last = focusables[focusables.length - 1]!;
      const active = document.activeElement as HTMLElement | null;

      if (event.shiftKey) {
        if (active === first || !root.contains(active)) {
          event.preventDefault();
          last.focus();
        }
        return;
      }

      if (active === last) {
        event.preventDefault();
        first.focus();
      }
    },
    [],
  );

  const handleLogout = useCallback(async () => {
    if (isLoggingOut) return;
    setIsLoggingOut(true);
    try {
      // Prefer the explicit override when present; fall back to the auth
      // context. Both branches are wrapped in the same try so the
      // redirect happens even if the action throws (best-effort logout
      // per design.md → A5).
      if (onLogout) {
        await onLogout();
      } else {
        await auth.logout();
      }
    } finally {
      close();
      setIsLoggingOut(false);
      router.push("/");
    }
  }, [auth, close, isLoggingOut, onLogout, router]);

  return (
    <div ref={containerRef} className="relative">
      <button
        ref={buttonRef}
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-controls={open ? menuId : undefined}
        aria-label={`Tài khoản của ${user.full_name}`}
        className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-brand text-[14px] font-semibold text-white shadow-soft ring-1 ring-ink-900/5 transition-colors duration-200 cursor-pointer hover:bg-brand-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 motion-reduce:transition-none"
      >
        <span aria-hidden="true">{initials}</span>
      </button>

      {open && (
        <div
          id={menuId}
          ref={menuRef}
          role="menu"
          aria-label="Tài khoản"
          onKeyDown={handleMenuKeyDown}
          className="absolute right-0 top-full z-40 mt-2 w-64 origin-top-right rounded-card border border-ink-200 bg-white/95 p-2 shadow-card ring-1 ring-ink-900/5 backdrop-blur supports-[backdrop-filter]:bg-white/85 motion-safe:animate-fade-in motion-reduce:animate-none"
        >
          <div className="px-3 pb-2 pt-1">
            <p
              className="truncate text-[14px] font-semibold text-ink-900"
              title={user.full_name}
            >
              {user.full_name}
            </p>
            <p
              className="truncate text-[12px] text-ink-600"
              title={user.email}
            >
              {user.email}
            </p>
          </div>

          <div className="my-1 h-px bg-ink-200" role="none" />

          <Link
            ref={firstItemRef}
            role="menuitem"
            href="/app"
            onClick={close}
            className="flex items-center gap-3 rounded-card px-3 py-2 text-[14px] font-medium text-ink-900 transition-colors duration-150 cursor-pointer hover:bg-ink-100 focus-visible:bg-ink-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-1 motion-reduce:transition-none"
          >
            <HomeIcon className="h-5 w-5 flex-none text-ink-600" />
            <span>Trang chủ ứng dụng</span>
          </Link>

          <Link
            role="menuitem"
            href="/app/profile"
            onClick={close}
            className="flex items-center gap-3 rounded-card px-3 py-2 text-[14px] font-medium text-ink-900 transition-colors duration-150 cursor-pointer hover:bg-ink-100 focus-visible:bg-ink-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-1 motion-reduce:transition-none"
          >
            <UserCircleIcon className="h-5 w-5 flex-none text-ink-600" />
            <span>Hồ sơ cá nhân</span>
          </Link>

          <div className="my-1 h-px bg-ink-200" role="none" />

          <button
            ref={logoutItemRef}
            role="menuitem"
            type="button"
            onClick={handleLogout}
            disabled={isLoggingOut}
            aria-busy={isLoggingOut ? "true" : "false"}
            className="flex w-full items-center gap-3 rounded-card px-3 py-2 text-left text-[14px] font-medium text-danger transition-colors duration-150 cursor-pointer hover:bg-danger-soft focus-visible:bg-danger-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-danger focus-visible:ring-offset-1 disabled:cursor-not-allowed disabled:opacity-60 motion-reduce:transition-none"
          >
            <LogoutIcon className="h-5 w-5 flex-none" />
            <span>{isLoggingOut ? "Đang đăng xuất..." : "Đăng xuất"}</span>
          </button>
        </div>
      )}
    </div>
  );
}
