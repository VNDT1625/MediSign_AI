/**
 * Shared Playwright fixtures and test user constants for E2E tests.
 *
 * Import `test` and `expect` from this file instead of `@playwright/test`
 * directly so that custom fixtures can be added here in future tasks without
 * touching every test file.
 *
 * Usage:
 *   import { test, expect, TEST_USER } from "../fixtures";
 */

export { test, expect } from "@playwright/test";

/**
 * Fixed credentials for the seeded E2E test user.
 * The user is created (or verified to exist) in `global-setup.ts`.
 */
export const TEST_USER = {
  email: "e2e_test@medisign.local",
  phone: "0900000001",
  username: "e2e_testuser",
  full_name: "E2E Test User",
  password: "E2eTest@123",
} as const;
