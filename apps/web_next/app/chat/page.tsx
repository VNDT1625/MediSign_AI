// Trang Chat AI — bố cục 3 cột (sidebar | chat | summary).
//
// Lift state lên parent vì hai cột bên trái (ChatSidebar) và giữa (ChatMain)
// đều cần biết mode hiện tại và thiết lập "Cao tuổi". 1 trục mode duy nhất
// `CommMode = text | voice | click | sign` — vừa là input vừa là output:
// mode quyết định cả cách user nhập và cách AI trả lời.

"use client";

import { useEffect, useState } from "react";
import { SiteHeader } from "@/components/SiteHeader";
import { LoginModal } from "@/components/LoginModal";
import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { ChatMain } from "@/components/chat/ChatMain";
import { ChatSummary } from "@/components/chat/ChatSummary";
import { defaultOutputFor, type CommMode, type OutputMode } from "@/components/chat/mock";

export default function ChatPage() {
  const [loginOpen, setLoginOpen] = useState(false);
  const [mode, setMode] = useState<CommMode>("text");
  // outputMode độc lập với input. `null` = chưa user-pick → tự mirror theo input.
  const [outputMode, setOutputMode] = useState<OutputMode | null>(null);
  const [elderly, setElderly] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const effectiveOutput: OutputMode = outputMode ?? defaultOutputFor(mode);

  // Voice intent integration — nhan event tu VoiceControlButton.
  useEffect(() => {
    function onMode(e: Event) {
      const m = (e as CustomEvent<CommMode>).detail;
      if (m === "text" || m === "voice" || m === "click" || m === "sign") {
        setMode(m);
        setOutputMode(null);
      }
    }
    function onElderly() {
      setElderly((v) => !v);
    }
    function onLogin() {
      setLoginOpen(true);
    }
    function onLogout() {
      setLoginOpen(false);
    }
    window.addEventListener("medisign:chat-mode", onMode as EventListener);
    window.addEventListener("medisign:elderly-toggle", onElderly);
    window.addEventListener("medisign:login", onLogin);
    window.addEventListener("medisign:logout", onLogout);
    return () => {
      window.removeEventListener("medisign:chat-mode", onMode as EventListener);
      window.removeEventListener("medisign:elderly-toggle", onElderly);
      window.removeEventListener("medisign:login", onLogin);
      window.removeEventListener("medisign:logout", onLogout);
    };
  }, []);

  // Persist elderly mode trong localStorage để user bật 1 lần là nhớ.
  useEffect(() => {
    try {
      const saved = localStorage.getItem("medisign:elderly");
      if (saved === "1") setElderly(true);
    } catch {}
  }, []);
  useEffect(() => {
    try { localStorage.setItem("medisign:elderly", elderly ? "1" : "0"); } catch {}
  }, [elderly]);

  return (
    <div className={`flex h-screen flex-col overflow-hidden bg-[#F1F5F9] ${elderly ? "elderly-mode" : ""}`}>
      <SiteHeader onLoginClick={() => setLoginOpen(true)} />

      {/* Mobile sidebar toggle — top-right floating to avoid overlap with composer */}
      <button
        type="button"
        onClick={() => setSidebarOpen(true)}
        aria-label="Mở menu chat"
        className="fixed top-[80px] right-3 z-30 inline-flex h-11 w-11 items-center justify-center rounded-full border border-ink-200 bg-white text-ink-700 shadow-card transition-transform hover:scale-105 cursor-pointer md:hidden"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M4 7h16M4 12h16M4 17h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        </svg>
      </button>

      {/* Mobile sidebar drawer overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div
            className="absolute inset-0 bg-ink-900/40 backdrop-blur-sm"
            onClick={() => setSidebarOpen(false)}
            aria-hidden="true"
          />
          <div className="absolute inset-y-0 left-0 w-[300px] max-w-[85vw] bg-white shadow-card">
            <div className="flex h-full flex-col">
              <div className="flex items-center justify-between border-b border-ink-200 px-4 py-3">
                <span className="text-sm font-semibold text-ink-900">Menu Chat</span>
                <button
                  type="button"
                  onClick={() => setSidebarOpen(false)}
                  aria-label="Đóng menu"
                  className="inline-flex h-9 w-9 items-center justify-center rounded-pill text-ink-500 hover:bg-ink-100 cursor-pointer"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M6 6l12 12M6 18L18 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  </svg>
                </button>
              </div>
              <div className="min-h-0 flex-1 overflow-hidden">
                <ChatSidebar
                  activeMode={mode}
                  onModeChange={(m) => {
                    setMode(m);
                    setSidebarOpen(false);
                  }}
                  outputMode={effectiveOutput}
                  onOutputModeChange={setOutputMode}
                  elderly={elderly}
                  onElderlyChange={setElderly}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* pt-* bù cho SiteHeader fixed (top-4 + h-14 + thở) */}
      <main
        id="main"
        className="mx-auto flex w-full min-h-0 max-w-[1440px] flex-1 px-2 pb-2 pt-[72px] sm:px-4 sm:pb-4 sm:pt-[80px] lg:px-6 lg:pt-[88px] 2xl:max-w-[1600px] 2xl:px-8"
      >
        <div
          className="
            grid h-full w-full gap-2 sm:gap-4
            grid-cols-1
            md:grid-cols-[300px_1fr]
            xl:grid-cols-[300px_1fr_320px]
            2xl:grid-cols-[340px_1fr_360px]
            2xl:gap-5
          "
        >
          {/* Cột trái */}
          <div className="hidden h-full min-h-0 overflow-hidden rounded-card border border-ink-200 bg-white shadow-soft md:block">
            <ChatSidebar
              activeMode={mode}
              onModeChange={setMode}
              outputMode={effectiveOutput}
              onOutputModeChange={setOutputMode}
              elderly={elderly}
              onElderlyChange={setElderly}
            />
          </div>

          {/* Cột giữa */}
          <div className="h-full min-h-0 overflow-hidden rounded-card border border-ink-200 bg-white shadow-soft">
            <ChatMain mode={mode} outputMode={effectiveOutput} elderly={elderly} />
          </div>

          {/* Cột phải */}
          <div className="hidden h-full min-h-0 overflow-hidden rounded-card border border-ink-200 bg-white shadow-soft xl:block">
            <ChatSummary />
          </div>
        </div>
      </main>

      <LoginModal open={loginOpen} onClose={() => setLoginOpen(false)} />
    </div>
  );
}
