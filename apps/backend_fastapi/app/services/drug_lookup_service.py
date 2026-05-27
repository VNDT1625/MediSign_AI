# -*- coding: utf-8 -*-
"""
Drug Recognition & Database Lookup Flow
Dành cho Qwen2.5-VL-72B - Khi AI nhận diện được tên thuốc từ ảnh
→ Tìm kiếm trong JSON database → Trả về kết quả
"""
import json
import re
import os
import unicodedata
from functools import lru_cache
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[4]
DEFAULT_DRUG_DB_PATHS = (
    ROOT_DIR / "data" / "training_clean" / "drug_database_dav_detailed_10k.json",
    ROOT_DIR / "data" / "training_clean" / "drug_database_10k_full.json",
    ROOT_DIR / "data" / "training_clean" / "drug_database_10k.json",
    ROOT_DIR / "data" / "training_clean" / "drug_database_expanded.json",
    ROOT_DIR / "data" / "training_clean" / "drug_database.json",
)


def _resolve_drug_db_path() -> Path:
    """Resolve the drug database path.

    BACKEND_DRUG_DB_PATH can point to a custom JSON file. Otherwise the
    expanded DAV-backed database is preferred when present, with the legacy
    242-drug database as fallback.
    """
    configured = os.getenv("BACKEND_DRUG_DB_PATH")
    if configured:
        path = Path(configured)
        if not path.is_absolute():
            path = ROOT_DIR / path
        return path

    for path in DEFAULT_DRUG_DB_PATHS:
        if path.exists():
            return path
    return DEFAULT_DRUG_DB_PATHS[-1]


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def _searchable_text(drug: dict) -> str:
    fields = (
        "name",
        "description",
        "active_ingredient_strength",
        "dosage_form",
        "registration_number",
    )
    return _normalize(" ".join(str(drug.get(field, "")) for field in fields))


def _detail_score(drug: dict) -> int:
    score = 0
    if drug.get("active_ingredient") or drug.get("active_ingredient_strength"):
        score += 4
    if drug.get("dosage_form"):
        score += 2
    if drug.get("strength"):
        score += 1
    if drug.get("registration_number"):
        score += 1
    if drug.get("source") == "dichvucong.dav.gov.vn":
        score += 2
    return score


@lru_cache(maxsize=4)
def load_drug_database():
    """Load drug database từ JSON file."""
    path = _resolve_drug_db_path()
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Drug database must be a JSON list: {path}")
    return data

def search_drug_by_name(drug_name, drug_database):
    """
    Tìm kiếm thuốc trong database bằng tên.

    Args:
        drug_name: Tên thuốc được nhận diện từ ảnh
        drug_database: List chứa tất cả thuốc

    Returns:
        dict: Thông tin thuốc hoặc None nếu không tìm thấy
    """
    drug_name_key = _normalize(drug_name)

    # Tìm chính xác trước
    exact_matches = [
        drug for drug in drug_database if _normalize(drug.get("name", "")) == drug_name_key
    ]
    if exact_matches:
        return max(exact_matches, key=_detail_score)

    # Tìm theo số đăng ký, hoạt chất, mô tả
    searchable_matches = [
        drug for drug in drug_database if drug_name_key and drug_name_key in _searchable_text(drug)
    ]
    if searchable_matches:
        return max(searchable_matches, key=_detail_score)

    # Tìm gần đúng (partial match)
    partial_matches = []
    for drug in drug_database:
        name_key = _normalize(drug.get("name", ""))
        if drug_name_key and (drug_name_key in name_key or name_key in drug_name_key):
            partial_matches.append(drug)
    if partial_matches:
        return max(partial_matches, key=_detail_score)

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
    keyword_key = _normalize(keyword)
    results = []
    seen = set()

    for drug in drug_database:
        searchable = _searchable_text(drug)

        if keyword_key and keyword_key in searchable:
            identity = (
                _normalize(drug.get("registration_number", "")),
                _normalize(drug.get("name", "")),
            )
            if identity in seen:
                continue
            seen.add(identity)
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
