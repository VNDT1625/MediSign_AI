#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MediSign AI — Vietnamese Sign Language (VSL) Classifier Training Pipeline
========================================================================

Kịch bản này cung cấp toàn bộ quy trình:
1. Giả lập dữ liệu chuỗi khung xương tay (Hand Landmarks) làm mẫu huấn luyện.
2. Xây dựng kiến trúc mô hình phân loại chuỗi tuần tự (Bi-LSTM / 1D-CNN + GRU).
3. Huấn luyện mô hình phân loại 10 cử chỉ y tế cơ bản.
4. Chuyển đổi mô hình đã huấn luyện sang định dạng TensorFlow Lite (.tflite) 
   kèm lượng tử hóa Float16 để chạy offline thời gian thực trên di động.

Đầu vào mô hình: Tensor dạng [Batch, 30 frames, 126 features]
- 30 frames: Cửa sổ thời gian 1 giây (ở tốc độ 30 FPS).
- 126 features: 21 landmarks × 2 bàn tay × 3D tọa độ (x, y, z).
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional, BatchNormalization, Input
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

# Cấu hình log
tf.get_logger().setLevel('INFO')

# ── CẤU HÌNH PIPELINE ──
CLASSES = ["dau", "dau_dau", "bung", "sot", "ho", "kho_tho", "chong_mat", "thuoc", "bac_si", "khan_cap"]
NUM_CLASSES = len(CLASSES)
SEQUENCE_LENGTH = 30  # 30 frames (~1 giây)
LANDMARKS_PER_HAND = 21
FEATURES_PER_LANDMARK = 3  # (x, y, z)
NUM_HANDS = 2  # Cả tay trái và tay phải
INPUT_FEATURES = SEQUENCE_LENGTH * LANDMARKS_PER_HAND * NUM_HANDS * FEATURES_PER_LANDMARK  # 30 * 21 * 2 * 3 = 3780 if flattened
# Nhưng ta giữ dạng tuần tự: [SEQUENCE_LENGTH, 126] (126 = 21 * 2 * 3)
FEATURE_DIM = LANDMARKS_PER_HAND * NUM_HANDS * FEATURES_PER_LANDMARK  # 126


def generate_mock_vsl_dataset(num_samples_per_class=100):
    """
    Giả lập dữ liệu chuỗi khung xương tay phục vụ chạy thử nghiệm pipeline.
    Dữ liệu thật sẽ được thu thập từ camera trước của thiết bị di động.
    """
    print(f"--> Đang sinh dữ liệu giả lập VSL cho {NUM_CLASSES} cử chỉ...")
    X = []
    y = []
    
    # Thiết lập seed để tạo sự đồng nhất
    np.random.seed(42)
    
    for class_idx, class_name in enumerate(CLASSES):
        for _ in range(num_samples_per_class):
            # Tạo một mẫu chuyển động tay chuẩn hóa (chuỗi 30 frames)
            # Khởi tạo một mẫu có nhiễu cơ bản
            sequence = np.random.normal(0.0, 0.05, size=(SEQUENCE_LENGTH, FEATURE_DIM))
            
            # Giả lập đặc trưng chuyển động tay riêng biệt cho từng từ cử chỉ
            # Ví dụ: Cử chỉ "Đầu" (đưa tay lên đầu) tọa độ Y của tay phải sẽ di chuyển lên cao dần
            time_steps = np.linspace(0, np.pi, SEQUENCE_LENGTH)
            
            if class_name == "dau_dau" or class_name == "dau":
                # Tay phải (cụm features từ index 63 đến 125) di chuyển lên trên đầu (Y giảm/tăng tùy hệ trục)
                sequence[:, 63:84] += 0.5 * np.sin(time_steps)[:, np.newaxis]
            elif class_name == "bung":
                # Tay phải di chuyển xuống vùng bụng
                sequence[:, 63:84] -= 0.6 * np.sin(time_steps)[:, np.newaxis]
            elif class_name == "ho" or class_name == "kho_tho":
                # Đưa tay lên che miệng
                sequence[:, 63:84] += 0.4 * np.sin(time_steps)[:, np.newaxis]
                sequence[:, 0:21] += 0.3 * np.sin(time_steps)[:, np.newaxis]  # Cả 2 tay di chuyển
            elif class_name == "khan_cap":
                # Cả hai tay vẫy liên tục tạo chuyển động sóng mạnh
                sequence[:, :] += 0.8 * np.sin(time_steps * 3)[:, np.newaxis]
            
            X.append(sequence)
            y.append(class_idx)
            
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32)


def build_vsl_classifier():
    """
    Xây dựng kiến trúc mô hình Bi-LSTM nhận dạng chuỗi cử chỉ.
    Kiến trúc này tối ưu cho thiết bị di động: vừa đủ sâu để học chuỗi, 
    nhưng đủ nhẹ để chạy mượt mà offline.
    """
    model = Sequential([
        Input(shape=(SEQUENCE_LENGTH, FEATURE_DIM), name="hand_landmarks_sequence"),
        
        # Lớp Bi-Directional LSTM thứ nhất giúp học chuyển động tiến/lùi
        Bidirectional(LSTM(64, return_sequences=True, unroll=True)),
        BatchNormalization(),
        Dropout(0.3),
        
        # Lớp Bi-Directional LSTM thứ hai để trích xuất đặc trưng sâu hơn
        Bidirectional(LSTM(32, return_sequences=False, unroll=True)),
        BatchNormalization(),
        Dropout(0.3),
        
        # Fully-connected layers
        Dense(32, activation="relu"),
        Dropout(0.2),
        Dense(NUM_CLASSES, activation="softmax", name="output_gesture")
    ])
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


def convert_to_tflite(keras_model_path, tflite_output_path):
    """
    Chuyển đổi mô hình Keras sang TensorFlow Lite (.tflite) 
    kèm theo lượng tử hóa Float16 để chạy offline tối ưu trên NPU/GPU di động.
    """
    print("--> Bắt đầu quá trình chuyển đổi sang TF Lite...")
    
    # Tải lại mô hình đã huấn luyện
    model = tf.keras.models.load_model(keras_model_path)
    
    # Khởi tạo bộ chuyển đổi
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # Bật tính năng tối ưu hóa kích thước mô hình
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    # Lượng tử hóa sang Float16 (giúp giảm 50% kích thước mà không mất độ chính xác)
    converter.target_spec.supported_types = [tf.float16]
    
    # Tiến hành chuyển đổi
    tflite_model = converter.convert()
    
    # Lưu file .tflite
    os.makedirs(os.path.dirname(tflite_output_path), exist_ok=True)
    with open(tflite_output_path, "wb") as f:
        f.write(tflite_model)
        
    print(f"✅ Đã xuất mô hình TF Lite thành công tại: {tflite_output_path}")
    print(f"   Dung lượng mô hình: {os.path.getsize(tflite_output_path) / 1024:.2f} KB (Cực kỳ nhẹ!)")


def main():
    print("======================================================================")
    print("     HUẤN LUYỆN MÔ HÌNH NHẬN DIỆN NGÔN NGỮ KÝ HIỆU TIẾNG VIỆT (VSL)")
    print("======================================================================")
    
    # Bước 1: Sinh tập dữ liệu thử nghiệm
    X, y = generate_mock_vsl_dataset(num_samples_per_class=150)
    y_cat = to_categorical(y, num_classes=NUM_CLASSES)
    
    # Chia tập Train/Test
    X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.2, random_state=42)
    print(f"   Tổng dữ liệu: {X.shape[0]} chuỗi mẫu.")
    print(f"   Tập huấn luyện: {X_train.shape[0]} mẫu. Tập kiểm thử: {X_test.shape[0]} mẫu.")
    print(f"   Hình dạng đầu vào: {X_train.shape[1:]} (Sequence length, Features per frame)")
    
    # Bước 2: Khởi tạo mô hình
    model = build_vsl_classifier()
    model.summary()
    
    # Bước 3: Huấn luyện mô hình
    print("\n--> Đang huấn luyện mô hình phân loại cử chỉ...")
    history = model.fit(
        X_train, y_train,
        epochs=15,  # Số epochs nhỏ cho chạy thử nghiệm nhanh
        batch_size=32,
        validation_data=(X_test, y_test),
        verbose=1
    )
    
    # Đánh giá hiệu năng trên tập test
    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"\n✅ Đánh giá hoàn tất: Độ chính xác trên tập kiểm thử = {accuracy * 100:.2f}%")
    
    # Lưu mô hình Keras
    keras_model_dir = "output/vsl_model"
    os.makedirs(keras_model_dir, exist_ok=True)
    keras_model_path = os.path.join(keras_model_dir, "vsl_model.h5")
    model.save(keras_model_path)
    print(f"--> Đã lưu mô hình Keras tạm thời tại: {keras_model_path}")
    
    # Bước 4: Chuyển đổi sang TF Lite
    tflite_output_path = "apps/mobile_flutter/assets/models/vsl_model.tflite"
    # Giả lập đường dẫn di động trong workspace
    workspace_tflite_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", tflite_output_path))
    
    convert_to_tflite(keras_model_path, workspace_tflite_path)
    
    print("\n👉 BƯỚC TIẾP THEO:")
    print("1. Đấu nối file 'vsl_model.tflite' vào thư mục assets của Flutter app.")
    print("2. Sử dụng RealSignLanguageService để nạp file model này qua thư viện tflite_flutter.")
    print("======================================================================\n")


if __name__ == "__main__":
    main()
