"use client";

import { useState } from "react";
import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { LoginModal } from "@/components/LoginModal";
import { Footer } from "@/components/sections/Footer";
import { PageHero } from "@/components/sections/PageHero";
import { AboutMission } from "@/components/sections/AboutMission";
import { AboutModules } from "@/components/sections/AboutModules";
import { AboutValues } from "@/components/sections/AboutValues";
import { AboutTech } from "@/components/sections/AboutTech";
import { AboutMilestones } from "@/components/sections/AboutMilestones";
import { AboutTeam } from "@/components/sections/AboutTeam";
import { ContactForm } from "@/components/sections/ContactForm";
import { AboutHeroVisual } from "@/components/sections/AboutHeroVisual";

export default function AboutPage() {
  const [loginOpen, setLoginOpen] = useState(false);

  return (
    <>
      <SiteHeader onLoginClick={() => setLoginOpen(true)} />

      <main id="main">
        <PageHero
          eyebrow="Về MediSign AI"
          title={
            <>
              Bác sĩ AI cho người Việt,
              <br />
              <span className="text-brand">làm bằng tay người Việt</span>
            </>
          }
          description={
            <p>
              MediSign sinh ra từ một câu hỏi đơn giản: làm sao để mẹ ở quê có thể
              hỏi một bác sĩ bất cứ lúc nào, bằng tiếng mẹ đẻ, mà không phải chờ
              đợi hay đi xa? Câu trả lời của chúng tôi là một bác sĩ AI thân thiện
              — luôn sẵn sàng và hiểu bạn.
            </p>
          }
          cta={
            <>
              <Link href="#mission" className="btn-primary">
                Sứ mệnh của chúng tôi
              </Link>
              <Link href="#team" className="btn-outline">
                Gặp đội ngũ
              </Link>
            </>
          }
          visual={<AboutHeroVisual />}
        />

        <AboutMission />
        <AboutModules />
        <AboutValues />
        <AboutTech />
        <AboutMilestones />
        <AboutTeam />
        <ContactForm />
      </main>

      <Footer />

      <LoginModal open={loginOpen} onClose={() => setLoginOpen(false)} />
    </>
  );
}
