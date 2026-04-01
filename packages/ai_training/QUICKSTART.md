# AI Training - Hướng Dẫn Nhanh

## 🎯 Mục tiêu: Đạt 85%+ Accuracy

---

## 📋 Tổng Quan

| Phase | Method | Accuracy | Timeline |
|-------|--------|----------|----------|
| Baseline | Qwen 72B (no fine-tune) | 55-65% | - |
| Phase 1 | Fine-tune + LoRA | 70-80% | 2 tuần |
| Phase 2 | + RAG | 80-85% | 1 tuần |
| Phase 3 | + Logic Layer | **85%+** | 1 tuần |

---

## 🚀 Bắt Đầu Nhanh

### Bước 1: Chuẩn bị Data (Chạy local)

```bash
cd packages/ai_training

# Download MedQuAD từ HuggingFace + Vietnamese data
python scripts/01_prepare_data.py --source all --lang en --model qwen_72b

# Hoặc chỉ Vietnamese data (nhanh hơn)
python scripts/01_prepare_data.py --source sample --model qwen_72b
```

**Kết quả:**
- `data/training_clean/qwen_72b/train.json`
- `data/training_clean/qwen_72b/eval.json`

### Bước 2: Train Qwen 72B (Cần Server A100)

```bash
# Chạy training script
python scripts/02_train_qwen.py
```

**Yêu cầu:**
- GPU: A100 80GB
- Time: 8-12 giờ
- Có thể thuê trên Vast.ai (~$1/giờ)

### Bước 3: Evaluate

```bash
python scripts/05_evaluate.py --model ./output/medisign_qwen/adapter
```

---

## 📁 Cấu Trúc Files

```
packages/ai_training/
├── scripts/
│   ├── 01_prepare_data.py    # Chuẩn bị data
│   ├── 02_train_gemma.py     # Train Gemma 2B (mobile)
│   ├── 02_train_qwen.py      # Train Qwen 72B (server)
│   ├── 03_inference.py       # Test inference
│   └── 05_evaluate.py       # Đánh giá accuracy
├── output/
│   └── eval_results/         # Kết quả đánh giá
└── medical_adapter/
    └── README.md

data/
├── training_raw/
│   ├── medquad/              # MedQuAD (sẽ tự download)
│   ├── vietnamese_medical/   # Vietnamese Q&A
│   └── symptom_disease/     # Symptom-Disease mapping
└── training_clean/
    ├── qwen_72b/
    │   ├── train.json
    │   └── eval.json
    └── gemma_2b/
        ├── train.json
        └── eval.json
```

---

## 🔧 Chi Tiết Từng Bước

### Bước 1: Chuẩn bị Data

```bash
# Tải tất cả data (MedQuAD + ChatDoctor + Vietnamese)
python scripts/01_prepare_data.py --source all --lang en --model qwen_72b

# Args:
# --source: medquad | chatdoctor | all | sample
# --lang: en | vi
# --model: qwen_72b | gemma_2b
# --eval_ratio: 0.1 (10% cho eval)
```

### Bước 2: Train

**Option A: Train Qwen 72B (Server A100)**

```bash
python scripts/02_train_qwen.py
```

**Option B: Train Gemma 2B (Google Colab)**

1. Upload `02_train_gemma.py` lên Colab
2. Upload data từ Bước 1
3. Chạy cells
4. Download adapter

### Bước 3: Evaluate

```bash
# Đánh giá accuracy trên MedQuAD
python scripts/05_evaluate.py \
    --base_model Qwen/Qwen2.5-72B-Instruct \
    --model ./output/medisign_qwen/adapter \
    --max_samples 1000
```

---

## 📊 Evaluation Metrics

| Metric | Mô tả | Target |
|--------|-------|--------|
| **Exact Match** | % câu trả lời khớp chính xác | ≥80% |
| **Token Accuracy** | % từ khớp | ≥85% |
| **ROUGE-L** | Similarity score | ≥0.75 |
| **BLEU** | Text quality | ≥0.5 |

---

## 🎓 Tips Để Đạt Điểm Cao

1. **Nhiều data hơn** - Ưu tiên MedQuAD đầy đủ (47K samples)
2. **Dịch sang tiếng Việt** - Dùng Gemini API để dịch
3. **RAG** - Thêm knowledge base để grounding
4. **Logic Layer** - Thêm symptom-disease mapping

---

## ❓ FAQ

**Q: Không có A100 làm sao?**
A: Dùng Qwen 7B thay 72B, hoặc thuê Vast.ai (~$1/giờ)

**Q: Data ít có sao không?**
A: 1000+ samples đã đủ cho baseline, càng nhiều càng tốt

**Q: Train bao lâu?**
A: Qwen 72B: 8-12 giờ, Qwen 7B: 2-4 giờ

**Q: Làm sao biết model tốt?**
A: Chạy `05_evaluate.py` để đo accuracy

---

## 📞 Support

- Xem chi tiết: `packages/ai_training/README.md`
- Code: `packages/ai_training/scripts/`
- Documentation: `docs/Required.md` (Phần 17)

---

## ⚠️ Lưu Ý Quan Trọng

1. **AI chỉ HỖ TRỢ** - Không thay thế bác sĩ
2. **Luôn có disclaimer** - Trong mọi response
3. **Red flags** - Khuyến khích khám bác sĩ ngay
4. **Đây là QA accuracy** - Không phải clinical diagnosis
