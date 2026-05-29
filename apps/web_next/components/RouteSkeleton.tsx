"use client";

/**
 * RouteSkeleton — skeleton chung dùng cho `loading.tsx` của các route
 * client-component nặng (chat, profile, about, download, pricing).
 *
 * Mục đích: khi user click vào header link, Next sẽ render skeleton này
 * ngay lập tức (vì nó là Server Component không phụ thuộc dữ liệu) trong
 * khi client bundle của trang đích đang được tải. Tránh cảm giác "click
 * không ăn" vì viewport giữ nguyên trang cũ.
 *
 * Layout mô phỏng cấu trúc chung: header pill nổi + main area + section
 * placeholder. Không cố gắng giống 1:1 với từng trang vì sẽ phải maintain
 * nhiều layout khác nhau — bản generic này đủ để báo hiệu "đang tải".
 */

import { Logo } from "./Logo";

export function RouteSkeleton({
  variant = "marketing",
}: {
  /**
   * - "marketing": header trên + main area kiểu landing (về trang chủ,
   *   pricing, about, download).
   * - "app": layout 3 cột chat-style (sidebar + main).
   * - "profile": dual-column (8/4) cho profile.
   */
  variant?: "marketing" | "app" | "profile";
}) {
  return (
    <div className="min-h-screen bg-ink-100/40">
      {/* Floating header pill — giống SiteHeader để không nhảy layout */}
      <header className="fixed top-4 left-4 right-4 z-30">
        <div className="flex h-16 items-center justify-between gap-3 rounded-pill border border-gray-200 bg-white/95 px-3 pl-4 shadow-card backdrop-blur sm:h-[72px] lg:h-20 lg:px-4 lg:pl-6 2xl:h-24">
          <Logo />
          <div className="flex items-center gap-2">
            <Shimmer className="hidden h-9 w-24 rounded-pill lg:block" />
            <Shimmer className="h-10 w-32 rounded-pill" />
          </div>
        </div>
      </header>

      {/* Body theo variant */}
      {variant === "app" ? (
        <main className="mx-auto flex h-screen w-full max-w-[1440px] flex-1 px-2 pb-2 pt-[88px] sm:px-4 sm:pb-4 lg:px-6 2xl:max-w-[1600px] 2xl:px-8">
          <div className="grid h-full w-full gap-2 sm:gap-4 grid-cols-1 md:grid-cols-[300px_1fr] xl:grid-cols-[300px_1fr_320px]">
            <Shimmer className="hidden md:block rounded-card" />
            <Shimmer className="rounded-card" />
            <Shimmer className="hidden xl:block rounded-card" />
          </div>
        </main>
      ) : variant === "profile" ? (
        <main className="container-page pt-28 pb-12 lg:pt-36">
          <Shimmer className="h-12 w-2/3 max-w-md rounded-card" />
          <div className="mt-8 grid gap-6 lg:grid-cols-12">
            <div className="space-y-5 lg:col-span-8">
              <Shimmer className="h-40 rounded-card" />
              <Shimmer className="h-32 rounded-card" />
              <Shimmer className="h-48 rounded-card" />
            </div>
            <div className="lg:col-span-4">
              <Shimmer className="h-72 rounded-card" />
            </div>
          </div>
        </main>
      ) : (
        <main className="container-page pt-28 pb-12 lg:pt-36">
          <div className="mx-auto max-w-2xl text-center">
            <Shimmer className="mx-auto h-6 w-32 rounded-pill" />
            <Shimmer className="mx-auto mt-4 h-10 w-3/4 rounded-card" />
            <Shimmer className="mx-auto mt-3 h-5 w-2/3 rounded-card" />
          </div>
          <div className="mx-auto mt-12 grid max-w-6xl gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <Shimmer className="h-48 rounded-card" />
            <Shimmer className="h-48 rounded-card" />
            <Shimmer className="h-48 rounded-card" />
          </div>
        </main>
      )}
    </div>
  );
}

function Shimmer({ className = "" }: { className?: string }) {
  return (
    <div
      aria-hidden="true"
      className={`relative overflow-hidden bg-ink-200/60 ${className}`}
    >
      {/*
        Lớp gradient + animate-shimmer (đã định nghĩa trong tailwind.config.ts).
        Dùng background-position trượt thay cho transform để tận dụng keyframe
        có sẵn — bằng cách set background-size 200% và để keyframe shimmer
        di chuyển backgroundPosition từ -200% → 200%.
      */}
      <div
        className="absolute inset-0 animate-shimmer"
        style={{
          background:
            "linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.55) 50%, transparent 100%)",
          backgroundSize: "200% 100%",
        }}
      />
    </div>
  );
}
