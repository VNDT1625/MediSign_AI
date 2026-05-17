import Link from "next/link";

const PEOPLE = [
  { name: "Đội ngũ Dev", role: "Sáng lập sản phẩm", initial: "D" },
  { name: "Bác sĩ tư vấn", role: "Đang hợp tác", initial: "B" },
  { name: "Nhà thiết kế", role: "Trải nghiệm người dùng", initial: "N" },
  { name: "AI Researcher", role: "Mô hình & dữ liệu", initial: "A" }
];

export function TeamSection() {
  return (
    <section className="py-20 lg:py-28 bg-white">
      <div className="container-page">
        <div className="mx-auto max-w-2xl text-center">
          <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-700">
            Đội ngũ
          </p>
          <h2 className="text-h1 text-ink-900">Bác sĩ chỉ tay giới thiệu cả nhóm</h2>
          <p className="mt-4 text-body text-ink-600">
            MediSign được xây bởi nhóm kỹ sư Việt Nam và đang hợp tác cùng các chuyên gia y tế.
          </p>
        </div>

        <ul className="mx-auto mt-12 grid max-w-5xl grid-cols-2 gap-5 md:grid-cols-4">
          {PEOPLE.map((p) => (
            <li key={p.name} className="card-soft text-center">
              <div
                aria-hidden="true"
                className="mx-auto mb-4 grid h-20 w-20 place-items-center rounded-pill bg-gradient-to-br from-brand-100 to-accent/20 text-2xl font-bold text-brand-700"
              >
                {p.initial}
              </div>
              <p className="font-semibold text-ink-900">{p.name}</p>
              <p className="mt-1 text-sm text-ink-500">{p.role}</p>
            </li>
          ))}
        </ul>

        <div className="mt-10 flex flex-wrap justify-center gap-3">
          <Link href="/about" className="btn-primary">
            Liên hệ với chúng tôi
          </Link>
          <Link href="/about" className="btn-outline">
            Xem trang giới thiệu
          </Link>
        </div>
      </div>
    </section>
  );
}
