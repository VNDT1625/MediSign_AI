#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adapter: Multi-VSL (WACV 2025) raw video → MediSign keypoint .npy format
========================================================================

Multi-VSL của AIOZ (https://github.com/Etdihatthoc/Multi-VSL_WACV_2025)
phát hành **video thô** + nhãn gloss. Trước khi train chung pipeline với
data ta tự thu, cần chuyển sang format `[30, 501]` (pose+hand+face) với
sequence length 30 frame ≈ 1s @ 30fps.

Reference paper: Dinh et al. "Sign Language Recognition: A Large-Scale
Multi-View Dataset and Comprehensive Evaluation" — WACV 2025.

Quy ước Multi-VSL:
  - Mỗi video tương ứng 1 gloss (1 từ).
  - 3 góc quay/từ × multiple signer.
  - Folder layout đơn giản: <root>/<gloss>/<video_id>.mp4.

Pipeline:
  1. Đọc video qua OpenCV → frame loop @ FPS gốc.
  2. Chạy MediaPipe Holistic → trích pose+hand+face.
  3. Continuity slot tracking cho 2 tay (mirror logic của
     `collect_vsl_data.py` để đồng nhất distribution).
  4. Resample về 30 frame: nearest-neighbor trên timeline đều.
  5. Lưu `data/vsl_dataset/<gloss>/seq_multivsl_<videoId>.npy` + sidecar
     .json metadata (signer_id="multivsl_<id>", source="multi_vsl").

Usage:
    python scripts/temp/adapt_multi_vsl.py \
        --input  /path/to/Multi-VSL/videos \
        --output data/vsl_dataset \
        --classes-json apps/web_next/public/models/vsl/classes.json \
        --max-videos-per-class 100   # tuỳ chọn; mặc định = all

Yêu cầu: Multi-VSL tải về theo hướng dẫn từ repo của họ. Adapter này
chỉ xử lý đúng những gloss khớp với code trong classes.json (case-
insensitive sau khi normalize). Gloss không khớp được skip + log.
"""

import os
import sys
import json
import time
import argparse
import glob
import unicodedata
import cv2
import numpy as np

try:
    import mediapipe as mp
except ImportError:
    print("❌ pip install mediapipe opencv-python numpy")
    sys.exit(1)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collect_vsl_data import (  # noqa: E402
    extract_holistic_features,
    _reset_hand_slot_state,
    SEQUENCE_LENGTH,
)
from landmark_spec import FEATURE_DIM  # noqa: E402

mp_holistic = mp.solutions.holistic


def normalize_label(s: str) -> str:
    """Chuẩn hoá tên gloss để match với code trong classes.json:
    - lowercase, bỏ dấu tiếng Việt, thay space/dấu gạch bằng underscore.
    """
    s = s.lower().strip()
    # Bỏ dấu
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = s.replace("đ", "d").replace("Đ", "d")
    # Thay non-alpha bằng underscore
    out = []
    for c in s:
        out.append(c if c.isalnum() else "_")
    s = "".join(out)
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")


def load_target_codes(classes_json_path: str) -> dict:
    """Trả về map normalized_name → code chính thức."""
    with open(classes_json_path, encoding="utf-8") as f:
        manifest = json.load(f)
    out = {}
    for cat in manifest.get("categories", []):
        for item in cat.get("items", []):
            code = item.get("code")
            vi = item.get("vi", "")
            if not code:
                continue
            # Cho phép match qua chính `code`, qua `vi` đã normalize, hoặc
            # các alias hay gặp (vd "đầu" vs "đau đầu").
            keys = {normalize_label(code), normalize_label(vi)}
            for k in keys:
                if k:
                    out[k] = code
    return out


def resample_to_fixed_length(frames: list, target_len: int) -> np.ndarray:
    """Nearest-neighbor sampling từ N frame về target_len.
    Đơn giản và đủ tốt cho action segment cố định 1 giây.
    """
    n = len(frames)
    if n == 0:
        return np.zeros((target_len, FEATURE_DIM), dtype=np.float32)
    if n == target_len:
        return np.array(frames, dtype=np.float32)
    indices = np.linspace(0, n - 1, target_len).round().astype(int)
    return np.array([frames[i] for i in indices], dtype=np.float32)


def process_video(video_path: str, holistic) -> np.ndarray:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    _reset_hand_slot_state()
    feats = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = holistic.process(rgb)
        rgb.flags.writeable = True
        feats.append(extract_holistic_features(results, now_sec=time.time()))
    cap.release()
    if not feats:
        return None
    return resample_to_fixed_length(feats, SEQUENCE_LENGTH)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Multi-VSL root: <gloss>/*.mp4")
    p.add_argument("--output", default=os.path.join("data", "vsl_dataset"))
    p.add_argument("--classes-json", required=True)
    p.add_argument("--max-videos-per-class", type=int, default=0,
                   help="0 = all. Hữu ích khi smoke-test pipeline.")
    p.add_argument("--limit-classes", type=int, default=0,
                   help="Chỉ xử lý N class đầu tiên (0 = tất cả).")
    args = p.parse_args()

    target_map = load_target_codes(args.classes_json)
    print(f"✅ Loaded {len(set(target_map.values()))} target codes from classes.json")

    src_glosses = sorted(d for d in os.listdir(args.input)
                         if os.path.isdir(os.path.join(args.input, d)))
    print(f"📁 Found {len(src_glosses)} gloss folders in source.")

    holistic = mp_holistic.Holistic(
        static_image_mode=False, model_complexity=1,
        min_detection_confidence=0.5, min_tracking_confidence=0.5,
        refine_face_landmarks=False,
    )

    matched = skipped = saved = 0
    classes_done = 0
    for gloss_name in src_glosses:
        if args.limit_classes and classes_done >= args.limit_classes:
            break
        norm = normalize_label(gloss_name)
        code = target_map.get(norm)
        if code is None:
            skipped += 1
            continue
        matched += 1
        classes_done += 1

        gloss_dir = os.path.join(args.input, gloss_name)
        videos = sorted(glob.glob(os.path.join(gloss_dir, "*.mp4")))
        if args.max_videos_per_class:
            videos = videos[: args.max_videos_per_class]

        out_dir = os.path.join(args.output, code)
        os.makedirs(out_dir, exist_ok=True)
        print(f"\n[{matched}] {gloss_name} → {code}: {len(videos)} videos")

        for v in videos:
            vid_id = os.path.splitext(os.path.basename(v))[0]
            out_npy = os.path.join(out_dir, f"seq_multivsl_{vid_id}.npy")
            out_json = out_npy.replace(".npy", ".json")
            if os.path.exists(out_npy):
                continue
            arr = process_video(v, holistic)
            if arr is None or arr.shape != (SEQUENCE_LENGTH, FEATURE_DIM):
                print(f"  ⚠️ skip {vid_id}")
                continue
            np.save(out_npy, arr)
            with open(out_json, "w", encoding="utf-8") as f:
                json.dump({
                    "signer_id": f"multivsl_{vid_id.split('_')[0]}",
                    "gesture": code,
                    "feature_dim": FEATURE_DIM,
                    "feature_layout": "pose51 + hand126 + face324",
                    "sequence_length": SEQUENCE_LENGTH,
                    "source": "multi_vsl_wacv2025",
                    "source_gloss": gloss_name,
                    "source_video": os.path.basename(v),
                    "spec_version": "holistic-v1",
                }, f, ensure_ascii=False, indent=2)
            saved += 1

    holistic.close()
    print(f"\n✅ Done. Matched gloss folders={matched} | skipped={skipped} | sequences saved={saved}")


if __name__ == "__main__":
    main()
