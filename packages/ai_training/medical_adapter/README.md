# Medical Adapter Training

## Mục tiêu: Đạt 85%+ Accuracy

### Accuracy Targets

| Phase | Method | Expected Accuracy |
|-------|--------|-------------------|
| Baseline | Qwen 72B (no fine-tune) | 55-65% |
| Phase 1 | Fine-tune + LoRA | 70-80% |
| Phase 2 | + RAG | 80-85% |
| Phase 3 | + Logic Layer | **85%+** |

### Hybrid Engine Architecture

```
User Input
    │
    ▼
┌─────────────────┐
│  LLM (Qwen 72B)│ ← MedQuAD + ChatDoctor
│  + Medical LoRA │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RAG Layer      │ ← Medical Knowledge Base
│ (FAISS Vector) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Symptom-Disease │ ← Disease-Symptom DB
│ Logic Layer    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Safety Layer   │ ← Red Flag Detection
└────────┬────────┘
         │
         ▼
    Response
```

## Data Sources

| Dataset | Quantity | Purpose |
|---------|----------|---------|
| MedQuAD | 47,000 Q&A | Medical Q&A benchmark |
| ChatDoctor | 100,000 dialogues | Patient-doctor conversations |
| Disease-Symptom | 500+ diseases | Logic layer |
| Dược thư VN | 30,000 drugs | Drug database |

## Scripts

| Script | Mô tả |
|--------|-------|
| `01_prepare_data.py` | Chuẩn bị data training |
| `02_train_gemma.py` | Train Gemma 2B (mobile) |
| `02_train_qwen.py` | Train Qwen 72B (server) |
| `03_inference.py` | Test inference |
| `04_deploy_server.py` | Deploy lên server |
| `05_evaluate.py` | Evaluation benchmark |

## Benchmark Comparison

| Model | Accuracy | Notes |
|-------|----------|-------|
| Med-PaLM 2 (Google) | 86% | Research |
| MedAlpaca-13B | 72% | Open source |
| GPT-3.5 | 60% | General |
| **MediSign (Target)** | **85%+** | Hybrid Engine |

## Training Commands

```bash
# Step 1: Prepare data
python scripts/01_prepare_data.py --source medquad --lang en --model qwen_72b

# Step 2: Train Qwen 72B
python scripts/02_train_qwen.py

# Step 3: Evaluate
python scripts/05_evaluate.py --model ./output/medisign_qwen/adapter
```

## Evaluation Metrics

- **Accuracy**: (Correct / Total) × 100
- **Precision**: TP / (TP + FP)
- **Recall**: TP / (TP + FN)
- **F1-Score**: 2×(P×R)/(P+R)
- **ROUGE-L**: Text similarity

## Disclaimer

- AI chỉ HỖ TRỢ, không thay thế bác sĩ
- Luôn có disclaimer trong mọi response
- Red flags → khuyến khích khám bác sĩ
