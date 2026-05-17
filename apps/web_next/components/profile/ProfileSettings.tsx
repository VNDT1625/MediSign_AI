"use client";

import { useState } from "react";

type Row =
  | { kind: "toggle"; key: string; title: string; desc: string; defaultOn?: boolean; icon: React.ReactNode }
  | { kind: "link"; key: string; title: string; desc: string; trailing?: string; icon: React.ReactNode };

const SETTINGS: Row[] = [
  {
    kind: "toggle",
    key: "noti",
    title: "Thông báo",
    desc: "Quản lý thông báo của bạn",
    defaultOn: true,
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M5 17h14l-1.5-2V11a5.5 5.5 0 1 0-11 0v4L5 17zM10 20h4" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
      </svg>
    )
  },
  {
    kind: "link",
    key: "privacy",
    title: "Quyền riêng tư",
    desc: "Kiểm soát dữ liệu và quyền riêng tư",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="5" y="11" width="14" height="9" rx="2" stroke="currentColor" strokeWidth="2" />
        <path d="M8 11V7a4 4 0 1 1 8 0v4" stroke="currentColor" strokeWidth="2" />
      </svg>
    )
  },
  {
    kind: "link",
    key: "lang",
    title: "Ngôn ngữ",
    desc: "Tiếng Việt",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
        <path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18" stroke="currentColor" strokeWidth="2" />
      </svg>
    )
  },
  {
    kind: "toggle",
    key: "dark",
    title: "Chế độ tối",
    desc: "Giao diện đêm",
    defaultOn: false,
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M21 13a8 8 0 0 1-10-10 9 9 0 1 0 10 10z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
      </svg>
    )
  },
  {
    kind: "link",
    key: "font",
    title: "Cỡ chữ",
    desc: "Trung bình",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path d="M5 19l5-14h2l5 14h-2.2l-1.3-4h-5l-1.3 4H5zm4-6h4l-2-6.5L9 13z" />
      </svg>
    )
  },
  {
    kind: "link",
    key: "a11y",
    title: "Trợ năng",
    desc: "Hỗ trợ trải nghiệm dễ dàng hơn",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="5" r="2" stroke="currentColor" strokeWidth="2" />
        <path d="M5 9h14M9 9l1 5h4l1-5M10 14l-2 7M14 14l2 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    )
  },
  {
    kind: "link",
    key: "help",
    title: "Trung tâm hỗ trợ",
    desc: "Câu hỏi thường gặp và trợ giúp",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
        <path d="M9.5 9.5a2.5 2.5 0 1 1 4 2.4c-.9.5-1.4 1.1-1.4 1.9M12 17h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
    )
  }
];

const SECURITY: Row[] = [
  {
    kind: "link",
    key: "password",
    title: "Đổi mật khẩu",
    desc: "Cập nhật mật khẩu tài khoản",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="5" y="11" width="14" height="9" rx="2" stroke="currentColor" strokeWidth="2" />
        <path d="M8 11V7a4 4 0 1 1 8 0v4" stroke="currentColor" strokeWidth="2" />
      </svg>
    )
  },
  {
    kind: "link",
    key: "2fa",
    title: "Xác thực hai yếu tố",
    desc: "Tăng cường bảo mật tài khoản",
    trailing: "Đang bật",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M12 3l8 3v6c0 5-3.5 8.5-8 9-4.5-.5-8-4-8-9V6l8-3z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
        <path d="M9 12l2 2 4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    )
  }
];

export function ProfileSettings() {
  return (
    <aside className="space-y-5">
      <SettingsCard title="Cài đặt" rows={SETTINGS} />
      <SettingsCard title="Bảo mật tài khoản" rows={SECURITY} />
      <ContinueJourneyCard />
    </aside>
  );
}

function SettingsCard({ title, rows }: { title: string; rows: Row[] }) {
  return (
    <section
      aria-label={title}
      className="rounded-card border border-ink-200 bg-white p-5 shadow-soft"
    >
      <h3 className="mb-3 flex items-center gap-2 text-base font-semibold text-ink-900">
        <span className="grid h-7 w-7 place-items-center rounded-pill bg-ink-100 text-ink-600">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="2" />
            <path
              d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33h0a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v0a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"
              stroke="currentColor"
              strokeWidth="2"
            />
          </svg>
        </span>
        {title}
      </h3>
      <ul className="divide-y divide-ink-100">
        {rows.map((r) => (
          <li key={r.key}>
            <SettingsRow row={r} />
          </li>
        ))}
      </ul>
    </section>
  );
}

function SettingsRow({ row }: { row: Row }) {
  const [on, setOn] = useState(row.kind === "toggle" ? Boolean(row.defaultOn) : false);

  if (row.kind === "toggle") {
    return (
      <div className="flex items-center gap-3 py-3">
        <span className="grid h-9 w-9 flex-none place-items-center rounded-pill bg-ink-100 text-ink-600">
          {row.icon}
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-ink-900">{row.title}</p>
          <p className="text-xs text-ink-500">{row.desc}</p>
        </div>
        <button
          type="button"
          role="switch"
          aria-checked={on}
          aria-label={`${row.title} - ${on ? "đang bật" : "đang tắt"}`}
          onClick={() => setOn((v) => !v)}
          className={`relative h-6 w-11 flex-none rounded-pill transition-colors ${
            on ? "bg-success" : "bg-ink-200"
          } cursor-pointer`}
        >
          <span
            className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow-soft transition-transform ${
              on ? "translate-x-[22px]" : "translate-x-0.5"
            }`}
          />
        </button>
      </div>
    );
  }

  return (
    <button
      type="button"
      className="group flex w-full items-center gap-3 py-3 text-left cursor-pointer"
    >
      <span className="grid h-9 w-9 flex-none place-items-center rounded-pill bg-ink-100 text-ink-600">
        {row.icon}
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-ink-900">{row.title}</p>
        <p className="text-xs text-ink-500">{row.desc}</p>
      </div>
      {row.trailing && (
        <span className="rounded-pill bg-success/12 px-2.5 py-1 text-[11px] font-semibold text-success">
          {row.trailing}
        </span>
      )}
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        aria-hidden="true"
        className="flex-none text-ink-400 transition-transform group-hover:translate-x-0.5 group-hover:text-brand"
      >
        <path d="M9 6l6 6-6 6" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </button>
  );
}

function ContinueJourneyCard() {
  return (
    <section
      aria-label="Tiếp tục hành trình"
      className="relative overflow-hidden rounded-card border border-success/30 bg-gradient-to-br from-success/10 via-white to-success/5 p-5 shadow-soft"
    >
      <h3 className="text-base font-semibold text-ink-900">Tiếp tục hành trình chăm sóc tâm hồn</h3>
      <p className="mt-1 max-w-[80%] text-xs text-ink-600">
        Bạn đang làm rất tốt. Hãy nhớ rằng mỗi ngày đều là một bước tiến nhỏ đến sự bình an.
      </p>

      <span className="mt-3 inline-flex h-8 w-8 items-center justify-center rounded-pill bg-success/15 text-success">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M12 21s-7-4.35-7-10a4.5 4.5 0 0 1 8-3 4.5 4.5 0 0 1 8 3c0 5.65-7 10-7 10h-2z" />
        </svg>
      </span>

      {/* Watering can illustration — placeholder SVG */}
      <span aria-hidden="true" className="pointer-events-none absolute right-2 bottom-2">
        <svg width="92" height="72" viewBox="0 0 120 90" fill="none">
          <path
            d="M30 45c0-8 7-15 18-15h28c10 0 18 7 18 15v22c0 4-3 7-7 7H37c-4 0-7-3-7-7V45z"
            fill="#86EFAC"
            opacity="0.7"
          />
          <path d="M30 50l-10-6v8l10 4M76 30l8-8h12l-4 8" stroke="#22C55E" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" fill="none" />
          <ellipse cx="55" cy="80" rx="14" ry="3" fill="#22C55E" opacity="0.4" />
          <path d="M50 32c2-6 5-9 8-9M58 28c2-4 5-6 9-6" stroke="#22C55E" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        </svg>
      </span>
    </section>
  );
}
