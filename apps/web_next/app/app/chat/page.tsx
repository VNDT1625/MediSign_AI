"use client";

/**
 * `/app/chat` — protected chat page (triage / consult).
 *
 * Layout mirrors the existing desktop shell pattern:
 *   - `DesktopAppHeader` at the top (pill nav + bell + avatar)
 *   - Three-column grid: ChatSidebar | ChatPanel | ChatSummary
 *
 * Task 10.2: wires the real triage API call.
 *   - `ChatPanelScaffold` holds `messages` state and `isPending` flag.
 *   - On `handleSend`: adds user bubble optimistically, calls
 *     `api.consult.triage({ symptom_text, locale: "vi-VN" })`, then
 *     appends a bot bubble with `summary` + `recommendations`.
 *   - `ChatSidebar` receives the in-session turns list so it can render
 *     an ephemeral history alongside the empty-state from the server.
 *
 * @see Requirements 2.1.4 (prefill intent), 2.3.1 (chat triage).
 */

import { Suspense, useState, useCallback } from "react";
import { DesktopAppHeader } from "@/components/desktop/DesktopAppHeader";
import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { ChatSummary } from "@/components/chat/ChatSummary";
import { ChatPanel } from "@/components/chat/ChatPanel";
import type { ChatMessage } from "@/components/chat/ChatPanel";
import { triage } from "@/lib/api/consult";

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function DesktopChatPage() {
  return (
    <div className="flex h-screen flex-col overflow-hidden bg-[#F1F5F9]">
      <DesktopAppHeader
        pathname="/app/chat"
        user={{ name: "Nguyễn Minh Anh" }}
        notificationCount={3}
      />

      <main
        id="main"
        className="mx-auto flex w-full min-h-0 max-w-[1440px] flex-1 px-4 pb-4 pt-3 lg:px-6"
      >
        <div
          className="
            grid h-full w-full gap-4
            grid-cols-1
            md:grid-cols-[300px_1fr]
            xl:grid-cols-[300px_1fr_320px]
          "
        >
          {/*
           * Left column — history + communication modes.
           * ChatPanelScaffold is the state owner; it passes the in-session
           * turns down to ChatSidebar via the Suspense boundary wrapper.
           * We lift state to the page level so both columns share it.
           */}
          <Suspense fallback={<SidebarSkeleton />}>
            <ChatPageContent />
          </Suspense>
        </div>
      </main>
    </div>
  );
}

// ---------------------------------------------------------------------------
// ChatPageContent — state owner for the whole chat layout
// ---------------------------------------------------------------------------

/**
 * Holds the shared `messages` + `isPending` state so both `ChatSidebar`
 * (ephemeral turn list) and `ChatPanel` (bubble rendering) stay in sync.
 * Wrapped in a Suspense boundary at the page level because `ChatPanel`
 * calls `useSearchParams()` internally.
 */
function ChatPageContent() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isPending, setIsPending] = useState(false);
  /** Latest urgency level from the triage API — drives the RED banner. */
  const [urgencyLevel, setUrgencyLevel] = useState<string | undefined>(undefined);

  /** Timestamp helper — returns "HH:MM" in vi-VN locale. */
  function nowTime(): string {
    return new Date().toLocaleTimeString("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  const handleSend = useCallback(async (message: string) => {
    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      text: message,
      time: nowTime(),
    };

    // Optimistic: add user bubble immediately.
    setMessages((prev) => [...prev, userMsg]);
    setIsPending(true);

    try {
      const response = await triage({ symptom_text: message, locale: "vi-VN" });

      // Track the latest urgency level so the RED banner can be shown.
      setUrgencyLevel(response.urgency_level);

      const botMsg: ChatMessage = {
        id: `b-${Date.now()}`,
        role: "bot",
        text: response.summary,
        recommendations: response.recommendations,
        time: nowTime(),
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err: unknown) {
      // Surface a friendly error bubble so the user knows something went wrong.
      const errorText =
        err instanceof Error
          ? err.message
          : "Đã xảy ra lỗi. Vui lòng thử lại.";

      const errMsg: ChatMessage = {
        id: `e-${Date.now()}`,
        role: "bot",
        text: errorText,
        time: nowTime(),
      };

      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsPending(false);
    }
  }, []);

  // Derive the in-session turn list for the sidebar: just the user messages.
  const sessionTurns = messages
    .filter((m) => m.role === "user")
    .map((m) => ({ id: m.id, text: m.text, time: m.time ?? "" }));

  return (
    <>
      {/* Left column — history + communication modes */}
      <div className="hidden h-full min-h-0 overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm md:block">
        <ChatSidebar sessionTurns={sessionTurns} />
      </div>

      {/* Centre column — ChatPanel */}
      <div className="h-full min-h-0 overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
        <ChatPanel
          messages={messages}
          isPending={isPending}
          onSend={handleSend}
          urgencyLevel={urgencyLevel}
          className="h-full"
        />
      </div>

      {/* Right column — quick summary */}
      <div className="hidden h-full min-h-0 overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm xl:block">
        <ChatSummary />
      </div>
    </>
  );
}

// ---------------------------------------------------------------------------
// Loading skeletons
// ---------------------------------------------------------------------------

function SidebarSkeleton() {
  return (
    <>
      {/* Sidebar skeleton */}
      <div
        aria-busy="true"
        aria-label="Đang tải lịch sử…"
        className="hidden h-full min-h-0 overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm md:block"
      >
        <div className="flex flex-col gap-3 p-4">
          <div className="h-11 w-full animate-pulse rounded-full bg-slate-200" />
          <div className="h-10 w-full animate-pulse rounded-full bg-slate-200" />
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-9 w-full animate-pulse rounded-xl bg-slate-100" />
          ))}
        </div>
      </div>

      {/* ChatPanel skeleton */}
      <div
        aria-busy="true"
        aria-label="Đang tải hội thoại…"
        className="flex h-full min-h-0 flex-col gap-4 overflow-hidden rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
      >
        <div className="flex items-start gap-3">
          <div className="h-9 w-9 animate-pulse rounded-xl bg-slate-200" />
          <div className="h-16 w-64 animate-pulse rounded-2xl rounded-tl-sm bg-slate-200" />
        </div>
        <div className="flex justify-end">
          <div className="h-10 w-48 animate-pulse rounded-2xl rounded-tr-sm bg-slate-200" />
        </div>
        <div className="mt-auto h-14 w-full animate-pulse rounded-2xl bg-slate-200" />
      </div>

      {/* Summary skeleton */}
      <div className="hidden h-full min-h-0 overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm xl:block">
        <div className="flex flex-col gap-3 p-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-12 w-full animate-pulse rounded-xl bg-slate-100" />
          ))}
        </div>
      </div>
    </>
  );
}
