"""Merge KB worker outputs (diseases + symptoms) → final files.

Usage:
  python scripts/merge_kb_workers.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB_DIR = ROOT / "data" / "knowledge_base"

JOBS = [
    ("vietnam_common_diseases",   "vietnam_common_diseases.json"),
    ("vietnamese_symptom_phrases", "vietnamese_symptom_phrases.json"),
]


def merge_one(stem: str, out_name: str) -> None:
    out_path = KB_DIR / out_name
    parts = sorted(KB_DIR.glob(f"{stem}_w*.json"))

    if not parts:
        print(f"[{out_name}] No worker files. Skipping.")
        return

    # Keep existing original file as one of the sources
    seen_ids = set()
    seen_titles = set()
    merged = []

    # 1. Load original (10 / 11 baseline records)
    if out_path.exists():
        try:
            base = json.loads(out_path.read_text(encoding="utf-8"))
            if isinstance(base, list):
                for item in base:
                    if not isinstance(item, dict):
                        continue
                    iid = item.get("id")
                    title = item.get("title", "").lower()
                    if iid and iid not in seen_ids and title not in seen_titles:
                        seen_ids.add(iid)
                        seen_titles.add(title)
                        merged.append(item)
                print(f"[{out_name}] Loaded {len(merged)} from original")
        except Exception as e:
            print(f"[{out_name}] Failed to load original: {e}")

    # 2. Append worker parts
    for part in parts:
        try:
            data = json.loads(part.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  [SKIP] {part.name}: {e}")
            continue
        if not isinstance(data, list):
            continue
        added = 0
        for item in data:
            if not isinstance(item, dict):
                continue
            iid = item.get("id")
            title = item.get("title", "").lower()
            if not iid or iid in seen_ids or title in seen_titles:
                continue
            seen_ids.add(iid)
            seen_titles.add(title)
            merged.append(item)
            added += 1
        print(f"  [{part.name}] +{added} unique")

    # 3. Write final
    out_path.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"✅ [{out_name}] {len(merged)} total → {out_path.relative_to(ROOT)}\n")


def main():
    print("=" * 60)
    print("  KB Worker Merge")
    print("=" * 60)
    for stem, out in JOBS:
        merge_one(stem, out)


if __name__ == "__main__":
    main()
