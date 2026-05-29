"use client";

/**
 * HydrationErrorSilencer — chặn dev overlay của Next.js cho lỗi
 * "Hydration failed" sinh ra do browser extension chèn DOM.
 *
 * Bối cảnh:
 *   - Password manager (LastPass, 1Password, Bitwarden, Dashlane...),
 *     Grammarly, antivirus extension... tự inject DOM/attribute vào
 *     trang ngay sau khi HTML server gửi xuống nhưng trước khi React
 *     hydrate. React thấy DOM != HTML server → ném warning hydration.
 *   - Đây là warning "recoverable": React vẫn auto fallback sang
 *     client rendering, page chạy bình thường. Vấn đề duy nhất là
 *     Next dev overlay pop lên "Unhandled Runtime Error" làm dev
 *     khó chịu.
 *
 * Quan trọng:
 *   - Trong production build (`next build && next start`) overlay
 *     này KHÔNG xuất hiện, end-user không thấy gì cả. Component này
 *     thuần là cải thiện DX khi dev.
 *   - Mọi lỗi runtime KHÁC (lỗi thật trong code) vẫn pop overlay
 *     bình thường — silencer chỉ filter đúng các pattern hydration.
 *   - Message vẫn được log ra dưới dạng `console.warn` với prefix
 *     `[hydration-silencer]` để dev có thể inspect khi cần.
 *
 * Cách dùng: mount 1 lần ở root client tree (vd `app/providers.tsx`).
 *
 * @see https://nextjs.org/docs/messages/react-hydration-error
 */

import { useEffect } from "react";

const HYDRATION_PATTERNS: RegExp[] = [
  /Hydration failed because/i,
  /There was an error while hydrating/i,
  /Text content (does not|did not) match/i,
  /Expected server HTML to contain/i,
  /Did not expect server HTML to contain/i,
  /A tree hydrated but some attributes/i,
  /Switched to client rendering/i,
  /In HTML, .* cannot be a child of/i,
];

function looksLikeHydrationError(value: unknown): boolean {
  const text =
    typeof value === "string"
      ? value
      : value instanceof Error && typeof value.message === "string"
        ? value.message
        : "";
  if (text.length === 0) return false;
  return HYDRATION_PATTERNS.some((p) => p.test(text));
}

export function HydrationErrorSilencer() {
  useEffect(() => {
    const w = window as unknown as {
      __medisignHydrationSilencerInstalled?: boolean;
    };
    if (w.__medisignHydrationSilencerInstalled) return;
    w.__medisignHydrationSilencerInstalled = true;

    // 1. Override console.error — Next dev overlay subscribe vào console
    //    để biết khi nào pop. Filter trước, demote sang warn để vẫn nhìn
    //    thấy được.
    const originalError = console.error.bind(console);
    console.error = (...args: unknown[]) => {
      if (args.some(looksLikeHydrationError)) {
        console.warn("[hydration-silencer]", ...args);
        return;
      }
      originalError(...args);
    };

    // 2. Bắt thêm window 'error' event ở capture phase phòng React rethrow
    //    qua kênh khác (Next overlay cũng listen kênh này).
    const onWindowError = (e: ErrorEvent) => {
      if (
        looksLikeHydrationError(e.error) ||
        looksLikeHydrationError(e.message)
      ) {
        e.stopImmediatePropagation();
        e.preventDefault();
        console.warn(
          "[hydration-silencer]",
          e.message || (e.error as Error)?.message
        );
      }
    };
    window.addEventListener("error", onWindowError, true);

    // 3. Promise rejection — không bắt buộc nhưng kín kẽ.
    const onRejection = (e: PromiseRejectionEvent) => {
      if (looksLikeHydrationError(e.reason)) {
        e.preventDefault();
        console.warn("[hydration-silencer]", e.reason);
      }
    };
    window.addEventListener("unhandledrejection", onRejection);

    return () => {
      console.error = originalError;
      window.removeEventListener("error", onWindowError, true);
      window.removeEventListener("unhandledrejection", onRejection);
      w.__medisignHydrationSilencerInstalled = false;
    };
  }, []);

  return null;
}
