import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({
  subsets: ["latin", "vietnamese"],
  variable: "--font-inter",
  display: "swap"
});

export const metadata: Metadata = {
  title: "MediSign AI — Trợ lý y tế AI cho mọi gia đình",
  description:
    "Hỏi bác sĩ AI bằng giọng nói, chữ viết, click, hay ngôn ngữ ký hiệu. Chăm sóc sức khỏe tại nhà cho người Việt.",
  metadataBase: new URL("https://medisign.ai"),
  openGraph: {
    title: "MediSign AI — Trợ lý y tế AI",
    description:
      "Hỏi bác sĩ AI bằng giọng nói, chữ viết, click, hay ngôn ngữ ký hiệu.",
    type: "website",
    locale: "vi_VN"
  }
};

// Viewport phải tách riêng theo Next 14+ — đảm bảo mobile rendering
// dùng width=device-width và cho phép user zoom (a11y).
export const viewport: import("next").Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: "#0EA5A5"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" className={inter.variable} suppressHydrationWarning>
      <head>
        {/*
          Preconnect tới R2 origin để rút ngắn TLS handshake khi `<video>`
          thật sự load (trang Login, Hero). KHÔNG dùng `<link rel="preload">`
          cho video MP4 ở đây vì:
            1. R2 chưa cấu hình CORS → request preload với `crossOrigin`
               sẽ bị block (`net::ERR_FAILED`).
            2. `<video>` element load qua range requests, không reuse được
               response của một preload đơn giản → browser raise warning
               "preloaded but not used" và tốn băng thông gấp đôi.
          Để tăng tốc lần đầu, hãy đặt `preload="auto"` trên element <video>
          tương ứng và bật CORS ở bucket R2 (Access-Control-Allow-Origin).
        */}
        <link
          rel="preconnect"
          href="https://pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev"
        />
        <link
          rel="dns-prefetch"
          href="https://pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev"
        />
      </head>
      <body suppressHydrationWarning>
        <a href="#main" className="skip-link">
          Bỏ qua đến nội dung chính
        </a>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
