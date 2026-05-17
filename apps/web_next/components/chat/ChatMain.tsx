"use client";

// Cột giữa: header AI, luồng tin nhắn, AI Analysis Card, quick replies, input.
// Theo spec mục 5.1 và 5.2.

import { useState } from "react";
import { apiFetch } from "@/lib/api/fetcher";
import {
  HistoryIcon,
  MoreIcon,
  DoubleCheckIcon,
  CheckIcon,
  VerifiedIcon,
  InfoIcon,
  PaperclipIcon,
  ImageIcon,
  SmileIcon,
  MicIcon,
  SendIcon,
  FileImageIcon,
  HospitalIcon,
  HomeIcon,
  StethoscopeIcon
} from "./icons";
import { MESSAGES, QUICK_REPLIES, type ChatMessage } from "./mock";

const QUICK_ICONS: Record<(typeof QUICK_REPLIES)[number]["icon"], React.ComponentType<{ size?: number }>> = {
  hospital: HospitalIcon,
  home: HomeIcon,
  stethoscope: StethoscopeIcon
};

export function ChatMain() {
  const [messages, setMessages] = useState<ChatMessage[]>(MESSAGES);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function sendMessage(text: string) {
    const trimmed = text.trim();
    if (!trimmed || isSending) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      kind: "text",
      text: trimmed,
      time: currentTime(),
      seen: true
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsSending(true);
    setError(null);

    try {
      const response = await apiFetch<AIChatResponse>("/ai/chat", {
        method: "POST",
        authRequired: false,
        timeoutMs: 45_000,
        body: {
          message: trimmed,
          adapter: "medical",
          use_rag: true,
          rag_top_k: 5
        }
      });

      const aiMessage: ChatMessage = {
        id: `ai-${Date.now()}`,
        role: "ai",
        kind: "text",
        text: formatAiContent(response),
        time: currentTime()
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Không gọi được backend AI.";
      setError(message);
      setMessages((prev) => [
        ...prev,
        {
          id: `ai-error-${Date.now()}`,
          role: "ai",
          kind: "text",
          text: "MediSign AI chưa kết nối được backend/model. Kiểm tra 3 server dev rồi thử lại.",
          bullets: [message],
          time: currentTime()
        }
      ]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <section
      aria-label="Hội thoại với MediSign AI"
      className="flex h-full min-h-0 w-full flex-col bg-white"
    >
      <ChatTopBar />
      <ChatStream messages={messages} isSending={isSending} />
      <QuickReplies />
      {error && (
        <div className="border-t border-rose-100 bg-rose-50 px-6 py-2 text-[13px] text-rose-700">
          {error}
        </div>
      )}
      <Composer isSending={isSending} onSend={sendMessage} />
    </section>
  );
}

function ChatTopBar() {
  return (
    <div className="flex items-center justify-between gap-3 border-b border-ink-200 px-6 py-4">
      <div className="flex items-center gap-3">
        <span
          aria-hidden
          className="flex h-11 w-11 items-center justify-center rounded-card bg-brand text-white shadow-soft"
        >
          <svg width="22" height="22" viewBox="0 0 32 32" fill="none">
            <path d="M16 2l11 4v9c0 7-5 12-11 15-6-3-11-8-11-15V6l11-4z" fill="currentColor" />
            <path
              d="M16 9v10M11 14h10"
              stroke="#fff"
              strokeWidth="2.4"
              strokeLinecap="round"
            />
          </svg>
        </span>
        <div>
          <div className="flex items-center gap-1.5">
            <h1 className="text-[18px] font-bold text-ink-900">MediSign AI</h1>
            <VerifiedIcon size={18} className="text-brand" />
          </div>
          <p className="text-[13px] text-ink-500">Trợ lý y tế AI của bạn</p>
        </div>
      </div>

      <div className="flex items-center gap-1">
        <button
          type="button"
          aria-label="Lịch sử cuộc trò chuyện"
          className="inline-flex h-10 w-10 items-center justify-center rounded-pill text-ink-500 hover:bg-ink-100 hover:text-ink-800 cursor-pointer"
        >
          <HistoryIcon size={20} />
        </button>
        <button
          type="button"
          aria-label="Tùy chọn khác"
          className="inline-flex h-10 w-10 items-center justify-center rounded-pill text-ink-500 hover:bg-ink-100 hover:text-ink-800 cursor-pointer"
        >
          <MoreIcon size={20} />
        </button>
      </div>
    </div>
  );
}

function ChatStream({
  messages,
  isSending
}: {
  messages: ChatMessage[];
  isSending: boolean;
}) {
  return (
    <div className="min-h-0 flex-1 overflow-y-auto bg-[#F8FAFC] px-6 py-6">
      <DateDivider label="Hôm nay" />
      <ul className="flex flex-col gap-4">
        {messages.map((m) => (
          <li key={m.id}>
            <MessageRow msg={m} />
          </li>
        ))}
        {isSending && (
          <li>
            <div className="flex items-start gap-3">
              <AiAvatar />
              <div className="rounded-2xl rounded-tl-sm bg-white px-4 py-3 text-[14px] text-ink-500 shadow-soft">
                Đang tra RAG và gọi model...
              </div>
            </div>
          </li>
        )}
      </ul>
    </div>
  );
}

function DateDivider({ label }: { label: string }) {
  return (
    <div className="mb-4 flex justify-center">
      <span className="rounded-pill bg-white px-3 py-1 text-[12px] font-medium text-ink-500 shadow-soft">
        {label}
      </span>
    </div>
  );
}

function MessageRow({ msg }: { msg: ChatMessage }) {
  if (msg.role === "user") {
    return <UserBubble msg={msg} />;
  }
  if (msg.kind === "analysis") {
    return <AnalysisCard msg={msg} />;
  }
  return <AiBubble msg={msg} />;
}

function AiAvatar() {
  return (
    <span
      aria-hidden
      className="flex h-9 w-9 shrink-0 items-center justify-center rounded-card bg-brand text-white shadow-soft"
    >
      <svg width="18" height="18" viewBox="0 0 32 32" fill="none">
        <path d="M16 2l11 4v9c0 7-5 12-11 15-6-3-11-8-11-15V6l11-4z" fill="currentColor" />
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

function AiBubble({
  msg
}: {
  msg: Extract<ChatMessage, { role: "ai"; kind: "text" }>;
}) {
  return (
    <div className="flex items-start gap-3">
      <AiAvatar />
      <div className="max-w-[640px] rounded-2xl rounded-tl-sm bg-white px-4 py-3 shadow-soft">
        <p className="text-[15px] leading-7 text-ink-800">{msg.text}</p>
        {msg.bullets && (
          <ul className="mt-2 space-y-1.5 text-[15px] text-ink-800">
            {msg.bullets.map((b, i) => (
              <li key={i} className="flex items-start gap-2">
                <span aria-hidden className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-ink-400" />
                <span>{b}</span>
              </li>
            ))}
          </ul>
        )}
        <p className="mt-2 text-right text-[11px] text-ink-400">{msg.time}</p>
      </div>
    </div>
  );
}

function UserBubble({
  msg
}: {
  msg: Extract<ChatMessage, { role: "user" }>;
}) {
  return (
    <div className="flex items-start justify-end">
      <div className="max-w-[640px] rounded-2xl rounded-tr-sm bg-brand px-4 py-3 text-white shadow-soft">
        {msg.kind === "text" ? (
          <p className="text-[15px] leading-7">{msg.text}</p>
        ) : (
          <ImageAttachmentPreview file={msg.file} />
        )}
        <div className="mt-1.5 flex items-center justify-end gap-1 text-[11px] text-white/80">
          <span>{msg.time}</span>
          {msg.seen ? (
            <DoubleCheckIcon size={14} className="text-white" />
          ) : (
            <CheckIcon size={14} className="text-white/80" />
          )}
        </div>
      </div>
    </div>
  );
}

function ImageAttachmentPreview({
  file
}: {
  file: { name: string; size: string };
}) {
  return (
    <div className="flex items-center gap-3 rounded-card bg-white/15 p-2 pr-4">
      <span
        aria-hidden
        className="flex h-14 w-14 items-center justify-center rounded-card bg-white/15 text-white"
      >
        {/* Placeholder ảnh X-quang — user sẽ bổ sung ảnh thật sau */}
        <FileImageIcon size={28} />
      </span>
      <div className="flex flex-col">
        <span className="truncate text-[14px] font-semibold">{file.name}</span>
        <span className="text-[12px] text-white/80">
          {file.size} · JPG
        </span>
      </div>
      <span className="ml-auto inline-flex h-7 w-7 items-center justify-center rounded-full bg-emerald-400/90 text-white">
        <CheckIcon size={16} />
      </span>
    </div>
  );
}

function AnalysisCard({
  msg
}: {
  msg: Extract<ChatMessage, { role: "ai"; kind: "analysis" }>;
}) {
  return (
    <div className="flex items-start gap-3">
      <AiAvatar />
      <div className="w-full max-w-[760px] space-y-3">
        <div className="rounded-2xl rounded-tl-sm bg-white px-4 py-3 shadow-soft">
          <p className="text-[15px] leading-7 text-ink-800">{msg.intro}</p>
          <p className="mt-1 text-right text-[11px] text-ink-400">{msg.time}</p>
        </div>

        {/* Hai cột: Đánh giá sơ bộ + Gợi ý xử trí */}
        <div className="grid gap-3 rounded-2xl bg-white p-4 shadow-soft md:grid-cols-2">
          <div className="rounded-card border border-ink-200 bg-ink-100/60 p-4">
            <h3 className="mb-2 flex items-center gap-2 text-[14px] font-semibold text-ink-800">
              <span
                aria-hidden
                className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-emerald-700"
              >
                <CheckIcon size={14} />
              </span>
              Đánh giá sơ bộ
            </h3>
            <ul className="space-y-1.5 text-[14px] text-ink-700">
              {msg.assessment.map((a) => (
                <li key={a.label} className="flex items-start gap-2">
                  <span
                    aria-hidden
                    className="mt-1 inline-flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-700"
                  >
                    <CheckIcon size={12} />
                  </span>
                  <span>
                    <span className="font-semibold text-ink-800">{a.label} </span>
                    {a.value}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-card border border-ink-200 bg-amber-50/60 p-4">
            <h3 className="mb-2 flex items-center gap-2 text-[14px] font-semibold text-ink-800">
              <span
                aria-hidden
                className="flex h-6 w-6 items-center justify-center rounded-full bg-amber-100 text-amber-700"
              >
                <InfoIcon size={14} />
              </span>
              Gợi ý xử trí
            </h3>
            <ul className="space-y-1.5 text-[14px] text-ink-700">
              {msg.handling.map((h, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span
                    aria-hidden
                    className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500"
                  />
                  <span>{h}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Lưu ý quan trọng */}
        <div className="flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-[13px] text-amber-900">
          <InfoIcon size={18} className="mt-0.5 shrink-0 text-amber-600" />
          <p className="flex-1 leading-6">{msg.note.text}</p>
          <span className="shrink-0 text-[11px] text-amber-700">{msg.note.time}</span>
        </div>
      </div>
    </div>
  );
}

function QuickReplies() {
  return (
    <div className="border-t border-ink-200 bg-white px-6 pt-3">
      <ul className="flex flex-wrap items-center gap-2">
        {QUICK_REPLIES.map((q) => {
          const Icon = QUICK_ICONS[q.icon];
          return (
            <li key={q.id}>
              <button
                type="button"
                className="inline-flex items-center gap-2 rounded-pill border border-ink-200 bg-white px-3.5 py-2 text-[13px] font-medium text-ink-700 transition-colors hover:border-brand hover:bg-brand-50 hover:text-brand-700 cursor-pointer"
              >
                <Icon size={16} />
                {q.label}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function Composer({
  isSending,
  onSend
}: {
  isSending: boolean;
  onSend: (message: string) => void;
}) {
  const [value, setValue] = useState("");

  return (
    <div className="bg-white px-6 pb-5 pt-3">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          const text = value;
          setValue("");
          onSend(text);
        }}
        className="flex items-center gap-2 rounded-pill border border-ink-200 bg-white px-3 py-2 shadow-soft focus-within:border-brand"
      >
        <label htmlFor="chat-input" className="sr-only">
          Nhập câu hỏi cho MediSign AI
        </label>
        <input
          id="chat-input"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={isSending}
          placeholder="Hỏi bất cứ điều gì về sức khỏe của bạn…"
          className="flex-1 bg-transparent px-2 py-2 text-[15px] text-ink-800 placeholder:text-ink-400 focus:outline-none"
        />

        <div className="flex items-center gap-1">
          <ToolbarButton aria-label="Đính kèm tệp">
            <PaperclipIcon size={18} />
          </ToolbarButton>
          <ToolbarButton aria-label="Đính kèm hình ảnh">
            <ImageIcon size={18} />
          </ToolbarButton>
          <ToolbarButton aria-label="Chèn biểu cảm">
            <SmileIcon size={18} />
          </ToolbarButton>
          <ToolbarButton aria-label="Ghi âm giọng nói">
            <MicIcon size={18} />
          </ToolbarButton>
          <button
            type="submit"
            aria-label="Gửi tin nhắn"
            disabled={isSending || !value.trim()}
            className="ml-1 inline-flex h-10 w-10 items-center justify-center rounded-pill bg-brand text-white shadow-soft transition-colors hover:bg-brand-700 cursor-pointer"
          >
            <SendIcon size={18} />
          </button>
        </div>
      </form>

      <p className="mt-3 text-center text-[12px] text-ink-500">
        MediSign AI có thể mắc sai sót. Vui lòng không thay thế cho chẩn đoán của bác sĩ.
      </p>
    </div>
  );
}

type AIChatResponse = {
  content: string;
  rag_used: boolean;
  fallback_used: boolean;
  sources: Array<{ record_id: string; title: string; type: string }>;
};

function formatAiContent(response: AIChatResponse): string {
  const sourceText = response.sources.length
    ? `\n\nNguồn RAG: ${response.sources
        .slice(0, 4)
        .map((source) => `[${source.record_id}] ${source.title}`)
        .join("; ")}`
    : "";
  const modeText = response.fallback_used
    ? "\n\nChế độ: fallback backend."
    : response.rag_used
      ? "\n\nChế độ: model + RAG."
      : "";
  return `${response.content}${sourceText}${modeText}`;
}

function currentTime(): string {
  return new Intl.DateTimeFormat("vi-VN", {
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date());
}

function ToolbarButton({
  children,
  ...rest
}: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type="button"
      className="inline-flex h-9 w-9 items-center justify-center rounded-pill text-ink-500 hover:bg-ink-100 hover:text-ink-800 cursor-pointer"
      {...rest}
    >
      {children}
    </button>
  );
}
