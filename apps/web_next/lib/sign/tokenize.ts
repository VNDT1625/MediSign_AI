/**
 * `lib/sign/tokenize.ts` — chia 1 đoạn tiếng Việt thành chuỗi segments
 * để VslSignVideoPlayer biết clip nào cần phát theo thứ tự.
 *
 * Thuật toán: greedy longest-match trên dictionary có sort theo độ dài
 * phrase giảm dần. Có check word-boundary để tránh match xuyên giữa từ
 * (ví dụ "thầu" KHÔNG match "thuốc" dù chứa subset).
 *
 * Output: mảng segments xen kẽ
 *   - { kind: "video", entry } — đoạn match dictionary, sẽ phát clip.
 *   - { kind: "gap",   text  } — đoạn không match, hiển thị làm phụ đề.
 *
 * Player hiện tại chỉ phát các segment "video"; các "gap" có thể dùng
 * hiển thị transcript strip để người xem theo dõi nội dung tổng.
 */

import { VSL_DICTIONARY, type VslEntry } from "./vslDictionary";

// ---------------------------------------------------------------------------
// Pre-computed sorted dictionary (longest phrase first → greedy match).
// ---------------------------------------------------------------------------

const SORTED_DICTIONARY: ReadonlyArray<VslEntry> = [...VSL_DICTIONARY].sort(
  (a, b) => b.phrase.length - a.phrase.length,
);

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type VslSegment =
  | { kind: "video"; entry: VslEntry }
  | { kind: "gap"; text: string };

// ---------------------------------------------------------------------------
// Word boundary helpers
// ---------------------------------------------------------------------------

/**
 * Ký tự coi là dấu phân cách (whitespace + punctuation thường gặp).
 * KHÔNG dùng `\p{P}` regex Unicode property vì target ES2017 chưa stable.
 */
const SEPARATOR_RE = /[\s.,!?;:'"()[\]/\\\-—–…“”‘’"'`«»]/;

function isAtWordBoundary(text: string, position: number): boolean {
  if (position === 0) return true;
  const prev = text[position - 1];
  return SEPARATOR_RE.test(prev);
}

function isAtWordEnd(text: string, position: number): boolean {
  if (position >= text.length) return true;
  const ch = text[position];
  return SEPARATOR_RE.test(ch);
}

// ---------------------------------------------------------------------------
// Lookup
// ---------------------------------------------------------------------------

/**
 * Tìm entry dài nhất trong dictionary khớp với `lowered` ở vị trí
 * `position`. Trả về entry hoặc `null` nếu không có gì match.
 *
 * `lowered` PHẢI đã `.toLowerCase().normalize("NFC")` để khớp với
 * `phrase` đã chuẩn hoá trong dictionary.
 */
function lookupLongest(lowered: string, position: number): VslEntry | null {
  if (!isAtWordBoundary(lowered, position)) return null;
  for (const entry of SORTED_DICTIONARY) {
    const end = position + entry.phrase.length;
    if (end > lowered.length) continue;
    const slice = lowered.substring(position, end);
    if (slice !== entry.phrase) continue;
    if (!isAtWordEnd(lowered, end)) continue;
    return entry;
  }
  return null;
}

// ---------------------------------------------------------------------------
// Tokenize
// ---------------------------------------------------------------------------

/**
 * Tách `text` thành chuỗi segments để phát VSL.
 *
 * @example
 *   tokenizeForVsl("Bạn bị đau đầu, nên đi khám.")
 *   // [
 *   //   { kind: "gap", text: "Bạn bị" },
 *   //   { kind: "video", entry: { phrase: "đau đầu", … } },
 *   //   { kind: "gap", text: ", nên" },
 *   //   { kind: "video", entry: { phrase: "đi khám", … } },
 *   //   { kind: "gap", text: "." },
 *   // ]
 */
export function tokenizeForVsl(text: string): VslSegment[] {
  const normalized = text.normalize("NFC");
  const lowered = normalized.toLowerCase();
  const segments: VslSegment[] = [];

  let i = 0;
  let gapStart = 0;

  while (i < lowered.length) {
    const match = lookupLongest(lowered, i);
    if (match) {
      // Flush gap text trước match (giữ casing gốc).
      if (gapStart < i) {
        const gap = normalized.substring(gapStart, i).trim();
        if (gap) segments.push({ kind: "gap", text: gap });
      }
      segments.push({ kind: "video", entry: match });
      i += match.phrase.length;
      gapStart = i;
      continue;
    }
    i += 1;
  }

  // Flush trailing gap.
  if (gapStart < lowered.length) {
    const gap = normalized.substring(gapStart).trim();
    if (gap) segments.push({ kind: "gap", text: gap });
  }

  return segments;
}

/**
 * Filter convenience — lấy danh sách video segments để pass vào player.
 */
export function videoSegmentsOnly(segments: VslSegment[]): VslEntry[] {
  return segments
    .filter((s): s is { kind: "video"; entry: VslEntry } => s.kind === "video")
    .map((s) => s.entry);
}
