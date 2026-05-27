"use client";

// SignAvatar — placeholder cho avatar 3D sẽ "diễn" lại câu trả lời của AI
// bằng ngôn ngữ ký hiệu Việt (VSL).
//
// PHASE HIỆN TẠI (chưa có asset 3D):
//   • Hiển thị một khung lớn với 1 emoji-icon "đại diện" + dòng chữ phụ to.
//   • Đủ để người câm/điếc nắm ý chính (gọi 115 / đi khám / nghỉ ngơi / uống thuốc).
//
// PHASE 3D (khi có asset):
//   • Thay nội dung trong <div data-stage> bằng <Canvas> react-three-fiber.
//   • Load GLTF avatar + animation pre-recorded theo `intent`.
//   • Subtitle bên dưới giữ nguyên cho accessibility.
//
// Interface giữ nguyên, ChatMain không cần đổi.

export type SignIntent =
  | "rest_drink_water"
  | "see_doctor"
  | "call_115"
  | "take_medicine"
  | "ok_safe"
  | "warn_followup"
  | "info";

const INTENT_DATA: Record<SignIntent, { emoji: string; subtitle: string; tone: string }> = {
  rest_drink_water: { emoji: "🛌💧", subtitle: "Nghỉ ngơi và uống nước",            tone: "border-emerald-200 bg-emerald-50 text-emerald-900" },
  see_doctor:       { emoji: "🩺",   subtitle: "Đến gặp bác sĩ",                    tone: "border-amber-300 bg-amber-50 text-amber-900" },
  call_115:         { emoji: "🚑",   subtitle: "Gọi cấp cứu 115 ngay",              tone: "border-rose-300 bg-rose-50 text-rose-900" },
  take_medicine:    { emoji: "💊",   subtitle: "Uống thuốc theo hướng dẫn",         tone: "border-blue-200 bg-blue-50 text-blue-900" },
  ok_safe:          { emoji: "✅",   subtitle: "Triệu chứng nhẹ, có thể tự theo dõi", tone: "border-emerald-200 bg-emerald-50 text-emerald-900" },
  warn_followup:    { emoji: "⚠️",   subtitle: "Cẩn thận theo dõi tiếp",            tone: "border-amber-300 bg-amber-50 text-amber-900" },
  info:             { emoji: "ℹ️",   subtitle: "AI đã có thông tin cho bạn",        tone: "border-blue-200 bg-blue-50 text-blue-900" }
};

/**
 * Heuristic suy ra `SignIntent` từ text trả về của AI. Khi backend trả về
 * intent chính thức, gọi `<SignAvatar intent={response.intent}>` thay vì gọi
 * `intentFromText`.
 */
export function intentFromText(text: string): SignIntent {
  const lower = text.toLowerCase();
  if (/(cấp cứu|115|khó thở nặng|mất ý thức|nguy hiểm|gấp khẩn)/.test(lower)) return "call_115";
  if (/(đi khám|gặp bác sĩ|bệnh viện|cơ sở y tế)/.test(lower)) return "see_doctor";
  if (/(uống thuốc|paracetamol|liều dùng)/.test(lower)) return "take_medicine";
  if (/(nghỉ ngơi|uống nước|súc họng|tự chăm sóc)/.test(lower)) return "rest_drink_water";
  if (/(nhẹ|ổn định|bình thường|không nguy hiểm)/.test(lower)) return "ok_safe";
  if (/(theo dõi|tái khám)/.test(lower)) return "warn_followup";
  return "info";
}

type SignAvatarProps = {
  intent: SignIntent;
  /** Bật chữ to. */
  elderly?: boolean;
};

export function SignAvatar({ intent, elderly = false }: SignAvatarProps) {
  const data = INTENT_DATA[intent];
  return (
    <div className={`flex w-full max-w-[420px] flex-col items-center gap-3 rounded-3xl border-2 px-4 py-4 shadow-soft ${data.tone}`}>
      <div
        data-stage
        className="flex aspect-video w-full items-center justify-center rounded-2xl bg-white"
        aria-label={"Avatar ký hiệu: " + data.subtitle}
      >
        {/* TODO(3D): thay khối này bằng <Canvas> react-three-fiber + GLTF khi có asset. */}
        <span aria-hidden className="text-[88px] leading-none">{data.emoji}</span>
      </div>
      <p className={`${elderly ? "text-[22px] leading-8" : "text-[18px] leading-7"} text-center font-bold`}>
        {data.subtitle}
      </p>
    </div>
  );
}
