/**
 * Playwright global setup — runs once before all tests.
 *
 * Seeds a deterministic test user in the FastAPI backend so every E2E test
 * can rely on a known account without creating a new one each run.
 *
 * The backend must be running on port 8000 before `npm run e2e` is invoked.
 * (The Next.js dev server is started automatically by playwright.config.ts.)
 */

const BACKEND_BASE = process.env.BACKEND_BASE_URL ?? "http://localhost:8000";
const API_BASE = `${BACKEND_BASE}/api/v1`;

/** Fixed credentials shared across all E2E tests. */
export const TEST_USER = {
  email: "e2e_test@medisign.local",
  phone: "0900000001",
  username: "e2e_testuser",
  full_name: "E2E Test User",
  password: "E2eTest@123",
} as const;

async function globalSetup(): Promise<void> {
  console.log("[global-setup] Seeding E2E test user…");

  const response = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: TEST_USER.email,
      phone: TEST_USER.phone,
      username: TEST_USER.username,
      full_name: TEST_USER.full_name,
      password: TEST_USER.password,
    }),
  });

  if (response.ok) {
    console.log("[global-setup] Test user created successfully.");
    return;
  }

  if (response.status === 409) {
    // User already exists from a previous run — that's fine.
    console.log("[global-setup] Test user already exists, skipping creation.");
    return;
  }

  // Any other error is unexpected; surface the body to help debugging.
  const body = await response.text().catch(() => "(no body)");
  throw new Error(
    `[global-setup] Failed to seed test user. ` +
      `Status: ${response.status}. Body: ${body}`
  );
}

export default globalSetup;
