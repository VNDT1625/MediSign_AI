"use client";

import { useState } from "react";
import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { LoginModal } from "@/components/LoginModal";
import { Footer } from "@/components/sections/Footer";
import { PageHero } from "@/components/sections/PageHero";
import { DownloadHeroVisual } from "@/components/sections/DownloadHeroVisual";
import { DownloadStores } from "@/components/sections/DownloadStores";
import { DownloadQR } from "@/components/sections/DownloadQR";
import { DownloadFeatures } from "@/components/sections/DownloadFeatures";
import { DownloadFAQ } from "@/components/sections/DownloadFAQ";
import { CTABanner } from "@/components/sections/CTABanner";

export default function DownloadPage() {
  const [loginOpen, setLoginOpen] = useState(false);

  return (
    <>
      <SiteHeader onLoginClick={() => setLoginOpen(true)} />

      <main id="main">
        <PageHero
          layout="balanced"
          eyebrow="Tải MediSign AI"
          title={
            <>
              Bác sĩ AI sẵn sàng,
              <br />
              <span className="gradient-text-brand">trên mọi thiết bị</span>
            </>
          }
          description={
            <p>
              Cài 1 lần, đồng bộ liền mạch giữa điện thoại, máy tính và web. Voice tiếng Việt,
              giao diện thân thiện cho cả người cao tuổi và khiếm thính.
            </p>
          }
          cta={
            <>
              <Link href="#stores" className="btn-primary">
                Chọn thiết bị
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  aria-hidden="true"
                >
                  <path
                    d="M12 4v12m0 0l-5-5m5 5l5-5M4 20h16"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </Link>
              <Link href="/" className="btn-outline">
                Dùng ngay trên web
              </Link>
            </>
          }
          extra={
            <ul className="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-ink-600">
              <li className="inline-flex items-center gap-2">
                <span className="flex items-center gap-0.5 text-warn">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <svg
                      key={i}
                      width="13"
                      height="13"
                      viewBox="0 0 24 24"
                      fill="currentColor"
                      aria-hidden="true"
                    >
                      <path d="M12 2l2.9 6.9L22 10l-5 4.9 1.2 7L12 18.6 5.8 22 7 14.9 2 10l7.1-1.1L12 2z" />
                    </svg>
                  ))}
                </span>
                <span className="font-semibold text-ink-900">4.9</span>
                <span className="text-ink-500">trên 8.200 reviews</span>
              </li>
              <li className="inline-flex items-center gap-2">
                <span className="grid h-6 w-6 place-items-center rounded-pill bg-success/15 text-success">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path
                      d="M12 3l8 3v6c0 5-3.5 8.5-8 9-4.5-.5-8-4-8-9V6l8-3z"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinejoin="round"
                    />
                    <path
                      d="M9 12l2 2 4-4"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </span>
                Bảo mật cấp y tế
              </li>
              <li className="inline-flex items-center gap-2">
                <span className="grid h-6 w-6 place-items-center rounded-pill bg-brand-50 text-brand-700">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path
                      d="M12 4v12m0 0l-5-5m5 5l5-5M4 20h16"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </span>
                250K+ lượt cài
              </li>
            </ul>
          }
          visual={<DownloadHeroVisual />}
        />

        <section id="stores">
          <DownloadStores />
        </section>
        <section id="qr">
          <DownloadQR />
        </section>
        <DownloadFeatures />
        <DownloadFAQ />
        <CTABanner onCta={() => setLoginOpen(true)} />
      </main>

      <Footer />

      <LoginModal open={loginOpen} onClose={() => setLoginOpen(false)} />
    </>
  );
}
