/**
 * Regex used to detect email-shaped identifiers.
 *
 * Matches `<non-whitespace>@<non-whitespace>.<non-whitespace>`. Intentionally
 * permissive — server-side validation is the source of truth; this is only a
 * cheap classifier to route the LoginModal identifier field to the email vs
 * phone branch.
 *
 * Anchored at both ends (`^` / `$`) so internal whitespace is rejected.
 */
const EMAIL_REGEX = /^\S+@\S+\.\S+$/;

/**
 * Checks whether a string looks like an email address.
 *
 * Pure and total: never throws, defensive against non-string runtime values,
 * and idempotent under input that already lacks internal whitespace.
 *
 * @param input Candidate identifier.
 * @returns `true` when `input` matches `^\S+@\S+\.\S+$`, otherwise `false`.
 *
 * @see Requirements 2.4.2 (email regex)
 */
export function isEmail(input: string): boolean {
  if (typeof input !== "string") {
    return false;
  }

  return EMAIL_REGEX.test(input);
}
