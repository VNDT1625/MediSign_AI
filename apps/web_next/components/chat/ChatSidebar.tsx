"use client";

// Sidebar trái: lịch sử hội thoại + 4 mode giao tiếp + cài đặt người cao tuổi.
// Theo spec mục 5.1 và mục 6 của MediSign_AI_UI_Web_Final.md.
//
// Task 10.2: accepts `sessionTurns` (in-session ephemeral list of user messages)
// and renders an empty state when no history is available from the server.

import { useState } from "react";
import {
  PlusIcon,
  SearchIcon,
  TextIcon,
  VoiceIcon,
  ClickIcon,
  SignIcon,
  SettingsIcon,
  HelpIcon,
  FontSizeIcon
} from "./icons";
import { COMM_MODES, OUTPUT_MODES, type CommMode, type OutputMode } from "./mock";

const MODE_ICONS: Record<CommMode, React.ComponentType<{ size?: number }>> = {
  text: TextIcon,
  voice: VoiceIcon,
  click: ClickIcon,
  sign: SignIcon
};

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** A single in-session turn (user message only). */
export interface SessionTurn {
  id: string;
  /** The user's message text — truncated in the sidebar. */
  text: string;
  /** Formatted time string, e.g. "10:24". */
  time: string;
}

export interface ChatSidebarProps {
  /**
   * In-session ephemeral list of user turns. Populated by the parent
   * `ChatPageContent` as the user sends messages. Shown above the
   * server-side history (which is empty in Phase 1).
   */
  sessionTurns?: SessionTurn[];
  /** Cách user nhập (input). */
  activeMode?: CommMode;
  onModeChange?: (mode: CommMode) => void;
  /** Cách AI trả lời (output) — pick độc lập với activeMode. */
  outputMode?: OutputMode;
  onOutputModeChange?: (mode: OutputMode) => void;
  /** Toggle chữ to cho người cao tuổi / nhìn kém. */
  elderly?: boolean;
  onElderlyChange?: (enabled: boolean) => void;
}

// ---------------------------------------------------------------------------
// ChatSidebar
// ---------------------------------------------------------------------------

export function ChatSidebar({
  sessionTurns = [],
  activeMode: controlledMode,
  onModeChange,
  outputMode: controlledOutput,
  onOutputModeChange,
  elderly: controlledElderly,
  onElderlyChange
}: ChatSidebarProps) {
  const [internalMode, setInternalMode] = useState<CommMode>("text");
  const [internalOutput, setInternalOutput] = useState<OutputMode>("text");
  const [internalElderly, setInternalElderly] = useState(false);
  const activeMode = controlledMode ?? internalMode;
  const outputMode = controlledOutput ?? internalOutput;
  const elderly = controlledElderly ?? internalElderly;
  const selectMode = (next: CommMode) => {
    setInternalMode(next);
    onModeChange?.(next);
  };
  const selectOutput = (next: OutputMode) => {
    setInternalOutput(next);
    onOutputModeChange?.(next);
  };
  const toggleElderly = () => {
    const next = !elderly;
    setInternalElderly(next);
    onElderlyChange?.(next);
  };

  const hasSessionTurns = sessionTurns.length > 0;

  return (
    <aside
      aria-label="Lịch sử và chế độ giao tiếp"
      className="flex h-full w-full flex-col overflow-hidden"
    >
      {/* Header sidebar — giữ trên cùng, không scroll */}
      <div className="space-y-3 border-b border-gray-200 p-4">
        <button
          type="button"
          className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-full bg-cyan-600 text-[15px] font-semibold text-white shadow-sm transition-colors hover:bg-cyan-700 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500 focus-visible:ring-offset-2"
        >
          <PlusIcon size={18} />
          Cuộc trò chuyện mới
        </button>

        <label className="relative block">
          <span className="sr-only">Tìm kiếm cuộc trò chuyện</span>
          <SearchIcon
            size={18}
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
          />
          <input
            type="search"
            placeholder="Tìm kiếm cuộc trò chuyện"
            className="h-10 w-full rounded-full border border-gray-200 bg-white pl-9 pr-3 text-[14px] text-slate-800 placeholder:text-slate-400 focus:border-cyan-500 focus:outline-none"
          />
        </label>
      </div>

      {/* Lịch sử cuộc trò chuyện — vùng cao nhất, ưu tiên không gian */}
      <section
        className="min-h-0 flex-1 overflow-y-auto px-3 py-3"
        aria-label="Lịch sử cuộc trò chuyện"
      >
        {/* In-session ephemeral turns (from current session) */}
        {hasSessionTurns && (
          <>
            <h2 className="px-2 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
              Phiên hiện tại
            </h2>
            <ul className="mb-4 flex flex-col gap-0.5">
              {sessionTurns.map((turn, index) => (
                <li key={turn.id}>
                  <div
                    aria-current={index === sessionTurns.length - 1 ? "true" : undefined}
                    className={`flex w-full items-center gap-2 rounded-xl px-2.5 py-2 text-left ${
                      index === sessionTurns.length - 1
                        ? "bg-cyan-50 text-cyan-700"
                        : "text-slate-700"
                    }`}
                  >
                    <span
                      aria-hidden
                      className={`h-2 w-2 shrink-0 rounded-full ${
                        index === sessionTurns.length - 1
                          ? "bg-cyan-500"
                          : "bg-slate-300"
                      }`}
                    />
                    <span className="flex-1 truncate text-[14px] font-medium">
                      {turn.text}
                    </span>
                    <span className="shrink-0 text-[11px] text-slate-500">
                      {turn.time}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          </>
        )}

        {/* Server-side history section */}
        <h2 className="px-2 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
          Cuộc trò chuyện trước
        </h2>

        {/* Empty state — server returns [] in Phase 1 */}
        <HistoryEmptyState />
      </section>

      {/* Chân sidebar — 4 mode + tiện ích, gọn trong border-top */}
      <div className="space-y-3 border-t border-gray-200 p-3">
        {/* INPUT — bạn nói với AI bằng */}
        <section aria-label="Cách bạn nói với AI">
          <h2 className="px-1 pb-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            Bạn nói với AI bằng
          </h2>
          <div className="grid grid-cols-4 gap-1.5">
            {COMM_MODES.map((m) => {
              const Icon = MODE_ICONS[m.id];
              const active = activeMode === m.id;
              return (
                <button
                  key={m.id}
                  type="button"
                  aria-pressed={active}
                  onClick={() => selectMode(m.id)}
                  title={m.label}
                  className={`flex h-12 flex-col items-center justify-center gap-0.5 rounded-xl border text-[11px] font-semibold transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500 focus-visible:ring-offset-1 ${
                    active
                      ? "border-cyan-600 bg-cyan-600 text-white shadow-sm"
                      : "border-gray-200 bg-white text-slate-700 hover:border-cyan-100 hover:bg-cyan-50 hover:text-cyan-700"
                  }`}
                >
                  <Icon size={18} />
                  {m.label}
                </button>
              );
            })}
          </div>
        </section>

        {/* OUTPUT — AI trả lời bằng */}
        <section aria-label="Cách AI trả lời">
          <h2 className="px-1 pb-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            AI trả lời bằng
          </h2>
          <div className="grid grid-cols-3 gap-1.5">
            {OUTPUT_MODES.map((om) => {
              const active = outputMode === om.id;
              return (
                <button
                  key={om.id}
                  type="button"
                  aria-pressed={active}
                  onClick={() => selectOutput(om.id)}
                  title={om.hint}
                  className={`flex h-11 items-center justify-center rounded-xl border text-[12px] font-semibold transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-1 ${
                    active
                      ? "border-emerald-600 bg-emerald-600 text-white shadow-sm"
                      : "border-gray-200 bg-white text-slate-700 hover:border-emerald-100 hover:bg-emerald-50 hover:text-emerald-700"
                  }`}
                >
                  {om.label}
                </button>
              );
            })}
          </div>
        </section>

        {/* Tiện ích — icon-only buttons + toggle Chế độ cao tuổi */}
        <section aria-label="Cài đặt nhanh" className="flex items-center gap-1">
          <IconButton aria-label="Cài đặt">
            <SettingsIcon size={18} />
          </IconButton>
          <IconButton aria-label="Trợ giúp & Hướng dẫn">
            <HelpIcon size={18} />
          </IconButton>

          <div className="ml-auto flex items-center gap-2">
            <FontSizeIcon size={16} className="text-slate-500" />
            <span className="text-[12px] font-medium text-slate-700">Cao tuổi</span>
            <button
              type="button"
              role="switch"
              aria-checked={elderly}
              aria-label="Bật chế độ cao tuổi"
              onClick={toggleElderly}
              className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500 focus-visible:ring-offset-1 ${
                elderly ? "bg-cyan-600" : "bg-slate-200"
              }`}
            >
              <span
                aria-hidden
                className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
                  elderly ? "translate-x-4" : "translate-x-0.5"
                }`}
              />
            </button>
          </div>
        </section>
      </div>
    </aside>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

/**
 * Empty state shown when `GET /consult/triage/history` returns `[]`.
 * Phase 1: backend always returns an empty list until persistence lands.
 */
function HistoryEmptyState() {
  return (
    <div
      role="status"
      aria-label="Chưa có lịch sử trò chuyện"
      className="flex flex-col items-center gap-3 px-4 py-8 text-center"
    >
      {/* Illustration — chat bubble icon */}
      <span
        aria-hidden
        className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400"
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden
        >
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
      </span>
      <div>
        <p className="text-[13px] font-semibold text-slate-700">
          Chưa có lịch sử
        </p>
        <p className="mt-0.5 text-[12px] text-slate-500">
          Các cuộc trò chuyện sẽ xuất hiện ở đây sau khi bạn gửi tin nhắn.
        </p>
      </div>
    </div>
  );
}

function IconButton({
  children,
  ...rest
}: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type="button"
      className="inline-flex h-9 w-9 items-center justify-center rounded-full text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-800 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500 focus-visible:ring-offset-1"
      {...rest}
    >
      {children}
    </button>
  );
}
