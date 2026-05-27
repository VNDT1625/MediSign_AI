/**
 * `Logo` — MediSign AI brand mark.
 *
 * Renders the cropped wordmark from `/public/logo.png` (944×322, aspect
 * ~2.93:1). The artwork already contains the "MediSign" wordmark, so
 * we do NOT render duplicate text next to it.
 *
 * Slot sizing:
 *   - Default: `h-10 lg:h-12` (40px / 48px tall) — sized for the header
 *     pill (h-14 / h-16) so the logo doesn't look lép. Width auto.
 *   - Caller can override via `className` (e.g. `[&>img]:h-8` for the
 *     compact desktop app header).
 *
 * Notes:
 * - Uses a plain `<img>` with the Next.js no-img-element disable because:
 *     1. The artwork is a raster brand mark — no responsive variants needed.
 *     2. Header / footer slots are above-the-fold; we want the byte to
 *        ship in the initial HTML, not deferred through next/image.
 * - `aria-label` on the wrapper announces the brand to AT; the `<img>`
 *   itself carries `alt=""` so screen readers don't read the name twice.
 */
export function Logo({ className = "" }: { className?: string }) {
  return (
    <span
      role="img"
      aria-label="MediSign AI"
      className={`inline-flex items-center ${className}`}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src="/logo.png"
        alt=""
        className="h-12 w-auto select-none sm:h-14 lg:h-16 2xl:h-20"
        draggable={false}
      />
    </span>
  );
}
