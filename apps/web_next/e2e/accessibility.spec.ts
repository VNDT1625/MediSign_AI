/**
 * E2E: Accessibility — WCAG AA compliance across all 5 pages.
 *
 * Requirements: 2.1 → 2.18, 3.7
 *
 * Uses axe-core via @axe-core/playwright to scan each page for WCAG violations.
 * Also tests keyboard navigation and LoginModal focus trap behaviour.
 *
 * DEPENDENCY NOTE:
 *   @axe-core/playwright is NOT yet in package.json.
 *   Install it before running these tests:
 *
 *     npm install --save-dev @axe-core/playwright
 *
 *   (or: npm install --save-dev @axe-core/playwright@^4.10.1)
 *
 * Run:
 *   npx playwright test e2e/accessibility.spec.ts
 *   npm run e2e -- --grep "Accessibility"
 */

import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Open the LoginModal from the landing page.
 * Tries both an aria-label selector and a visible button text selector.
 */
async function openLoginModal(page: import("@playwright/test").Page) {
  // SiteHeader renders a "Đăng nhập" button when the user is anonymous.
  await page
    .getByRole("button", { name: "Đăng nhập", exact: true })
    .first()
    .click();
}

/**
 * Skip the LoginModal video intro and wait for the dialog to be interactive.
 */
async function skipVideoIntro(page: import("@playwright/test").Page) {
  const skipBtn = page.getByRole("button", { name: "Bỏ qua intro" });
  try {
    await skipBtn.waitFor({ state: "visible", timeout: 5_000 });
    await skipBtn.click();
  } catch {
    // Video already ended — form is already visible.
  }
  // Wait for the dialog to be fully rendered and interactive.
  await page.locator('[role="dialog"]').waitFor({ state: "visible", timeout: 10_000 });
}

// ---------------------------------------------------------------------------
// Accessibility test suite
// ---------------------------------------------------------------------------

test.describe("Accessibility — WCAG AA compliance", () => {
  // -------------------------------------------------------------------------
  // Page-level axe scans
  // -------------------------------------------------------------------------

  test("Home page has no accessibility violations", async ({ page }) => {
    await page.goto("/");
    // Wait for the page to be fully loaded before scanning.
    await page.waitForLoadState("networkidle");

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test("About page has no accessibility violations", async ({ page }) => {
    await page.goto("/about");
    await page.waitForLoadState("networkidle");

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test("Chat page has no accessibility violations", async ({ page }) => {
    await page.goto("/chat");
    await page.waitForLoadState("networkidle");

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();

    // Specifically verifies Level A fixes: heading hierarchy (A2) and
    // chat input label (A1) are no longer reported as violations.
    expect(results.violations).toEqual([]);
  });

  test("Download page has no accessibility violations", async ({ page }) => {
    await page.goto("/download");
    await page.waitForLoadState("networkidle");

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  // -------------------------------------------------------------------------
  // LoginModal — axe scan
  // -------------------------------------------------------------------------

  test("LoginModal has no accessibility violations", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Open the modal and wait for it to be visible.
    await openLoginModal(page);
    await page.locator('[role="dialog"]').waitFor({ state: "visible", timeout: 10_000 });

    // Scan only the dialog to avoid noise from the background page.
    const results = await new AxeBuilder({ page })
      .include('[role="dialog"]')
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  // -------------------------------------------------------------------------
  // LoginModal — keyboard navigation / focus trap
  // -------------------------------------------------------------------------

  test("LoginModal keyboard navigation — focus trap", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Open the modal.
    await openLoginModal(page);
    await page.locator('[role="dialog"]').waitFor({ state: "visible", timeout: 10_000 });

    // Skip the video intro so the form is interactive.
    await skipVideoIntro(page);

    // Tab 10 times and verify focus stays inside the dialog each time.
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press("Tab");

      const focusedInsideDialog = await page.evaluate(() => {
        const dialog = document.querySelector('[role="dialog"]');
        if (!dialog) return false;
        return dialog.contains(document.activeElement);
      });

      expect(focusedInsideDialog).toBe(true);
    }
  });

  test("LoginModal ESC closes modal and returns focus to trigger", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Focus the trigger button before opening the modal so we can verify
    // that focus is returned to it after the modal closes.
    const triggerBtn = page.getByRole("button", { name: "Đăng nhập", exact: true }).first();
    await triggerBtn.focus();

    // Open the modal.
    await triggerBtn.click();
    await page.locator('[role="dialog"]').waitFor({ state: "visible", timeout: 10_000 });

    // Skip the video intro.
    await skipVideoIntro(page);

    // Press ESC to close the modal.
    await page.keyboard.press("Escape");

    // The dialog should now be hidden (aria-hidden="true" or removed from DOM).
    // Wait for it to disappear.
    await page.locator('[role="dialog"][aria-hidden="true"]').waitFor({
      state: "visible",
      timeout: 5_000,
    });

    // Verify focus has returned to the trigger button.
    const triggerIsFocused = await page.evaluate(() => {
      const btn = document.querySelector(
        '[role="button"][aria-label*="Đăng nhập"], button',
      );
      // Check if the currently focused element is the "Đăng nhập" button.
      const active = document.activeElement;
      return active?.textContent?.trim() === "Đăng nhập" ||
        active?.getAttribute("aria-label")?.includes("Đăng nhập");
    });

    expect(triggerIsFocused).toBe(true);
  });
});
