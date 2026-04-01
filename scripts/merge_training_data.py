"""
Script merge data training mới vào file train.json chính
"""
import json

def main():
    # Đọc data cũ
    with open("c:/NDT/PJ/MediSign_AI/data/training_clean/qwen_72b/train.json", "r", encoding="utf-8") as f:
        old_data = json.load(f)

    # Đọc data mới
    with open("c:/NDT/PJ/MediSign_AI/data/training_clean/qwen_72b/train_new.json", "r", encoding="utf-8") as f:
        new_data = json.load(f)

    print(f"Data cũ: {len(old_data)} samples")
    print(f"Data mới: {len(new_data)} samples")

    # Merge - thêm data mới vào sau data cũ
    combined_data = old_data + new_data

    print(f"Tổng cộng: {len(combined_data)} samples")

    # Lưu file
    with open("c:/NDT/PJ/MediSign_AI/data/training_clean/qwen_72b/train.json", "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)

    print("Đã merge vào train.json")

if __name__ == "__main__":
    main()
