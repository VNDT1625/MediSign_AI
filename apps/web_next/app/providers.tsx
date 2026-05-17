"use client";

/**
 * Root client providers.
 *
 * Mounts the React Query client and `AuthProvider` so every client component
 * (including the public landing page and the protected `/app/*` shell) can
 * call `useAuth()` and React Query hooks.
 *
 * Wired into `app/layout.tsx` — see design.md → "Phân lớp web client"
 * (`AuthProvider` row) and `app/providers.tsx` row.
 */

import { useState, type ReactNode } from "react";
import { QueryClientProvider } from "@tanstack/react-query";

import { AuthProvider } from "../lib/auth/AuthProvider";
import { makeQueryClient } from "../lib/query/queryClient";

export function Providers({ children }: { children: ReactNode }) {
  // Lazy-init via `useState` so the client is created exactly once per
  // browser tab (component tree) and never reinstantiated on re-render.
  // On the server, each request gets its own isolated client.
  const [queryClient] = useState(() => makeQueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>{children}</AuthProvider>
    </QueryClientProvider>
  );
}
