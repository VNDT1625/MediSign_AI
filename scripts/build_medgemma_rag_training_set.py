"""Build final MedGemma train/eval files for RAG diagnostic chat.

This combines:
  - Step 1 base medical QA from merged_dataset.json
  - Step 2 Vietnamese OARS conversation samples
  - Step 3 diagnostic output-format samples

The script always rebuilds Step 1 from merged_dataset.json, so rerunning it
does not duplicate Step 2/3 records inside train.jsonl/eval.jsonl.

Usage:
    python scripts/build_medgemma_rag_training_set.py
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Iterable

import format_medgemma_dataset as base_format


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "training_clean" / "medgemma_4b"

BASE_MERGED_FILE = DATA_DIR / "merged_dataset.json"
TRAIN_FILE = DATA_DIR / "train.jsonl"
EVAL_FILE = DATA_DIR / "eval.jsonl"
STATS_FILE = DATA_DIR / "rag_training_set_stats.json"

EXTRA_TRAIN_FILES = [
    DATA_DIR / "oars_train.jsonl",
    DATA_DIR / "output_format_train.jsonl",
]
EXTRA_EVAL_FILES = [
    DATA_DIR / "oars_eval.jsonl",
    DATA_DIR / "output_format_eval.jsonl",
]

SEED = 42


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if not isinstance(record, dict) or not record.get("text"):
                raise ValueError(f"Invalid JSONL record at {path}:{line_no}")
            rows.append(record)
    return rows


def _write_jsonl(path: Path, rows: Iterable[dict]) -> int:
    count = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def _source_counts(rows: Iterable[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        source = str(row.get("source") or "unknown")
        counts[source] = counts.get(source, 0) + 1
    return dict(sorted(counts.items()))


def build_training_set() -> dict:
    base_records = base_format.read_merged_dataset(BASE_MERGED_FILE)
    base_formatted, disclaimer_added, disclaimer_present = base_format.format_records(base_records)
    base_train, base_eval = base_format.split_train_eval(base_formatted)

    train_parts = [base_train]
    eval_parts = [base_eval]
    extra_stats: dict[str, int] = {}

    for path in EXTRA_TRAIN_FILES:
        rows = _read_jsonl(path)
        train_parts.append(rows)
        extra_stats[path.name] = len(rows)

    for path in EXTRA_EVAL_FILES:
        rows = _read_jsonl(path)
        eval_parts.append(rows)
        extra_stats[path.name] = len(rows)

    train_rows = [row for part in train_parts for row in part]
    eval_rows = [row for part in eval_parts for row in part]
    random.Random(SEED).shuffle(train_rows)
    random.Random(SEED + 1).shuffle(eval_rows)

    train_count = _write_jsonl(TRAIN_FILE, train_rows)
    eval_count = _write_jsonl(EVAL_FILE, eval_rows)

    stats = {
        "total": train_count + eval_count,
        "train": train_count,
        "eval": eval_count,
        "base": {
            "records": len(base_formatted),
            "train": len(base_train),
            "eval": len(base_eval),
            "disclaimer_added": disclaimer_added,
            "disclaimer_already_present": disclaimer_present,
        },
        "extras": extra_stats,
        "train_source_counts": _source_counts(train_rows),
        "eval_source_counts": _source_counts(eval_rows),
        "seed": SEED,
    }
    STATS_FILE.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    return stats


if __name__ == "__main__":
    print(json.dumps(build_training_set(), ensure_ascii=False, indent=2))
