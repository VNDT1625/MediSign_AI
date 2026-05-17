// Bộ icon SVG dùng riêng cho trang Chat AI.
// Style đồng bộ Lucide (stroke 1.8, line-cap round) — đáp ứng quy tắc UI:
// "Không dùng emoji làm icon, kích thước/viewBox nhất quán".

import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement> & { size?: number };

function base({ size = 20, ...rest }: IconProps) {
  return {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.8,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true,
    ...rest
  };
}

export const PlusIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M12 5v14M5 12h14" />
  </svg>
);

export const SearchIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <circle cx="11" cy="11" r="7" />
    <path d="m20 20-3.5-3.5" />
  </svg>
);

export const HistoryIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M3 12a9 9 0 1 0 3-6.7L3 8" />
    <path d="M3 3v5h5" />
    <path d="M12 7v5l3 2" />
  </svg>
);

export const MoreIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <circle cx="12" cy="6" r="1.4" />
    <circle cx="12" cy="12" r="1.4" />
    <circle cx="12" cy="18" r="1.4" />
  </svg>
);

export const ChevronUpIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="m6 15 6-6 6 6" />
  </svg>
);

export const ChevronDownIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="m6 9 6 6 6-6" />
  </svg>
);

export const ChevronRightIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="m9 6 6 6-6 6" />
  </svg>
);

export const CheckIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="m5 13 4 4L19 7" />
  </svg>
);

export const DoubleCheckIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="m2 13 4 4 9-9" />
    <path d="m9 17 9-10" />
  </svg>
);

export const TextIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M4 7h16" />
    <path d="M9 7v13" />
    <path d="M7 12h10" />
  </svg>
);

export const VoiceIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M5 11v2" />
    <path d="M9 8v8" />
    <path d="M13 5v14" />
    <path d="M17 9v6" />
    <path d="M21 11v2" />
  </svg>
);

export const ClickIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M9 4v8" />
    <path d="m6 9 3 3 3-3" />
    <path d="M15 12v6a3 3 0 0 1-6 0" />
  </svg>
);

export const SignIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M9 11V5a1.5 1.5 0 0 1 3 0v5" />
    <path d="M12 5V3.5a1.5 1.5 0 0 1 3 0V10" />
    <path d="M15 6.5a1.5 1.5 0 0 1 3 0V13" />
    <path d="M6 11.5a1.5 1.5 0 0 1 3 0V14l-2-1.5" />
    <path d="M6 12.5c0 5 3 8.5 7 8.5s5-3 5-7" />
  </svg>
);

export const SettingsIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3h0a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8v0a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z" />
  </svg>
);

export const HelpIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <circle cx="12" cy="12" r="9" />
    <path d="M9.5 9a2.5 2.5 0 0 1 5 0c0 1.5-2.5 2-2.5 4" />
    <path d="M12 17h.01" />
  </svg>
);

export const FontSizeIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M4 19V8a3 3 0 0 1 6 0v11" />
    <path d="M4 14h6" />
    <path d="M14 19v-7a2 2 0 0 1 4 0v7" />
    <path d="M14 16h4" />
  </svg>
);

export const SoulIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M12 21s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 11c0 5.5-7 10-7 10Z" />
  </svg>
);

export const PillIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <rect x="2" y="9" width="20" height="6" rx="3" />
    <path d="M12 9v6" />
  </svg>
);

export const ShieldCheckIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6l-8-3Z" />
    <path d="m9 12 2 2 4-4" />
  </svg>
);

export const VerifiedIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="m12 2 2.4 2 3.1-.4.4 3.1L20 9l-2 2.4.4 3.1-3.1.4L12 17l-2.4-2-3.1.4-.4-3.1L4 9l2-2.4L5.6 3.5l3.1-.4L12 2Z" />
    <path d="m9 11 2 2 4-4" />
  </svg>
);

export const InfoIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 8h.01" />
    <path d="M11 12h1v5h1" />
  </svg>
);

export const PaperclipIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M21 12.5 12.5 21a5 5 0 0 1-7-7L14 5.5a3.5 3.5 0 0 1 5 5L10.5 19a2 2 0 0 1-3-3l8-8" />
  </svg>
);

export const ImageIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <rect x="3" y="3" width="18" height="18" rx="2" />
    <circle cx="9" cy="9" r="1.6" />
    <path d="m21 15-5-5L5 21" />
  </svg>
);

export const SmileIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <circle cx="12" cy="12" r="9" />
    <path d="M9 14c.8 1 1.8 1.5 3 1.5s2.2-.5 3-1.5" />
    <path d="M9 9h.01" />
    <path d="M15 9h.01" />
  </svg>
);

export const MicIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <rect x="9" y="3" width="6" height="11" rx="3" />
    <path d="M5 11a7 7 0 0 0 14 0" />
    <path d="M12 18v3" />
  </svg>
);

export const SendIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="m4 12 16-8-7 16-2-7-7-1Z" />
  </svg>
);

export const DownloadIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M12 4v12" />
    <path d="m7 11 5 5 5-5" />
    <path d="M5 20h14" />
  </svg>
);

export const FileImageIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5Z" />
    <path d="M14 3v5h5" />
    <circle cx="10" cy="13" r="1.4" />
    <path d="m7 18 3-3 5 4" />
  </svg>
);

export const FilePdfIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5Z" />
    <path d="M14 3v5h5" />
    <path d="M9 14h1a1.5 1.5 0 0 1 0 3H9v-3Z" />
    <path d="M9 17v2" />
    <path d="M14 14v5" />
    <path d="M14 14h2" />
    <path d="M14 16.5h1.5" />
  </svg>
);

export const BellIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M6 8a6 6 0 0 1 12 0c0 7 3 8 3 8H3s3-1 3-8" />
    <path d="M10 21a2 2 0 0 0 4 0" />
  </svg>
);

export const AppleIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M12 7c-1-2-3-3-5-2 0 2 1 4 3 5" />
    <path d="M19 14c0-3-2-5-5-5-1 0-2 .5-2 1-1-.5-2-1-3-1-3 0-5 2-5 6 0 4 3 7 5 7 1 0 2-.5 3-1 1 .5 2 1 3 1 2 0 4-3 4-5" />
  </svg>
);

export const HospitalIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M4 21V8l8-5 8 5v13" />
    <path d="M12 12v5" />
    <path d="M9.5 14.5h5" />
    <path d="M9 21v-4h6v4" />
  </svg>
);

export const HomeIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M4 11 12 4l8 7" />
    <path d="M6 10v10h12V10" />
  </svg>
);

export const StethoscopeIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M5 4v6a4 4 0 0 0 8 0V4" />
    <path d="M5 4h2" />
    <path d="M11 4h2" />
    <path d="M9 14v2a4 4 0 0 0 8 0v-1" />
    <circle cx="17" cy="13" r="2" />
  </svg>
);

export const RunIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <circle cx="14" cy="5" r="2" />
    <path d="m9 21 2-6-4-3 3-5 4 3 4-1" />
    <path d="m13 11 2 4 4 1" />
  </svg>
);

export const AppleNutritionIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M12 8c-2-3-5-3-7-1-2 3 0 9 3 11 1 .7 2 1 3 1s2-.3 3-1c3-2 5-8 3-11-2-2-5-2-7 1Z" />
    <path d="M12 8c0-2 1-4 3-5" />
  </svg>
);
