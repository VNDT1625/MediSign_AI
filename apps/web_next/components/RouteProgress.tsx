"use client";

/**
 * RouteProgress — top progress bar mảnh hiển thị khi user chuyển route,
 * tương tự nProgress trên GitHub / YouTube.
 *
 * Vấn đề giải quyết:
 *   Next App Router không có visual feedback giữa click và page transition.
 *   Pages "use client" + nặng chunk (chat, about) mất 0.5-2s để mount, user
 *   tưởng UI đơ. Component này hiện thanh tiến trình mảnh ở top → biết
 *   request đã được nhận, đang load.
 *
 * Cách hoạt động:
 *   - Listen click vào mọi `<a href>` cùng origin trong tài liệu (capture).
 *   - Bỏ qua: external link, target="_blank", anchor (#...), modifier key,
 *     hoặc href trùng pathname hiện tại (no-op).
 *   - Khi click hợp lệ → start animation: 0% → 70% (ease-out 600ms),
 *     giữ ở 70% để chờ page mới mount.
 *   - Khi `pathname` đổi → finish animation: 70% → 100% (200ms) rồi
 *     fade out (200ms) và reset.
 *   - Dùng `requestAnimationFrame` cho mượt, không setState liên tục.
 *
 * SSR-safe: tất cả DOM access nằm trong useEffect, render `null` ở server.
 *
 * A11y: thanh có `role="progressbar"` + aria-valuenow update qua
 * `aria-valuenow` attribute. `aria-hidden` khi ẩn.
 */

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";

const FINISH_MS = 200;
const FADE_OUT_MS = 200;

export function RouteProgress() {
  const pathname = usePathname();
  const barRef = useRef<HTMLDivElement | null>(null);
  const stateRef = useRef<{
    rafId: number | null;
    timeoutId: ReturnType<typeof setTimeout> | null;
    startedAt: number;
    progress: number;
    isActive: boolean;
  }>({
    rafId: null,
    timeoutId: null,
    startedAt: 0,
    progress: 0,
    isActive: false,
  });

  // Start animation khi user click <a> cùng origin.
  useEffect(() => {
    const apply = (progress: number, opacity = 1) => {
      const bar = barRef.current;
      if (!bar) return;
      bar.style.transform = `translateX(${progress - 100}%)`;
      bar.style.opacity = opacity.toString();
      bar.setAttribute("aria-valuenow", Math.round(progress).toString());
    };

    const reset = () => {
      const s = stateRef.current;
      if (s.rafId !== null) cancelAnimationFrame(s.rafId);
      if (s.timeoutId !== null) clearTimeout(s.timeoutId);
      s.rafId = null;
      s.timeoutId = null;
      s.progress = 0;
      s.isActive = false;
      const bar = barRef.current;
      if (bar) {
        bar.style.transition = "none";
        bar.style.transform = "translateX(-100%)";
        bar.style.opacity = "0";
        bar.setAttribute("aria-valuenow", "0");
        bar.setAttribute("aria-hidden", "true");
      }
    };

    const start = () => {
      const s = stateRef.current;
      if (s.isActive) return;
      s.isActive = true;
      s.startedAt = performance.now();
      s.progress = 0;
      const bar = barRef.current;
      if (bar) {
        bar.style.transition = "none";
        bar.removeAttribute("aria-hidden");
      }
      apply(0);

      // Ramp 0 → 70% theo easeOutCubic trong ~600ms, sau đó dừng để chờ
      // pathname đổi.
      const RAMP_MS = 600;
      const TARGET = 70;
      const tick = (now: number) => {
        const elapsed = now - s.startedAt;
        const t = Math.min(1, elapsed / RAMP_MS);
        const eased = 1 - Math.pow(1 - t, 3);
        s.progress = eased * TARGET;
        apply(s.progress);
        if (t < 1 && s.isActive) {
          s.rafId = requestAnimationFrame(tick);
        } else {
          s.rafId = null;
        }
      };
      s.rafId = requestAnimationFrame(tick);
    };

    const finish = () => {
      const s = stateRef.current;
      if (!s.isActive) return;
      if (s.rafId !== null) {
        cancelAnimationFrame(s.rafId);
        s.rafId = null;
      }
      const bar = barRef.current;
      if (bar) {
        bar.style.transition = `transform ${FINISH_MS}ms ease-out`;
        bar.style.transform = "translateX(0%)";
        bar.setAttribute("aria-valuenow", "100");
      }
      s.timeoutId = setTimeout(() => {
        if (bar) {
          bar.style.transition = `opacity ${FADE_OUT_MS}ms ease-out`;
          bar.style.opacity = "0";
        }
        s.timeoutId = setTimeout(reset, FADE_OUT_MS);
      }, FINISH_MS);
    };

    // Click handler — start progress khi click vào internal link.
    const onClick = (e: MouseEvent) => {
      // Modifier keys → mở tab mới, không phải nội bộ navigation.
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      if (e.button !== 0) return;
      if (e.defaultPrevented) return;

      const path = e.composedPath();
      let anchor: HTMLAnchorElement | null = null;
      for (const node of path) {
        if (
          node instanceof HTMLAnchorElement ||
          (node as HTMLElement)?.tagName === "A"
        ) {
          anchor = node as HTMLAnchorElement;
          break;
        }
      }
      if (!anchor) return;
      if (anchor.target && anchor.target !== "_self") return;
      if (anchor.hasAttribute("download")) return;

      const href = anchor.getAttribute("href");
      if (!href) return;
      // Anchor trong trang
      if (href.startsWith("#")) return;
      // mailto: tel: javascript:
      if (/^[a-z]+:/.test(href) && !href.startsWith("http")) return;

      let url: URL;
      try {
        url = new URL(anchor.href, window.location.href);
      } catch {
        return;
      }
      if (url.origin !== window.location.origin) return;

      // Click vào chính trang hiện tại (chỉ đổi hash hoặc trùng URL) → no-op.
      if (
        url.pathname === window.location.pathname &&
        url.search === window.location.search
      ) {
        return;
      }

      start();
    };

    document.addEventListener("click", onClick, true);
    return () => {
      document.removeEventListener("click", onClick, true);
      reset();
    };
  }, []);

  // Khi pathname đổi → kết thúc animation.
  useEffect(() => {
    const s = stateRef.current;
    if (!s.isActive) return;
    const bar = barRef.current;
    if (!bar) return;
    if (s.rafId !== null) {
      cancelAnimationFrame(s.rafId);
      s.rafId = null;
    }
    bar.style.transition = `transform ${FINISH_MS}ms ease-out`;
    bar.style.transform = "translateX(0%)";
    bar.setAttribute("aria-valuenow", "100");

    s.timeoutId = setTimeout(() => {
      if (bar) {
        bar.style.transition = `opacity ${FADE_OUT_MS}ms ease-out`;
        bar.style.opacity = "0";
      }
      s.timeoutId = setTimeout(() => {
        if (bar) {
          bar.style.transition = "none";
          bar.style.transform = "translateX(-100%)";
          bar.style.opacity = "0";
          bar.setAttribute("aria-valuenow", "0");
          bar.setAttribute("aria-hidden", "true");
        }
        s.progress = 0;
        s.isActive = false;
      }, FADE_OUT_MS);
    }, FINISH_MS);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname]);

  return (
    <div
      role="progressbar"
      aria-label="Đang tải trang"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={0}
      aria-hidden="true"
      className="pointer-events-none fixed inset-x-0 top-0 z-[100] h-[3px] overflow-hidden"
    >
      <div
        ref={barRef}
        className="h-full w-full bg-gradient-to-r from-brand via-[#0EA5E9] to-accent shadow-[0_0_8px_rgba(14,165,233,0.6)]"
        style={{ transform: "translateX(-100%)", opacity: 0 }}
      />
    </div>
  );
}
