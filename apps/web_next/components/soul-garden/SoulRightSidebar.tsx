"use client";

// Sidebar phải Soul Garden — 4 card:
// 1) Khoảnh khắc hôm nay (quote)
// 2) Nhắc nhẹ cho bạn (3 reminders)
// 3) Năng lượng cảm xúc (gauge 78)
// 4) Cảm xúc nổi bật gần đây (5 chip)

const REMINDERS = [
  {
    title: "Viết nhật ký biết ơn",
    sub: "Ghi lại 3 điều khiến bạn biết ơn",
    time: "09:00",
    done: true
  },
  {
    title: "Thở 3 phút",
    sub: "Hít thở sâu để thư giãn",
    time: "12:00",
    done: false
  },
  {
    title: "Thiền buổi tối",
    sub: "Thư giãn và buông bỏ",
    time: "20:00",
    done: false
  }
];

const RECENT_MOODS = [
  { label: "Bình yên", icon: <LeafIcon />, tone: "text-emerald-700 bg-emerald-50" },
  { label: "Biết ơn", icon: <HeartIcon />, tone: "text-rose-700 bg-rose-50" },
  { label: "Hạnh phúc", icon: <SmileIcon />, tone: "text-amber-700 bg-amber-50" },
  { label: "Tự tin", icon: <StarIcon />, tone: "text-violet-700 bg-violet-50" },
  { label: "Hy vọng", icon: <SunIcon />, tone: "text-emerald-700 bg-emerald-50" }
];

export function SoulRightSidebar() {
  return (
    <div className="flex flex-col gap-5">
      {/* 1. Quote of the day */}
      <section
        aria-labelledby="quote-today"
        className="rounded-card border border-ink-200 bg-white p-5 shadow-soft"
      >
        <div className="flex items-center gap-2">
          <span className="text-amber-500">
            <SunIconSolid />
          </span>
          <h3 id="quote-today" className="text-[14px] font-bold text-ink-900">
            Khoảnh khắc hôm nay
          </h3>
        </div>
        <blockquote className="mt-4 text-center text-[14px] italic leading-relaxed text-ink-700">
          &ldquo;Bạn không cần phải tuyệt vời mỗi ngày, chỉ cần tiến bộ một chút mỗi ngày là đủ.&rdquo;
        </blockquote>
        <div className="mt-3 flex justify-center">
          <span className="text-emerald-500">
            <DividerLeaf />
          </span>
        </div>
      </section>

      {/* 2. Reminders */}
      <section
        aria-labelledby="reminders"
        className="rounded-card border border-ink-200 bg-white p-5 shadow-soft"
      >
        <div className="mb-4 flex items-center justify-between">
          <h3
            id="reminders"
            className="inline-flex items-center gap-2 text-[14px] font-bold text-ink-900"
          >
            <span className="text-amber-500">
              <BellIcon />
            </span>
            Nhắc nhẹ cho bạn
          </h3>
          <button
            type="button"
            className="text-[12px] font-semibold text-emerald-700 hover:underline cursor-pointer"
          >
            Xem tất cả
          </button>
        </div>

        <ul className="space-y-3">
          {REMINDERS.map((r) => (
            <li
              key={r.title}
              className="flex items-start gap-3 rounded-card bg-ink-100/40 p-3"
            >
              <span
                className={`grid h-9 w-9 flex-none place-items-center rounded-pill ${
                  r.done
                    ? "bg-emerald-100 text-emerald-700"
                    : "bg-white text-ink-500 ring-1 ring-ink-200"
                }`}
                aria-hidden="true"
              >
                {r.done ? <CheckIcon /> : <DotIcon />}
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-[13px] font-semibold text-ink-900">
                  {r.title}
                </p>
                <p className="truncate text-[11px] text-ink-500">{r.sub}</p>
              </div>
              <div className="flex flex-col items-end gap-1">
                <span className="rounded-pill bg-white px-2 py-0.5 text-[11px] font-medium text-ink-700 ring-1 ring-ink-200">
                  {r.time}
                </span>
                {r.done ? (
                  <span className="text-emerald-600" aria-label="Đã làm">
                    <CheckIcon />
                  </span>
                ) : (
                  <span
                    className="block h-3 w-3 rounded-full ring-1 ring-ink-300"
                    aria-label="Chưa làm"
                  />
                )}
              </div>
            </li>
          ))}
        </ul>
      </section>

      {/* 3. Mood energy gauge */}
      <section
        aria-labelledby="mood-energy"
        className="rounded-card border border-ink-200 bg-white p-5 shadow-soft"
      >
        <div className="flex items-center gap-2">
          <span className="text-emerald-500">
            <PulseIcon />
          </span>
          <h3 id="mood-energy" className="text-[14px] font-bold text-ink-900">
            Năng lượng cảm xúc
          </h3>
          <span className="text-ink-400">
            <InfoIcon />
          </span>
        </div>

        <div className="mt-4 grid grid-cols-[auto_1fr] items-center gap-4">
          <MoodGauge value={78} />
          <p className="text-[12px] leading-snug text-ink-700">
            Bạn đang duy trì cảm xúc ổn định. Tiếp tục chăm sóc bản thân nhé!
          </p>
        </div>
      </section>

      {/* 4. Recent moods */}
      <section
        aria-labelledby="recent-moods"
        className="rounded-card border border-ink-200 bg-white p-5 shadow-soft"
      >
        <div className="mb-3 flex items-center justify-between">
          <h3
            id="recent-moods"
            className="text-[14px] font-bold text-ink-900"
          >
            Cảm xúc nổi bật gần đây
          </h3>
          <button
            type="button"
            className="text-[12px] font-semibold text-emerald-700 hover:underline cursor-pointer"
          >
            Xem thêm
          </button>
        </div>

        <ul className="grid grid-cols-5 gap-2">
          {RECENT_MOODS.map((m) => (
            <li key={m.label} className="text-center">
              <span
                className={`mx-auto grid h-10 w-10 place-items-center rounded-pill ${m.tone}`}
                aria-hidden="true"
              >
                {m.icon}
              </span>
              <p className="mt-1.5 text-[10px] font-medium leading-tight text-ink-700">
                {m.label}
              </p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

/* ─────────── Mood gauge ─────────── */

function MoodGauge({ value }: { value: number }) {
  // Half-circle gauge — semi-arc 180°
  const clamped = Math.max(0, Math.min(100, value));
  const radius = 38;
  const cx = 44;
  const cy = 44;
  const circumference = Math.PI * radius;
  const strokeDash = (clamped / 100) * circumference;

  return (
    <div className="relative h-[88px] w-[88px]">
      <svg viewBox="0 0 88 88" className="h-full w-full">
        {/* track */}
        <path
          d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
          fill="none"
          stroke="#E2E8F0"
          strokeWidth="6"
          strokeLinecap="round"
        />
        {/* progress */}
        <path
          d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
          fill="none"
          stroke="#10B981"
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={`${strokeDash} ${circumference}`}
        />
        {/* smiley face */}
        <circle cx={cx} cy={cy + 2} r="11" fill="#D1FAE5" />
        <circle cx={cx - 4} cy={cy} r="1.4" fill="#065F46" />
        <circle cx={cx + 4} cy={cy} r="1.4" fill="#065F46" />
        <path
          d={`M ${cx - 4} ${cy + 4} q 4 4 8 0`}
          stroke="#065F46"
          strokeWidth="1.6"
          fill="none"
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-x-0 bottom-0 text-center">
        <span className="block text-[20px] font-extrabold leading-none text-ink-900">
          {clamped}
        </span>
        <span className="block text-[10px] font-medium text-emerald-700">
          Khá tốt
        </span>
      </div>
    </div>
  );
}

/* ─────────── Tiny icons ─────────── */

function SunIconSolid() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <circle cx="12" cy="12" r="4" />
      <path
        d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4L7 17M17 7l1.4-1.4"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function DividerLeaf() {
  return (
    <svg width="60" height="12" viewBox="0 0 60 12" fill="none" aria-hidden="true">
      <line x1="2" y1="6" x2="22" y2="6" stroke="currentColor" strokeWidth="1" strokeLinecap="round" />
      <ellipse cx="30" cy="6" rx="4" ry="3" fill="currentColor" />
      <line x1="38" y1="6" x2="58" y2="6" stroke="currentColor" strokeWidth="1" strokeLinecap="round" />
    </svg>
  );
}

function BellIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M6 9a6 6 0 1 1 12 0c0 4 1.5 6 2 6.5H4c.5-.5 2-2.5 2-6.5z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
      <path d="M10 19a2 2 0 0 0 4 0" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M5 12l4 4L19 6"
        stroke="currentColor"
        strokeWidth="2.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function DotIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function PulseIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M3 12h4l2-6 4 12 2-6h6"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function InfoIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M12 11v5M12 8.5h.01"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function LeafIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M20 4c-9 0-15 5-15 12 0 2 0 3 1 4 3-7 8-10 12-11-3 2-7 5-9 11 6 0 11-3 12-10 1-3 0-5-1-6z"
        stroke="currentColor"
        strokeWidth="1.6"
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

function SmileIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
      <circle cx="9" cy="10" r="1" fill="currentColor" />
      <circle cx="15" cy="10" r="1" fill="currentColor" />
      <path
        d="M8 14c1 2 2.5 3 4 3s3-1 4-3"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

function StarIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 2l3 6.5 7 .9-5 4.8 1.2 7-6.2-3.4-6.2 3.4 1.2-7-5-4.8 7-.9z" />
    </svg>
  );
}

function SunIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4L7 17M17 7l1.4-1.4"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}
