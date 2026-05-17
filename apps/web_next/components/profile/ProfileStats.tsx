type Stat = {
  value: string;
  label: string;
  icon: React.ReactNode;
  tone: "leaf" | "star" | "heart" | "badge";
};

const STATS: Stat[] = [
  {
    value: "28",
    label: "Ngày đồng hành liên tiếp",
    tone: "leaf",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 3c4 4 7 8 7 12a7 7 0 0 1-14 0c0-4 3-8 7-12z"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinejoin="round"
        />
      </svg>
    )
  },
  {
    value: "156",
    label: "Khoảnh khắc đã ghi lại",
    tone: "star",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77 5.82 21l1.18-6.88-5-4.87 6.91-1.01L12 2z" />
      </svg>
    )
  },
  {
    value: "78",
    label: "Điểm cảm xúc trung bình",
    tone: "heart",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path d="M12 21s-7-4.35-7-10a4.5 4.5 0 0 1 8-3 4.5 4.5 0 0 1 8 3c0 5.65-7 10-7 10h-2z" />
      </svg>
    )
  },
  {
    value: "12",
    label: "Huy hiệu đã đạt được",
    tone: "badge",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77 5.82 21l1.18-6.88-5-4.87 6.91-1.01L12 2z" />
      </svg>
    )
  }
];

const TONE: Record<Stat["tone"], string> = {
  leaf: "bg-success/12 text-success",
  star: "bg-purple-100 text-purple-600",
  heart: "bg-danger/12 text-danger",
  badge: "bg-warn/15 text-warn"
};

export function ProfileStats() {
  return (
    <ul className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {STATS.map((s) => (
        <li
          key={s.label}
          className="rounded-card border border-ink-200 bg-white p-4 shadow-soft"
        >
          <div className="flex items-center gap-3">
            <span className={`grid h-10 w-10 flex-none place-items-center rounded-pill ${TONE[s.tone]}`}>
              {s.icon}
            </span>
            <div className="min-w-0">
              <p className="text-2xl font-bold leading-tight text-ink-900">{s.value}</p>
              <p className="text-xs leading-tight text-ink-500">{s.label}</p>
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}
