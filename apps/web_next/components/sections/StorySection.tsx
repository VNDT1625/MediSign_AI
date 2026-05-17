import { ReactNode } from "react";

type Props = {
  eyebrow?: string;
  title: string;
  description?: ReactNode;
  badge?: string;
  reverse?: boolean;
  bg?: "white" | "soft";
  visual: ReactNode;
  cta?: ReactNode;
};

export function StorySection({
  eyebrow,
  title,
  description,
  badge,
  reverse = false,
  bg = "white",
  visual,
  cta
}: Props) {
  const bgClass = bg === "soft" ? "bg-brand-50/60" : "bg-white";
  return (
    <section className={`${bgClass} py-20 lg:py-28`}>
      <div className="container-page">
        <div
          className={`grid items-center gap-10 lg:grid-cols-2 lg:gap-16 ${
            reverse ? "lg:[&>div:first-child]:order-2" : ""
          }`}
        >
          <div>
            {eyebrow && (
              <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-700">
                {eyebrow}
              </p>
            )}
            <h2 className="text-h1 text-ink-900">{title}</h2>
            {badge && <p className="mt-3 inline-block badge-app">{badge}</p>}
            {description && (
              <div className="mt-5 text-body text-ink-600">{description}</div>
            )}
            {cta && <div className="mt-7">{cta}</div>}
          </div>
          <div className="relative">{visual}</div>
        </div>
      </div>
    </section>
  );
}

export function PlaceholderVisual({
  label,
  ratio = "aspect-[4/3]",
  tone = "brand"
}: {
  label: string;
  ratio?: string;
  tone?: "brand" | "accent" | "soft";
}) {
  const toneClass =
    tone === "accent"
      ? "from-accent/15 via-white to-brand-50"
      : tone === "soft"
      ? "from-ink-100 via-white to-brand-50"
      : "from-brand-50 via-white to-accent/10";
  return (
    <div
      className={`relative w-full ${ratio} overflow-hidden rounded-card border border-ink-200 bg-gradient-to-br ${toneClass}`}
      role="img"
      aria-label={label}
    >
      <div className="absolute inset-0 grid place-items-center text-center">
        <div className="px-6">
          <div className="mx-auto mb-3 grid h-14 w-14 place-items-center rounded-pill bg-white shadow-soft">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path
                d="M4 7h16v10H4zM4 7l8 7 8-7"
                stroke="#0284C7"
                strokeWidth="2"
                strokeLinejoin="round"
                strokeLinecap="round"
              />
            </svg>
          </div>
          <p className="text-sm font-medium text-ink-600">Hình ảnh đang chuẩn bị</p>
          <p className="mt-1 text-xs text-ink-400">{label}</p>
        </div>
      </div>
    </div>
  );
}
