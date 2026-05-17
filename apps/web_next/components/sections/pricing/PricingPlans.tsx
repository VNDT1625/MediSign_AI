"use client";

import { useState } from "react";
import { Reveal } from "@/components/Reveal";

type Cycle = "monthly" | "yearly";

type Plan = {
  id: string;
  name: string;
  monthlyPrice: string;
  yearlyPrice: string;
  yearlySaving?: string;
  cycle: string;
  desc: string;
  features: { text: string; highlight?: boolean }[];
  cta: string;
  tone: "light" | "dark" | "premium";
  badge?: string;
  /** Hiển thị "Phổ biến nhất" ribbon */
  popular?: boolean;
};

const PLANS: Plan[] = [
  {
    id: "free",
    name: "Cơ bản",
    monthlyPrice: "Miễn phí",
    yearlyPrice: "Miễn phí",
    cycle: "",
    desc: "Khám phá AI y tế, không cần thẻ tín dụng.",
    features: [
      { text: "Chat AI cơ bản (20 lượt/ngày)" },
      { text: "Lịch sử hội thoại 7 ngày" },
      { text: "Tra cứu thông tin thuốc" },
      { text: "Hỗ trợ qua email" },
      { text: "1 thiết bị" }
    ],
    cta: "Bắt đầu miễn phí",
    tone: "light"
  },
  {
    id: "pro",
    name: "Pro",
    monthlyPrice: "199.000đ",
    yearlyPrice: "159.000đ",
    yearlySaving: "Tiết kiệm 480.000đ/năm",
    cycle: "/ tháng",
    desc: "Trải nghiệm đầy đủ cho cá nhân chăm sóc sức khoẻ.",
    features: [
      { text: "Chat AI không giới hạn 24/7", highlight: true },
      { text: "Hồ sơ sức khoẻ chi tiết", highlight: true },
      { text: "Lịch sử & nhắc lịch không giới hạn" },
      { text: "Đồng bộ đa thiết bị" },
      { text: "Phân tích triệu chứng nâng cao" },
      { text: "Ưu tiên hỗ trợ 24/7" }
    ],
    cta: "Dùng thử Pro 7 ngày",
    tone: "dark",
    badge: "Phổ biến nhất",
    popular: true
  },
  {
    id: "family",
    name: "Gia đình",
    monthlyPrice: "399.000đ",
    yearlyPrice: "319.000đ",
    yearlySaving: "Tiết kiệm 960.000đ/năm",
    cycle: "/ tháng",
    desc: "Chăm sóc toàn diện cho cả gia đình bạn.",
    features: [
      { text: "Tất cả tính năng Pro", highlight: true },
      { text: "Tối đa 6 thành viên", highlight: true },
      { text: "Theo dõi sức khoẻ cả nhà" },
      { text: "Tư vấn chuyên sâu theo hồ sơ" },
      { text: "Báo cáo tổng hợp hàng tháng" },
      { text: "Cảnh báo sức khoẻ thông minh" }
    ],
    cta: "Dùng thử Gia đình 7 ngày",
    tone: "premium"
  }
];

export function PricingPlans({ onCta }: { onCta?: () => void }) {
  const [cycle, setCycle] = useState<Cycle>("monthly");

  return (
    <section id="plans" className="py-16 lg:py-24">
      <div className="container-page">
        {/* ── Billing toggle ── */}
        <Reveal className="flex flex-col items-center gap-3">
          <div className="flex items-center gap-3">
            <span
              className={`text-sm font-medium transition-colors duration-200 ${
                cycle === "monthly" ? "text-ink-900" : "text-ink-400"
              }`}
            >
              Hàng tháng
            </span>

            <button
              type="button"
              role="switch"
              aria-checked={cycle === "yearly"}
              aria-label="Chuyển sang thanh toán hàng năm"
              onClick={() => setCycle((c) => (c === "monthly" ? "yearly" : "monthly"))}
              className={`relative inline-flex h-7 w-12 cursor-pointer items-center rounded-pill transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 ${
                cycle === "yearly" ? "bg-brand" : "bg-ink-200"
              }`}
            >
              <span
                className={`inline-block h-5 w-5 rounded-full bg-white shadow-soft transition-transform duration-200 ${
                  cycle === "yearly" ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>

            <span
              className={`flex items-center gap-1.5 text-sm font-medium transition-colors duration-200 ${
                cycle === "yearly" ? "text-ink-900" : "text-ink-400"
              }`}
            >
              Hàng năm
              <span className="rounded-pill bg-success-soft px-2 py-0.5 text-xs font-bold text-success">
                -20%
              </span>
            </span>
          </div>

          {cycle === "yearly" && (
            <p className="text-sm font-medium text-success">
              Tiết kiệm tới 960.000đ mỗi năm khi chọn thanh toán hàng năm
            </p>
          )}
        </Reveal>

        {/* ── Plan cards ── */}
        <Reveal
          as="ul"
          stagger
          className="mx-auto mt-10 grid max-w-6xl items-stretch gap-6 lg:grid-cols-3"
        >
          {PLANS.map((plan, i) => (
            <li
              key={plan.id}
              className="reveal flex"
              style={{ ["--reveal-i" as any]: i }}
            >
              <PlanCard plan={plan} cycle={cycle} onCta={onCta} />
            </li>
          ))}
        </Reveal>

        {/* ── Bottom note ── */}
        <Reveal delay={320} className="mt-8 text-center">
          <p className="text-sm text-ink-500">
            Tất cả gói trả phí đều có{" "}
            <strong className="font-semibold text-ink-700">7 ngày dùng thử miễn phí</strong>.
            {" "}Không cần thẻ tín dụng. Huỷ bất cứ lúc nào.
          </p>
        </Reveal>
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────────────────────
   Plan card — 3 tones: light (free), dark (pro), premium (family)
───────────────────────────────────────────────────────────── */
function PlanCard({
  plan,
  cycle,
  onCta
}: {
  plan: Plan;
  cycle: Cycle;
  onCta?: () => void;
}) {
  const price = cycle === "yearly" ? plan.yearlyPrice : plan.monthlyPrice;
  const saving = cycle === "yearly" ? plan.yearlySaving : undefined;

  if (plan.tone === "dark") {
    return (
      <div className="card-lift relative flex w-full flex-col overflow-hidden rounded-card bg-gradient-to-b from-[#0B3A8C] to-[#0F4FBF] p-6 text-white shadow-card lg:scale-[1.04]">
        {/* Decorative blobs */}
        <span aria-hidden className="pointer-events-none absolute -right-10 -top-10 h-36 w-36 rounded-full bg-white/10 blur-2xl" />
        <span aria-hidden className="pointer-events-none absolute -left-8 bottom-0 h-28 w-28 rounded-full bg-accent/15 blur-2xl" />

        {/* Popular badge */}
        {plan.badge && (
          <span className="absolute -top-3.5 left-1/2 -translate-x-1/2 rounded-pill bg-accent px-4 py-1 text-xs font-bold uppercase tracking-wider text-white shadow-soft">
            {plan.badge}
          </span>
        )}

        <PlanHeader name={plan.name} price={price} cycle={plan.cycle} saving={saving} dark />

        <p className="mt-2 text-sm text-white/70">{plan.desc}</p>

        <ul className="mt-5 flex-1 space-y-2.5">
          {plan.features.map((f) => (
            <li key={f.text} className="flex items-start gap-2 text-sm">
              <CheckIcon dark />
              <span className={f.highlight ? "font-semibold text-white" : "text-white/85"}>
                {f.text}
              </span>
            </li>
          ))}
        </ul>

        <button
          type="button"
          onClick={onCta}
          className="mt-6 inline-flex h-11 w-full cursor-pointer items-center justify-center rounded-pill bg-white text-base font-semibold text-brand-700 shadow-soft transition-colors duration-200 hover:bg-brand-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-brand-700"
        >
          {plan.cta}
        </button>

        <p className="mt-3 text-center text-xs text-white/50">7 ngày miễn phí · Không cần thẻ</p>
      </div>
    );
  }

  if (plan.tone === "premium") {
    return (
      <div className="card-lift relative flex w-full flex-col overflow-hidden rounded-card border border-ink-200 bg-white p-6 shadow-soft hover:border-brand/30">
        {/* Subtle premium top accent */}
        <div className="absolute inset-x-0 top-0 h-1 rounded-t-card bg-gradient-to-r from-brand via-[#0EA5E9] to-brand" aria-hidden />

        <PlanHeader name={plan.name} price={price} cycle={plan.cycle} saving={saving} />

        <p className="mt-2 text-sm text-ink-500">{plan.desc}</p>

        <ul className="mt-5 flex-1 space-y-2.5">
          {plan.features.map((f) => (
            <li key={f.text} className="flex items-start gap-2 text-sm">
              <CheckIcon />
              <span className={f.highlight ? "font-semibold text-ink-900" : "text-ink-700"}>
                {f.text}
              </span>
            </li>
          ))}
        </ul>

        <button
          type="button"
          onClick={onCta}
          className="mt-6 inline-flex h-11 w-full cursor-pointer items-center justify-center rounded-pill border-2 border-ink-200 bg-white text-base font-semibold text-ink-800 transition-colors duration-200 hover:border-brand hover:text-brand focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2"
        >
          {plan.cta}
        </button>

        <p className="mt-3 text-center text-xs text-ink-400">7 ngày miễn phí · Không cần thẻ</p>
      </div>
    );
  }

  // tone === "light" (free plan)
  return (
    <div className="card-lift flex w-full flex-col rounded-card border border-ink-200 bg-white p-6 shadow-soft hover:border-brand/30">
      <PlanHeader name={plan.name} price={price} cycle={plan.cycle} saving={saving} />

      <p className="mt-2 text-sm text-ink-500">{plan.desc}</p>

      <ul className="mt-5 flex-1 space-y-2.5">
        {plan.features.map((f) => (
          <li key={f.text} className="flex items-start gap-2 text-sm text-ink-700">
            <CheckIcon />
            <span>{f.text}</span>
          </li>
        ))}
      </ul>

      <button
        type="button"
        onClick={onCta}
        className="mt-6 inline-flex h-11 w-full cursor-pointer items-center justify-center rounded-pill border-2 border-ink-200 bg-white text-base font-semibold text-ink-800 transition-colors duration-200 hover:border-brand hover:text-brand focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2"
      >
        {plan.cta}
      </button>
    </div>
  );
}

function PlanHeader({
  name,
  price,
  cycle,
  saving,
  dark = false
}: {
  name: string;
  price: string;
  cycle: string;
  saving?: string;
  dark?: boolean;
}) {
  return (
    <div>
      <h2 className={`text-h3 ${dark ? "text-white" : "text-ink-900"}`}>{name}</h2>
      <div className="mt-3 flex items-baseline gap-1">
        <span className={`text-3xl font-bold ${dark ? "text-white" : "text-ink-900"}`}>
          {price}
        </span>
        {cycle && (
          <span className={`text-base font-medium ${dark ? "text-white/60" : "text-ink-500"}`}>
            {cycle}
          </span>
        )}
      </div>
      {saving && (
        <span className={`mt-1 inline-block text-xs font-semibold ${dark ? "text-green-300" : "text-success"}`}>
          {saving}
        </span>
      )}
    </div>
  );
}

function CheckIcon({ dark = false }: { dark?: boolean }) {
  return (
    <span
      aria-hidden
      className={`mt-0.5 grid h-5 w-5 flex-none place-items-center rounded-full ${
        dark ? "bg-white/15 text-white" : "bg-success-soft text-success"
      }`}
    >
      <svg width="11" height="11" viewBox="0 0 24 24" fill="none">
        <path d="M5 12l4 4L19 6" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </span>
  );
}
