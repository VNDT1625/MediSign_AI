"use client";

/**
 * `components/chat/ChatPanel.tsx` — self-contained chat UI panel.
 *
 * Responsibilities (Requirements 2.1.4, 2.3.1):
 *   - Read `?prefill=` from `useSearchParams()` and populate the textarea
 *     on first mount. Does NOT auto-send — the user must confirm.
 *   - Textarea: Enter key sends, Shift+Enter inserts a newline.
 *   - Textarea and send button are disabled while `isPending` is true.
 *   - Accepts `onSend(message: string)` prop so the parent wires the
 *     actual API call (task 10.2).
 *   - Accepts `messages` prop to render the conversation (user + bot
 *     bubbles). Falls back to an empty-state illustration when empty.
 *   - Accessible: all interactive elements have `aria-label`, visible
 *     `focus-visible:ring-2`, and `cursor-pointer`.
 *
 * @see Requirements 2.1.4 (prefill intent), 2.3.1 (chat triage).
 */

import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { SendIcon } from "./icons";

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

/** A single turn in the conversation. */
export interface ChatMessage {
  id: string;
  role: "user" | "bot";
  /** Primary text content (user message or bot summary). */
  text: string;
  /**
   * Ordered list of recommendation bullets rendered below the summary.
   * Only meaningful for bot messages from the triage endpoint.
   */
  recommendations?: string[];
  /** Optional timestamp string (e.g. "10:24"). */
  time?: string;
}

export interface ChatPanelProps {
  /** Called when the user submits a non-empty message. */
  onSend: (message: string) => void;
  /** Conversation turns to render. */
  messages?: ChatMessage[];
  /** When true, the input and send button are disabled. */
  isPending?: boolean;
  /**
   * Urgency level from the latest triage response.
   * When `"RED"`, a top-of-panel emergency banner is shown.
   * Requirements: 2.3.1, 2.4.3
   */
  urgencyLevel?: string;
  /** Optional CSS class applied to the root element. */
  className?: string;
}

// ---------------------------------------------------------------------------
// ChatPanel
// ---------------------------------------------------------------------------

export function ChatPanel({
  onSend,
  messages = [],
  isPending = false,
  urgencyLevel,
  className = "",
}: ChatPanelProps) {
  const searchParams = useSearchParams();
  const prefill = searchParams.get("prefill") ?? "";

  const [value, setValue] = useState<string>("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Populate from ?prefill= on first mount only — do NOT auto-send.
  useEffect(() => {
    if (prefill) {
      setValue(prefill);
      // Move cursor to end of pre-filled text.
      requestAnimationFrame(() => {
        const el = textareaRef.current;
        if (el) {
          el.selectionStart = el.selectionEnd = el.value.length;
          el.focus();
        }
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // intentionally run once on mount

  // Scroll to the latest message whenever the list changes.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSubmit() {
    const trimmed = value.trim();
    if (!trimmed || isPending) return;
    setValue("");
    onSend(trimmed);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
    // Shift+Enter falls through to the default textarea behaviour (newline).
  }

  return (
    <section
      aria-label="Hội thoại với MediSign AI"
      className={`flex h-full min-h-0 w-full flex-col bg-white ${className}`}
    >
      {/* ------------------------------------------------------------------ */}
      {/* RED urgency banner (Requirements 2.3.1, 2.4.3)                      */}
      {/* Shown when triage returns urgency_level === "RED".                  */}
      {/* Uses icon + text so color is NOT the only indicator (a11y).         */}
      {/* Contrast: white (#FFFFFF) on red-700 (#B91C1C) ≈ 5.9:1 ✓           */}
      {/* ------------------------------------------------------------------ */}
      {urgencyLevel === "RED" && (
        <div
          role="alert"
          aria-live="assertive"
          aria-atomic="true"
          className="flex items-center justify-between gap-3 bg-red-700 px-4 py-3 sm:px-6"
        >
          <div className="flex items-center gap-2.5 text-white">
            {/* Heroicons: phone-arrow-up-right (solid) */}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
              className="h-5 w-5 shrink-0"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M1.5 4.5a3 3 0 0 1 3-3h1.372c.86 0 1.61.586 1.819 1.42l1.105 4.423a1.875 1.875 0 0 1-.694 1.955l-1.293.97c-.135.101-.164.249-.126.352a11.285 11.285 0 0 0 6.697 6.697c.103.038.25.009.352-.126l.97-1.293a1.875 1.875 0 0 1 1.955-.694l4.423 1.105c.834.209 1.42.959 1.42 1.82V19.5a3 3 0 0 1-3 3h-2.25C8.552 22.5 1.5 15.448 1.5 6.75V4.5ZM16.5 3a.75.75 0 0 1 .75.75v3.75h3.75a.75.75 0 0 1 0 1.5h-3.75v3.75a.75.75 0 0 1-1.5 0V9h-3.75a.75.75 0 0 1 0-1.5H15.75V3.75A.75.75 0 0 1 16.5 3Z"
                clipRule="evenodd"
              />
            </svg>
            <span className="text-[15px] font-semibold leading-tight">
              Triệu chứng nguy hiểm — Gọi 115 ngay
            </span>
          </div>

          <a
            href="tel:115"
            aria-label="Gọi 115 ngay — cấp cứu"
            className="
              inline-flex shrink-0 cursor-pointer items-center gap-1.5
              rounded-lg border-2 border-white bg-white px-3 py-1.5
              text-[14px] font-bold text-red-700
              transition-colors
              hover:bg-red-50
              focus-visible:outline-none focus-visible:ring-2
              focus-visible:ring-white focus-visible:ring-offset-2
              focus-visible:ring-offset-red-700
            "
          >
            {/* Heroicons: phone-solid */}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
              className="h-4 w-4"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M1.5 4.5a3 3 0 0 1 3-3h1.372c.86 0 1.61.586 1.819 1.42l1.105 4.423a1.875 1.875 0 0 1-.694 1.955l-1.293.97c-.135.101-.164.249-.126.352a11.285 11.285 0 0 0 6.697 6.697c.103.038.25.009.352-.126l.97-1.293a1.875 1.875 0 0 1 1.955-.694l4.423 1.105c.834.209 1.42.959 1.42 1.82V19.5a3 3 0 0 1-3 3h-2.25C8.552 22.5 1.5 15.448 1.5 6.75V4.5Z"
                clipRule="evenodd"
              />
            </svg>
            Gọi 115
          </a>
        </div>
      )}
      {/* ------------------------------------------------------------------ */}
      {/* Message list                                                         */}
      {/* ------------------------------------------------------------------ */}
      <div
        role="log"
        aria-live="polite"
        aria-label="Lịch sử tin nhắn"
        className="min-h-0 flex-1 overflow-y-auto bg-[#F8FAFC] px-4 py-6 sm:px-6"
      >
        {messages.length === 0 ? (
          <EmptyState />
        ) : (
          <ul className="flex flex-col gap-4">
            {messages.map((msg) => (
              <li key={msg.id}>
                {msg.role === "user" ? (
                  <UserBubble message={msg} />
                ) : (
                  <BotBubble message={msg} />
                )}
              </li>
            ))}
          </ul>
        )}

        {isPending && <TypingIndicator />}

        {/* Scroll anchor */}
        <div ref={bottomRef} aria-hidden />
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Composer                                                             */}
      {/* ------------------------------------------------------------------ */}
      <div className="border-t border-gray-200 bg-white px-4 pb-5 pt-3 sm:px-6">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
          className="flex items-end gap-2 rounded-2xl border border-gray-200 bg-white px-3 py-2 shadow-sm transition-colors focus-within:border-cyan-500"
        >
          <label htmlFor="chat-panel-input" className="sr-only">
            Nhập câu hỏi cho MediSign AI
          </label>
          <textarea
            ref={textareaRef}
            id="chat-panel-input"
            rows={1}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isPending}
            placeholder="Hỏi bất cứ điều gì về sức khỏe của bạn… (Enter để gửi, Shift+Enter để xuống dòng)"
            aria-label="Nhập câu hỏi cho MediSign AI"
            className="
              max-h-40 min-h-[40px] flex-1 resize-none bg-transparent
              px-2 py-2 text-[15px] leading-6 text-slate-900
              placeholder:text-slate-400
              focus:outline-none
              disabled:cursor-not-allowed disabled:opacity-50
            "
            style={{ fieldSizing: "content" } as React.CSSProperties}
          />

          <button
            type="submit"
            aria-label="Gửi tin nhắn"
            disabled={isPending || !value.trim()}
            className="
              mb-0.5 inline-flex h-10 w-10 shrink-0 cursor-pointer items-center
              justify-center rounded-full bg-cyan-600 text-white shadow-sm
              transition-colors
              hover:bg-cyan-700
              focus-visible:outline-none focus-visible:ring-2
              focus-visible:ring-cyan-500 focus-visible:ring-offset-2
              disabled:cursor-not-allowed disabled:opacity-40
            "
          >
            <SendIcon size={18} aria-hidden />
          </button>
        </form>

        <p className="mt-2 text-center text-[12px] text-slate-500">
          MediSign AI có thể mắc sai sót. Vui lòng không thay thế cho chẩn đoán của bác sĩ.
        </p>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function EmptyState() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-4 py-16 text-center">
      {/* MediSign shield icon */}
      <span
        aria-hidden
        className="flex h-16 w-16 items-center justify-center rounded-2xl bg-cyan-600 text-white shadow-md"
      >
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none" aria-hidden>
          <path
            d="M16 2l11 4v9c0 7-5 12-11 15-6-3-11-8-11-15V6l11-4z"
            fill="currentColor"
          />
          <path
            d="M16 9v10M11 14h10"
            stroke="#fff"
            strokeWidth="2.4"
            strokeLinecap="round"
          />
        </svg>
      </span>
      <div>
        <p className="text-[17px] font-semibold text-slate-800">
          Xin chào! Tôi là MediSign AI
        </p>
        <p className="mt-1 text-[14px] text-slate-500">
          Hãy mô tả triệu chứng hoặc đặt câu hỏi về sức khỏe của bạn.
        </p>
      </div>
    </div>
  );
}

function AiAvatar() {
  return (
    <span
      aria-hidden
      className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-cyan-600 text-white shadow-sm"
    >
      <svg width="18" height="18" viewBox="0 0 32 32" fill="none" aria-hidden>
        <path
          d="M16 2l11 4v9c0 7-5 12-11 15-6-3-11-8-11-15V6l11-4z"
          fill="currentColor"
        />
        <path
          d="M16 9v10M11 14h10"
          stroke="#fff"
          strokeWidth="2.4"
          strokeLinecap="round"
        />
      </svg>
    </span>
  );
}

function BotBubble({ message }: { message: ChatMessage }) {
  return (
    <div className="flex items-start gap-3">
      <AiAvatar />
      <div className="max-w-[640px] rounded-2xl rounded-tl-sm bg-white px-4 py-3 shadow-sm">
        {/* Summary / main text */}
        <p className="whitespace-pre-wrap text-[15px] leading-7 text-slate-800">
          {message.text}
        </p>

        {/* Recommendations bulleted list */}
        {message.recommendations && message.recommendations.length > 0 && (
          <ul
            aria-label="Khuyến nghị"
            className="mt-3 flex flex-col gap-1.5 border-t border-slate-100 pt-3"
          >
            {message.recommendations.map((rec, i) => (
              <li
                key={i}
                className="flex items-start gap-2 text-[14px] leading-6 text-slate-700"
              >
                {/* Bullet dot */}
                <span
                  aria-hidden
                  className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-cyan-500"
                />
                {rec}
              </li>
            ))}
          </ul>
        )}

        {message.time && (
          <p className="mt-1.5 text-right text-[11px] text-slate-400">
            {message.time}
          </p>
        )}
      </div>
    </div>
  );
}

function UserBubble({ message }: { message: ChatMessage }) {
  return (
    <div className="flex items-start justify-end">
      <div className="max-w-[640px] rounded-2xl rounded-tr-sm bg-cyan-600 px-4 py-3 text-white shadow-sm">
        <p className="whitespace-pre-wrap text-[15px] leading-7">{message.text}</p>
        {message.time && (
          <p className="mt-1.5 text-right text-[11px] text-white/70">
            {message.time}
          </p>
        )}
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="mt-4 flex items-start gap-3">
      <AiAvatar />
      <div
        aria-label="MediSign AI đang trả lời"
        className="flex items-center gap-1.5 rounded-2xl rounded-tl-sm bg-white px-4 py-3 shadow-sm"
      >
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            aria-hidden
            className="h-2 w-2 animate-bounce rounded-full bg-slate-400"
            style={{ animationDelay: `${i * 150}ms` }}
          />
        ))}
      </div>
    </div>
  );
}
