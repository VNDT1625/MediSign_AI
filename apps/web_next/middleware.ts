import { NextResponse, type NextRequest } from "next/server";

/**
 * Legacy `/app/*` cleanup middleware.
 *
 * Trước đây các trang chat / profile sống trong shell `/app/*`. Sau khi
 * dọn dẹp lên public route, các URL thật là `/chat` và `/profile`.
 * Bất kỳ link cũ nào dạng `/app/...` đều được normalise lại để không
 * 404 và không bị middleware cũ đẩy về `/?login=1&intent=/app/...`
 * (gây loop khi đã đăng nhập).
 *
 *   - `/app/chat[*]`     → `/chat[*]`
 *   - `/app/profile[*]`  → `/profile[*]`
 *   - mọi `/app[/*]`     → `/`
 *
 * Search / hash được giữ nguyên để link sâu (`/app/chat?prefill=hi`
 * trở thành `/chat?prefill=hi`).
 */

export const config = {
  matcher: ["/app/:path*", "/app"],
};

export function middleware(req: NextRequest) {
  const { pathname, search } = req.nextUrl;

  let target = "/";
  if (pathname === "/app/chat" || pathname.startsWith("/app/chat/")) {
    target = pathname.replace(/^\/app\/chat/, "/chat");
  } else if (
    pathname === "/app/profile" ||
    pathname.startsWith("/app/profile/")
  ) {
    target = pathname.replace(/^\/app\/profile/, "/profile");
  }

  const redirectUrl = new URL(target, req.url);
  redirectUrl.search = search;
  return NextResponse.redirect(redirectUrl);
}
