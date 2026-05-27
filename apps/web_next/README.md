# MediSign AI — Web (Next.js)

Web client cho MediSign AI. App Router cua Next.js **14.2.33**, TypeScript **5.6.3**,
Tailwind CSS **3.4.14**, React **18.3.1**.

## Chay dev

```bash
cd apps/web_next
npm install
npm run dev
```

Mac dinh o `http://localhost:3000`.

## Cac route hien co

```
apps/web_next/app/
├── page.tsx                # Landing page (/)
├── about/                  # /about
├── chat/                   # /chat (AI chat — public, ho tro voice vi-VN va sign mode)
├── download/               # /download
├── login/                  # /login
├── pricing/                # /pricing
├── profile/                # /profile
├── reset-password/         # /reset-password
└── api/
    ├── auth/login | refresh | logout    # Edge proxy toi backend FastAPI
    └── sign/recognize/                  # Gemini Vision VSL recognizer
```

`middleware.ts` chi de **redirect cleanup** cac URL legacy `/app/*` → `/`,
`/app/chat` → `/chat`, `/app/profile` → `/profile`. Khong con shell `/app/*`
duoc bao ve nua — auth duoc handle phia client (`lib/auth/AuthProvider`).

## Cau truc thu muc

```
apps/web_next/
├── app/                    # App Router pages + API route handlers
├── components/
│   ├── HeroVideo.tsx       # Hero voi video R2 + o chat (text + mic vi-VN)
│   ├── LoginModal.tsx      # Modal dang nhap, dung video login R2 lam backdrop
│   ├── SiteHeader.tsx      # Top nav: Home / Chat / Pricing / About / Download
│   ├── Logo.tsx            # SVG logo
│   ├── auth/               # Form dang nhap / dang ky / reset password
│   ├── chat/               # Chat UI components
│   ├── desktop/, profile/  # Layout desktop + profile editor
│   └── sections/           # Story / Platforms / Security / Pricing / Team / ...
├── lib/
│   ├── auth/               # AuthProvider, tokenStore, fetcher
│   ├── api/                # Backend API client wrappers
│   ├── hooks/              # React hooks chia se
│   ├── query/              # TanStack Query setup
│   ├── sign/               # VSL parser + recognizer client
│   ├── utils/              # Utilities chung
│   ├── validation/         # Zod schemas
│   ├── voice/              # Speech recognition (vi-VN)
│   └── vsl/                # Vietnamese Sign Language helpers
├── tailwind.config.ts      # Tokens: brand #0284C7, accent #F97316, success #22C55E
├── next.config.mjs         # Cho phep load asset tu R2 (pub-9e85...r2.dev)
└── tsconfig.json
```

## Asset

- `Hero idle video`: pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev/kling_20260516_作品_The_doctor_3654_0.mp4
- `Login video`: pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev/kling_20260516_作品_The_camera_4212_0%20(1).mp4
- Cac phan con lai dung `PlaceholderVisual` cho den khi co du anh.

## Tuan thu design system

Tham chieu `docs/design UI/Web/MediSign_AI_UI_Web_Final.md` va
`design-system/medisign-ai/MASTER.md`. Quy uoc:
- Cau truc 60 / 30 / 10 (trang / xanh bien / cam)
- Font Inter, hero `clamp(40px, 6vw, 64px)`
- Touch target ≥ 44px, focus ring 3px mau cam, AAA contrast
- `prefers-reduced-motion` duoc ton trong (CSS reset)

## Tests

| Loai | Tool | Cau lenh |
| --- | --- | --- |
| Unit / component | Vitest 3 + Testing Library + MSW 2 | `npm run test:run` |
| Property-based | fast-check | `npm run test:property` |
| E2E | Playwright | `npm run e2e` |
| Coverage | Vitest v8 | `npm run test:coverage` |
