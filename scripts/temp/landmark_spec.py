#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Landmark specification — phải khớp 1:1 với
`apps/web_next/lib/vsl/landmarkSpec.ts`.

Theo chuẩn quốc tế Sign Language Recognition:
  - Pose upper-body  (15 points × 3 = 45)
  - Hands L+R        (21 × 3 × 2  = 126)
  - Face Holistic    (108 × 3     = 324)
      * face oval (jawline + forehead) — 36
      * eyebrows L + R                 — 10
      * eyes L + R                     — 16
      * nose                           —  6
      * lips outer + inner             — 40
Tổng: 45 + 126 + 324 = 495 chiều / frame.
"""

# ── POSE (MediaPipe Pose, 33 điểm) ────────────────────────────────────
POSE_UPPER_BODY = [
    0,                     # nose
    2, 5,                  # eye L, eye R (inner)
    7, 8,                  # ear L, ear R
    9, 10,                 # mouth L, mouth R
    11, 12,                # shoulder L, shoulder R
    13, 14,                # elbow L, elbow R
    15, 16,                # wrist L, wrist R
    23, 24,                # hip L, hip R (anchor cho thân)
]
POSE_DIM = len(POSE_UPPER_BODY) * 3   # 15 × 3 = 45

# ── FACE (MediaPipe FaceMesh, 478 điểm) ───────────────────────────────
FACE_OVAL = [
    10, 338, 297, 332, 284, 251, 389, 356, 454,
    323, 361, 288, 397, 365, 379, 378, 400, 377,
    152, 148, 176, 149, 150, 136, 172, 58, 132,
    93, 234, 127, 162, 21, 54, 103, 67, 109,
]
EYEBROW_LEFT  = [70, 63, 105, 66, 107]
EYEBROW_RIGHT = [336, 296, 334, 293, 300]
EYE_LEFT  = [33, 7, 163, 144, 145, 153, 154, 155]
EYE_RIGHT = [362, 382, 381, 380, 374, 373, 390, 263]
NOSE = [1, 4, 5, 6, 168, 195]
LIPS_OUTER = [
    61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291,
    409, 270, 269, 267, 0, 37, 39, 40, 185,
]
LIPS_INNER = [
    78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308,
    415, 310, 311, 312, 13, 82, 81, 80, 191,
]

FACE_KEY_INDICES = (
    FACE_OVAL + EYEBROW_LEFT + EYEBROW_RIGHT
    + EYE_LEFT + EYE_RIGHT + NOSE
    + LIPS_OUTER + LIPS_INNER
)
FACE_DIM = len(FACE_KEY_INDICES) * 3   # 36+10+16+6+20+20 = 108 → 324

# ── HAND ─────────────────────────────────────────────────────────────
HAND_DIM = 21 * 3 * 2   # 126

FEATURE_DIM = POSE_DIM + HAND_DIM + FACE_DIM   # 45 + 126 + 324 = 495

# Offsets cho consumers:
POSE_OFFSET = 0
HAND_OFFSET = POSE_DIM
FACE_OFFSET = POSE_DIM + HAND_DIM
