// Mock data cho trang Chat AI.
// Tách thành module riêng để dễ thay bằng API thật về sau.

export type ConversationItem = {
  id: string;
  title: string;
  time: string;
  active?: boolean;
  unread?: boolean;
};

export const RECENT_CONVERSATIONS: ConversationItem[] = [
  { id: "c1", title: "Viêm họng và ho kéo dài", time: "10:24", active: true, unread: true },
  { id: "c2", title: "Sốt nhẹ và đau đầu", time: "Hôm qua" },
  { id: "c3", title: "Dinh dưỡng cho người lớn tuổi", time: "Hôm qua" },
  { id: "c4", title: "Đau cổ tay khi ấn cây", time: "2 ngày trước" },
  { id: "c5", title: "Tư vấn thuốc cảm cúm", time: "3 ngày trước" },
  { id: "c6", title: "Tập thể dục cho người cao tuổi", time: "5 ngày trước" },
  { id: "c7", title: "Kiểm tra sức khỏe định kỳ", time: "7 ngày trước" }
];

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

// Dữ liệu hội thoại mẫu — nguyên văn theo ảnh thiết kế.
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

export const MESSAGES: ChatMessage[] = [
  {
    id: "m1",
    role: "user",
    kind: "text",
    text: "Chào MediSign AI, tôi bị đau họng và ho khan 2 ngày nay, nuốt vướng và rất khó chịu. Tôi nên làm gì?",
    time: "10:24",
    seen: true
  },
  {
    id: "m2",
    role: "ai",
    kind: "text",
    text: "Chào bạn Minh An, cảm ơn bạn đã chia sẻ về triệu chứng. Dựa trên mô tả ban đầu, đây có thể là viêm họng do virus. Để đánh giá chính xác hơn, bạn có thể cung cấp thêm thông tin:",
    bullets: [
      "Nhiệt độ cơ thể hiện tại là bao nhiêu (°C)?",
      "Có đau đầu, mệt mỏi hoặc nổi hạch cổ không?",
      "Đã sử dụng thuốc hoặc biện pháp nào chưa?",
      "Tiền sử dị ứng hoặc bệnh lý nền (nếu có)?"
    ],
    time: "10:24"
  },
  {
    id: "m3",
    role: "user",
    kind: "text",
    text: "Tôi sốt 37.8°C, hơi mệt, không nổi hạch. Tôi đã ngậm muối ấm. Đây là kết quả X-quang phổi tuần trước.",
    time: "10:27",
    seen: true
  },
  {
    id: "m4",
    role: "user",
    kind: "image",
    file: { name: "Xquang_phoi_07052025.jpg", size: "327 KB" },
    time: "10:27",
    seen: true
  },
  {
    id: "m5",
    role: "ai",
    kind: "analysis",
    intro: "Cảm ơn bạn đã cung cấp thêm thông tin và hình ảnh. Dưới đây là phân tích sơ bộ:",
    assessment: [
      { label: "Nhiệt độ:", value: "37.8°C (sốt nhẹ)" },
      { label: "Triệu chứng:", value: "Đau họng, ho khan, mệt nhẹ" },
      { label: "X-quang phổi:", value: "Không thấy tổn thương rõ ràng, phổi thông khí tốt" }
    ],
    handling: [
      "Nghỉ ngơi, uống nhiều nước ấm.",
      "Có thể dùng Paracetamol nếu sốt cao.",
      "Súc họng bằng nước muối ấm 2–3 lần/ngày.",
      "Theo dõi thêm 1–2 ngày."
    ],
    note: {
      text: "Lưu ý: Đây không phải là chẩn đoán cuối cùng. Nếu sốt cao >38.5°C, khó thở, đau họng kéo dài không đỡ, hãy đi khám sớm.",
      time: "10:30"
    },
    time: "10:30"
  }
];
