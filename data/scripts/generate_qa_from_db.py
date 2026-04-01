# -*- coding: utf-8 -*-
"""Generate Q&A from drug database for training."""
import json
import random
random.seed(111)

D = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."
INSTRUCTION = "Bạn là MediSign AI - trợ lý y tế thông minh. Hướng dẫn: 1. Chỉ gợi ý, KHÔNG chẩn đoán chắc chắn 2. Luôn khuyên gặp bác sĩ khi không chắc 3. Trả lời rõ ràng, dễ hiểu 4. Thêm lưu ý miễn trách."

# Load drug database
with open(r"C:\NDT\PJ\MediSign_AI\data\training_clean\drug_database.json", 'r', encoding='utf-8') as f:
    drugs = json.load(f)

print(f"Loaded {len(drugs)} drugs from database")

result = []

# Generate Q&A for each drug
for drug in drugs:
    name = drug.get('name', '')
    desc = drug.get('description', '')

    if not name:
        continue

    # Various question types
    result.append({
        "question": f"Thuốc {name} là gì? Công dụng?",
        "answer": f"{name}: {desc[:400]}... {D}",
        "source": "drug_db"
    })

    result.append({
        "question": f"{name} có tác dụng gì?",
        "answer": f"Thông tin về {name}: {desc[:400]}... {D}",
        "source": "drug_db"
    })

    result.append({
        "question": f"Cho tôi biết về thuốc {name}",
        "answer": f"{name}: {desc[:400]}... {D}",
        "source": "drug_db"
    })

    result.append({
        "question": f"Tìm hiểu thuốc {name}",
        "answer": f"{name}: {desc[:400]}... {D}",
        "source": "drug_db"
    })

print(f"Generated {len(result)} Q&A from drug database")

# Save
output_path = r"C:\NDT\PJ\MediSign_AI\data\training_raw\drug_db_qa.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Saved to: {output_path}")
