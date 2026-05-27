"""
Tasks 1.3 & 1.4 — Convert merged corpus to MedGemma 4B chat template
and split into train/eval.

Inputs
------
data/training_clean/medgemma_4b/merged_dataset.json
    Output of `scripts/prepare_medgemma_data.py` (Task 1.1) — list of
    {instruction, input, output, source} records.

Outputs
-------
data/training_clean/medgemma_4b/train.jsonl
    90% of records, JSONL, each line:
      {"text": <chat-template string>, "instruction": ..., "input": ...,
       "output": ..., "source": ...}
data/training_clean/medgemma_4b/eval.jsonl
    Remaining 10% in the same format.
data/training_clean/medgemma_4b/format_stats.json
    {"total": ..., "train": ..., "eval": ...,
     "disclaimer_added": ..., "disclaimer_already_present": ...}

Chat template (Task 1.3.1)
--------------------------
Gemma chat format does not have a separate `system` role, so the
system instruction is prepended to the user turn — this matches the
pattern used by Google's MedGemma examples and HuggingFace's
`google/gemma-*` chat templates:

    <start_of_turn>user
    {instruction}

    {input}<end_of_turn>
    <start_of_turn>model
    {output}<end_of_turn>

Disclaimer enforcement (Task 1.3.2)
-----------------------------------
Outputs already containing one of the common Vietnamese / English
medical-disclaimer variants are kept as-is. Otherwise the canonical
disclaimer is appended on a new paragraph:

    "Đây là gợi ý sơ bộ, không thay thế chẩn đoán bác sĩ"

Train/eval split (Task 1.4)
---------------------------
90/10 split using `random.Random(42).shuffle` — fully deterministic
for the same input list, so re-running this script produces byte-
identical train/eval files.

Usage
-----
    python scripts/format_medgemma_dataset.py
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "training_clean" / "medgemma_4b"
INPUT_FILE = DATA_DIR / "merged_dataset.json"
TRAIN_FILE = DATA_DIR / "train.jsonl"
EVAL_FILE = DATA_DIR / "eval.jsonl"
STATS_FILE = DATA_DIR / "format_stats.json"

CANONICAL_DISCLAIMER = "Đây là gợi ý sơ bộ, không thay thế chẩn đoán bác sĩ"

SPLIT_SEED = 42
TRAIN_RATIO = 0.85

# Phrases that, if present (case-insensitive), are accepted as an existing
# disclaimer and therefore prevent the canonical one from being appended.
# Generic phrases like "khám bác sĩ" are intentionally NOT included — they
# usually appear as plain medical advice, not as a disclaimer about the
# limitations of the AI's answer.
DISCLAIMER_VARIANTS: tuple[str, ...] = (
    "đây là gợi ý sơ bộ",
    "không thay thế chẩn đoán",
    "không thay thế bác sĩ",
    "không thay thế cho",          # "không thay thế cho lời khuyên của bác sĩ"
    "chỉ mang tính tham khảo",
    "mang tính chất tham khảo",
    "chỉ là tham khảo",
    "tham khảo ý kiến bác sĩ",
    "tham vấn ý kiến bác sĩ",
    "tham khảo ý kiến chuyên gia",
    "consult a doctor",
    "consult your doctor",
    "not a substitute for",
    "is not medical advice",
)


# ---------------------------------------------------------------------------
# 1.3.1 Chat template
# ---------------------------------------------------------------------------

def build_chat_text(instruction: str, user_input: str, model_output: str) -> str:
    """Render a record into MedGemma 4B's chat template.

    The system instruction is prepended to the user turn (Gemma chat
    format has no system role) — matches Google's MedGemma examples.
    """
    instruction = instruction.strip()
    user_input = user_input.strip()
    model_output = model_output.strip()

    if instruction:
        user_block = f"{instruction}\n\n{user_input}"
    else:
        user_block = user_input

    return (
        "<start_of_turn>user\n"
        f"{user_block}<end_of_turn>\n"
        "<start_of_turn>model\n"
        f"{model_output}<end_of_turn>"
    )


# ---------------------------------------------------------------------------
# 1.3.2 Disclaimer enforcement
# ---------------------------------------------------------------------------

def has_disclaimer(text: str) -> bool:
    """Return True if `text` already contains one of the accepted
    disclaimer variants (case-insensitive)."""
    low = text.lower()
    return any(variant in low for variant in DISCLAIMER_VARIANTS)


def ensure_disclaimer(text: str) -> tuple[str, bool]:
    """Return (output, was_appended).

    If `text` already contains a disclaimer variant it is returned
    unchanged. Otherwise the canonical disclaimer is appended on a new
    paragraph.
    """
    text = text.rstrip()
    if has_disclaimer(text):
        return text, False
    if not text:
        return CANONICAL_DISCLAIMER, True
    return f"{text}\n\n{CANONICAL_DISCLAIMER}", True


# ---------------------------------------------------------------------------
# Record formatter
# ---------------------------------------------------------------------------

def format_record(record: dict) -> tuple[dict, bool]:
    """Build a chat-templated record. Returns (record, disclaimer_was_appended)."""
    instruction = (record.get("instruction") or "").strip()
    user_input = (record.get("input") or "").strip()
    raw_output = (record.get("output") or "").strip()
    source = record.get("source") or ""

    output, appended = ensure_disclaimer(raw_output)
    text = build_chat_text(instruction, user_input, output)

    return (
        {
            "text": text,
            "instruction": instruction,
            "input": user_input,
            "output": output,
            "source": source,
        },
        appended,
    )


def format_records(records: Iterable[dict]) -> tuple[list[dict], int, int]:
    """Format every record. Returns (formatted, added, already_present)."""
    formatted: list[dict] = []
    added = 0
    already_present = 0
    for rec in records:
        formatted_rec, appended = format_record(rec)
        formatted.append(formatted_rec)
        if appended:
            added += 1
        else:
            already_present += 1
    return formatted, added, already_present


# ---------------------------------------------------------------------------
# 1.4 Train/eval split
# ---------------------------------------------------------------------------

def split_train_eval(
    records: list[dict],
    train_ratio: float = TRAIN_RATIO,
    seed: int = SPLIT_SEED,
) -> tuple[list[dict], list[dict]]:
    """Deterministic 90/10 split using `random.Random(seed).shuffle`.

    The shuffle is done on a copy so the input list is never mutated.
    """
    if not 0 < train_ratio < 1:
        raise ValueError(f"train_ratio must be in (0, 1), got {train_ratio}")

    shuffled = list(records)
    random.Random(seed).shuffle(shuffled)
    split_at = int(len(shuffled) * train_ratio)
    return shuffled[:split_at], shuffled[split_at:]


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------

def _display_path(path: Path) -> str:
    """Best-effort relative path for logging; falls back to absolute."""
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def write_jsonl(path: Path, records: Iterable[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False))
            fh.write("\n")
            count += 1
    return count


def read_merged_dataset(path: Path = INPUT_FILE) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"Expected merged dataset at {path}. Run "
            "`python scripts/prepare_medgemma_data.py` first (Task 1.1)."
        )
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    return data


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def format_dataset(
    input_file: Path = INPUT_FILE,
    train_file: Path = TRAIN_FILE,
    eval_file: Path = EVAL_FILE,
    stats_file: Path = STATS_FILE,
    train_ratio: float = TRAIN_RATIO,
    seed: int = SPLIT_SEED,
) -> dict:
    print(f"[1.3] Loading merged dataset from {_display_path(input_file)} ...")
    records = read_merged_dataset(input_file)
    print(f"  loaded: {len(records)} records")

    print("[1.3.1/1.3.2] Applying chat template + ensuring disclaimer ...")
    formatted, added, already_present = format_records(records)
    print(f"  disclaimer added:           {added}")
    print(f"  disclaimer already present: {already_present}")

    print(f"[1.4.1] Splitting 85/15 with seed={seed} ...")
    train, eval_ = split_train_eval(formatted, train_ratio=train_ratio, seed=seed)
    print(f"  train: {len(train)} ({len(train) / len(formatted):.1%})")
    print(f"  eval:  {len(eval_)} ({len(eval_) / len(formatted):.1%})")

    print(f"[1.4.2] Writing JSONL outputs ...")
    write_jsonl(train_file, train)
    write_jsonl(eval_file, eval_)
    print(f"  wrote {_display_path(train_file)}")
    print(f"  wrote {_display_path(eval_file)}")

    stats = {
        "total": len(formatted),
        "train": len(train),
        "eval": len(eval_),
        "disclaimer_added": added,
        "disclaimer_already_present": already_present,
        "seed": seed,
        "train_ratio": train_ratio,
        "input_file": _display_path(input_file),
        "train_file": _display_path(train_file),
        "eval_file": _display_path(eval_file),
    }
    stats_file.parent.mkdir(parents=True, exist_ok=True)
    with stats_file.open("w", encoding="utf-8") as fh:
        json.dump(stats, fh, ensure_ascii=False, indent=2)
    print(f"  wrote {_display_path(stats_file)}")
    return stats


if __name__ == "__main__":
    format_dataset()
