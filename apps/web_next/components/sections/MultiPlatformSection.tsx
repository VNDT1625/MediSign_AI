// "Trải nghiệm trên mọi thiết bị" — refactor để cảm giác cinematic hơn.
// 4 store buttons gọn icon-first. Mockup laptop+phone vẽ chi tiết hơn.
// Background blob brand mờ tạo chiều sâu.

import { Reveal } from "@/components/Reveal";

const STORES = [
  { name: "App Store", caption: "Tải trên", icon: <AppleIcon /> },
  { name: "Google Play", caption: "Tải trên", icon: <PlayIcon /> },
  { name: "Web", caption: "Dùng trên", icon: <GlobeIcon /> },
  { name: "Windows", caption: "Tải cho", icon: <WindowsIcon /> }
];

export function MultiPlatformSection() {
  return (
    <section className="relative overflow-hidden py-16 lg:py-24">
      {/* Ambient blob */}
      <div
        aria-hidden
        className="pointer-events-none absolute -left-40 top-1/4 h-[420px] w-[420px] rounded-full bg-brand/10 blur-3xl"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -right-40 bottom-0 h-[400px] w-[400px] rounded-full bg-accent/10 blur-3xl"
      />

      <div className="container-page relative">
        <div className="grid gap-10 lg:grid-cols-2 lg:items-start lg:gap-16">
          {/* Left — copy + stores */}
          <Reveal>
            <span className="badge-pill">Đa nền tảng</span>
            <h2 className="mt-3 text-h1 text-ink-900">
              Trải nghiệm trên mọi thiết bị
            </h2>
            <p className="mt-3 max-w-xl text-body text-ink-600">
              MediSign AI đồng hành cùng bạn ở bất cứ đâu — Web, mobile hay
              desktop. Đồng bộ liền mạch, bảo mật toàn diện.
            </p>

            <div className="mt-6 inline-flex items-center gap-3 rounded-pill border border-ink-200 bg-white px-4 py-3 shadow-soft">
              <span className="grid h-9 w-9 place-items-center rounded-pill bg-brand-50 text-brand-700">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path
                    d="M21 12a8 8 0 0 1-11.5 7.2L4 21l1.8-5.5A8 8 0 1 1 21 12z"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinejoin="round"
                  />
                </svg>
              </span>
              <span>
                <span className="block text-sm font-semibold text-ink-900">
                  Chat AI mọi nền tảng
                </span>
                <span className="block text-xs text-ink-500">
                  Web, mobile, desktop — đồng bộ và bảo mật.
                </span>
              </span>
            </div>

            <ul className="mt-6 grid grid-cols-2 gap-3 sm:max-w-md">
              {STORES.map((s) => (
                <li key={s.name}>
                  <button
                    type="button"
                    className="group flex w-full items-center gap-3 rounded-pill border border-ink-200 bg-white px-4 py-3 text-left shadow-soft transition-all hover:border-brand hover:shadow-card cursor-pointer"
                  >
                    <span className="grid h-9 w-9 flex-none place-items-center rounded-pill bg-ink-900 text-white transition-colors group-hover:bg-brand">
                      {s.icon}
                    </span>
                    <span className="min-w-0">
                      <span className="block text-[11px] uppercase tracking-wide text-ink-500">
                        {s.caption}
                      </span>
                      <span className="block text-sm font-semibold text-ink-900">
                        {s.name}
                      </span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </Reveal>

          {/* Right — mockup */}
          <Reveal direction="left" delay={120}>
            <DeviceMockups />
          </Reveal>
        </div>
      </div>
    </section>
  );
}

function DeviceMockups() {
  return (
    <div className="relative mx-auto h-[400px] w-full max-w-xl">
      {/* Laptop */}
      <div className="absolute inset-x-2 top-2 rounded-t-card border border-ink-200 bg-white shadow-card">
        <div className="flex items-center gap-1.5 border-b border-ink-200 px-3 py-2.5">
          <span className="h-2.5 w-2.5 rounded-full bg-danger/70" />
          <span className="h-2.5 w-2.5 rounded-full bg-warn/70" />
          <span className="h-2.5 w-2.5 rounded-full bg-success/70" />
          <span className="ml-3 inline-block rounded-pill bg-ink-100 px-3 py-0.5 text-[10px] text-ink-500">
            medisign.ai/chat
          </span>
        </div>
        <div className="p-3">
          <div className="aspect-[16/9] overflow-hidden rounded-card bg-gradient-to-br from-brand-50 to-white p-4">
            {/* Fake chat preview */}
            <div className="flex items-start gap-2">
              <span className="grid h-8 w-8 flex-none place-items-center rounded-card bg-brand text-white">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden>
                  <path
                    d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6l-8-3Z"
                    fill="currentColor"
                  />
                  <path
                    d="M12 9v6M9 12h6"
                    stroke="#fff"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                </svg>
              </span>
              <div className="rounded-card bg-white px-3 py-2 shadow-soft">
                <div className="h-2 w-32 rounded-pill bg-ink-200" />
                <div className="mt-1.5 h-2 w-44 rounded-pill bg-ink-200" />
              </div>
            </div>
            <div className="mt-3 flex items-start justify-end gap-2">
              <div className="rounded-card bg-brand px-3 py-2 shadow-soft">
                <div className="h-2 w-28 rounded-pill bg-white/70" />
              </div>
            </div>
            <div className="mt-3 flex items-start gap-2">
              <span className="grid h-8 w-8 flex-none place-items-center rounded-card bg-brand text-white">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden>
                  <path
                    d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6l-8-3Z"
                    fill="currentColor"
                  />
                </svg>
              </span>
              <div className="rounded-card bg-white px-3 py-2 shadow-soft">
                <div className="h-2 w-40 rounded-pill bg-ink-200" />
                <div className="mt-1.5 h-2 w-24 rounded-pill bg-ink-200" />
                <div className="mt-2 inline-flex items-center gap-1.5 rounded-pill bg-success-soft px-2 py-0.5 text-[10px] font-semibold text-success">
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" aria-hidden>
                    <path
                      d="m5 13 4 4L19 7"
                      stroke="currentColor"
                      strokeWidth="3"
                      strokeLinecap="round"
                    />
                  </svg>
                  An toàn
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* Laptop base */}
      <div
        aria-hidden
        className="absolute top-[300px] mx-auto h-3 w-[103%] -translate-x-1/2 rounded-b-pill bg-ink-200"
        style={{ left: "50%" }}
      />

      {/* Phone */}
      <div className="absolute right-2 top-16 w-[160px] rotate-[3deg] rounded-[28px] border-[6px] border-ink-900 bg-white shadow-card">
        <div className="aspect-[9/16] overflow-hidden rounded-[20px] bg-gradient-to-b from-brand-50 to-white">
          <div className="space-y-2 p-3">
            <div className="flex items-center justify-between">
              <span className="rounded-pill bg-brand/15 px-2.5 py-0.5 text-[10px] font-medium text-brand-700">
                MediSign AI
              </span>
              <span aria-hidden className="grid h-5 w-5 place-items-center rounded-full bg-success/20 text-success">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="4" fill="currentColor" />
                </svg>
              </span>
            </div>
            <div className="rounded-card bg-white p-2 shadow-soft">
              <div className="h-1.5 w-3/4 rounded-pill bg-ink-200" />
              <div className="mt-1 h-1.5 w-1/2 rounded-pill bg-ink-200" />
            </div>
            <div className="rounded-card bg-brand p-2">
              <div className="h-1.5 w-3/4 rounded-pill bg-white/70" />
              <div className="mt-1 h-1.5 w-1/2 rounded-pill bg-white/70" />
            </div>
            <div className="rounded-card bg-white p-2 shadow-soft">
              <div className="h-1.5 w-2/3 rounded-pill bg-ink-200" />
              <div className="mt-1 h-1.5 w-1/2 rounded-pill bg-ink-200" />
            </div>
            <div className="flex items-center gap-1.5 rounded-pill bg-accent-soft px-2 py-1">
              <span className="h-1.5 w-1.5 rounded-full bg-accent animate-pulse-soft" />
              <span className="text-[9px] font-medium text-accent">Đang lắng nghe...</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function PlayIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M5 3l14 9-14 9V3z" />
    </svg>
  );
}
function AppleIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M16 1c0 2-2 4-4 4 0-2 2-4 4-4zM20 17c-1 2-2 4-4 4-1 0-2-1-4-1s-3 1-4 1c-2 0-4-2-5-5-2-5 0-11 4-11 1 0 3 1 4 1s2-1 4-1c2 0 3 1 4 3-3 2-3 6 1 9z" />
    </svg>
  );
}
function GlobeIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
      <path
        d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"
        stroke="currentColor"
        strokeWidth="2"
      />
    </svg>
  );
}
function WindowsIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M3 5l8-1v8H3V5zm9-1l9-1v10h-9V4zM3 13h8v8l-8-1v-7zm9 0h9v10l-9-1V13z" />
    </svg>
  );
}
