/**
 * E2E: Register → auto-login → /app
 *
 * Requirements: 2.1.1, 2.1.4
 *
 * Flow:
 *   1. Navigate to `/`
 *   2. Click "Tạo tài khoản" in the SiteHeader to open LoginModal
 *   3. The modal opens in "login" mode by default; switch to "Đăng ký" tab
 *   4. Fill in the 3-step RegisterForm with a unique email/phone
 *   5. Submit → backend creates account → auto-login chains in
 *   6. Verify redirect to /app (or /app/chat)
 *   7. Verify AvatarMenu is visible (authenticated state)
 */

import { test, expect } from "./fixtures";

/**
 * Generate a unique suffix based on the current timestamp so each test
 * run registers a fresh account and avoids 409 conflicts.
 */
function uniqueSuffix(): string {
  return Date.now().toString(36);
}

test.describe("Register → auto-login → /app", () => {
  test("registers a new user, auto-logs in, and lands on /app", async ({
    page,
  }) => {
    const suffix = uniqueSuffix();
    const newUser = {
      full_name: `Test User ${suffix}`,
      username: `testuser_${suffix}`,
      email: `test_${suffix}@medisign.local`,
      phone: `09${suffix.slice(-8).padStart(8, "0")}`,
      password: "E2eTest@123",
    };

    // ── Step 1: Navigate to the landing page ──────────────────────────────
    await page.goto("/");

    // Wait for the page to be interactive (SiteHeader hydrated)
    await page.waitForLoadState("networkidle");

    // ── Step 2: Open LoginModal via "Tạo tài khoản" CTA ──────────────────
    // The SiteHeader renders "Tạo tài khoản" for anonymous users.
    // On desktop it's in the right rail; on mobile it's in the drawer.
    // We target the desktop button (visible at default viewport).
    const createAccountBtn = page
      .getByRole("button", { name: "Tạo tài khoản" })
      .first();
    await createAccountBtn.click();

    // The LoginModal fades in after the intro video ends (or can be skipped).
    // Wait for the "Bỏ qua intro" button and click it to skip the video.
    const skipBtn = page.getByRole("button", { name: "Bỏ qua intro" });
    if (await skipBtn.isVisible()) {
      await skipBtn.click();
    }

    // Wait for the form surface to appear (opacity transition after video)
    await page.waitForSelector('[role="dialog"]', { state: "visible" });

    // ── Step 3: Switch to the "Đăng ký" (Register) tab ───────────────────
    // The modal opens in "login" mode by default; click the register tab.
    const registerTab = page.getByRole("button", { name: "Đăng ký" });
    await registerTab.click();

    // Confirm we're on the register form (step indicator should be visible)
    await expect(page.getByText("Bước 1 · Thông tin cá nhân")).toBeVisible();

    // ── Step 4a: Fill Step 1 — full_name + username ───────────────────────
    await page.getByLabel("Họ và tên").fill(newUser.full_name);
    await page.getByLabel("Tên đăng nhập").fill(newUser.username);

    // Click "Tiếp theo" to advance to step 2
    await page.getByRole("button", { name: "Tiếp theo" }).click();

    // ── Step 4b: Fill Step 2 — email + phone ─────────────────────────────
    await expect(page.getByText("Bước 2 · Thông tin liên hệ")).toBeVisible();

    await page.getByLabel("Email").fill(newUser.email);
    await page.getByLabel("Số điện thoại").fill(newUser.phone);

    await page.getByRole("button", { name: "Tiếp theo" }).click();

    // ── Step 4c: Fill Step 3 — password + terms ───────────────────────────
    await expect(page.getByText("Bước 3 · Đặt mật khẩu")).toBeVisible();

    await page.getByLabel("Mật khẩu").fill(newUser.password);

    // Accept terms checkbox
    await page.getByLabel(/Tôi đồng ý với/).check();

    // ── Step 5: Submit the registration form ─────────────────────────────
    await page.getByRole("button", { name: "Tạo tài khoản" }).click();

    // ── Step 6: Verify redirect to /app ──────────────────────────────────
    // After register → auto-login, the intent was "home" (set by the
    // SiteHeader CTA), so consume() returns /app.
    await page.waitForURL(/\/app(\/|$)/, { timeout: 15_000 });

    const currentUrl = page.url();
    expect(currentUrl).toMatch(/\/app(\/|$)/);

    // ── Step 7: Verify AvatarMenu is visible (authenticated state) ────────
    // AvatarMenu renders a button with aria-label="Tài khoản của {full_name}"
    // when the user is authenticated. We use a partial match since the
    // full_name includes the timestamp suffix.
    const avatarMenuBtn = page.getByRole("button", {
      name: /Tài khoản của/,
    });
    await expect(avatarMenuBtn).toBeVisible({ timeout: 10_000 });
  });
});
