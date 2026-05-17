/**
 * Regex used to detect Vietnamese phone-shaped identifiers.
 *
 * Accepts the country-prefixed form `+84` or the local leading-zero form `0`,
 * followed by 9 or 10 digits — covering the common 10- and 11-digit VN mobile
 * formats. Anchored at both ends so internal whitespace and stray characters
 * are rejected.
 *
 * Server-side validation remains the source of truth; this regex only routes
 * the LoginModal identifier field between email and phone branches.
 */
const PHONE_VN_REGEX = /^(\+84|0)\d{9,10}$/;

/**
 * Checks whether a string looks like a Vietnamese phone number.
 *
 * Pure and total: never throws, defensive against non-string runtime values,
 * and idempotent under `trim` for inputs without internal whitespace
 * (`isPhoneVN(s) === isPhoneVN(s.trim())`).
 *
 * @param input Candidate identifier.
 * @returns `true` when `input` matches `^(\+84|0)\d{9,10}$`, otherwise `false`.
 *
 * @see Requirements 2.4.2 (phone regex VN)
 */
export function isPhoneVN(input: string): boolean {
  if (typeof input !== "string") {
    return false;
  }

  return PHONE_VN_REGEX.test(input);
}
