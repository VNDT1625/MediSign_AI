"""Quick smoke test for VSL Bi-LSTM model.

Verify:
  1. Model file (vsl_model.h5) loads correctly.
  2. Web export (weights.json + weights.bin) is consistent.
  3. Inference pipeline produces sane output shape.
"""

import json
import os
import sys

import numpy as np

PROJ_ROOT = r"C:\ndt\PJ\MediSign_AI - Copy"
H5_PATH = os.path.join(PROJ_ROOT, "output", "vsl_model", "vsl_model.h5")
WEIGHTS_JSON = os.path.join(PROJ_ROOT, "apps", "web_next", "public", "models", "vsl", "weights.json")
WEIGHTS_BIN = os.path.join(PROJ_ROOT, "apps", "web_next", "public", "models", "vsl", "weights.bin")
CLASSES_JSON = os.path.join(PROJ_ROOT, "apps", "web_next", "public", "models", "vsl", "classes.json")


def main() -> int:
    errors = []

    # 1. Check files exist
    for label, path in [
        ("h5", H5_PATH),
        ("weights.json", WEIGHTS_JSON),
        ("weights.bin", WEIGHTS_BIN),
        ("classes.json", CLASSES_JSON),
    ]:
        if not os.path.isfile(path):
            errors.append(f"MISSING: {label} at {path}")
            continue
        size = os.path.getsize(path)
        print(f"[OK] {label}: {size:,} bytes ({path})")

    if errors:
        print("\n=== ERRORS ===")
        for e in errors:
            print(e)
        return 1

    # 2. Verify classes
    with open(CLASSES_JSON, "r", encoding="utf-8") as f:
        classes_data = json.load(f)
    classes = classes_data.get("classes", [])
    print(f"\n[OK] Classes ({len(classes)}): {classes}")

    if len(classes) != 10:
        errors.append(f"Expected 10 classes, got {len(classes)}")

    # 3. Verify weights.json schema
    with open(WEIGHTS_JSON, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    weights = manifest.get("weights", [])
    print(f"\n[OK] Weights manifest: {len(weights)} tensors")
    total_floats = 0
    for i, entry in enumerate(weights[:5]):
        shape = entry.get("shape", [])
        offset = entry.get("offset", -1)
        length = entry.get("length", 0)
        n_floats = length // 4
        total_floats += n_floats
        print(f"   [{i}] shape={shape} offset={offset} length={length} ({n_floats:,} floats)")

    bin_size = os.path.getsize(WEIGHTS_BIN)
    sum_lengths = sum(e.get("length", 0) for e in weights)
    if sum_lengths != bin_size:
        errors.append(f"Mismatch: weights.json declares {sum_lengths:,} bytes but bin is {bin_size:,} bytes")
    else:
        print(f"\n[OK] Bin size matches manifest: {bin_size:,} bytes")

    # 4. Try loading h5 (optional — needs tensorflow)
    try:
        import tensorflow as tf  # type: ignore
        print(f"\n[INFO] TensorFlow {tf.__version__}")
        model = tf.keras.models.load_model(H5_PATH, compile=False)
        print(f"[OK] H5 model loaded")
        print(f"     Input shape: {model.input_shape}")
        print(f"     Output shape: {model.output_shape}")
        print(f"     Total params: {model.count_params():,}")

        # Sanity inference: random input
        dummy = np.random.randn(1, 30, 126).astype(np.float32)
        pred = model.predict(dummy, verbose=0)
        print(f"\n[OK] Inference test: output shape={pred.shape}, sum={pred[0].sum():.4f}")
        if abs(pred[0].sum() - 1.0) > 0.01:
            errors.append(f"Softmax output doesn't sum to 1: {pred[0].sum()}")
        else:
            print(f"     Softmax probabilities valid (sum=1.0)")

        top_idx = int(np.argmax(pred[0]))
        print(f"     Top class for random input: {classes[top_idx]} ({pred[0][top_idx]*100:.1f}%)")

    except ImportError:
        print("\n[SKIP] TensorFlow not installed — skipping h5 model test.")
    except Exception as e:
        errors.append(f"H5 load failed: {e}")

    print("\n=== SUMMARY ===")
    if errors:
        print(f"FAILED with {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
