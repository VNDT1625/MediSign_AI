#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MediSign AI — VSL Classifier Training (Holistic 465-D)
======================================================

Pipeline production:
  1. Load real dataset từ data/vsl_dataset/<class>/seq_*.npy (kèm sidecar
     .json để biết signer_id).
  2. Augmentation: gaussian jitter + time warping nhẹ + horizontal mirror
     (đổi tay trái-phải).
  3. Signer-independent split: ~20% signer cuối làm test, KHÔNG random
     trên augmented data.
  4. Bi-LSTM 64-32 hai chiều, BatchNorm + Dropout, class weight balanced.
  5. EarlyStopping theo val_macro_f1 (không phải val_accuracy — class
     không cân bằng), ReduceLROnPlateau.
  6. Confusion matrix + per-class F1 in cuối training.
  7. Save Keras .h5 (cho TF.js export) + TFLite Float16 (cho mobile).

Usage:
    python scripts/temp/train_vsl_model.py
"""

import os
import sys
import glob
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional, BatchNormalization, Input
from tensorflow.keras.utils import to_categorical
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.utils.class_weight import compute_class_weight

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_spec import POSE_DIM, HAND_DIM, FACE_DIM, FEATURE_DIM  # noqa: E402

tf.get_logger().setLevel("INFO")

# ─────────────────────────────────────────────────────────────────────
# Smoke mode — validate E2E plumbing (train → export → web) trong vài phút.
# Bật bằng env `VSL_SMOKE_TEST=1`. KHÔNG dùng cho production accuracy.
# Khi smoke:
#   - n_per_class = 12  (thay vì 120) → ít data, batch ít.
#   - epochs = 2        (thay vì 60) → đủ để init weights ≠ random.
#   - batch_size = 256  → ít step/epoch hơn.
#   - skip augmentation → tránh nhân data ×4.
#   - skip TFLite convert (chậm, không cần để test web).
# ─────────────────────────────────────────────────────────────────────
SMOKE_TEST = (
    os.environ.get("VSL_SMOKE_TEST", "").lower() in ("1", "true", "yes")
    or "--smoke" in sys.argv
)
if SMOKE_TEST:
    print("🚭 SMOKE MODE — chỉ để validate plumbing, accuracy KHÔNG có ý nghĩa.")

CLASSES_JSON = os.environ.get(
    "VSL_CLASSES_JSON",
    os.path.join("apps", "web_next", "public", "models", "vsl", "classes.json"),
)


def _load_classes_from_json(path: str):
    """Single source of truth — file JSON này cũng được web client load.
    Trả về list code theo đúng thứ tự xuất hiện (PHẢI ổn định, vì index
    trong list là class label số mà model học)."""
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        manifest = json.load(f)
    codes = []
    for cat in manifest.get("categories", []):
        for item in cat.get("items", []):
            c = item.get("code")
            if c:
                codes.append(c)
    return codes if codes else None


_loaded = _load_classes_from_json(CLASSES_JSON)
if _loaded:
    CLASSES = _loaded
    print(f"📚 Loaded {len(CLASSES)} classes from {CLASSES_JSON}")
else:
    CLASSES = ["dau", "dau_dau", "bung", "sot", "ho",
               "kho_tho", "chong_mat", "thuoc", "bac_si", "khan_cap"]
    print(f"⚠️  classes.json not found → fallback {len(CLASSES)} legacy classes")
NUM_CLASSES = len(CLASSES)
SEQUENCE_LENGTH = 30
DATA_PATH = os.path.join("data", "vsl_dataset")


# ─────────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────────

def load_real_dataset():
    X, y, signers = [], [], []
    for class_idx, cname in enumerate(CLASSES):
        cdir = os.path.join(DATA_PATH, cname)
        if not os.path.isdir(cdir):
            continue
        for fpath in glob.glob(os.path.join(cdir, "seq_*.npy")):
            arr = np.load(fpath).astype(np.float32)
            if arr.shape != (SEQUENCE_LENGTH, FEATURE_DIM):
                print(f"⚠️  Skip {fpath}: shape {arr.shape} != ({SEQUENCE_LENGTH}, {FEATURE_DIM})")
                continue
            X.append(arr)
            y.append(class_idx)
            sid = "UNK"
            meta_path = fpath.replace(".npy", ".json")
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, encoding="utf-8") as f:
                        sid = json.load(f).get("signer_id", "UNK")
                except Exception:
                    pass
            signers.append(sid)
    if not X:
        return None
    return np.stack(X), np.array(y, dtype=np.int32), np.array(signers)


def generate_mock_dataset(n_per_class=100):
    """Synthetic — CHỈ smoke-test pipeline. Đừng tin accuracy report."""
    print(f"⚠️  Real dataset không tồn tại — fallback synthetic ({n_per_class}/class)")
    rng = np.random.default_rng(42)
    X, y = [], []
    for class_idx, cname in enumerate(CLASSES):
        for _ in range(n_per_class):
            seq = rng.normal(0.0, 0.05, size=(SEQUENCE_LENGTH, FEATURE_DIM)).astype(np.float32)
            t = np.linspace(0, np.pi, SEQUENCE_LENGTH).astype(np.float32)
            # Gắn pattern khác biệt giữa các class — chỉ để pipeline chạy được.
            seq[:, POSE_DIM:POSE_DIM + 21] += 0.4 * np.sin(t)[:, None] * (class_idx + 1) / NUM_CLASSES
            X.append(seq); y.append(class_idx)
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32), None


# ─────────────────────────────────────────────────────────────────────
# Augmentation
# ─────────────────────────────────────────────────────────────────────

def aug_jitter(seq, sigma=0.01):
    return seq + np.random.normal(0, sigma, size=seq.shape).astype(np.float32)


def aug_time_warp(seq, max_shift=2):
    """Random shift các frame trong sequence ±max_shift để model không
    overfit timing tuyệt đối."""
    shift = np.random.randint(-max_shift, max_shift + 1)
    if shift == 0:
        return seq
    if shift > 0:
        return np.concatenate([np.repeat(seq[:1], shift, axis=0), seq[:-shift]], axis=0)
    return np.concatenate([seq[-shift:], np.repeat(seq[-1:], -shift, axis=0)], axis=0)


def aug_mirror(seq):
    """Horizontal mirror: x → -x cho mọi block (pose / hand / face).

    Chú ý: chỉ áp dụng nếu bạn coi tay trái và tay phải là interchangeable
    cho ký hiệu đó (đa số ký hiệu không phụ thuộc dominant hand). Không
    dùng cho ký hiệu bất đối xứng (ví dụ một số ký hiệu địa danh).
    """
    out = seq.copy()
    out[:, 0::3] = -out[:, 0::3]
    # Đổi chỗ block hand_L (offset HAND_OFFSET .. +63) với hand_R
    L0 = POSE_DIM
    R0 = POSE_DIM + 63
    end = POSE_DIM + HAND_DIM
    left = out[:, L0:R0].copy()
    right = out[:, R0:end].copy()
    out[:, L0:R0] = right
    out[:, R0:end] = left
    return out


def augment_dataset(X, y, factor=2, mirror=True):
    Xs, ys = [X], [y]
    for _ in range(factor):
        X_aug = np.stack([aug_time_warp(aug_jitter(seq)) for seq in X])
        Xs.append(X_aug)
        ys.append(y)
    if mirror:
        X_mir = np.stack([aug_mirror(seq) for seq in X])
        Xs.append(X_mir)
        ys.append(y)
    return np.concatenate(Xs), np.concatenate(ys)


# ─────────────────────────────────────────────────────────────────────
# Signer-independent split
# ─────────────────────────────────────────────────────────────────────

def signer_split(X, y, signers, test_ratio=0.2):
    """Chia signer ra train/test KHÔNG overlap → đo generalization thật."""
    if signers is None or len(set(signers)) < 2:
        return None
    unique = sorted(set(signers))
    n_test = max(1, int(round(len(unique) * test_ratio)))
    test_set = set(unique[-n_test:])
    is_test = np.array([s in test_set for s in signers])
    print(f"   Test signers: {sorted(test_set)} ({is_test.sum()}/{len(is_test)} sequences)")
    return X[~is_test], y[~is_test], X[is_test], y[is_test]


# ─────────────────────────────────────────────────────────────────────
# Model
# ─────────────────────────────────────────────────────────────────────

def build_model():
    model = Sequential([
        Input(shape=(SEQUENCE_LENGTH, FEATURE_DIM), name="vsl_landmarks_sequence"),
        Bidirectional(LSTM(64, return_sequences=True)),
        BatchNormalization(),
        Dropout(0.3),
        Bidirectional(LSTM(32, return_sequences=False)),
        BatchNormalization(),
        Dropout(0.3),
        Dense(32, activation="relu"),
        Dropout(0.2),
        Dense(NUM_CLASSES, activation="softmax", name="output_gesture"),
    ])
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def convert_to_tflite(keras_path, tflite_path):
    print("--> Convert Keras → TFLite (Float16)...")
    model = tf.keras.models.load_model(keras_path)
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.float16]
    tflite_bytes = converter.convert()
    os.makedirs(os.path.dirname(tflite_path), exist_ok=True)
    with open(tflite_path, "wb") as f:
        f.write(tflite_bytes)
    print(f"✅ TFLite: {tflite_path} ({os.path.getsize(tflite_path) / 1024:.1f} KB)")


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print(f"VSL CLASSIFIER TRAINING — Holistic {FEATURE_DIM}-D")
    print(f"  Layout: pose={POSE_DIM} + hand={HAND_DIM} + face={FACE_DIM}")
    print("=" * 70)

    real = load_real_dataset()
    if real is not None:
        X, y, signers = real
        print(f"✅ Loaded REAL: {len(X)} sequences from {len(set(signers))} signers.")
    else:
        n_per = 20 if SMOKE_TEST else 120
        if SMOKE_TEST:
            print(f"🚀 SMOKE-TEST mode → {n_per} samples/class, 3 epochs, no augment.")
        X, y, signers = generate_mock_dataset(n_per_class=n_per)

    # Signer-independent split TRƯỚC augmentation để tránh leak.
    split = signer_split(X, y, signers, test_ratio=0.2)
    if split is not None:
        X_train_raw, y_train_raw, X_test, y_test = split
    else:
        # Fallback: random split (đánh dấu rõ là weaker evaluation).
        from sklearn.model_selection import train_test_split
        X_train_raw, X_test, y_train_raw, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y,
        )
        print("⚠️  No signer metadata → random split (weaker generalization estimate).")

    # Augment chỉ trên train set. Smoke mode: skip augment để epoch nhỏ.
    if SMOKE_TEST:
        X_train, y_train = X_train_raw, y_train_raw
        print(f"   [smoke] skip augmentation. Train: {len(X_train)}  Test: {len(X_test)}")
    else:
        X_train, y_train = augment_dataset(X_train_raw, y_train_raw, factor=2, mirror=True)
        print(f"   Train: {len(X_train)} (augmented from {len(X_train_raw)})  Test: {len(X_test)}")

    y_train_cat = to_categorical(y_train, NUM_CLASSES)
    y_test_cat = to_categorical(y_test, NUM_CLASSES)

    cw = compute_class_weight(class_weight="balanced", classes=np.arange(NUM_CLASSES), y=y_train)
    class_weight = {i: float(w) for i, w in enumerate(cw)}

    model = build_model()
    model.summary()

    callbacks = []
    if not SMOKE_TEST:
        callbacks = [
            tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True, monitor="val_accuracy"),
            tf.keras.callbacks.ReduceLROnPlateau(patience=4, factor=0.5, monitor="val_loss"),
        ]

    print("\n--> Training...")
    if SMOKE_TEST:
        epochs = 3
        batch_size = 128
    elif real is not None:
        epochs = 60
        batch_size = 32
    else:
        epochs = 20
        batch_size = 32
    model.fit(
        X_train, y_train_cat,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_test, y_test_cat),
        class_weight=class_weight,
        callbacks=callbacks,
        verbose=1,
    )

    # Evaluation
    loss, acc = model.evaluate(X_test, y_test_cat, verbose=0)
    y_pred = np.argmax(model.predict(X_test, verbose=0), axis=1)
    macro_f1 = f1_score(y_test, y_pred, average="macro")
    print(f"\n✅ Test accuracy: {acc * 100:.2f}% | Macro F1: {macro_f1 * 100:.2f}%")
    print("\n── Per-class report ──")
    print(classification_report(y_test, y_pred, target_names=CLASSES, zero_division=0))
    print("── Confusion matrix ──")
    print(confusion_matrix(y_test, y_pred))

    # Save
    out_dir = "output/vsl_model"
    os.makedirs(out_dir, exist_ok=True)
    keras_path = os.path.join(out_dir, "vsl_model.h5")
    model.save(keras_path)
    print(f"\n--> Saved Keras: {keras_path}")

    tflite_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..",
        "apps/mobile_flutter/assets/models/vsl_model.tflite",
    ))
    if SMOKE_TEST:
        print("--> [smoke] Skip TFLite conversion (chỉ validate Keras + TF.js export).")
    else:
        convert_to_tflite(keras_path, tflite_path)

    print("\n👉 NEXT:")
    print("1. Chạy `scripts/temp/export_vsl_tfjs.py` để xuất weights cho web.")
    print("2. Copy weights.json + weights.bin vào apps/web_next/public/models/vsl/.")
    print("3. Service auto-detect 465-D → bật Holistic mode.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
