"use client";

/**
 * VoiceControlButton — pill noi va panel trang thai cho voice control.
 *
 * Su dung VoiceContext de chia se state voi cac trigger khac
 * (vd: HelloBubble tren home dat mic vao bong bong cua bac si).
 *
 * Tren route "/" (home) — pill o goc se an di vi HelloBubble da co mic CTA.
 * Cac trang khac — pill van hien.
 */

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import { useVoice } from "@/lib/voice/VoiceContext";

export function VoiceControlButton() {
  const voice = useVoice();
  const pathname = usePathname();

  // Esc dong panel
  useEffect(() => {
    if (!voice) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape" && voice && voice.panelOpen) voice.setPanelOpen(false);
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [voice]);

  if (!voice) return null;
  if (!voice.mounted) return null;
  if (!voice.isSupported) return null;

  const isHome = pathname === "/";

  const statusText = (() => {
    if (!voice.enabled) return 'Bấm để bật. Sau đó nói "Bác sĩ ơi" để ra lệnh.';
    switch (voice.mode) {
      case "wake": return 'Đang chờ wake-word "Bác sĩ ơi"...';
      case "command": return "Mình đang nghe. Hãy nói lệnh của bạn.";
      case "executing": return voice.lastReply || "Đang xử lý...";
      case "off":
      default: return "Đã tắt.";
    }
  })();

  return (
    <>
      {/* Pill noi — an tren home vi HelloBubble da co mic CTA */}
      {!isHome && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center" aria-live="polite">
          <button
            type="button"
            onClick={voice.toggle}
            className={`
              group flex items-center gap-2 pl-4 pr-2 py-2
              rounded-full shadow-xl border
              text-[13px] font-semibold
              transition-all duration-200
              hover:shadow-2xl hover:-translate-y-[1px]
              focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-blue-200
              cursor-pointer
              ${voice.enabled
                ? "bg-rose-600 text-white border-rose-700 hover:bg-rose-700"
                : "bg-white text-gray-800 border-gray-200 hover:bg-gray-50"}
            `}
            aria-label={voice.enabled ? "Tắt điều khiển bằng giọng nói" : "Bật điều khiển bằng giọng nói"}
            title={voice.enabled ? "Đang nghe — bấm để tắt" : "Điều khiển web qua giọng nói"}
          >
            <span className="whitespace-nowrap">
              {voice.enabled ? "Đang nghe..." : "Điều khiển web qua"}
            </span>
            <span
              className={`
                relative inline-flex h-9 w-9 items-center justify-center rounded-full
                transition-colors
                ${voice.enabled ? "bg-white/20" : "bg-blue-600 text-white"}
              `}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                <line x1="12" x2="12" y1="19" y2="22" />
              </svg>
              {voice.enabled && (
                <span className="absolute -right-0.5 -top-0.5 flex h-3 w-3">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75" />
                  <span className="relative inline-flex h-3 w-3 rounded-full bg-green-500" />
                </span>
              )}
            </span>
          </button>
        </div>
      )}

      {/* Panel trang thai — luon hien o moi route khi panelOpen */}
      {voice.panelOpen && (
        <div
          role="dialog"
          aria-label="Điều khiển bằng giọng nói"
          aria-modal="false"
          className="fixed bottom-24 right-6 z-50 w-[360px] max-w-[calc(100vw-48px)] overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-2xl"
        >
          <div className="flex items-center justify-between border-b border-gray-100 bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-3">
            <div>
              <h2 className="text-[14px] font-bold text-white">MediSign Voice</h2>
              <p className="text-[11px] text-white/80">Điều khiển bằng giọng nói</p>
            </div>
            <button
              type="button"
              onClick={() => voice.setPanelOpen(false)}
              className="flex h-8 w-8 items-center justify-center rounded-full text-white/80 transition-colors hover:bg-white/20 hover:text-white cursor-pointer"
              aria-label="Đóng"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="space-y-3 px-4 py-4">
            <div className="rounded-lg bg-blue-50 px-3 py-2 text-[13px] text-blue-900">
              {statusText}
            </div>

            {voice.transcript && (
              <div className="rounded-lg border border-gray-100 bg-gray-50 px-3 py-2">
                <p className="text-[11px] uppercase tracking-wide text-gray-500">Bạn vừa nói</p>
                <p className="mt-1 text-[13px] text-gray-800">{voice.transcript}</p>
              </div>
            )}

            {voice.lastReply && (
              <div className="rounded-lg border border-emerald-100 bg-emerald-50 px-3 py-2">
                <p className="text-[11px] uppercase tracking-wide text-emerald-700">Trợ lý</p>
                <p className="mt-1 text-[13px] text-emerald-900">{voice.lastReply}</p>
              </div>
            )}

            {voice.error && (
              <div className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-[12px] text-rose-700">
                {voice.error}
              </div>
            )}

            <div className="flex items-center gap-2 pt-1">
              <button
                type="button"
                onClick={voice.toggle}
                className={`flex-1 rounded-full px-3 py-2 text-[13px] font-semibold text-white transition-colors cursor-pointer ${
                  voice.enabled ? "bg-rose-600 hover:bg-rose-700" : "bg-blue-600 hover:bg-blue-700"
                }`}
              >
                {voice.enabled ? "Tắt nghe" : "Bật nghe"}
              </button>
              <button
                type="button"
                disabled={!voice.enabled}
                onClick={voice.beginCommand}
                className="flex-1 rounded-full border border-gray-200 bg-white px-3 py-2 text-[13px] font-medium text-gray-700 transition-colors hover:bg-gray-50 disabled:opacity-50 cursor-pointer"
              >
                Nói lệnh ngay
              </button>
            </div>

            <details className="rounded-lg border border-gray-100 bg-white">
              <summary className="cursor-pointer px-3 py-2 text-[12px] font-semibold text-gray-700">
                Các lệnh mẫu
              </summary>
              <ul className="space-y-1 px-3 pb-3 text-[12px] text-gray-600">
                <li>"Bác sĩ ơi, mở trang chat"</li>
                <li>"Bác sĩ ơi, mở tủ thuốc / hồ sơ / Soul Garden"</li>
                <li>"Cuộn xuống" / "Lên đầu trang"</li>
                <li>"Quay lại" / "Tải lại trang"</li>
                <li>"Đăng nhập" / "Đăng xuất"</li>
                <li>"Bấm gửi" / "Bấm đăng ký"</li>
                <li>"Viết là &lt;nội dung&gt;" - nhập vào ô</li>
                <li>"Gửi" / "Xóa nội dung"</li>
                <li>"Chế độ giọng nói" / "Chế độ văn bản"</li>
                <li>"Tăng cỡ chữ" / "Giảm cỡ chữ"</li>
                <li>"Đọc trang" / "Nói lại"</li>
              </ul>
            </details>
          </div>

          <div className="border-t border-gray-100 bg-gray-50 px-4 py-2 text-center text-[11px] text-gray-500">
            Nhấn <kbd className="rounded bg-gray-200 px-1 py-0.5 font-mono text-[10px]">Esc</kbd> để đóng panel · Hỗ trợ tiếng Việt
          </div>
        </div>
      )}
    </>
  );
}
