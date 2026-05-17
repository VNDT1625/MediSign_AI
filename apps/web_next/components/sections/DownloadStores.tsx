import { Reveal } from "@/components/Reveal";

/**
 * DownloadStores — bento layout
 *
 * Desktop:
 *   ┌─────────────┬───────────┐
 *   │             │  Windows  │
 *   │   Mobile    ├───────────┤
 *   │  (featured) │   macOS   │
 *   │             ├───────────┤
 *   │             │   Linux   │
 *   └─────────────┴───────────┘
 *
 * Mobile: stacked.
 */
export function DownloadStores() {
  return (
    <section className="py-16 lg:py-20">
      <div className="container-page">
        <Reveal className="mx-auto max-w-2xl text-center">
          <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-700">
            Mọi nền tảng
          </p>
          <h2 className="text-h1 text-ink-900">
            Tải MediSign AI cho{" "}
            <span className="gradient-text-brand">thiết bị của bạn</span>
          </h2>
          <p className="mt-4 text-body text-ink-600">
            Một tài khoản, đồng bộ trên điện thoại, máy tính và web — không cần cài đặt lại.
          </p>
        </Reveal>

        <Reveal
          stagger
          className="mx-auto mt-12 grid max-w-6xl gap-4 lg:grid-cols-5 lg:grid-rows-3"
        >
          {/* FEATURED — Mobile (iOS + Android) */}
          <article className="reveal card-lift shine-card relative overflow-hidden rounded-[24px] border border-ink-200 bg-gradient-to-br from-brand-50 via-white to-accent/10 p-6 shadow-soft lg:col-span-3 lg:row-span-3 lg:p-8">
            {/* Ambient blob */}
            <div
              aria-hidden="true"
              className="anim-blob-drift pointer-events-none absolute -right-10 -top-10 h-56 w-56 rounded-full bg-brand/15 blur-3xl"
            />

            <div className="relative flex h-full flex-col">
              <div className="flex items-center gap-2">
                <span className="badge-pill">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <rect x="6" y="2" width="12" height="20" rx="3" stroke="currentColor" strokeWidth="1.8" />
                    <path d="M10 18h4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                  </svg>
                  Phổ biến nhất
                </span>
                <span className="text-[11px] font-semibold uppercase tracking-wide text-brand-700">
                  Khuyên dùng
                </span>
              </div>

              <h3 className="mt-3 text-2xl font-bold text-ink-900 sm:text-3xl">
                Điện thoại — trải nghiệm đầy đủ
              </h3>
              <p className="mt-2 max-w-md text-sm text-ink-600">
                Tủ thuốc, voice tiếng Việt, SoulGarden và thông báo nhắc thuốc.
                Hoạt động cả khi không có mạng.
              </p>

              {/* Store buttons */}
              <div className="mt-5 flex flex-wrap gap-3">
                <StoreButton
                  href="#"
                  caption="Tải trên"
                  name="App Store"
                  sub="iOS 14+"
                  accent="from-ink-900 to-ink-800"
                  icon={
                    <svg
                      width="22"
                      height="22"
                      viewBox="0 0 24 24"
                      fill="currentColor"
                      aria-hidden="true"
                    >
                      <path d="M16 1c0 2-2 4-4 4 0-2 2-4 4-4zM20 17c-1 2-2 4-4 4-1 0-2-1-4-1s-3 1-4 1c-2 0-4-2-5-5-2-5 0-11 4-11 1 0 3 1 4 1s2-1 4-1c2 0 3 1 4 3-3 2-3 6 1 9z" />
                    </svg>
                  }
                />
                <StoreButton
                  href="#"
                  caption="Tải trên"
                  name="Google Play"
                  sub="Android 8+"
                  accent="from-brand-700 to-brand"
                  icon={
                    <svg
                      width="22"
                      height="22"
                      viewBox="0 0 24 24"
                      fill="currentColor"
                      aria-hidden="true"
                    >
                      <path d="M5 3l14 9-14 9V3z" />
                    </svg>
                  }
                />
              </div>

              {/* Mini perk list */}
              <ul className="mt-6 grid grid-cols-1 gap-2 text-sm text-ink-700 sm:grid-cols-2">
                <Perk>Camera quét vỉ thuốc</Perk>
                <Perk>Voice tiếng Việt 24/7</Perk>
                <Perk>Thông báo nhắc thuốc</Perk>
                <Perk>Hoạt động offline</Perk>
              </ul>

              {/* QR pointer chip — shifted to bottom */}
              <div className="mt-auto flex items-center gap-3 pt-6">
                <span className="grid h-10 w-10 flex-none place-items-center rounded-pill bg-white text-brand-700 shadow-soft">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <rect x="3" y="3" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="2" />
                    <rect x="14" y="3" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="2" />
                    <rect x="3" y="14" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="2" />
                    <path d="M14 14h3v3M21 14v3M14 18v3h3M17 21h4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  </svg>
                </span>
                <p className="text-xs text-ink-600">
                  Hoặc <a href="#qr" className="font-semibold text-brand-700 underline-offset-2 hover:underline">quét mã QR</a>{" "}
                  để mở đúng cửa hàng
                </p>
              </div>
            </div>
          </article>

          {/* Desktop tiles */}
          <DesktopTile
            name="Windows"
            sub="Windows 10/11"
            href="#"
            accent="from-[#0F4FBF] to-brand"
            icon={
              <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M3 5l8-1v8H3V5zm9-1l9-1v10h-9V4zM3 13h8v8l-8-1v-7zm9 0h9v10l-9-1V13z" />
              </svg>
            }
          />
          <DesktopTile
            name="macOS"
            sub="macOS 12+"
            href="#"
            accent="from-ink-800 to-ink-600"
            icon={
              <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M16 1c0 2-2 4-4 4 0-2 2-4 4-4zM20 17c-1 2-2 4-4 4-1 0-2-1-4-1s-3 1-4 1c-2 0-4-2-5-5-2-5 0-11 4-11 1 0 3 1 4 1s2-1 4-1c2 0 3 1 4 3-3 2-3 6 1 9z" />
              </svg>
            }
          />
          <DesktopTile
            name="Linux & Web"
            sub="PWA · không cần cài"
            href="/"
            accent="from-success to-brand-700"
            icon={
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
                <path
                  d="M3 12h18M12 3a13 13 0 0 1 0 18M12 3a13 13 0 0 0 0 18"
                  stroke="currentColor"
                  strokeWidth="2"
                />
              </svg>
            }
          />
        </Reveal>
      </div>
    </section>
  );
}

/* ---------- sub components ---------- */

function StoreButton({
  href,
  caption,
  name,
  sub,
  accent,
  icon,
}: {
  href: string;
  caption: string;
  name: string;
  sub: string;
  accent: string;
  icon: React.ReactNode;
}) {
  return (
    <a
      href={href}
      className="card-lift group inline-flex min-w-[180px] flex-1 items-center gap-3 rounded-pill border border-ink-200 bg-white px-4 py-3 shadow-soft hover:border-brand cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2"
    >
      <span
        className={`grid h-11 w-11 flex-none place-items-center rounded-pill bg-gradient-to-br ${accent} text-white shadow-soft`}
      >
        {icon}
      </span>
      <span className="min-w-0">
        <span className="block text-[11px] uppercase tracking-wide text-ink-500">
          {caption}
        </span>
        <span className="block text-sm font-semibold text-ink-900">{name}</span>
        <span className="block text-[11px] text-ink-500">{sub}</span>
      </span>
    </a>
  );
}

function DesktopTile({
  name,
  sub,
  href,
  accent,
  icon,
}: {
  name: string;
  sub: string;
  href: string;
  accent: string;
  icon: React.ReactNode;
}) {
  return (
    <a
      href={href}
      className="reveal card-lift shine-card group relative flex items-center gap-3 overflow-hidden rounded-[20px] border border-ink-200 bg-white p-5 shadow-soft hover:border-brand cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 lg:col-span-2"
    >
      <span
        className={`grid h-12 w-12 flex-none place-items-center rounded-card bg-gradient-to-br ${accent} text-white shadow-soft transition-transform duration-300 group-hover:-translate-y-0.5 group-hover:scale-105`}
      >
        {icon}
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-base font-semibold text-ink-900">{name}</span>
        <span className="block text-xs text-ink-500">{sub}</span>
      </span>
      <span
        aria-hidden="true"
        className="grid h-8 w-8 flex-none translate-x-1 place-items-center rounded-pill bg-brand-50 text-brand-700 opacity-0 transition-all duration-300 group-hover:translate-x-0 group-hover:opacity-100"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
          <path
            d="M5 12h14M13 6l6 6-6 6"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </span>
    </a>
  );
}

function Perk({ children }: { children: React.ReactNode }) {
  return (
    <li className="flex items-center gap-2">
      <span className="grid h-5 w-5 flex-none place-items-center rounded-full bg-success/15 text-success">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M5 12l4 4L19 6"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </span>
      {children}
    </li>
  );
}
