# -*- coding: utf-8 -*-
"""Gom tat ca du lieu da dich thanh 1 file thong nhat + don dep."""
import json, os, shutil

base = r"C:\NDT\PJ\MediSign_AI\data"

# 1. Doc tat ca JSON da dich
files_to_merge = [
    os.path.join(base, "training_raw", "full_medical_vi.json"),
    os.path.join(base, "training_raw", "vietnamese_medical", "vietnamese_medical_qa.json"),
    os.path.join(base, "training_raw", "MedQuAD", "medquad_vi.json"),
    os.path.join(base, "training_raw", "Medical-Dialogue-Dataset-Chinese", "chinese_medical_vi.json"),
    os.path.join(base, "training_raw", "pubmedqa", "pubmedqa_vi.json"),
]

all_data = []
for fp in files_to_merge:
    if os.path.exists(fp):
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
        all_data.extend(data)
        print(f"  + {os.path.basename(fp)}: {len(data)} muc")
    else:
        print(f"  ! Khong tim thay: {fp}")

# 2. Chuan hoa format: moi entry co question, answer, source
standardized = []
for item in all_data:
    entry = {
        "question": item.get("question", item.get("input", "")),
        "answer": item.get("answer", item.get("output", "")),
        "source": item.get("source", "unknown"),
    }
    if entry["question"] and entry["answer"]:
        standardized.append(entry)

# 3. Ghi file tong hop
out_dir = os.path.join(base, "training_raw")
out_file = os.path.join(out_dir, "all_medical_vi.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(standardized, f, ensure_ascii=False, indent=2)
print(f"\n=== TONG HOP: {len(standardized)} cau hoi-tra loi ===")
print(f"Ghi vao: {out_file}")

# 4. Thong ke theo source
from collections import Counter
sources = Counter(e["source"] for e in standardized)
print("\nThong ke theo nguon:")
for src, cnt in sources.most_common():
    print(f"  {src}: {cnt}")

# 5. Don dep scripts tam
scripts_dir = os.path.join(base, "scripts")
for tmp in ["_p1.json", "_p2.json"]:
    tmp_path = os.path.join(scripts_dir, tmp)
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
        print(f"Da xoa: {tmp_path}")
