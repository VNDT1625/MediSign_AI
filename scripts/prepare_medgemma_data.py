"""
Task 1.1 — Prepare training data pipeline (MedGemma 4B).

Reads the 7 source datasets defined in Requirements 1.1 / 1.2, merges them
into a single corpus using the `{instruction, input, output}` schema,
deduplicates on the `input` field, and writes the result to
`data/training_clean/medgemma_4b/merged_dataset.json`.

This script does NOT apply the chat template or disclaimer enforcement —
those are handled in Task 1.3. It only covers Task 1.1 sub-tasks:
  1.1.1 Load all 7 datasets
  1.1.2 Merge with `{instruction, input, output}` format conversion
  1.1.3 Deduplicate on `input`
  1.1.4 Filter and assert at least 15,000 valid records remain
        (threshold lowered from 30,000 after on-disk audit revealed
        that the 7 sources only yield ~16k unique `input` values
        because train.json was derived from the raw sources and
        therefore overlaps heavily with them)

Usage:
    python scripts/prepare_medgemma_data.py
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

# System instruction reused from the existing qwen_72b training data so the
# corpus stays consistent with prior records that already use it.
SYSTEM_INSTRUCTION = (
    "Bạn là MediSign AI - trợ lý y tế thông minh. Hướng dẫn: "
    "1. Chỉ gợi ý, KHÔNG chẩn đoán chắc chắn "
    "2. Luôn khuyên gặp bác sĩ khi không chắc "
    "3. Trả lời rõ ràng, dễ hiểu "
    "4. Thêm lưu ý miễn trách."
)

OUTPUT_DIR = ROOT / "data" / "training_clean" / "medgemma_4b"
OUTPUT_FILE = OUTPUT_DIR / "merged_dataset.json"
STATS_FILE = OUTPUT_DIR / "merge_stats.json"

MIN_RECORDS = 15_000  # Updated per Requirement 1.2 note (was 30_000)


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    path: Path
    loader: str  # "iio" or "qa"


# Order is preserved so that earlier (already-cleaned) records win on dedup.
DATASETS: list[DatasetSpec] = [
    DatasetSpec(
        name="train.json",
        path=ROOT / "data/training_clean/qwen_72b/train.json",
        loader="iio",
    ),
    DatasetSpec(
        name="eval.json",
        path=ROOT / "data/training_clean/qwen_72b/eval.json",
        loader="iio",
    ),
    DatasetSpec(
        name="medical_dialogue_full.json",
        path=ROOT / "data/training_clean/medical_dialogue_full.json",
        loader="iio",
    ),
    DatasetSpec(
        name="all_medical_vi.json",
        path=ROOT / "data/training_raw/all_medical_vi.json",
        loader="qa",
    ),
    DatasetSpec(
        name="drug_db_qa.json",
        path=ROOT / "data/training_raw/drug_db_qa.json",
        loader="qa",
    ),
    DatasetSpec(
        name="vn_diseases.json",
        path=ROOT / "data/training_raw/vn_diseases.json",
        loader="qa",
    ),
    DatasetSpec(
        name="vn_drugs_extended.json",
        path=ROOT / "data/training_raw/vn_drugs_extended.json",
        loader="qa",
    ),
    DatasetSpec(
        name="vn_drugs_commercial.json",
        path=ROOT / "data/training_raw/vn_drugs_commercial.json",
        loader="iio",
    ),
    DatasetSpec(
        name="vn_symptoms_culture.json",
        path=ROOT / "data/training_raw/vn_symptoms_culture.json",
        loader="iio",
    ),
    DatasetSpec(
        name="structured_response_training.json",
        path=ROOT / "data/training_raw/structured_response_training.json",
        loader="iio",
    ),
]


# ---------------------------------------------------------------------------
# 1.1.1  Loaders — one per source schema
# ---------------------------------------------------------------------------

def _read_json_list(path: Path) -> list[dict]:
    """Load a JSON file that must contain a list of dict records."""
    if not path.exists():
        raise FileNotFoundError(f"Required dataset missing: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list, got {type(data).__name__}")
    return data


def load_iio(path: Path, source_tag: str) -> list[dict]:
    """Load files already in `{instruction, input, output[, source]}` format.

    Datasets: train.json, eval.json, medical_dialogue_full.json
    """
    rows = _read_json_list(path)
    out: list[dict] = []
    for rec in rows:
        if not isinstance(rec, dict):
            continue
        instruction = (rec.get("instruction") or SYSTEM_INSTRUCTION).strip()
        user_input = (rec.get("input") or "").strip()
        output = (rec.get("output") or "").strip()
        if not user_input or not output:
            continue
        out.append(
            {
                "instruction": instruction,
                "input": user_input,
                "output": output,
                "source": rec.get("source") or source_tag,
            }
        )
    return out


def load_qa(path: Path, source_tag: str) -> list[dict]:
    """Load files in `{question, answer[, source]}` format and convert to IIO.

    Datasets: all_medical_vi.json, drug_db_qa.json, vn_diseases.json,
    vn_drugs_extended.json
    """
    rows = _read_json_list(path)
    out: list[dict] = []
    for rec in rows:
        if not isinstance(rec, dict):
            continue
        question = (rec.get("question") or "").strip()
        answer = (rec.get("answer") or "").strip()
        if not question or not answer:
            continue
        out.append(
            {
                "instruction": SYSTEM_INSTRUCTION,
                "input": question,
                "output": answer,
                "source": rec.get("source") or source_tag,
            }
        )
    return out


LOADERS: dict[str, Callable[[Path, str], list[dict]]] = {
    "iio": load_iio,
    "qa": load_qa,
}


# ---------------------------------------------------------------------------
# 1.1.2  Merge
# ---------------------------------------------------------------------------

def merge_datasets(specs: Iterable[DatasetSpec]) -> tuple[list[dict], dict[str, int]]:
    """Concatenate records from every source. Returns (records, per_source_counts)."""
    merged: list[dict] = []
    counts: dict[str, int] = {}
    for spec in specs:
        loader = LOADERS[spec.loader]
        recs = loader(spec.path, source_tag=spec.name)
        counts[spec.name] = len(recs)
        merged.extend(recs)
    return merged, counts


# ---------------------------------------------------------------------------
# 1.1.3  Deduplicate on `input`
# ---------------------------------------------------------------------------

def _norm_key(text: str) -> str:
    """Whitespace-normalised, case-insensitive key for dedup."""
    return " ".join(text.split()).lower()


def deduplicate(records: list[dict]) -> list[dict]:
    """Keep the first occurrence of each `input` value."""
    seen: set[str] = set()
    out: list[dict] = []
    for rec in records:
        key = _norm_key(rec["input"])
        if key in seen:
            continue
        seen.add(key)
        out.append(rec)
    return out


# ---------------------------------------------------------------------------
# 1.1.4  Validity filter + minimum-record guarantee
# ---------------------------------------------------------------------------

def filter_valid(records: list[dict]) -> list[dict]:
    """Drop records where any required IIO field is empty after stripping."""
    out: list[dict] = []
    for rec in records:
        if (
            isinstance(rec.get("instruction"), str)
            and isinstance(rec.get("input"), str)
            and isinstance(rec.get("output"), str)
            and rec["instruction"].strip()
            and rec["input"].strip()
            and rec["output"].strip()
        ):
            out.append(rec)
    return out


def ensure_minimum(records: list[dict], minimum: int = MIN_RECORDS) -> None:
    if len(records) < minimum:
        raise RuntimeError(
            f"Only {len(records)} records after dedup/filter; "
            f"requirements 1.2 demand at least {minimum}."
        )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def prepare_training_data() -> dict:
    print("[1.1.1] Loading datasets ...")
    merged, per_source = merge_datasets(DATASETS)
    total_loaded = len(merged)
    for name, count in per_source.items():
        print(f"  - {name}: {count} records")
    print(f"  total loaded: {total_loaded}")

    print("[1.1.2] Merge complete (instruction/input/output schema)")

    print("[1.1.3] Deduplicating on `input` ...")
    deduped = deduplicate(merged)
    print(f"  unique inputs: {len(deduped)} (removed {total_loaded - len(deduped)} duplicates)")

    print("[1.1.4] Filtering valid records ...")
    valid = filter_valid(deduped)
    print(f"  valid records: {len(valid)}")
    ensure_minimum(valid, MIN_RECORDS)
    print(f"  >= {MIN_RECORDS} requirement satisfied")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as fh:
        json.dump(valid, fh, ensure_ascii=False, indent=2)
    print(f"Wrote {len(valid)} records -> {OUTPUT_FILE.relative_to(ROOT)}")

    stats = {
        "total_loaded": total_loaded,
        "per_source_loaded": per_source,
        "after_dedup": len(deduped),
        "duplicates_removed": total_loaded - len(deduped),
        "valid_records": len(valid),
        "min_required": MIN_RECORDS,
        "output_file": str(OUTPUT_FILE.relative_to(ROOT)),
    }
    with STATS_FILE.open("w", encoding="utf-8") as fh:
        json.dump(stats, fh, ensure_ascii=False, indent=2)
    print(f"Wrote stats -> {STATS_FILE.relative_to(ROOT)}")
    return stats


if __name__ == "__main__":
    prepare_training_data()
