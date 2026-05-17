/**
 * E2E: Route guard → intent → return path
 *
 * Validates Requirements 2.1.4 (smart redirect / login intent) and
 * 2.2.1 (route guard for /app/* protected routes).
 *
 * Flow under test:
 *   1. Anonymous user navigates directly to /app/medicine.
 *   2. Edge middleware detects no `medisign_rt` cookie → redirects to
 *      /?login=1&intent=%2Fapp%2Fmedicine.
 *   3. The landing page detects `?login=1` and auto-opens LoginModal.
 *   4. User fills in credentials and submits.
 *   5. After successful login the intent is consumed and the user lands
 *      on /app/medicine (the original destination).
 */

import { test, expect, TEST_USER } from "./fixtures";

test.describe("Route guard → intent → return path", () => {
  test(
    "anonymous visit to /app/medicine redirects to login, then returns to /app/medicine after login",
    async ({ page }) => {
      // ----------------------------------------------------------------
      // Step 1: Navigate to a protected route without any auth cookie.
      // The browser starts with a clean context (no cookies) so the
      // middleware will always redirect.
      // ----------------------------------------------------------------
      await page.goto("/app/medicine");

      // ----------------------------------------------------------------
      // Step 2: Verify the middleware redirect landed on the home page
      // with the expected query parameters.
      //
      // The middleware sets:
      //   ?login=1&intent=%2Fapp%2Fmedicine
      // ----------------------------------------------------------------
      await expect(page).toHaveURL(/\/\?login=1/);

      const url = new URL(page.url());
      expect(url.searchParams.get("login")).toBe("1");
      expect(url.searchParams.get("intent")).toBe("/app/medicine");

      // ----------------------------------------------------------------
      // Step 3: Verify the LoginModal opened automatically.
      //
      // The modal is a `role="dialog"` element. The landing page's
      // useEffect watches for `?login=1` and calls setLoginOpen(true).
      // We wait for the dialog to become visible (aria-hidden="false").
      // ----------------------------------------------------------------
      const dialog = page.getByRole("dialog");
      await expect(dialog).toBeVisible({ timeout: 10_000 });

      // ----------------------------------------------------------------
      // Step 4: Wait for the video intro to finish (or skip it) so the
      // login form becomes interactive.
      //
      // The form surface fades in after the video ends. The "Bỏ qua
      // intro" button is present while the video is playing; clicking it
      // advances the video to the end and reveals the form immediately.
      // ----------------------------------------------------------------
      const skipButton = page.getByRole("button", { name: /bỏ qua intro/i });
      if (await skipButton.isVisible({ timeout: 3_000 }).catch(() => false)) {
        await skipButton.click();
      }

      // ----------------------------------------------------------------
      // Step 5: Fill in the login form and submit.
      //
      // The form has a single "identifier" field (email or phone) and a
      // password field. We use the seeded test user's email.
      // ----------------------------------------------------------------
      const identifierInput = page.getByRole("textbox", {
        name: /email|số điện thoại|identifier/i,
      });
      await expect(identifierInput).toBeVisible({ timeout: 8_000 });
      await identifierInput.fill(TEST_USER.email);

      const passwordInput = page.locator('input[type="password"]');
      await expect(passwordInput).toBeVisible();
      await passwordInput.fill(TEST_USER.password);

      const submitButton = page.getByRole("button", {
        name: /đăng nhập/i,
      });
      await expect(submitButton).toBeEnabled();
      await submitButton.click();

      // ----------------------------------------------------------------
      // Step 6: After successful login the modal closes and the router
      // pushes to the original intent path: /app/medicine.
      // ----------------------------------------------------------------
      await expect(page).toHaveURL(/\/app\/medicine/, { timeout: 15_000 });
    },
  );
});
