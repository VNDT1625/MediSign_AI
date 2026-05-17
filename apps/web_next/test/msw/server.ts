import { setupServer } from "msw/node";

import { defaultHandlers } from "./handlers";

/**
 * Default Node MSW server used by the Vitest setup file
 * (`test/setup.ts`). It boots with the full default handler set so that
 * any test that exercises the FastAPI surface gets a happy-path response
 * out of the box. Individual tests override specific routes via
 * `server.use(...)` to drive error / edge-case behaviour.
 */
export const server = setupServer(...defaultHandlers);
