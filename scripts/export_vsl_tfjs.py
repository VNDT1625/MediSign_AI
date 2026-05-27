#!/usr/bin/env python3
"""Export the trained Keras VSL model weights for the web runtime.

The installed tensorflowjs converter is incompatible with the local
TensorFlow build, so the web app builds the same Layers architecture in
TypeScript and loads these exported tensors directly.
"""

from __future__ import annotations

import json
import struct
from pathlib import Path

import h5py
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
KERAS_MODEL = ROOT / "output" / "vsl_model" / "vsl_model.h5"
WEB_MODEL_DIR = ROOT / "apps" / "web_next" / "public" / "models" / "vsl"

WEIGHT_ORDER = [
    ("sequential/bidirectional/forward_lstm/lstm_cell/kernel", [126, 256]),
    ("sequential/bidirectional/forward_lstm/lstm_cell/recurrent_kernel", [64, 256]),
    ("sequential/bidirectional/forward_lstm/lstm_cell/bias", [256]),
    ("sequential/bidirectional/backward_lstm/lstm_cell/kernel", [126, 256]),
    ("sequential/bidirectional/backward_lstm/lstm_cell/recurrent_kernel", [64, 256]),
    ("sequential/bidirectional/backward_lstm/lstm_cell/bias", [256]),
    ("sequential/batch_normalization/gamma", [128]),
    ("sequential/batch_normalization/beta", [128]),
    ("sequential/bidirectional_1/forward_lstm_1/lstm_cell/kernel", [128, 128]),
    ("sequential/bidirectional_1/forward_lstm_1/lstm_cell/recurrent_kernel", [32, 128]),
    ("sequential/bidirectional_1/forward_lstm_1/lstm_cell/bias", [128]),
    ("sequential/bidirectional_1/backward_lstm_1/lstm_cell/kernel", [128, 128]),
    ("sequential/bidirectional_1/backward_lstm_1/lstm_cell/recurrent_kernel", [32, 128]),
    ("sequential/bidirectional_1/backward_lstm_1/lstm_cell/bias", [128]),
    ("sequential/batch_normalization_1/gamma", [64]),
    ("sequential/batch_normalization_1/beta", [64]),
    ("sequential/dense/kernel", [64, 32]),
    ("sequential/dense/bias", [32]),
    ("sequential/output_gesture/kernel", [32, 10]),
    ("sequential/output_gesture/bias", [10]),
    ("sequential/batch_normalization/moving_mean", [128]),
    ("sequential/batch_normalization/moving_variance", [128]),
    ("sequential/batch_normalization_1/moving_mean", [64]),
    ("sequential/batch_normalization_1/moving_variance", [64]),
]


def read_weight(h5: h5py.File, weight_name: str) -> np.ndarray:
    for layer_name in h5["model_weights"].keys():
        layer = h5["model_weights"][layer_name]
        if weight_name in layer:
            return np.array(layer[weight_name], dtype=np.float32)
    raise KeyError(f"Missing weight in Keras model: {weight_name}")


def main() -> None:
    if not KERAS_MODEL.exists():
        raise FileNotFoundError(f"Missing Keras model: {KERAS_MODEL}")

    WEB_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    offset = 0
    manifest = {"format": "medisign-vsl-weights-v1", "dtype": "float32", "weights": []}
    chunks: list[bytes] = []

    with h5py.File(KERAS_MODEL, "r") as h5:
        for name, shape in WEIGHT_ORDER:
            arr = read_weight(h5, name)
            if list(arr.shape) != shape:
                raise ValueError(f"Unexpected shape for {name}: {arr.shape}, expected {shape}")
            data = arr.astype("<f4", copy=False).tobytes(order="C")
            manifest["weights"].append(
                {"name": name, "shape": shape, "offset": offset, "length": len(data)}
            )
            chunks.append(data)
            offset += len(data)

    (WEB_MODEL_DIR / "weights.bin").write_bytes(b"".join(chunks))
    (WEB_MODEL_DIR / "weights.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (WEB_MODEL_DIR / "classes.json").write_text(
        json.dumps(
            {
                "classes": [
                    "dau",
                    "dau_dau",
                    "bung",
                    "sot",
                    "ho",
                    "kho_tho",
                    "chong_mat",
                    "thuoc",
                    "bac_si",
                    "khan_cap",
                ]
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Exported {len(manifest['weights'])} tensors ({offset} bytes) to {WEB_MODEL_DIR}")


if __name__ == "__main__":
    main()
