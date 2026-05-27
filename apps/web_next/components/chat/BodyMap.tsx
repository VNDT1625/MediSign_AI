"use client";

// BodyMap — SVG đơn giản hình người (front view) để user click vào vùng đau.
// Mỗi vùng là 1 path/circle có id thuộc BODY_REGIONS. Click toggle multi-select.
//
// 3D EXTENSION: Khi sẵn sàng cắm 3D, thay component này bằng <Canvas> của
// react-three-fiber với một GLTF body. Interface (props selected/onToggle)
// giữ nguyên, ChatMain không cần đổi.

import type { BodyRegionId } from "./mock";

type BodyMapProps = {
  selected: Set<BodyRegionId>;
  onToggle: (id: BodyRegionId) => void;
  /** Bật chữ to / vùng to hơn cho người cao tuổi. */
  elderly?: boolean;
};

const REGION_FILL_ACTIVE = "#dc2626";   // rose-600
const REGION_FILL_HOVER = "#f87171";    // rose-400
const REGION_FILL_IDLE = "#cbd5e1";     // slate-300

export function BodyMap({ selected, onToggle, elderly = false }: BodyMapProps) {
  const isOn = (id: BodyRegionId) => selected.has(id);

  function regionProps(id: BodyRegionId, label: string) {
    const active = isOn(id);
    return {
      role: "button",
      tabIndex: 0,
      "aria-pressed": active,
      "aria-label": label + (active ? " (đã chọn)" : ""),
      onClick: () => onToggle(id),
      onKeyDown: (e: React.KeyboardEvent) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onToggle(id);
        }
      },
      style: {
        fill: active ? REGION_FILL_ACTIVE : REGION_FILL_IDLE,
        cursor: "pointer",
        transition: "fill 0.15s",
        outline: "none"
      } as React.CSSProperties,
      onPointerEnter: (e: React.PointerEvent<SVGElement>) => {
        if (!active) (e.currentTarget as SVGElement).style.fill = REGION_FILL_HOVER;
      },
      onPointerLeave: (e: React.PointerEvent<SVGElement>) => {
        if (!active) (e.currentTarget as SVGElement).style.fill = REGION_FILL_IDLE;
      }
    };
  }

  return (
    <svg
      viewBox="0 0 200 400"
      role="img"
      aria-label="Bản đồ cơ thể, chạm vào vùng bị đau"
      className={`mx-auto block ${elderly ? "h-[360px]" : "h-[300px]"} w-auto`}
    >
      {/* Đầu */}
      <circle cx="100" cy="40" r="28" {...regionProps("head", "Đầu")} />

      {/* Cổ / họng */}
      <rect x="86" y="66" width="28" height="20" rx="4" {...regionProps("throat", "Cổ và họng")} />

      {/* Ngực */}
      <rect x="64" y="86" width="72" height="60" rx="14" {...regionProps("chest", "Ngực")} />

      {/* Bụng */}
      <rect x="68" y="146" width="64" height="60" rx="12" {...regionProps("abdomen", "Bụng")} />

      {/* Lưng — nửa dưới mờ phía sau, hiển thị bằng dải bên */}
      <rect x="58" y="86" width="6" height="120" rx="3" {...regionProps("back", "Lưng")} />
      <rect x="136" y="86" width="6" height="120" rx="3" {...regionProps("back", "Lưng")} />

      {/* Tay trái */}
      <rect x="36" y="90" width="22" height="120" rx="11" {...regionProps("arm_left", "Tay trái")} />

      {/* Tay phải */}
      <rect x="142" y="90" width="22" height="120" rx="11" {...regionProps("arm_right", "Tay phải")} />

      {/* Chân trái */}
      <rect x="74" y="206" width="22" height="160" rx="11" {...regionProps("leg_left", "Chân trái")} />

      {/* Chân phải */}
      <rect x="104" y="206" width="22" height="160" rx="11" {...regionProps("leg_right", "Chân phải")} />
    </svg>
  );
}
