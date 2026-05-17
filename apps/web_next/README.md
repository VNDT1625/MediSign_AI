# MediSign AI — Web (Next.js)

Web client cho MediSign AI. App Router của Next.js 14, TypeScript, Tailwind CSS.

## Chạy dev

```bash
cd apps/web_next
npm install
npm run dev
```

Mặc định ở `http://localhost:3000`.

## Cấu trúc

```
apps/web_next/
├── app/
│   ├── layout.tsx        # Layout gốc, font Inter, skip link
│   ├── page.tsx          # Trang Home
│   └── globals.css       # Tailwind + design tokens (clamp typography, btn classes)
├── components/
│   ├── HeroVideo.tsx     # Hero với video R2 + ô chat (text + mic vi-VN)
│   ├── LoginModal.tsx    # Modal đăng nhập, dùng video login R2 làm backdrop
│   ├── SiteHeader.tsx    # Top nav: Home / Chat / Pricing / About / Download
│   ├── Logo.tsx          # SVG logo
│   └── sections/         # Story / Platforms / Security / Pricing / Team / ...
├── tailwind.config.ts    # Tokens: brand #0284C7, accent #F97316, success #22C55E
├── next.config.mjs       # Cho phép load asset từ R2 (pub-9e85...r2.dev)
└── tsconfig.json
```

## Asset

- `Hero idle video`: pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev/kling_20260516_作品_The_doctor_3654_0.mp4
- `Login video`: pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev/kling_20260516_作品_The_camera_4212_0%20(1).mp4
- Các phần còn lại dùng `PlaceholderVisual` cho đến khi có đủ ảnh.

## Tuân thủ design system

Tham chiếu `docs/design UI/Web/MediSign_AI_UI_Web_Final.md` và `design-system/medisign-ai/MASTER.md`. Quy ước:
- Cấu trúc 60 / 30 / 10 (trắng / xanh biển / cam)
- Font Inter, hero `clamp(40px, 6vw, 64px)`
- Touch target ≥ 44px, focus ring 3px màu cam, AAA contrast
- `prefers-reduced-motion` được tôn trọng (CSS reset)
