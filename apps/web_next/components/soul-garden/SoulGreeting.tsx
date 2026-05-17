"use client";

// Banner chào buổi sáng — top của main column.
// Có ảnh minh hoạ thiền + badge streak 7 ngày.

export function SoulGreeting({ userName = "An" }: { userName?: string }) {
  return (
    <section
      aria-labelledby="soul-greet"
      className="relative overflow-hidden rounded-[20px] border border-emerald-100 bg-gradient-to-br from-emerald-50/70 via-emerald-50/30 to-amber-50/40 p-6 lg:p-7"
    >
      <div className="grid grid-cols-1 items-center gap-4 md:grid-cols-[1fr_auto]">
        <div>
          <p className="inline-flex items-center gap-1.5 text-[14px] text-ink-700">
            Chào buổi sáng, {userName}
            <SeedlingDoodle />
          </p>
          <h1
            id="soul-greet"
            className="mt-2 text-[clamp(22px,2.4vw,30px)] font-bold leading-tight text-ink-900"
          >
            Hôm nay bạn chọn
            <br />
            chăm sóc tâm hồn nhé.
          </h1>
          <p className="mt-2 max-w-md text-[14px] text-ink-600">
            Hãy hít thở sâu và bắt đầu một ngày thật nhẹ nhàng.
          </p>

          <button
            type="button"
            className="mt-5 inline-flex items-center gap-2 rounded-pill border border-emerald-200 bg-white/85 px-4 py-2 text-[13px] font-medium text-ink-800 shadow-soft hover:bg-white hover:border-emerald-400 cursor-pointer"
          >
            <span className="text-emerald-600">
              <HeartIcon />
            </span>
            Bạn đã chăm sóc tâm trí 7 ngày liên tiếp
            <ChevronRight />
          </button>
        </div>

        {/* Illustration on the right */}
        <div className="hidden md:block">
          <SoulSceneIllustration />
        </div>
      </div>
    </section>
  );
}

function SeedlingDoodle() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      className="inline-block text-emerald-600"
    >
      <path
        d="M12 21v-7M12 14c0-3 2-5 5-5-1 4-3 5-5 5zM12 14c0-3-2-5-5-5 1 4 3 5 5 5z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function HeartIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 21s-7-4.5-9.5-9C1 9 2.5 5 6 5c2 0 3.5 1 6 3 2.5-2 4-3 6-3 3.5 0 5 4 3.5 7-2.5 4.5-9.5 9-9.5 9z" />
    </svg>
  );
}

function ChevronRight() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      className="text-ink-400"
    >
      <path
        d="M9 6l6 6-6 6"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/**
 * Minh hoạ "thiền buổi sáng": cuốn sách + nến + cây + sỏi.
 * Vẽ bằng SVG primitives — không phụ thuộc asset.
 */
function SoulSceneIllustration() {
  return (
    <svg
      viewBox="0 0 280 180"
      className="h-[150px] w-[260px] lg:h-[170px] lg:w-[300px]"
      aria-hidden="true"
    >
      {/* table surface */}
      <ellipse cx="140" cy="160" rx="130" ry="10" fill="#000" fillOpacity="0.04" />

      {/* background warm light */}
      <circle cx="240" cy="60" r="60" fill="#FEF3C7" fillOpacity="0.6" />

      {/* potted plant */}
      <g transform="translate(200, 60)">
        <rect x="6" y="42" width="44" height="38" rx="5" fill="#E5E7EB" />
        <rect x="2" y="38" width="52" height="8" rx="3" fill="#D1D5DB" />
        {/* leaves */}
        <ellipse cx="20" cy="28" rx="10" ry="18" fill="#10B981" transform="rotate(-15 20 28)" />
        <ellipse cx="34" cy="22" rx="9" ry="22" fill="#34D399" transform="rotate(10 34 22)" />
        <ellipse cx="28" cy="14" rx="6" ry="12" fill="#6EE7B7" />
      </g>

      {/* book */}
      <g transform="translate(140, 110)">
        <rect width="70" height="44" rx="3" fill="#86EFAC" />
        <rect x="3" y="3" width="64" height="38" rx="2" fill="#34D399" />
        <text
          x="35"
          y="22"
          textAnchor="middle"
          fontSize="6"
          fontWeight="600"
          fill="#065F46"
          fontFamily="serif"
        >
          Soul
        </text>
        <text
          x="35"
          y="30"
          textAnchor="middle"
          fontSize="6"
          fontWeight="600"
          fill="#065F46"
          fontFamily="serif"
        >
          Garden
        </text>
      </g>

      {/* candle */}
      <g transform="translate(220, 130)">
        <rect x="0" y="6" width="14" height="22" rx="2" fill="#FED7AA" />
        <ellipse cx="7" cy="6" rx="6" ry="2" fill="#FB923C" />
        <path d="M7 0 Q9 4 7 6 Q5 4 7 0z" fill="#F59E0B" />
      </g>

      {/* zen stones */}
      <g transform="translate(60, 130)">
        <ellipse cx="20" cy="22" rx="22" ry="6" fill="#9CA3AF" />
        <ellipse cx="20" cy="14" rx="14" ry="5" fill="#6B7280" />
        <ellipse cx="20" cy="8" rx="8" ry="4" fill="#4B5563" />
      </g>

      {/* small leaves scattered */}
      <path d="M30 70 q5 -8 12 -4" stroke="#10B981" strokeWidth="2" fill="none" strokeLinecap="round" />
      <ellipse cx="38" cy="68" rx="3" ry="5" fill="#34D399" />
    </svg>
  );
}
