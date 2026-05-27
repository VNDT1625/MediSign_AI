/**
 * Bug Condition Exploration Test — Level AA Color Contrast
 *
 * **Validates: Requirements 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12, 1.13,
 *              1.14, 1.15, 1.16, 1.17, 1.18**
 *
 * CRITICAL: These tests are EXPECTED TO FAIL on unfixed code.
 * Failure confirms that contrast violations exist (isBugCondition_Contrast: ratio < 4.5).
 * DO NOT fix the code or the tests when they fail.
 *
 * Bug Condition Methodology:
 *   - Property 1 (Bug Condition): ratio < 4.5 → test asserts ≥ 4.5 → FAIL confirms bug
 *   - Each failing test surfaces a counterexample proving the violation exists
 */

import { describe, it, expect } from "vitest";

// ---------------------------------------------------------------------------
// WCAG Relative Luminance & Contrast Ratio helpers
// Spec: https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
// ---------------------------------------------------------------------------

/**
 * Convert a single 8-bit sRGB channel value (0–255) to its linear-light
 * contribution as defined by the WCAG 2.1 relative luminance formula.
 */
function linearize(channel8bit: number): number {
  const sRGB = channel8bit / 255;
  return sRGB <= 0.04045
    ? sRGB / 12.92
    : Math.pow((sRGB + 0.055) / 1.055, 2.4);
}

/**
 * Compute the WCAG 2.1 relative luminance of a hex color string.
 * Accepts 6-digit hex with or without leading '#'.
 */
function relativeLuminance(hex: string): number {
  const clean = hex.replace(/^#/, "");
  const r = parseInt(clean.slice(0, 2), 16);
  const g = parseInt(clean.slice(2, 4), 16);
  const b = parseInt(clean.slice(4, 6), 16);
  return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b);
}

/**
 * Compute the WCAG 2.1 contrast ratio between two hex colors.
 * Returns a value in the range [1, 21].
 *
 * isBugCondition_Contrast: contrastRatio(fg, bg) < 4.5
 */
export function contrastRatio(fg: string, bg: string): number {
  const L1 = relativeLuminance(fg);
  const L2 = relativeLuminance(bg);
  const lighter = Math.max(L1, L2);
  const darker = Math.min(L1, L2);
  return (lighter + 0.05) / (darker + 0.05);
}

// ---------------------------------------------------------------------------
// Bug Condition Exploration Tests
// ALL tests below MUST FAIL on unfixed code — failure confirms violations exist.
// ---------------------------------------------------------------------------

describe("Bug Condition — Color Contrast Failures (WCAG 1.4.3 Level AA)", () => {
  /**
   * Counterexample documentation format:
   *   actual ratio  vs  required ratio (4.5:1)
   *   component / usage context
   */

  it.fails("btn-primary: #0284C7 on #ffffff should be ≥ 4.5:1 [FAIL expected — actual: 4.10:1]", () => {
    // Counterexample: contrastRatio("#0284C7", "#ffffff") = 4.10 < 4.5
    // Component: .btn-primary (globals.css) — bg-brand (#0284C7) with white text
    // isBugCondition_Contrast: 4.10 < 4.5 → BUG CONFIRMED
    const ratio = contrastRatio("#0284C7", "#ffffff");
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });

  it.fails("cyan-600 button: #0891B2 on #ffffff should be ≥ 4.5:1 [FAIL expected — actual: 3.68:1]", () => {
    // Counterexample: contrastRatio("#0891B2", "#ffffff") = 3.68 < 4.5
    // Component: ChatSidebar "Cuộc trò chuyện mới" button (bg-cyan-600)
    // isBugCondition_Contrast: 3.68 < 4.5 → BUG CONFIRMED
    const ratio = contrastRatio("#0891B2", "#ffffff");
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });

  it.fails("badge-app: #F97316 on #FFEDD5 should be ≥ 4.5:1 [FAIL expected — actual: 2.45:1]", () => {
    // Counterexample: contrastRatio("#F97316", "#FFEDD5") = 2.45 < 4.5
    // Component: .badge-app (globals.css) — text-accent (#F97316) on bg-accent-soft (#FFEDD5)
    // isBugCondition_Contrast: 2.45 < 4.5 → BUG CONFIRMED
    const ratio = contrastRatio("#F97316", "#FFEDD5");
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });

  it.fails('"Hoàn thành" chip: #22C55E on #DCFCE7 should be ≥ 4.5:1 [FAIL expected — actual: 2.07:1]', () => {
    // Counterexample: contrastRatio("#22C55E", "#DCFCE7") = 2.07 < 4.5
    // Component: AboutMilestones STATUS_CHIP.done — text-success (#22C55E) on bg-success-soft (#DCFCE7)
    // isBugCondition_Contrast: 2.07 < 4.5 → BUG CONFIRMED
    const ratio = contrastRatio("#22C55E", "#DCFCE7");
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });

  it.fails('"Tất cả" badge: #22C55E on #DEF6E7 should be ≥ 4.5:1 [FAIL expected — actual: 2.00:1]', () => {
    // Counterexample: contrastRatio("#22C55E", "#DEF6E7") = 2.00 < 4.5
    // Component: Download/Login "Tất cả" badge — text-success (#22C55E) on #DEF6E7
    // isBugCondition_Contrast: 2.00 < 4.5 → BUG CONFIRMED
    const ratio = contrastRatio("#22C55E", "#DEF6E7");
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });

  it.fails('"Giảng viên hướng dẫn": #F97316 on #ffffff should be ≥ 4.5:1 [FAIL expected — actual: 2.80:1]', () => {
    // Counterexample: contrastRatio("#F97316", "#ffffff") = 2.80 < 4.5
    // Component: AboutTeam ACCENT.accent.text — text-accent (#F97316) on white background
    // isBugCondition_Contrast: 2.80 < 4.5 → BUG CONFIRMED
    const ratio = contrastRatio("#F97316", "#ffffff");
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });

  it.fails("tech tags: #22C55E on #ffffff should be ≥ 4.5:1 [FAIL expected — actual: 2.28:1]", () => {
    // Counterexample: contrastRatio("#22C55E", "#ffffff") = 2.28 < 4.5
    // Component: AboutTech / AboutTeam — text-success (#22C55E) on white background
    // isBugCondition_Contrast: 2.28 < 4.5 → BUG CONFIRMED
    const ratio = contrastRatio("#22C55E", "#ffffff");
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });

  it.fails('"Thiết kế cho mọi người": #F59E0B on #ffffff should be ≥ 4.5:1 [FAIL expected — actual: 2.15:1]', () => {
    // Counterexample: contrastRatio("#F59E0B", "#ffffff") = 2.15 < 4.5
    // Component: AboutTeam ACCENT.warn.text — text-warn (#F59E0B) on white background
    // isBugCondition_Contrast: 2.15 < 4.5 → BUG CONFIRMED
    const ratio = contrastRatio("#F59E0B", "#ffffff");
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });

  it.fails("timestamps/ink-400: #94A3B8 on #ffffff should be ≥ 4.5:1 [FAIL expected — actual: 2.56:1]", () => {
    // Counterexample: contrastRatio("#94A3B8", "#ffffff") = 2.56 < 4.5
    // Component: ChatMain AiBubble timestamp — text-ink-400 (#94A3B8) on white background
    // isBugCondition_Contrast: 2.56 < 4.5 → BUG CONFIRMED
    const ratio = contrastRatio("#94A3B8", "#ffffff");
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });

  it.fails("file attachment name: #ffffff on #2896CF should be ≥ 4.5:1 [FAIL expected — actual: 3.31:1]", () => {
    // Counterexample: contrastRatio("#ffffff", "#2896CF") = 3.31 < 4.5
    // Component: ChatMain ImageAttachmentPreview — white text on #2896CF (brand overlay)
    // isBugCondition_Contrast: 3.31 < 4.5 → BUG CONFIRMED
    const ratio = contrastRatio("#ffffff", "#2896CF");
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });
});
