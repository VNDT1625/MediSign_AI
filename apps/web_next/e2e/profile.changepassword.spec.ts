/**
 * E2E: Change password → force re-login
 *
 * Flow:
 *   1. Log in as the seeded test user.
 *   2. Navigate to /app/profile.
 *   3. Fill the change-password form (current → new → confirm).
 *   4. Submit and verify the success banner appears.
 *   5. Verify the user is redirected to /?session=changed-password.
 *   6. Verify the user is logged out (login button visible).
 *
 * Password hygiene:
 *   After the test the password has been changed to NEW_PASSWORD.
 *   The afterAll hook changes it back to TEST_USER.password via the
 *   FastAPI endpoint directly so subsequent runs (and global-setup) still
 *   work with the original credentials.
 *
 * @see Requirements 2.3.3
 */

import { test, expect, TEST_USER } from "./fixtures";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BACKEND_BASE = process.env.BACKEND_BASE_URL ?? "http://localhost:8000";
const API_BASE = `${BACKEND_BASE}/api/v1`;

/**
 * A unique new password that satisfies the backend policy:
 *   - min 8 chars
 *   - at least 1 uppercase letter
 *   - at least 1 digit
 */
const NEW_PASSWORD = "E2eChanged@456";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Obtain an access token for the given credentials via the FastAPI backend.
 * Used in afterAll to restore the original password without going through
 * the browser.
 */
async function getAccessToken(
  email: string,
  password: string
): Promise<string> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "(no body)");
    throw new Error(
      `[afterAll] Login failed (${res.status}): ${body}`
    );
  }
  const data = (await res.json()) as { access_token: string };
  return data.access_token;
}

/**
 * Change the password for the authenticated user via the FastAPI backend.
 * Used in afterAll to restore the original password.
 */
async function changePasswordViaApi(
  accessToken: string,
  currentPassword: string,
  newPassword: string
): Promise<void> {
  const res = await fetch(`${API_BASE}/auth/change-password`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "(no body)");
    throw new Error(
      `[afterAll] change-password failed (${res.status}): ${body}`
    );
  }
}

// ---------------------------------------------------------------------------
// Teardown: restore original password so subsequent runs still work
// ---------------------------------------------------------------------------

test.afterAll(async () => {
  try {
    const token = await getAccessToken(TEST_USER.email, NEW_PASSWORD);
    await changePasswordViaApi(token, NEW_PASSWORD, TEST_USER.password);
    console.log("[afterAll] Password restored to original.");
  } catch (err) {
    // If the password was never changed (test failed before submit), the
    // original password is still in place — try to confirm that.
    try {
      await getAccessToken(TEST_USER.email, TEST_USER.password);
      console.log(
        "[afterAll] Password was not changed; original credentials still valid."
      );
    } catch {
      console.error(
        "[afterAll] Could not restore password. Manual reset may be required.",
        err
      );
    }
  }
});

// ---------------------------------------------------------------------------
// Test
// ---------------------------------------------------------------------------

test("change password → success banner → logged out → redirect to /?session=changed-password", async ({
  page,
}) => {
  // ── Step 1: Log in as the test user ──────────────────────────────────────
  await page.goto("/");

  // Open the login modal (look for a button that opens it)
  const loginButton = page
    .getByRole("button", { name: /đăng nhập/i })
    .first();
  await loginButton.click();

  // Fill in credentials
  await page.getByLabel(/email|số điện thoại|identifier/i).fill(TEST_USER.email);
  await page.getByLabel(/mật khẩu/i).first().fill(TEST_USER.password);

  // Submit the login form
  await page.getByRole("button", { name: /đăng nhập/i }).last().click();

  // Wait until we land on an /app/* page (redirect after login)
  await page.waitForURL(/\/app/, { timeout: 15_000 });

  // ── Step 2: Navigate to /app/profile ─────────────────────────────────────
  await page.goto("/app/profile");

  // Wait for the change-password section to be visible
  await expect(
    page.getByRole("heading", { name: /đổi mật khẩu/i })
  ).toBeVisible({ timeout: 10_000 });

  // ── Step 3: Fill the change-password form ────────────────────────────────
  await page
    .locator("#change-current-password")
    .fill(TEST_USER.password);

  await page
    .locator("#change-new-password")
    .fill(NEW_PASSWORD);

  await page
    .locator("#change-confirm-password")
    .fill(NEW_PASSWORD);

  // ── Step 4: Submit ────────────────────────────────────────────────────────
  await page.getByRole("button", { name: /đổi mật khẩu/i }).click();

  // ── Step 5: Verify success banner ────────────────────────────────────────
  // The banner text is "Đổi mật khẩu thành công. Đang đăng xuất…"
  await expect(
    page.getByText(/đổi mật khẩu thành công/i)
  ).toBeVisible({ timeout: 10_000 });

  // ── Step 6: Verify redirect to /?session=changed-password ────────────────
  // The component waits 1500ms then calls logout() and router.push()
  await page.waitForURL(/\/\?session=changed-password/, { timeout: 15_000 });

  expect(page.url()).toContain("session=changed-password");

  // ── Step 7: Verify user is logged out (login button visible) ─────────────
  await expect(
    page.getByRole("button", { name: /đăng nhập/i }).first()
  ).toBeVisible({ timeout: 5_000 });
});
