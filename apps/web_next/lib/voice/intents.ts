/**
 * Intent matcher cho voice command - KHONG goi AI.
 * Tat ca lenh duoc parse local theo regex/keyword tieng Viet (da bo dau).
 */

import { SECTION_NAMES } from "./pageScenarios";

export type IntentKind =
  | "navigate"
  | "scroll"
  | "scroll_section"
  | "page"
  | "ui_search"
  | "ui_click"
  | "ui_submit"
  | "ui_dictate"
  | "ui_clear"
  | "auth_login"
  | "auth_logout"
  | "chat_mode"
  | "elderly_toggle"
  | "font_size"
  | "read_page"
  | "repeat"
  | "help"
  | "close"
  | "stop"
  | "unknown";

export type ScrollDir = "up" | "down" | "top" | "bottom";
export type PageAction = "back" | "forward" | "reload";
export type ChatMode = "text" | "voice" | "click" | "sign";
export type FontDir = "increase" | "decrease" | "reset";

export interface IntentMatch {
  kind: IntentKind;
  target?: string;
  action?: ScrollDir | PageAction;
  label?: string;
  text?: string;
  chatMode?: ChatMode;
  fontDir?: FontDir;
  sectionId?: string;
  reply: string;
  normalized: string;
}

export const WEB_ROUTES: Array<{ keys: string[]; path: string; reply: string }> = [
  { keys: ["trang chu", "home", "trang chinh"], path: "/", reply: "Đang mở trang chủ." },
  { keys: ["chat", "tro chuyen", "hoi bac si", "bac si ai"], path: "/chat", reply: "Đang mở trang chat." },
  { keys: ["bang gia", "gia", "pricing", "goi"], path: "/pricing", reply: "Đang mở bảng giá." },
  { keys: ["gioi thieu", "ve chung toi", "about"], path: "/about", reply: "Đang mở trang giới thiệu." },
  { keys: ["tai ung dung", "tai app", "download"], path: "/download", reply: "Đang mở trang tải ứng dụng." },
];

export function normalize(text: string): string {
  return text
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/đ/gi, "d")
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export const WAKE_WORDS: string[] = [
  "bac si oi",
  "bac sy oi",
  "bacsi oi",
  "bac si",
];

export function containsWakeWord(transcript: string): boolean {
  const norm = normalize(transcript);
  return WAKE_WORDS.some((w) => norm.includes(w));
}

export function stripWakeWord(transcript: string): string {
  const norm = normalize(transcript);
  for (const w of WAKE_WORDS) {
    const i = norm.indexOf(w);
    if (i >= 0) return norm.slice(i + w.length).trim();
  }
  return norm;
}

/** Helper: thay reply chua text theo template "{x}". */
function fmt(template: string, values: Record<string, string>): string {
  return template.replace(/\{(\w+)\}/g, (_, k) => values[k] ?? "");
}

export function matchIntent(rawTranscript: string): IntentMatch {
  const normalized = normalize(rawTranscript);
  const original = rawTranscript.trim();

  if (!normalized) {
    return { kind: "unknown", reply: "Mình chưa nghe rõ, bạn nói lại giúp nhé.", normalized };
  }

  // Stop / close / help
  if (/(dung lai|dung nghe|tat mic|stop)/.test(normalized)) {
    return { kind: "stop", reply: "Đã dừng nghe.", normalized };
  }
  if (/(^|\s)(dong|tat overlay|huy bo)(\s|$)/.test(normalized)) {
    return { kind: "close", reply: "Đã đóng trợ lý giọng nói.", normalized };
  }
  if (/(giup|tro giup|huong dan|lam gi duoc|menu lenh|lenh)/.test(normalized) && !/lenh\s*moi/.test(normalized)) {
    return {
      kind: "help",
      reply:
        'Bạn có thể nói: "mở trang chat", "mở tủ thuốc", "cuộn xuống", "quay lại", "đăng nhập", "gửi", "viết là <nội dung>", "đọc trang", "nói lại", "tăng cỡ chữ", hoặc "chế độ giọng nói".',
      normalized,
    };
  }

  // Repeat
  if (/(noi lai|doc lai|nhac lai|repeat)/.test(normalized)) {
    return { kind: "repeat", reply: "", normalized };
  }

  // Read page
  if (/(doc trang|doc giup|doc noi dung trang|read page)/.test(normalized)) {
    return { kind: "read_page", reply: "Mình đọc nội dung trang.", normalized };
  }

  // Auth
  if (/(dang nhap|login|sign in)/.test(normalized)) {
    return { kind: "auth_login", reply: "Vâng ạ, mình mở trang đăng nhập để hỗ trợ bạn nhé.", normalized };
  }
  if (/(dang xuat|dang xuat ra|logout|sign out|thoat tai khoan)/.test(normalized)) {
    return { kind: "auth_logout", reply: "Đang đăng xuất.", normalized };
  }

  // Chat mode
  const modeMatch = normalized.match(/che do (van ban|text|giong noi|voice|am thanh|chon|click|tap|ngon ngu ky hieu|ky hieu|sign)/);
  if (modeMatch) {
    const m = modeMatch[1];
    const mode: ChatMode = /text|van ban/.test(m)
      ? "text"
      : /voice|giong|am thanh/.test(m)
      ? "voice"
      : /click|chon|tap/.test(m)
      ? "click"
      : "sign";
    const replyMap: Record<ChatMode, string> = {
      text: "Đã chuyển sang chế độ văn bản.",
      voice: "Đã chuyển sang chế độ giọng nói.",
      click: "Đã chuyển sang chế độ chọn nhanh.",
      sign: "Đã chuyển sang chế độ ngôn ngữ ký hiệu.",
    };
    return { kind: "chat_mode", chatMode: mode, reply: replyMap[mode], normalized };
  }

  // Elderly toggle
  if (/(che do nguoi (cao tuoi|gia)|elderly|chu to|man hinh lon)/.test(normalized)) {
    return { kind: "elderly_toggle", reply: "Đã chuyển chế độ thân thiện cho người cao tuổi.", normalized };
  }

  // Font size
  if (/(tang co chu|chu to hon|phong to chu|to chu|increase font)/.test(normalized)) {
    return { kind: "font_size", fontDir: "increase", reply: "Đã tăng cỡ chữ.", normalized };
  }
  if (/(giam co chu|chu nho hon|thu nho chu|nho chu|decrease font)/.test(normalized)) {
    return { kind: "font_size", fontDir: "decrease", reply: "Đã giảm cỡ chữ.", normalized };
  }
  if (/(co chu mac dinh|chu mac dinh|reset font)/.test(normalized)) {
    return { kind: "font_size", fontDir: "reset", reply: "Đã đặt lại cỡ chữ mặc định.", normalized };
  }

  // Page actions
  if (/(quay lai|tro lai|back)/.test(normalized)) {
    return { kind: "page", action: "back", reply: "Quay lại trang trước.", normalized };
  }
  if (/(tien len|forward|di tiep)/.test(normalized)) {
    return { kind: "page", action: "forward", reply: "Tiến tới trang sau.", normalized };
  }
  if (/(tai lai|reload|lam moi)/.test(normalized)) {
    return { kind: "page", action: "reload", reply: "Đang tải lại trang.", normalized };
  }

  // Scroll to named section: "cuon toi bang gia", "cuon toi cach hoat dong"
  const sectionMatch = normalized.match(/cuon (?:toi|den|vao)\s+(?:phan\s+)?(.+)/);
  if (sectionMatch) {
    const sectionName = sectionMatch[1].trim();
    const sectionId = SECTION_NAMES[sectionName];
    if (sectionId) {
      return { kind: "scroll_section", sectionId, reply: `Cuộn tới phần ${sectionName}.`, normalized };
    }
  }

  // Scroll
  if (/len dau trang|ve dau trang|len tren cung/.test(normalized)) {
    return { kind: "scroll", action: "top", reply: "Cuộn lên đầu trang.", normalized };
  }
  if (/cuoi trang|xuong duoi cung|het trang/.test(normalized)) {
    return { kind: "scroll", action: "bottom", reply: "Cuộn xuống cuối trang.", normalized };
  }
  if (/cuon len|keo len|len tren/.test(normalized)) {
    return { kind: "scroll", action: "up", reply: "Cuộn lên.", normalized };
  }
  if (/cuon xuong|keo xuong|xuong duoi/.test(normalized)) {
    return { kind: "scroll", action: "down", reply: "Cuộn xuống.", normalized };
  }

  // Search
  if (/^(tim kiem|tim giup|search)$/.test(normalized) || /^tim$/.test(normalized)) {
    return { kind: "ui_search", reply: "Mình đã chuyển vào ô tìm kiếm.", normalized };
  }

  // Clear input
  if (/(xoa noi dung|xoa o nhap|xoa input|clear)/.test(normalized)) {
    return { kind: "ui_clear", reply: "Đã xóa nội dung ô nhập.", normalized };
  }

  // Submit
  if (/^(gui|gui di|submit|enter|gui tin nhan|hoi)$/.test(normalized)) {
    return { kind: "ui_submit", reply: "Đã gửi.", normalized };
  }

  // Dictation: "viet la <noi dung>" / "ghi la <noi dung>" / "nhap <noi dung>"
  // Lay phan goc co dau de giu nguyen tieng Viet.
  const dictateNorm = normalized.match(/^(?:viet la|ghi la|nhap|nhap noi dung|go la|nhap rang|ghi rang)\s+(.+)$/);
  if (dictateNorm) {
    // Tim cau goc khop voi tail bang cach lay tu sau prefix tieng Viet phu hop
    const m = original.match(/^(?:viết là|ghi là|nhập\s*(?:nội dung|rằng)?|gõ là|ghi rằng)\s+(.+)$/i);
    const text = (m?.[1] ?? dictateNorm[1]).trim();
    return {
      kind: "ui_dictate",
      text,
      reply: fmt('Đã nhập: "{t}".', { t: text.length > 40 ? text.slice(0, 40) + "..." : text }),
      normalized,
    };
  }

  // Navigate
  for (const r of WEB_ROUTES) {
    if (r.keys.some((k) => normalized.includes(k))) {
      return { kind: "navigate", target: r.path, reply: r.reply, normalized };
    }
  }

  // Click <label>
  const clickMatch = normalized.match(/^(?:bam|nhan|click|chon)\s+(?:nut\s+|vao\s+)?(.+)$/);
  if (clickMatch) {
    return {
      kind: "ui_click",
      label: clickMatch[1].trim(),
      reply: fmt("Đang bấm {l}.", { l: clickMatch[1].trim() }),
      normalized,
    };
  }

  return {
    kind: "unknown",
    reply: 'Mình chưa hiểu lệnh đó. Nói "giúp" để xem các lệnh hỗ trợ.',
    normalized,
  };
}
