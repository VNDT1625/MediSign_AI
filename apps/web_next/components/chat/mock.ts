// Mock data cho trang Chat AI.
// Tách thành module riêng để dễ thay bằng API thật về sau.

export type ConversationItem = {
  id: string;
  title: string;
  time: string;
  active?: boolean;
  unread?: boolean;
};

export const RECENT_CONVERSATIONS: ConversationItem[] = [];

export type CommMode = "text" | "voice" | "click" | "sign";

export const COMM_MODES: { id: CommMode; label: string }[] = [
  { id: "text", label: "Text" },
  { id: "voice", label: "Voice" },
  { id: "click", label: "Click" },
  { id: "sign", label: "Ký hiệu" }
];

export type Suggestion = {
  id: string;
  icon: "bell" | "apple" | "run" | "hospital";
  label: string;
};

export const NEXT_SUGGESTIONS: Suggestion[] = [
  { id: "s1", icon: "bell", label: "Lịch uống thuốc nhắc nhở" },
  { id: "s2", icon: "apple", label: "Thực phẩm nên ăn khi viêm họng" },
  { id: "s3", icon: "run", label: "Bài tập thở giúp giảm ho" },
  { id: "s4", icon: "hospital", label: "Khi nào cần đi khám ngay?" }
];

export type Attachment = {
  id: string;
  name: string;
  size: string;
  kind: "jpg" | "pdf" | "png";
};

export const ATTACHMENTS: Attachment[] = [
  { id: "a1", name: "Xquang_phoi_07052025.jpg", size: "327 KB", kind: "jpg" },
  { id: "a2", name: "Công thức nấu nước gừng.pdf", size: "128 KB", kind: "pdf" }
];

export type QuickReply = { id: string; icon: "hospital" | "home" | "stethoscope"; label: string };

export const QUICK_REPLIES: QuickReply[] = [
  { id: "q1", icon: "hospital", label: "Viêm họng do virus là gì?" },
  { id: "q2", icon: "home", label: "Cách chăm sóc tại nhà?" },
  { id: "q3", icon: "stethoscope", label: "Khi nào cần đi khám?" }
];

export type ChatMessage =
  | {
      id: string;
      role: "user";
      kind: "text";
      text: string;
      time: string;
      seen?: boolean;
    }
  | {
      id: string;
      role: "user";
      kind: "image";
      file: { name: string; size: string };
      time: string;
      seen?: boolean;
    }
  | {
      id: string;
      role: "ai";
      kind: "text";
      text: string;
      bullets?: string[];
      time: string;
    }
  | {
      id: string;
      role: "ai";
      kind: "analysis";
      intro: string;
      assessment: { label: string; value: string }[];
      handling: string[];
      note: { text: string; time: string };
      time: string;
    };

export const MESSAGES: ChatMessage[] = [];

// ---------------------------------------------------------------------------
// BODY_REGIONS — dùng cho ClickMode: bản đồ vùng cơ thể trên SVG/3D model.
// Mỗi region được click → có 3 mức nhẹ/vừa/nặng (multi-select). Khi user
// bấm "Gửi", composer ghép 1 câu tiếng Việt rồi gọi /ai/chat như text bình
// thường, không cần backend mới.
// ---------------------------------------------------------------------------

export type BodyRegionId =
  | "head"
  | "throat"
  | "chest"
  | "abdomen"
  | "back"
  | "arm_left"
  | "arm_right"
  | "leg_left"
  | "leg_right";

export type BodyRegion = {
  id: BodyRegionId;
  /** Tên hiển thị tiếng Việt. */
  label: string;
  /** Cụm dùng trong câu gửi AI. Ví dụ: "đầu", "ngực". */
  phrase: string;
};

export const BODY_REGIONS: BodyRegion[] = [
  { id: "head",      label: "Đầu",        phrase: "đầu" },
  { id: "throat",    label: "Cổ / họng",  phrase: "cổ và họng" },
  { id: "chest",     label: "Ngực",       phrase: "ngực" },
  { id: "abdomen",   label: "Bụng",       phrase: "bụng" },
  { id: "back",      label: "Lưng",       phrase: "lưng" },
  { id: "arm_left",  label: "Tay trái",   phrase: "tay trái" },
  { id: "arm_right", label: "Tay phải",   phrase: "tay phải" },
  { id: "leg_left",  label: "Chân trái",  phrase: "chân trái" },
  { id: "leg_right", label: "Chân phải",  phrase: "chân phải" }
];

export type PainLevel = "mild" | "moderate" | "severe";

export const PAIN_LEVELS: { id: PainLevel; label: string; phrase: string }[] = [
  { id: "mild",     label: "Nhẹ",  phrase: "nhẹ" },
  { id: "moderate", label: "Vừa", phrase: "vừa" },
  { id: "severe",   label: "Nặng", phrase: "nặng" }
];

// ---------------------------------------------------------------------------
// SIGN_PHRASES — dùng cho SignMode khi user chưa có model nhận diện video
// VSL. Người câm/điếc chạm vào nút phrase để ghép thành câu, rồi gửi.
// Khi có model VSL thật, frames camera sẽ được gửi qua WebSocket; bộ phrase
// dưới đây vẫn dùng làm fallback.
// ---------------------------------------------------------------------------

export type SignPhrase = { id: string; label: string; text: string };

export const SIGN_PHRASES: SignPhrase[] = [
  { id: "fever",    label: "Sốt",       text: "Tôi bị sốt" },
  { id: "headache", label: "Đau đầu",   text: "Tôi bị đau đầu" },
  { id: "cough",    label: "Ho",        text: "Tôi bị ho" },
  { id: "sore",     label: "Đau họng",  text: "Tôi bị đau họng" },
  { id: "stomach",  label: "Đau bụng",  text: "Tôi bị đau bụng" },
  { id: "chest",    label: "Đau ngực",  text: "Tôi bị đau ngực" },
  { id: "mild",     label: "Nhẹ",       text: "ở mức nhẹ" },
  { id: "severe",   label: "Nặng",      text: "ở mức nặng" },
  { id: "today",    label: "Hôm nay",   text: "từ hôm nay" },
  { id: "2days",    label: "2 ngày",    text: "khoảng 2 ngày" },
  { id: "advice",   label: "Lời khuyên", text: "Tôi cần lời khuyên" },
  { id: "doctor",   label: "Đi khám",   text: "Tôi nên đi khám không?" }
];

// ---------------------------------------------------------------------------
// OUTPUT_MODES — cách AI trả lời lại user (độc lập với CommMode = input).
// Chỉ có 3 giá trị; mặc định mirror theo input. Cho phép kết hợp như:
//   • input "voice" + output "text" (nói nhưng đọc câu trả lời thay vì nghe)
//   • input "click" + output "sign"  (chọn vùng đau, xem avatar diễn ký hiệu)
// ---------------------------------------------------------------------------

export type OutputMode = "text" | "voice" | "sign";

export const OUTPUT_MODES: { id: OutputMode; label: string; hint: string }[] = [
  { id: "text",  label: "Văn bản",  hint: "Bubble chữ và bullets như thông thường." },
  { id: "voice", label: "Đọc to",   hint: "Tự đọc câu trả lời bằng giọng tiếng Việt." },
  { id: "sign",  label: "Ký hiệu",  hint: "Avatar diễn lại ý chính bằng ngôn ngữ ký hiệu." }
];

/** Mặc định mirror input → output gần nhất có thể. Click không có output riêng → text. */
export function defaultOutputFor(mode: CommMode): OutputMode {
  if (mode === "voice") return "voice";
  if (mode === "sign") return "sign";
  return "text"; // text & click
}
