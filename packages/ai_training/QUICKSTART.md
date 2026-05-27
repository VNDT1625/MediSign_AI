# AI Training - Huong dan nhanh

Muc tieu hien tai: train **2 QLoRA adapter** (Medical + Psychology) cho
`google/medgemma-1.5-4b-it`, dung chung 1 mo hinh nen.

## Tong quan

| Phase | Method | Output |
| --- | --- | --- |
| Baseline | MedGemma 4B instruction model | Chua co adapter MediSign |
| Phase 1a | QLoRA Medical adapter | `output/medisign-medgemma4b-adapter/` |
| Phase 1b | QLoRA Psychology adapter (OARS) | `output/medisign_medgemma4b_psychology/adapter/` |
| Phase 2 | + RAG-MediSign | Grounding bang knowledge base 128,380 records |
| Phase 3 | + Safety/logic layer | Triage va red-flag tot hon |

## Bat dau nhanh

### Buoc 1: Kiem tra data

Du lieu da duoc chuan bi san:

```text
data/training_clean/medgemma_4b/medical_train.jsonl       (15,693 records)
data/training_clean/medgemma_4b/medical_eval.jsonl        (2,770 records)
data/training_clean/medgemma_4b/psychology_train.jsonl    (1,201 records)
data/training_clean/medgemma_4b/psychology_eval.jsonl     (212 records)
```

Neu can build lai medical corpus:

```bash
python scripts/prepare_medgemma_data.py
python scripts/format_medgemma_dataset.py
python scripts/split_dual_adapter_dataset.py
```

Neu can regenerate psychology corpus (DeepSeek/FPT Cloud):

```bash
python scripts/regenerate_psychology_data.py --target 1500
```

### Buoc 2: Cai dependencies

```bash
pip install -r scripts/requirements_train.txt
huggingface-cli login
```

`google/medgemma-1.5-4b-it` la gated model, can chap nhan dieu khoan tren Hugging Face truoc khi train.

### Buoc 3: Smoke test

```bash
python scripts/train_qlora_medgemma_smoke_test.py
```

### Buoc 4: Train cac adapter

Notebook tren H100 (FPT Cloud / Kaggle / Colab Pro):

```text
notebooks/train_medical_adapter.ipynb       (~1-1.5 gio)
notebooks/train_psychology_adapter.ipynb    (~10-15 phut)
```

Hoac chay script truc tiep:

```bash
# Medical
python scripts/train_qlora_medgemma.py \
  --train_file data/training_clean/medgemma_4b/medical_train.jsonl \
  --eval_file  data/training_clean/medgemma_4b/medical_eval.jsonl \
  --adapter_dir output/medisign-medgemma4b-adapter

# Psychology
python scripts/train_qlora_medgemma.py \
  --train_file data/training_clean/medgemma_4b/psychology_train.jsonl \
  --eval_file  data/training_clean/medgemma_4b/psychology_eval.jsonl \
  --adapter_dir output/medisign_medgemma4b_psychology/adapter
```

Output:

```text
output/medisign-medgemma4b-adapter/                  # Medical (preload khi server start)
output/medisign_medgemma4b_psychology/adapter/       # Psychology (lazy load)
```

## Cau truc lien quan

```text
scripts/
├── prepare_medgemma_data.py
├── format_medgemma_dataset.py
├── split_dual_adapter_dataset.py
├── regenerate_psychology_data.py
├── train_qlora_medgemma.py
├── train_qlora_medgemma_smoke_test.py
├── serve_medgemma.py
├── cloud/
│   ├── h100_train_medical.py
│   ├── train_dual_adapter.sh
│   └── start-fpt-medgemma.sh
└── requirements_train.txt

data/training_clean/medgemma_4b/
├── medical_train.jsonl       # 15,693
├── medical_eval.jsonl        # 2,770
├── psychology_train.jsonl    # 1,201
├── psychology_eval.jsonl     # 212
├── train.jsonl               # 17,393 (legacy combined)
├── eval.jsonl                # 3,070  (legacy combined)
├── merged_dataset.json
├── merge_stats.json
├── format_stats.json
├── psychology_merge_stats.json
└── oars_stats.json
```

## Cau hinh mac dinh

Co 3 entry point train va dung **hyperparams khac nhau**:

| Setting | Adapter trên disk (already trained) | `train_qlora_medgemma.py` (manual) | `cloud/h100_train_medical.py` + medical notebook | `cloud/rtx4090_train_psychology.py` | `train_psychology_adapter.ipynb` |
| --- | --- | --- | --- | --- | --- |
| Medical adapter rank | **r=64, alpha=64** (250 MB) | r=32, alpha=64 | r=16, alpha=32 | — | — |
| Psychology adapter rank | **r=8, alpha=16** (62 MB) | r=32, alpha=64 | — | r=8, alpha=16 | r=16, alpha=32 |
| Dropout | medical 0.05 / psych 0.1 (deployed) | 0.05 | 0.05 | 0.1 | 0.05 |
| Max sequence length | — | 2048 | 2048 | 1024 | 2048 |
| Quantization | 4-bit NF4 | 4-bit NF4 | 4-bit NF4 | 4-bit NF4 | 4-bit NF4 |
| Epochs | — | 3 | 3 | 4 | 5 |
| Learning rate | — | 2e-4 | 2e-4 | 1e-4 | 2e-4 |
| Train/eval split | — | 90/10 (legacy combined) | 85/15 (medical_*) | 85/15 (psychology_*) | 85/15 (psychology_*) |
| Eval interval (steps) | — | 500 | 200 | 50 | 50 |
| Target modules | q/k/v/o/gate/up/down | q/k/v/o/gate/up/down | q/k/v/o/gate/up/down | q/k/v/o/gate/up/down | q/k/v/o/gate/up/down |

**Lưu ý:** Adapter Medical đang deploy (`output/medisign-medgemma4b-adapter/` + HF
`thuaannn/medisign-medgemma4b-adapter`) được train với **r=64**, không khớp default
của bất kỳ script nào trong repo hiện tại. Nếu chạy lại pipeline production
(`scripts/cloud/h100_train_medical.py`), adapter mới sẽ có r=16 — kích thước
nhỏ hơn nhưng có thể chất lượng khác.

Notebook tren H100 / RTX 4090 va cac script `scripts/cloud/*.py` la **production
default**; `scripts/train_qlora_medgemma.py` co default lon hon (rank 32) cho
cac may local nho hon, va co the override qua flag --adapter_dir / --train_file.

## Evaluation

Repo hien co script evaluation legacy trong `packages/ai_training/scripts/05_evaluate.py`, nhung bo eval co dinh cho MediSign van can duoc bo sung trong `data/eval_sets`.

Danh gia nen gom:

- Vietnamese medical QA
- Safety disclaimer
- Red-flag triage
- Drug lookup and interaction cases
- Refusal/escalation behavior for dangerous advice

## Luu y

1. AI chi ho tro, khong thay the bac si.
2. Moi response y te can co disclaimer.
3. Red flags can uu tien safety/logic layer, khong chi dua vao model.
