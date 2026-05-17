import "@testing-library/jest-dom/vitest";
import { server } from "./msw/server";

// Default MSW server lifecycle. Handlers are registered in
// `test/msw/server.ts` (task 2.1 ships an empty server; task 2.2 wires
// the FastAPI surface). Hooks come from Vitest globals (configured in
// vitest.config.ts) so we don't import the runner from a setup file.
beforeAll(() => {
  server.listen({ onUnhandledRequest: "error" });
});

afterEach(() => {
  server.resetHandlers();
});

afterAll(() => {
  server.close();
});
