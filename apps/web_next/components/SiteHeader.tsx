"use client";

/**
 * SiteHeader — public site (marketing + landing) floating navbar.
 *
 * Phase-1 wiring (task 9.1 of the web-app-functional-integration spec):
 *
 * 1. Reads `useAuth()` to drive a three-way render:
 *      - `state.status === "loading"` → render a skeleton CTA so the
 *        header never flashes anonymous controls before we know whether
 *        the visitor has a live session (Requirements 2.2.2).
 *      - `state.status === "anonymous"` → keep the original two CTA
 *        buttons ("Đăng nhập" / "Tạo tài khoản"). Each button records
 *        an intent via `useIntent().set("home")` before delegating to
 *        the page-owned `onLoginClick` callback so the LoginModal opens
 *        and the post-login redirect lands on `/app` (Requirements
 *        2.1.4 — smart redirect).
 *      - `state.status === "authenticated"` → render `<AvatarMenu>` so
 *        the user can jump into the app shell, profile, or sign out.
 *
 * 2. The LoginModal itself stays mounted at page-level (see `app/page.tsx`
 *    et al.). The header only triggers the open via `onLoginClick` so we
 *    avoid duplicating the modal in every layout the header lives under
 *    and so each page can carry its own `prefilledMessage` (e.g. the
 *    HeroVideo question on `/`).
 *
 * 3. The mobile drawer mirrors the same state machine — anonymous users
 *    see the "Tạo tài khoản" pill, authenticated users see quick links
 *    into `/app` plus a sign-out button.
 *
 * UI polish (Pre-Delivery Checklist): cursor-pointer on every clickable,
 * visible `focus-visible:ring-2`, no emojis as icons (Heroicons inline
 * SVG), floating navbar surface kept at `top-0` of `container-page` with
 * `pt-2 lg:pt-3` so the pill is offset from the viewport edge — matches
 * the rest of the marketing chrome.
 */

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Suspense, useCallback, useState } from "react";

import { AvatarMenu } from "./auth/AvatarMenu";
import { Logo } from "./Logo";
import { useAuth } from "@/lib/auth/useAuth";
import { useIntent } from "@/lib/auth/useIntent";

const NAV = [
  { href: "/", label: "Trang chủ" },
  { href: "/chat", label: "Chat AI" },
  { href: "/pricing", label: "Pricing" },
  { href: "/about", label: "Về chúng tôi" },
  { href: "/download", label: "Tải ứng dụng" },
];

export interface SiteHeaderProps {
  /**
   * Opens the page-owned `LoginModal`. Anonymous CTA buttons call this
   * after stamping `intent="home"` into `useIntent`. Optional because a
   * fully wrapped layout (e.g. when the user is already authenticated)
   * never needs to open the modal — `AvatarMenu` takes over instead.
   */
  onLoginClick?: () => void;
}

export function SiteHeader(props: SiteHeaderProps) {
  // `useSearchParams()` (called transitively via `useIntent` and the
  // `LoginRedirectHandler` stamping flow) requires a Suspense boundary
  // during static prerender (Next.js App Router 14 CSR-bailout rule).
  // Wrapping the SiteHeader content in <Suspense> keeps every page that
  // mounts the header (e.g. `/`, `/profile`, `/chat`, …) buildable
  // without forcing each page to add its own boundary.
  return (
    <Suspense fallback={
      <header className="fixed top-2 left-2 right-2 z-30 sm:top-4 sm:left-4 sm:right-4 2xl:left-1/2 2xl:right-auto 2xl:w-[calc(100%-2rem)] 2xl:max-w-[1440px] 2xl:-translate-x-1/2">
        <div className="flex h-14 items-center justify-between gap-2 rounded-pill border border-gray-200 bg-white/95 px-2.5 pl-3 shadow-card backdrop-blur supports-[backdrop-filter]:bg-white/85 sm:gap-3 sm:px-3 sm:pl-4 lg:h-16 lg:px-4 lg:pl-6 2xl:px-6 2xl:pl-8">
          <div className="cursor-pointer rounded-pill">
            <Logo />
          </div>
          <div className="h-10 w-36 animate-pulse rounded-pill bg-ink-100" />
        </div>
      </header>
    }>
      <SiteHeaderContent {...props} />
    </Suspense>
  );
}

function SiteHeaderContent({ onLoginClick }: SiteHeaderProps) {
  const [open, setOpen] = useState(false);
  const router = useRouter();
  const pathname = usePathname();
  const { state } = useAuth();
  const { set: setIntent } = useIntent();

  /**
   * Stamp `intent="home"` so the post-login redirect lands on `/app`
   * regardless of which marketing page the user was on, then ask the
   * page to open the LoginModal. Wrapping in `useCallback` lets us pass
   * the same handler to both desktop CTAs and the mobile drawer button
   * without re-rendering them on every parent state change.
   */
  const openLoginWithHomeIntent = useCallback(() => {
    setIntent("home");
    onLoginClick?.();
  }, [setIntent, onLoginClick]);

  const isAuthenticated = state.status === "authenticated";
  const isLoading = state.status === "loading";

  /**
   * Check if a nav item is active based on current pathname.
   * Strip hash fragments before comparing.
   */
  const isNavItemActive = (href: string) => {
    const cleanHref = href.split("#")[0] || "/";
    return pathname === cleanHref;
  };

  return (
    <header className="fixed top-4 left-4 right-4 z-30">
        <div className="flex h-16 items-center justify-between gap-3 rounded-pill border border-gray-200 bg-white/95 px-3 pl-4 shadow-card backdrop-blur supports-[backdrop-filter]:bg-white/85 sm:h-[72px] lg:h-20 lg:px-4 lg:pl-6 2xl:h-24">
          <Link
            href="/"
            aria-label="MediSign AI - Trang chủ"
            className="cursor-pointer rounded-pill focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2"
          >
            <Logo />
          </Link>

          <nav aria-label="Điều hướng chính" className="hidden lg:block">
            <ul className="flex items-center gap-1">
              {NAV.map((item) => {
                const isActive = isNavItemActive(item.href);
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      aria-current={isActive ? "page" : undefined}
                      className={`rounded-pill px-4 py-2 text-[15px] font-medium transition-colors duration-200 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 ${
                        isActive
                          ? "bg-brand-50 text-brand-700"
                          : "text-ink-600 hover:bg-ink-100 hover:text-ink-900"
                      }`}
                    >
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>

          {/* Desktop right rail — switches on auth state */}
          <div className="hidden items-center gap-2 lg:flex">
            {isLoading && (
              // Single neutral placeholder — same width as the
              // "Tạo tài khoản" pill so the layout doesn't reflow when
              // hydration completes.
              <div
                aria-hidden="true"
                className="h-10 w-36 animate-pulse rounded-pill bg-ink-100"
              />
            )}

            {!isLoading && !isAuthenticated && (
              <>
                <button
                  type="button"
                  onClick={openLoginWithHomeIntent}
                  className="cursor-pointer rounded-pill px-4 py-2 text-[15px] font-medium text-ink-700 transition-colors duration-200 hover:text-brand-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2"
                  aria-haspopup="dialog"
                >
                  Đăng nhập
                </button>
                <button
                  type="button"
                  onClick={openLoginWithHomeIntent}
                  className="inline-flex cursor-pointer items-center gap-1.5 rounded-pill bg-brand px-5 py-2.5 text-[15px] font-semibold text-white shadow-soft transition-colors duration-200 hover:bg-brand-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2"
                  aria-haspopup="dialog"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path
                      d="M12 5v14M5 12h14"
                      stroke="currentColor"
                      strokeWidth="2.4"
                      strokeLinecap="round"
                    />
                  </svg>
                  Tạo tài khoản
                </button>
              </>
            )}

            {isAuthenticated && <AvatarMenu user={state.user} />}
          </div>

          <button
            type="button"
            aria-label={open ? "Đóng menu" : "Mở menu"}
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
            className="inline-flex h-11 w-11 cursor-pointer items-center justify-center rounded-pill border border-ink-200 transition-colors duration-200 hover:bg-ink-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 lg:hidden"
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              {open ? (
                <path d="M6 6l12 12M6 18L18 6" stroke="#0F172A" strokeWidth="2" strokeLinecap="round" />
              ) : (
                <path d="M4 7h16M4 12h16M4 17h16" stroke="#0F172A" strokeWidth="2" strokeLinecap="round" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile drawer — mirrors the desktop auth state machine */}
        {open && (
          <div className="mt-2 rounded-card border border-gray-200 bg-white shadow-card lg:hidden">
            <nav aria-label="Điều hướng phụ" className="p-3">
              <ul className="flex flex-col">
                {NAV.map((item) => (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className="block cursor-pointer rounded-pill px-4 py-3 text-base font-medium text-ink-800 transition-colors duration-200 hover:bg-ink-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2"
                      onClick={() => setOpen(false)}
                    >
                      {item.label}
                    </Link>
                  </li>
                ))}

                {/* Auth-aware footer of the mobile drawer */}
                {isLoading && (
                  <li className="px-2 pt-2">
                    <div
                      aria-hidden="true"
                      className="h-12 w-full animate-pulse rounded-pill bg-ink-100"
                    />
                  </li>
                )}

                {!isLoading && !isAuthenticated && (
                  <li className="px-2 pt-2">
                    <button
                      type="button"
                      className="btn-primary w-full cursor-pointer"
                      onClick={() => {
                        setOpen(false);
                        openLoginWithHomeIntent();
                      }}
                    >
                      Tạo tài khoản
                    </button>
                  </li>
                )}

                {isAuthenticated && (
                  <>
                    <li className="px-2 pt-2">
                      <Link
                        href="/chat"
                        className="btn-primary w-full cursor-pointer"
                        onClick={() => setOpen(false)}
                      >
                        Mở Chat AI
                      </Link>
                    </li>
                    <li className="px-2 pt-2">
                      <Link
                        href="/profile"
                        className="block cursor-pointer rounded-pill border border-ink-200 px-4 py-3 text-center text-base font-medium text-ink-800 transition-colors duration-200 hover:bg-ink-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2"
                        onClick={() => setOpen(false)}
                      >
                        Hồ sơ của tôi
                      </Link>
                    </li>
                  </>
                )}
              </ul>
            </nav>
          </div>
        )}
    </header>
  );
}
