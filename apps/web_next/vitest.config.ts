import { defineConfig } from "vitest/config";
import { fileURLToPath } from "node:url";
import path from "node:path";

const rootDir = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  resolve: {
    alias: {
      "@": rootDir,
      "@medisign/shared-contracts": path.resolve(
        rootDir,
        "../../packages/shared_contracts/src",
      ),
    },
  },
  // Use the React 17+ automatic JSX runtime in test files. The app's
  // `tsconfig.json` keeps `"jsx": "preserve"` because Next.js handles
  // JSX transformation at build time, but Vitest transforms JSX with
  // esbuild — without `jsx: "automatic"` here, esbuild falls back to
  // the classic runtime which requires every `.tsx` test file to
  // import `React` explicitly. Setting it once here keeps test
  // authoring frictionless.
  esbuild: {
    jsx: "automatic",
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./test/setup.ts"],
    include: ["**/*.{test,spec,property.test}.{ts,tsx}"],
    exclude: ["node_modules", ".next", "e2e", "dist"],
    css: false,
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "lcov"],
      include: ["lib/**/*.{ts,tsx}", "components/**/*.{ts,tsx}", "app/**/*.{ts,tsx}"],
      exclude: ["**/*.d.ts", "**/__tests__/**", "**/test/**"],
    },
  },
});
