#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MediSign AI — VSL Data Collection Tool (Holistic, 465-D)
========================================================

Thu data thật theo chuẩn quốc tế SLR:
  - MediaPipe Holistic = Pose + Hands + FaceMesh chạy 1 lần.
  - Mỗi sequence 30 frame × 465 chiều = 51 pose + 126 hand + 288 face.
  - Lưu .npy + sidecar .json metadata (signer / lighting / ...) cho phép
    chia signer-independent lúc train.
  - Vẽ overlay đầy đủ (pose + face oval + brows + eyes + lips + hands)
    để verify tracking trước khi ghi.

Usage:
    pip install mediapipe opencv-python numpy
    python scripts/temp/collect_vsl_data.py \
        --signer S01 \
        --lighting normal \
        --background plain \
        --distance 1.5m \
        --angle 0deg
"""

import os
import sys
import time
import json
import argparse
import cv2
import numpy as np

try:
    import mediapipe as mp
except ImportError:
    print("❌ Cài thiếu: pip install mediapipe opencv-python numpy")
    sys.exit(1)

# Import landmark spec — phải khớp với landmarkSpec.ts.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_spec import (  # noqa: E402
    POSE_UPPER_BODY, FACE_KEY_INDICES,
    POSE_DIM, HAND_DIM, FACE_DIM, FEATURE_DIM,
    LIPS_OUTER, LIPS_INNER,
    EYEBROW_LEFT, EYEBROW_RIGHT, EYE_LEFT, EYE_RIGHT, FACE_OVAL,
)

CLASSES_JSON = os.environ.get(
    "VSL_CLASSES_JSON",
    os.path.join("apps", "web_next", "public", "models", "vsl", "classes.json"),
)


def _load_classes_from_json(path: str):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        manifest = json.load(f)
    out = []
    for cat in manifest.get("categories", []):
        for item in cat.get("items", []):
            c = item.get("code")
            v = item.get("vi", "")
            if c:
                out.append((c, v))
    return out if out else None


_loaded = _load_classes_from_json(CLASSES_JSON)
if _loaded:
    CLASSES = [c for c, _ in _loaded]
    LABELS_VI = {c: v for c, v in _loaded}
    print(f"📚 Loaded {len(CLASSES)} classes from {CLASSES_JSON}")
else:
    CLASSES = ["dau", "dau_dau", "bung", "sot", "ho",
               "kho_tho", "chong_mat", "thuoc", "bac_si", "khan_cap"]
    LABELS_VI = {c: c for c in CLASSES}
    print(f"⚠️  classes.json not found → fallback {len(CLASSES)} legacy classes")

SEQUENCE_LENGTH = 30
DATA_PATH = os.path.join("data", "vsl_dataset")

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

holistic = mp_holistic.Holistic(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    refine_face_landmarks=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)


def _normalize_pose(pose_landmarks):
    """Anchor midpoint vai (idx 11, 12); scale theo vai-hông trái."""
    out = np.zeros(POSE_DIM, dtype=np.float32)
    if pose_landmarks is None:
        return out
    lm = pose_landmarks.landmark
    sL, sR, hL = lm[11], lm[12], lm[23]
    cx, cy, cz = (sL.x + sR.x) / 2, (sL.y + sR.y) / 2, (sL.z + sR.z) / 2
    scale = max(np.hypot(sL.x - hL.x, sL.y - hL.y) + abs(sL.z - hL.z), 1e-6)
    for j, idx in enumerate(POSE_UPPER_BODY):
        p = lm[idx]
        out[j * 3] = (p.x - cx) / scale
        out[j * 3 + 1] = (p.y - cy) / scale
        out[j * 3 + 2] = (p.z - cz) / scale
    return out


def _normalize_hand(hand_landmarks):
    """Anchor wrist (idx 0); scale theo max distance từ wrist."""
    out = np.zeros(63, dtype=np.float32)
    if hand_landmarks is None:
        return out
    pts = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark], dtype=np.float32)
    wrist = pts[0]
    rel = pts - wrist
    scale = max(float(np.linalg.norm(rel, axis=1).max()), 1e-6)
    return (rel / scale).flatten()


# ── Hand slot tracker (occlusion handling, mirror logic của web client) ──
# State holders ở module-level cho đơn giản; reset trong collect_gestures().
_HAND_SLOT_STATE = {
    "left":  {"landmarks": None, "palm": None, "timestamp": 0.0},
    "right": {"landmarks": None, "palm": None, "timestamp": 0.0},
}
_HAND_STALE_SEC = 0.2  # 200 ms


def _palm_xyz(hand_landmarks):
    """Lấy palm center (idx 9 — middle MCP) làm tracker anchor."""
    if hand_landmarks is None:
        return None
    p = hand_landmarks.landmark[9]
    return np.array([p.x, p.y, p.z], dtype=np.float32)


def _assign_slots_with_continuity(left_lm, right_lm, midline_x, now_sec):
    """Mirror logic của VslRecognitionService.assignHandSlots.

    Holistic Python đã trả riêng `left_hand_landmarks` và `right_hand_landmarks`
    (tự dán nhãn theo ảnh đã mirror). Tuy nhiên khi 2 tay chạm/che lấp,
    nhãn này có thể flip giữa các frame. Ta áp dụng continuity assignment
    qua palm center + carry-forward khi 1 tay biến mất ngắn hạn.

    Trả về tuple (lm_for_left_slot, lm_for_right_slot).
    """
    # Detected list từ kết quả frame hiện tại.
    detected = []
    if left_lm is not None:
        detected.append(("left_label", left_lm, _palm_xyz(left_lm)))
    if right_lm is not None:
        detected.append(("right_label", right_lm, _palm_xyz(right_lm)))

    slots = ["left", "right"]
    fresh = {s: (_HAND_SLOT_STATE[s]["palm"] is not None
                 and now_sec - _HAND_SLOT_STATE[s]["timestamp"] <= _HAND_STALE_SEC)
             for s in slots}

    assigned = {s: None for s in slots}

    if any(fresh.values()) and detected:
        pairs = []
        for s in slots:
            if not fresh[s]:
                continue
            slot_palm = _HAND_SLOT_STATE[s]["palm"]
            for h_idx, (_, _, palm) in enumerate(detected):
                if palm is None:
                    continue
                d = float(np.sum((slot_palm - palm) ** 2))
                pairs.append((d, s, h_idx))
        pairs.sort()
        slot_taken = set()
        hand_used = set()
        for d, s, h_idx in pairs:
            if d > 0.0625:  # ≈ 0.25 đơn vị normalized
                continue
            if s in slot_taken or h_idx in hand_used:
                continue
            assigned[s] = detected[h_idx][1]
            slot_taken.add(s)
            hand_used.add(h_idx)

        # Slot trống → gán hand chưa dùng theo midline tiebreak.
        unused = [(i, detected[i][2][0]) for i in range(len(detected)) if i not in hand_used]
        if assigned["left"] is None and unused:
            unused.sort(key=lambda t: t[1])  # x nhỏ → trái
            i = unused.pop(0)[0]
            assigned["left"] = detected[i][1]
            hand_used.add(i)
        unused = [(i, detected[i][2][0]) for i in range(len(detected)) if i not in hand_used]
        if assigned["right"] is None and unused:
            unused.sort(key=lambda t: -t[1])
            i = unused.pop(0)[0]
            assigned["right"] = detected[i][1]
    elif detected:
        # Bootstrap: dùng nhãn gốc; còn dư → midline.
        for lbl, lm, palm in detected:
            slot = "left" if lbl == "left_label" else "right"
            if assigned[slot] is None:
                assigned[slot] = lm
        # Dồn dư
        unused_lms = [lm for _, lm, _ in detected if all(lm is not v for v in assigned.values())]
        for s in slots:
            if assigned[s] is None and unused_lms:
                assigned[s] = unused_lms.pop(0)

    # Update slot state + áp carry-forward cho slot chưa được gán.
    final = {}
    for s in slots:
        if assigned[s] is not None:
            _HAND_SLOT_STATE[s]["landmarks"] = assigned[s]
            _HAND_SLOT_STATE[s]["palm"] = _palm_xyz(assigned[s])
            _HAND_SLOT_STATE[s]["timestamp"] = now_sec
            final[s] = assigned[s]
        elif (_HAND_SLOT_STATE[s]["landmarks"] is not None
              and now_sec - _HAND_SLOT_STATE[s]["timestamp"] <= _HAND_STALE_SEC):
            final[s] = _HAND_SLOT_STATE[s]["landmarks"]
        else:
            _HAND_SLOT_STATE[s]["landmarks"] = None
            _HAND_SLOT_STATE[s]["palm"] = None
            final[s] = None
    return final["left"], final["right"]


def _reset_hand_slot_state():
    for s in _HAND_SLOT_STATE:
        _HAND_SLOT_STATE[s]["landmarks"] = None
        _HAND_SLOT_STATE[s]["palm"] = None
        _HAND_SLOT_STATE[s]["timestamp"] = 0.0


def _normalize_face(face_landmarks):
    """Anchor-based local frame (Procrustes-style) — cùng thuật toán với
    `fillFaceFeatures` trên web client. 3 anchor:
      - Đỉnh mũi (1)        → origin
      - Mắt L (133), R (362) → X-axis = mắt R − mắt L
      - Cằm (152)           → Y-axis sau Gram-Schmidt
    Z-axis = X × Y (right-handed).
    Scale = interocular distance.

    Khi đầu nghiêng yaw/pitch/roll, 3 anchor xoay theo nhau → frame xoay
    theo → toạ độ trong frame ổn định → bất biến head pose. KHÔNG dùng
    `facialTransformationMatrix` vì nó ở metric face-space, không khớp
    với landmark image-normalized space.
    """
    out = np.zeros(FACE_DIM, dtype=np.float32)
    if face_landmarks is None:
        return out
    pts = face_landmarks.landmark
    nose_tip = np.array([pts[1].x, pts[1].y, pts[1].z], dtype=np.float32)
    eye_l = np.array([pts[133].x, pts[133].y, pts[133].z], dtype=np.float32)
    eye_r = np.array([pts[362].x, pts[362].y, pts[362].z], dtype=np.float32)
    chin = np.array([pts[152].x, pts[152].y, pts[152].z], dtype=np.float32)

    x_axis = eye_r - eye_l
    interocular = float(np.linalg.norm(x_axis))
    if interocular < 1e-6:
        return out
    x_axis = x_axis / interocular

    eyes_mid = (eye_l + eye_r) / 2
    y_raw = chin - eyes_mid
    y_proj = float(np.dot(y_raw, x_axis))
    y_axis = y_raw - x_axis * y_proj
    y_len = float(np.linalg.norm(y_axis))
    if y_len < 1e-6:
        return out
    y_axis = y_axis / y_len

    z_axis = np.cross(x_axis, y_axis)

    rotation = np.stack([x_axis, y_axis, z_axis], axis=0)  # 3×3

    keys = np.array(
        [[pts[i].x, pts[i].y, pts[i].z] for i in FACE_KEY_INDICES],
        dtype=np.float32,
    )
    rel = keys - nose_tip                       # (N, 3)
    local = rel @ rotation.T                    # (N, 3) trong local frame
    return (local / interocular).flatten()


def extract_holistic_features(results, midline_x=0.5, now_sec=None):
    """Ghép vector 501-D = pose + hand_L + hand_R + face với continuity
    slot tracking cho 2 tay (carry-forward khi 1 tay che lấp).

    Args:
        results: output của holistic.process(rgb).
        midline_x: x-coord normalized làm tiebreak (mặc định 0.5 = giữa khung).
        now_sec: timestamp giây cho carry-forward; mặc định time.time().
    """
    if now_sec is None:
        now_sec = time.time()
    pose_vec = _normalize_pose(results.pose_landmarks)

    # Lấy nose từ pose nếu có để midline thực tế hơn 0.5.
    if results.pose_landmarks is not None:
        midline_x = results.pose_landmarks.landmark[0].x

    lh_lm, rh_lm = _assign_slots_with_continuity(
        results.left_hand_landmarks,
        results.right_hand_landmarks,
        midline_x, now_sec,
    )
    lh_vec = _normalize_hand(lh_lm)
    rh_vec = _normalize_hand(rh_lm)
    face_vec = _normalize_face(results.face_landmarks)
    vec = np.concatenate([pose_vec, lh_vec, rh_vec, face_vec])
    assert vec.shape[0] == FEATURE_DIM, f"Expected {FEATURE_DIM}, got {vec.shape[0]}"
    return vec


def _draw_face_subset(frame, face_landmarks, indices, color, thickness=1):
    h, w, _ = frame.shape
    for idx in indices:
        lm = face_landmarks.landmark[idx]
        cv2.circle(frame, (int(lm.x * w), int(lm.y * h)), thickness, color, -1)


def _draw_overlay(frame, results):
    h, w, _ = frame.shape
    # Pose
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255, 200, 80), thickness=2, circle_radius=2),
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 200, 80), thickness=2),
        )
    # Hands
    if results.left_hand_landmarks:
        mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                                  mp_styles.get_default_hand_landmarks_style(),
                                  mp_styles.get_default_hand_connections_style())
    if results.right_hand_landmarks:
        mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                                  mp_styles.get_default_hand_landmarks_style(),
                                  mp_styles.get_default_hand_connections_style())
    # Face: vẽ subset có ý nghĩa SLR thay vì full mesh để không che khuất.
    if results.face_landmarks:
        # Oval xám
        _draw_face_subset(frame, results.face_landmarks, FACE_OVAL, (180, 180, 180), 1)
        # Brows + eyes hồng
        _draw_face_subset(frame, results.face_landmarks, EYEBROW_LEFT + EYEBROW_RIGHT, (180, 105, 255), 2)
        _draw_face_subset(frame, results.face_landmarks, EYE_LEFT + EYE_RIGHT, (180, 105, 255), 2)
        # Lips đậm hơn (feature quan trọng nhất)
        _draw_face_subset(frame, results.face_landmarks, LIPS_OUTER + LIPS_INNER, (60, 60, 255), 2)


def collect_gestures(signer_id: str, session_meta: dict):
    for gesture in CLASSES:
        os.makedirs(os.path.join(DATA_PATH, gesture), exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Không thể mở Camera!")
        return

    print("\n" + "=" * 60)
    print("🔥 VSL Data Collector — HOLISTIC 501-D 🔥")
    print("=" * 60)
    print(f"  Vocabulary: {len(CLASSES)} classes (xem classes.json)")
    print("-" * 60)
    print("[Space] thu 1 sequence (30 frame ≈ 1 giây)")
    print("[ ] / [ ]  prev / next class")
    print("[J]    nhập số thứ tự class (1-N)")
    print("[F]    tìm class theo từ khoá")
    print("[Q]    thoát")
    print(f"Signer: {signer_id} | Meta: {session_meta}")
    print("=" * 60 + "\n")

    current_idx = 0
    is_collecting = False
    frame_buffer = []
    last_msg = ""

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = holistic.process(rgb)
        rgb.flags.writeable = True

        _draw_overlay(frame, results)
        feats = extract_holistic_features(results)
        gesture = CLASSES[current_idx]
        gesture_vi = LABELS_VI.get(gesture, gesture)
        gdir = os.path.join(DATA_PATH, gesture)
        os.makedirs(gdir, exist_ok=True)
        existing = len([f for f in os.listdir(gdir) if f.endswith(".npy") and signer_id in f])

        # HUD
        cv2.putText(frame, f"VSL Holistic — {signer_id}", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"[{current_idx + 1}/{len(CLASSES)}] {gesture_vi} ({gesture})", (15, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 0), 2)
        cv2.putText(frame, f"Samples (signer): {existing}", (15, 92), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Quality indicator: warn nếu thiếu modalities
        warn = []
        if results.pose_landmarks is None: warn.append("NO POSE")
        if results.face_landmarks is None: warn.append("NO FACE")
        if results.left_hand_landmarks is None and results.right_hand_landmarks is None: warn.append("NO HANDS")
        if warn:
            cv2.putText(frame, " | ".join(warn), (15, 118), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        if is_collecting:
            frame_buffer.append(feats)
            cv2.circle(frame, (w - 30, 30), 15, (0, 0, 255), -1)
            cv2.putText(frame, f"REC {len(frame_buffer)}/{SEQUENCE_LENGTH}", (15, 145),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            if len(frame_buffer) == SEQUENCE_LENGTH:
                arr = np.array(frame_buffer, dtype=np.float32)
                # Quality check: reject sample mà > 30% frame thiếu cả 2 tay.
                hand_zero_rate = np.mean(np.all(arr[:, POSE_DIM:POSE_DIM + HAND_DIM] == 0, axis=1))
                if hand_zero_rate > 0.3:
                    last_msg = f"⚠️  REJECTED (no-hand frames {hand_zero_rate*100:.0f}%)"
                    print(last_msg)
                else:
                    ts = int(time.time() * 1000)
                    fname = f"seq_{signer_id}_{ts}.npy"
                    fpath = os.path.join(gdir, fname)
                    np.save(fpath, arr)
                    meta = dict(session_meta)
                    meta.update({
                        "signer_id": signer_id,
                        "gesture": gesture,
                        "feature_dim": FEATURE_DIM,
                        "feature_layout": "pose51 + hand126 + face288",
                        "sequence_length": SEQUENCE_LENGTH,
                        "timestamp_ms": ts,
                        "hand_zero_rate": float(hand_zero_rate),
                        "spec_version": "holistic-v1",
                    })
                    with open(fpath.replace(".npy", ".json"), "w", encoding="utf-8") as fjson:
                        json.dump(meta, fjson, ensure_ascii=False, indent=2)
                    last_msg = f"✅ Saved {fname}"
                    print(last_msg)
                is_collecting = False
                frame_buffer = []
        else:
            cv2.putText(frame, "[SPACE] de bat dau quay", (15, 145),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        if last_msg:
            cv2.putText(frame, last_msg[:60], (15, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 220, 255), 1)

        cv2.imshow("MediSign AI - VSL Holistic Collector", frame)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), ord('Q')):
            break
        elif key == ord(' '):
            if not is_collecting:
                print(f"--> Quay '{gesture}' ({gesture_vi})...")
                is_collecting = True
                frame_buffer = []
                _reset_hand_slot_state()
        elif key in (ord('['), ord(',')):
            current_idx = (current_idx - 1) % len(CLASSES)
            print(f"← {CLASSES[current_idx]} ({LABELS_VI.get(CLASSES[current_idx], '')})")
        elif key in (ord(']'), ord('.')):
            current_idx = (current_idx + 1) % len(CLASSES)
            print(f"→ {CLASSES[current_idx]} ({LABELS_VI.get(CLASSES[current_idx], '')})")
        elif key in (ord('j'), ord('J')):
            cv2.destroyWindow("MediSign AI - VSL Holistic Collector")
            try:
                raw = input(f"Nhập số thứ tự class (1-{len(CLASSES)}): ").strip()
                idx = int(raw) - 1
                if 0 <= idx < len(CLASSES):
                    current_idx = idx
                    print(f"--> {CLASSES[current_idx]}")
            except ValueError:
                pass
        elif key in (ord('f'), ord('F')):
            cv2.destroyWindow("MediSign AI - VSL Holistic Collector")
            kw = input("Tìm class (substring code/vi, lowercase): ").strip().lower()
            if kw:
                for i, c in enumerate(CLASSES):
                    if kw in c.lower() or kw in LABELS_VI.get(c, "").lower():
                        current_idx = i
                        print(f"--> {c} ({LABELS_VI.get(c, '')})")
                        break

    cap.release()
    cv2.destroyAllWindows()
    holistic.close()
    print("\n👋 Đóng tool.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--signer", required=True)
    p.add_argument("--lighting", default="normal", choices=["normal", "low", "warm", "cold", "harsh"])
    p.add_argument("--background", default="plain")
    p.add_argument("--distance", default="1.5m")
    p.add_argument("--angle", default="0deg")
    args = p.parse_args()
    collect_gestures(args.signer, {
        "lighting": args.lighting,
        "background": args.background,
        "distance": args.distance,
        "angle": args.angle,
    })
