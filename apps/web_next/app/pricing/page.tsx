"use client";

import { useState } from "react";
import { SiteHeader } from "@/components/SiteHeader";
import { LoginModal } from "@/components/LoginModal";
import { Footer } from "@/components/sections/Footer";
import { PricingHero } from "@/components/sections/pricing/PricingHero";
import { PricingPlans } from "@/components/sections/pricing/PricingPlans";
import { PricingComparison } from "@/components/sections/pricing/PricingComparison";
import { PricingTestimonials } from "@/components/sections/pricing/PricingTestimonials";
import { PricingFAQ } from "@/components/sections/pricing/PricingFAQ";
import { PricingCTA } from "@/components/sections/pricing/PricingCTA";

export default function PricingPage() {
  const [loginOpen, setLoginOpen] = useState(false);

  return (
    <>
      <SiteHeader onLoginClick={() => setLoginOpen(true)} />

      <main id="main">
        {/* 1. Hero — value prop + metrics + trust badges */}
        <PricingHero onCta={() => setLoginOpen(true)} />

        {/* 2. Plans — 3 tiers with monthly/yearly toggle */}
        <PricingPlans onCta={() => setLoginOpen(true)} />

        {/* 3. Feature comparison table */}
        <PricingComparison />

        {/* 4. Social proof — testimonials before final CTA (skill recommendation) */}
        <PricingTestimonials />

        {/* 5. FAQ — address objections */}
        <PricingFAQ />

        {/* 6. Final CTA with trust badges */}
        <PricingCTA onCta={() => setLoginOpen(true)} />
      </main>

      <Footer />

      <LoginModal open={loginOpen} onClose={() => setLoginOpen(false)} />
    </>
  );
}
