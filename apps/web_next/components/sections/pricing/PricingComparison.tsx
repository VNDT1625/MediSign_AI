import { Reveal } from "@/components/Reveal";
import { Fragment } from "react";

type FeatureRow = {
  category: string;
  features: {
    label: string;
    tooltip?: string;
    free: string | boolean;
    pro: string | boolean;
    family: string | boolean;
  }[];
};

const ROWS: FeatureRow[] = [
  {
    category: "Chat & Tư vấn AI",
    features: [
      { label: "Chat AI cơ bản", free: true, pro: true, family: true },
      { label: "Số lượt chat mỗi ngày", free: "20 lượt", pro: "Không giới hạn", family: "Không giới hạn" },
      { label: "Tư vấn 24/7", free: false, pro: true, family: true },
      { label: "Phân tích triệu chứng nâng cao", free: false, pro: true, family: true },
      { label: "Tư vấn chuyên sâu theo hồ sơ", free: false, pro: false, family: true }
    ]
  },
  {
    category: "Hồ sơ & Lịch sử",
    features: [
      { label: "Lịch sử hội thoại", free: "7 ngày", pro: "Không giới hạn", family: "Không giới hạn" },
      { label: "Hồ sơ sức khoẻ cá nhân", free: false, pro: true, family: true },
      { label: "Nhắc lịch uống thuốc", free: false, pro: true, family: true },
      { label: "Báo cáo sức khoẻ hàng tháng", free: false, pro: false, family: true }
    ]
  },
  {
    category: "Quản lý gia đình",
    features: [
      { label: "Số thành viên", free: "1", pro: "1", family: "Tối đa 6" },
      { label: "Theo dõi sức khoẻ cả nhà", free: false, pro: false, family: true },
      { label: "Cảnh báo sức khoẻ thông minh", free: false, pro: false, family: true }
    ]
  },
  {
    category: "Thiết bị & Đồng bộ",
    features: [
      { label: "Số thiết bị", free: "1", pro: "Không giới hạn", family: "Không giới hạn" },
      { label: "Đồng bộ đa thiết bị", free: false, pro: true, family: true },
      { label: "Ứng dụng di động (iOS & Android)", free: true, pro: true, family: true }
    ]
  },
  {
    category: "Hỗ trợ & Bảo mật",
    features: [
      { label: "Hỗ trợ qua email", free: true, pro: true, family: true },
      { label: "Hỗ trợ ưu tiên 24/7", free: false, pro: true, family: true },
      { label: "Hỗ trợ ưu tiên cao nhất", free: false, pro: false, family: true },
      { label: "Mã hoá dữ liệu end-to-end", free: true, pro: true, family: true }
    ]
  }
];

export function PricingComparison() {
  return (
    <section aria-labelledby="comparison-heading" className="bg-[#F8FAFC] py-16 lg:py-24">
      <div className="container-page">
        <Reveal className="mx-auto max-w-2xl text-center">
          <span className="badge-pill">So sánh chi tiết</span>
          <h2 id="comparison-heading" className="mt-3 text-h1 text-ink-900">
            Tính năng từng gói
          </h2>
          <p className="mt-3 text-body text-ink-600">
            Xem đầy đủ những gì bạn nhận được với mỗi gói dịch vụ.
          </p>
        </Reveal>

        <Reveal delay={150} className="mx-auto mt-12 max-w-5xl">
          {/* Overflow wrapper — horizontal scroll on mobile */}
          <div className="overflow-x-auto rounded-card border border-ink-200 bg-white shadow-soft">
            <table className="w-full min-w-[640px] border-collapse text-sm">
              {/* ── Column headers ── */}
              <thead>
                <tr className="border-b border-ink-200">
                  <th
                    scope="col"
                    className="py-5 pl-6 pr-4 text-left text-base font-semibold text-ink-900 lg:w-[40%]"
                  >
                    Tính năng
                  </th>

                  {/* Free */}
                  <th scope="col" className="px-4 py-5 text-center">
                    <div className="text-base font-semibold text-ink-900">Cơ bản</div>
                    <div className="mt-0.5 text-xs font-medium text-ink-500">Miễn phí</div>
                  </th>

                  {/* Pro — highlighted column */}
                  <th scope="col" className="bg-brand-50/60 px-4 py-5 text-center">
                    <div className="inline-flex items-center gap-1.5 rounded-pill bg-brand-700 px-3 py-1 text-sm font-bold text-white">
                      Pro
                      <span className="rounded-pill bg-white px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-brand-700">
                        Phổ biến
                      </span>
                    </div>
                    <div className="mt-1.5 text-xs font-medium text-ink-500">199.000đ/tháng</div>
                  </th>

                  {/* Family */}
                  <th scope="col" className="px-4 py-5 pr-6 text-center">
                    <div className="text-base font-semibold text-ink-900">Gia đình</div>
                    <div className="mt-0.5 text-xs font-medium text-ink-500">399.000đ/tháng</div>
                  </th>
                </tr>
              </thead>

              <tbody>
                {ROWS.map((row) => (
                  <Fragment key={row.category}>
                    {/* Category header */}
                    <tr className="border-b border-ink-100 bg-ink-100/50">
                      <td
                        colSpan={4}
                        className="py-2.5 pl-6 text-[11px] font-bold uppercase tracking-widest text-ink-600"
                      >
                        {row.category}
                      </td>
                    </tr>

                    {/* Feature rows */}
                    {row.features.map((feat, fi) => (
                      <tr
                        key={feat.label}
                        className={`border-b transition-colors duration-150 hover:bg-brand-50/20 ${
                          fi === row.features.length - 1 ? "border-ink-200" : "border-ink-100"
                        }`}
                      >
                        <td className="py-3.5 pl-6 pr-4 font-medium text-ink-800">
                          {feat.label}
                        </td>
                        <td className="px-4 py-3.5 text-center">
                          <CellValue value={feat.free} />
                        </td>
                        <td className="bg-brand-50/30 px-4 py-3.5 text-center">
                          <CellValue value={feat.pro} highlight />
                        </td>
                        <td className="px-4 py-3.5 pr-6 text-center">
                          <CellValue value={feat.family} />
                        </td>
                      </tr>
                    ))}
                  </Fragment>
                ))}
              </tbody>
            </table>
          </div>
        </Reveal>
      </div>
    </section>
  );
}

function CellValue({
  value,
  highlight = false
}: {
  value: string | boolean;
  highlight?: boolean;
}) {
  if (value === true) {
    return (
      <span
        aria-label="Có"
        className={`inline-grid h-6 w-6 place-items-center rounded-full ${
          highlight ? "bg-brand text-white" : "bg-success-soft text-success"
        }`}
      >
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M5 12l4 4L19 6" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </span>
    );
  }

  if (value === false) {
    return (
      <span
        aria-label="Không có"
        className="inline-grid h-6 w-6 place-items-center rounded-full bg-ink-100 text-ink-300"
      >
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M6 18L18 6M6 6l12 12" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
        </svg>
      </span>
    );
  }

  return (
    <span className={`font-medium ${highlight ? "text-brand-700" : "text-ink-700"}`}>
      {value}
    </span>
  );
}
