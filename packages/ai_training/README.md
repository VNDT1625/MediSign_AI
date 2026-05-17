# AI Training Documentation

> Quick Start: xem `QUICKSTART.md`.

Huong train hien tai cua MediSign AI la **MedGemma 4B + QLoRA medical adapter**.

## Deployment Modes

```text
+--------------------+----------------------+----------------------+
| Mode               | Runtime              | Purpose              |
+--------------------+----------------------+----------------------+
| Backend fallback   | Rule-based services  | Always available     |
| Medical AI         | MedGemma 4B server   | Medical assistant    |
| Hybrid             | Rule-based + AI + RAG| Safer production UX  |
+--------------------+----------------------+----------------------+
```

## Model Can Train

### Medical Adapter

| Thanh phan | Mo ta |
| --- | --- |
| Base model | `google/medgemma-4b-it` |
| Adapter | QLoRA Medical Adapter |
| Train data | `data/training_clean/medgemma_4b/train.jsonl` |
| Eval data | `data/training_clean/medgemma_4b/eval.jsonl` |
| Output | `output/medisign_medgemma4b/adapter/` |

Medical adapter can hoc:

- Hoi dap y te tieng Viet
- Trieu chung va goi y muc do can chu y
- Thuoc Viet Nam, hoat chat, dang bao che, so dang ky
- Tinh than safety: khong chan doan chac chan, khuyen gap bac si khi can

### Personal/Psychology Adapter

Adapter ca nhan hoa va SoulGarden van la muc tieu sau. Hien chua co dataset train rieng du chat luong trong repo.

## Data Directories

```text
data/
├── training_raw/        # Raw training data
├── training_clean/      # Cleaned training data
└── eval_sets/           # Fixed evaluation sets
```

## Current MedGemma Corpus

```text
data/training_clean/medgemma_4b/
├── merged_dataset.json  # 17,196 records sau dedup
├── train.jsonl          # 15,476 records
├── eval.jsonl           # 1,720 records
├── merge_stats.json
└── format_stats.json
```

Nguon chinh:

| Source | Records |
| --- | ---: |
| `all_medical` | 12,391 |
| `medquad` | 1,362 |
| `drug_db` | 968 |
| `medical_dialogue_2010` | 800 |
| `vn_drugs_commercial` | 576 |
| `vn_symptoms_culture` | 224 |

## Training Pipeline

```text
Step 1: Collect / crawl / translate data
Step 2: Merge and deduplicate
Step 3: Apply MedGemma chat template
Step 4: Split train/eval
Step 5: Train QLoRA adapter
Step 6: Evaluate safety and quality
Step 7: Deploy adapter behind OpenAI-compatible runtime
```

Commands:

```bash
python scripts/prepare_medgemma_data.py
python scripts/format_medgemma_dataset.py
python scripts/train_qlora_medgemma_smoke_test.py
python scripts/train_qlora_medgemma.py
```

## Current Implementation Status

| Component | Status | Notes |
| --- | --- | --- |
| Rule-based triage | Done | Keyword matching, Vietnamese normalization |
| Drug lookup database | Done/MVP | DAV-backed database available |
| MedGemma 4B medical adapter | Ready to train | Main training path |
| Fixed eval sets | Incomplete | `data/eval_sets` needs real cases |
| Personal adapter | Planned | Needs separate data |
| Vision drug classifier | Not ready | Needs real medicine images |

## Medicine Recognition

Current implementation is lookup-first:

```text
Image or text
    |
    v
OCR / vision runtime extracts drug name
    |
    v
Backend drug lookup
    |
    v
Drug info + warnings
```

For direct image classification, the project still needs:

- 10,000+ labeled medicine images for MVP
- Multiple views: box, blister, pill, instruction leaflet
- Labels mapped to drug name, registration number, active ingredient
- Train/eval/test split by product and capture condition

## Evaluation Priorities

Before production, add fixed eval sets for:

- Vietnamese medical QA
- Red-flag triage and emergency escalation
- Dangerous medication advice refusal
- Drug lookup correctness
- Disclaimer compliance
- Hallucination and uncertainty handling

## References

- Quick Start: `QUICKSTART.md`
- MedGemma train guide: `docs/training/QLORA_TRAINING.md`
- Data prep: `scripts/prepare_medgemma_data.py`
- Formatting: `scripts/format_medgemma_dataset.py`
- Training: `scripts/train_qlora_medgemma.py`
- Backend AI client: `apps/backend_fastapi/app/services/ai_model_service.py`
- Drug lookup: `apps/backend_fastapi/app/services/drug_lookup_service.py`
