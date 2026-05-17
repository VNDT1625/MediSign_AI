// Feature: web-app-functional-integration, Property 6: Token expiry monotonicity
/**
 * Property test for `lib/auth/tokenStore.ts`.
 *
 * Feature: web-app-functional-integration, Property 6: Token expiry monotonicity
 * Validates: Requirements 2.1.6
 *
 * Property 6 — for any pair of writes `tokenStore.set(t, n)` then
 * `tokenStore.set(t', n')` with `n, n' > 30`:
 *   • after the second write `tokenStore.get() === t'`
 *   • `tokenStore.isExpired()` flips to `true` only after `(n' - 30) * 1000` ms
 *     of wall-clock time have elapsed since the second write
 *   • `clear()` makes `get() === null` and `isExpired() === true`
 *
 * The store is a module-level singleton, so each fast-check iteration must
 * reset both the store and the fake-timer wall clock to keep iterations
 * independent.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import fc from "fast-check";
import { tokenStore } from "../tokenStore";

const FROZEN_BASELINE = new Date("2025-01-01T00:00:00.000Z");

describe("tokenStore — Property 6: Token expiry monotonicity", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(FROZEN_BASELINE);
    tokenStore.clear();
  });

  afterEach(() => {
    tokenStore.clear();
    vi.useRealTimers();
  });

  it("set overrides token; isExpired flips at (n' - 30) * 1000 ms after the second set; clear resets fully", () => {
    fc.assert(
      fc.property(
        fc.string(),
        fc.string(),
        // n, n' > 30 (above the 30s safety margin baked into tokenStore.set)
        fc.integer({ min: 31, max: 86_400 }),
        fc.integer({ min: 31, max: 86_400 }),
        // Arbitrary wall-clock gap (ms) between the two `set` calls.
        fc.integer({ min: 0, max: 10_000_000 }),
        (t1, t2, n1, n2, gapMs) => {
          // Reset singleton state and fake-clock between iterations so prior
          // iterations cannot leak.
          tokenStore.clear();
          vi.setSystemTime(FROZEN_BASELINE);

          // First write — sanity check that `get` returns what was stored.
          tokenStore.set(t1, n1);
          expect(tokenStore.get()).toBe(t1);

          // Move forward an arbitrary amount before the override.
          vi.advanceTimersByTime(gapMs);

          // Second write must override both the token and the expiry baseline.
          tokenStore.set(t2, n2);
          expect(tokenStore.get()).toBe(t2);

          // n' > 30 ⇒ (n' - 30) * 1000 > 0, so right after the second set we
          // are not yet expired.
          expect(tokenStore.isExpired()).toBe(false);

          const lifetimeMs = (n2 - 30) * 1000;

          // 1 ms before the cliff: still not expired.
          vi.advanceTimersByTime(lifetimeMs - 1);
          expect(tokenStore.isExpired()).toBe(false);
          // Token must still be reachable while not expired.
          expect(tokenStore.get()).toBe(t2);

          // At exactly (n' - 30) * 1000 ms elapsed since the second set:
          // `Date.now() >= _expiresAt` flips true.
          vi.advanceTimersByTime(1);
          expect(tokenStore.isExpired()).toBe(true);

          // `clear()` returns the store to the unauthenticated state.
          tokenStore.clear();
          expect(tokenStore.get()).toBeNull();
          expect(tokenStore.isExpired()).toBe(true);
        },
      ),
      { numRuns: 25 },
    );
  });
});
