/**
 * `lib/sign/vslDictionary.ts` — bảng tra từ/cụm từ tiếng Việt → clip VSL.
 *
 * Phase 1: dictionary thủ công, khớp 14 clip có sẵn trong `public/signs/`.
 *
 * Quy tắc mở rộng dữ liệu (Phase 2 — khi quay thêm clip):
 *   1. Thêm clip mới vào `apps/web_next/public/signs/<slug>.webm`.
 *   2. Khai báo 1 entry trong `VSL_DICTIONARY` bên dưới với `phrase`
 *      VIẾT THƯỜNG, có dấu, đúng chính tả tiếng Việt.
 *   3. Các alias (cụm đồng nghĩa cùng dùng 1 clip) — thêm entry trỏ
 *      cùng `src`. Ví dụ "cấp cứu" và "khẩn cấp".
 *
 * Tokenizer (`tokenize.ts`) tự sort theo độ dài phrase giảm dần để
 * "đau đầu" luôn được match trước "đau"; dictionary này KHÔNG cần sort
 * thủ công.
 */

export type VslEntry = {
  /** Cụm tiếng Việt CHUẨN HÓA (NFC, viết thường, có dấu). */
  phrase: string;
  /** Đường dẫn clip tương đối, sẽ resolve qua public/. */
  src: string;
  /** Nhãn hiển thị trên pill (có thể viết hoa chữ đầu). */
  label: string;
};

export const VSL_DICTIONARY: VslEntry[] = [
  // ─── Cụm 2 từ ưu tiên (dài hơn, tokenizer match trước) ────────────
  { phrase: "khẩn cấp",  src: "/signs/khan_cap.webm",  label: "Khẩn cấp" },
  { phrase: "cấp cứu",   src: "/signs/khan_cap.webm",  label: "Khẩn cấp" }, // alias
  { phrase: "đau đầu",   src: "/signs/dau_dau.webm",   label: "Đau đầu" },
  { phrase: "nhức đầu",  src: "/signs/dau_dau.webm",   label: "Đau đầu" }, // alias
  { phrase: "đi khám",   src: "/signs/di_kham.webm",   label: "Đi khám" },
  { phrase: "khó thở",   src: "/signs/kho_tho.webm",   label: "Khó thở" },
  { phrase: "chóng mặt", src: "/signs/chong_mat.webm", label: "Chóng mặt" },
  { phrase: "xây xẩm",   src: "/signs/chong_mat.webm", label: "Chóng mặt" }, // alias
  { phrase: "bác sĩ",    src: "/signs/bac_si.webm",    label: "Bác sĩ" },
  { phrase: "nghỉ ngơi", src: "/signs/nghi_ngoi.webm", label: "Nghỉ ngơi" },
  { phrase: "uống nước", src: "/signs/uong_nuoc.webm", label: "Uống nước" },
  { phrase: "bù nước",   src: "/signs/uong_nuoc.webm", label: "Uống nước" }, // alias
  { phrase: "theo dõi",  src: "/signs/theo_doi.webm",  label: "Theo dõi" },
  { phrase: "tái khám",  src: "/signs/di_kham.webm",   label: "Đi khám" }, // alias

  // ─── Từ đơn ──────────────────────────────────────────────────────
  { phrase: "đau",       src: "/signs/dau.webm",       label: "Đau" },
  { phrase: "nhức",      src: "/signs/dau.webm",       label: "Đau" }, // alias
  { phrase: "bụng",      src: "/signs/bung.webm",      label: "Bụng" },
  { phrase: "sốt",       src: "/signs/sot.webm",       label: "Sốt" },
  { phrase: "ho",        src: "/signs/ho.webm",        label: "Ho" },
  { phrase: "thuốc",     src: "/signs/thuoc.webm",     label: "Thuốc" },
];
