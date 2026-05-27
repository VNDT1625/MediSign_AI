"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { SiteHeader } from "@/components/SiteHeader";
import { LoginModal } from "@/components/LoginModal";
import { Footer } from "@/components/sections/Footer";
import { ProfileHeader } from "@/components/profile/ProfileHeader";
import { ProfileCard } from "@/components/profile/ProfileCard";
import { ProfileStats } from "@/components/profile/ProfileStats";
import { ProfilePersonalInfo } from "@/components/profile/ProfilePersonalInfo";
import { ProfileJourney } from "@/components/profile/ProfileJourney";
import { ProfileSettings } from "@/components/profile/ProfileSettings";
import { ChangePasswordCard } from "@/components/profile/ChangePasswordCard";
import { useAuth } from "@/lib/auth/useAuth";

export default function ProfilePage() {
  const [loginOpen, setLoginOpen] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const { state, logout } = useAuth();
  const router = useRouter();

  async function handleLogout() {
    if (isLoggingOut) return;
    setIsLoggingOut(true);
    try {
      await logout();
    } catch {
      // Logout là best-effort: kể cả khi server lỗi vẫn quay về public site.
    } finally {
      router.push("/");
    }
  }

  return (
    <>
      <SiteHeader onLoginClick={() => setLoginOpen(true)} />

      <main id="main" className="bg-ink-100/40 pt-20 pb-12 sm:pt-24 sm:pb-16 lg:pt-28 lg:pb-20">
        <div className="container-page">
          <ProfileHeader />

          <div className="grid gap-6 lg:grid-cols-12 lg:gap-7">
            {/* Cột chính 8/12 */}
            <div className="space-y-5 lg:col-span-8">
              <ProfileCard />
              <ProfileStats />
              <ProfilePersonalInfo />
              <ChangePasswordCard />
              <ProfileJourney />

              <button
                type="button"
                onClick={handleLogout}
                disabled={
                  isLoggingOut || state.status !== "authenticated"
                }
                aria-busy={isLoggingOut ? "true" : "false"}
                className="flex w-full items-center justify-center gap-2 rounded-card border border-danger/40 bg-danger/5 px-6 py-3.5 text-base font-semibold text-danger hover:bg-danger/10 cursor-pointer disabled:cursor-not-allowed disabled:opacity-60"
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
                {isLoggingOut ? "Đang đăng xuất..." : "Đăng xuất"}
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
