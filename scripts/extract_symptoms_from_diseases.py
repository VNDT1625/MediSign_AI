"""Extract unique Vietnamese symptom phrases from disease KB.

Sau khi gen xong vietnam_diseases_full.json (~7000 bệnh):
  - Mỗi bệnh có 6-12 symptoms
  - Tổng có thể lên 40K-80K phrases
  - Dedup → còn ~3K-5K cụm từ unique

Output: vietnamese_symptom_phrases.json (mở rộng từ 261)

Usage:
  python scripts/extract_symptoms_from_diseases.py
"""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB_DIR = ROOT / "data" / "knowledge_base"

DISEASE_FILE = KB_DIR / "vietnam_diseases_full.json"
SYMPTOM_FILE = KB_DIR / "vietnamese_symptom_phrases.json"


def normalize(s: str) -> str:
    """Normalize for dedup: lowercase, trim, collapse whitespace."""
    s = re.sub(r"\s+", " ", s.lower().strip())
    s = s.rstrip(".,;:")
    return s


def main():
    if not DISEASE_FILE.exists():
        print(f"[ERROR] Chưa có {DISEASE_FILE.name} — chạy gen trước")
        return

    diseases = json.loads(DISEASE_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(diseases)} diseases")

    # Collect symptoms with disease references
    symptom_to_diseases: dict[str, list[str]] = {}  # normalized symptom → [disease ids]
    symptom_canonical: dict[str, str] = {}  # normalized → original (best form)

    for d in diseases:
        s = d.get("structured") or {}
        symptoms = s.get("symptoms", [])
        if not isinstance(symptoms, list):
            continue
        disease_id = d.get("id", "")
        for sym in symptoms:
            if not isinstance(sym, str):
                continue
            sym = sym.strip()
            if not sym or len(sym) > 80:  # skip too long
                continue
            norm = normalize(sym)
            if not norm or len(norm) < 3:
                continue
            symptom_to_diseases.setdefault(norm, []).append(disease_id)
            # Keep first occurrence as canonical (or shortest)
            if norm not in symptom_canonical or len(sym) < len(symptom_canonical[norm]):
                symptom_canonical[norm] = sym

    print(f"Unique symptoms: {len(symptom_canonical)}")

    # Filter: keep symptoms that appear in ≥1 disease
    counter = Counter({k: len(v) for k, v in symptom_to_diseases.items()})
    print(f"\nTop 20 most common symptoms:")
    for sym, n in counter.most_common(20):
        print(f"  {symptom_canonical[sym]:<30} → {n} diseases")

    # Build symptom records
    records = []
    for norm, canonical in symptom_canonical.items():
        n_diseases = len(symptom_to_diseases[norm])
        diseases_refs = symptom_to_diseases[norm][:5]  # cap at 5
        records.append({
            "id": f"symptom_{re.sub(r'[^a-z0-9]+', '_', norm)[:50]}",
            "type": "vietnamese_symptom_phrase",
            "title": canonical,
            "aliases": [canonical, norm],
            "content": (
                f"Triệu chứng '{canonical}' xuất hiện trong {n_diseases} bệnh "
                f"(theo CSDL ICD-10 enriched). Liên quan đến: "
                + ", ".join(diseases_refs[:3])
            ),
            "confidence": "high" if n_diseases >= 2 else "medium",
            "source": {"name": "Extracted from ICD-10 disease KB"},
            "structured": {
                "category": "extracted_symptom",
                "disease_count": n_diseases,
                "related_disease_ids": diseases_refs,
            },
        })

    # Merge with existing symptom file (preserve manually-curated entries)
    if SYMPTOM_FILE.exists():
        existing = json.loads(SYMPTOM_FILE.read_text(encoding="utf-8"))
        if isinstance(existing, list):
            existing_titles = {normalize(item.get("title", "")) for item in existing if isinstance(item, dict)}
            new_records = [r for r in records if normalize(r["title"]) not in existing_titles]
            print(f"\nExisting: {len(existing)} | New: {len(new_records)}")
            records = existing + new_records
        else:
            print(f"\nWARN: existing file is not a list, overwriting")
    else:
        existing = []

    SYMPTOM_FILE.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    size_kb = SYMPTOM_FILE.stat().st_size / 1024
    print(f"\n✅ Wrote {len(records)} records → {SYMPTOM_FILE.relative_to(ROOT)} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
