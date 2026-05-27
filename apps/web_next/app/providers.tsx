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

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(() => makeQueryClient());

  return (
    <QueryClientProvider client={queryClient}>
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
