"""
Download 3 HuggingFace teacher datasets cho OARS Bước 2 training.

Datasets:
  1. anuradha1992/Motivational-Interviewing-Dataset
       ~2K hội thoại có nhãn MITI — gold standard OARS labels
  2. Amod/mental_health_counseling_conversations
       Hội thoại 1-1 thật, validate cảm xúc tốt
  3. ShenLab/MentalChat16K
       16K cặp Q&A lo âu / trầm cảm / grief

Output:
    data/training_raw/oars_teacher/motivational_interviewing.json
    data/training_raw/oars_teacher/counseling_conversations.json
    data/training_raw/oars_teacher/mentalchat16k.json
    data/training_raw/oars_teacher/summary.json

Usage:
    python scripts/download_oars_datasets.py
    python scripts/download_oars_datasets.py --hf-token YOUR_TOKEN
    python scripts/download_oars_datasets.py --only mi   # chỉ download 1 dataset
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "training_raw" / "oars_teacher"

# ---------------------------------------------------------------------------
# Dataset configs
# ---------------------------------------------------------------------------

DATASETS: list[dict[str, Any]] = [
    {
        "key": "mi",
        "hf_name": "anuradha1992/Motivational-Interviewing-Dataset",
        "split": "train",
        "output_file": "motivational_interviewing.json",
        "description": "~2K MITI-labeled Motivational Interviewing dialogs — gold standard OARS",
        # Columns vary by version — we discover at runtime
        "dialog_cols": ["conversation", "dialogue", "text", "utterances"],
        "speaker_cols": ["speaker", "role", "utterance_type"],
    },
    {
        "key": "counseling",
        "hf_name": "Amod/mental_health_counseling_conversations",
        "split": "train",
        "output_file": "counseling_conversations.json",
        "description": "Real 1-on-1 counseling conversations — good emotional validation examples",
        "context_col": "Context",
        "response_col": "Response",
    },
    {
        "key": "mentalchat",
        "hf_name": "ShenLab/MentalChat16K",
        "split": "train",
        "output_file": "mentalchat16k.json",
        "description": "16K mental health Q&A covering anxiety / depression / grief",
        "input_col": "input",
        "output_col": "output",
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _try_import_datasets() -> Any:
    try:
        from datasets import load_dataset  # type: ignore
        return load_dataset
    except ImportError:
        print(
            "[ERROR] `datasets` package not found.\n"
            "Install it with:  pip install datasets>=3.0"
        )
        sys.exit(1)


def _display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _write_json(path: Path, data: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def _first_valid_col(columns: list[str], candidate_cols: list[str]) -> str | None:
    for c in candidate_cols:
        if c in columns:
            return c
    return None


# ---------------------------------------------------------------------------
# Per-dataset downloaders
# ---------------------------------------------------------------------------

def _download_mi(load_dataset: Any, cfg: dict, token: str | None) -> list[dict]:
    """Motivational Interviewing Dataset — structure varies by version."""
    print(f"  Loading {cfg['hf_name']} ...")
    ds = load_dataset(cfg["hf_name"], split=cfg["split"], token=token, trust_remote_code=True)
    cols = ds.column_names
    print(f"  Columns: {cols}")
    print(f"  Rows:    {len(ds)}")

    records: list[dict] = []
    dialog_col = _first_valid_col(cols, cfg["dialog_cols"])

    for row in ds:
        if dialog_col and row.get(dialog_col):
            raw = row[dialog_col]
            # Some versions store list-of-dicts, some store raw text
            if isinstance(raw, list):
                messages = []
                for utt in raw:
                    if isinstance(utt, dict):
                        role = str(utt.get("speaker", utt.get("role", "unknown"))).lower()
                        text = str(utt.get("text", utt.get("utterance", utt.get("content", ""))))
                        messages.append({"role": role, "content": text})
                    else:
                        messages.append({"role": "unknown", "content": str(utt)})
                records.append({
                    "messages": messages,
                    "source": "anuradha1992/Motivational-Interviewing-Dataset",
                    "raw_row": {k: v for k, v in row.items() if k != dialog_col},
                })
            else:
                # Plain text conversation
                records.append({
                    "text": str(raw),
                    "source": "anuradha1992/Motivational-Interviewing-Dataset",
                    "meta": {k: v for k, v in row.items() if k != dialog_col},
                })
        else:
            # Fallback: keep all columns as-is
            records.append({**row, "source": "anuradha1992/Motivational-Interviewing-Dataset"})

    return records


def _download_counseling(load_dataset: Any, cfg: dict, token: str | None) -> list[dict]:
    """Amod/mental_health_counseling_conversations — Context + Response."""
    print(f"  Loading {cfg['hf_name']} ...")
    ds = load_dataset(cfg["hf_name"], split=cfg["split"], token=token, trust_remote_code=True)
    cols = ds.column_names
    print(f"  Columns: {cols}")
    print(f"  Rows:    {len(ds)}")

    ctx_col = cfg.get("context_col", "Context")
    res_col = cfg.get("response_col", "Response")
    if ctx_col not in cols:
        ctx_col = _first_valid_col(cols, ["context", "question", "input", "Context"]) or cols[0]
    if res_col not in cols:
        res_col = _first_valid_col(cols, ["response", "answer", "output", "Response"]) or cols[1]

    records: list[dict] = []
    for row in ds:
        records.append({
            "messages": [
                {"role": "user", "content": str(row.get(ctx_col, ""))},
                {"role": "assistant", "content": str(row.get(res_col, ""))},
            ],
            "source": "Amod/mental_health_counseling_conversations",
        })
    return records


def _download_mentalchat(load_dataset: Any, cfg: dict, token: str | None) -> list[dict]:
    """ShenLab/MentalChat16K — input + output pairs."""
    print(f"  Loading {cfg['hf_name']} ...")
    ds = load_dataset(cfg["hf_name"], split=cfg["split"], token=token, trust_remote_code=True)
    cols = ds.column_names
    print(f"  Columns: {cols}")
    print(f"  Rows:    {len(ds)}")

    in_col  = cfg.get("input_col",  "input")
    out_col = cfg.get("output_col", "output")
    if in_col not in cols:
        in_col  = _first_valid_col(cols, ["input", "question", "context"]) or cols[0]
    if out_col not in cols:
        out_col = _first_valid_col(cols, ["output", "answer", "response"]) or cols[1]

    records: list[dict] = []
    for row in ds:
        records.append({
            "messages": [
                {"role": "user",      "content": str(row.get(in_col,  ""))},
                {"role": "assistant", "content": str(row.get(out_col, ""))},
            ],
            "source": "ShenLab/MentalChat16K",
        })
    return records


_DOWNLOADERS = {
    "mi":          _download_mi,
    "counseling":  _download_counseling,
    "mentalchat":  _download_mentalchat,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def download_all(only: str | None = None, hf_token: str | None = None) -> dict:
    load_dataset = _try_import_datasets()
    token = hf_token or os.environ.get("HF_TOKEN")

    summary: dict[str, Any] = {"datasets": {}}
    targets = [d for d in DATASETS if only is None or d["key"] == only]

    if not targets:
        print(f"[ERROR] Unknown key '{only}'. Valid: {[d['key'] for d in DATASETS]}")
        sys.exit(1)

    for cfg in targets:
        key  = cfg["key"]
        name = cfg["hf_name"]
        out  = OUTPUT_DIR / cfg["output_file"]

        print(f"\n{'='*60}")
        print(f"Dataset: {name}")
        print(f"  {cfg['description']}")
        print(f"  → {_display(out)}")

        try:
            records = _DOWNLOADERS[key](load_dataset, cfg, token)
        except Exception as exc:
            print(f"  [ERROR] Failed to download: {exc}")
            summary["datasets"][key] = {"status": "error", "error": str(exc)}
            continue

        _write_json(out, records)
        print(f"  Saved {len(records):,} records → {_display(out)}")

        summary["datasets"][key] = {
            "status":  "ok",
            "hf_name": name,
            "records": len(records),
            "file":    str(out.relative_to(ROOT)),
        }

    # Summary
    total = sum(v.get("records", 0) for v in summary["datasets"].values())
    summary["total_records"] = total
    summary_path = OUTPUT_DIR / "summary.json"
    _write_json(summary_path, summary)

    print(f"\n{'='*60}")
    print(f"Done. Total records: {total:,}")
    print(f"Summary → {_display(summary_path)}")
    return summary


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--hf-token", default=None, help="HuggingFace access token (or set HF_TOKEN env var)")
    p.add_argument(
        "--only",
        choices=["mi", "counseling", "mentalchat"],
        default=None,
        help="Download only one dataset (mi / counseling / mentalchat)",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    download_all(only=args.only, hf_token=args.hf_token)
