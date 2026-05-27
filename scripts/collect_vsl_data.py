#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MediSign AI — Vietnamese Sign Language (VSL) Data Collection Tool
================================================================

Kịch bản này hỗ trợ thu thập dữ liệu tọa độ khớp tay (landmarks) thực tế từ camera:
1. Mở camera thời gian thực bằng OpenCV.
2. Sử dụng MediaPipe Hands để phát hiện và trích xuất 21 landmarks (x, y, z) của cả 2 tay.
3. Cho phép chọn cử chỉ cần quay và thực hiện nhiều lượt thu thập (sequences).
4. Mỗi cử chỉ được quay trong 30 frames (~1 giây) và lưu trực tiếp thành file numpy (.npy)
   để huấn luyện mô hình Bi-LSTM thật sự hoạt động ngoài đời thực.
"""

import os
import time
import cv2
import numpy as np

# Thử import mediapipe, nếu chưa có sẽ hướng dẫn cài đặt
try:
    import mediapipe as mp
except ImportError:
    print("❌ Thiếu thư viện 'mediapipe' hoặc 'opencv-python'!")
    print("👉 Hãy cài đặt bằng lệnh: pip install mediapipe opencv-python")
    exit(1)

# Cấu hình danh mục từ khóa y tế
CLASSES = ["dau", "dau_dau", "bung", "sot", "ho", "kho_tho", "chong_mat", "thuoc", "bac_si", "khan_cap"]
SEQUENCE_LENGTH = 30  # 30 frames
DATA_PATH = os.path.join("data", "vsl_dataset")

# Khởi tạo MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def extract_landmarks(results):
    """
    Trích xuất và làm phẳng tọa độ khớp tay của cả hai tay.
    Kết quả trả về luôn có kích thước cố định là 126 (21 landmarks * 2 tay * 3D).
    Nếu thiếu tay nào thì lấp đầy bằng số 0.0.
    """
    lh = np.zeros(21 * 3)
    rh = np.zeros(21 * 3)
    
    if results.multi_hand_landmarks and results.multi_handedness:
        for idx, hand_handedness in enumerate(results.multi_handedness):
            label = hand_handedness.classification[0].label # 'Left' hoặc 'Right'
            hand_landmarks = results.multi_hand_landmarks[idx]
            
            # Trích xuất 21 điểm landmarks (x, y, z)
            coords = []
            for lm in hand_landmarks.landmark:
                coords.extend([lm.x, lm.y, lm.z])
            
            # Phân loại đúng tay trái / tay phải
            if label == 'Left':
                lh = np.array(coords)
            else:
                rh = np.array(coords)
                
    # Nối 2 mảng tọa độ thành vector 126 đặc trưng
    return np.concatenate([lh, rh])

def collect_gestures():
    # Tạo các thư mục lưu trữ dữ liệu nếu chưa có
    for gesture in CLASSES:
        os.makedirs(os.path.join(DATA_PATH, gesture), exist_ok=True)
        
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Không thể mở Camera!")
        return
        
    print("\n=======================================================")
    # Hướng dẫn sử dụng
    print("🔥 CÔNG CỤ THU THẬP DỮ LIỆU CỬ CHỈ NGÔN NGỮ KÝ HIỆU VS 🔥")
    print("=======================================================")
    print("Danh sách cử chỉ hỗ trợ:")
    for i, name in enumerate(CLASSES):
        print(f"  [{i}] {name.upper()}")
    print("-------------------------------------------------------")
    print("👉 Nhấn các số [0-9] trên bàn phím để chọn cử chỉ cần quay.")
    print("👉 Nhấn [Space] để bắt đầu thu thập 1 sequence (30 frames).")
    print("👉 Nhấn [Q] để thoát chương trình.")
    print("=======================================================\n")
    
    current_class_idx = 0
    is_collecting = False
    frame_buffer = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Lật ảnh theo chiều ngang để hiển thị như gương soi
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        # Chuyển hệ màu sang RGB phục vụ MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        # Vẽ các kết nối khớp tay lên màn hình
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
        # Trích xuất landmarks của frame hiện tại
        landmarks = extract_landmarks(results)
        
        current_gesture = CLASSES[current_class_idx]
        
        # Đếm số mẫu đã quay sẵn trong thư mục
        gesture_dir = os.path.join(DATA_PATH, current_gesture)
        existing_samples = len([f for f in os.listdir(gesture_dir) if f.endswith('.npy')])
        
        # Hiển thị thông tin trạng thái lên màn hình HUD
        cv2.putText(frame, f"Giao dien Thu thap VSL", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"Cu chi dang chon: {current_gesture.upper()}", (15, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 0), 2)
        cv2.putText(frame, f"So luot da quay: {existing_samples} sequences", (15, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        if is_collecting:
            frame_buffer.append(landmarks)
            # Hiển thị vòng tròn đỏ báo hiệu đang ghi
            cv2.circle(frame, (w - 30, 30), 15, (0, 0, 255), -1)
            cv2.putText(frame, f"RECORDING: {len(frame_buffer)}/{SEQUENCE_LENGTH}", (15, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            if len(frame_buffer) == SEQUENCE_LENGTH:
                # Đã đủ 30 frames, lưu lại file numpy
                is_collecting = False
                timestamp = int(time.time() * 1000)
                file_path = os.path.join(gesture_dir, f"seq_{timestamp}.npy")
                np.save(file_path, np.array(frame_buffer))
                print(f"✅ Đã ghi thành công sequence mới cho '{current_gesture}' tại: {file_path}")
                frame_buffer = []
        else:
            cv2.putText(frame, "NHAN [SPACE] DE BAT DAU QUAY 1 GIAY", (15, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
        cv2.imshow("MediSign AI - VSL Data Collector", frame)
        
        # Bắt sự kiện phím bấm
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord(' '):
            if not is_collecting:
                print(f"--> Chuẩn bị làm cử chỉ '{current_gesture}'...")
                is_collecting = True
                frame_buffer = []
        # Chọn cử chỉ bằng các số 0-9
        elif ord('0') <= key <= ord('9'):
            selected_idx = key - ord('0')
            if selected_idx < len(CLASSES):
                current_class_idx = selected_idx
                print(f"--> Đổi cử chỉ thu thập sang: {CLASSES[current_class_idx].upper()}")
                
    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    print("\n👋 Đã tắt camera và đóng công cụ thu thập dữ liệu.")

if __name__ == "__main__":
    collect_gestures()
