"use client";

// Header dành riêng cho Desktop App (Tauri shell, dùng chung web frontend).
// Theo readme UI_Mau: "desktop = header của mobile và content của web"
// Thiết kế match screenshot Soul Garden:
//  • Logo + tagline "Chăm sóc sức khoẻ mỗi ngày"
//  • Pill nav 5 tab có icon: Home / Chat AI / Tủ thuốc / Soul Garden / Hồ sơ
//  • Bell + avatar người dùng (có tên)
// KHÔNG dùng cho web marketing (web dùng SiteHeader.tsx).

import Link from "next/link";
import { useState } from "react";

type NavItem = {
  href: string;
  label: string;
  icon: React.ReactNode;
  match: (path: string) => boolean;
};

const NAV: NavItem[] = [
  {
    href: "/app",
    label: "Home",
    icon: <HomeIcon />,
    match: (p) => p === "/app" || p === "/app/"
  },
  {
    href: "/app/chat",
    label: "Chat AI",
    icon: <ChatIcon />,
    match: (p) => p.startsWith("/app/chat")
  },
  {
    href: "/app/medicine",
    label: "Tủ thuốc",
    icon: <MedicineIcon />,
    match: (p) => p.startsWith("/app/medicine")
  },
  {
    href: "/app/soul-garden",
    label: "Soul Garden",
    icon: <LeafIcon />,
    match: (p) => p.startsWith("/app/soul-garden")
  },
  {
    href: "/app/profile",
    label: "Hồ sơ",
    icon: <UserIcon />,
    match: (p) => p.startsWith("/app/profile")
  }
];

export type DesktopUser = {
  name: string;
  avatarUrl?: string;
};

export function DesktopAppHeader({
  pathname = "/app",
  user,
  notificationCount = 0,
  overlay = false,
  onLogout,
  onOpenNotifications
}: {
  pathname?: string;
  user: DesktopUser;
  notificationCount?: number;
  /** Khi true: header nằm absolute, đè lên hero (dùng cho trang Home có video). */
  overlay?: boolean;
  onLogout?: () => void;
  onOpenNotifications?: () => void;
}) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header
      className={
        overlay
          ? "absolute top-0 left-0 right-0 z-30 w-full"
          : "sticky top-0 z-30 w-full"
      }
    >
      <div className="container-page pt-3 lg:pt-4">
        <div className="flex h-[68px] items-center justify-between gap-3 rounded-pill border border-ink-200/70 bg-white/95 px-3 pl-4 shadow-card backdrop-blur supports-[backdrop-filter]:bg-white/85 lg:px-4 lg:pl-6">
          {/* Left — logo + tagline */}
          <Link
            href="/app"
            aria-label="MediSign AI - Trang chủ ứng dụng"
            className="flex items-center gap-2.5 cursor-pointer"
          >
            <span className="grid h-10 w-10 flex-none place-items-center rounded-xl bg-gradient-to-br from-brand to-brand-700 text-white shadow-soft">
              <ShieldPlusIcon />
            </span>
            <span className="hidden flex-col leading-none sm:flex">
              <span className="text-[16px] font-bold tracking-tight text-ink-900">
                MediSign <span className="text-brand">AI</span>
              </span>
              <span className="mt-1 inline-flex items-center gap-1 text-[11px] font-medium text-ink-500">
                <span
                  aria-hidden="true"
                  className="h-1.5 w-1.5 rounded-full bg-success"
                />
                Chăm sóc sức khoẻ mỗi ngày
              </span>
            </span>
          </Link>

          {/* Center — pill nav */}
          <nav aria-label="Điều hướng chính" className="hidden lg:block">
            <ul className="flex items-center gap-1">
              {NAV.map((item) => {
                const active = item.match(pathname);
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      aria-current={active ? "page" : undefined}
                      className={`inline-flex items-center gap-2 rounded-pill px-4 py-2 text-[14px] font-semibold transition-colors ${
                        active
                          ? "bg-brand-50 text-brand-700"
                          : "text-ink-600 hover:bg-ink-100 hover:text-ink-900"
                      }`}
                    >
                      <span
                        className={active ? "text-brand-700" : "text-ink-500"}
                        aria-hidden="true"
                      >
                        {item.icon}
                      </span>
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>

          {/* Right — bell + avatar */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              aria-label={
                notificationCount > 0
                  ? `Thông báo, ${notificationCount} chưa đọc`
                  : "Thông báo"
              }
              onClick={onOpenNotifications}
              className="relative inline-flex h-10 w-10 items-center justify-center rounded-pill text-ink-500 hover:bg-ink-100 hover:text-ink-800 cursor-pointer"
            >
              <BellIcon />
              {notificationCount > 0 && (
                <span
                  aria-hidden="true"
                  className="absolute right-1.5 top-1.5 grid h-4 min-w-4 place-items-center rounded-pill bg-accent px-1 text-[10px] font-bold text-white ring-2 ring-white"
                >
                  {notificationCount > 9 ? "9+" : notificationCount}
                </span>
              )}
            </button>

            <div className="relative">
              <button
                type="button"
                onClick={() => setMenuOpen((v) => !v)}
                aria-haspopup="menu"
                aria-expanded={menuOpen}
                className="inline-flex items-center gap-2 rounded-pill border border-ink-200 bg-white px-2 py-1.5 pr-3 hover:border-brand cursor-pointer"
              >
                <Avatar name={user.name} src={user.avatarUrl} />
                <span className="hidden text-[14px] font-semibold text-ink-900 sm:inline">
                  {user.name}
                </span>
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  aria-hidden="true"
                  className="text-ink-500"
                >
                  <path
                    d="M6 9l6 6 6-6"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>

              {menuOpen && (
                <>
                  <button
                    type="button"
                    aria-label="Đóng menu"
                    onClick={() => setMenuOpen(false)}
                    className="fixed inset-0 z-10 cursor-default"
                    tabIndex={-1}
                  />
                  <div
                    role="menu"
                    className="absolute right-0 top-[calc(100%+8px)] z-20 w-56 overflow-hidden rounded-card border border-ink-200 bg-white shadow-card"
                  >
                    <Link
                      href="/app/profile"
                      role="menuitem"
                      onClick={() => setMenuOpen(false)}
                      className="block px-4 py-3 text-[14px] text-ink-800 hover:bg-ink-100"
                    >
                      Hồ sơ của tôi
                    </Link>
                    <Link
                      href="/app/profile?tab=settings"
                      role="menuitem"
                      onClick={() => setMenuOpen(false)}
                      className="block px-4 py-3 text-[14px] text-ink-800 hover:bg-ink-100"
                    >
                      Cài đặt
                    </Link>
                    <button
                      role="menuitem"
                      type="button"
                      onClick={() => {
                        setMenuOpen(false);
                        onLogout?.();
                      }}
                      className="block w-full border-t border-ink-200 px-4 py-3 text-left text-[14px] text-ink-800 hover:bg-ink-100 cursor-pointer"
                    >
                      Đăng xuất
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

/* ----------------------- Avatar ----------------------- */

function Avatar({ name, src }: { name: string; src?: string }) {
  if (src) {
    // eslint-disable-next-line @next/next/no-img-element
    return (
      <img
        src={src}
        alt=""
        className="h-9 w-9 rounded-pill object-cover ring-2 ring-white"
      />
    );
  }
  const initials = name
    .split(/\s+/)
    .filter(Boolean)
    .slice(-2)
    .map((s) => s[0]?.toUpperCase() ?? "")
    .join("");
  return (
    <span
      aria-hidden="true"
      className="grid h-9 w-9 place-items-center rounded-pill bg-gradient-to-br from-brand to-brand-700 text-[12px] font-bold text-white ring-2 ring-white"
    >
      {initials || "U"}
    </span>
  );
}

/* ------------------------ Icons ----------------------- */

function ShieldPlusIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M12 3l8 3v5c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-3z"
        fill="currentColor"
        fillOpacity="0.18"
        stroke="currentColor"
        strokeWidth="1.6"
      />
      <path d="M12 8v6M9 11h6" stroke="white" strokeWidth="2.4" strokeLinecap="round" />
    </svg>
  );
}

function HomeIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M4 11l8-7 8 7v9a1 1 0 0 1-1 1h-4v-6h-6v6H5a1 1 0 0 1-1-1v-9z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function ChatIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M5 5h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-7l-5 4v-4H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
      <circle cx="9" cy="11.5" r="1" fill="currentColor" />
      <circle cx="13" cy="11.5" r="1" fill="currentColor" />
      <circle cx="17" cy="11.5" r="1" fill="currentColor" />
    </svg>
  );
}

function MedicineIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="3.5" y="6" width="17" height="13.5" rx="2.5" stroke="currentColor" strokeWidth="1.8" />
      <path d="M3.5 11h17" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path
        d="M9 3.5h6M12 14v3.5M10.25 15.75h3.5"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

function LeafIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M20 4c-9 0-15 5-15 12 0 2 0 3 1 4 3-7 8-10 12-11-3 2-7 5-9 11 6 0 11-3 12-10 1-3 0-5-1-6z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function UserIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

function BellIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M6 9a6 6 0 1 1 12 0c0 4 1.5 6 2 6.5H4c.5-.5 2-2.5 2-6.5z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
      <path
        d="M10 19a2 2 0 0 0 4 0"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}
