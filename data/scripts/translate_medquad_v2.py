# -*- coding: utf-8 -*-
"""Dịch MedQuAD answer từ Anh sang Việt - v2: dịch từng entry, debug rõ hơn."""
import json, time, os, sys

from deep_translator import GoogleTranslator

SRC = r"C:\NDT\PJ\MediSign_AI\data\training_raw\MedQuAD\medquad_vi.json"
OUT = r"C:\NDT\PJ\MediSign_AI\data\training_raw\MedQuAD\medquad_vi.json"
PROGRESS_FILE = r"C:\NDT\PJ\MediSign_AI\data\scripts\_mq2_progress.txt"
BATCH_SAVE = 100
DISCLAIMER = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

translator = GoogleTranslator(source='en', target='vi')

def clean_answer(text):
    """Bỏ disclaimer và whitespace thừa."""
    text = text.replace(DISCLAIMER, "").replace("⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ.", "")
    # Clean up weird whitespace from XML
    import re
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove "Key Points" header
    text = re.sub(r'^Key Points\s*-?\s*', '', text, flags=re.IGNORECASE).strip()
    return text

def translate_chunk(text):
    """Dịch 1 đoạn text <= 4900 chars."""
    try:
        result = translator.translate(text)
        return result if result else text
    except Exception as e:
        print(f"\n  ! Loi dich chunk: {e}")
        time.sleep(5)
        try:
            result = translator.translate(text)
            return result if result else text
        except:
            return text

def translate_text(text):
    """Dịch text, chia nhỏ nếu cần."""
    text = clean_answer(text)
    if not text or len(text) < 5:
        return text + DISCLAIMER

    if len(text) <= 4900:
        result = translate_chunk(text)
        return result + DISCLAIMER

    # Chia theo câu
    sentences = text.replace('. ', '.|').split('|')
    parts = []
    current = ""
    for s in sentences:
        if len(current) + len(s) < 4500:
            current += s + " "
        else:
            if current.strip():
                parts.append(current.strip())
            current = s + " "
    if current.strip():
        parts.append(current.strip())

    translated = []
    for p in parts:
        r = translate_chunk(p)
        translated.append(r)
        time.sleep(0.3)

    return ' '.join(translated) + DISCLAIMER

# Load data
with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)
total = len(data)
print(f"Tong: {total} muc")

# Load progress
start_idx = 0
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, "r") as f:
        start_idx = int(f.read().strip())
    print(f"Resume tu muc {start_idx}")

# Test dich 1 entry truoc
test_text = clean_answer(data[0]["answer"])[:200]
print(f"Test input: {test_text[:100]}")
test_result = translate_chunk(test_text)
print(f"Test output: {test_result[:100]}")
if test_result == test_text:
    print("CANH BAO: Translation khong thay doi! Kiem tra connection.")
else:
    print("OK - Translation hoat dong!")

# Main loop
for i in range(start_idx, total):
    answer = data[i]["answer"]

    # Kiem tra da dich chua
    cleaned = clean_answer(answer)
    if not cleaned:
        continue

    # Dich
    data[i]["answer"] = translate_text(answer)

    # Progress indicator
    if (i + 1) % 10 == 0:
        sys.stdout.write(f"\r  {i+1}/{total} ({(i+1)*100//total}%)")
        sys.stdout.flush()

    # Save periodically
    if (i + 1) % BATCH_SAVE == 0:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        with open(PROGRESS_FILE, "w") as f:
            f.write(str(i + 1))
        print(f"  -> Saved {i+1}/{total}")

    # Rate limit
    time.sleep(0.2)

# Final save
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"\n=== HOAN THANH: {total} muc ===")

# Cleanup
if os.path.exists(PROGRESS_FILE):
    os.remove(PROGRESS_FILE)
