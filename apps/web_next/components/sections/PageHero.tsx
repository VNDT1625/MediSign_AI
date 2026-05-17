import { ReactNode } from "react";
import { Reveal } from "@/components/Reveal";

type Props = {
  eyebrow?: string;
  title: ReactNode;
  description?: ReactNode;
  cta?: ReactNode;
  visual?: ReactNode;
  /**
   * Layout split between text and visual. Default 7/5.
   * "balanced" -> 6/6, useful when visual carries strong content (e.g. Download).
   */
  layout?: "default" | "balanced";
  /** Extra slot below CTA, e.g. trust signal row. */
  extra?: ReactNode;
};

/**
 * Hero dùng chung cho các trang phụ (About, Download, Pricing...).
 * Khác hero Home: không dùng video, không glass card nghiêng.
 */
export function PageHero({
  eyebrow,
  title,
  description,
  cta,
  visual,
  layout = "default",
  extra,
}: Props) {
  const textCol =
    layout === "balanced" ? "lg:col-span-6" : "lg:col-span-7";
  const visualCol =
    layout === "balanced" ? "lg:col-span-6" : "lg:col-span-5";

  return (
    <section className="relative isolate overflow-hidden pt-28 pb-16 lg:pt-32 lg:pb-20">
      {/* Background gradient mềm mại */}
      <div
        aria-hidden="true"
        className="absolute inset-0 -z-10 bg-gradient-to-b from-brand-50 via-white to-white"
      />
      <div
        aria-hidden="true"
        className="absolute -top-32 left-1/2 -z-10 h-[420px] w-[1100px] -translate-x-1/2 rounded-full bg-brand/10 blur-3xl"
      />
      {/* Subtle dot grid for depth (decorative) */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 -z-10 opacity-[0.35]"
        style={{
          backgroundImage:
            "radial-gradient(rgba(2,132,199,0.18) 1px, transparent 1px)",
          backgroundSize: "26px 26px",
          maskImage:
            "linear-gradient(to bottom, black 0%, transparent 80%)",
          WebkitMaskImage:
            "linear-gradient(to bottom, black 0%, transparent 80%)",
        }}
      />

      <div className="container-page">
        <div className="grid items-center gap-10 lg:grid-cols-12 lg:gap-12">
          <Reveal className={textCol}>
            {eyebrow && (
              <span className="inline-flex items-center gap-2 rounded-pill bg-white px-4 py-1.5 text-xs font-semibold uppercase tracking-wide text-brand-700 shadow-soft">
                <span className="h-2 w-2 rounded-full bg-success animate-pulse-soft" />
                {eyebrow}
              </span>
            )}
            <h1 className="mt-4 text-[clamp(36px,5vw,56px)] font-extrabold leading-[1.05] tracking-tight text-ink-900">
              {title}
            </h1>
            {description && (
              <div className="mt-5 max-w-xl text-body text-ink-600">
                {description}
              </div>
            )}
            {cta && <div className="mt-7 flex flex-wrap gap-3">{cta}</div>}
            {extra && <div className="mt-6">{extra}</div>}
          </Reveal>
          {visual && <Reveal className={visualCol}>{visual}</Reveal>}
        </div>
      </div>
    </section>
  );
}
