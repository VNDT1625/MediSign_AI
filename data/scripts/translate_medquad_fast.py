# -*- coding: utf-8 -*-
"""Dịch MedQuAD answer - FAST version: concurrent threads."""
import json, time, os, sys, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from deep_translator import GoogleTranslator

SRC = r"C:\NDT\PJ\MediSign_AI\data\training_raw\MedQuAD\medquad_vi.json"
OUT = r"C:\NDT\PJ\MediSign_AI\data\training_raw\MedQuAD\medquad_vi.json"
PROGRESS_FILE = r"C:\NDT\PJ\MediSign_AI\data\scripts\_mqfast_progress.txt"
WORKERS = 8
SAVE_EVERY = 500
DISCLAIMER = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

def clean(text):
    text = text.replace(DISCLAIMER, "").replace("⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ.", "")
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'^Key Points\s*-?\s*', '', text, flags=re.IGNORECASE).strip()
    return text

def translate_one(idx_text):
    """Translate a single (index, text) pair. Each thread gets its own translator."""
    idx, text = idx_text
    t = GoogleTranslator(source='en', target='vi')
    cleaned = clean(text)
    if not cleaned or len(cleaned) < 5:
        return idx, cleaned + DISCLAIMER

    # Split long texts
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
        translated_parts = []
        for p in parts:
            for attempt in range(3):
                try:
                    r = t.translate(p)
                    translated_parts.append(r if r else p)
                    break
                except Exception:
                    time.sleep(2 * (attempt + 1))
            else:
                translated_parts.append(p)
        return idx, ' '.join(translated_parts) + DISCLAIMER
    else:
        for attempt in range(3):
            try:
                r = t.translate(cleaned)
                return idx, (r if r else cleaned) + DISCLAIMER
            except Exception:
                time.sleep(2 * (attempt + 1))
        return idx, cleaned + DISCLAIMER

# Load
with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)
total = len(data)

start_idx = 0
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, "r") as f:
        start_idx = int(f.read().strip())
print(f"Total: {total}, resuming from: {start_idx}")

# Quick test
test_t = GoogleTranslator(source='en', target='vi')
r = test_t.translate("Heart disease symptoms include chest pain and shortness of breath.")
print(f"Test: {r}")

# Process in chunks with thread pool
chunk_size = SAVE_EVERY
t_start = time.time()

for chunk_start in range(start_idx, total, chunk_size):
    chunk_end = min(chunk_start + chunk_size, total)
    tasks = [(i, data[i]["answer"]) for i in range(chunk_start, chunk_end)]

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {executor.submit(translate_one, task): task[0] for task in tasks}
        done_count = 0
        for future in as_completed(futures):
            idx, translated = future.result()
            data[idx]["answer"] = translated
            done_count += 1
            if done_count % 50 == 0:
                elapsed = time.time() - t_start
                total_done = chunk_start + done_count
                rate = total_done / elapsed if elapsed > 0 else 0
                eta_min = (total - total_done) / rate / 60 if rate > 0 else 0
                sys.stdout.write(f"\r  {total_done}/{total} ({total_done*100//total}%) | {rate:.1f}/s | ETA: {eta_min:.0f}min")
                sys.stdout.flush()

    # Save after each chunk
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(chunk_end))
    elapsed = time.time() - t_start
    total_done = chunk_end
    rate = total_done / elapsed if elapsed > 0 else 0
    eta_min = (total - total_done) / rate / 60 if rate > 0 else 0
    print(f"\n  Saved {chunk_end}/{total} | {rate:.1f}/s | ETA: {eta_min:.0f}min")

# Done
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
elapsed = time.time() - t_start
print(f"\n=== DONE: {total} entries in {elapsed/60:.1f} min ===")

if os.path.exists(PROGRESS_FILE):
    os.remove(PROGRESS_FILE)
