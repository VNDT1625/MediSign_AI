# -*- coding: utf-8 -*-
"""
Phase 1: Fix 605 entries còn tiếng Anh trong all_medical_vi.json
Dùng multi-thread Google Translate để dịch lại.
"""
import json, time, os, sys, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from deep_translator import GoogleTranslator

SRC = r"C:\NDT\PJ\MediSign_AI\data\training_raw\all_medical_vi.json"
OUT = r"C:\NDT\PJ\MediSign_AI\data\training_raw\all_medical_vi.json"
DISCLAIMER = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."
WORKERS = 8

def is_mostly_english(text, threshold=0.8):
    clean = text.replace("⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ.", "").strip()
    sample = clean[:200]
    ascii_a = sum(1 for c in sample if c.isascii() and c.isalpha())
    total_a = sum(1 for c in sample if c.isalpha())
    return total_a > 0 and ascii_a / total_a > threshold

def clean_text(text):
    text = text.replace(DISCLAIMER, "").replace("⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ.", "")
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'^Key Points\s*-?\s*', '', text, flags=re.IGNORECASE).strip()
    return text

def translate_one(idx_text):
    idx, text = idx_text
    t = GoogleTranslator(source='en', target='vi')
    cleaned = clean_text(text)
    if not cleaned or len(cleaned) < 5:
        return idx, cleaned + DISCLAIMER

    if len(cleaned) > 4500:
        parts = []
        cur = ""
        for s in cleaned.split('. '):
            if len(cur) + len(s) + 2 < 4200:
                cur += s + '. '
            else:
                if cur.strip():
                    parts.append(cur.strip())
                cur = s + '. '
        if cur.strip():
            parts.append(cur.strip())
        translated = []
        for p in parts:
            for attempt in range(3):
                try:
                    r = t.translate(p)
                    translated.append(r if r else p)
                    break
                except:
                    time.sleep(2 * (attempt + 1))
            else:
                translated.append(p)
        return idx, ' '.join(translated) + DISCLAIMER
    else:
        for attempt in range(3):
            try:
                r = t.translate(cleaned)
                return idx, (r if r else cleaned) + DISCLAIMER
            except:
                time.sleep(2 * (attempt + 1))
        return idx, cleaned + DISCLAIMER

# Load
with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

# Find entries to fix
to_fix = [(i, data[i]["answer"]) for i in range(len(data)) if is_mostly_english(data[i]["answer"])]
print(f"Entries to fix: {len(to_fix)}/{len(data)}")

if not to_fix:
    print("Nothing to fix!")
    sys.exit(0)

# Translate with thread pool
t_start = time.time()
done = 0
with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    futures = {executor.submit(translate_one, task): task[0] for task in to_fix}
    for future in as_completed(futures):
        idx, translated = future.result()
        data[idx]["answer"] = translated
        done += 1
        if done % 50 == 0:
            elapsed = time.time() - t_start
            rate = done / elapsed if elapsed > 0 else 0
            eta = (len(to_fix) - done) / rate / 60 if rate > 0 else 0
            print(f"  {done}/{len(to_fix)} ({done*100//len(to_fix)}%) | {rate:.1f}/s | ETA: {eta:.0f}min")

# Save
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
elapsed = time.time() - t_start
print(f"\n=== Fixed {len(to_fix)} entries in {elapsed:.0f}s ===")

# Verify
remaining = sum(1 for d in data if is_mostly_english(d["answer"]))
print(f"Remaining EN entries: {remaining}")
