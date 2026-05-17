"use client";

// Trang Home cho Desktop App (Tauri shell dùng web frontend).
// Theo UI_Mau/web_desktop/readme.md: "desktop = header của mobile và content của web"
// → Header: DesktopAppHeader (pill 5 tab + bell + avatar có tên)
// → Content: 100% giống web home (HeroVideo, WhyChoose, HowItWorks,
//             MultiPlatform, Pricing, Testimonials, CTA, Footer)

import { useState } from "react";
import { DesktopAppHeader } from "@/components/desktop/DesktopAppHeader";
import { HeroVideo } from "@/components/HeroVideo";
import { LoginModal } from "@/components/LoginModal";
import { WhyChooseSection } from "@/components/sections/WhyChooseSection";
import { HowItWorksSection } from "@/components/sections/HowItWorksSection";
import { MultiPlatformSection } from "@/components/sections/MultiPlatformSection";
import { PricingSection } from "@/components/sections/PricingSection";
import { TestimonialsSection } from "@/components/sections/TestimonialsSection";
import { CTABanner } from "@/components/sections/CTABanner";
import { Footer } from "@/components/sections/Footer";

export default function DesktopHomePage() {
  const [loginOpen, setLoginOpen] = useState(false);
  const [pendingMessage, setPendingMessage] = useState<string | undefined>();

  function openLogin(message?: string) {
    setPendingMessage(message);
    setLoginOpen(true);
  }

  return (
    <>
      <DesktopAppHeader
        pathname="/app"
        overlay
        user={{ name: "Nguyễn Minh Anh" }}
        notificationCount={3}
        onLogout={() => openLogin()}
      />

      <main id="main">
        <HeroVideo onAsk={(msg) => openLogin(msg || undefined)} />
        <WhyChooseSection />
        <HowItWorksSection />
        <MultiPlatformSection />
        <PricingSection />
        <TestimonialsSection />
        <CTABanner onCta={() => openLogin()} />
      </main>

      <Footer />

      <LoginModal
        open={loginOpen}
        onClose={() => setLoginOpen(false)}
        prefilledMessage={pendingMessage}
      />
    </>
  );
}
