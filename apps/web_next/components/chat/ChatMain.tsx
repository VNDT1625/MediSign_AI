"use client";

// =============================================================================
// ChatMain — cột giữa của trang Chat AI.
//
// LUỒNG (đơn giản — 1 trục mode):
//
//   1. User input qua composer ứng với mode (text / voice / click / sign).
//   2. Composer chuẩn hoá thành 1 string tiếng Việt — gọi là "câu chuẩn hoá".
//   3. POST /api/v1/ai/chat { message, mode, ... } — backend chỉ nhận text.
//   4. AI trả về text (content + sources).
//   5. Render câu trả lời theo output mode:
//        - text:  bubble chữ + bullets (mặc định)
//        - voice: bubble chữ + tự động TTS đọc to bằng tiếng Việt
//        - click: bubble chữ + nút "Bấm tiếp triệu chứng khác" để tiếp tục
//                  luồng click (multi-turn không cần gõ)
//        - sign:  rút ý chính từ text và phát chuỗi video VSL ngắn liên tục.
// =============================================================================

import { useEffect, useRef, useState } from "react";
import { apiFetch } from "@/lib/api/fetcher";
import { useSpeechRecognition } from "@/lib/hooks/useSpeechRecognition";
import { useTextToSpeech } from "@/lib/hooks/useTextToSpeech";
import { useVideoRecorder } from "@/lib/sign/useVideoRecorder";
import { recognizeSignVideo, SignRecognitionFailure } from "@/lib/sign/recognize";
import { BodyMap } from "./BodyMap";
import { intentFromText, type SignIntent } from "./SignAvatar";
import { VslSignVideoPlayer } from "./VslSignVideoPlayer";
import { VslRealtimeComposer } from "./VslRealtimeComposer";
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
  SignIcon,
  SendIcon,
  FileImageIcon
} from "./icons";
import {
  BODY_REGIONS,
  PAIN_LEVELS,
  type ChatMessage,
  type CommMode,
  type OutputMode,
  type BodyRegionId,
  type PainLevel
} from "./mock";

// Mỗi AI message có thể kèm `intent` (đã suy ra ở client) để mode sign
// dùng cho avatar, mode voice dùng cho TTS. Gắn vào ngay khi nhận response.
type AiTextMessage = Extract<ChatMessage, { role: "ai"; kind: "text" }> & { intent?: SignIntent };
type Message = ChatMessage | AiTextMessage;

type ChatMainProps = {
  /** Cách user nhập (input mode). */
  mode?: CommMode;
  /** Cách AI trả lời (output mode) — pick độc lập với mode. Mặc định = mode khi text/voice/sign, fallback "text" với click. */
  outputMode?: OutputMode;
  elderly?: boolean;
};

const MODE_LABEL: Record<CommMode, string> = {
  text: "Văn bản",
  voice: "Giọng nói",
  click: "Bấm chọn",
  sign: "Ký hiệu"
};

// =============================================================================
// Root
// =============================================================================

export function ChatMain({ mode = "text", outputMode = "text", elderly = false }: ChatMainProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setMessages([
      {
        id: "welcome",
        role: "ai",
        kind: "text",
        text: "Chào bạn! Tôi là MediSign AI, trợ lý chăm sóc sức khỏe thông minh của bạn. Bạn đang gặp triệu chứng gì hoặc có câu hỏi y tế nào không? Hãy chia sẻ để tôi hỗ trợ nhé!",
        time: currentTime(),
      }
    ]);
  }, []);

  async function sendMessage(text: string) {
    const trimmed = text.trim();
    if (!trimmed || isSending) return;

    const userMessage: Message = {
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
        body: { message: trimmed, mode, adapter: "medical", use_rag: false, rag_top_k: 5 }
      });
      const formatted = formatAiContent(response);
      const aiMessage: AiTextMessage = {
        id: `ai-${Date.now()}`,
        role: "ai",
        kind: "text",
        text: formatted,
        time: currentTime(),
        intent: intentFromText(formatted)
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Không gọi được backend AI.";
      setError(msg);
      setMessages((prev) => [
        ...prev,
        {
          id: `ai-error-${Date.now()}`,
          role: "ai",
          kind: "text",
          text: "MediSign AI chưa kết nối được backend. Hãy kiểm tra dev server và thử lại.",
          bullets: [msg],
          time: currentTime(),
          intent: "warn_followup"
        } as AiTextMessage
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
      <ChatTopBar mode={mode} elderly={elderly} />
      <ChatStream messages={messages} isSending={isSending} outputMode={outputMode} elderly={elderly} />
      {error && (
        <div className="border-t border-rose-100 bg-rose-50 px-6 py-2 text-[13px] text-rose-700">
          {error}
        </div>
      )}
      <Composer mode={mode} elderly={elderly} isSending={isSending} onSend={sendMessage} />
    </section>
  );
}

// =============================================================================
// Top bar
// =============================================================================

function ChatTopBar({ mode, elderly }: { mode: CommMode; elderly: boolean }) {
  return (
    <div id="chat-header" className="flex items-center justify-between gap-3 border-b border-ink-200 bg-white px-3 py-2.5 sm:px-5">
      <div className="flex min-w-0 items-center gap-3">
        <span aria-hidden className="flex h-9 w-9 shrink-0 items-center justify-center rounded-card bg-brand text-white shadow-soft">
          <svg width="18" height="18" viewBox="0 0 32 32" fill="none">
            <path d="M16 2l11 4v9c0 7-5 12-11 15-6-3-11-8-11-15V6l11-4z" fill="currentColor" />
            <path d="M16 9v10M11 14h10" stroke="#fff" strokeWidth="2.4" strokeLinecap="round" />
          </svg>
        </span>
        <div className="min-w-0">
          <div className="flex items-center gap-1.5">
            <h1 className={`truncate font-bold leading-tight text-ink-900 ${elderly ? "text-[18px]" : "text-[15px]"}`}>MediSign AI</h1>
            <VerifiedIcon size={15} className="shrink-0 text-brand" />
            <span className="ml-0.5 inline-flex shrink-0 items-center gap-1 rounded-pill bg-emerald-50 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-700">
              <span aria-hidden className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              Online
            </span>
          </div>
          <p className={`truncate leading-tight text-ink-500 ${elderly ? "text-[13px]" : "text-[11px]"}`}>
            Chế độ: <span className="font-semibold text-cyan-700">{MODE_LABEL[mode]}</span>
          </p>
        </div>
      </div>
      <div className="flex shrink-0 items-center gap-1">
        <button type="button" aria-label="Lịch sử cuộc trò chuyện" className="inline-flex h-9 w-9 items-center justify-center rounded-pill text-ink-500 hover:bg-ink-100 hover:text-ink-800 cursor-pointer">
          <HistoryIcon size={18} />
        </button>
        <button type="button" aria-label="Tùy chọn khác" className="inline-flex h-9 w-9 items-center justify-center rounded-pill text-ink-500 hover:bg-ink-100 hover:text-ink-800 cursor-pointer">
          <MoreIcon size={18} />
        </button>
      </div>
    </div>
  );
}

// =============================================================================
// Stream — render messages, auto-TTS khi mode = voice, render SignAvatar
// khi mode = sign, mọi cái khác là bubble chữ.
// =============================================================================

function ChatStream({
  messages,
  isSending,
  outputMode,
  elderly
}: {
  messages: Message[];
  isSending: boolean;
  outputMode: OutputMode;
  elderly: boolean;
}) {
  const tts = useTextToSpeech({ lang: "vi-VN", rate: elderly ? 0.9 : 1 });
  const lastSpokenRef = useRef<string | null>(null);

  // Voice mode: tự đọc câu trả lời AI mới nhất.
  useEffect(() => {
    if (outputMode !== "voice" || !tts.isSupported) return;
    const lastAi = [...messages].reverse().find((m) => m.role === "ai");
    if (!lastAi || lastAi.id === lastSpokenRef.current) return;
    const speech =
      lastAi.kind === "text" ? lastAi.text :
      lastAi.kind === "analysis" ? lastAi.intro : "";
    if (speech) {
      tts.speak(speech);
      lastSpokenRef.current = lastAi.id;
    }
  }, [messages, outputMode, tts]);

  return (
    <div id="chat-messages" className="min-h-0 flex-1 overflow-y-auto bg-[#F8FAFC] px-3 py-4 sm:px-6 sm:py-6">
      <DateDivider label="Hôm nay" />
      <ul className="flex flex-col gap-4">
        {messages.map((m) => (
          <li key={m.id}>
            <MessageRow msg={m} outputMode={outputMode} elderly={elderly} ttsSpeak={tts.speak} ttsSupported={tts.isSupported} />
          </li>
        ))}
        {isSending && (
          <li>
            <div className="flex items-start gap-3">
              <AiAvatar />
              <div className={`rounded-2xl rounded-tl-sm bg-white px-4 py-3 text-ink-500 shadow-soft ${elderly ? "text-[17px]" : "text-[14px]"}`}>
                Đang xử lý...
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
      <span className="rounded-pill bg-white px-3 py-1 text-[12px] font-medium text-ink-500 shadow-soft">{label}</span>
    </div>
  );
}

function MessageRow({
  msg,
  outputMode,
  elderly,
  ttsSpeak,
  ttsSupported
}: {
  msg: Message;
  outputMode: OutputMode;
  elderly: boolean;
  ttsSpeak: (text: string) => void;
  ttsSupported: boolean;
}) {
  if (msg.role === "user") return <UserBubble msg={msg} elderly={elderly} />;
  if (msg.kind === "analysis") return <AnalysisCard msg={msg} elderly={elderly} />;
  if (outputMode === "sign") {
    const ai = msg as AiTextMessage;
    return (
      <div className="flex items-start gap-3">
        <AiAvatar />
        <VslSignVideoPlayer text={ai.text} intent={ai.intent ?? intentFromText(ai.text)} elderly={elderly} />
      </div>
    );
  }
  return (
    <AiBubble
      msg={msg}
      onSpeak={outputMode === "voice" && ttsSupported ? () => ttsSpeak(msg.text) : undefined}
      elderly={elderly}
    />
  );
}

function AiBubble({
  msg,
  onSpeak,
  elderly
}: {
  msg: Extract<ChatMessage, { role: "ai"; kind: "text" }>;
  onSpeak?: () => void;
  elderly: boolean;
}) {
  return (
    <div className="flex items-start gap-3">
      <AiAvatar />
      <div className="max-w-[85%] rounded-2xl rounded-tl-sm bg-white px-4 py-3 shadow-soft sm:max-w-[640px]">
        <p className={`${elderly ? "text-[17px] leading-8" : "text-[14px] leading-6 sm:text-[15px] sm:leading-7"} text-ink-800`}>
          {msg.text}
        </p>
        {msg.bullets && (
          <ul className={`mt-2 space-y-1.5 ${elderly ? "text-[16px]" : "text-[14px] sm:text-[15px]"} text-ink-800`}>
            {msg.bullets.map((b, i) => (
              <li key={i} className="flex items-start gap-2">
                <span aria-hidden className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-ink-400" />
                <span>{b}</span>
              </li>
            ))}
          </ul>
        )}
        <div className="mt-2 flex items-center justify-end gap-2">
          {onSpeak && (
            <button type="button" onClick={onSpeak} aria-label="Đọc to lại câu này" className="inline-flex h-6 items-center gap-1 rounded-pill border border-emerald-200 bg-emerald-50 px-2 text-[11px] font-semibold text-emerald-700 hover:bg-emerald-100 cursor-pointer">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden>
                <path d="M11 5L6 9H2v6h4l5 4V5z" />
                <path d="M19 12c0-3-2-5-4-5" />
              </svg>
              Đọc to
            </button>
          )}
          <p className="text-[11px] text-ink-400">{msg.time}</p>
        </div>
      </div>
    </div>
  );
}

function UserBubble({ msg, elderly }: { msg: Extract<ChatMessage, { role: "user" }>; elderly: boolean }) {
  return (
    <div className="flex items-start justify-end">
      <div className="max-w-[85%] rounded-2xl rounded-tr-sm bg-brand px-4 py-3 text-white shadow-soft sm:max-w-[640px]">
        {msg.kind === "text" ? (
          <p className={`${elderly ? "text-[17px] leading-8" : "text-[14px] leading-6 sm:text-[15px] sm:leading-7"}`}>{msg.text}</p>
        ) : (
          <ImageAttachmentPreview file={msg.file} />
        )}
        <div className="mt-1.5 flex items-center justify-end gap-1 text-[11px] text-white/80">
          <span>{msg.time}</span>
          {msg.seen ? <DoubleCheckIcon size={14} className="text-white" /> : <CheckIcon size={14} className="text-white/80" />}
        </div>
      </div>
    </div>
  );
}

function ImageAttachmentPreview({ file }: { file: { name: string; size: string } }) {
  return (
    <div className="flex items-center gap-3 rounded-card bg-white/15 p-2 pr-4">
      <span aria-hidden className="flex h-14 w-14 items-center justify-center rounded-card bg-white/15 text-white">
        <FileImageIcon size={28} />
      </span>
      <div className="flex flex-col">
        <span className="truncate text-[14px] font-semibold">{file.name}</span>
        <span className="text-[12px] text-white/80">{file.size} · JPG</span>
      </div>
      <span className="ml-auto inline-flex h-7 w-7 items-center justify-center rounded-full bg-emerald-400/90 text-white">
        <CheckIcon size={16} />
      </span>
    </div>
  );
}

export function AnalysisCard({ msg, elderly = false }: { msg: Extract<ChatMessage, { role: "ai"; kind: "analysis" }>; elderly?: boolean }) {
  return (
    <div className="flex items-start gap-3">
      <AiAvatar />
      <div className="w-full max-w-[85%] space-y-3 sm:max-w-[760px]">
        <div className="rounded-2xl rounded-tl-sm bg-white px-4 py-3 shadow-soft">
          <p className={`text-ink-800 ${elderly ? "text-[18px] leading-8" : "text-[15px] leading-7"}`}>{msg.intro}</p>
          <p className="mt-1 text-right text-[11px] text-ink-400">{msg.time}</p>
        </div>
        <div className="grid gap-3 rounded-2xl bg-white p-4 shadow-soft md:grid-cols-2">
          <div className="rounded-card border border-ink-200 bg-ink-100/60 p-4">
            <h2 className="mb-2 flex items-center gap-2 text-[14px] font-semibold text-ink-800">
              <span aria-hidden className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">
                <CheckIcon size={14} />
              </span>
              Đánh giá sơ bộ
            </h2>
            <ul className={`space-y-1.5 text-ink-700 ${elderly ? "text-[16px]" : "text-[14px]"}`}>
              {msg.assessment.map((a) => (
                <li key={a.label} className="flex items-start gap-2">
                  <span aria-hidden className="mt-1 inline-flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">
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
            <h2 className="mb-2 flex items-center gap-2 text-[14px] font-semibold text-ink-800">
              <span aria-hidden className="flex h-6 w-6 items-center justify-center rounded-full bg-amber-100 text-amber-700">
                <InfoIcon size={14} />
              </span>
              Gợi ý xử trí
            </h2>
            <ul className={`space-y-1.5 text-ink-700 ${elderly ? "text-[16px]" : "text-[14px]"}`}>
              {msg.handling.map((h, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span aria-hidden className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                  <span>{h}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className={`flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-amber-900 ${elderly ? "text-[15px]" : "text-[13px]"}`}>
          <InfoIcon size={18} className="mt-0.5 shrink-0 text-amber-600" />
          <p className="flex-1 leading-6">{msg.note.text}</p>
          <span className="shrink-0 text-[11px] text-amber-700">{msg.note.time}</span>
        </div>
      </div>
    </div>
  );
}

function AiAvatar() {
  return (
    <span aria-hidden className="flex h-9 w-9 shrink-0 items-center justify-center rounded-card bg-brand text-white shadow-soft">
      <svg width="18" height="18" viewBox="0 0 32 32" fill="none">
        <path d="M16 2l11 4v9c0 7-5 12-11 15-6-3-11-8-11-15V6l11-4z" fill="currentColor" />
        <path d="M16 9v10M11 14h10" stroke="#fff" strokeWidth="2.4" strokeLinecap="round" />
      </svg>
    </span>
  );
}

// =============================================================================
// Composer router — chọn UI theo mode. Mỗi composer cuối cùng đều gọi
// onSend(text) với 1 string tiếng Việt — backend không biết user dùng mode nào.
// =============================================================================

function Composer({ mode, elderly, isSending, onSend }: { mode: CommMode; elderly: boolean; isSending: boolean; onSend: (m: string) => void }) {
  if (mode === "voice") return <VoiceComposer elderly={elderly} isSending={isSending} onSend={onSend} />;
  if (mode === "click") return <ClickComposer elderly={elderly} isSending={isSending} onSend={onSend} />;
  if (mode === "sign")  return <VslRealtimeComposer elderly={elderly} isSending={isSending} onSend={onSend} />;
  return <TextComposer elderly={elderly} isSending={isSending} onSend={onSend} />;
}

// =============================================================================
// Text composer — input + nút mic inline (mặc định)
// =============================================================================

function TextComposer({ elderly, isSending, onSend }: { elderly: boolean; isSending: boolean; onSend: (m: string) => void }) {
  const [value, setValue] = useState("");
  const sr = useSpeechRecognition({ lang: "vi-VN", interimResults: true, continuous: false, silenceTimeoutMs: 3000 });
  useEffect(() => { if (sr.transcript) setValue(sr.transcript); }, [sr.transcript]);

  function toggleMic() {
    if (sr.isListening) sr.stop();
    else { sr.resetTranscript(); setValue(""); sr.start(); }
  }

  return (
    <div id="chat-input" className="bg-white px-3 pb-4 pt-3 sm:px-6 sm:pb-5">
      {sr.error && (
        <div className="mb-2 rounded-lg border border-rose-200 bg-rose-50 px-3 py-1.5 text-[12px] text-rose-700">{sr.error}</div>
      )}
      <form
        onSubmit={(e) => { e.preventDefault(); const text = value; setValue(""); sr.resetTranscript(); onSend(text); }}
        className="flex items-center gap-2 rounded-pill border border-ink-200 bg-white px-3 py-2 shadow-soft focus-within:border-brand"
      >
        <label htmlFor="chat-input-field" className="sr-only">Nhập câu hỏi cho MediSign AI</label>
        <input
          id="chat-input-field"
          data-voice="input"
          aria-label="Nhập câu hỏi cho MediSign AI"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={isSending}
          placeholder={sr.isListening ? "Đang nghe giọng nói..." : "Hỏi bất cứ điều gì về sức khỏe của bạn…"}
          className={`flex-1 bg-transparent px-2 py-2 text-ink-800 placeholder:text-ink-400 focus:outline-none ${elderly ? "text-[18px]" : "text-[15px]"}`}
        />
        <div className="flex items-center gap-1">
          {/* Paperclip + Image + Smile — chỉ hiện từ sm để tiết kiệm chỗ trên mobile */}
          <ToolbarButton aria-label="Đính kèm tệp" className="hidden sm:inline-flex h-9 w-9 items-center justify-center rounded-pill text-ink-500 hover:bg-ink-100 hover:text-ink-800 cursor-pointer"><PaperclipIcon size={18} /></ToolbarButton>
          <ToolbarButton aria-label="Đính kèm hình ảnh" className="hidden sm:inline-flex h-9 w-9 items-center justify-center rounded-pill text-ink-500 hover:bg-ink-100 hover:text-ink-800 cursor-pointer"><ImageIcon size={18} /></ToolbarButton>
          <ToolbarButton aria-label="Chèn biểu cảm" className="hidden md:inline-flex h-9 w-9 items-center justify-center rounded-pill text-ink-500 hover:bg-ink-100 hover:text-ink-800 cursor-pointer"><SmileIcon size={18} /></ToolbarButton>
          <ToolbarButton
            aria-label={sr.isListening ? "Dừng ghi âm" : "Ghi âm giọng nói"}
            onClick={toggleMic}
            disabled={!sr.isSupported}
            className={`inline-flex h-9 w-9 items-center justify-center rounded-pill cursor-pointer transition-colors ${
              sr.isListening
                ? "bg-rose-100 text-rose-600 hover:bg-rose-200"
                : "text-ink-500 hover:bg-ink-100 hover:text-ink-800"
            } ${!sr.isSupported ? "opacity-40 cursor-not-allowed" : ""}`}
          >
            <MicIcon size={18} />
          </ToolbarButton>
          <button
            type="submit"
            data-voice="submit"
            aria-label="Gửi tin nhắn"
            disabled={isSending || !value.trim()}
            className="ml-1 inline-flex h-10 w-10 items-center justify-center rounded-pill bg-brand text-white shadow-soft transition-colors hover:bg-brand-700 cursor-pointer disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-brand"
          >
            <SendIcon size={18} />
          </button>
        </div>
      </form>
      <p className="mt-3 text-center text-[11px] text-ink-500 sm:text-[12px]">MediSign AI có thể mắc sai sót. Không thay thế cho chẩn đoán của bác sĩ.</p>
    </div>
  );
}

// =============================================================================
// Voice composer — 1 nút orb đơn giản kiểu ChatGPT voice mode.
// User bấm = bắt đầu nghe, bấm lần nữa = dừng và GỬI luôn (không cần gõ).
// =============================================================================

function VoiceComposer({ elderly, isSending, onSend }: { elderly: boolean; isSending: boolean; onSend: (m: string) => void }) {
  const sr = useSpeechRecognition({ lang: "vi-VN", interimResults: true, continuous: true, silenceTimeoutMs: 4000 });
  const [draft, setDraft] = useState("");
  useEffect(() => { setDraft(sr.transcript); }, [sr.transcript]);

  function handleToggle() {
    if (sr.isListening) {
      const finalText = sr.stop();
      const send = (finalText || draft).trim();
      sr.resetTranscript();
      setDraft("");
      if (send) onSend(send);
    } else {
      setDraft("");
      sr.resetTranscript();
      sr.start();
    }
  }

  return (
    <div id="chat-input" className="border-t border-blue-100 bg-gradient-to-b from-blue-50 to-white px-6 pb-6 pt-5">
      {!sr.isSupported && (
        <div className="mb-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-[13px] text-amber-800">
          <strong>Trình duyệt không hỗ trợ.</strong> Hãy dùng Chrome/Edge/Safari.
        </div>
      )}
      {sr.error && (
        <div className="mb-3 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-[13px] text-rose-800">{sr.error}</div>
      )}
      <div className="flex flex-col items-center gap-3">
        <button
          type="button"
          onClick={handleToggle}
          disabled={isSending || !sr.isSupported}
          aria-label={sr.isListening ? "Dừng nghe và gửi cho AI" : "Bắt đầu nói với AI"}
          className={`relative inline-flex h-24 w-24 items-center justify-center rounded-full text-white shadow-xl transition-all duration-200 disabled:opacity-50 cursor-pointer ${
            sr.isListening ? "bg-rose-600 hover:bg-rose-700" : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          <MicIcon size={36} />
          {sr.isListening && (
            <>
              <span className="absolute inset-0 animate-ping rounded-full bg-rose-400 opacity-30" />
              <span className="absolute -inset-2 animate-pulse rounded-full border-2 border-rose-300 opacity-40" />
            </>
          )}
        </button>
        <p className={`${elderly ? "text-[18px]" : "text-[14px]"} font-semibold text-blue-950`}>
          {sr.isListening ? "Đang nghe..." : "Chạm để nói"}
        </p>
        <p className={`${elderly ? "text-[14px]" : "text-[12px]"} -mt-1 text-blue-700`}>
          {sr.isListening ? "Bấm lại để gửi, hoặc đợi tự dừng." : "Câu trả lời sẽ được đọc to bằng tiếng Việt."}
        </p>
        {draft && (
          <p className={`${elderly ? "text-[16px]" : "text-[13px]"} mt-1 max-w-[420px] rounded-xl bg-white px-3 py-1.5 text-center italic text-ink-600 shadow-soft`}>
            "{draft}"
          </p>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Click composer — SVG body map (multi-select) + chip mức độ (per-region).
//
// Luồng:
//   1. User chạm vùng đau trên BodyMap → multi-select Set<BodyRegionId>.
//   2. Mỗi vùng được chọn hiện 1 dòng có 3 chip nhẹ/vừa/nặng — chỉ chọn 1.
//   3. Khi đủ thông tin (có ít nhất 1 vùng + 1 mức độ), bấm "Hỏi AI" →
//      composer ghép thành câu tiếng Việt rồi gọi onSend(). Backend không
//      cần biết user dùng click — vẫn nhận text như mọi mode khác.
//
// 3D EXTENSION: thay <BodyMap> bằng react-three-fiber + GLTF body. Props
// (selected/onToggle) giữ nguyên.
// =============================================================================

function ClickComposer({ elderly, isSending, onSend }: { elderly: boolean; isSending: boolean; onSend: (m: string) => void }) {
  const [selected, setSelected] = useState<Set<BodyRegionId>>(new Set());
  const [levels, setLevels] = useState<Record<BodyRegionId, PainLevel>>({} as Record<BodyRegionId, PainLevel>);

  function toggleRegion(id: BodyRegionId) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
        setLevels((prevL) => {
          const copy = { ...prevL };
          delete copy[id];
          return copy;
        });
      } else {
        next.add(id);
      }
      return next;
    });
  }

  function setLevel(id: BodyRegionId, lvl: PainLevel) {
    setLevels((prev) => ({ ...prev, [id]: lvl }));
  }

  const orderedRegions = BODY_REGIONS.filter((r) => selected.has(r.id));
  const allRegionsHaveLevel = orderedRegions.every((r) => levels[r.id]);
  const canSend = orderedRegions.length > 0 && allRegionsHaveLevel;

  function handleSend() {
    if (!canSend) return;
    const parts = orderedRegions.map((r) => {
      const lvl = PAIN_LEVELS.find((p) => p.id === levels[r.id]);
      return `${r.phrase} mức ${lvl?.phrase ?? "vừa"}`;
    });
    const sentence = `Tôi bị đau ở ${parts.join(", ")}. Hãy tư vấn cho tôi nên làm gì.`;
    onSend(sentence);
    setSelected(new Set());
    setLevels({} as Record<BodyRegionId, PainLevel>);
  }

  return (
    <div id="chat-input" className="border-t border-amber-100 bg-amber-50/50 px-3 pb-4 pt-3 sm:px-6">
      <div className="grid gap-3 md:grid-cols-[260px_1fr]">
        <div className="flex flex-col items-center justify-start rounded-2xl border border-amber-200 bg-white p-2">
          <p className={`mb-1 ${elderly ? "text-[14px]" : "text-[12px]"} font-semibold text-amber-900`}>
            Chạm vào vùng bạn bị đau
          </p>
          <BodyMap selected={selected} onToggle={toggleRegion} elderly={elderly} />
          <p className={`mt-1 px-2 ${elderly ? "text-[12px]" : "text-[11px]"} text-center text-amber-800`}>
            Có thể chọn nhiều vùng. Chạm lại để bỏ chọn.
          </p>
        </div>

        <div className="flex flex-col gap-2">
          {orderedRegions.length === 0 ? (
            <p className={`rounded-xl border border-dashed border-amber-300 bg-white px-3 py-3 text-center ${elderly ? "text-[15px]" : "text-[13px]"} text-amber-900`}>
              Chưa có vùng nào được chọn. Hãy chạm vào hình bên trái.
            </p>
          ) : (
            <ul className="flex flex-col gap-2">
              {orderedRegions.map((region) => (
                <li key={region.id} className="flex flex-col gap-1.5 rounded-xl border border-amber-200 bg-white px-3 py-2">
                  <p className={`${elderly ? "text-[16px]" : "text-[13px]"} font-bold text-amber-900`}>{region.label}</p>
                  <div className="flex gap-1.5">
                    {PAIN_LEVELS.map((lvl) => {
                      const active = levels[region.id] === lvl.id;
                      return (
                        <button
                          key={lvl.id}
                          type="button"
                          onClick={() => setLevel(region.id, lvl.id)}
                          aria-pressed={active}
                          className={`flex-1 rounded-lg border px-2 py-1.5 ${elderly ? "text-[14px]" : "text-[12px]"} font-semibold cursor-pointer ${
                            active
                              ? "border-amber-500 bg-amber-500 text-white"
                              : "border-amber-200 bg-white text-amber-900 hover:bg-amber-100"
                          }`}
                        >
                          {lvl.label}
                        </button>
                      );
                    })}
                  </div>
                </li>
              ))}
            </ul>
          )}

          <button
            type="button"
            onClick={handleSend}
            disabled={!canSend || isSending}
            aria-label="Gửi mô tả vùng đau cho AI"
            className={`mt-1 inline-flex h-12 items-center justify-center gap-2 rounded-xl bg-amber-600 px-4 font-bold text-white shadow-soft hover:bg-amber-700 disabled:opacity-40 cursor-pointer ${elderly ? "text-[16px]" : "text-[14px]"}`}
          >
            <SendIcon size={18} />
            {canSend ? `Hỏi AI (${orderedRegions.length} vùng)` : "Chọn mức độ cho mỗi vùng"}
          </button>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Sign composer — record video → Gemini Vision → text → /ai/chat.
//
// LUỒNG (Phase 1 MVP, dùng Gemini làm zero-shot VSL recognizer):
//   1. User bấm "Mở camera"  → useVideoRecorder.requestCamera()
//   2. User bấm "Bắt đầu quay" → MediaRecorder buffer các chunk webm.
//   3. User bấm "Tôi nói xong" (hoặc tự dừng sau 15s) → đóng gói Blob.
//   4. POST /api/sign/recognize (multipart) → Gemini Vision dịch VSL → text VN.
//   5. onSend(text) — ChatMain gọi /ai/chat như mọi mode khác.
//   6. Output: VslSignVideoPlayer ghép clip có sẵn theo intent.
//
// Phase 2 (sau này): thay /api/sign/recognize bằng model VSL nội bộ
// (BiLSTM trên VOYA_VSL + nguyenanfms 472 từ — xem docs/CHAT_FLOW.md).
// UI giữ nguyên, chỉ đổi endpoint.
// =============================================================================

function SignComposer({ elderly, isSending, onSend }: { elderly: boolean; isSending: boolean; onSend: (m: string) => void }) {
  const recorder = useVideoRecorder({ maxDurationMs: 15_000 });
  const [phase, setPhase] = useState<"closed" | "ready" | "recording" | "recognizing" | "review">("closed");
  const [recognizedText, setRecognizedText] = useState<string>("");
  const [confidence, setConfidence] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const previewRef = useRef<HTMLVideoElement>(null);

  // Bind stream vào <video> preview khi camera bật / tắt.
  useEffect(() => {
    const el = previewRef.current;
    if (!el) return;
    if (recorder.stream) {
      el.srcObject = recorder.stream;
      el.play().catch(() => { /* autoplay policy — ignore */ });
    } else {
      el.srcObject = null;
    }
  }, [recorder.stream]);

  // Bám sát recorder.error để hiển thị banner đỏ.
  useEffect(() => {
    if (recorder.error) {
      setErrorMessage(recorder.error);
      setPhase("closed");
    }
  }, [recorder.error]);

  async function openCamera() {
    setErrorMessage(null);
    await recorder.requestCamera();
    setPhase("ready");
  }

  function closeCamera() {
    recorder.releaseCamera();
    setPhase("closed");
    setRecognizedText("");
    setConfidence(0);
  }

  function startRecording() {
    setRecognizedText("");
    setConfidence(0);
    setErrorMessage(null);
    recorder.start();
    setPhase("recording");
  }

  async function stopAndRecognize() {
    setPhase("recognizing");
    const blob = await recorder.stop();
    if (!blob || blob.size === 0) {
      setErrorMessage("Không có dữ liệu video. Hãy thử lại.");
      setPhase("ready");
      return;
    }
    try {
      const result = await recognizeSignVideo(blob);
      setRecognizedText(result.text);
      setConfidence(result.confidence);
      setPhase("review");
    } catch (err) {
      const msg =
        err instanceof SignRecognitionFailure
          ? err.message
          : err instanceof Error
            ? err.message
            : "Không nhận diện được video.";
      setErrorMessage(msg);
      setPhase("ready");
    }
  }

  function discardRecognition() {
    setRecognizedText("");
    setConfidence(0);
    setPhase("ready");
  }

  function confirmAndSend() {
    if (!recognizedText.trim()) return;
    onSend(recognizedText.trim());
    setRecognizedText("");
    setConfidence(0);
    setPhase("ready");
  }

  const seconds = Math.floor(recorder.elapsedMs / 1000);
  const tenths = Math.floor((recorder.elapsedMs % 1000) / 100);

  return (
    <div id="chat-input" className="border-t border-violet-100 bg-violet-50/60 px-3 pb-4 pt-3 sm:px-6">
      {/* Banner lỗi */}
      {errorMessage && (
        <div role="alert" className="mb-3 flex items-start gap-2 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-[13px] text-rose-800">
          <span aria-hidden className="mt-0.5">⚠</span>
          <span className="flex-1">{errorMessage}</span>
          <button
            type="button"
            onClick={() => setErrorMessage(null)}
            aria-label="Đóng thông báo"
            className="rounded-full px-1.5 text-rose-600 hover:bg-rose-100 cursor-pointer"
          >
            ×
          </button>
        </div>
      )}

      {/* Phase 0 — chưa mở camera */}
      {phase === "closed" && (
        <div className="flex flex-col items-center gap-3 rounded-2xl border-2 border-dashed border-violet-300 bg-white px-4 py-8 text-center">
          <span aria-hidden className="grid h-14 w-14 place-items-center rounded-full bg-violet-100 text-violet-700">
            <SignIcon size={28} />
          </span>
          <p className={`font-bold text-violet-900 ${elderly ? "text-[18px]" : "text-[15px]"}`}>
            Trò chuyện bằng ngôn ngữ ký hiệu Việt
          </p>
          <p className={`max-w-md text-violet-700 ${elderly ? "text-[15px]" : "text-[13px]"}`}>
            Bật camera, ký hiệu câu hỏi của bạn, AI sẽ nhận diện và trả lời.
            Tối đa 15 giây mỗi lần.
          </p>
          <button
            type="button"
            onClick={openCamera}
            className={`inline-flex h-12 items-center gap-2 rounded-xl bg-violet-600 px-5 font-bold text-white shadow-soft hover:bg-violet-700 cursor-pointer ${elderly ? "text-[16px]" : "text-[14px]"}`}
          >
            <SignIcon size={18} />
            Mở camera
          </button>
        </div>
      )}

      {/* Phase 1+ — camera đang mở */}
      {phase !== "closed" && phase !== "review" && (
        <div className="grid gap-3 md:grid-cols-[1fr_280px]">
          {/* Preview video */}
          <div className="relative overflow-hidden rounded-2xl bg-black">
            <video
              ref={previewRef}
              playsInline
              muted
              className="aspect-video h-full w-full -scale-x-100 object-cover"
              aria-label="Xem trước camera"
            />

            {/* Overlay chấm REC + đồng hồ */}
            {phase === "recording" && (
              <div className="absolute left-3 top-3 flex items-center gap-2 rounded-pill bg-black/70 px-3 py-1.5 text-white">
                <span aria-hidden className="h-2.5 w-2.5 animate-pulse rounded-full bg-rose-500" />
                <span className="font-mono text-[13px] font-bold tabular-nums">
                  {seconds.toString().padStart(2, "0")}.{tenths}s / 15s
                </span>
              </div>
            )}

            {/* Overlay loading khi đang gửi Gemini */}
            {phase === "recognizing" && (
              <div className="absolute inset-0 flex items-center justify-center bg-black/60 text-white">
                <div className="flex flex-col items-center gap-2 text-center">
                  <span aria-hidden className="h-10 w-10 animate-spin rounded-full border-4 border-white border-t-transparent" />
                  <p className="font-bold">Đang nhận diện ký hiệu…</p>
                  <p className="text-[12px] text-white/80">Có thể mất 5–10 giây</p>
                </div>
              </div>
            )}
          </div>

          {/* Cột điều khiển */}
          <div className="flex flex-col gap-2 rounded-2xl border border-violet-200 bg-white p-3">
            <p className={`font-bold text-violet-900 ${elderly ? "text-[16px]" : "text-[14px]"}`}>
              {phase === "ready" && "Sẵn sàng quay"}
              {phase === "recording" && "Đang ghi…"}
              {phase === "recognizing" && "AI đang đọc…"}
            </p>
            <p className={`text-violet-700 ${elderly ? "text-[14px]" : "text-[12px]"}`}>
              {phase === "ready" && "Bấm nút bên dưới để bắt đầu ký hiệu. Camera đang nhìn bạn."}
              {phase === "recording" && "Ký hiệu rõ ràng trong khung hình. Bấm 'Tôi nói xong' khi kết thúc."}
              {phase === "recognizing" && "Đang gửi video lên AI để dịch sang tiếng Việt."}
            </p>

            {phase === "ready" && (
              <>
                <button
                  type="button"
                  onClick={startRecording}
                  disabled={!recorder.stream || isSending}
                  className={`inline-flex h-12 items-center justify-center gap-2 rounded-xl bg-rose-600 px-4 font-bold text-white shadow-soft hover:bg-rose-700 disabled:opacity-40 cursor-pointer ${elderly ? "text-[16px]" : "text-[14px]"}`}
                >
                  <span aria-hidden className="h-3 w-3 rounded-full bg-white" />
                  Bắt đầu quay
                </button>
                <button
                  type="button"
                  onClick={closeCamera}
                  className={`inline-flex h-10 items-center justify-center rounded-xl border border-violet-200 bg-white font-semibold text-violet-700 hover:bg-violet-50 cursor-pointer ${elderly ? "text-[14px]" : "text-[13px]"}`}
                >
                  Đóng camera
                </button>
              </>
            )}

            {phase === "recording" && (
              <button
                type="button"
                onClick={stopAndRecognize}
                className={`inline-flex h-12 items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 font-bold text-white shadow-soft hover:bg-emerald-700 cursor-pointer ${elderly ? "text-[16px]" : "text-[14px]"}`}
              >
                <span aria-hidden className="h-3 w-3 rounded-sm bg-white" />
                Tôi nói xong
              </button>
            )}

            {phase === "recognizing" && (
              <button
                type="button"
                disabled
                className={`inline-flex h-12 items-center justify-center rounded-xl bg-violet-200 text-violet-500 ${elderly ? "text-[16px]" : "text-[14px]"}`}
              >
                Đang xử lý…
              </button>
            )}

            <p className="mt-1 text-center text-[11px] text-violet-500">
              MediSign AI dùng Google Gemini để nhận diện. Có thể mắc sai sót.
            </p>
          </div>
        </div>
      )}

      {/* Phase review — Gemini đã trả text, user xác nhận trước khi gửi */}
      {phase === "review" && (
        <div className="grid gap-3 md:grid-cols-[1fr_280px]">
          <div className="flex flex-col gap-2 rounded-2xl border-2 border-emerald-200 bg-emerald-50 p-4">
            <div className="flex items-center justify-between gap-2">
              <span className={`font-bold text-emerald-800 ${elderly ? "text-[15px]" : "text-[13px]"}`}>
                AI nhận diện được:
              </span>
              <span className={`rounded-pill bg-emerald-100 px-2.5 py-0.5 font-bold text-emerald-800 ${elderly ? "text-[13px]" : "text-[11px]"}`}>
                Độ tin cậy {Math.round(confidence * 100)}%
              </span>
            </div>
            <textarea
              aria-label="Câu được nhận diện, có thể chỉnh sửa"
              value={recognizedText}
              onChange={(e) => setRecognizedText(e.target.value)}
              rows={3}
              className={`w-full resize-none rounded-xl border border-emerald-300 bg-white px-3 py-2 text-emerald-950 focus:border-emerald-500 focus:outline-none ${elderly ? "text-[16px]" : "text-[14px]"}`}
            />
            <p className={`text-emerald-700 ${elderly ? "text-[13px]" : "text-[11px]"}`}>
              Bạn có thể chỉnh lại trước khi gửi cho AI.
            </p>
          </div>

          <div className="flex flex-col gap-2">
            <button
              type="button"
              onClick={confirmAndSend}
              disabled={isSending || !recognizedText.trim()}
              className={`inline-flex h-12 items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 font-bold text-white shadow-soft hover:bg-violet-700 disabled:opacity-40 cursor-pointer ${elderly ? "text-[16px]" : "text-[14px]"}`}
            >
              <SendIcon size={18} />
              Gửi cho AI
            </button>
            <button
              type="button"
              onClick={discardRecognition}
              className={`inline-flex h-10 items-center justify-center rounded-xl border border-violet-200 bg-white font-semibold text-violet-700 hover:bg-violet-50 cursor-pointer ${elderly ? "text-[14px]" : "text-[13px]"}`}
            >
              Quay lại
            </button>
            <button
              type="button"
              onClick={closeCamera}
              className={`inline-flex h-10 items-center justify-center rounded-xl text-violet-500 hover:bg-violet-100 cursor-pointer ${elderly ? "text-[13px]" : "text-[12px]"}`}
            >
              Đóng camera
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

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
        .map((s) => `[${s.record_id}] ${s.title}`)
        .join("; ")}`
    : "";
  const modeText = response.fallback_used
    ? "\n\nChế độ: fallback backend."
    : response.rag_used ? "\n\nChế độ: model + RAG." : "";
  return `${response.content}${sourceText}${modeText}`;
}

function currentTime(): string {
  return new Intl.DateTimeFormat("vi-VN", { hour: "2-digit", minute: "2-digit" }).format(new Date());
}

function ToolbarButton({ children, className: customClass, ...rest }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type="button"
      className={customClass ?? "inline-flex h-9 w-9 items-center justify-center rounded-pill text-ink-500 hover:bg-ink-100 hover:text-ink-800 cursor-pointer"}
      {...rest}
    >
      {children}
    </button>
  );
}

