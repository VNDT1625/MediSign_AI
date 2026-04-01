# -*- coding: utf-8 -*-
"""Tổng hợp tất cả dữ liệu y tế tiếng Việt cho training.
- Merge all_medical_vi + vn_diseases + vn_dialogues + vn_pharma_bhyt + MedQuAD + PubMedQA
- Ưu tiên: chẩn đoán bệnh + thuốc + tương tác thuốc
- Output: train.json, eval.json
"""
import json
import os
import random
from pathlib import Path

# Config
BASE_DIR = Path(r"C:\NDT\PJ\MediSign_AI\data")
OUT_DIR = BASE_DIR / "training_clean" / "qwen_72b"

INSTRUCTION = "Bạn là MediSign AI - trợ lý y tế thông minh. Hướng dẫn: 1. Chỉ gợi ý, KHÔNG chẩn đoán chắc chắn 2. Luôn khuyên gặp bác sĩ khi không chắc 3. Trả lời rõ ràng, dễ hiểu 4. Thêm lưu ý miễn trách."
DISCLAIMER = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

EVAL_RATIO = 0.1
MIN_ANSWER_LEN = 30  # Tăng lên để đảm bảo chất lượng
SEED = 42

def normalize_text(text):
    """Chuẩn hóa text."""
    import re
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def ensure_disclaimer(text):
    """Đảm bảo có disclaimer."""
    if "⚠️ Lưu ý" not in text:
        text = text.rstrip() + DISCLAIMER
    return text

def convert_to_training_format(item, source_name):
    """Convert item sang format training."""
    q = item.get("question", "").strip()
    a = item.get("answer", "").strip()

    if not q or not a or len(a) < MIN_ANSWER_LEN:
        return None

    return {
        "instruction": INSTRUCTION,
        "input": normalize_text(q),
        "output": ensure_disclaimer(normalize_text(a)),
        "source": source_name
    }

# Define all sources
SOURCES = [
    ("all_medical_vi.json", "all_medical"),
    ("vn_diseases.json", "vn_diseases"),
    ("vn_dialogues.json", "vn_dialogues"),
    ("vn_pharma_bhyt.json", "vn_pharma_bhyt"),
    ("MedQuAD/medquad_vi.json", "medquad"),
    ("pubmedqa/pubmedqa_vi.json", "pubmedqa"),
    ("vietnamese_medical/vietnamese_medical_qa.json", "vn_medical_qa"),
]

def main():
    print("=" * 60)
    print("TỔNG HỢP DỮ LIỆU Y TẾ TIẾNG VIỆT")
    print("=" * 60)

    # 1. Load all sources
    all_data = []
    source_stats = {}

    for filename, source_name in SOURCES:
        filepath = BASE_DIR / "training_raw" / filename
        if not filepath.exists():
            print(f"⚠️ File not found: {filename}")
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            # Convert to training format
            converted = []
            for item in raw_data:
                converted_item = convert_to_training_format(item, source_name)
                if converted_item:
                    converted.append(converted_item)

            all_data.extend(converted)
            source_stats[source_name] = len(converted)
            print(f"✓ {source_name}: {len(raw_data):,} -> {len(converted):,} (kept)")

        except Exception as e:
            print(f"✗ Error loading {filename}: {e}")

    print(f"\n📊 Total after conversion: {len(all_data):,} records")

    # 2. Deduplicate by input
    print("\n2. Deduplicating...")
    seen_inputs = {}
    unique_data = []

    for item in all_data:
        key = item["input"].strip().lower()
        if key not in seen_inputs:
            seen_inputs[key] = True
            unique_data.append(item)

    dupes_removed = len(all_data) - len(unique_data)
    print(f"   Removed {dupes_removed:,} duplicates")
    print(f"   Unique records: {len(unique_data):,}")

    # 3. Shuffle
    print("\n3. Shuffling...")
    random.seed(SEED)
    random.shuffle(unique_data)

    # 4. Split train/eval
    print("\n4. Splitting train/eval...")
    eval_count = max(int(len(unique_data) * EVAL_RATIO), 100)
    eval_data = unique_data[:eval_count]
    train_data = unique_data[eval_count:]

    print(f"   Train: {len(train_data):,}")
    print(f"   Eval: {len(eval_data):,}")

    # 5. Save
    print("\n5. Saving...")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    train_path = OUT_DIR / "train.json"
    eval_path = OUT_DIR / "eval.json"

    # Backup old files
    for old_path in [train_path, eval_path]:
        if old_path.exists():
            backup_path = old_path.with_suffix(old_path.suffix + ".backup.json")
            with open(old_path, "r", encoding="utf-8") as f:
                backup_path.write_text(f.read(), encoding="utf-8")
            print(f"   Backed up: {backup_path.name}")

    with open(train_path, "w", encoding="utf-8") as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)

    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(eval_data, f, ensure_ascii=False, indent=2)

    print(f"   Saved: {train_path}")
    print(f"   Saved: {eval_path}")

    # 6. Statistics
    print("\n" + "=" * 60)
    print("KẾT QUẢ CUỐI CÙNG")
    print("=" * 60)
    print(f"Train: {len(train_data):,} records")
    print(f"Eval:  {len(eval_data):,}")
    print(f"Total: {len(train_data) + len(eval_data):,}")
    print()

    # Source breakdown
    print("Source breakdown:")
    train_sources = {}
    for item in train_data:
        s = item.get("source", "unknown")
        train_sources[s] = train_sources.get(s, 0) + 1

    for src, count in sorted(train_sources.items(), key=lambda x: -x[1]):
        pct = count / len(train_data) * 100
        print(f"  {src}: {count:,} ({pct:.1f}%)")

    # Quality check
    print("\nQuality check:")
    vi_chars = 'àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ'
    vi_count = sum(1 for d in train_data if any(c in d['output'] for c in vi_chars))
    disclaimer_count = sum(1 for d in train_data if '⚠️' in d['output'])
    print(f"  Vietnamese: {vi_count:,}/{len(train_data):,} ({vi_count*100//len(train_data)}%)")
    print(f"  Has disclaimer: {disclaimer_count:,}/{len(train_data):,} ({disclaimer_count*100//len(train_data)}%)")

    # Sample
    print("\nSample (train[0]):")
    print(f"  Q: {train_data[0]['input'][:80]}...")
    print(f"  A: {train_data[0]['output'][:120]}...")

if __name__ == "__main__":
    main()
