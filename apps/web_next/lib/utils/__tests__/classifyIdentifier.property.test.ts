// Feature: web-app-functional-integration, Property 2: Identifier classification disjoint
import { describe, expect, it } from "vitest";
import fc from "fast-check";

import { classifyIdentifier } from "../classifyIdentifier";
import { isEmail } from "../isEmail";
import { isPhoneVN } from "../isPhoneVN";

/**
 * Property 2: Identifier classification disjoint
 * Validates: Requirements 2.1.2
 *
 * `classifyIdentifier` is the routing helper used by `LoginModal` to decide
 * whether the identifier field should be sent as an email or a phone number.
 * It must satisfy three operational properties for any string input:
 *
 *   1. Total / disjoint return: classifyIdentifier(s) is exactly one of
 *      `"email" | "phone" | "invalid"` and the call never throws. Disjointness
 *      is structurally enforced by the union return type, so the test simply
 *      asserts membership in the allowlist.
 *
 *   2. Trim idempotence: classifyIdentifier(s) === classifyIdentifier(s.trim())
 *      because the implementation trims its input before classifying.
 *
 *   3. Branch semantics (the actual disjointness contract):
 *        - "email"   ⇒ isEmail(trimmed) === true
 *        - "phone"   ⇒ isEmail(trimmed) === false ∧ isPhoneVN(trimmed) === true
 *        - "invalid" ⇒ isEmail(trimmed) === false ∧ isPhoneVN(trimmed) === false
 *      In particular there is no string `s` whose classification can be
 *      simultaneously "email" and "phone".
 *
 * Generators cover arbitrary strings (with whitespace and unicode), known
 * email shapes, known VN phone shapes, and freeform noise.
 */

const ALLOWED = ["email", "phone", "invalid"] as const;
type Label = (typeof ALLOWED)[number];

/** Arbitrary that produces email-shaped strings (`local@domain.tld`). */
const emailArb = fc
  .tuple(
    fc.stringMatching(/^[A-Za-z0-9._%+-]{1,16}$/),
    fc.stringMatching(/^[A-Za-z0-9-]{1,16}$/),
    fc.stringMatching(/^[A-Za-z]{2,8}$/),
  )
  .map(([local, domain, tld]) => `${local}@${domain}.${tld}`);

/** Arbitrary that produces VN phone-shaped strings (`+84` or `0` prefix + 9..10 digits). */
const phoneArb = fc
  .tuple(fc.constantFrom("+84", "0"), fc.integer({ min: 9, max: 10 }))
  .chain(([prefix, digitCount]) =>
    fc
      .stringMatching(new RegExp(`^\\d{${digitCount}}$`))
      .map((digits) => `${prefix}${digits}`),
  );

/**
 * Freeform noise: arbitrary strings (ASCII + unicode graphemes) that are
 * usually neither email nor phone. Length is bounded for shrinker speed.
 */
const noiseArb = fc.string({ minLength: 1, maxLength: 64, unit: "grapheme" });

/**
 * Malformed inputs that look almost-email or almost-phone but should fall
 * through to "invalid". These are deterministic seeds, not generators, but
 * we let `fc.constantFrom` lift them into the same arbitrary universe.
 */
const malformedArb = fc.constantFrom(
  "",
  " ",
  "   ",
  "\t\n",
  "@",
  "@.",
  "a@b",
  "a@b.",
  ".@.",
  "+84",
  "0",
  "0123",
  "+8401234567890123", // too long
  "012345678", // 9 digits without prefix → fails the `^(\+84|0)\d{9,10}$` shape
  "+84 912 345 678", // internal whitespace → rejected
  "user @example.com", // internal whitespace
  "không-phải-email", // unicode noise
  "📞0987654321", // emoji prefix
);

/** Mixed arbitrary covering valid email/phone shapes, arbitrary noise, and malformed seeds. */
const identifierArb = fc.oneof(
  { weight: 1, arbitrary: emailArb },
  { weight: 1, arbitrary: phoneArb },
  { weight: 3, arbitrary: noiseArb },
  { weight: 1, arbitrary: malformedArb },
);

describe("classifyIdentifier — Property 2: classification disjoint", () => {
  it("returns exactly one of email | phone | invalid for any non-empty string", () => {
    fc.assert(
      fc.property(identifierArb, (raw) => {
        // Constrain to the spec's domain: non-empty strings.
        fc.pre(raw.length > 0);

        const result = classifyIdentifier(raw);
        expect(ALLOWED).toContain(result satisfies Label);
      }),
      { numRuns: 25 },
    );
  });

  it("never throws for any string input (including empty and whitespace-only)", () => {
    fc.assert(
      fc.property(fc.string({ unit: "grapheme" }), (raw) => {
        expect(() => classifyIdentifier(raw)).not.toThrow();
      }),
      { numRuns: 25 },
    );
  });

  it("is idempotent under trim: classify(s) === classify(s.trim())", () => {
    // Pad the inner identifier with arbitrary leading/trailing whitespace
    // (spaces, tabs, newlines) and verify the label is unaffected.
    const whitespaceArb = fc.stringMatching(/^[ \t\n\r]{0,8}$/);

    fc.assert(
      fc.property(
        identifierArb,
        whitespaceArb,
        whitespaceArb,
        (inner, leading, trailing) => {
          const padded = `${leading}${inner}${trailing}`;

          expect(classifyIdentifier(padded)).toBe(
            classifyIdentifier(padded.trim()),
          );
        },
      ),
      { numRuns: 25 },
    );
  });

  it("each branch implies the corresponding predicate combination on the trimmed input", () => {
    // The disjointness contract: at most one of (isEmail, isPhoneVN) can drive
    // the classification, and "invalid" is reached only when both predicates
    // reject the trimmed input. We verify by case-splitting on the returned
    // label rather than asserting `email && phone` is impossible (which is
    // structurally guaranteed by the return type).
    fc.assert(
      fc.property(identifierArb, (raw) => {
        const trimmed = raw.trim();
        const label = classifyIdentifier(raw);

        if (label === "email") {
          expect(isEmail(trimmed)).toBe(true);
        } else if (label === "phone") {
          // Email check must fail (email is preferred when both match), and
          // phone check must succeed.
          expect(isEmail(trimmed)).toBe(false);
          expect(isPhoneVN(trimmed)).toBe(true);
        } else {
          // "invalid" ⇒ both predicates reject (or the trimmed string is empty).
          expect(isEmail(trimmed)).toBe(false);
          expect(isPhoneVN(trimmed)).toBe(false);
        }
      }),
      { numRuns: 25 },
    );
  });
});
