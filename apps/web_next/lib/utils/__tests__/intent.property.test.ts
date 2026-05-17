// Feature: web-app-functional-integration, Property 1: Intent round-trip
import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { decodeIntent, encodeIntent, type Intent } from "../intent";

/**
 * Property 1: Intent round-trip
 *
 * Validates: Requirements 2.1.4, 2.2.1
 *
 * For any allowed `intent` ∈ `{"home", "chat", `/app/${string}`}` and any
 * string `prefilledMessage` (≤ 500 chars, may contain unicode and URL-
 * special characters like `?`, `&`, `=`), the codec must round-trip
 * cleanly:
 *
 *   decodeIntent(encodeIntent(i, p)) === { intent: i, prefilledMessage: p }
 *
 * and must never throw for valid intents.
 *
 * This anchors the open-redirect defense: values inside the allowlist
 * must survive the wire format unchanged so that post-login redirects
 * land where the user intended.
 */
describe("intent codec — Property 1: Intent round-trip", () => {
  // Allowlist arbitrary. The `/app/${string}` branch generates a `string`
  // suffix that may be empty (per the type `/app/${string}`, an empty
  // suffix yields the bare path `"/app/"` which is still valid) and may
  // contain URL-special and unicode characters to exercise encoding edges.
  // We use `unit: "grapheme"` so the generated suffixes are always well-
  // formed Unicode (no lone surrogates, which the URL spec would replace
  // with U+FFFD and break the round-trip — that's outside this property).
  const intentArb: fc.Arbitrary<Intent> = fc.oneof(
    fc.constant<Intent>("home"),
    fc.constant<Intent>("chat"),
    fc
      .string({ maxLength: 500, unit: "grapheme" })
      .map((suffix) => `/app/${suffix}` as Intent),
  );

  // Prefilled message arbitrary: any string ≤ 500 chars. We deliberately
  // include URL-special characters (?, &, =) and unicode via the grapheme
  // unit so the property covers the realistic input space described in
  // the design (HeroVideo question, chat bot prefill, etc.).
  const prefillArb = fc.string({ maxLength: 500, unit: "grapheme" });

  it("decodeIntent(encodeIntent(i, p)) returns {intent: i, prefilledMessage: p} and never throws", () => {
    fc.assert(
      fc.property(intentArb, prefillArb, (intent, prefilledMessage) => {
        // If either function throws, fast-check surfaces it as a property
        // failure with a shrunk counterexample — that satisfies the
        // "never throws" half of the property for valid inputs.
        const encoded = encodeIntent(intent, prefilledMessage);
        const decoded = decodeIntent(encoded);

        expect(decoded).toEqual({ intent, prefilledMessage });
      }),
      { numRuns: 25 },
    );
  });
});
