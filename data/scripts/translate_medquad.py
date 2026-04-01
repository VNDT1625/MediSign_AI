# -*- coding: utf-8 -*-
"""Dịch answer trong medquad_vi.json từ Anh sang Việt (Google Translate, miễn phí).
- Xử lý theo batch 50 mục
- Lưu tiến độ mỗi batch (có thể resume nếu bị gián đoạn)
- Delay giữa các batch để tránh rate limit
"""
import json, time, os, sys

from deep_translator import GoogleTranslator

SRC = r"C:\NDT\PJ\MediSign_AI\data\training_raw\MedQuAD\medquad_vi.json"
OUT = r"C:\NDT\PJ\MediSign_AI\data\training_raw\MedQuAD\medquad_vi_translated.json"
PROGRESS = r"C:\NDT\PJ\MediSign_AI\data\scripts\_medquad_progress.json"
BATCH = 50
DELAY = 2  # giây giữa mỗi batch
DISCLAIMER = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

translator = GoogleTranslator(source='en', target='vi')

def translate_text(text):
    """Dịch text, xử lý text dài bằng cách chia nhỏ."""
    if not text or len(text.strip()) < 5:
        return text
    # Bỏ disclaimer cũ trước khi dịch
    text = text.replace(DISCLAIMER, "").strip()
    if not text:
        return DISCLAIMER.strip()
    try:
        # Google Translate giới hạn 5000 ký tự
        if len(text) <= 4900:
            result = translator.translate(text)
            return result + DISCLAIMER if result else text + DISCLAIMER
        else:
            # Chia theo dấu chấm
            parts = []
            current = ""
            for sentence in text.split('. '):
                if len(current) + len(sentence) < 4500:
                    current += sentence + '. '
                else:
                    if current.strip():
                        parts.append(current.strip())
                    current = sentence + '. '
            if current.strip():
                parts.append(current.strip())

            translated_parts = []
            for p in parts:
                r = translator.translate(p)
                if r:
                    translated_parts.append(r)
                else:
                    translated_parts.append(p)
                time.sleep(0.5)
            return ' '.join(translated_parts) + DISCLAIMER
    except Exception as e:
        print(f"    Loi dich: {e}")
        return text + DISCLAIMER

# Load data
with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)
total = len(data)
print(f"Tong: {total} muc")

# Load progress nếu có
start_idx = 0
if os.path.exists(PROGRESS):
    with open(PROGRESS, "r", encoding="utf-8") as f:
        prog = json.load(f)
    start_idx = prog.get("last_done", 0)
    # Load partially translated data
    if os.path.exists(OUT):
        with open(OUT, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Resume tu muc {start_idx}/{total}")

# Translate
for i in range(start_idx, total, BATCH):
    batch_end = min(i + BATCH, total)
    print(f"Batch {i}-{batch_end} / {total} ({i*100//total}%)")

    for j in range(i, batch_end):
        answer = data[j].get("answer", "")
        # Kiểm tra xem đã dịch chưa (nếu answer chứa tiếng Việt phổ biến thì bỏ qua)
        if any(vw in answer.lower() for vw in ["triệu chứng", "điều trị", "bệnh nhân", "bác sĩ", "thuốc", "phòng ngừa", "chẩn đoán"]):
            continue
        # Kiểm tra xem có phải tiếng Anh không
        has_english = any(c.isascii() and c.isalpha() for c in answer[:100])
        if not has_english:
            continue

        translated = translate_text(answer)
        data[j]["answer"] = translated

        if (j - i) % 10 == 0 and j > i:
            sys.stdout.write(".")
            sys.stdout.flush()

    # Lưu progress sau mỗi batch
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(PROGRESS, "w", encoding="utf-8") as f:
        json.dump({"last_done": batch_end}, f)
    print(f"  -> Da luu ({batch_end}/{total})")

    if batch_end < total:
        time.sleep(DELAY)

# Xong
print(f"\n=== HOAN THANH: {total} muc da dich ===")
print(f"File: {OUT}")

# Xóa file progress
if os.path.exists(PROGRESS):
    os.remove(PROGRESS)
