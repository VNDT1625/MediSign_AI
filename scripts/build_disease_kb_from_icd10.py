"""Build Vietnam Disease KB from ICD-10 + FPT Cloud AI enrichment.

Pipeline:
  1. Download ICD-10 codes từ HuggingFace (atta00/icd10-codes)
  2. Filter ~17K mã bệnh có tên tiếng Anh
  3. Translate + enrich qua FPT Cloud (gemma-3-27b-it):
     - Tên tiếng Việt
     - Triệu chứng chính
     - Nguyên nhân
     - Mức độ nguy hiểm
     - Khi nào cần đi khám
  4. Ghi ra vietnam_diseases_full.json (format RAGDocument)

Usage:
  set FPT_API_KEY_1=sk-xxx
  set FPT_API_KEY_2=sk-yyy   (optional, 2nd key for parallel)
  python scripts/build_disease_kb_from_icd10.py

  # Resume nếu crash
  python scripts/build_disease_kb_from_icd10.py --resume

  # Worker mode (2 terminal song song)
  python scripts/build_disease_kb_from_icd10.py --worker-id 0 --total-workers 2
  python scripts/build_disease_kb_from_icd10.py --worker-id 1 --total-workers 2

  # Merge sau khi cả 2 worker xong
  python scripts/build_disease_kb_from_icd10.py --merge
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB_DIR = ROOT / "data" / "knowledge_base"
CACHE_DIR = ROOT / "data" / "processed"

ICD10_CACHE = CACHE_DIR / "icd10_codes_raw.json"
OUTPUT_FILE = KB_DIR / "vietnam_diseases_full.json"

BATCH_SIZE = 10  # 10 bệnh / 1 API call


# ── Download ICD-10 ────────────────────────────────────────────────────
def download_icd10() -> list[dict]:
    """Download ICD-10 codes from HuggingFace dataset."""
    if ICD10_CACHE.exists():
        print(f"[ICD-10] Loading from cache: {ICD10_CACHE}")
        return json.loads(ICD10_CACHE.read_text(encoding="utf-8"))

    print("[ICD-10] Downloading from HuggingFace (atta00/icd10-codes)...")
    try:
        from datasets import load_dataset
    except ImportError:
        print("[ERROR] pip install datasets")
        sys.exit(1)

    ds = load_dataset("atta00/icd10-codes", split="train")
    records = []
    for row in ds:
        code = str(row.get("code", "") or "").strip()
        desc = str(row.get("description", "") or row.get("long_description", "") or "").strip()
        if code and desc and len(desc) > 5:
            records.append({"code": code, "description": desc})

    print(f"[ICD-10] Downloaded {len(records)} codes")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    ICD10_CACHE.write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")
    return records


def filter_icd10(records: list[dict]) -> list[dict]:
    """Filter to meaningful disease codes.

    1. Skip external causes (Z/V/W/X/Y/U)
    2. Deduplicate by 4-char code (M17.011/M17.012/M17.019 → M17.0)
       This collapses ~25K detailed CM codes to ~5-7K base diseases.
       4-char level keeps clinical detail (subtype) but removes laterality
       (left/right/bilateral) duplicates.
    """
    skip_prefixes = ("Z", "V", "W", "X", "Y", "U")
    seen_base = {}  # 4-char base → first record

    for r in records:
        code = r["code"]
        if any(code.startswith(p) for p in skip_prefixes):
            continue
        desc = r["description"]
        if len(desc) < 10:
            continue

        # Get 4-char base (e.g., "M17.011" → "M17.0", "A00.0" → "A00.0")
        # Format: "XNN.M" — first 5 chars including dot
        if "." in code:
            base = code.split(".")[0] + "." + code.split(".")[1][:1]
        else:
            base = code[:4] if len(code) >= 4 else code

        if base not in seen_base:
            seen_base[base] = r
        else:
            # Prefer more generic ("unspecified") or shorter description
            existing_desc = seen_base[base]["description"]
            if "unspecified" in desc.lower() and "unspecified" not in existing_desc.lower():
                seen_base[base] = r
            elif len(desc) < len(existing_desc) and "unspecified" not in existing_desc.lower():
                seen_base[base] = r

    filtered = list(seen_base.values())
    for r in filtered:
        r["base_code"] = r["code"]

    print(f"[ICD-10] After filter + dedup by 4-char: {len(filtered)} unique diseases (from {len(records)} raw)")
    return filtered


# ── FPT Cloud client ───────────────────────────────────────────────────
def get_client(api_key: str | None = None):
    try:
        from openai import OpenAI
    except ImportError:
        print("[ERROR] pip install openai")
        sys.exit(1)

    key = (
        api_key
        or os.environ.get("FPT_API_KEY")
        or os.environ.get("FPT_API_KEY_1")
        or os.environ.get("DEEPSEEK_API_KEY")
        or ""
    ).strip()
    if not key:
        print("[ERROR] Set FPT_API_KEY env var")
        sys.exit(1)

    base_url = os.environ.get("DEEPSEEK_BASE_URL") or "https://mkp-api.fptcloud.com/v1"
    print(f"  API: {base_url}")
    return OpenAI(api_key=key, base_url=base_url)


def call_llm(client, model, system, user, max_tokens=6000, retries=4):
    for attempt in range(retries):
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.5,
                max_tokens=max_tokens,
                top_p=0.9,
                timeout=180,
            )
            return r.choices[0].message.content or ""
        except Exception as e:
            wait = min(60, 2 ** attempt + 2)
            print(f"  [retry {attempt+1}] {type(e).__name__}: {str(e)[:100]} — {wait}s")
            time.sleep(wait)
    return None


# ── Enrichment prompt ──────────────────────────────────────────────────
SYSTEM_PROMPT = """Bạn là bác sĩ chuyên khoa Việt Nam. Nhiệm vụ: dịch và mô tả bệnh từ ICD-10 sang tiếng Việt.

Với mỗi bệnh được cung cấp (mã ICD-10 + tên tiếng Anh), sinh 1 dòng JSON:
{
  "id": "icd10_<CODE_lowercase_no_dots>",
  "type": "vietnam_common_disease",
  "title": "<Tên tiếng Việt> (<Tên tiếng Anh>)",
  "aliases": ["<3-5 tên gọi khác tiếng Việt, gồm cả tên dân gian>"],
  "content": "<Mô tả 150-250 từ — xem cấu trúc bên dưới>",
  "confidence": "high",
  "source": {"name": "ICD-10 Vietnam — AI enriched"},
  "structured": {
    "severity": "low|medium|high",
    "icd10_code": "<CODE>",
    "category": "<nhóm bệnh tiếng Việt>",
    "specialty": "<chuyên khoa khám: nội|ngoại|sản|nhi|da liễu|tâm thần|tai mũi họng|mắt|răng hàm mặt|cấp cứu|truyền nhiễm>",
    "risk_groups": ["<đối tượng dễ mắc: trẻ em|người già|phụ nữ mang thai|người có bệnh nền|...>"],
    "symptoms": ["<6-12 keyword triệu chứng tiếng Việt CỤ THỂ — TỪ ĐƠN/CỤM NGẮN, không phải câu>"],
    "red_flags": ["<2-4 dấu hiệu nguy hiểm cần đi cấp cứu ngay>"],
    "common_complications": ["<2-3 biến chứng nếu không điều trị>"]
  }
}

CẤU TRÚC content (150-250 từ, viết liền mạch tiếng Việt):
1. Triệu chứng chính (cụ thể, để RAG matching tốt — dùng từ ngữ người dân thường nói)
2. Nguyên nhân thường gặp
3. Đối tượng dễ mắc (tuổi/giới/nghề/yếu tố nguy cơ)
4. Mức độ nguy hiểm + biến chứng nếu không điều trị
5. Khi nào cần đi khám / chuyên khoa nên đến
6. Phòng ngừa cơ bản (1-2 câu)

YÊU CẦU FIELD `symptoms`:
- 6-12 keyword/cụm ngắn TIẾNG VIỆT (mỗi cụm ≤5 từ)
- Cách dân thường gọi, KHÔNG phải thuật ngữ y học
- Ví dụ: ["đau đầu", "sốt 38-39°C", "ho khan", "đau họng", "sổ mũi", "mệt mỏi"]
- KHÔNG: ["pyrexia", "cephalgia"] (thuật ngữ Latin)

YÊU CẦU FIELD `red_flags`:
- 2-4 dấu hiệu báo NGUY HIỂM cần cấp cứu
- Ví dụ: ["sốt >40°C kéo dài", "khó thở dữ dội", "lú lẫn ý thức"]

YÊU CẦU CHUNG:
1. Output: N dòng JSONL, KHÔNG markdown, KHÔNG ```
2. Bệnh quá hiếm → vẫn mô tả đầy đủ, dù ngắn
3. Aliases bao gồm cách dân VN thường gọi
4. Triệu chứng phải concrete, không generic
5. Severity:
   - low: tự khỏi, không cần điều trị đặc biệt
   - medium: cần khám và điều trị
   - high: nguy hiểm, có thể tử vong nếu không cấp cứu"""


def enrich_batch(client, model: str, batch: list[dict]) -> list[dict]:
    """Full gen for new ICD-10 codes."""
    lines = "\n".join(f"{r['code']}: {r['description']}" for r in batch)
    prompt = f"Sinh {len(batch)} dòng JSONL cho các bệnh sau:\n\n{lines}"

    raw = call_llm(client, model, SYSTEM_PROMPT, prompt, max_tokens=10000)
    if not raw:
        return []

    results = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        if not obj.get("id") or not obj.get("content"):
            continue
        if len(obj.get("content", "")) < 100:
            continue
        s = obj.get("structured", {})
        if not isinstance(s, dict) or "icd10_code" not in s:
            continue
        symptoms = s.get("symptoms", [])
        if not isinstance(symptoms, list) or len(symptoms) < 3:
            continue
        results.append(obj)
    return results


PATCH_SYSTEM = """Bạn là bác sĩ chuyên khoa Việt Nam. Bổ sung thông tin còn thiếu cho bệnh đã có mô tả.

Với mỗi bệnh được cung cấp (id + tên + mô tả sẵn có), sinh 1 dòng JSON chỉ gồm:
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


def _needs_patch(record: dict) -> bool:
    """True nếu record thiếu symptoms hoặc red_flags."""
    s = record.get("structured") or {}
    symptoms = s.get("symptoms", [])
    return not isinstance(symptoms, list) or len(symptoms) < 3


def _merge_symptoms_into_aliases(record: dict) -> None:
    """Merge symptoms list vào aliases để BM25 match tốt hơn."""
    s = record.get("structured") or {}
    symptoms = s.get("symptoms", [])
    if not symptoms:
        return
    existing = record.get("aliases", []) or []
    merged = list(dict.fromkeys(list(existing) + list(symptoms)))
    record["aliases"] = merged[:20]


def patch_batch(client, model: str, batch: list[dict]) -> dict[str, dict]:
    """Patch a batch of existing records — only request missing fields."""
    lines = []
    for r in batch:
        lines.append(f"ID: {r['id']}")
        lines.append(f"Tên: {r.get('title', '')}")
        lines.append(f"Mô tả: {r.get('content', '')[:300]}")
        lines.append("")

    prompt = (
        f"Bổ sung symptoms/red_flags/complications cho {len(batch)} bệnh sau:\n\n"
        + "\n".join(lines)
    )
    raw = call_llm(client, model, PATCH_SYSTEM, prompt, max_tokens=8000)
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


# ── Main generation ────────────────────────────────────────────────────
def generate(
    worker_id: int | None,
    total_workers: int,
    model: str,
    resume: bool,
) -> None:
    # Determine output path
    if worker_id is not None:
        out_path = KB_DIR / f"vietnam_diseases_full_w{worker_id}.json"
        ckpt_path = ROOT / f".icd10_progress_w{worker_id}.json"
    else:
        out_path = OUTPUT_FILE
        ckpt_path = ROOT / ".icd10_progress.json"

    label = f"W{worker_id}" if worker_id is not None else "M"

    # Load ICD-10 seed
    all_codes = download_icd10()
    all_codes = filter_icd10(all_codes)

    # Assign slice to this worker (sequential split)
    if worker_id is not None and total_workers > 1:
        n = len(all_codes)
        chunk_size = (n + total_workers - 1) // total_workers
        start = worker_id * chunk_size
        end = min(start + chunk_size, n)
        all_codes = all_codes[start:end]
        print(f"[{label}] Assigned codes [{start}..{end-1}] = {len(all_codes)} entries")

    # Load existing results (from checkpoint or output file)
    existing: list[dict] = []
    if ckpt_path.exists():
        existing = json.loads(ckpt_path.read_text(encoding="utf-8"))
        print(f"[{label}] Loaded {len(existing)} from checkpoint")
    elif out_path.exists() and resume:
        existing = json.loads(out_path.read_text(encoding="utf-8"))
        print(f"[{label}] Loaded {len(existing)} from output file (resume)")

    # Build lookup: icd10_code → record index
    code_to_idx: dict[str, int] = {}
    for idx, item in enumerate(existing):
        s = item.get("structured") or {}
        code = s.get("icd10_code", "")
        if code:
            code_to_idx[code] = idx

    # Classify each code: new (need full gen) or existing (need patch)
    new_codes: list[dict] = []
    patch_records: list[dict] = []

    for r in all_codes:
        code = r["code"]
        if code not in code_to_idx:
            new_codes.append(r)
        else:
            rec = existing[code_to_idx[code]]
            if _needs_patch(rec):
                patch_records.append(rec)

    print(f"[{label}] New (full gen)  : {len(new_codes)}")
    print(f"[{label}] Existing (patch): {len(patch_records)}")
    eta_new   = len(new_codes)   // BATCH_SIZE * 15
    eta_patch = len(patch_records) // (BATCH_SIZE * 2) * 15  # patch batch = 2× larger
    print(f"[{label}] ETA: ~{(eta_new + eta_patch) // 60}h{(eta_new + eta_patch) % 60}m\n")

    client = get_client()

    # ── Phase 1: Full gen for new codes ──────────────────────────────
    if new_codes:
        print(f"[{label}] === Phase 1: Full gen ({len(new_codes)} new codes) ===")
        i = 0
        while i < len(new_codes):
            batch = new_codes[i:i + BATCH_SIZE]
            progress = i / len(new_codes) * 100
            print(
                f"[{label}][NEW {i:4d}/{len(new_codes)}] ({progress:5.1f}%) "
                f"{batch[0]['code']}..{batch[-1]['code']}",
                flush=True,
            )
            enriched = enrich_batch(client, model, batch)
            for rec in enriched:
                _merge_symptoms_into_aliases(rec)
                s = rec.get("structured") or {}
                code = s.get("icd10_code", "")
                if code and code not in code_to_idx:
                    code_to_idx[code] = len(existing)
                    existing.append(rec)
            print(f"  + {len(enriched)}/{len(batch)} (total {len(existing)})", flush=True)
            i += BATCH_SIZE
            if len(existing) % 50 < BATCH_SIZE:
                ckpt_path.write_text(json.dumps(existing, ensure_ascii=False), encoding="utf-8")
            time.sleep(0.3)

    # ── Phase 2: Patch existing records missing symptoms ─────────────
    if patch_records:
        print(f"\n[{label}] === Phase 2: Patch ({len(patch_records)} records missing symptoms) ===")
        PATCH_BATCH = 30  # patch is much cheaper (no full gen), use 3× batch size
        # Build id → index map for O(1) lookup
        id_to_idx: dict[str, int] = {r.get("id", ""): i for i, r in enumerate(existing)}
        i = 0
        patched = 0
        while i < len(patch_records):
            batch = patch_records[i:i + PATCH_BATCH]
            progress = i / len(patch_records) * 100
            print(
                f"[{label}][PATCH {i:4d}/{len(patch_records)}] ({progress:5.1f}%)",
                flush=True,
            )
            patches = patch_batch(client, model, batch)
            for iid, patch_data in patches.items():
                idx = id_to_idx.get(iid)
                if idx is None:
                    continue
                s = existing[idx].get("structured") or {}
                s["symptoms"] = patch_data["symptoms"]
                if patch_data.get("red_flags"):
                    s["red_flags"] = patch_data["red_flags"]
                if patch_data.get("common_complications"):
                    s["common_complications"] = patch_data["common_complications"]
                existing[idx]["structured"] = s
                _merge_symptoms_into_aliases(existing[idx])
                patched += 1
            print(f"  + {len(patches)}/{len(batch)} patched (total patched: {patched})", flush=True)
            i += PATCH_BATCH
            if patched % 100 < PATCH_BATCH:
                ckpt_path.write_text(json.dumps(existing, ensure_ascii=False), encoding="utf-8")
            time.sleep(0.3)

    # Final save
    KB_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    ckpt_path.write_text(json.dumps(existing, ensure_ascii=False), encoding="utf-8")

    still_missing = sum(1 for r in existing if _needs_patch(r))
    print(f"\n✅ [{label}] Done: {len(existing)} records → {out_path.relative_to(ROOT)}")
    if still_missing:
        print(f"   ⚠️  Still missing symptoms: {still_missing} (LLM parse fail)")


# ── Merge worker outputs ───────────────────────────────────────────────
def merge_workers(total_workers: int) -> None:
    print("=" * 60)
    print("Merging worker outputs...")

    seen_ids: set[str] = set()
    merged: list[dict] = []

    # Include original file if exists
    if OUTPUT_FILE.exists():
        try:
            base = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
            for item in base:
                iid = item.get("id")
                if iid and iid not in seen_ids:
                    seen_ids.add(iid)
                    merged.append(item)
            print(f"  Original: {len(merged)} records")
        except Exception:
            pass

    for w in range(total_workers):
        part = KB_DIR / f"vietnam_diseases_full_w{w}.json"
        if not part.exists():
            print(f"  [W{w}] NOT FOUND, skip")
            continue
        data = json.loads(part.read_text(encoding="utf-8"))
        added = 0
        for item in data:
            iid = item.get("id")
            if iid and iid not in seen_ids:
                seen_ids.add(iid)
                merged.append(item)
                added += 1
        print(f"  [W{w}] +{added} unique (from {len(data)} total)")

    OUTPUT_FILE.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n✅ Merged: {len(merged)} total → {OUTPUT_FILE.relative_to(ROOT)}")
    print(f"   Size: {OUTPUT_FILE.stat().st_size / 1024:.0f} KB")


# ── Entry point ────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--worker-id", type=int, default=None)
    p.add_argument("--total-workers", type=int, default=2)
    p.add_argument("--model", default="gemma-3-27b-it")
    p.add_argument("--resume", action="store_true")
    p.add_argument("--merge", action="store_true")
    args = p.parse_args()

    print("=" * 60)
    print("  ICD-10 → Vietnam Disease KB Builder")
    print(f"  Model: {args.model}")
    print("=" * 60)

    if args.merge:
        merge_workers(args.total_workers)
        return

    generate(args.worker_id, args.total_workers, args.model, args.resume)


if __name__ == "__main__":
    main()
