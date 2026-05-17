# AI Training - Huong dan nhanh

Muc tieu hien tai: train **QLoRA medical adapter** cho `google/medgemma-1.5-4b-it`.

## Tong quan

| Phase | Method | Output |
| --- | --- | --- |
| Baseline | MedGemma 4B instruction model | Chua co adapter MediSign |
| Phase 1 | QLoRA medical adapter | `output/medisign_medgemma4b/adapter/` |
| Phase 2 | + RAG | Grounding bang knowledge base |
| Phase 3 | + Safety/logic layer | Triage va red-flag tot hon |

## Bat dau nhanh

### Buoc 1: Kiem tra data

Du lieu da duoc chuan bi san:

```text
data/training_clean/medgemma_4b/train.jsonl
data/training_clean/medgemma_4b/eval.jsonl
```

Neu can build lai:

```bash
python scripts/prepare_medgemma_data.py
python scripts/format_medgemma_dataset.py
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

### Buoc 4: Train adapter

```bash
python scripts/train_qlora_medgemma.py
```

Output:

```text
output/medisign_medgemma4b/checkpoints/
output/medisign_medgemma4b/adapter/
```

## Cau truc lien quan

```text
scripts/
├── prepare_medgemma_data.py
├── format_medgemma_dataset.py
├── train_qlora_medgemma.py
├── train_qlora_medgemma_smoke_test.py
└── requirements_train.txt

data/training_clean/medgemma_4b/
├── merged_dataset.json
├── train.jsonl
├── eval.jsonl
├── merge_stats.json
└── format_stats.json
```

## Cau hinh mac dinh

| Setting | Value |
| --- | --- |
| Base model | `google/medgemma-1.5-4b-it` |
| Max sequence length | 2048 |
| LoRA rank | 32 |
| LoRA alpha | 64 |
| LoRA dropout | 0.1 |
| Quantization | 4-bit NF4 |
| Epochs | 3 |
| Train/eval split | 90/10 |

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
