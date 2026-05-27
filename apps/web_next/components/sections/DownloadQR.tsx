import { Reveal } from "@/components/Reveal";

export function DownloadQR() {
  return (
    <section className="relative overflow-hidden bg-brand-50/40 py-16 lg:py-20">
      {/* Soft brand glow */}
      <div
        aria-hidden="true"
        className="absolute -left-24 top-1/2 h-[420px] w-[420px] -translate-y-1/2 rounded-full bg-brand/15 blur-3xl"
      />
      <div
        aria-hidden="true"
        className="absolute -right-32 -top-24 h-[420px] w-[420px] rounded-full bg-accent/10 blur-3xl"
      />

      <div className="container-page relative">
        <div className="mx-auto grid max-w-6xl items-center gap-10 lg:grid-cols-12 lg:gap-12">
          {/* LEFT: Text + steps */}
          <Reveal className="lg:col-span-7">
            <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-700">
              Quét nhanh
            </p>
            <h2 className="text-h1 text-ink-900">
              Quét QR — tải app trong{" "}
              <span className="gradient-text-brand">10 giây</span>
            </h2>
            <p className="mt-4 max-w-xl text-body text-ink-600">
              Mở camera điện thoại quét mã, hệ thống tự nhận iOS hay Android và đưa bạn đến đúng
              cửa hàng. Không cần gõ địa chỉ.
            </p>

            {/* 3 steps in horizontal cards (denser than vertical list) */}
            <ol className="mt-8 grid gap-3 sm:grid-cols-3">
              <Step
                n={1}
                title="Mở camera"
                desc="App camera mặc định trên điện thoại"
              />
              <Step
                n={2}
                title="Hướng vào QR"
                desc="Giữ ổn định 1-2 giây để đọc mã"
              />
              <Step
                n={3}
                title="Mở store"
                desc="Nhấn thông báo, cài đặt là xong"
              />
            </ol>

            {/* Trust microcopy */}
            <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-ink-600">
              <span className="inline-flex items-center gap-2">
                <span className="grid h-6 w-6 place-items-center rounded-pill bg-success/15 text-emerald-800">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path
                      d="M12 3l8 3v6c0 5-3.5 8.5-8 9-4.5-.5-8-4-8-9V6l8-3z"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinejoin="round"
                    />
                  </svg>
                </span>
                Liên kết chính thức
              </span>
              <span className="inline-flex items-center gap-2">
                <span className="grid h-6 w-6 place-items-center rounded-pill bg-brand-50 text-brand-700">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
                    <path
                      d="M12 8v4l2 2"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                </span>
                Mất khoảng 30 giây
              </span>
            </div>
          </Reveal>

          {/* RIGHT: QR card + small phone-scanning illustration */}
          <Reveal className="relative mx-auto w-full max-w-[420px] lg:col-span-5">
            {/* Floating ambient blob behind QR */}
            <div
              aria-hidden="true"
              className="anim-blob-drift absolute -inset-6 -z-10 rounded-[44px] bg-gradient-to-br from-brand-100 via-white to-accent/10 blur-2xl"
            />

            <div className="card-lift anim-float-slow relative rounded-[24px] border border-ink-200 bg-white p-6 shadow-card">
              <div className="qr-scan relative">
                <div
                  aria-hidden="true"
                  className="grid aspect-square w-full grid-cols-12 grid-rows-12 gap-[3px] rounded-card bg-white p-3"
                >
                  {Array.from({ length: 144 }).map((_, i) => {
                    const on = (i * 37 + 11) % 5 < 2;
                    return (
                      <span
                        key={i}
                        className={`rounded-[2px] ${
                          on ? "bg-ink-900" : "bg-transparent"
                        }`}
                      />
                    );
                  })}
                </div>

                {/* Corner markers */}
                <span className="pointer-events-none absolute left-4 top-4 h-12 w-12 rounded-md border-[5px] border-ink-900 animate-pulse-soft" />
                <span className="pointer-events-none absolute right-4 top-4 h-12 w-12 rounded-md border-[5px] border-ink-900" />
                <span className="pointer-events-none absolute left-4 bottom-4 h-12 w-12 rounded-md border-[5px] border-ink-900" />

                {/* Center logo */}
                <span className="pointer-events-none absolute left-1/2 top-1/2 grid h-12 w-12 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-2xl bg-white shadow-card">
                  <span className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-brand to-brand-700 text-white">
                    <svg
                      width="18"
                      height="18"
                      viewBox="0 0 24 24"
                      fill="none"
                      aria-hidden="true"
                    >
                      <path
                        d="M12 21s-7-4.5-7-11a5 5 0 0 1 9-3 5 5 0 0 1 9 3c0 6.5-7 11-7 11h-4z"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </span>
                </span>
              </div>

              <div className="mt-5 flex items-center justify-center gap-2 text-sm font-medium text-ink-700">
                <span className="grid h-7 w-7 place-items-center rounded-pill bg-brand text-white">
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    aria-hidden="true"
                  >
                    <path
                      d="M3 7V5a2 2 0 0 1 2-2h2M3 17v2a2 2 0 0 0 2 2h2M21 7V5a2 2 0 0 0-2-2h-2M21 17v2a2 2 0 0 1-2 2h-2M7 12h10"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                </span>
                Quét bằng camera điện thoại
              </div>

              <div className="mt-3 flex items-center justify-center gap-2 text-[11px]">
                <span className="rounded-pill bg-ink-100 px-2 py-0.5 text-ink-600">iOS</span>
                <span className="rounded-pill bg-ink-100 px-2 py-0.5 text-ink-600">Android</span>
                <span className="rounded-pill bg-success/15 px-2 py-0.5 text-emerald-800">
                  An toàn
                </span>
              </div>
            </div>

            {/* Small floating phone-scanning chip — overlaps QR card bottom-left */}
            <div
              aria-hidden="true"
              className="anim-float-tilt absolute -bottom-3 -left-3 hidden items-center gap-2 rounded-pill bg-white px-3 py-2 shadow-card sm:flex"
            >
              <span className="grid h-7 w-7 place-items-center rounded-pill bg-accent text-white">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                  <rect x="6" y="2" width="12" height="20" rx="3" stroke="currentColor" strokeWidth="2" />
                  <path d="M10 18h4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
              </span>
              <span className="text-xs font-semibold text-ink-900">Đang quét…</span>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}

function Step({
  n,
  title,
  desc,
}: {
  n: number;
  title: string;
  desc: string;
}) {
  return (
    <li className="card-lift relative rounded-[16px] border border-ink-200 bg-white p-4 shadow-soft">
      <span className="grid h-8 w-8 place-items-center rounded-pill bg-brand text-sm font-bold text-white shadow-soft">
        {n}
      </span>
      <h3 className="mt-3 text-sm font-semibold text-ink-900">{title}</h3>
      <p className="mt-1 text-xs leading-relaxed text-ink-600">{desc}</p>
    </li>
  );
}
