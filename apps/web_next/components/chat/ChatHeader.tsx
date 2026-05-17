"use client";

// Header riêng cho trang Chat AI — dùng pattern floating-pill giống SiteHeader
// (mục "Floating navbar" trong rule UI), nhưng tab "Chat AI" đang active.

import Link from "next/link";
import { Logo } from "@/components/Logo";
import { HelpIcon } from "./icons";

const NAV = [
  { href: "/", label: "Trang chủ" },
  { href: "/chat", label: "Chat AI", active: true },
  { href: "/#pricing", label: "Bảng giá" },
  { href: "/about", label: "Giới thiệu" },
  { href: "/download", label: "Tải ứng dụng" }
];

export function ChatHeader() {
  return (
    <header className="sticky top-0 z-30 w-full">
      <div className="mx-auto w-full max-w-[1440px] px-4 pt-4 lg:px-6 lg:pt-5">
        <div className="flex h-14 items-center justify-between gap-3 rounded-pill border border-ink-200/70 bg-white/95 px-3 pl-4 shadow-card backdrop-blur supports-[backdrop-filter]:bg-white/85 lg:h-16 lg:px-4 lg:pl-6">
          <Link
            href="/"
            aria-label="MediSign AI - Trang chủ"
            className="cursor-pointer"
          >
            <Logo />
          </Link>

          <nav aria-label="Điều hướng chính" className="hidden lg:block">
            <ul className="flex items-center gap-1">
              {NAV.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    aria-current={item.active ? "page" : undefined}
                    className={`relative inline-flex items-center rounded-pill px-4 py-2 text-[15px] font-medium transition-colors ${
                      item.active
                        ? "text-brand-700"
                        : "text-ink-600 hover:bg-ink-100 hover:text-ink-900"
                    }`}
                  >
                    {item.label}
                    {item.active && (
                      <span
                        aria-hidden
                        className="absolute inset-x-4 -bottom-[6px] h-[3px] rounded-full bg-brand"
                      />
                    )}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          <div className="flex items-center gap-2">
            <button
              type="button"
              aria-label="Trợ giúp"
              className="hidden h-10 w-10 items-center justify-center rounded-pill border border-ink-200 text-ink-500 hover:bg-ink-100 hover:text-ink-800 cursor-pointer lg:inline-flex"
            >
              <HelpIcon size={20} />
            </button>
            <Link
              href="#"
              className="rounded-pill border-2 border-ink-200 px-4 py-2 text-[15px] font-semibold text-ink-800 hover:border-brand hover:text-brand cursor-pointer"
            >
              Đăng nhập
            </Link>
            <Link
              href="#"
              className="inline-flex items-center gap-1.5 rounded-pill bg-brand px-5 py-2.5 text-[15px] font-semibold text-white shadow-soft hover:bg-brand-700 cursor-pointer"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                aria-hidden="true"
              >
                <path
                  d="M12 5v14M5 12h14"
                  stroke="currentColor"
                  strokeWidth="2.4"
                  strokeLinecap="round"
                />
              </svg>
              Tạo tài khoản
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
