/**
 * TranscriptCorrector — sửa lỗi nhận dạng STT tiếng Việt trước khi
 * gọi Intent_Matcher. Sử dụng exact match + Levenshtein fuzzy matching
 * trên normalized strings.
 *
 * Pipeline:
 *   raw transcript → normalize() → exact lookup → fuzzy (≤ 2) → original
 *
 * Idempotent: correct(correct(x)) === correct(x) (Property 13).
 *
 * Validates: Requirements 4.1–4.7
 */

import { normalize } from "./intents";

/** Từ điển ánh xạ: chuỗi sai (normalized) → chuỗi đúng (có dấu). */
export const FUZZY_DICTIONARY: Record<string, string> = {
  // Scroll commands — `cuộn xuống` thường bị nhận thành `cũng xuống`, `cuốn xuống`, ...
  "cung xuon": "cuộn xuống",
  "cung xuong": "cuộn xuống",
  "cuon suong": "cuộn xuống",
  "cuon xong": "cuộn xuống",
  "cuon xuong": "cuộn xuống",
  "cuong xuong": "cuộn xuống",
  "kuon xuong": "cuộn xuống",
  "cuon len": "cuộn lên",
  "cung len": "cuộn lên",
  "keo xuong": "kéo xuống",
  "keo len": "kéo lên",
  "len dau trang": "lên đầu trang",
  "ve dau trang": "về đầu trang",
  "cuoi trang": "cuối trang",

  // Auth commands
  "dang nhap": "đăng nhập",
  "dan nhap": "đăng nhập",
  "dang xuat": "đăng xuất",
  "dan xuat": "đăng xuất",
  "dang ki": "đăng ký",
  "dang ky": "đăng ký",

  // Navigation
  "mo trang chu": "mở trang chủ",
  "mo chat": "mở chat",
  "mo tu thuoc": "mở tủ thuốc",
  "mo ho so": "mở hồ sơ",
  "mo bang gia": "mở bảng giá",

  // UI commands
  "gui di": "gửi đi",
  "gui tin nhan": "gửi tin nhắn",
  "xoa noi dung": "xóa nội dung",
  "doc trang": "đọc trang",
  "noi lai": "nói lại",
  "tang co chu": "tăng cỡ chữ",
  "giam co chu": "giảm cỡ chữ",

  // Wake word
  "bac si oi": "bác sĩ ơi",
  "bac sy oi": "bác sĩ ơi",
  "bac si": "bác sĩ",
  "bacsi oi": "bác sĩ ơi",

  // Stop
  "dung lai": "dừng lại",
  "dung nghe": "dừng nghe",
};

/**
 * Tính khoảng cách Levenshtein giữa hai chuỗi.
 * Pure function, dynamic programming O(m*n).
 */
export function levenshteinDistance(a: string, b: string): number {
  const m = a.length;
  const n = b.length;
  if (m === 0) return n;
  if (n === 0) return m;

  // Sử dụng 2 row thay vì full matrix để tiết kiệm memory.
  let prev = new Array<number>(n + 1);
  let curr = new Array<number>(n + 1);
  for (let j = 0; j <= n; j++) prev[j] = j;

  for (let i = 1; i <= m; i++) {
    curr[0] = i;
    for (let j = 1; j <= n; j++) {
      if (a[i - 1] === b[j - 1]) {
        curr[j] = prev[j - 1];
      } else {
        curr[j] = 1 + Math.min(prev[j], curr[j - 1], prev[j - 1]);
      }
    }
    [prev, curr] = [curr, prev];
  }
  return prev[n];
}

/**
 * Sửa transcript bị nhận dạng sai.
 * 1. Trim và normalize input.
 * 2. Exact match trong FUZZY_DICTIONARY.
 * 3. Fuzzy match (Levenshtein ≤ 2) nếu không có exact match.
 * 4. Trả về chuỗi gốc nếu không tìm được match.
 *
 * Idempotent: correct(correct(x)) === correct(x).
 */
export function correct(transcript: string): string {
  if (!transcript || !transcript.trim()) return transcript;

  const norm = normalize(transcript);

  // 1. Exact match
  if (norm in FUZZY_DICTIONARY) {
    return FUZZY_DICTIONARY[norm];
  }

  // 2. Substring match: nếu transcript chứa key dictionary, thay thế phần đó.
  // Hữu ích khi user nói thêm từ phụ ("cũng xuống đi" → "cuộn xuống đi").
  for (const key of Object.keys(FUZZY_DICTIONARY)) {
    // Chỉ match key có ≥ 2 từ để tránh false positive trên 1 ký tự
    if (key.split(" ").length >= 2 && norm.includes(key)) {
      return transcript.replace(
        new RegExp(escapeRegex(key), "i"),
        FUZZY_DICTIONARY[key]
      );
    }
  }

  // 3. Fuzzy match toàn chuỗi (Levenshtein ≤ 2)
  const MAX_DISTANCE = 2;
  let bestMatch: string | null = null;
  let bestDist = MAX_DISTANCE + 1;

  for (const key of Object.keys(FUZZY_DICTIONARY)) {
    // Chỉ fuzzy match nếu length tương đồng (tránh "len" matches "cuon")
    if (Math.abs(key.length - norm.length) > MAX_DISTANCE) continue;
    const dist = levenshteinDistance(norm, key);
    if (dist <= MAX_DISTANCE && dist < bestDist) {
      bestDist = dist;
      bestMatch = key;
    }
  }

  if (bestMatch !== null) {
    return FUZZY_DICTIONARY[bestMatch];
  }

  // 4. No match — trả về nguyên bản (giữ dấu).
  return transcript;
}

/** Escape regex special chars để dùng trong RegExp constructor. */
function escapeRegex(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
