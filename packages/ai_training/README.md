# AI Training Documentation

> **Quick Start**: Xem `QUICKSTART.md` để bắt đầu nhanh!

## MediSign AI - 3 Deployment Modes

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MEDISIGN AI DEPLOYMENT MODES                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐│
│  │    CLOUD        │    │     LOCAL        │    │    HYBRID       ││
│  │   (Bảo mật)     │    │  (Security)      │    │  (Kết hợp)     ││
│  ├─────────────────┤    ├─────────────────┤    ├─────────────────┤│
│  │ Qwen 2.5 72B   │    │  Gemma 2B       │    │   Cloud +      ││
│  │ + LoRA Y tế VN │    │  + 2 Adapters    │    │   Local        ││
│  │ Self-hosted    │    │  On-device      │    │                 ││
│  └─────────────────┘    └─────────────────┘    └─────────────────┘│
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Models Cần Train

### 1. Cloud Mode: Qwen 2.5 72B + Medical Adapter

| Thành phần | Mô tả |
|------------|-------|
| Base Model | Qwen 2.5 72B |
| Adapter | **LoRA Medical Adapter** - fine-tuned cho y tế VN |
| VRAM | ~40GB (4-bit quantization) |
| Deploy | Self-hosted server (A100) |

**Tại sao Qwen 72B:**
- Tiếng Việt tốt nhất
- License thương mại (Apache 2.0)
- Dễ fine-tune với LoRA/QLoRA
- Hiệu năng cao

**Adapter Medical cần học:**
- Triệu chứng → chẩn đoán gợi ý
- Thuốc VN, tương tác thuốc
- Phân mức độ nghiêm trọng (Xanh/Vàng/Đỏ)
- Luôn ghi "không thay thế bác sĩ"

**⚠️ IMPORTANT: Gemini là FALLBACK, không phải primary:**

```
┌─────────────────────────────────────────────────────────────┐
│               CLOUD FALLBACK STRATEGY                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Request → Qwen 72B (primary)                               │
│             │                                                │
│             ├─ <80% load → OK                                │
│             │                                                │
│             ├─ 80-95% load → Qwen 7B (light)                │
│             │                                                │
│             └─ >95% load → Gemini Flash API ← BACKUP        │
│                                                              │
│  Khi server Qwen sập HOÀN TOÀN:                            │
│    → Multi-region backup (Singapore → Japan)               │
│    → Cuối cùng: Gemini Flash API                           │
│                                                              │
│  NOTE: Gemini CHỈ dùng khi Qwen không khả dụng             │
│        Không phải để thay thế vĩnh viễn!                   │
└─────────────────────────────────────────────────────────────┘
```

---

### 2. Local Mode: Gemma 2B + 2 Adapters

```
RAM Usage:
├── Gemma 2B (base)      = 1.5GB  ← Tải 1 lần
├── Adapter Medical      = ~50MB  ← Gắn khi cần
└── Adapter Personal     = ~50-100MB ← Swap khi cần
    Total               = ~1.65GB
```

| Adapter | Kích thước | Chức năng | Cần train? |
|---------|------------|-----------|------------|
| **MediSign-Med** | ~50MB | AI Thạc sĩ Y tế | ✅ YES |
| **MediSign-Personal** | ~50-100MB | AI Cá nhân hóa | ✅ YES |

#### Adapter #1: Medical Adapter
- Triệu chứng, chẩn đoán gợi ý
- Thuốc VN, tương tác thuốc
- Quản lý thuốc (cabinet)
- Triaje mức độ khẩn cấp

#### Adapter #2: Personal Adapter
- Cá nhân hóa câu trả lời theo user
- Hiểu Soul Garden (cảm xúc, thói quen)
- Viết lại câu trả lời phù hợp với context
- Encrypted, riêng từng user

---

### 3. Hybrid Mode
- Cloud: Qwen 72B cho complex queries
- Local: Gemma 2B cho quick responses + offline
- Adapter Personal sync encrypted lên cloud (backup)

---

## Data Directories

```
data/
├── training_raw/        # Raw training data (chưa xử lý)
├── training_clean/      # Cleaned training data
└── eval_sets/          # Evaluation datasets
```

### Nguồn Dữ liệu Training

| Nguồn | Nội dung | Số lượng |
|-------|----------|----------|
| MedQuAD (GitHub) | Q&A y khoa (Anh) | 47,000 cặp |
| ChatDoctor (GitHub) | Hội thoại bệnh nhân-bác sĩ | 100,000 cặp |
| Dược thư Quốc gia VN | Thuốc, liều, tương tác | 30,000 thuốc |
| Tự tạo (VN) | Dịch + viết Q&A tiếng Việt | 5,000-10,000 cặp |

---

## Training Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    TRAINING PIPELINE                         │
└─────────────────────────────────────────────────────────────┘

Step 1: Thu thập dữ liệu
        ├── Crawl/public datasets
        ├── Translate to Vietnamese
        └── Clean & validate

Step 2: Prepare training data
        ├── Format: Instruction tuning (system/user/assistant)
        ├── Split: train/eval (90/10)
        └── Tokenize

Step 3: Train Medical Adapter
        ├── Base: Qwen 2.5 72B / Gemma 2B
        ├── Method: LoRA/QLoRA
        ├── Hardware: A100 80GB / RTX 4090
        └── Time: 8-12h (72B) / 2-4h (2B)

Step 4: Evaluate
        ├── Medical accuracy
        ├── Safety (no harmful suggestions)
        └── Vietnamese fluency

Step 5: Deploy
        ├── Cloud: vLLM server
        └── Local: GGML/llama.cpp quantization
```

---

## Current Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Rule-based triage | ✅ Done | Keyword matching, Vietnamese |
| Qwen via DashScope | ✅ Done | Optional enhancement |
| Gemma 2B + Medical Adapter | 🔄 Ready to train | **PRIORITY - Xem QUICKSTART.md** |
| Qwen 72B + Medical Adapter | 🔄 Planned | Cloud mode (cần A100) |
| Personal Adapter | 🔄 Planned | Local mode |
| Fitness Pose Detection | ✅ Done | ML Kit (pre-trained) |

---

## Training Roadmap - Bắt Đầu Ngay

### Phase 1: MVP - Gemma 2B (PRIORITY CAO NHẤT)
```
⏱ Thời gian: 30-60 phút
💰 Chi phí: ~$0 (Google Colab miễn phí)
🎯 Kết quả: AI y tế tiếng Việt, chạy offline

📋 Các bước:
1. python scripts/01_prepare_data.py
2. Upload lên Colab → chạy 02_train_gemma.py
3. Download adapter
4. Test với 03_inference.py
```

### Phase 2: Medicine Database
```
Mở rộng database thuốc VN
Thu thập data từ Cục Dược
Rule-based + lookup cho medicine
```

### Phase 3: Qwen 72B (Optional - khi có budget)
```
Chỉ train khi có server A100
Dùng cho cloud mode với AI mạnh hơn
```

---

## Quick Links

| File | Description |
|------|-------------|
| `QUICKSTART.md` | Hướng dẫn nhanh nhất ✅ BẮT ĐẦU TỪ ĐÂY |
| `scripts/01_prepare_data.py` | Chuẩn bị data |
| `scripts/02_train_gemma.py` | Train Gemma 2B (Colab) |
| `scripts/02_train_qwen.py` | Train Qwen 72B (Server) |
| `scripts/03_inference.py` | Test model |

---

## References

Module này nhận dạng thuốc từ ảnh chụp vỉ/hộp thuốc.

### 2 Approaches Cần Train

```
┌─────────────────────────────────────────────────────────────────────┐
│               MEDICINE RECOGNITION PIPELINE                          │
└─────────────────────────────────────────────────────────────────────┘

📸 Chụp ảnh thuốc
       │
       ▼
┌──────────────────┐     ┌──────────────────┐
│  OCR + NLP      │     │  Image CNN       │
│  (Text-based)   │     │  (Vision-based)  │
├──────────────────┤     ├──────────────────┤
│ • ML Kit/       │     │ • ResNet/Efficient│
│   Tesseract    │     │   Net train      │
│ • Extract text │     │ • Classify pills  │
│ • Match DB     │     │ • Match visual   │
└──────────────────┘     └──────────────────┘
       │                        │
       └────────┬───────────────┘
                ▼
┌─────────────────────────────────────────────┐
│         MEDICINE DATABASE                    │
│   (~30,000 thuốc VN từ Cục Dược)            │
│   - Tên thuốc, hoạt chất                    │
│   - Liều dùng, tác dụng phụ                 │
│   - Tương tác thuốc                         │
│   - Chống chỉ định                          │
└─────────────────────────────────────────────┘
```

### Approach 1: OCR + NLP (Text-based)

| Component | Technology | Status |
|-----------|-----------|--------|
| OCR | ML Kit / Tesseract | ✅ Có thể dùng |
| Text processing | Rule-based (hiện tại) | ✅ MVP done |
| **NLP Enhancement** | **Cần train** | 🔄 Planned |

**Cần train:**
- Fine-tune model để extract tên thuốc tiếng Việt từ OCR output
- Xử lý abbreviations, typos phổ biến trong đơn thuốc VN
- Map tên thương mại ↔ hoạt chất

### Approach 2: Image Classification (Vision-based)

| Component | Technology | Status |
|-----------|-----------|--------|
| Image classification | CNN/ViT | 🔄 Cần train |
| Training data | Chụp ảnh thuốc thật | 📋 Thu thập |

**Cần train:**
- Dataset: 10,000+ ảnh thuốc VN (vỉ, hộp, viên)
- Model: EfficientNet hoặc ViT fine-tuned
- Classes: ~30,000 thuốc (hoặc cluster thành groups)

### Data Sources

| Nguồn | Nội dung | Số lượng |
|-------|----------|----------|
| Cục Dược VN | Database thuốc chính thức | ~30,000 thuốc |
| Bệnh viện | Đơn thuốc mẫu (đã sanitize) | 5,000+ mẫu |
| Tự chụp | Chụp ảnh thuốc thật | 10,000+ ảnh |

### Current Implementation

Xem: `apps/backend_fastapi/app/services/medicine_service.py`

Hiện tại dùng rule-based:
- Keyword matching cho tên thuốc
- Tương tác thuốc đơn giản (Paracetamol + Alcohol, etc.)

### Priority

| Priority | Task | Notes |
|----------|------|-------|
| 1 | Mở rộng Medicine Database | Thêm 30,000 thuốc VN |
| 2 | OCR Enhancement | Xử lý text tiếng Việt tốt hơn |
| 3 | Image Classification | Nhận diện qua hình ảnh |

---

## References

- Quick Start: `QUICKSTART.md`
- Data Prep: `scripts/01_prepare_data.py`
- Gemma Training: `scripts/02_train_gemma.py`
- Qwen Training: `scripts/02_train_qwen.py`
- Inference: `scripts/03_inference.py`
- Full Docs: `docs/Required.md` (Module 2: Camera Quét Thuốc)
- Code: `apps/backend_fastapi/app/services/medicine_service.py`
