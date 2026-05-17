import Link from "next/link";
import { Logo } from "../Logo";

export function Footer() {
  return (
    <footer className="border-t border-ink-200 bg-white">
      <div className="container-page py-12 lg:py-14">
        <div className="grid gap-10 lg:grid-cols-4">
          <div>
            <Logo />
            <p className="mt-4 max-w-sm text-sm text-ink-600">
              MediSign AI — bác sĩ AI đồng hành chăm sóc sức khoẻ cho mọi gia đình Việt.
            </p>
            <div className="mt-4 flex items-center gap-3 text-ink-500">
              <SocialIcon label="Facebook">
                <path d="M14 9h3V6h-3a4 4 0 0 0-4 4v2H7v3h3v6h3v-6h3l1-3h-4v-2a1 1 0 0 1 1-1z" />
              </SocialIcon>
              <SocialIcon label="YouTube">
                <path d="M22 7.5a3 3 0 0 0-2.1-2.1C18.1 5 12 5 12 5s-6.1 0-7.9.4A3 3 0 0 0 2 7.5 31 31 0 0 0 2 12a31 31 0 0 0 0 4.5 3 3 0 0 0 2.1 2.1C5.9 19 12 19 12 19s6.1 0 7.9-.4a3 3 0 0 0 2.1-2.1A31 31 0 0 0 22 12a31 31 0 0 0 0-4.5zM10 15V9l5 3-5 3z" />
              </SocialIcon>
              <SocialIcon label="LinkedIn">
                <path d="M6.94 8.5A1.94 1.94 0 1 1 6.94 4.6a1.94 1.94 0 0 1 0 3.9zM5 10h4v10H5V10zm6 0h3.8v1.4A4.2 4.2 0 0 1 18.4 10c2.7 0 4.6 1.7 4.6 5.2V20h-4v-4.3c0-1.4-.5-2.4-1.8-2.4-1 0-1.6.7-1.9 1.4-.1.2-.1.6-.1.9V20h-4V10z" />
              </SocialIcon>
            </div>
          </div>

          <FooterCol
            title="Về chúng tôi"
            links={[
              { href: "/about", label: "Giới thiệu" },
              { href: "/about#mission", label: "Sứ mệnh" },
              { href: "/about#team", label: "Đội ngũ" }
            ]}
          />
          <FooterCol
            title="Hỗ trợ"
            links={[
              { href: "/support", label: "Trung tâm hỗ trợ" },
              { href: "/support#faq", label: "Câu hỏi thường gặp" },
              { href: "/support#contact", label: "Liên hệ" }
            ]}
          />
          <FooterCol
            title="Tin tức"
            links={[
              { href: "/blog", label: "Blog" },
              { href: "/blog/health", label: "Tin sức khoẻ" },
              { href: "/blog/release", label: "Cập nhật ứng dụng" }
            ]}
          />
        </div>

        <div className="mt-10 flex flex-col items-start justify-between gap-3 border-t border-ink-200 pt-6 text-sm text-ink-500 sm:flex-row sm:items-center">
          <p>© {new Date().getFullYear()} MediSign AI. Bác sĩ AI đồng hành cùng bạn.</p>
          <div className="flex flex-wrap items-center gap-4">
            <Link href="/privacy" className="hover:text-ink-800">Chính sách bảo mật</Link>
            <Link href="/terms" className="hover:text-ink-800">Điều khoản sử dụng</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}

function FooterCol({
  title,
  links
}: {
  title: string;
  links: { href: string; label: string }[];
}) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-ink-900">{title}</h3>
      <ul className="mt-4 space-y-2">
        {links.map((l) => (
          <li key={l.href}>
            <Link href={l.href} className="text-sm text-ink-600 hover:text-brand-700">
              {l.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

function SocialIcon({
  label,
  children
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      className="grid h-10 w-10 place-items-center rounded-pill border border-ink-200 hover:border-brand hover:text-brand cursor-pointer"
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        {children}
      </svg>
    </button>
  );
}
