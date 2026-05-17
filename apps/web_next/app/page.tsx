"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { SiteHeader } from "@/components/SiteHeader";
import { HeroVideo } from "@/components/HeroVideo";
import { LoginModal } from "@/components/LoginModal";
import { WhyChooseSection } from "@/components/sections/WhyChooseSection";
import { HowItWorksSection } from "@/components/sections/HowItWorksSection";
import { MultiPlatformSection } from "@/components/sections/MultiPlatformSection";
import { AppOnlyFeaturesSection } from "@/components/sections/AppOnlyFeaturesSection";
import { PricingSection } from "@/components/sections/PricingSection";
import { TestimonialsSection } from "@/components/sections/TestimonialsSection";
import { CTABanner } from "@/components/sections/CTABanner";
import { Footer } from "@/components/sections/Footer";

export default function HomePage() {
  const [loginOpen, setLoginOpen] = useState(false);
  const [pendingMessage, setPendingMessage] = useState<string | undefined>();
  const searchParams = useSearchParams();

  // Tự mở LoginModal khi được redirect từ /app/* với ?login=1
  // Ví dụ: /?login=1&session=expired (phiên hết hạn)
  //        /?login=1&intent=/app/medicine (chưa đăng nhập)
  useEffect(() => {
    const shouldOpenLogin = searchParams.get("login") === "1";
    const isSessionExpired = searchParams.get("session") === "expired";
    if (shouldOpenLogin) {
      if (isSessionExpired) {
        setPendingMessage("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại.");
      }
      setLoginOpen(true);
    }
  }, [searchParams]);

  function openLogin(message?: string) {
    setPendingMessage(message);
    setLoginOpen(true);
  }

  return (
    <>
      <SiteHeader onLoginClick={() => openLogin()} />

      <main id="main">
        <HeroVideo onAsk={(msg) => openLogin(msg || undefined)} />
        <WhyChooseSection />
        <HowItWorksSection />
        <MultiPlatformSection />
        <AppOnlyFeaturesSection />
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
