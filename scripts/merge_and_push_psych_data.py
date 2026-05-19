#!/usr/bin/env python3
"""
Merge Psychology Worker Outputs + Push to HuggingFace
======================================================

Tự động:
  1. Merge psychology_part_*.jsonl từ N worker (dedup theo prefix assistant)
  2. Split 85/15 train/eval
  3. Ghi psychology_train.jsonl + psychology_eval.jsonl
  4. Validate cuối cùng (sample count, format check)
  5. Push lên HuggingFace dataset thuaannn/medisign-training-data

Usage:
  # Merge 2 workers + push HF (yêu cầu HF_TOKEN env)
  python scripts/merge_and_push_psych_data.py --workers 2 --push

  # Chỉ merge, không push
  python scripts/merge_and_push_psych_data.py --workers 2

  # Tùy chỉnh repo
  python scripts/merge_and_push_psych_data.py --workers 2 --push --repo myuser/my-data
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLEAN_DIR = ROOT / "data" / "training_clean" / "medgemma_4b"

TRAIN_FILE = CLEAN_DIR / "psychology_train.jsonl"
EVAL_FILE  = CLEAN_DIR / "psychology_eval.jsonl"
STATS_FILE = CLEAN_DIR / "psychology_merge_stats.json"

TRAIN_RATIO = 0.85
SEED        = 42

CHAT_SYSTEM = (
    "Bạn là MediSign AI, trợ lý y tế tiếng Việt. "
    "Bạn lắng nghe và hỏi thêm theo phương pháp OARS để hiểu rõ tình trạng người dùng "
    "trước khi đưa ra bất kỳ gợi ý nào."
)


def to_gemma_text(messages: list[dict]) -> str:
    """Format conversation thành Gemma chat template."""
    lines = []
    first_user = True
    for m in messages:
        role = m["role"]
        content = m["content"].strip()
        if role == "user":
            if first_user:
                content = f"{CHAT_SYSTEM}\n\n{content}"
                first_user = False
            lines.append(f"<start_of_turn>user\n{content}<end_of_turn>")
        else:
            lines.append(f"<start_of_turn>model\n{content}<end_of_turn>")
    return "\n".join(lines)


def load_part(worker_id: int) -> list[dict]:
    path = CLEAN_DIR / f"psychology_part_{worker_id}.jsonl"
    if not path.exists():
        print(f"  [W{worker_id}] {path.name} — NOT FOUND, skip")
        return []
    samples = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if "messages" in obj and "topic" in obj:
                    samples.append(obj)
            except json.JSONDecodeError:
                continue
    return samples


def dedup(samples: list[dict]) -> list[dict]:
    """Dedup theo prefix 50 ký tự đầu của assistant message đầu tiên."""
    seen = set()
    out = []
    for s in samples:
        msgs = s.get("messages", [])
        first_assist = next(
            (m["content"].strip()[:50] for m in msgs if m.get("role") == "assistant"),
            None,
        )
        if first_assist and first_assist in seen:
            continue
        if first_assist:
            seen.add(first_assist)
        out.append(s)
    return out


def write_jsonl(path: Path, data: list[dict]) -> int:
    with path.open("w", encoding="utf-8") as f:
        for s in data:
            messages = s["messages"]
            rec = {
                "text":     to_gemma_text(messages),
                "messages": messages,
                "topic":    s.get("topic", ""),
                "source":   s.get("source", "deepseek_oars_vi_v2"),
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return len(data)


def validate_final(train: list[dict], eva: list[dict]) -> bool:
    """Smoke check trước khi push HF."""
    if not train or not eva:
        print("❌ Train hoặc eval empty")
        return False
    if len(train) < 100:
        print(f"❌ Train quá ít ({len(train)} samples) — chưa đủ để fine-tune")
        return False

    # Sample check first record
    sample = train[0]
    msgs = sample.get("messages", [])
    if not msgs or msgs[0].get("role") != "user":
        print("❌ First message không phải user")
        return False

    last_assist = next(
        (m["content"] for m in reversed(msgs) if m.get("role") == "assistant"),
        None,
    )
    if not last_assist or not last_assist.rstrip().endswith("?"):
        print("⚠️  Last assistant không kết thúc bằng '?' — kiểm tra OARS rule")

    print(f"✅ Train sample format OK")
    return True


def push_hf(repo_id: str, files: list[Path], token: str) -> bool:
    """Push files lên HuggingFace dataset."""
    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("❌ huggingface_hub chưa cài. Run: pip install huggingface_hub")
        return False

    print(f"\nPushing → https://huggingface.co/datasets/{repo_id} ...")
    api = HfApi(token=token.strip())
    try:
        api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True, private=False)
        for f in files:
            print(f"  Uploading {f.name} ({f.stat().st_size/1024:.0f} KB)...")
            api.upload_file(
                path_or_fileobj=str(f),
                path_in_repo=f.name,
                repo_id=repo_id,
                repo_type="dataset",
                commit_message=f"update {f.name} from worker merge",
            )
        print(f"✅ HF push OK: https://huggingface.co/datasets/{repo_id}")
        return True
    except Exception as e:
        print(f"❌ HF push failed: {e}")
        return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, required=True,
                   help="Số worker (sẽ load psychology_part_0..N-1.jsonl)")
    p.add_argument("--push", action="store_true",
                   help="Push lên HuggingFace sau khi merge")
    p.add_argument("--repo", default="thuaannn/medisign-training-data",
                   help="HuggingFace dataset repo (default: thuaannn/medisign-training-data)")
    p.add_argument("--no-shuffle", action="store_true",
                   help="Không shuffle trước khi split (default: shuffle)")
    args = p.parse_args()

    print("═" * 60)
    print(f"Merging {args.workers} worker output files...")
    print("═" * 60)

    all_samples = []
    per_worker = {}
    for w in range(args.workers):
        s = load_part(w)
        per_worker[w] = len(s)
        print(f"  [W{w}] loaded {len(s)} samples")
        all_samples.extend(s)

    print(f"\nTotal raw: {len(all_samples)}")

    # Dedup cross-worker
    deduped = dedup(all_samples)
    print(f"After dedup: {len(deduped)} (removed {len(all_samples) - len(deduped)} duplicates)")

    if not deduped:
        print("❌ Nothing to write")
        sys.exit(1)

    # Shuffle + split
    rng = random.Random(SEED)
    if not args.no_shuffle:
        rng.shuffle(deduped)
    split = int(len(deduped) * TRAIN_RATIO)
    train, eva = deduped[:split], deduped[split:]

    # Write
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    n_train = write_jsonl(TRAIN_FILE, train)
    n_eval  = write_jsonl(EVAL_FILE, eva)
    print(f"\nWrote:")
    print(f"  Train: {n_train:,} → {TRAIN_FILE.relative_to(ROOT)}")
    print(f"  Eval : {n_eval:,} → {EVAL_FILE.relative_to(ROOT)}")

    # Topic distribution
    topics = Counter(s.get("topic", "?") for s in deduped)
    print(f"\nTop 10 topics:")
    for t, n in topics.most_common(10):
        print(f"  {t:<28} {n}")

    # Validate
    print()
    if not validate_final(train, eva):
        print("⚠️  Validation cảnh báo — kiểm tra trước khi push")

    # Stats
    stats = {
        "merged_total":  len(deduped),
        "raw_total":     len(all_samples),
        "duplicates":    len(all_samples) - len(deduped),
        "train":         n_train,
        "eval":          n_eval,
        "topics":        dict(topics.most_common()),
        "per_worker":    per_worker,
    }
    STATS_FILE.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nStats: {STATS_FILE.relative_to(ROOT)}")

    # Push HF
    if args.push:
        token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
        if not token:
            print("\n❌ HF_TOKEN env không set. Skip push.")
            print("   Run: set HF_TOKEN=hf_xxx (Windows CMD)")
            sys.exit(1)
        ok = push_hf(args.repo, [TRAIN_FILE, EVAL_FILE], token)
        if not ok:
            sys.exit(1)

    print("\n" + "═" * 60)
    print(f"DONE — {len(deduped):,} unique samples")
    print("═" * 60)


if __name__ == "__main__":
    main()
