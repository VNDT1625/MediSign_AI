/**
 * VSL Landmark Specification (Holistic-style)
 * ===========================================
 *
 * Theo chuẩn quốc tế SLR (MediaPipe Holistic + non-manual markers literature):
 *   - Pose upper-body: cần thiết để xác định vị trí tay so với thân (đầu /
 *     ngực / bụng), nhất là với ký hiệu y tế.
 *   - Hands: hình bàn tay + chuyển động.
 *   - Face: phải bao phủ oval (đường viền mặt + hàm), brows, eyes, nose,
 *     lips ngoài + trong. Mouth/lips là feature quan trọng nhất (Lyu et al.
 *     2025: "The Importance of Facial Features in Vision-based SLR").
 *
 * Tất cả index dưới đây là index chuẩn của MediaPipe (không đổi giữa các
 * version Tasks Vision). Chia thành nhóm để vẽ contour và compute feature
 * dễ verify.
 *
 * QUAN TRỌNG: file này phải ĐỒNG BỘ với
 *   - `scripts/temp/collect_vsl_data.py`
 *   - `scripts/temp/train_vsl_model.py`
 * vì training pipeline dựa vào cùng index. Nếu sửa, sửa cả 3.
 */

// ─── POSE (MediaPipe PoseLandmarker — 33 điểm) ─────────────────────────
// Lấy 15 điểm upper-body có ý nghĩa cho SLR.
// Source: https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker
export const POSE_UPPER_BODY: ReadonlyArray<number> = [
  0,  // nose
  2, 5,             // eye L, eye R (inner)
  7, 8,             // ear L, ear R
  9, 10,            // mouth L, mouth R
  11, 12,           // shoulder L, shoulder R
  13, 14,           // elbow L, elbow R
  15, 16,           // wrist L, wrist R
  23, 24,           // hip L, hip R (anchor cho thân — chuẩn hoá scale)
];

export const POSE_DIM = POSE_UPPER_BODY.length * 3; // 15 × 3 = 45

// ─── FACE (MediaPipe FaceLandmarker — 478 điểm) ────────────────────────
// FACE_OVAL: viền ngoài mặt (jawline + đỉnh trán). Index chuẩn từ
// `FACEMESH_FACE_OVAL` connections trong MediaPipe.
export const FACE_OVAL: ReadonlyArray<number> = [
  10, 338, 297, 332, 284, 251, 389, 356, 454,
  323, 361, 288, 397, 365, 379, 378, 400, 377,
  152, 148, 176, 149, 150, 136, 172, 58, 132,
  93, 234, 127, 162, 21, 54, 103, 67, 109,
];

// Lông mày: 5 điểm mỗi bên (chuẩn dùng trong NMM analysis literature).
export const EYEBROW_LEFT: ReadonlyArray<number> = [70, 63, 105, 66, 107];
export const EYEBROW_RIGHT: ReadonlyArray<number> = [336, 296, 334, 293, 300];

// Mắt: 8 điểm mỗi bên — 2 góc + lid trên/dưới + 2 ngoài + 2 trong giúp
// ước lượng eye gaze + nheo mắt (NMM).
export const EYE_LEFT: ReadonlyArray<number> = [33, 7, 163, 144, 145, 153, 154, 155];
export const EYE_RIGHT: ReadonlyArray<number> = [362, 382, 381, 380, 374, 373, 390, 263];

// Mũi: anchor de-rotate + sống mũi.
export const NOSE: ReadonlyArray<number> = [1, 4, 5, 6, 168, 195];

// Môi ngoài — 20 điểm theo thứ tự traverse FACEMESH_LIPS chuẩn của
// MediaPipe (tránh cross-line khi vẽ closed-loop).
//   Bottom contour: 61 (góc trái) → 146 → 91 → 181 → 84 → 17 → 314 → 405 → 321 → 375 → 291 (góc phải)
//   Top contour:    291 → 409 → 270 → 269 → 267 → 0 → 37 → 39 → 40 → 185 → 61 (đóng)
export const LIPS_OUTER: ReadonlyArray<number> = [
  61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291,
  409, 270, 269, 267, 0, 37, 39, 40, 185,
];

// Môi trong — 20 điểm full set (8 cũ không tạo loop hợp lệ → wireframe
// vỡ thành zigzag). Thứ tự: vòng dưới ngược chiều kim → vòng trên về.
//   Bottom inner: 78 → 95 → 88 → 178 → 87 → 14 → 317 → 402 → 318 → 324 → 308
//   Top inner:    308 → 415 → 310 → 311 → 312 → 13 → 82 → 81 → 80 → 191 → 78
export const LIPS_INNER: ReadonlyArray<number> = [
  78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308,
  415, 310, 311, 312, 13, 82, 81, 80, 191,
];

export const FACE_KEY_INDICES: ReadonlyArray<number> = [
  ...FACE_OVAL,
  ...EYEBROW_LEFT,
  ...EYEBROW_RIGHT,
  ...EYE_LEFT,
  ...EYE_RIGHT,
  ...NOSE,
  ...LIPS_OUTER,
  ...LIPS_INNER,
];

export const FACE_DIM = FACE_KEY_INDICES.length * 3; // 36+10+16+6+20+20 = 108 → ×3 = 324

// ─── HAND ──────────────────────────────────────────────────────────────
export const HAND_DIM = 21 * 3 * 2; // 126

// ─── TOTAL ─────────────────────────────────────────────────────────────
export const FULL_FEATURE_DIM = POSE_DIM + HAND_DIM + FACE_DIM; // 45 + 126 + 324 = 495

// Feature offsets giúp downstream code trích slice an toàn.
export const FEATURE_OFFSETS = {
  POSE_START: 0,
  POSE_END: POSE_DIM, // 45
  HAND_START: POSE_DIM,
  HAND_END: POSE_DIM + HAND_DIM, // 171
  FACE_START: POSE_DIM + HAND_DIM,
  FACE_END: FULL_FEATURE_DIM, // 495
} as const;

// Connections để vẽ overlay (tham chiếu MediaPipe FACEMESH_*).
export const HAND_CONNECTIONS: ReadonlyArray<readonly [number, number]> = [
  [0, 1], [1, 2], [2, 3], [3, 4],         // thumb
  [0, 5], [5, 6], [6, 7], [7, 8],         // index
  [9, 10], [10, 11], [11, 12],            // middle
  [13, 14], [14, 15], [15, 16],           // ring
  [0, 17], [17, 18], [18, 19], [19, 20],  // pinky
  [5, 9], [9, 13], [13, 17],              // palm
];

// Pose connections theo MediaPipe POSE_CONNECTIONS chuẩn — bỏ 2 đường
// tai-vai (gây "tam giác cổ" hở vì đầu hẹp / vai rộng). Cổ được vẽ
// riêng trong overlay bằng 1 line từ midpoint tai → midpoint vai.
export const POSE_CONNECTIONS: ReadonlyArray<readonly [number, number]> = [
  // Head
  [0, 2], [0, 5],                         // nose ↔ inner eyes
  [2, 7], [5, 8],                         // inner eye ↔ ear
  [9, 10],                                // mouth corners
  // Shoulders + arms
  [11, 12], [11, 13], [13, 15],
  [12, 14], [14, 16],
  // Torso
  [11, 23], [12, 24], [23, 24],
];

// Face contours dùng cho overlay: nối các điểm theo thứ tự định sẵn.
export const FACE_CONTOUR_GROUPS: ReadonlyArray<{
  name: string;
  indices: ReadonlyArray<number>;
  closed: boolean;
}> = [
  { name: "oval", indices: FACE_OVAL, closed: true },
  { name: "browL", indices: EYEBROW_LEFT, closed: false },
  { name: "browR", indices: EYEBROW_RIGHT, closed: false },
  { name: "eyeL", indices: EYE_LEFT, closed: true },
  { name: "eyeR", indices: EYE_RIGHT, closed: true },
  { name: "lipsOuter", indices: LIPS_OUTER, closed: true },
  { name: "lipsInner", indices: LIPS_INNER, closed: true },
];
