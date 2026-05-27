"""Patch existing disease KB records that are missing 'symptoms' field.

Chỉ re-enrich các record thiếu structured.symptoms, giữ nguyên record đã có.

Usage:
  set FPT_API_KEY=sk-xxx
  python scripts/patch_disease_symptoms.py --input data/knowledge_base/vietnam_diseases_full_w0.json
  python scripts/patch_disease_symptoms.py --input data/knowledge_base/vietnam_diseases_full_w1.json

  # Hoặc patch file final sau merge:
  python scripts/patch_disease_symptoms.py --input data/knowledge_base/vietnam_diseases_full.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_SIZE = 10

PATCH_SYSTEM = """Bạn là bác sĩ chuyên khoa Việt Nam. Nhiệm vụ: bổ sung thông tin triệu chứng còn thiếu.

Với mỗi bệnh được cung cấp (tên tiếng Việt + mô tả), sinh 1 dòng JSON chỉ gồm:
{
  "id": "<id của bệnh>",
  "symptoms": ["<6-12 keyword triệu chứng tiếng Việt ngắn gọn>"],
  "red_flags": ["<2-4 dấu hiệu nguy hiểm cần cấp cứu>"],
  "common_complications": ["<2-3 biến chứng nếu không điều trị>"]
}

YÊU CẦU symptoms:
- 6-12 keyword/cụm ngắn TIẾNG VIỆT (mỗi cụm ≤5 từ)
- Cách dân thường gọi, KHÔNG thuật ngữ Latin
- Ví dụ: ["đau đầu", "sốt 38-39°C", "ho khan", "đau họng", "mệt mỏi"]

Output: N dòng JSONL, KHÔNG markdown, KHÔNG ```"""


def get_client():
    try:
        from openai import OpenAI
    except ImportError:
        print("[ERROR] pip install openai")
        sys.exit(1)
    key = (
        os.environ.get("FPT_API_KEY")
        or os.environ.get("FPT_API_KEY_1")
        or os.environ.get("DEEPSEEK_API_KEY")
        or ""
    ).strip()
    if not key:
        print("[ERROR] Set FPT_API_KEY")
        sys.exit(1)
    base_url = os.environ.get("DEEPSEEK_BASE_URL") or "https://mkp-api.fptcloud.com/v1"
    return OpenAI(api_key=key, base_url=base_url)


def call_llm(client, model, system, user, retries=4):
    for attempt in range(retries):
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.4,
                max_tokens=6000,
                timeout=120,
            )
            return r.choices[0].message.content or ""
        except Exception as e:
            wait = min(60, 2 ** attempt + 2)
            print(f"  [retry {attempt+1}] {type(e).__name__}: {str(e)[:80]} — {wait}s")
            time.sleep(wait)
    return None


def patch_batch(client, model, batch: list[dict]) -> dict[str, dict]:
    """Return dict: id → {symptoms, red_flags, common_complications}"""
    lines = []
    for r in batch:
        lines.append(f"ID: {r['id']}")
        lines.append(f"Tên: {r.get('title', '')}")
        lines.append(f"Mô tả: {r.get('content', '')[:300]}")
        lines.append("")

    prompt = f"Bổ sung symptoms/red_flags/complications cho {len(batch)} bệnh sau:\n\n" + "\n".join(lines)

    raw = call_llm(client, model, PATCH_SYSTEM, prompt)
    if not raw:
        return {}

    result = {}
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        iid = obj.get("id")
        symptoms = obj.get("symptoms", [])
        if iid and isinstance(symptoms, list) and len(symptoms) >= 3:
            result[iid] = {
                "symptoms": symptoms,
                "red_flags": obj.get("red_flags", []),
                "common_complications": obj.get("common_complications", []),
            }
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Path to disease JSON file to patch")
    p.add_argument("--model", default="gemma-3-27b-it")
    args = p.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"[ERROR] File not found: {in_path}")
        sys.exit(1)

    print(f"Loading: {in_path}")
    records = json.loads(in_path.read_text(encoding="utf-8"))
    print(f"Total records: {len(records)}")

    # Find records missing symptoms
    need_patch = []
    for r in records:
        s = r.get("structured", {})
        if not isinstance(s, dict):
            continue
        if not s.get("symptoms") or len(s.get("symptoms", [])) < 3:
            need_patch.append(r)

    print(f"Need patch: {len(need_patch)} records (missing symptoms)")
    if not need_patch:
        print("✅ All records already have symptoms. Nothing to do.")
        return

    client = get_client()

    # Build id → record index map
    id_to_idx = {r.get("id"): i for i, r in enumerate(records)}

    patched = 0
    i = 0
    while i < len(need_patch):
        batch = need_patch[i:i + BATCH_SIZE]
        progress = i / len(need_patch) * 100
        print(f"[{i:4d}/{len(need_patch)}] ({progress:5.1f}%) patching batch...", flush=True)

        patches = patch_batch(client, args.model, batch)

        for iid, patch_data in patches.items():
            idx = id_to_idx.get(iid)
            if idx is None:
                continue
            s = records[idx].get("structured", {})
            if not isinstance(s, dict):
                s = {}
                records[idx]["structured"] = s
            s["symptoms"] = patch_data["symptoms"]
            if patch_data.get("red_flags"):
                s["red_flags"] = patch_data["red_flags"]
            if patch_data.get("common_complications"):
                s["common_complications"] = patch_data["common_complications"]
            # Merge symptoms into aliases for BM25
            existing_aliases = records[idx].get("aliases", []) or []
            merged = list(dict.fromkeys(list(existing_aliases) + patch_data["symptoms"]))
            records[idx]["aliases"] = merged[:20]
            patched += 1

        print(f"  + {len(patches)}/{len(batch)} patched (total patched: {patched})", flush=True)

        # Save every 50
        if patched % 50 < BATCH_SIZE:
            in_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

        i += BATCH_SIZE
        time.sleep(0.3)

    # Final save
    in_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ Patched {patched} records → {in_path}")

    # Report remaining missing
    still_missing = sum(
        1 for r in records
        if len((r.get("structured") or {}).get("symptoms", [])) < 3
    )
    if still_missing:
        print(f"⚠️  Still missing symptoms: {still_missing} records (LLM failed to parse)")
    else:
        print("✅ All records now have symptoms field")


if __name__ == "__main__":
    main()
