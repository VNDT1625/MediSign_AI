# -*- coding: utf-8 -*-
"""Chuẩn hóa dữ liệu raw → clean format cho training.
- Merge all_medical_vi.json + existing clean data
- Loại trùng theo input (câu hỏi)
- Loại entry rỗng/quá ngắn
- Đảm bảo disclaimer
- Chia 90% train / 10% eval
- Shuffle ngẫu nhiên
"""
import json, os, random

INSTRUCTION = "Bạn là MediSign AI - trợ lý y tế thông minh. Hướng dẫn: 1. Chỉ gợi ý, KHÔNG chẩn đoán chắc chắn 2. Luôn khuyên gặp bác sĩ khi không chắc 3. Trả lời rõ ràng, dễ hiểu 4. Thêm lưu ý miễn trách."
DISCLAIMER = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

RAW_FILE = r"C:\NDT\PJ\MediSign_AI\data\training_raw\all_medical_vi.json"
EXISTING_TRAIN = r"C:\NDT\PJ\MediSign_AI\data\training_clean\qwen_72b\train.json"
EXISTING_EVAL = r"C:\NDT\PJ\MediSign_AI\data\training_clean\qwen_72b\eval.json"
OUT_TRAIN = r"C:\NDT\PJ\MediSign_AI\data\training_clean\qwen_72b\train.json"
OUT_EVAL = r"C:\NDT\PJ\MediSign_AI\data\training_clean\qwen_72b\eval.json"
BACKUP_TRAIN = r"C:\NDT\PJ\MediSign_AI\data\training_clean\qwen_72b\train_backup.json"
BACKUP_EVAL = r"C:\NDT\PJ\MediSign_AI\data\training_clean\qwen_72b\eval_backup.json"

EVAL_RATIO = 0.1
MIN_ANSWER_LEN = 20
SEED = 42

def ensure_disclaimer(text):
    if "⚠️ Lưu ý" not in text:
        text = text.rstrip() + DISCLAIMER
    return text

def normalize_text(text):
    """Chuẩn hóa whitespace."""
    import re
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# 1. Load raw data
print("1. Loading raw data...")
with open(RAW_FILE, "r", encoding="utf-8") as f:
    raw = json.load(f)
print(f"   Raw: {len(raw)} entries")

# 2. Load existing clean data
print("2. Loading existing clean data...")
existing = []
for fp in [EXISTING_TRAIN, EXISTING_EVAL]:
    if os.path.exists(fp):
        with open(fp, "r", encoding="utf-8") as f:
            existing.extend(json.load(f))
print(f"   Existing clean: {len(existing)} entries")

# 3. Convert raw → clean format
print("3. Converting raw → clean format...")
converted = []
for item in raw:
    q = item.get("question", "").strip()
    a = item.get("answer", "").strip()
    if not q or not a or len(a) < MIN_ANSWER_LEN:
        continue
    converted.append({
        "instruction": INSTRUCTION,
        "input": normalize_text(q),
        "output": ensure_disclaimer(normalize_text(a)),
    })
print(f"   Converted: {len(converted)} entries (skipped {len(raw) - len(converted)} too short/empty)")

# 4. Merge + dedup by input
print("4. Merging and deduplicating...")
seen_inputs = set()
all_clean = []

# Existing clean first (priority)
for item in existing:
    key = item["input"].strip().lower()
    if key not in seen_inputs:
        seen_inputs.add(key)
        all_clean.append(item)

# Then converted
for item in converted:
    key = item["input"].strip().lower()
    if key not in seen_inputs:
        seen_inputs.add(key)
        all_clean.append(item)

print(f"   After dedup: {len(all_clean)} entries (removed {len(existing) + len(converted) - len(all_clean)} dupes)")

# 5. Shuffle and split
print("5. Shuffling and splitting...")
random.seed(SEED)
random.shuffle(all_clean)

eval_count = max(int(len(all_clean) * EVAL_RATIO), 10)
eval_data = all_clean[:eval_count]
train_data = all_clean[eval_count:]
print(f"   Train: {len(train_data)}, Eval: {len(eval_data)}")

# 6. Backup old files
print("6. Backing up old files...")
if os.path.exists(EXISTING_TRAIN):
    with open(EXISTING_TRAIN, "r", encoding="utf-8") as f:
        old = f.read()
    with open(BACKUP_TRAIN, "w", encoding="utf-8") as f:
        f.write(old)
if os.path.exists(EXISTING_EVAL):
    with open(EXISTING_EVAL, "r", encoding="utf-8") as f:
        old = f.read()
    with open(BACKUP_EVAL, "w", encoding="utf-8") as f:
        f.write(old)
print("   Backed up train_backup.json, eval_backup.json")

# 7. Save
print("7. Saving clean data...")
with open(OUT_TRAIN, "w", encoding="utf-8") as f:
    json.dump(train_data, f, ensure_ascii=False, indent=2)
with open(OUT_EVAL, "w", encoding="utf-8") as f:
    json.dump(eval_data, f, ensure_ascii=False, indent=2)

# 8. Verify
print("\n=== KẾT QUẢ ===")
print(f"Train: {len(train_data)} entries -> {OUT_TRAIN}")
print(f"Eval:  {len(eval_data)} entries -> {OUT_EVAL}")

# Quick quality check
vi_chars = 'àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ'
vi_count = sum(1 for d in train_data + eval_data if any(c in d['output'] for c in vi_chars))
disclaimer_count = sum(1 for d in train_data + eval_data if '⚠️' in d['output'])
total = len(train_data) + len(eval_data)
print(f"\nQuality check:")
print(f"  Vietnamese content: {vi_count}/{total} ({vi_count*100//total}%)")
print(f"  Has disclaimer: {disclaimer_count}/{total} ({disclaimer_count*100//total}%)")
print(f"  Sample train[0]: input={train_data[0]['input'][:80]}...")
print(f"  Sample eval[0]:  input={eval_data[0]['input'][:80]}...")
