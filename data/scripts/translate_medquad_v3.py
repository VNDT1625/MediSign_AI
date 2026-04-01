# -*- coding: utf-8 -*-
"""Dịch MedQuAD answer - v3: batch translation, nhanh hơn ~10x."""
import json, time, os, sys, re

from deep_translator import GoogleTranslator

SRC = r"C:\NDT\PJ\MediSign_AI\data\training_raw\MedQuAD\medquad_vi.json"
OUT = r"C:\NDT\PJ\MediSign_AI\data\training_raw\MedQuAD\medquad_vi.json"
PROGRESS_FILE = r"C:\NDT\PJ\MediSign_AI\data\scripts\_mq3_progress.txt"
BATCH_SIZE = 20  # entries per batch translate call
SAVE_EVERY = 500
DISCLAIMER = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

translator = GoogleTranslator(source='en', target='vi')

def clean(text):
    text = text.replace(DISCLAIMER, "").replace("⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ.", "")
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'^Key Points\s*-?\s*', '', text, flags=re.IGNORECASE).strip()
    return text

def split_long(text, max_len=4500):
    if len(text) <= max_len:
        return [text]
    parts = []
    current = ""
    for s in text.split('. '):
        if len(current) + len(s) + 2 < max_len:
            current += s + '. '
        else:
            if current.strip():
                parts.append(current.strip())
            current = s + '. '
    if current.strip():
        parts.append(current.strip())
    return parts if parts else [text[:max_len]]

def translate_batch_safe(texts):
    """Dịch batch texts, retry on error."""
    results = []
    for t in texts:
        try:
            r = translator.translate(t)
            results.append(r if r else t)
        except Exception as e:
            print(f"\n  ! Err: {e}, retry...")
            time.sleep(3)
            try:
                r = translator.translate(t)
                results.append(r if r else t)
            except:
                results.append(t)
        time.sleep(0.1)
    return results

# Load
with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)
total = len(data)

start_idx = 0
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, "r") as f:
        start_idx = int(f.read().strip())
print(f"Tong: {total}, start: {start_idx}")

# Test
test = clean(data[0]["answer"])[:200]
r = translator.translate(test)
print(f"Test: {r[:80]}...")

# Process in batches
i = start_idx
while i < total:
    batch_end = min(i + BATCH_SIZE, total)
    
    # Prepare texts
    texts_to_translate = []
    indices = []
    for j in range(i, batch_end):
        cleaned = clean(data[j]["answer"])
        if not cleaned:
            continue
        parts = split_long(cleaned)
        for pi, p in enumerate(parts):
            texts_to_translate.append(p)
            indices.append((j, pi, len(parts)))

    if texts_to_translate:
        translated = translate_batch_safe(texts_to_translate)
        
        # Reassemble
        entry_parts = {}
        for (j, pi, part_count), t in zip(indices, translated):
            if j not in entry_parts:
                entry_parts[j] = [""] * part_count
            entry_parts[j][pi] = t
        
        for j, parts in entry_parts.items():
            data[j]["answer"] = ' '.join(parts) + DISCLAIMER

    i = batch_end
    
    if i % 100 == 0 or i == total:
        sys.stdout.write(f"\r  {i}/{total} ({i*100//total}%)")
        sys.stdout.flush()

    if i % SAVE_EVERY == 0:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        with open(PROGRESS_FILE, "w") as f:
            f.write(str(i))
        print(f"  -> Saved {i}/{total}")
        time.sleep(1)

# Final save
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"\n=== DONE: {total} entries ===")

if os.path.exists(PROGRESS_FILE):
    os.remove(PROGRESS_FILE)
