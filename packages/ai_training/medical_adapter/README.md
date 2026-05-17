# Medical Adapter Training

Medical adapter hien tai duoc dinh huong cho `google/medgemma-4b-it` bang QLoRA.

## Muc tieu

| Phase | Method | Expected outcome |
| --- | --- | --- |
| Baseline | MedGemma 4B without MediSign adapter | General medical assistant |
| Phase 1 | QLoRA medical adapter | Better Vietnamese MediSign style and drug/triage responses |
| Phase 2 | + RAG | More grounded answers |
| Phase 3 | + Logic/safety layer | Better red-flag handling |

## Hybrid Engine Architecture

```text
User Input
    |
    v
+----------------------+
| MedGemma 4B Runtime  |
| + Medical LoRA       |
+----------+-----------+
           |
           v
+----------------------+
| RAG Layer            |
| Medical Knowledge DB |
+----------+-----------+
           |
           v
+----------------------+
| Symptom/Drug Logic   |
| Red Flag Rules       |
+----------+-----------+
           |
           v
Response with disclaimer
```

## Data Sources

| Dataset | Purpose |
| --- | --- |
| MedQuAD-derived QA | Medical Q&A |
| Medical dialogue data | Patient-doctor style answers |
| Vietnamese drug data | Drug lookup and medicine education |
| DAV drug registry data | Vietnamese registered drug database |
| Synthetic Vietnamese data | Local phrasing and app-specific intents |

## Scripts

| Script | Mo ta |
| --- | --- |
| `scripts/prepare_medgemma_data.py` | Merge and deduplicate training data |
| `scripts/format_medgemma_dataset.py` | Apply MedGemma chat template and split train/eval |
| `scripts/train_qlora_medgemma.py` | Train QLoRA adapter |
| `scripts/train_qlora_medgemma_smoke_test.py` | Validate train config without full training |

## Training Commands

```bash
python scripts/prepare_medgemma_data.py
python scripts/format_medgemma_dataset.py
python scripts/train_qlora_medgemma_smoke_test.py
python scripts/train_qlora_medgemma.py
```

## Evaluation Metrics

- Vietnamese answer quality
- Medical factuality
- Safety disclaimer presence
- Red-flag escalation behavior
- Drug lookup correctness
- ROUGE/BLEU only as supporting text-similarity metrics

## Disclaimer

- AI chi ho tro, khong thay the bac si.
- Luon co disclaimer trong response y te.
- Red flags can khuyen kham/cap cuu ngay.
