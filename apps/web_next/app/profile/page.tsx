"use client";

import { useState } from "react";
import { SiteHeader } from "@/components/SiteHeader";
import { LoginModal } from "@/components/LoginModal";
import { Footer } from "@/components/sections/Footer";
import { ProfileHeader } from "@/components/profile/ProfileHeader";
import { ProfileCard } from "@/components/profile/ProfileCard";
import { ProfileStats } from "@/components/profile/ProfileStats";
import { ProfilePersonalInfo } from "@/components/profile/ProfilePersonalInfo";
import { ProfileJourney } from "@/components/profile/ProfileJourney";
import { ProfileSettings } from "@/components/profile/ProfileSettings";

export default function ProfilePage() {
  const [loginOpen, setLoginOpen] = useState(false);

  return (
    <>
      <SiteHeader onLoginClick={() => setLoginOpen(true)} />

      <main id="main" className="bg-ink-100/40 pt-24 pb-16 lg:pt-28 lg:pb-20">
        <div className="container-page">
          <ProfileHeader />

          <div className="grid gap-6 lg:grid-cols-12 lg:gap-7">
            {/* Cột chính 8/12 */}
            <div className="space-y-5 lg:col-span-8">
              <ProfileCard />
              <ProfileStats />
              <ProfilePersonalInfo />
              <ProfileJourney />

              <button
                type="button"
                className="flex w-full items-center justify-center gap-2 rounded-card border border-danger/40 bg-danger/5 px-6 py-3.5 text-base font-semibold text-danger hover:bg-danger/10 cursor-pointer"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path
                    d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                Đăng xuất
              </button>
            </div>

            {/* Sidebar 4/12 */}
            <div className="lg:col-span-4">
              <ProfileSettings />
            </div>
          </div>
        </div>
      </main>

      <Footer />

      <LoginModal open={loginOpen} onClose={() => setLoginOpen(false)} />
    </>
  );
}
