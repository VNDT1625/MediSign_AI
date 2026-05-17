import { isEmail } from "./isEmail";
import { isPhoneVN } from "./isPhoneVN";

/**
 * Classifies a user-supplied identifier as an email address, a Vietnamese
 * phone number, or invalid input.
 *
 * The function:
 *  - Trims surrounding whitespace before classification, so
 *    `classify(s) === classify(s.trim())` for any input.
 *  - Is disjoint: at most one branch is taken. If the trimmed input matches
 *    both regexes (theoretical overlap), email is preferred.
 *  - Never throws, even for non-string inputs at runtime (defensive guard).
 *
 * @param input Raw user input (e.g., from the LoginModal identifier field).
 * @returns `"email" | "phone" | "invalid"`.
 *
 * @see Requirements 2.1.2 (auto-detect email vs phone)
 */
export function classifyIdentifier(
  input: string,
): "email" | "phone" | "invalid" {
  // Defensive: never throw, even if a non-string slips through at runtime.
  if (typeof input !== "string") {
    return "invalid";
  }

  const trimmed = input.trim();

  if (trimmed.length === 0) {
    return "invalid";
  }

  // Email is checked first so the classifier stays disjoint even if a future
  // phone regex change accidentally overlaps with the email regex.
  if (isEmail(trimmed)) {
    return "email";
  }

  if (isPhoneVN(trimmed)) {
    return "phone";
  }

  return "invalid";
}
