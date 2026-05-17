import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Bảng giá — MediSign AI",
  description:
    "Chọn gói phù hợp với nhu cầu chăm sóc sức khoẻ của bạn. Bắt đầu miễn phí, nâng cấp bất cứ lúc nào. Không phí ẩn, huỷ dễ dàng.",
  openGraph: {
    title: "Bảng giá — MediSign AI",
    description:
      "Gói Cơ bản miễn phí, Gói Pro 199.000đ/tháng, Gói Gia đình 399.000đ/tháng. Dùng thử 7 ngày miễn phí.",
    type: "website",
    locale: "vi_VN"
  }
};

export default function PricingLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return children;
}
