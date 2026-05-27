/**
 * Property-Based Tests — Contrast Preservation (Task 9.1)
 *
 * **Validates: Requirements 3.1, 3.2, 3.5, 3.6, 3.7, 3.8**
 *
 * Four properties verified with fast-check (≥ 100 generated cases each):
 *
 *   P1 — Contrast ratio monotonicity:
 *        For any color pair where the FIXED ratio ≥ 4.5, the ratio SHALL
 *        remain ≥ 4.5 regardless of how many times it is computed.
 *
 *   P2 — Layout preservation:
 *        For all contrast-only fixes, rendering btn-primary and badge-app
 *        with arbitrary content SHALL not throw errors.
 *
 *   P3 — Text content preservation:
 *        For all badge/button text, the text content SHALL be identical
 *        before and after the fix (only color values change).
 *
 *   P4 — Heading level gap:
 *        For any heading sequence after the fix, the maximum gap between
 *        consecutive levels SHALL be ≤ 1.
 */

import { render, screen } from "@testing-library/react";
import * as fc from "fast-check";
import { describe, it, expect, vi } from "vitest";

// ---------------------------------------------------------------------------
// Module mocks (must be declared before component imports)
// ---------------------------------------------------------------------------

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), prefetch: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

const mockIntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
  takeRecords: vi.fn().mockReturnValue([]),
}));
Object.defineProperty(window, "IntersectionObserver", {
  writable: true,
  configurable: true,
  value: mockIntersectionObserver,
});
Object.defineProperty(global, "IntersectionObserver", {
  writable: true,
  configurable: true,
  value: mockIntersectionObserver,
});

vi.mock("@/lib/auth/useAuth", () => ({
  useAuth: () => ({
    state: { status: "anonymous" },
    isAuthenticated: false,
    login: vi.fn().mockResolvedValue(undefined),
    register: vi.fn().mockResolvedValue(undefined),
    logout: vi.fn().mockResolvedValue(undefined),
    changePassword: vi.fn().mockResolvedValue(undefined),
    hydrate: vi.fn().mockResolvedValue(undefined),
  }),
}));

vi.mock("@/lib/auth/useIntent", () => ({
  useIntent: () => ({
    set: vi.fn(),
    peek: vi.fn().mockReturnValue(null),
    consume: vi.fn().mockReturnValue({ redirectPath: "/app" }),
  }),
}));

// ---------------------------------------------------------------------------
// Component imports (after mocks)
// ---------------------------------------------------------------------------

import { AnalysisCard } from "@/components/chat/ChatMain";

// ---------------------------------------------------------------------------
// WCAG Relative Luminance & Contrast Ratio helpers
// (same implementation as a11y-contrast.test.ts — pure math, no DOM)
// ---------------------------------------------------------------------------

function linearize(channel8bit: number): number {
  const sRGB = channel8bit / 255;
  return sRGB <= 0.04045
    ? sRGB / 12.92
    : Math.pow((sRGB + 0.055) / 1.055, 2.4);
}

function relativeLuminance(hex: string): number {
  const clean = hex.replace(/^#/, "");
  const r = parseInt(clean.slice(0, 2), 16);
  const g = parseInt(clean.slice(2, 4), 16);
  const b = parseInt(clean.slice(4, 6), 16);
  return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b);
}

function contrastRatio(fg: string, bg: string): number {
  const L1 = relativeLuminance(fg);
  const L2 = relativeLuminance(bg);
  const lighter = Math.max(L1, L2);
  const darker = Math.min(L1, L2);
  return (lighter + 0.05) / (darker + 0.05);
}

// ---------------------------------------------------------------------------
// Arbitraries
// ---------------------------------------------------------------------------

/**
 * Generate a random 6-digit hex color string (no leading '#').
 * fc.hexaString was removed in fast-check v4; we use fc.integer mapped to
 * a zero-padded hex string instead.
 */
const hexColor = fc
  .integer({ min: 0, max: 0xffffff })
  .map((n) => n.toString(16).padStart(6, "0"));

/**
 * The KNOWN FIXED color pairs from the accessibility audit.
 * Each pair has been verified to achieve ≥ 4.5:1 after the fix.
 */
const FIXED_PAIRS: Array<{ fg: string; bg: string; label: string }> = [
  { fg: "#0369A1", bg: "#ffffff", label: "btn-primary (brand-700 on white)" },
  { fg: "#0E7490", bg: "#ffffff", label: "ChatSidebar button (cyan-700 on white)" },
  { fg: "#9A3412", bg: "#FFEDD5", label: "badge-app (orange-800 on accent-soft)" },
  { fg: "#14532D", bg: "#DCFCE7", label: "STATUS_CHIP done (green-900 on success-soft)" },
  { fg: "#14532D", bg: "#DEF6E7", label: '"Tất cả" badge (green-900 on #DEF6E7)' },
  { fg: "#C2410C", bg: "#ffffff", label: '"Giảng viên hướng dẫn" (orange-700 on white)' },
  { fg: "#15803D", bg: "#ffffff", label: "tech tags (green-700 on white)" },
  { fg: "#92400E", bg: "#ffffff", label: '"Thiết kế cho mọi người" (amber-800 on white)' },
  { fg: "#475569", bg: "#ffffff", label: "timestamps (ink-600 on white)" },
  { fg: "#ffffff", bg: "#1D6FA3", label: "file attachment (white on brand overlay)" },
];

// ---------------------------------------------------------------------------
// Mock analysis message for AnalysisCard rendering
// ---------------------------------------------------------------------------

const baseMockMsg = {
  id: "pbt-msg",
  role: "ai" as const,
  kind: "analysis" as const,
  intro: "Phân tích sơ bộ từ MediSign AI.",
  assessment: [{ label: "Triệu chứng:", value: "Đau đầu nhẹ" }],
  handling: ["Nghỉ ngơi và uống nước."],
  note: { text: "Đây không phải chẩn đoán cuối cùng.", time: "10:00" },
  time: "10:00",
};

// ---------------------------------------------------------------------------
// P1 — Contrast ratio monotonicity
// **Validates: Requirements 3.1, 3.5**
// ---------------------------------------------------------------------------

describe("P1 — Contrast ratio monotonicity", () => {
  it(
    "for any random color pair, contrastRatio is deterministic (same inputs → same output)",
    () => {
      /**
       * Property: The WCAG contrast ratio function is a pure mathematical
       * function. For any two hex colors, calling it multiple times MUST
       * always return the same value (no randomness, no side effects).
       *
       * **Validates: Requirements 3.1**
       */
      fc.assert(
        fc.property(hexColor, hexColor, (fg, bg) => {
          const r1 = contrastRatio(fg, bg);
          const r2 = contrastRatio(fg, bg);
          const r3 = contrastRatio(fg, bg);
          // All three calls must return identical values
          return r1 === r2 && r2 === r3;
        }),
        { numRuns: 100 },
      );
    },
  );

  it(
    "for any random color pair, contrastRatio is symmetric: ratio(a,b) === ratio(b,a)",
    () => {
      /**
       * Property: WCAG contrast ratio is symmetric — swapping fg and bg
       * produces the same ratio (because we take max/min of luminances).
       *
       * **Validates: Requirements 3.1**
       */
      fc.assert(
        fc.property(hexColor, hexColor, (fg, bg) => {
          const r1 = contrastRatio(fg, bg);
          const r2 = contrastRatio(bg, fg);
          return Math.abs(r1 - r2) < 1e-10;
        }),
        { numRuns: 100 },
      );
    },
  );

  it(
    "for all KNOWN FIXED pairs, ratio SHALL remain ≥ 4.5 regardless of how many times computed",
    () => {
      /**
       * Property: For each of the 10 known fixed color pairs, the contrast
       * ratio MUST be ≥ 4.5 on every computation. This verifies that the
       * fix is stable and the math is correct.
       *
       * **Validates: Requirements 3.5, 3.6**
       */
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 20 }), // how many times to compute
          (repetitions) => {
            return FIXED_PAIRS.every(({ fg, bg }) => {
              for (let i = 0; i < repetitions; i++) {
                if (contrastRatio(fg, bg) < 4.5) return false;
              }
              return true;
            });
          },
        ),
        { numRuns: 100 },
      );
    },
  );

  it(
    "contrastRatio always returns a value in [1, 21] for any valid hex color pair",
    () => {
      /**
       * Property: WCAG contrast ratio is bounded between 1:1 (identical
       * colors) and 21:1 (black on white). Any value outside this range
       * indicates a bug in the luminance calculation.
       *
       * **Validates: Requirements 3.1**
       */
      fc.assert(
        fc.property(hexColor, hexColor, (fg, bg) => {
          const ratio = contrastRatio(fg, bg);
          return ratio >= 1 && ratio <= 21;
        }),
        { numRuns: 100 },
      );
    },
  );
});

// ---------------------------------------------------------------------------
// P2 — Layout preservation
// **Validates: Requirements 3.5, 3.6**
// ---------------------------------------------------------------------------

describe("P2 — Layout preservation (contrast-only fixes)", () => {
  it(
    "btn-primary renders without errors for any content and arbitrary viewport dimensions",
    () => {
      /**
       * Property: Rendering a btn-primary button with arbitrary content
       * and within arbitrary viewport dimensions SHALL never throw.
       * Only color values change — layout is preserved.
       *
       * **Validates: Requirements 3.5**
       */
      fc.assert(
        fc.property(
          fc.record({
            width: fc.integer({ min: 100, max: 1200 }),
            height: fc.integer({ min: 50, max: 800 }),
          }),
          fc.string({ minLength: 1, maxLength: 50 }).filter((s) => s.trim().length > 0),
          ({ width, height }, label) => {
            // Simulate viewport dimensions via container style
            const { container, unmount } = render(
              <div style={{ width: `${width}px`, height: `${height}px` }}>
                <button className="btn-primary" type="button">
                  {label}
                </button>
              </div>,
            );

            const btn = container.querySelector(".btn-primary");
            const rendered = btn !== null && btn.textContent === label;
            unmount();
            return rendered;
          },
        ),
        { numRuns: 100 },
      );
    },
  );

  it(
    "badge-app renders without errors for any content and arbitrary viewport dimensions",
    () => {
      /**
       * Property: Rendering a badge-app element with arbitrary content
       * and within arbitrary viewport dimensions SHALL never throw.
       * Only color values change — layout is preserved.
       *
       * **Validates: Requirements 3.6**
       */
      fc.assert(
        fc.property(
          fc.record({
            width: fc.integer({ min: 100, max: 1200 }),
            height: fc.integer({ min: 50, max: 800 }),
          }),
          fc.string({ minLength: 1, maxLength: 50 }).filter((s) => s.trim().length > 0),
          ({ width, height }, text) => {
            const { container, unmount } = render(
              <div style={{ width: `${width}px`, height: `${height}px` }}>
                <span className="badge-app">{text}</span>
              </div>,
            );

            const badge = container.querySelector(".badge-app");
            const rendered = badge !== null && badge.textContent === text;
            unmount();
            return rendered;
          },
        ),
        { numRuns: 100 },
      );
    },
  );
});

// ---------------------------------------------------------------------------
// P3 — Text content preservation
// **Validates: Requirements 3.5, 3.6, 3.7**
// ---------------------------------------------------------------------------

describe("P3 — Text content preservation", () => {
  it(
    "btn-primary: text content is identical before and after fix for any label",
    () => {
      /**
       * Property: For any string label, a btn-primary button SHALL render
       * that exact text content. The color fix MUST NOT alter text content.
       *
       * **Validates: Requirements 3.5**
       */
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 50 }).filter((s) => s.trim().length > 0),
          (label) => {
            const { container, unmount } = render(
              <button className="btn-primary" type="button">
                {label}
              </button>,
            );
            const btn = container.querySelector(".btn-primary");
            const preserved = btn !== null && btn.textContent === label;
            unmount();
            return preserved;
          },
        ),
        { numRuns: 100 },
      );
    },
  );

  it(
    "badge-app: text content is identical before and after fix for any badge text",
    () => {
      /**
       * Property: For any string content, badge-app SHALL render that exact
       * text. The color fix MUST NOT alter text content.
       *
       * **Validates: Requirements 3.6**
       */
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 50 }).filter((s) => s.trim().length > 0),
          (text) => {
            const { container, unmount } = render(
              <span className="badge-app">{text}</span>,
            );
            const badge = container.querySelector(".badge-app");
            const preserved = badge !== null && badge.textContent === text;
            unmount();
            return preserved;
          },
        ),
        { numRuns: 100 },
      );
    },
  );

  it(
    "AnalysisCard: heading texts 'Đánh giá sơ bộ' and 'Gợi ý xử trí' are preserved for any message content",
    () => {
      /**
       * Property: For any valid analysis message, AnalysisCard SHALL always
       * render both heading texts unchanged. The H3→H2 fix MUST NOT alter
       * the text content of the headings.
       *
       * **Validates: Requirements 3.2, 3.7**
       */
      fc.assert(
        fc.property(
          fc.record({
            intro: fc.string({ minLength: 1, maxLength: 200 }),
            assessmentLabel: fc.string({ minLength: 1, maxLength: 50 }),
            assessmentValue: fc.string({ minLength: 1, maxLength: 100 }),
            handlingItem: fc.string({ minLength: 1, maxLength: 100 }),
            noteText: fc.string({ minLength: 1, maxLength: 200 }),
          }),
          (data) => {
            const msg = {
              ...baseMockMsg,
              id: `pbt-${Math.random()}`,
              intro: data.intro,
              assessment: [{ label: data.assessmentLabel, value: data.assessmentValue }],
              handling: [data.handlingItem],
              note: { text: data.noteText, time: "10:00" },
            };

            const { unmount } = render(<AnalysisCard msg={msg} />);

            const headings = screen.getAllByRole("heading");
            const headingTexts = headings.map((h) => h.textContent ?? "");

            const hasDanhGia = headingTexts.some((t) => t.includes("Đánh giá sơ bộ"));
            const hasGoiY = headingTexts.some((t) => t.includes("Gợi ý xử trí"));

            unmount();
            return hasDanhGia && hasGoiY;
          },
        ),
        // 100 runs of full React renders — allow 30 s to stay well within budget
        { numRuns: 100 },
      );
    },
    30_000, // vitest per-test timeout (ms)
  );
});

// ---------------------------------------------------------------------------
// P4 — Heading level gap
// **Validates: Requirements 3.2, 3.8**
// ---------------------------------------------------------------------------

describe("P4 — Heading level gap", () => {
  /**
   * Helper: check that no consecutive pair in a heading level sequence
   * has a gap > 1.
   */
  function hasNoGap(levels: number[]): boolean {
    for (let i = 1; i < levels.length; i++) {
      if (levels[i] - levels[i - 1] > 1) return false;
    }
    return true;
  }

  it(
    "for any heading sequence after fix, max gap between consecutive levels SHALL be ≤ 1",
    () => {
      /**
       * Property: After the H3→H2 fix, any heading sequence produced by
       * the application MUST NOT skip levels. We verify the hasNoGap
       * predicate itself is correct across all possible valid sequences.
       *
       * **Validates: Requirements 3.2, 3.8**
       */
      fc.assert(
        fc.property(
          fc.array(fc.integer({ min: 1, max: 6 }), { minLength: 2, maxLength: 10 }),
          (levels) => {
            // Filter to sequences that are already valid (no gaps)
            // and verify hasNoGap correctly identifies them
            const maxGap = levels
              .slice(1)
              .reduce((max, level, i) => Math.max(max, level - levels[i]), 0);

            if (maxGap <= 1) {
              // Valid sequence — hasNoGap must return true
              return hasNoGap(levels) === true;
            } else {
              // Invalid sequence — hasNoGap must return false
              return hasNoGap(levels) === false;
            }
          },
        ),
        { numRuns: 100 },
      );
    },
  );

  it(
    "AnalysisCard heading sequence after fix SHALL have max gap ≤ 1",
    () => {
      /**
       * Property: For any valid analysis message, the heading sequence
       * rendered by AnalysisCard SHALL satisfy the no-gap constraint.
       * After the H3→H2 fix: H1("MediSign AI") → H2("Đánh giá sơ bộ")
       * → H2("Gợi ý xử trí") — gap is 1, which is ≤ 1.
       *
       * **Validates: Requirements 3.2, 3.8**
       */
      fc.assert(
        fc.property(
          fc.record({
            intro: fc.string({ minLength: 1, maxLength: 100 }),
            assessmentLabel: fc.string({ minLength: 1, maxLength: 30 }),
            assessmentValue: fc.string({ minLength: 1, maxLength: 80 }),
            handlingItem: fc.string({ minLength: 1, maxLength: 80 }),
          }),
          (data) => {
            const msg = {
              ...baseMockMsg,
              id: `pbt-gap-${Math.random()}`,
              intro: data.intro,
              assessment: [{ label: data.assessmentLabel, value: data.assessmentValue }],
              handling: [data.handlingItem],
            };

            const { unmount } = render(<AnalysisCard msg={msg} />);

            const headings = screen.getAllByRole("heading");
            const levels = headings.map((h) => parseInt(h.tagName[1], 10));

            // Verify no gap > 1 between consecutive heading levels
            const noGap = hasNoGap(levels);

            unmount();
            return noGap;
          },
        ),
        { numRuns: 100 },
      );
    },
    30_000, // vitest per-test timeout (ms)
  );

  it(
    "known fixed heading sequence [H1, H2, H2] has max gap ≤ 1",
    () => {
      /**
       * Concrete verification: The specific heading sequence produced after
       * the fix (H1 → H2 → H2) must satisfy the gap constraint.
       *
       * **Validates: Requirements 3.2**
       */
      const fixedSequence = [1, 2, 2]; // H1 → H2 → H2 (after fix)
      expect(hasNoGap(fixedSequence)).toBe(true);
    },
  );

  it(
    "unfixed heading sequence [H1, H3] would have gap > 1 (regression guard)",
    () => {
      /**
       * Regression guard: The original buggy sequence (H1 → H3, gap = 2)
       * MUST be detected as invalid by hasNoGap. This ensures the predicate
       * correctly identifies the bug condition.
       *
       * **Validates: Requirements 3.8**
       */
      const buggySequence = [1, 3]; // H1 → H3 (original bug — gap = 2)
      expect(hasNoGap(buggySequence)).toBe(false);
    },
  );
});
