// Browser MSW worker — DEFERRED until E2E coverage requires it.
//
// Phase 1 testing runs entirely in jsdom (Vitest) using `msw/node`
// (see `test/msw/server.ts`). The Playwright E2E suite (task 15.x) hits
// the real FastAPI dev server, so a service-worker-based mock is not
// needed yet. When that changes (e.g. for offline E2E or Storybook),
// uncomment the block below, install the worker via
// `npx msw init public/ --save`, and import `worker` from this module.
//
// import { setupWorker } from "msw/browser";
// import { defaultHandlers } from "./handlers";
//
// export const worker = setupWorker(...defaultHandlers);

export {};
