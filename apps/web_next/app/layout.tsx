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

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" className={inter.variable}>
      <head>
        {/*
          Preload video Login với priority cao — browser bắt đầu fetch ngay
          khi tải trang chủ, nên lần đầu user click "Tạo tài khoản" video
          đã có sẵn trong cache, không bị lag decode/network.
        */}
        <link
          rel="preload"
          as="video"
          type="video/mp4"
          href="https://pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev/kling_20260516_%E4%BD%9C%E5%93%81_The_camera_4212_0%20(1).mp4"
        />
        {/* Hint cho browser kết nối sớm tới R2 origin */}
        <link
          rel="preconnect"
          href="https://pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev"
          crossOrigin="anonymous"
        />
      </head>
      <body>
        <a href="#main" className="skip-link">
          Bỏ qua đến nội dung chính
        </a>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
