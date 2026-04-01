# Architecture (Bootstrap)

## 3 Deployment Modes

| Mode | Model | Adapters | Use Case |
|------|-------|----------|----------|
| **Cloud** | Qwen 2.5 72B | Medical LoRA | AI mạnh nhất, ẩn danh |
| **Local** | Gemma 2B | Medical + Personal | 100% offline, bảo mật |
| **Hybrid** | Qwen + Gemma | Cả hai | Kết hợp |

## Cloud Mode - Load Balancing & Fallback

```
                        User Request
                            │
                    ┌───────▼───────┐
                    │  Load Balancer │
                    └───────┬───────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Qwen 72B #1  │   │ Qwen 72B #2  │   │ Qwen 7B      │
│ (Chính)      │   │ (Backup)     │   │ (Light)      │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────▼───────┐
                    │  Overload?     │
                    │  (>95% load)  │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │ Gemini Flash  │ ← FALLBACK CUỐI CÙNG
                    │ (trả phí)     │   Khi Qwen quá tải/sập
                    └───────────────┘
```

**Load Balancing Strategy:**
| Mức tải | Hành động |
|---------|-----------|
| < 80% | Qwen 72B xử lý bình thường |
| 80-95% | Chuyển sang Qwen 7B (nhanh 10x) |
| 95-100% | Gemini Flash API (backup) |
| 100% | Request Queue + Ưu tiên emergency |

## Components

- Mobile Flutter: UI + local state + local DB.
- Backend FastAPI: API gateway + service triage/medicine.
- AI service:
  - Cloud: Qwen 72B + Medical Adapter (cần train)
  - Local: Gemma 2B + 2 Adapters (cần train)
- Fallback: decision tree + rule-based khi AI không khả dụng

## AI Training

Xem chi tiết: `packages/ai_training/README.md`

### Models Cần Train

```
AI Models:
├── Qwen 2.5 72B + Medical Adapter (Cloud)
├── Gemma 2B + Medical Adapter (Local)
└── Gemma 2B + Personal Adapter (Local)

Medicine Recognition:
├── OCR + NLP Enhancement (text-based)
└── Image Classification (vision-based)
```

### Medicine Recognition Pipeline

```
📸 Chụp ảnh thuốc
       │
       ▼
┌──────────────────┐     ┌──────────────────┐
│  OCR + NLP      │     │  Image CNN       │
│  (Text-based)   │     │  (Vision-based)  │
└──────────────────┘     └──────────────────┘
       │                        │
       └────────┬───────────────┘
                ▼
┌─────────────────────────────────────────────┐
│         MEDICINE DATABASE                    │
│   (~30,000 thuốc VN từ Cục Dược)            │
└─────────────────────────────────────────────┘
```
