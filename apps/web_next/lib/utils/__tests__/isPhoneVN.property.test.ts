// Feature: web-app-functional-integration, Property 5: Phone regex VN

import { describe, expect, it } from "vitest";
import fc from "fast-check";

import { isPhoneVN } from "../isPhoneVN";

/**
 * Authoritative regex from `Requirements 2.4.2` — kept in lockstep with the
 * implementation. The property tests below MUST NOT diverge from this source.
 *
 * Validates: Requirements 2.4.2
 */
const PHONE_VN_REGEX = /^(\+84|0)\d{9,10}$/;

/**
 * Arbitrary that mints a string the regex SHOULD accept: a `+84` or `0` prefix
 * followed by exactly 9 or 10 ASCII digits. Used to bias the input space toward
 * the positive case so we don't rely solely on random noise.
 */
const validPhoneArb = fc
  .tuple(
    fc.constantFrom("+84", "0"),
    fc.integer({ min: 9, max: 10 }).chain((len) =>
      fc.stringMatching(new RegExp(`^\\d{${len}}$`)),
    ),
  )
  .map(([prefix, digits]) => prefix + digits);

/**
 * Arbitrary for strings that explicitly have **no internal whitespace** (the
 * precondition for the trim-idempotence property). We start from any string,
 * collapse any internal whitespace to a non-whitespace placeholder, and then
 * optionally prepend / append leading and trailing whitespace runs.
 */
const noInternalWhitespaceArb = fc
  .tuple(
    fc.string({ maxLength: 64 }).map((core) => core.replace(/\s/g, "X")),
    fc.stringMatching(/^[ \t\n\r]{0,4}$/),
    fc.stringMatching(/^[ \t\n\r]{0,4}$/),
  )
  .map(([core, lead, tail]) => `${lead}${core}${tail}`);

describe("isPhoneVN — Property 5: Phone regex VN", () => {
  it("agrees with /^(\\+84|0)\\d{9,10}$/ across valid, noisy, and mixed inputs", () => {
    // Validates: Requirements 2.4.2
    const inputArb = fc.oneof(
      validPhoneArb,
      fc.string(),
      fc.stringMatching(/^[+\d]*$/),
      fc.stringMatching(/^(\+84|0)\d*$/),
    );

    fc.assert(
      fc.property(inputArb, (s) => {
        expect(isPhoneVN(s)).toBe(PHONE_VN_REGEX.test(s));
      }),
      { numRuns: 25 },
    );
  });

  it("is idempotent under trim() when the input has no internal whitespace", () => {
    // Validates: Requirements 2.4.2
    fc.assert(
      fc.property(noInternalWhitespaceArb, (s) => {
        // Sanity: the generator must hold its precondition. Internal
        // whitespace is whitespace not at the very start or end of the string.
        const trimmed = s.trim();
        const internalHasWhitespace = /\s/.test(trimmed);
        fc.pre(!internalHasWhitespace);

        expect(isPhoneVN(s)).toBe(isPhoneVN(s.trim()));
      }),
      { numRuns: 25 },
    );
  });

  it("recognises every prefix · digit combination produced by validPhoneArb", () => {
    // Validates: Requirements 2.4.2
    fc.assert(
      fc.property(validPhoneArb, (s) => {
        expect(isPhoneVN(s)).toBe(true);
        expect(PHONE_VN_REGEX.test(s)).toBe(true);
      }),
      { numRuns: 25 },
    );
  });
});
