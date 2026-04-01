# -*- coding: utf-8 -*-
"""Dịch answer trong pubmedqa_vi.json từ Anh sang Việt (Google Translate, miễn phí)."""
import json, time, os, sys

from deep_translator import GoogleTranslator

SRC = r"C:\NDT\PJ\MediSign_AI\data\training_raw\pubmedqa\pubmedqa_vi.json"
OUT = r"C:\NDT\PJ\MediSign_AI\data\training_raw\pubmedqa\pubmedqa_vi_translated.json"
PROGRESS = r"C:\NDT\PJ\MediSign_AI\data\scripts\_pubmedqa_progress.json"
BATCH = 50
DELAY = 2
DISCLAIMER = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

translator_en = GoogleTranslator(source='en', target='vi')

def translate_text(text):
    if not text or len(text.strip()) < 5:
        return text
    text = text.replace(DISCLAIMER, "").strip()
    if not text:
        return DISCLAIMER.strip()
    try:
        if len(text) <= 4900:
            result = translator_en.translate(text)
            return result + DISCLAIMER if result else text + DISCLAIMER
        else:
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
                r = translator_en.translate(p)
                translated_parts.append(r if r else p)
                time.sleep(0.5)
            return ' '.join(translated_parts) + DISCLAIMER
    except Exception as e:
        print(f"    Loi dich: {e}")
        return text + DISCLAIMER

with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)
total = len(data)
print(f"Tong: {total} muc")

start_idx = 0
if os.path.exists(PROGRESS):
    with open(PROGRESS, "r", encoding="utf-8") as f:
        prog = json.load(f)
    start_idx = prog.get("last_done", 0)
    if os.path.exists(OUT):
        with open(OUT, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Resume tu muc {start_idx}/{total}")

for i in range(start_idx, total, BATCH):
    batch_end = min(i + BATCH, total)
    print(f"Batch {i}-{batch_end} / {total} ({i*100//total}%)")

    for j in range(i, batch_end):
        # Dịch cả question và answer
        question = data[j].get("question", "")
        answer = data[j].get("answer", "")

        # Dịch question nếu còn tiếng Anh
        has_en_q = any(c.isascii() and c.isalpha() for c in question[:50])
        if has_en_q and not any(vw in question.lower() for vw in ["triệu chứng", "điều trị", "bệnh", "bác sĩ"]):
            try:
                tq = translator_en.translate(question)
                if tq:
                    data[j]["question"] = tq
            except:
                pass

        # Dịch answer
        has_en_a = any(c.isascii() and c.isalpha() for c in answer[:100])
        if has_en_a:
            data[j]["answer"] = translate_text(answer)

        if (j - i) % 10 == 0 and j > i:
            sys.stdout.write(".")
            sys.stdout.flush()

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(PROGRESS, "w", encoding="utf-8") as f:
        json.dump({"last_done": batch_end}, f)
    print(f"  -> Da luu ({batch_end}/{total})")

    if batch_end < total:
        time.sleep(DELAY)

print(f"\n=== HOAN THANH: {total} muc da dich ===")
print(f"File: {OUT}")

if os.path.exists(PROGRESS):
    os.remove(PROGRESS)
