/**
 * E2E: Login (email + phone) and Logout flows.
 *
 * Requirements: 2.1.2 (login with email or phone), 2.1.5 (logout)
 *
 * Each test:
 *  1. Navigates to `/`
 *  2. Opens the LoginModal via the "Đăng nhập" button in SiteHeader
 *  3. Skips the video intro so the form surface becomes interactive
 *  4. Fills in credentials and submits
 *  5. Verifies the authenticated state (redirect to /app, AvatarMenu visible)
 *
 * The logout test builds on the login-with-email flow:
 *  - After login, opens AvatarMenu and clicks "Đăng xuất"
 *  - Verifies redirect to `/` and anonymous state (login button visible)
 *
 * The test user is seeded by `e2e/global-setup.ts` before the suite runs.
 */

import { test, expect, TEST_USER } from "./fixtures";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Open the LoginModal from the landing page.
 *
 * Clicks the "Đăng nhập" button in the SiteHeader. The button is only
 * rendered when the auth state is `anonymous`, which is the default for a
 * fresh browser context.
 */
async function openLoginModal(page: import("@playwright/test").Page) {
  // The SiteHeader renders two anonymous CTAs: "Đăng nhập" and "Tạo tài khoản".
  // We target the first one by its exact text.
  await page.getByRole("button", { name: "Đăng nhập", exact: true }).click();
}

/**
 * Skip the LoginModal video intro and wait for the form surface to appear.
 *
 * The modal plays a short cinematic video before fading in the form. The
 * "Bỏ qua intro" button is visible while the video is running. Clicking it
 * (or waiting for the video to end) makes the form interactive.
 *
 * We click "Bỏ qua intro" when it appears; if it has already disappeared
 * (video ended on its own) we proceed immediately.
 */
async function skipVideoIntro(page: import("@playwright/test").Page) {
  const skipBtn = page.getByRole("button", { name: "Bỏ qua intro" });
  // Wait up to 5 s for the skip button to appear; if it never shows the
  // video already ended and the form is visible.
  try {
    await skipBtn.waitFor({ state: "visible", timeout: 5_000 });
    await skipBtn.click();
  } catch {
    // Video ended before we could click — that's fine.
  }

  // Wait for the form surface to become interactive. The identifier input
  // is the first focusable element in the login form.
  await page.locator("#login-identifier").waitFor({ state: "visible", timeout: 10_000 });
}

/**
 * Fill in the login form and submit.
 *
 * @param identifier - email address or phone number
 * @param password   - account password
 */
async function fillAndSubmitLoginForm(
  page: import("@playwright/test").Page,
  identifier: string,
  password: string,
) {
  await page.locator("#login-identifier").fill(identifier);
  await page.locator("#login-password").fill(password);
  await page.getByRole("button", { name: "Đăng nhập", exact: true }).last().click();
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

test.describe("Auth: Login & Logout", () => {
  test("login with email → redirect to /app → AvatarMenu visible", async ({ page }) => {
    // 1. Navigate to the landing page
    await page.goto("/");

    // 2. Open the LoginModal
    await openLoginModal(page);

    // 3. Skip the video intro
    await skipVideoIntro(page);

    // 4. Fill in email credentials and submit
    await fillAndSubmitLoginForm(page, TEST_USER.email, TEST_USER.password);

    // 5. Verify redirect to /app
    await page.waitForURL("**/app**", { timeout: 15_000 });
    expect(page.url()).toContain("/app");

    // 6. Verify authenticated state: AvatarMenu button is visible.
    //    The button has aria-label "Tài khoản của <full_name>".
    await expect(
      page.getByRole("button", { name: `Tài khoản của ${TEST_USER.full_name}` }),
    ).toBeVisible({ timeout: 10_000 });
  });

  test("login with phone number → redirect to /app → AvatarMenu visible", async ({ page }) => {
    // 1. Navigate to the landing page
    await page.goto("/");

    // 2. Open the LoginModal
    await openLoginModal(page);

    // 3. Skip the video intro
    await skipVideoIntro(page);

    // 4. Fill in phone credentials and submit
    await fillAndSubmitLoginForm(page, TEST_USER.phone, TEST_USER.password);

    // 5. Verify redirect to /app
    await page.waitForURL("**/app**", { timeout: 15_000 });
    expect(page.url()).toContain("/app");

    // 6. Verify authenticated state: AvatarMenu button is visible
    await expect(
      page.getByRole("button", { name: `Tài khoản của ${TEST_USER.full_name}` }),
    ).toBeVisible({ timeout: 10_000 });
  });

  test("logout → redirect to / → login button visible (anonymous state)", async ({ page }) => {
    // ---- Setup: log in first (email path) ----
    await page.goto("/");
    await openLoginModal(page);
    await skipVideoIntro(page);
    await fillAndSubmitLoginForm(page, TEST_USER.email, TEST_USER.password);

    // Wait until we are on /app and the AvatarMenu is rendered
    await page.waitForURL("**/app**", { timeout: 15_000 });
    const avatarBtn = page.getByRole("button", {
      name: `Tài khoản của ${TEST_USER.full_name}`,
    });
    await expect(avatarBtn).toBeVisible({ timeout: 10_000 });

    // ---- Logout flow ----

    // 1. Open the AvatarMenu dropdown
    await avatarBtn.click();

    // 2. Click "Đăng xuất" inside the dropdown
    //    The button has role="menuitem" and text "Đăng xuất"
    await page.getByRole("menuitem", { name: "Đăng xuất" }).click();

    // 3. Verify redirect to /
    await page.waitForURL("**/", { timeout: 15_000 });
    expect(new URL(page.url()).pathname).toBe("/");

    // 4. Verify anonymous state: the "Đăng nhập" button is visible again
    //    (SiteHeader renders it when auth state is anonymous)
    await expect(
      page.getByRole("button", { name: "Đăng nhập", exact: true }),
    ).toBeVisible({ timeout: 10_000 });
  });
});
