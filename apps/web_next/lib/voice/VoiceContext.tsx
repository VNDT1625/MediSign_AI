"use client";

/**
 * VoiceContext — share trang thai/handler controller giua nhieu component
 * (vd: nut floating o cac trang khac va chat-bubble cua bac si tren home).
 *
 * Mounted o `Providers` de cay component ben trong (HelloBubble, VoiceControlButton)
 * co the goi `useVoice()` lay state va goi `toggle()`.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import { useVoiceController } from "./useVoiceController";
import { executeIntent } from "./executor";
import type { IntentMatch } from "./intents";
import { tokenStore } from "@/lib/auth/tokenStore";

export type VoiceMode = "off" | "wake" | "command" | "executing";

export interface VoiceContextValue {
  enabled: boolean;
  panelOpen: boolean;
  mode: VoiceMode;
  transcript: string;
  lastReply: string;
  error: string | null;
  isSupported: boolean;
  mounted: boolean;
  toggle: () => void;
  setPanelOpen: (open: boolean) => void;
  beginCommand: () => void;
}

const VoiceContext = createContext<VoiceContextValue | null>(null);

export function VoiceProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [panelOpen, setPanelOpen] = useState(false);
  const [enabled, setEnabled] = useState(false);
  const lastReplyRef = useRef<string>("");
  const speakRef = useRef<(t: string) => void>(() => {});

  const handleIntent = useCallback(
    (intent: IntentMatch): string => {
      setPanelOpen(true);
      const reply = executeIntent(intent, {
        navigate: (path) => router.push(path),
        closeOverlay: () => setPanelOpen(false),
        stopListening: () => setEnabled(false),
        triggerEvent: (name, detail) => {
          if (typeof window !== "undefined") {
            window.dispatchEvent(new CustomEvent(name, { detail }));
          }
        },
        getLastReply: () => lastReplyRef.current,
        speak: (t) => speakRef.current(t),
        isLoggedIn: () => {
          const token = tokenStore.get();
          return token !== null && !tokenStore.isExpired();
        },
      });
      lastReplyRef.current = reply || lastReplyRef.current;
      return reply;
    },
    [router]
  );

  const controller = useVoiceController({ onIntent: handleIntent });

  useEffect(() => {
    speakRef.current = controller.speak;
  }, [controller.speak]);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (enabled) controller.start();
    else controller.stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled]);

  useEffect(() => {
    if (controller.mode === "command" || controller.mode === "executing") {
      setPanelOpen(true);
    }
  }, [controller.mode]);

  const toggle = useCallback(() => {
    setEnabled((v) => !v);
    setPanelOpen(true);
  }, []);

  const value = useMemo<VoiceContextValue>(
    () => ({
      enabled,
      panelOpen,
      mode: controller.mode,
      transcript: controller.transcript,
      lastReply: controller.lastReply,
      error: controller.error,
      isSupported: controller.isSupported,
      mounted,
      toggle,
      setPanelOpen,
      beginCommand: controller.beginCommand,
    }),
    [
      enabled,
      panelOpen,
      controller.mode,
      controller.transcript,
      controller.lastReply,
      controller.error,
      controller.isSupported,
      controller.beginCommand,
      mounted,
      toggle,
    ]
  );

  return <VoiceContext.Provider value={value}>{children}</VoiceContext.Provider>;
}

export function useVoice(): VoiceContextValue | null {
  return useContext(VoiceContext);
}
