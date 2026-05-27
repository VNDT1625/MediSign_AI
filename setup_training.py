"""
MediSign Training Setup Script
===============================
Chạy script này 1 lần trước khi train để chuẩn bị toàn bộ dataset.

Usage:
    python setup_training.py

Sau khi chạy xong, chỉ cần:
    python scripts/train_qlora_medgemma.py
"""
import json
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

DATA_DIR = ROOT / "data" / "training_clean" / "medgemma_4b"
TRAIN_FILE = DATA_DIR / "train.jsonl"
EVAL_FILE  = DATA_DIR / "eval.jsonl"

def step(msg: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print('='*60)

def ok(msg: str) -> None:
    print(f"  ✓ {msg}")

def warn(msg: str) -> None:
    print(f"  ⚠ {msg}")

def fail(msg: str) -> None:
    print(f"  ✗ {msg}")
    sys.exit(1)


# ─── Step 1: Generate output format samples V2 ───────────────────────────────
step("Step 1/3 — Generate output format samples (V2, 1200 mẫu, balanced triage)")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "gen_v2", SCRIPTS / "generate_output_format_samples_v2.py"
    )
    gen_v2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen_v2)

    records = gen_v2.generate_records(target=1200)
    stats = gen_v2.write_split(records, dry_run=False)
    ok(f"Output format: {stats['train']} train / {stats['eval']} eval")
    ok(f"Triage: {stats['triage_distribution']}")
except Exception:
    traceback.print_exc()
    fail("Output format generation failed")


# ─── Step 2: Generate OARS samples ───────────────────────────────────────────
step("Step 2/3 — Generate OARS samples (template-only, 2000 mẫu)")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "gen_oars", SCRIPTS / "generate_vi_oars_samples.py"
    )
    gen_oars = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen_oars)

    gen_oars.generate(
        target=2000,
        template_only=True,
        dry_run=False,
        resume=False,
    )
    oars_train = DATA_DIR / "oars_train.jsonl"
    oars_eval  = DATA_DIR / "oars_eval.jsonl"
    n_train = sum(1 for _ in oars_train.open(encoding="utf-8"))
    n_eval  = sum(1 for _ in oars_eval.open(encoding="utf-8"))
    ok(f"OARS: {n_train} train / {n_eval} eval")
except Exception:
    traceback.print_exc()
    fail("OARS generation failed")


# ─── Step 3: Rebuild final dataset ───────────────────────────────────────────
step("Step 3/3 — Rebuild final training dataset (85/15 split)")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "build", SCRIPTS / "build_medgemma_rag_training_set.py"
    )
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)

    stats = build.build_training_set()
    ok(f"Dataset built: {stats['train']} train / {stats['eval']} eval / {stats['total']} total")
    ok(f"Sources: {list(stats['train_source_counts'].keys())}")
except Exception:
    traceback.print_exc()
    fail("Dataset build failed")


# ─── Final verification ───────────────────────────────────────────────────────
step("Verification")

# Check files exist and have content
for f, label in [(TRAIN_FILE, "train.jsonl"), (EVAL_FILE, "eval.jsonl")]:
    if not f.exists():
        fail(f"Missing: {label}")
    lines = f.read_text(encoding="utf-8").strip().splitlines()
    if len(lines) < 100:
        fail(f"{label} too small: {len(lines)} lines")
    # Spot-check first record
    try:
        rec = json.loads(lines[0])
        assert "text" in rec, "Missing 'text' field"
        assert "<start_of_turn>" in rec["text"], "Missing chat template"
    except Exception as e:
        fail(f"{label} format invalid: {e}")
    ok(f"{label}: {len(lines):,} records — format OK")

# Check eval ratio
n_train = sum(1 for _ in TRAIN_FILE.open(encoding="utf-8"))
n_eval  = sum(1 for _ in EVAL_FILE.open(encoding="utf-8"))
ratio = n_eval / (n_train + n_eval)
ok(f"Split ratio: {n_train:,} train / {n_eval:,} eval ({ratio:.1%} eval)")
if ratio < 0.12 or ratio > 0.20:
    warn(f"Eval ratio {ratio:.1%} outside expected 12-20% range")

# Check model path
model_id = "google/medgemma-1.5-4b-it"
ok(f"Model: {model_id}")

print(f"""
{'='*60}
  ✅  SETUP COMPLETE — Dataset sẵn sàng để train!
{'='*60}

Bước tiếp theo:
  1. Đảm bảo đã login HuggingFace:
       huggingface-cli login

  2. Chạy training:
       python scripts/train_qlora_medgemma.py

  3. Hoặc smoke test (5 bước để kiểm tra GPU/env):
       python scripts/train_qlora_medgemma.py --max_steps 5

Train config:
  Model    : {model_id}
  Method   : QLoRA r=32 alpha=64
  Epochs   : 3
  Train    : {n_train:,} records
  Eval     : {n_eval:,} records
  Output   : output/medisign_medgemma4b/adapter/
{'='*60}
""")
