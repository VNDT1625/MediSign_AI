import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright E2E configuration.
 * Runs against the Next.js dev server on port 3000.
 * Backend (FastAPI) must be running separately on port 8000.
 *
 * Run: npm run e2e
 */
export default defineConfig({
  testDir: "e2e",

  /** Global setup: seed test user in the backend before any test runs */
  globalSetup: "./e2e/global-setup.ts",

  /** Maximum time one test can run */
  timeout: 30_000,

  /** Fail the build on CI if you accidentally left test.only in the source */
  forbidOnly: !!process.env.CI,

  /** Retry on CI only */
  retries: process.env.CI ? 2 : 0,

  /** Opt out of parallel tests on CI */
  workers: process.env.CI ? 1 : undefined,

  reporter: [["list"], ["html", { open: "never" }]],

  use: {
    /** Base URL for all page.goto() calls */
    baseURL: "http://localhost:3000",

    /** Collect trace on first retry to help debug failures */
    trace: "on-first-retry",

    /** Screenshot on failure */
    screenshot: "only-on-failure",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "webkit",
      use: { ...devices["Desktop Safari"] },
    },
  ],

  /**
   * Start the Next.js dev server before running tests.
   * The server is reused if already running on port 3000.
   */
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
    stdout: "pipe",
    stderr: "pipe",
  },
});
