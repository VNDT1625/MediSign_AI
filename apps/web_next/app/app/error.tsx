"use client";

// Error boundary cho khu vực /app/* (Next.js App Router convention).
//
// File này BẮT BUỘC là Client Component (`"use client"`) — đây là yêu cầu
// của Next.js: error boundary chạy ở client để có thể `reset()` lại tree.
//
// Trách nhiệm:
//   - Hiển thị fallback thân thiện thay cho stack trace mặc định của
//     Next.js khi server layout (`/app/layout.tsx`) hoặc một sub-tree
//     trong `/app/*` ném exception (ví dụ `/auth/me` trả 5xx, lỗi runtime
//     khi render).
//   - Cung cấp nút "Thử lại" để gọi `reset()` (Next sẽ render lại đoạn
//     bị lỗi) — đây là cách phục hồi cục bộ, không cần full reload.
//   - Lộ `request_id` (nếu lỗi là `ApiError` từ `lib/api/errors`) ở footer
//     dưới dạng nhỏ, dễ copy, dùng cho ticket hỗ trợ.
//
// Tham chiếu:
//   - Requirement 2.2.2 (Auth Context / Loading shell).
//   - Requirement 2.4.1 (Error UX): "THE error toast SHALL hiển thị
//     `message` từ backend (đã VN hoá) + `request_id` ở góc nhỏ để hỗ
//     trợ. THE web SHALL có Error Boundary cấp `/app/layout.tsx` để
//     chặn crash."

import { useEffect } from "react";
import { ApiError } from "@/lib/api/errors";

type Props = {
  /**
   * Lỗi ném ra từ server component / client component bên trong /app/*.
   * Next.js gắn thêm `digest` (mã hash phục vụ tra log server-side) khi
   * lỗi xảy ra ở phía server.
   */
  error: Error & { digest?: string };
  /**
   * Callback do Next.js cung cấp để re-render sub-tree đã lỗi. Gọi nó
   * khi người dùng nhấn "Thử lại".
   */
  reset: () => void;
};

/**
 * Trả về `requestId` nếu `err` là instance `ApiError` (để TS thu hẹp
 * kiểu mà không cần ép kiểu ngoài). Tách ra cho dễ test sau này.
 */
function extractRequestId(err: Error): string | undefined {
  if (err instanceof ApiError) {
    return err.requestId;
  }
  return undefined;
}

export default function AppError({ error, reset }: Props) {
  // Log lỗi ra console phía client để dev có thông tin trong DevTools.
  // (Trong môi trường production, một telemetry hook sẽ thay thế chỗ này
  // ở Phase 2; hiện tại giữ tối giản để tránh phụ thuộc thêm.)
  useEffect(() => {
    // eslint-disable-next-line no-console
    console.error("[/app] error boundary:", error);
  }, [error]);

  const requestId = extractRequestId(error);
  const digest = error.digest;
  const friendlyMessage =
    error.message && error.message.length > 0
      ? error.message
      : "Có lỗi xảy ra khi tải khu vực ứng dụng. Vui lòng thử lại.";

  return (
    <div
      role="alert"
      aria-live="assertive"
      className="min-h-screen bg-[#F1F5F9] px-4 py-10"
    >
      <div className="mx-auto flex max-w-xl flex-col items-center gap-5 rounded-card border border-ink-200 bg-white/90 p-8 text-center shadow-card">
        {/* Heroicons exclamation-triangle 24/outline (inline SVG, no emoji). */}
        <span
          aria-hidden="true"
          className="grid h-14 w-14 place-items-center rounded-pill bg-warn-soft text-warn"
        >
          <svg
            width="28"
            height="28"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01M5.07 19h13.86c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </span>

        <div className="flex flex-col gap-2">
          <h1 className="text-h3 text-ink-900">Đã xảy ra lỗi</h1>
          <p className="text-body text-ink-600">{friendlyMessage}</p>
        </div>

        <div className="mt-2 flex flex-col gap-2 sm:flex-row">
          <button
            type="button"
            onClick={reset}
            className="inline-flex items-center justify-center gap-2 rounded-pill bg-brand px-5 py-2.5 text-[15px] font-semibold text-white shadow-soft transition-colors hover:bg-brand-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2 cursor-pointer"
          >
            {/* Heroicons arrow-path 24/outline */}
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16.023 9.348h4.992V4.355M2.985 14.652h4.992v4.992M3.51 9.348a8.25 8.25 0 0114.073-2.92l3.422 3.422M20.49 14.652a8.25 8.25 0 01-14.073 2.92L2.995 14.15"
              />
            </svg>
            Thử lại
          </button>

          <a
            href="/"
            className="inline-flex items-center justify-center rounded-pill border border-ink-200 bg-white px-5 py-2.5 text-[15px] font-semibold text-ink-800 transition-colors hover:bg-ink-100 hover:text-ink-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2 cursor-pointer"
          >
            Về trang chủ
          </a>
        </div>

        {/* Footer: request_id (ApiError) hoặc digest (server error) cho hỗ trợ */}
        {(requestId || digest) && (
          <div className="mt-2 w-full border-t border-ink-200 pt-3">
            <p className="text-[12px] leading-snug text-ink-500">
              {requestId && (
                <>
                  Mã yêu cầu (gửi cho hỗ trợ):{" "}
                  <code className="rounded bg-ink-100 px-1.5 py-0.5 font-mono text-ink-800">
                    {requestId}
                  </code>
                </>
              )}
              {requestId && digest && <span aria-hidden="true"> · </span>}
              {digest && (
                <>
                  Mã lỗi máy chủ:{" "}
                  <code className="rounded bg-ink-100 px-1.5 py-0.5 font-mono text-ink-800">
                    {digest}
                  </code>
                </>
              )}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
