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
| Base model | `google/medgemma-1.5-4b-it` |
| Adapter (deployed) | QLoRA Medical Adapter on disk + HF: **r=64, alpha=64, dropout=0.05** (~250 MB) — không match default cua bat ky training script nao trong repo hien tai |
| Re-train default (nếu chạy lại) | `cloud/h100_train_medical.py` & notebook: r=16, alpha=32 — `train_qlora_medgemma.py`: r=32, alpha=64 |
| Target modules | q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj |
| Train data | `data/training_clean/medgemma_4b/medical_train.jsonl` (15,693 records) |
| Eval data | `data/training_clean/medgemma_4b/medical_eval.jsonl` (2,770 records) |
| Output | `output/medisign-medgemma4b-adapter/` |
| HF mirror | `thuaannn/medisign-medgemma4b-adapter` |

Medical adapter can hoc:

- Hoi dap y te tieng Viet
- Trieu chung va goi y muc do can chu y
- Thuoc Viet Nam, hoat chat, dang bao che, so dang ky
- Tinh than safety: khong chan doan chac chan, khuyen gap bac si khi can

### Personal/Psychology Adapter

| Thanh phan | Mo ta |
| --- | --- |
| Base model | `google/medgemma-1.5-4b-it` (chia chung mo hinh nen) |
| Adapter | QLoRA Psychology Adapter (production: r=8, alpha=16, dropout=0.1) |
| Target modules | q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj |
| Train data | `data/training_clean/medgemma_4b/psychology_train.jsonl` (1,201 records) |
| Eval data | `data/training_clean/medgemma_4b/psychology_eval.jsonl` (212 records) |
| Output | `output/medisign_medgemma4b_psychology/adapter/` |
| HF mirror | `thuaannn/medisign-medgemma4b-psychology` |

Psychology adapter tap trung vao Soul Garden + Motivational Interviewing
(Open question, Affirmation, Reflective listening, Summary).

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
├── medical_train.jsonl       15,693 records (Medical adapter — train)
├── medical_eval.jsonl         2,770 records (Medical adapter — eval)
├── psychology_train.jsonl     1,201 records (Psychology adapter — train, OARS)
├── psychology_eval.jsonl        212 records (Psychology adapter — eval)
├── train.jsonl              17,393 records (combined v1 — legacy)
├── eval.jsonl                3,070 records (combined v1 — legacy)
├── merged_dataset.json
├── merge_stats.json
├── format_stats.json
├── psychology_merge_stats.json
└── oars_stats.json
```

Nguồn chinh cua medical corpus (hop nhat tu nhieu nguon):

| Source | Records |
| --- | ---: |
| `all_medical` (tong hop tieng Viet) | 12,391 |
| `medquad` (dich tu MedQuAD) | 1,362 |
| `drug_db` (Q&A tu drug database) | 968 |
| `medical_dialogue_2010` | 800 |
| `vn_drugs_commercial` | 576 |
| `vn_symptoms_culture` | 224 |

Psychology corpus duoc regenerate qua DeepSeek/FPT Cloud bang
`scripts/regenerate_psychology_data.py` voi 20 chu de OARS va 30+ persona;
sau dedup giua 2 worker con 1,413 mau hop le, chia 85/15.

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
| Drug lookup database | Done | DAV-backed, 60,472 drug records + 67,493 interactions |
| MedGemma 4B Medical adapter | Ready to train | 15,693 records, notebook H100 san sang |
| MedGemma 4B Psychology adapter | Ready to train | 1,201 OARS records (DeepSeek-regenerated), notebook H100 san sang |
| Dual adapter runtime server | Done | Single endpoint route theo `model` field |
| RAG-MediSign (BM25 + Dense + RRF) | Done | 128,380 KB records, auto-reload |
| Multi-turn diagnostic chat | Done | conversations + summary + feedback endpoints |
| Fixed eval sets | Partial | `data/eval_sets/demo_safety_eval.jsonl` (427 cases) — can them real cases |
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
