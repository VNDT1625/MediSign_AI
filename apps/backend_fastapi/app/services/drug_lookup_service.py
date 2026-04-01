# -*- coding: utf-8 -*-
"""
Drug Recognition & Database Lookup Flow
Dành cho Qwen2.5-VL-72B - Khi AI nhận diện được tên thuốc từ ảnh
→ Tìm kiếm trong JSON database → Trả về kết quả
"""
import json
import re

# Load drug database
DRUG_DB_PATH = r"C:\NDT\PJ\MediSign_AI\data\training_clean\drug_database.json"

def load_drug_database():
    """Load drug database từ JSON file."""
    with open(DRUG_DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def search_drug_by_name(drug_name, drug_database):
    """
    Tìm kiếm thuốc trong database bằng tên.

    Args:
        drug_name: Tên thuốc được nhận diện từ ảnh
        drug_database: List chứa tất cả thuốc

    Returns:
        dict: Thông tin thuốc hoặc None nếu không tìm thấy
    """
    drug_name_lower = drug_name.lower().strip()

    # Tìm chính xác trước
    for drug in drug_database:
        if drug.get('name', '').lower() == drug_name_lower:
            return drug

    # Tìm gần đúng (partial match)
    for drug in drug_database:
        name_lower = drug.get('name', '').lower()
        if drug_name_lower in name_lower or name_lower in drug_name_lower:
            return drug

    return None

def search_drugs_by_keyword(keyword, drug_database, limit=5):
    """
    Tìm kiếm thuốc bằng keyword.

    Args:
        keyword: Từ khóa tìm kiếm
        drug_database: List chứa tất cả thuốc
        limit: Số lượng kết quả trả về

    Returns:
        list: Danh sách thuốc liên quan
    """
    keyword_lower = keyword.lower().strip()
    results = []

    for drug in drug_database:
        name = drug.get('name', '').lower()
        desc = drug.get('description', '').lower()

        if keyword_lower in name or keyword_lower in desc:
            results.append(drug)

        if len(results) >= limit:
            break

    return results

def get_drug_info(drug_name):
    """
    Main function: Lấy thông tin thuốc từ tên.

    Args:
        drug_name: Tên thuốc được AI nhận diện từ ảnh

    Returns:
        dict: Thông tin thuốc đầy đủ hoặc thông báo lỗi
    """
    drug_database = load_drug_database()

    # Tìm chính xác
    drug = search_drug_by_name(drug_name, drug_database)

    if drug:
        return {
            "status": "found",
            "drug": drug
        }

    # Tìm gần đúng
    suggestions = search_drugs_by_keyword(drug_name, drug_database, limit=5)

    if suggestions:
        return {
            "status": "suggestions",
            "suggestions": suggestions,
            "message": f"Không tìm thấy '{drug_name}'. Gợi ý:"
        }

    return {
        "status": "not_found",
        "message": f"Không tìm thấy thuốc '{drug_name}' trong database."
    }

# ============================================================
# VÍ DỤ SỬ DỤNG
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("DRUG RECOGNITION & DATABASE LOOKUP FLOW")
    print("=" * 60)
    print()

    # Test cases
    test_drugs = [
        "Paracetamol",
        "Ibuprofen",
        "Aspirin",
        "Metformin",
        "Thuốc không có trong DB"
    ]

    for drug_name in test_drugs:
        print(f"\n--- Tìm kiếm: '{drug_name}' ---")

        result = get_drug_info(drug_name)

        if result["status"] == "found":
            drug = result["drug"]
            print(f"✓ TÌM THẤY!")
            print(f"  Tên: {drug['name']}")
            print(f"  Mô tả: {drug['description'][:150]}...")

        elif result["status"] == "suggestions":
            print(f"⚠ GỢI Ý:")
            for s in result["suggestions"]:
                print(f"  - {s['name']}")

        else:
            print(f"✗ KHÔNG TÌM THẤY")
            print(f"  {result['message']}")

# ============================================================
# INTEGRATION VỚI QWEN2.5-VL-72B
# ============================================================

"""
Luồng hoạt động với Qwen2.5-VL-72B:

1. USER gửi ẢNH THUỐC
         │
         ▼
2. Qwen2.5-VL-72B đọc ảnh → Extract tên thuốc
         │
         ▼
3. Gọi hàm get_drug_info(drug_name)
         │
         ▼
4. Tìm trong drug_database.json
         │
         ├── Tìm thấy → Trả thông tin thuốc
         │
         └── Không tìm thấy → Gợi ý thuốc tương tự
         │
         ▼
5. Trả lời USER với kết quả

Ví dụ API call:
---------------
Input: "Paracetamol 500mg" (từ ảnh)
Output:
{
  "status": "found",
  "drug": {
    "name": "Paracetamol",
    "description": "Paracetamol, còn được gọi là acetaminophen...",
    ...
  }
}
"""
