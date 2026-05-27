"""Split training data into Medical and Psychology adapter datasets.

Medical adapter sources:
  all_medical, drug_db, drug_medicine, drug_synthetic, vn_drugs,
  vn_drugs_commercial, structured_response_training, medquad,
  medical_dialogue_2010, pubmedqa, synthetic, synthetic_v2,
  vn_symptoms_culture, generated_output_format

Psychology adapter sources:
  generated_vi_oars_template  (OARS conversations)

Usage:
    python scripts/split_dual_adapter_dataset.py
"""
from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "training_clean" / "medgemma_4b"

TRAIN_FILE = DATA_DIR / "train.jsonl"
EVAL_FILE  = DATA_DIR / "eval.jsonl"

# Output files
MEDICAL_TRAIN = DATA_DIR / "medical_train.jsonl"
MEDICAL_EVAL  = DATA_DIR / "medical_eval.jsonl"
PSYCH_TRAIN   = DATA_DIR / "psychology_train.jsonl"
PSYCH_EVAL    = DATA_DIR / "psychology_eval.jsonl"

PSYCHOLOGY_SOURCES = {"generated_vi_oars_template"}
SEED = 42


def split(input_file: Path, medical_out: Path, psych_out: Path) -> tuple[int, int]:
    medical, psych = [], []
    with input_file.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            source = record.get("source", "")
            if source in PSYCHOLOGY_SOURCES:
                psych.append(line)
            else:
                medical.append(line)

    # Shuffle for good measure
    rng = random.Random(SEED)
    rng.shuffle(medical)
    rng.shuffle(psych)

    medical_out.parent.mkdir(parents=True, exist_ok=True)
    medical_out.write_text("\n".join(medical) + "\n", encoding="utf-8")
    psych_out.write_text("\n".join(psych) + "\n", encoding="utf-8")
    return len(medical), len(psych)


def main() -> None:
    for f in [TRAIN_FILE, EVAL_FILE]:
        if not f.exists():
            print(f"[ERROR] Missing: {f}")
            print("Run `python setup_training.py` first.")
            return

    n_med_train, n_psy_train = split(TRAIN_FILE, MEDICAL_TRAIN, PSYCH_TRAIN)
    n_med_eval,  n_psy_eval  = split(EVAL_FILE,  MEDICAL_EVAL,  PSYCH_EVAL)

    print("Dataset split complete:")
    print(f"  Medical    — train: {n_med_train:,}  eval: {n_med_eval:,}")
    print(f"  Psychology — train: {n_psy_train:,}  eval: {n_psy_eval:,}")
    print()
    print(f"Files written to {DATA_DIR.relative_to(ROOT)}/")
    print(f"  {MEDICAL_TRAIN.name}")
    print(f"  {MEDICAL_EVAL.name}")
    print(f"  {PSYCH_TRAIN.name}")
    print(f"  {PSYCH_EVAL.name}")


if __name__ == "__main__":
    main()
