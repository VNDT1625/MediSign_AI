#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export Keras VSL model → web runtime weights (dynamic shape)
============================================================

`tensorflowjs_converter` thường conflict version với TF local — nên web
client tự build kiến trúc Layers tương đương trong TS rồi load 24 tensor
trọng số raw từ `weights.json` + `weights.bin`.

Khác bản trước:
  - KHÔNG hard-code shape `[126, 256]` / `[32, 10]`. Tự suy ra từ chính
    Keras model → support cả 126 (hand-only), 225 (hand+face), 501
    (Holistic) và bất kỳ feature_dim/num_classes nào sau này.
  - KHÔNG ghi đè `classes.json` (file vocab y tế tự quản lý).
  - Verify model architecture đúng schema 24 weights (Bi-LSTM × 2 +
    BatchNorm × 2 + Dense × 2). Nếu khác → fail-fast với lỗi rõ.

Usage:
    python scripts/temp/export_vsl_tfjs.py
    # hoặc
    VSL_KERAS_PATH=/path/to/model.h5 python scripts/temp/export_vsl_tfjs.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
KERAS_MODEL = Path(os.environ.get(
    "VSL_KERAS_PATH",
    ROOT / "output" / "vsl_model" / "vsl_model.h5",
))
WEB_MODEL_DIR = ROOT / "apps" / "web_next" / "public" / "models" / "vsl"


# Thứ tự PHẢI khớp với `model.weights[]` của TF.js (trainable trước, non-
# trainable sau — convention Keras). Mỗi entry: (logical_name, h5_name_pattern).
# h5_name_pattern là tên weight trong Keras h5 (khác với layer-prefix path
# vì h5 lưu theo layer/weight_name không có 'sequential/' prefix).
def get_weight_layout(num_classes: int, feature_dim: int) -> list[tuple[str, list[int]]]:
    """Sinh thứ tự + shape mong đợi cho 24 tensor.

    Bi-LSTM 1: 64 units mỗi chiều → kernel [feature_dim, 4*64=256], bias [256], rk [64, 256]
    Concat → 128
    Bi-LSTM 2: 32 units mỗi chiều → kernel [128, 4*32=128], bias [128], rk [32, 128]
    Concat → 64
    Dense 32 → kernel [64, 32], bias [32]
    Dense num_classes → kernel [32, num_classes], bias [num_classes]
    """
    return [
        ("sequential/bidirectional/forward_lstm/lstm_cell/kernel",            [feature_dim, 256]),
        ("sequential/bidirectional/forward_lstm/lstm_cell/recurrent_kernel",  [64, 256]),
        ("sequential/bidirectional/forward_lstm/lstm_cell/bias",              [256]),
        ("sequential/bidirectional/backward_lstm/lstm_cell/kernel",           [feature_dim, 256]),
        ("sequential/bidirectional/backward_lstm/lstm_cell/recurrent_kernel", [64, 256]),
        ("sequential/bidirectional/backward_lstm/lstm_cell/bias",             [256]),
        ("sequential/batch_normalization/gamma",                              [128]),
        ("sequential/batch_normalization/beta",                               [128]),
        ("sequential/bidirectional_1/forward_lstm_1/lstm_cell/kernel",            [128, 128]),
        ("sequential/bidirectional_1/forward_lstm_1/lstm_cell/recurrent_kernel",  [32, 128]),
        ("sequential/bidirectional_1/forward_lstm_1/lstm_cell/bias",              [128]),
        ("sequential/bidirectional_1/backward_lstm_1/lstm_cell/kernel",           [128, 128]),
        ("sequential/bidirectional_1/backward_lstm_1/lstm_cell/recurrent_kernel", [32, 128]),
        ("sequential/bidirectional_1/backward_lstm_1/lstm_cell/bias",             [128]),
        ("sequential/batch_normalization_1/gamma",                            [64]),
        ("sequential/batch_normalization_1/beta",                             [64]),
        ("sequential/dense/kernel",                                           [64, 32]),
        ("sequential/dense/bias",                                             [32]),
        ("sequential/output_gesture/kernel",                                  [32, num_classes]),
        ("sequential/output_gesture/bias",                                    [num_classes]),
        # Non-trainable (BN moving stats) sau cùng — TF.js convention.
        ("sequential/batch_normalization/moving_mean",                        [128]),
        ("sequential/batch_normalization/moving_variance",                    [128]),
        ("sequential/batch_normalization_1/moving_mean",                      [64]),
        ("sequential/batch_normalization_1/moving_variance",                  [64]),
    ]


def find_weight_in_h5(h5: h5py.File, suffix: str) -> np.ndarray:
    """Tìm tensor theo suffix path trong cây model_weights/<layer>/<...>.

    Keras h5 lưu mỗi weight dưới layer name của nó (vd
    `model_weights/bidirectional/...`). Ta scan recursive thay vì hard-
    code path, vì naming có thể khác giữa Keras 2.x / 3.x.
    """
    target = suffix.lower()
    found = []

    def walk(group, path=""):
        for key in group.keys():
            full = f"{path}/{key}" if path else key
            obj = group[key]
            if isinstance(obj, h5py.Dataset):
                # So sánh suffix path để tolerant với variant naming.
                norm = full.lower()
                if norm.endswith(target) or target.split("/")[-1] in norm:
                    found.append((full, np.array(obj, dtype=np.float32)))
            else:
                walk(obj, full)

    walk(h5["model_weights"])
    if not found:
        raise KeyError(
            f"Không tìm thấy weight match suffix={suffix!r} trong h5. "
            f"Có thể model architecture đã thay đổi."
        )
    # Nếu có nhiều match (vd có cả forward và backward), pick cái khớp suffix tốt nhất.
    found.sort(key=lambda x: -len(os.path.commonprefix([x[0].lower()[::-1], target[::-1]])))
    return found[0][1]


def infer_shape_from_keras(h5: h5py.File) -> tuple[int, int]:
    """Suy ra (feature_dim, num_classes) từ Keras model h5."""
    # feature_dim = shape[0] của LSTM forward kernel đầu tiên
    fwd_kernel = find_weight_in_h5(h5, "bidirectional/forward_lstm/lstm_cell/kernel")
    feature_dim = int(fwd_kernel.shape[0])
    # num_classes = shape[-1] của output_gesture kernel
    out_kernel = find_weight_in_h5(h5, "output_gesture/kernel")
    num_classes = int(out_kernel.shape[-1])
    return feature_dim, num_classes


def main() -> None:
    if not KERAS_MODEL.exists():
        print(f"❌ Missing Keras model: {KERAS_MODEL}", file=sys.stderr)
        print("   Set VSL_KERAS_PATH hoặc train trước với `train_vsl_model.py`.", file=sys.stderr)
        sys.exit(1)

    WEB_MODEL_DIR.mkdir(parents=True, exist_ok=True)

    with h5py.File(KERAS_MODEL, "r") as h5:
        feature_dim, num_classes = infer_shape_from_keras(h5)
        print(f"📐 Inferred: feature_dim={feature_dim}, num_classes={num_classes}")

        layout = get_weight_layout(num_classes, feature_dim)
        offset = 0
        manifest = {
            "format": "medisign-vsl-weights-v1",
            "dtype": "float32",
            "feature_dim": feature_dim,
            "num_classes": num_classes,
            "weights": [],
        }
        chunks: list[bytes] = []

        for full_name, expected_shape in layout:
            suffix = full_name.split("sequential/", 1)[-1]
            arr = find_weight_in_h5(h5, suffix)
            if list(arr.shape) != expected_shape:
                raise ValueError(
                    f"Shape mismatch for {full_name}: got {list(arr.shape)}, "
                    f"expected {expected_shape}. "
                    f"Architecture của Keras model khác với spec — kiểm tra train_vsl_model.py."
                )
            data = arr.astype("<f4", copy=False).tobytes(order="C")
            manifest["weights"].append({
                "name": full_name,
                "shape": expected_shape,
                "offset": offset,
                "length": len(data),
            })
            chunks.append(data)
            offset += len(data)

    (WEB_MODEL_DIR / "weights.bin").write_bytes(b"".join(chunks))
    (WEB_MODEL_DIR / "weights.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # KHÔNG ghi đè classes.json — đó là vocab manifest do người dùng quản lý.
    classes_path = WEB_MODEL_DIR / "classes.json"
    if not classes_path.exists():
        print(
            f"⚠️  {classes_path} không tồn tại. Đây là single source of truth "
            f"cho vocabulary; tạo file rỗng default 10 class để service không "
            f"crash, nhưng bạn nên copy file vocab y tế đầy đủ vào đây."
        )
        classes_path.write_text(
            json.dumps({
                "version": "auto-fallback",
                "feature_dim": feature_dim,
                "categories": [{
                    "name": "fallback",
                    "vi": "Auto fallback",
                    "items": [{"code": f"class_{i}", "vi": f"Lớp {i}"} for i in range(num_classes)],
                }],
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(f"✅ Exported {len(manifest['weights'])} tensors ({offset} bytes)")
    print(f"   weights.json + weights.bin → {WEB_MODEL_DIR}")
    print(f"   classes.json (giữ nguyên): {classes_path}")
    print(f"   → Reload web → service tự detect feature_dim={feature_dim}, num_classes={num_classes}")


if __name__ == "__main__":
    main()
