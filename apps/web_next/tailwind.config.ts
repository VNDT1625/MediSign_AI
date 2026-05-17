import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        // Theo MediSign_AI_UI_Web_Final.md mục 10 — Color Design
        brand: {
          DEFAULT: "#0284C7", // Xanh biển chủ đạo
          50: "#F0F9FF",
          100: "#E0F2FE",
          500: "#0EA5E9",
          600: "#0284C7",
          700: "#0369A1",
          900: "#0C4A6E"
        },
        accent: {
          DEFAULT: "#F97316", // Cam accent chính
          soft: "#FFEDD5"
        },
        success: { DEFAULT: "#22C55E", soft: "#DCFCE7" },
        warn: { DEFAULT: "#F59E0B", soft: "#FEF3C7" },
        danger: { DEFAULT: "#DC2626", soft: "#FEE2E2" },
        ink: {
          900: "#0F172A",
          800: "#1E293B",
          600: "#475569",
          500: "#64748B",
          400: "#94A3B8",
          200: "#E2E8F0",
          100: "#F1F5F9"
        }
      },
      fontFamily: {
        sans: ["var(--font-inter)", "Segoe UI", "Roboto", "Helvetica Neue", "sans-serif"]
      },
      fontSize: {
        // Spec mục 11
        hero: ["clamp(40px, 6vw, 64px)", { lineHeight: "1.1", fontWeight: "700" }],
        h1: ["clamp(32px, 4vw, 40px)", { lineHeight: "1.2", fontWeight: "700" }],
        h2: ["clamp(24px, 3vw, 32px)", { lineHeight: "1.3", fontWeight: "600" }],
        h3: ["22px", { lineHeight: "1.4", fontWeight: "600" }],
        body: ["18px", { lineHeight: "1.6" }],
        caption: ["15px", { lineHeight: "1.5" }]
      },
      borderRadius: {
        card: "12px",
        modal: "16px",
        pill: "9999px"
      },
      boxShadow: {
        soft: "0 1px 3px rgba(0,0,0,0.08)",
        card: "0 6px 24px -8px rgba(15,23,42,0.18)",
        focus: "0 0 0 3px rgba(2,132,199,0.25)"
      },
      maxWidth: {
        page: "1280px"
      },
      animation: {
        "fade-up": "fadeUp 400ms cubic-bezier(0.4,0,0.2,1) both",
        "fade-in": "fadeIn 500ms ease-out both",
        "scale-in": "scaleIn 500ms cubic-bezier(0.34,1.56,0.64,1) both",
        "pulse-soft": "pulseSoft 2.4s ease-in-out infinite",
        "float-slow": "float 6s ease-in-out infinite",
        "float-mid": "float 4.5s ease-in-out infinite",
        "float-fast": "float 3.5s ease-in-out infinite",
        "blob": "blob 14s ease-in-out infinite",
        "spin-slow": "spin 22s linear infinite",
        "shimmer": "shimmer 2.4s linear infinite",
        "draw-line": "drawLine 1200ms cubic-bezier(0.4,0,0.2,1) forwards"
      },
      keyframes: {
        fadeUp: {
          from: { opacity: "0", transform: "translateY(12px)" },
          to: { opacity: "1", transform: "translateY(0)" }
        },
        fadeIn: {
          from: { opacity: "0" },
          to: { opacity: "1" }
        },
        scaleIn: {
          from: { opacity: "0", transform: "scale(0.85)" },
          to: { opacity: "1", transform: "scale(1)" }
        },
        pulseSoft: {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" }
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-8px)" }
        },
        blob: {
          "0%, 100%": { transform: "translate(0,0) scale(1)" },
          "33%": { transform: "translate(20px,-18px) scale(1.05)" },
          "66%": { transform: "translate(-16px,12px) scale(0.97)" }
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" }
        },
        drawLine: {
          from: { strokeDashoffset: "1000" },
          to: { strokeDashoffset: "0" }
        }
      }
    }
  },
  plugins: []
};

export default config;
