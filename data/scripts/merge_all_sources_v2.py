# -*- coding: utf-8 -*-
"""Tổng hợp dữ liệu y tế - GIỮ VARIANT (cùng Q, khác A).
Điều này giúp model học được nhiều cách trả lời khác nhau.
"""
import json
import os
import random
from pathlib import Path
from collections import defaultdict

# Config
BASE_DIR = Path(r"C:\NDT\PJ\MediSign_AI\data")
OUT_DIR = BASE_DIR / "training_clean" / "qwen_72b"

INSTRUCTION = "Bạn là MediSign AI - trợ lý y tế thông minh. Hướng dẫn: 1. Chỉ gợi ý, KHÔNG chẩn đoán chắc chắn 2. Luôn khuyên gặp bác sĩ khi không chắc 3. Trả lời rõ ràng, dễ hiểu 4. Thêm lưu ý miễn trách."
DISCLAIMER = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

EVAL_RATIO = 0.1
MIN_ANSWER_LEN = 30
SEED = 42

def normalize_text(text):
    import re
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def ensure_disclaimer(text):
    if "⚠️ Lưu ý" not in text:
        text = text.rstrip() + DISCLAIMER
    return text

SOURCES = [
    ("all_medical_vi.json", "all_medical"),
    ("vn_diseases.json", "vn_diseases"),
    ("vn_dialogues.json", "vn_dialogues"),
    ("vn_pharma_bhyt.json", "vn_pharma_bhyt"),
    ("MedQuAD/medquad_vi.json", "medquad"),
    ("pubmedqa/pubmedqa_vi.json", "pubmedqa"),
    ("vietnamese_medical/vietnamese_medical_qa.json", "vn_medical_qa"),
    ("drug_medicine_qa.json", "drug_medicine"),
    ("vn_drugs_extended.json", "vn_drugs"),
    ("wikipedia_drugs_clean.json", "wikipedia_drugs"),
    ("crawled_extended_clean.json", "crawled_extended"),
    ("synthetic_data.json", "synthetic"),
    ("synthetic_v2.json", "synthetic_v2"),
    ("synthetic_drugs.json", "drug_synthetic"),
    ("drug_db_qa.json", "drug_db"),
]

def main():
    print("=" * 60)
    print("TỔNG HỢP DỮ LIỆU - GIỮ VARIANT")
    print("=" * 60)

    # 1. Load all sources and group by question
    question_groups = defaultdict(list)  # question -> list of (answer, source)
    source_stats = {}

    for filename, source_name in SOURCES:
        filepath = BASE_DIR / "training_raw" / filename
        if not filepath.exists():
            print(f"⚠️ File not found: {filename}")
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            count = 0
            for item in raw_data:
                q = item.get("question", "").strip()
                a = item.get("answer", "").strip()

                if q and a and len(a) >= MIN_ANSWER_LEN:
                    question_groups[q].append({
                        "answer": ensure_disclaimer(normalize_text(a)),
                        "source": source_name
                    })
                    count += 1

            source_stats[source_name] = count
            print(f"✓ {source_name}: {len(raw_data):,} -> {count:,}")

        except Exception as e:
            print(f"✗ Error: {filename}: {e}")

    print(f"\n📊 Unique questions: {len(question_groups):,}")

    # 2. Create training data - keep up to 3 variants per question
    all_data = []
    variant_counts = defaultdict(int)

    for q, answers in question_groups.items():
        # Keep up to 3 different answers for the same question
        unique_answers = []
        seen_ans = set()

        for ans_obj in answers:
            ans = ans_obj["answer"]
            # Simple dedupe by first 50 chars of answer
            ans_key = ans[:100].lower()
            if ans_key not in seen_ans and len(unique_answers) < 3:
                seen_ans.add(ans_key)
                unique_answers.append(ans_obj)

        for ans_obj in unique_answers:
            all_data.append({
                "instruction": INSTRUCTION,
                "input": normalize_text(q),
                "output": ans_obj["answer"],
                "source": ans_obj["source"]
            })
            variant_counts[len(unique_answers)] += 1

    print(f"   Total records (with variants): {len(all_data):,}")
    print(f"   Variant distribution: {dict(variant_counts)}")

    # 3. Shuffle
    random.seed(SEED)
    random.shuffle(all_data)

    # 4. Split
    eval_count = max(int(len(all_data) * EVAL_RATIO), 100)
    eval_data = all_data[:eval_count]
    train_data = all_data[eval_count:]

    print(f"\n📊 Train: {len(train_data):,}, Eval: {len(eval_data):,}")

    # 5. Save
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    train_path = OUT_DIR / "train.json"
    eval_path = OUT_DIR / "eval.json"

    with open(train_path, "w", encoding="utf-8") as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)

    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(eval_data, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Saved: {train_path}")
    print(f"✓ Saved: {eval_path}")

    # Stats
    print("\n" + "=" * 60)
    print("KẾT QUẢ")
    print("=" * 60)
    print(f"Train: {len(train_data):,}")
    print(f"Eval: {len(eval_data):,}")
    print(f"Total: {len(train_data) + len(eval_data):,}")

    # Source breakdown
    train_sources = defaultdict(int)
    for item in train_data:
        train_sources[item.get("source", "unknown")] += 1

    print("\nSource breakdown:")
    for src, count in sorted(train_sources.items(), key=lambda x: -x[1]):
        print(f"  {src}: {count:,}")

    # Quality
    vi_count = sum(1 for d in train_data if any(c in d['output'] for c in 'àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ'))
    disc_count = sum(1 for d in train_data if '⚠️' in d['output'])
    print(f"\nQuality: Vietnamese={vi_count*100//len(train_data)}%, Disclaimer={disc_count*100//len(train_data)}%")

if __name__ == "__main__":
    main()
