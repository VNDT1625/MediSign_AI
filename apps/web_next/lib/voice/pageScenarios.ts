/**
 * pageScenarios — Registry cac section theo trang de voice command "cuon xuong"
 * cuon toi section tiep theo thay vi scroll 80% viewport.
 *
 * Moi entry: pathname -> danh sach section IDs (thu tu xuat hien tu tren xuong duoi).
 */

export const PAGE_SECTIONS: Record<string, string[]> = {
  "/": [
    "benefits",       // WhyChooseSection
    "how-it-works",   // HowItWorksSection
    "multi-platform", // MultiPlatformSection
    "app-features",   // AppOnlyFeaturesSection
    "pricing",        // PricingSection
    "testimonials",   // TestimonialsSection
    "cta",            // CTABanner
  ],
  "/pricing": [
    "plans",
    "comparison",
    "faq",
    "testimonials",
    "cta",
  ],
  "/about": [
    "mission",
    "modules",
    "tech",
    "team",
    "values",
    "story",
    "contact",
  ],
};

/** Section name mapping: ten tieng Viet (da bo dau) -> section ID. */
export const SECTION_NAMES: Record<string, string> = {
  "loi ich": "benefits",
  "tai sao chon": "benefits",
  "cach hoat dong": "how-it-works",
  "da nen tang": "multi-platform",
  "tinh nang app": "app-features",
  "bang gia": "pricing",
  "gia ca": "pricing",
  "danh gia": "testimonials",
  "y kien": "testimonials",
  "lien he": "contact",
  "su menh": "mission",
  "module": "modules",
  "cong nghe": "tech",
  "doi ngu": "team",
  "gia tri": "values",
  "cau chuyen": "story",
  "goi dich vu": "plans",
  "so sanh": "comparison",
  "cau hoi": "faq",
};

/**
 * Tim section ID hien tai dang hien o gan viewport nhat.
 * Tra ve index trong mang sections cua trang.
 */
function getCurrentSectionIndex(sections: string[]): number {
  if (typeof window === "undefined") return -1;
  const viewportMiddle = window.scrollY + window.innerHeight / 3;

  let best = -1;
  let bestDist = Infinity;

  for (let i = 0; i < sections.length; i++) {
    const el = document.getElementById(sections[i]);
    if (!el) continue;
    const top = el.getBoundingClientRect().top + window.scrollY;
    const dist = Math.abs(top - viewportMiddle);
    if (dist < bestDist) {
      bestDist = dist;
      best = i;
    }
  }
  return best;
}

/**
 * Cuon toi section tiep theo tren trang hien tai.
 * Tra ve ten section da cuon toi, hoac null neu khong co.
 */
export function scrollToNextSection(): string | null {
  if (typeof window === "undefined") return null;
  const pathname = window.location.pathname;
  const sections = PAGE_SECTIONS[pathname];
  if (!sections?.length) return null;

  const currentIdx = getCurrentSectionIndex(sections);
  const nextIdx = currentIdx + 1;

  if (nextIdx >= sections.length) {
    // Da o section cuoi -> cuon xuong cuoi trang
    window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
    return "cuối trang";
  }

  const el = document.getElementById(sections[nextIdx]);
  if (!el) return null;
  el.scrollIntoView({ behavior: "smooth", block: "start" });
  return sections[nextIdx];
}

/**
 * Cuon toi section truoc do tren trang hien tai.
 */
export function scrollToPrevSection(): string | null {
  if (typeof window === "undefined") return null;
  const pathname = window.location.pathname;
  const sections = PAGE_SECTIONS[pathname];
  if (!sections?.length) return null;

  const currentIdx = getCurrentSectionIndex(sections);
  const prevIdx = currentIdx - 1;

  if (prevIdx < 0) {
    window.scrollTo({ top: 0, behavior: "smooth" });
    return "đầu trang";
  }

  const el = document.getElementById(sections[prevIdx]);
  if (!el) return null;
  el.scrollIntoView({ behavior: "smooth", block: "start" });
  return sections[prevIdx];
}

/**
 * Cuon toi 1 section cu the theo ID.
 */
export function scrollToSection(sectionId: string): boolean {
  if (typeof document === "undefined") return false;
  const el = document.getElementById(sectionId);
  if (!el) return false;
  el.scrollIntoView({ behavior: "smooth", block: "start" });
  return true;
}
