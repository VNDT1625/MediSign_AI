"use client";

/**
 * Root client providers.
 *
 * Mounts:
 *   - QueryClientProvider (React Query)
 *   - AuthProvider
 *   - VoiceProvider (chia se voice state cho HelloBubble + VoiceControlButton)
 *   - VoiceControlButton (pill noi + panel)
 */

import { useState, type ReactNode } from "react";
import { QueryClientProvider } from "@tanstack/react-query";

import { AuthProvider } from "../lib/auth/AuthProvider";
import { makeQueryClient } from "../lib/query/queryClient";
import { VoiceProvider } from "../lib/voice/VoiceContext";
import { VoiceControlButton } from "../components/VoiceControlButton";
import { HydrationErrorSilencer } from "../components/HydrationErrorSilencer";
import { RouteProgress } from "../components/RouteProgress";

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(() => makeQueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      {/*
        Filter dev-overlay cho lỗi hydration sinh ra do browser
        extension (password manager, Grammarly...) chèn DOM. Production
        không bị overlay nên component này chỉ ảnh hưởng dev DX.
      */}
      <HydrationErrorSilencer />
      {/*
        Top progress bar mảnh — feedback cho user khi click chuyển trang
        đỡ cảm giác "đơ". Tự bắt mọi <a> nội bộ, không cần wrap thêm.
      */}
      <RouteProgress />
      <AuthProvider>
        <VoiceProvider>
          {children}
          {/* Pill noi — tu an tren route "/" vi HelloBubble da co mic CTA */}
          <VoiceControlButton />
        </VoiceProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
