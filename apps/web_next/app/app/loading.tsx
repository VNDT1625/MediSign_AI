// Loading state cho khu vực /app/* (Next.js App Router convention).
//
// Khi điều hướng vào `/app/*` lần đầu hoặc khi server layout
// (`app/app/layout.tsx`) đang `await` `/auth/me`, Next.js render file này
// thay cho `{children}`. Mục tiêu:
//   - KHÔNG để chớp UI public (landing) khi đang hydrate auth.
//   - Render skeleton "đầy đủ vỏ app" (header + sidebar + content blocks)
//     để người dùng thấy đúng bố cục đang được tải.
//
// Đây là Server Component — KHÔNG có "use client".
//
// Tham chiếu:
//   - Requirement 2.2.2 (Auth Context): "WHILE hydrate đang chạy, THE
//     protected layout SHALL hiển thị skeleton, KHÔNG flash UI public."
//   - Requirement 2.4.1 (Loading & Error UX): "Mọi request SHALL có 3
//     trạng thái UI: loading (skeleton/spinner), success, error."
//   - Design language match: `DesktopAppHeader` rounded-pill 68px, content
//     `container-page`, card `rounded-card border-ink-200 shadow-soft`.

const SKELETON_PULSE =
  "bg-ink-100 motion-safe:animate-pulse rounded-md";

export default function AppLoading() {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-busy="true"
      className="min-h-screen bg-[#F1F5F9]"
    >
      {/* Visually hidden status announcement for AT users */}
      <span className="sr-only">Đang tải nội dung ứng dụng…</span>

      {/* Header skeleton — match shape of DesktopAppHeader pill */}
      <div className="container-page pt-3 lg:pt-4">
        <div className="flex h-[68px] items-center justify-between gap-3 rounded-pill border border-ink-200/70 bg-white/95 px-3 pl-4 shadow-card lg:px-4 lg:pl-6">
          {/* Logo + tagline placeholder */}
          <div className="flex items-center gap-2.5">
            <div className={`${SKELETON_PULSE} h-10 w-10 rounded-xl`} />
            <div className="hidden flex-col gap-1.5 sm:flex">
              <div className={`${SKELETON_PULSE} h-3.5 w-28`} />
              <div className={`${SKELETON_PULSE} h-2.5 w-40`} />
            </div>
          </div>

          {/* Pill nav placeholder (5 tabs) */}
          <div className="hidden items-center gap-1 lg:flex" aria-hidden="true">
            {Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className={`${SKELETON_PULSE} h-9 w-24 rounded-pill`}
              />
            ))}
          </div>

          {/* Bell + avatar placeholder */}
          <div className="flex items-center gap-2">
            <div className={`${SKELETON_PULSE} h-10 w-10 rounded-pill`} />
            <div
              className={`${SKELETON_PULSE} h-10 w-32 rounded-pill hidden sm:block`}
            />
            <div
              className={`${SKELETON_PULSE} h-10 w-10 rounded-pill sm:hidden`}
            />
          </div>
        </div>
      </div>

      {/* Body skeleton — sidebar + main content + right rail */}
      <main className="container-page pb-10 pt-4 lg:pt-5">
        <div className="grid gap-5 grid-cols-1 md:grid-cols-[300px_1fr] xl:grid-cols-[300px_1fr_320px]">
          {/* Sidebar */}
          <aside
            aria-hidden="true"
            className="hidden md:flex flex-col gap-3 rounded-card border border-ink-200 bg-white p-4 shadow-soft"
          >
            <div className={`${SKELETON_PULSE} h-5 w-32`} />
            <div className="mt-2 flex flex-col gap-2">
              {Array.from({ length: 6 }).map((_, i) => (
                <div
                  key={i}
                  className={`${SKELETON_PULSE} h-10 w-full rounded-card`}
                />
              ))}
            </div>
            <div className="mt-4 flex flex-col gap-2 border-t border-ink-200 pt-4">
              <div className={`${SKELETON_PULSE} h-4 w-24`} />
              <div className={`${SKELETON_PULSE} h-9 w-full rounded-pill`} />
            </div>
          </aside>

          {/* Main content area */}
          <section
            aria-hidden="true"
            className="flex flex-col gap-4 rounded-card border border-ink-200 bg-white p-5 shadow-soft lg:p-6"
          >
            <div className="flex flex-col gap-3">
              <div className={`${SKELETON_PULSE} h-7 w-2/3 max-w-md`} />
              <div className={`${SKELETON_PULSE} h-4 w-1/2 max-w-sm`} />
            </div>

            <div className="mt-2 grid grid-cols-1 gap-4 sm:grid-cols-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <div
                  key={i}
                  className="flex flex-col gap-3 rounded-card border border-ink-200 bg-ink-100/40 p-4"
                >
                  <div className={`${SKELETON_PULSE} h-5 w-3/4`} />
                  <div className={`${SKELETON_PULSE} h-4 w-full`} />
                  <div className={`${SKELETON_PULSE} h-4 w-5/6`} />
                  <div className={`${SKELETON_PULSE} mt-2 h-9 w-28 rounded-pill`} />
                </div>
              ))}
            </div>

            <div className="mt-2 flex flex-col gap-3">
              <div className={`${SKELETON_PULSE} h-4 w-full`} />
              <div className={`${SKELETON_PULSE} h-4 w-11/12`} />
              <div className={`${SKELETON_PULSE} h-4 w-10/12`} />
              <div className={`${SKELETON_PULSE} h-4 w-9/12`} />
            </div>
          </section>

          {/* Right rail */}
          <aside
            aria-hidden="true"
            className="hidden xl:flex flex-col gap-4"
          >
            <div className="flex flex-col gap-3 rounded-card border border-ink-200 bg-white p-5 shadow-soft">
              <div className={`${SKELETON_PULSE} h-5 w-32`} />
              <div className={`${SKELETON_PULSE} h-24 w-full rounded-card`} />
            </div>
            <div className="flex flex-col gap-3 rounded-card border border-ink-200 bg-white p-5 shadow-soft">
              <div className={`${SKELETON_PULSE} h-5 w-40`} />
              <div className={`${SKELETON_PULSE} h-4 w-full`} />
              <div className={`${SKELETON_PULSE} h-4 w-5/6`} />
              <div className={`${SKELETON_PULSE} h-4 w-2/3`} />
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}
