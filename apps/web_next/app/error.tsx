"use client";

/**
 * Root error boundary — bắt mọi lỗi không được xử lý trong toàn bộ app.
 *
 * Next.js App Router yêu cầu file này phải là Client Component.
 * Đây là lớp bảo vệ cuối cùng: nếu một component nào đó ném lỗi mà
 * không có error boundary gần hơn (ví dụ lỗi từ AuthProvider, fetcher,
 * hay bất kỳ component nào trên trang chủ), lỗi sẽ được bắt ở đây
 * thay vì hiển thị màn hình trắng hoặc stack trace cho người dùng.
 *
 * Trường hợp phổ biến nhất: ApiError "Phiên đã hết hạn" từ fetcher
 * bung ra ngoài AuthProvider khi không có cookie hoặc cookie hết hạn.
 */

import { useEffect } from "react";
import { ApiError } from "@/lib/api/errors";

type Props = {
  error: Error & { digest?: string };
  reset: () => void;
};

function extractRequestId(err: Error): string | undefined {
  if (err instanceof ApiError) return err.requestId;
  return undefined;
}

export default function RootError({ error, reset }: Props) {
  useEffect(() => {
    // eslint-disable-next-line no-console
    console.error("[root] error boundary:", error);
  }, [error]);

  const isSessionExpired =
    error instanceof ApiError && error.code === "AUTH_SESSION_EXPIRED";

  const requestId = extractRequestId(error);
  const digest = error.digest;

  const friendlyMessage = isSessionExpired
    ? "Phiên đăng nhập đã hết hạn. Vui lòng tải lại trang và đăng nhập lại."
    : error.message && error.message.length > 0
      ? error.message
      : "Có lỗi xảy ra. Vui lòng thử lại.";

  return (
    <div
      role="alert"
      aria-live="assertive"
      className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10"
    >
      <div className="flex w-full max-w-md flex-col items-center gap-5 rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-lg">
        {/* Heroicons exclamation-triangle — không dùng emoji */}
        <span
          aria-hidden="true"
          className="grid h-14 w-14 place-items-center rounded-full bg-amber-50 text-amber-500"
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
          <h1 className="text-xl font-bold text-slate-900">Đã xảy ra lỗi</h1>
          <p className="text-sm text-slate-600">{friendlyMessage}</p>
        </div>

        <div className="flex flex-col gap-2 sm:flex-row">
          {isSessionExpired ? (
            <a
              href="/"
              className="inline-flex cursor-pointer items-center justify-center rounded-full bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow transition-colors hover:bg-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
            >
              Về trang chủ để đăng nhập
            </a>
          ) : (
            <>
              <button
                type="button"
                onClick={reset}
                className="inline-flex cursor-pointer items-center justify-center gap-2 rounded-full bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow transition-colors hover:bg-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
              >
                {/* Heroicons arrow-path */}
                <svg
                  width="16"
                  height="16"
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
                className="inline-flex cursor-pointer items-center justify-center rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-800 transition-colors hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
              >
                Về trang chủ
              </a>
            </>
          )}
        </div>

        {(requestId || digest) && (
          <div className="mt-1 w-full border-t border-slate-200 pt-3">
            <p className="text-xs leading-snug text-slate-400">
              {requestId && (
                <>
                  Mã yêu cầu:{" "}
                  <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-slate-700">
                    {requestId}
                  </code>
                </>
              )}
              {requestId && digest && <span aria-hidden="true"> · </span>}
              {digest && (
                <>
                  Mã lỗi:{" "}
                  <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-slate-700">
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
