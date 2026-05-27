"use client";

import { Suspense, useEffect, useState } from "react";
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

  function openLogin(message?: string) {
    setPendingMessage(message);
    setLoginOpen(true);
  }

  // Voice command "dang nhap" / "dang xuat" -> mo / dong LoginModal.
  useEffect(() => {
    function onLogin() {
      setLoginOpen(true);
    }
    function onLogout() {
      setLoginOpen(false);
    }
    window.addEventListener("medisign:login", onLogin);
    window.addEventListener("medisign:logout", onLogout);
    return () => {
      window.removeEventListener("medisign:login", onLogin);
      window.removeEventListener("medisign:logout", onLogout);
    };
  }, []);

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

      <Suspense fallback={null}>
        <LoginRedirectHandler onOpenLogin={openLogin} />
      </Suspense>

      <LoginModal
        open={loginOpen}
        onClose={() => setLoginOpen(false)}
        prefilledMessage={pendingMessage}
      />
    </>
  );
}

function LoginRedirectHandler({
  onOpenLogin,
}: {
  onOpenLogin: (message?: string) => void;
}) {
  const searchParams = useSearchParams();

  useEffect(() => {
    const shouldOpenLogin = searchParams.get("login") === "1";
    const isSessionExpired = searchParams.get("session") === "expired";
    if (shouldOpenLogin) {
      const msg = isSessionExpired
        ? "Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại."
        : undefined;
      onOpenLogin(msg);
    }
  }, [searchParams, onOpenLogin]);

  return null;
}
