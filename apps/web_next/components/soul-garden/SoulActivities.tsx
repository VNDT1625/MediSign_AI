"use client";

// Hàng 4 hoạt động: Viết vài dòng / Bài tập thở / Thiền ngắn / Âm nhạc chữa lành.
// Mỗi card có ảnh minh hoạ + title + sub + nút arrow.

const ACTIVITIES = [
  {
    title: "Viết vài dòng",
    sub: "Giải toả và thấu hiểu cảm xúc của bạn",
    illust: <JournalIllust />,
    tone: "from-violet-50 to-white"
  },
  {
    title: "Bài tập thở",
    sub: "Thư giãn cơ thể và tâm trí",
    illust: <BreathIllust />,
    tone: "from-rose-50 to-white"
  },
  {
    title: "Thiền ngắn",
    sub: "3-10 phút hiện tại trọn vẹn",
    illust: <MeditationIllust />,
    tone: "from-emerald-50 to-white"
  },
  {
    title: "Âm nhạc chữa lành",
    sub: "Lắng nghe và nuôi dưỡng tâm hồn",
    illust: <MusicIllust />,
    tone: "from-amber-50 to-white"
  }
];

export function SoulActivities() {
  return (
    <section
      aria-labelledby="soul-activities"
      className="rounded-[20px] border border-ink-200 bg-white p-6 shadow-soft lg:p-7"
    >
      <div className="mb-5 flex items-center justify-between gap-4">
        <h2
          id="soul-activities"
          className="text-[16px] font-bold text-ink-900"
        >
          Hôm nay, bạn muốn bắt đầu với điều gì?
        </h2>
        <button
          type="button"
          className="inline-flex items-center gap-1.5 rounded-pill px-3 py-1.5 text-[13px] font-medium text-ink-600 hover:bg-ink-100 cursor-pointer"
        >
          <SettingsIcon />
          Tuỳ chỉnh
        </button>
      </div>

      <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {ACTIVITIES.map((a) => (
          <li key={a.title}>
            <button
              type="button"
              className={`group flex h-full w-full flex-col rounded-card border border-ink-200 bg-gradient-to-b ${a.tone} p-4 text-left shadow-soft transition-colors hover:border-emerald-300 hover:shadow-card cursor-pointer`}
            >
              <div className="grid h-24 w-full place-items-center">
                {a.illust}
              </div>
              <div className="mt-3">
                <p className="text-[14px] font-semibold text-ink-900">
                  {a.title}
                </p>
                <p className="mt-0.5 text-[12px] leading-snug text-ink-500">
                  {a.sub}
                </p>
              </div>
              <span
                aria-hidden="true"
                className="mt-3 inline-flex h-8 w-8 items-center justify-center self-start rounded-pill border border-ink-200 bg-white text-ink-500 group-hover:border-emerald-300 group-hover:text-emerald-700"
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  aria-hidden="true"
                >
                  <path
                    d="M5 12h14M13 6l6 6-6 6"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}

/* ─────────── Illustrations ─────────── */

function JournalIllust() {
  return (
    <svg viewBox="0 0 100 80" className="h-20 w-full" aria-hidden="true">
      {/* notebook */}
      <rect x="20" y="10" width="60" height="60" rx="5" fill="#A78BFA" />
      <rect x="22" y="12" width="56" height="56" rx="3" fill="#F5F3FF" />
      <line x1="30" y1="26" x2="68" y2="26" stroke="#A78BFA" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="30" y1="34" x2="62" y2="34" stroke="#C4B5FD" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="30" y1="42" x2="66" y2="42" stroke="#C4B5FD" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="30" y1="50" x2="58" y2="50" stroke="#C4B5FD" strokeWidth="1.5" strokeLinecap="round" />
      {/* spiral */}
      <circle cx="20" cy="20" r="2" fill="#7C3AED" />
      <circle cx="20" cy="32" r="2" fill="#7C3AED" />
      <circle cx="20" cy="44" r="2" fill="#7C3AED" />
      <circle cx="20" cy="56" r="2" fill="#7C3AED" />
      {/* pen */}
      <rect x="56" y="56" width="22" height="4" rx="2" fill="#6B7280" transform="rotate(-30 56 56)" />
      <polygon points="56,56 60,54 60,60" fill="#1F2937" transform="rotate(-30 56 56)" />
    </svg>
  );
}

function BreathIllust() {
  return (
    <svg viewBox="0 0 100 80" className="h-20 w-full" aria-hidden="true">
      {/* lavender stems */}
      <line x1="40" y1="70" x2="40" y2="20" stroke="#10B981" strokeWidth="2" strokeLinecap="round" />
      <line x1="50" y1="70" x2="50" y2="14" stroke="#10B981" strokeWidth="2" strokeLinecap="round" />
      <line x1="60" y1="70" x2="60" y2="22" stroke="#10B981" strokeWidth="2" strokeLinecap="round" />
      {/* lavender heads */}
      <ellipse cx="40" cy="22" rx="3" ry="6" fill="#A78BFA" />
      <ellipse cx="40" cy="16" rx="2.5" ry="4" fill="#A78BFA" />
      <ellipse cx="50" cy="16" rx="3" ry="6" fill="#8B5CF6" />
      <ellipse cx="50" cy="10" rx="2.5" ry="4" fill="#8B5CF6" />
      <ellipse cx="60" cy="24" rx="3" ry="6" fill="#A78BFA" />
      <ellipse cx="60" cy="18" rx="2.5" ry="4" fill="#A78BFA" />
      {/* leaves */}
      <ellipse cx="36" cy="50" rx="6" ry="3" fill="#34D399" transform="rotate(-30 36 50)" />
      <ellipse cx="64" cy="52" rx="6" ry="3" fill="#34D399" transform="rotate(30 64 52)" />
      {/* base ground */}
      <ellipse cx="50" cy="72" rx="30" ry="3" fill="#000" fillOpacity="0.05" />
    </svg>
  );
}

function MeditationIllust() {
  return (
    <svg viewBox="0 0 100 80" className="h-20 w-full" aria-hidden="true">
      {/* zen stones stack */}
      <ellipse cx="50" cy="68" rx="32" ry="5" fill="#000" fillOpacity="0.05" />
      <ellipse cx="50" cy="62" rx="26" ry="6" fill="#9CA3AF" />
      <ellipse cx="50" cy="50" rx="20" ry="6" fill="#6B7280" />
      <ellipse cx="50" cy="38" rx="14" ry="5" fill="#4B5563" />
      <ellipse cx="50" cy="28" rx="9" ry="4" fill="#374151" />
      {/* bamboo leaf next to stack */}
      <line x1="78" y1="60" x2="78" y2="20" stroke="#16A34A" strokeWidth="2" strokeLinecap="round" />
      <ellipse cx="82" cy="32" rx="6" ry="2.5" fill="#22C55E" transform="rotate(20 82 32)" />
      <ellipse cx="80" cy="40" rx="5" ry="2" fill="#22C55E" transform="rotate(-10 80 40)" />
    </svg>
  );
}

function MusicIllust() {
  return (
    <svg viewBox="0 0 100 80" className="h-20 w-full" aria-hidden="true">
      {/* headphones */}
      <path
        d="M22 50 v-8 a28 28 0 0 1 56 0 v8"
        stroke="#0F172A"
        strokeWidth="3"
        fill="none"
        strokeLinecap="round"
      />
      <rect x="14" y="48" width="14" height="20" rx="4" fill="#FB923C" />
      <rect x="72" y="48" width="14" height="20" rx="4" fill="#FB923C" />
      <rect x="16" y="50" width="10" height="16" rx="3" fill="#FED7AA" />
      <rect x="74" y="50" width="10" height="16" rx="3" fill="#FED7AA" />
      {/* music notes */}
      <text x="38" y="34" fontSize="14" fill="#F59E0B">♪</text>
      <text x="56" y="28" fontSize="12" fill="#FB923C">♫</text>
    </svg>
  );
}

function SettingsIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3h0a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5h0a1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8v0a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"
        stroke="currentColor"
        strokeWidth="1.6"
      />
    </svg>
  );
}
