# MediSign AI

<p align="right"><a href="README.md">English</a> · <strong>Tiếng Việt</strong></p>

<p align="center">
  <strong>Nền tảng trợ lý sức khỏe đa phương thức cho người Việt</strong><br />
  Triage triệu chứng, tra cứu thuốc, RAG y tế, sức khỏe tinh thần, fitness và nhận diện ngôn ngữ ký hiệu Việt.
</p>

<p align="center">
  <img alt="FastAPI" src="https://img.shields.io/badge/backend-FastAPI-009688?logo=fastapi&logoColor=white" />
  <img alt="Next.js" src="https://img.shields.io/badge/web-Next.js-000000?logo=next.js&logoColor=white" />
  <img alt="Flutter" src="https://img.shields.io/badge/mobile-Flutter-02569B?logo=flutter&logoColor=white" />
  <img alt="AI" src="https://img.shields.io/badge/AI-MedGemma%20%2B%20RAG-6C63FF" />
  <img alt="Status" src="https://img.shields.io/badge/status-research%20prototype-F59E0B" />
</p>

Ứng dụng y tế thông minh cho người Việt — tư vấn triệu chứng, tra cứu thuốc, chăm sóc sức khỏe tâm thần và theo dõi thể lực trên web và mobile.

> **Lưu ý y tế:** AI chỉ đưa ra gợi ý sơ bộ, không thay thế chẩn đoán hoặc chỉ định của bác sĩ. Khi có dấu hiệu nặng, hãy gọi cấp cứu **115** hoặc đến cơ sở y tế ngay.

---

## Mục lục

- [Tổng quan](#tổng-quan)
- [Kết quả benchmark](#kết-quả-benchmark)
- [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
- [Model AI — MedGemma 1.5 4B](#model-ai--medgemma-15-4b)
- [RAG — Kho kiến thức y tế](#rag--kho-kiến-thức-y-tế)
- [Sign Mode — Nhận diện ngôn ngữ ký hiệu (VSL)](#sign-mode--nhận-diện-ngôn-ngữ-ký-hiệu-vsl)
- [Cơ sở dữ liệu thuốc](#cơ-sở-dữ-liệu-thuốc)
- [Tech Stack](#tech-stack)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Cài đặt & Chạy](#cài-đặt--chạy)
- [Biến môi trường](#biến-môi-trường)
- [API Endpoints](#api-endpoints)
- [Train MedGemma Adapter](#train-medgemma-adapter)
- [Trạng thái hiện tại](#trạng-thái-hiện-tại)
- [Đội ngũ](#đội-ngũ)
- [Disclaimer](#disclaimer)

---

## Tổng quan

MediSign AI là nền tảng y tế đa nền tảng (web + mobile) phục vụ người Việt, đặc biệt người cao tuổi, người khuyết tật và gia đình ở vùng sâu vùng xa.

Tính năng chính:

- **Tư vấn triệu chứng** — phân loại 3 mức khẩn cấp (Xanh / Vàng / Đỏ) bằng rule-based + AI
- **Tra cứu thuốc** — 60.472 records thuốc từ Cục Dược Việt Nam (DAV), có hoạt chất, số đăng ký, cảnh báo tương tác
- **AI Chat y tế** — trợ lý tiếng Việt dựa trên `google/medgemma-1.5-4b-it` + RAG 128.380 records
- **SoulGarden** — hỗ trợ sức khỏe tâm thần, nhật ký cảm xúc
- **Fitness** — theo dõi tập luyện, phát hiện tư thế bằng ML on-device
- **Cộng đồng** — chia sẻ kinh nghiệm sức khỏe ẩn danh, có kiểm duyệt
- **Hỗ trợ NKT** — **Sign Mode** nhận diện ngôn ngữ ký hiệu Việt (VSL) realtime on-device + fallback Gemini Vision, voice tiếng Việt, Elderly Mode

---

## Kết quả benchmark

Repository đi kèm benchmark định lượng chạy trực tiếp trên các service thật của backend. Kết quả dưới đây được ghi nhận trong artifact local `benchmark_full.log`; kịch bản có thể tái lập bằng [`scripts/benchmark_real.py`](scripts/benchmark_real.py). File log không được track trong public repository.

| Hạng mục | Quy mô | Kết quả nổi bật |
|----------|--------|-----------------|
| **Rule-based triage** | 100 ca có nhãn | Accuracy **89,0%**; emergency recall **100%**; latency trung bình **0,051 ms** |
| **RAG retrieval** | 30 truy vấn y tế | Hit@1 **93,3% → 96,7%**; Hit@5 **93,3% → 100%**; MRR **93,3% → 97,3%** khi bật synonym expansion |
| **Drug lookup** | 64.045 records, 20 truy vấn | Positive recall **100%**; 19/20 truy vấn tìm thấy; mean **671,66 ms**, p95 **3.652,51 ms** |
| **Triage throughput** | 1.000 lượt gọi local | Mean **0,061 ms**; p99 **0,099 ms**; khoảng **16.453 req/s** trên benchmark machine |
| **Adapter routing** | 9 prompt kiểm tra | Adapter làm thay đổi top-1 retrieval ở **5/9** prompt |

Chạy lại benchmark từ thư mục gốc:

```bash
python scripts/benchmark_real.py --output apps/backend_fastapi/output/benchmark_real_report.json
```

> **Phạm vi kết quả:** đây là engineering benchmark trên tập đánh giá nhỏ, curated và môi trường local; không phải thử nghiệm lâm sàng, không chứng minh hiệu quả chẩn đoán và không nên được diễn giải như chứng nhận thiết bị y tế. Chỉ số latency/throughput phụ thuộc phần cứng và trạng thái cache.

---

## Kiến trúc hệ thống

```
Flutter App / Next.js Web  ── Sign Mode (VSL): realtime TFJS on-device
         │                     + Gemini Vision fallback (/api/sign/recognize)
         ▼
   FastAPI Backend  ──────────────────────────────────────────┐
         │                                                     │
         ├── Rule-based Triage (luôn hoạt động)               │
         ├── Drug Lookup Service (60k+ records DAV)           │
         ├── RAG Service (BM25 local, 128k records)           │
         │                                                     │
         └── AI Model Client (httpx async)                    │
                  │                                            │
                  ▼                                            │
     MedGemma Runtime Server (GPU riêng)                      │
     /v1/chat/completions (OpenAI-compatible)                  │
     ├── Base: google/medgemma-1.5-4b-it                      │
     ├── Adapter: medisign-medgemma-medical (QLoRA)           │
     └── Adapter: medisign-medgemma-psychology (QLoRA)        │
                                                               │
   PostgreSQL 16 ◄─────────────────────────────────────────────┘
```

FastAPI **không load model trực tiếp**. Model chạy trong GPU process riêng, expose OpenAI-compatible endpoint. Backend là thin client gọi qua `httpx`.

### 3 Deployment Modes

| Mode | Model chính | Use case |
|------|-------------|----------|
| **Cloud** | MedGemma 1.5 4B + Medical/Psychology adapter (AI server cloud — H100/A100) | AI mạnh nhất, ổn định, qua API OpenAI-compatible |
| **Local** | Gemma 2B + 2 LoRA Adapters (~1.65 GB RAM) | 100% offline, data không rời máy |
| **Hybrid** | Cloud cho complex queries + Local fallback | Cân bằng hiệu năng và bảo mật |

**MVP hiện tại:** `BACKEND_AI_PROVIDER=rule_based` — không cần GPU, backend trả fallback response an toàn.

---

## Model AI — MedGemma 1.5 4B

### Base Model

| Thành phần | Giá trị |
|------------|---------|
| Base model | `google/medgemma-1.5-4b-it` |
| Phương pháp fine-tune | **QLoRA** (4-bit NF4 quantization, không train lại full model) |
| LoRA — Medical adapter (đang trên disk + HF) | r=64, alpha=64, dropout=0.05 (~250 MB) — train trước đó, KHÔNG khớp default của bất kỳ script nào trong repo hiện tại |
| LoRA — Psychology adapter (đang trên disk + HF) | r=8, alpha=16, dropout=0.1 (~62 MB) — match `scripts/cloud/rtx4090_train_psychology.py` defaults |
| LoRA — Script defaults (nếu re-train) | `scripts/train_qlora_medgemma.py`: r=32 / α=64 — `scripts/cloud/h100_train_medical.py`: r=16 / α=32 — `train_medical_adapter.ipynb`: r=16 / α=32 — `train_psychology_adapter.ipynb`: r=16 / α=32 (5 epochs) |
| Target modules | `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` (attention + MLP) |
| GPU yêu cầu | RTX 4090 (24 GB) hoặc 2× T4 (Kaggle free) — production khuyến nghị H100 80GB cho Flash-Attention 2 |

> MedGemma là model y tế của Google, gated trên Hugging Face. Cần chấp nhận điều khoản tại [huggingface.co/google/medgemma-1.5-4b-it](https://huggingface.co/google/medgemma-1.5-4b-it) trước khi train.

### Hai Adapter (Dual Adapter Architecture)

| Adapter | Tên runtime | Mục đích | HuggingFace |
|---------|-------------|----------|-------------|
| Medical | `medisign-medgemma-medical` | RAG diagnostic chat, tra cứu thuốc, triệu chứng | [thuaannn/medisign-medgemma4b-adapter](https://huggingface.co/thuaannn/medisign-medgemma4b-adapter) |
| Psychology | `medisign-medgemma-psychology` | SoulGarden — OARS, hỗ trợ tâm lý | [thuaannn/medisign-medgemma4b-psychology](https://huggingface.co/thuaannn/medisign-medgemma4b-psychology) |

**1 server, 2 adapter, switch theo request:**

```
POST /v1/chat/completions
body: { "model": "medisign-medgemma-medical" | "medisign-medgemma-psychology", ... }
                              │
                              ▼
                    Server tự route adapter
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
   Medical Adapter                Psychology Adapter
   (preload khi start)            (lazy load)
```

Server reference implementation: [`scripts/serve_medgemma.py`](scripts/serve_medgemma.py)
và [`scripts/dev/medgemma_openai_server.py`](scripts/dev/medgemma_openai_server.py).

Adapter output paths (trên VM sau khi pull):
```
output/medisign-medgemma4b-adapter/                       ← Medical (preload)
output/medisign_medgemma4b_psychology/adapter/            ← Psychology (lazy)
```

### Training Data — Dual Dataset

Dataset đã tách thành 2 file riêng cho 2 adapter, đẩy lên HuggingFace:

[thuaannn/medisign-training-data](https://huggingface.co/datasets/thuaannn/medisign-training-data)

| File | Records | Train cho |
|------|--------:|-----------|
| `data/training_clean/medgemma_4b/medical_train.jsonl` | 15.693 | Medical Adapter |
| `data/training_clean/medgemma_4b/medical_eval.jsonl` | 2.770 | Medical Adapter (eval) |
| `data/training_clean/medgemma_4b/psychology_train.jsonl` | 1.201 | Psychology Adapter |
| `data/training_clean/medgemma_4b/psychology_eval.jsonl` | 212 | Psychology Adapter (eval) |

```
data/training_clean/medgemma_4b/
├── medical_train.jsonl       15.693 records (Medical)
├── medical_eval.jsonl         2.770 records (Medical eval)
├── psychology_train.jsonl     1.201 records (Psychology OARS, DeepSeek-regenerated)
├── psychology_eval.jsonl        212 records (Psychology eval)
├── train.jsonl              17.393 records (combined, legacy v1)
└── eval.jsonl                3.070 records (combined, legacy v1)
```

Bộ Psychology được regenerate qua `scripts/regenerate_psychology_data.py` (DeepSeek/FPT
Cloud API) với 20 chủ đề OARS và 30+ persona. Sau dedup giữa các worker còn 1.413 mẫu
hợp lệ, chia 85/15 → train 1.201 / eval 212.

Format JSONL (Gemma chat template):
```json
{
  "text": "<start_of_turn>user\n...<end_of_turn>\n<start_of_turn>model\n...<end_of_turn>",
  "messages": [...],
  "source": "all_medical | drug_db | generated_vi_oars_template | ..."
}
```

### Cách backend chọn adapter

```python
# ai_model_service.py
def _model_for_adapter(self, adapter: str) -> str:
    if adapter == "psychology":
        return settings.ai_psychology_model   # medisign-medgemma-psychology
    if adapter == "medical":
        return settings.ai_medical_model      # medisign-medgemma-medical
    return settings.ai_model                  # google/medgemma-1.5-4b-it (default)
```

### Triage AI (MedGemma — tùy chọn)

`AITriageService` gọi MedGemma medical adapter qua AI server (OpenAI-compatible) cho phân tích triệu chứng phức tạp:

```
REQUEST → Rule-based (fast path, luôn chạy trước)
              │
              ▼ Nếu KHÔNG phải emergency → MedGemma medical adapter (qua AI server cloud)
              │
              ▼ Nếu AI server lỗi / không cấu hình → Rule-based fallback
```

Emergency keywords (rule-based, không qua AI): `khó thở`, `đau ngực`, `ngất`, `chết nguồn`.

---

## RAG — Kho kiến thức y tế

Backend tích hợp **BM25-style sparse retrieval** tự xây dựng — không cần vector DB hay embedding model.

### Knowledge Base (build_report.json)

| Loại | Records |
|------|--------:|
| Thuốc (drugs) | 60.472 |
| Tương tác thuốc (drug_interactions) | 67.493 |
| Nhu cầu dinh dưỡng theo tuổi | 38 |
| Triệu chứng tiếng Việt | 11 |
| Bệnh thường gặp tại Việt Nam | 10 |
| Hướng dẫn y tế công khai | 356 |
| **Tổng cộng** | **128.380** |

### Đặc điểm kỹ thuật

- Vietnamese text normalization (NFD, bỏ dấu, `đ→d`)
- Medical synonym expansion: `panadol → paracetamol`, `sốt → nhiệt`, `khó thở → hô hấp`, v.v. (14 nhóm)
- BM25 scoring (k1=1.5, b=0.75) + title/alias boost (+3.0)
- Type boosting: `drug`, `drug_interaction`, `nutrition_requirement` × 1.12 (medical adapter)
- Auto-reload khi file knowledge base thay đổi (không cần restart)

### Cấu hình mặc định

| Tham số | Giá trị |
|---------|---------|
| `RAG_DEFAULT_TOP_K` | 5 |
| `RAG_MIN_SCORE` | 0.15 |
| `RAG_MAX_CONTEXT_CHARS` | 6.000 |
| Knowledge base | `data/knowledge_base/knowledge_base.json` |

Rebuild index sau khi cập nhật knowledge base:
```bash
python scripts/build_demo_knowledge_base.py
# Hoặc gọi API:
POST /api/v1/ai/rag/rebuild
```

---

## Sign Mode — Nhận diện ngôn ngữ ký hiệu (VSL)

MediSign hỗ trợ người khiếm thính/khiếm ngôn nhập triệu chứng bằng **ngôn ngữ ký hiệu Việt Nam (VSL)** ngay trong khung chat. Tính năng nằm hoàn toàn ở web frontend (`apps/web_next`), có 2 đường nhận diện bổ trợ nhau:

### 1. Realtime on-device (mặc định)

`VslRecognitionService` (`apps/web_next/lib/vsl/VslRecognitionService.ts`) chạy 100% trên trình duyệt, không gọi API:

- **MediaPipe Tasks-Vision** (Hand + Face + Pose landmarker) trích keypoint mỗi frame.
- Ghép thành feature vector **495-D** (45 pose + 126 hand + 324 face) — định nghĩa tại `apps/web_next/lib/vsl/landmarkSpec.ts`.
- Head-pose de-rotation (Procrustes matrix) + body-relative normalization để bất biến với góc nghiêng đầu và khoảng cách camera.
- Sliding window 30 frame → model **Bi-LSTM** (TensorFlow.js) inference liên tục, voting + confidence/margin gate trước khi emit.
- Component UI: `apps/web_next/components/chat/VslRealtimeComposer.tsx` — mở camera, hiển thị ký hiệu nhận diện realtime, ghép thành câu rồi gửi vào chat.

Model assets: `public/models/vsl/` (`classes.json`, `weights.json`, `weights.bin`).
Từ vựng nạp từ `classes.json` (single source of truth) — mục tiêu giai đoạn 1 là **150 từ y tế**, mở rộng 300-500 từ ở giai đoạn sau. Code fallback 10 lớp khi chưa có manifest.

### 2. Fallback Gemini Vision (quay video)

Khi cần độ chính xác cao hơn hoặc thiết bị yếu, người dùng quay 1 đoạn video ngắn (< 15s, < 18MB) → gửi tới route handler `app/api/sign/recognize/route.ts`:

- Server-side gọi **Google Gemini 2.5 Flash** (video understanding), trả JSON `{ text, confidence, notes }`.
- `GOOGLE_GEMINI_API_KEY` chỉ đọc ở server (Next.js Route Handler), **không** expose ra browser — không đặt prefix `NEXT_PUBLIC_`.
- Free tier (Dec 2025): 10 RPM / 250 RPD / 250K TPM — đủ cho demo + dev.

Helper liên quan: `lib/sign/` (`apps/web_next/lib/sign/recognize.ts`, `apps/web_next/lib/sign/tokenize.ts`, `apps/web_next/lib/sign/useVideoRecorder.ts`, `apps/web_next/lib/sign/vslDictionary.ts`).

> Lấy API key free tại [aistudio.google.com](https://aistudio.google.com/) → "Get API key" (không cần thẻ). Đặt vào `apps/web_next/.env.local`.

---

## Cơ sở dữ liệu thuốc

Backend ưu tiên file lớn nhất có sẵn, fallback về file nhỏ hơn:

| File | Records | Ghi chú |
|------|--------:|---------|
| `data/training_clean/drug_database_dav_detailed_10k.json` | 64.045 | **Ưu tiên 1** — DAV chi tiết, nguồn `dichvucong.dav.gov.vn` |
| `data/training_clean/drug_database_10k_full.json` | 12.570 | Ưu tiên 2 |
| `data/training_clean/drug_database_10k.json` | 8.149 | Ưu tiên 3 |
| `data/training_clean/drug_database_expanded.json` | 801 | Ưu tiên 4 |
| `data/training_clean/drug_database.json` | 242 | Fallback cuối (legacy) |

File chính (`data/training_clean/drug_database_dav_detailed_10k.json`) — crawl đầy đủ 53.814/53.814 records từ DAV:
- Tên thuốc, hoạt chất, dạng bào chế, hàm lượng
- Số đăng ký, nhà sản xuất
- Chống chỉ định, tác dụng phụ, tương tác, cảnh báo
- Hướng dẫn sử dụng, bảo quản

Override path: `BACKEND_DRUG_DB_PATH` env var.

---

## Tech Stack

### Backend (`apps/backend_fastapi`) — v0.2.0

| Thành phần | Công nghệ |
|------------|-----------|
| Framework | FastAPI ≥0.115 |
| Server | Uvicorn (standard) |
| Python | 3.11+ |
| ORM | SQLAlchemy 2.0 |
| DB Driver | psycopg3 (binary) |
| Auth | PyJWT (HS256), PBKDF2-SHA256 (120k iterations) |
| HTTP Client | httpx ≥0.27 (async) |
| Validation | Pydantic Settings v2 |
| Linting | Ruff + Black |

### Web Frontend (`apps/web_next`) — v0.1.0

| Thành phần | Công nghệ |
|------------|-----------|
| Framework | Next.js 14.2.33 (App Router) |
| Language | TypeScript 5.6.3 |
| UI | React 18.3.1 + Tailwind CSS 3.4.14 |
| Forms | react-hook-form 7 + Zod 4 |
| Data Fetching | TanStack Query v5 |
| VSL / On-device ML | TensorFlow.js 4.22 + MediaPipe Tasks-Vision 0.10 |
| Sign recognition (cloud) | Google Gemini 2.5 Flash (video understanding) |
| Testing | Vitest 3 + Testing Library + MSW 2 + Playwright |

### Mobile (`apps/mobile_flutter`) — v0.1.0+1

| Thành phần | Công nghệ |
|------------|-----------|
| Framework | Flutter (Dart SDK ≥3.4) |
| State | flutter_riverpod 2.5 |
| Navigation | go_router 14 |
| HTTP | dio 5.7 |
| On-device ML | google_mlkit_pose_detection 0.12 |
| Voice | speech_to_text 6.6 + flutter_tts 4 |
| Camera | camera 0.11 |
| Code gen | freezed + json_serializable |

---

## Cấu trúc dự án

```
MediSign_AI/
├── apps/
│   ├── backend_fastapi/          # FastAPI backend (v0.2.0)
│   │   ├── app/
│   │   │   ├── api/routes/       # auth, consult, medicine, ai, admin, health
│   │   │   ├── core/             # config, security (JWT, PBKDF2)
│   │   │   ├── database/         # SQLAlchemy models (cloud + local)
│   │   │   ├── routers/          # drug_router (/api/drug)
│   │   │   ├── schemas/          # Pydantic schemas
│   │   │   └── services/         # ai_model, rag, drug_lookup, triage, auth, medicine
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── web_next/                 # Next.js 14 web app
│   │   ├── app/
│   │   │   ├── page.tsx          # Landing page (/)
│   │   │   ├── about/            # Về chúng tôi (/about)
│   │   │   ├── pricing/          # Bảng giá (/pricing)
│   │   │   ├── download/         # Tải ứng dụng (/download)
│   │   │   ├── chat/             # Chat AI (/chat)
│   │   │   ├── login/            # Đăng nhập (/login)
│   │   │   ├── profile/          # Hồ sơ người dùng (/profile)
│   │   │   ├── reset-password/   # Đặt lại mật khẩu
│   │   │   └── api/
│   │   │       ├── auth/         # login / refresh / logout (Edge proxy)
│   │   │       └── sign/recognize/  # Gemini Vision VSL recognizer (fallback)
│   │   ├── components/
│   │   │   └── chat/             # ChatMain, VslRealtimeComposer, SignAvatar...
│   │   ├── lib/auth/             # AuthProvider, tokenStore, fetcher
│   │   ├── lib/vsl/              # Realtime VSL: VslRecognitionService + landmarkSpec
│   │   ├── lib/sign/             # Video-record VSL helpers + dictionary + tokenizer
│   │   ├── lib/voice/            # Speech recognition (vi-VN)
│   │   ├── public/models/vsl/    # Bi-LSTM TFJS model (classes/weights)
│   │   └── middleware.ts         # Legacy /app/* → / cleanup redirect
│   │
│   └── mobile_flutter/           # Flutter cross-platform app
│       └── lib/features/
│           ├── auth/             # Login, register, welcome
│           ├── onboarding/       # 7-step health survey
│           ├── home/             # 4-tab navigation shell
│           ├── consult/          # AI symptom consultation
│           ├── medicine_cabinet/ # Personal medicine tracker
│           ├── medicine_scan/    # Camera-based drug recognition
│           ├── soul_garden/      # Mental health, mood journal
│           ├── fitness/          # Workout + pose detection
│           ├── community/        # Anonymous health community
│           ├── achievements/     # Gamification
│           ├── doctor_hub/       # Doctor-facing features
│           ├── admin/            # Admin panel
│           ├── profile/          # User profile
│           └── settings/         # App settings
│
├── packages/
│   ├── ai_training/              # Training docs + README
│   ├── shared_contracts/         # OpenAPI + JSON Schema (TypeScript)
│   ├── decision_trees/           # Rule-based decision logic
│   └── prompt_library/           # Prompt templates
│
├── data/
│   ├── training_clean/
│   │   ├── medgemma_4b/          # medical_train.jsonl (15.693), medical_eval.jsonl (2.770),
│   │   │                         # psychology_train.jsonl (1.201), psychology_eval.jsonl (212),
│   │   │                         # train.jsonl (17.393, legacy), eval.jsonl (3.070, legacy)
│   │   └── drug_database_*.json  # DAV drug databases
│   └── knowledge_base/
│       └── knowledge_base.json   # RAG knowledge base (128.380 records)
│
├── scripts/                      # Data prep, training, crawling, QA
│   ├── train_qlora_medgemma.py
│   ├── train_qlora_medgemma_smoke_test.py
│   ├── format_medgemma_dataset.py
│   ├── build_demo_knowledge_base.py
│   ├── serve_medgemma.py         # OpenAI-compatible runtime server
│   ├── cloud/                    # H100/RTX4090 train + FPT Cloud deploy scripts
│   ├── dev/                      # Local dev launchers (PowerShell) + mock model
│   ├── qa/                       # Quality gate, doctor-review export/import
│   ├── tests/                    # Pytest for the data/training pipeline
│   ├── temp/                     # Scratch crawlers + VSL data tooling
│   └── requirements_train.txt
│
├── notebooks/                    # train_medical_adapter.ipynb, train_psychology_adapter.ipynb
│
├── output/                       # Adapter outputs (gitignored)
│   ├── medisign-medgemma4b-adapter/             # Medical (preload)
│   └── medisign_medgemma4b_psychology/adapter/  # Psychology (lazy)
│
├── docs/
│   ├── engineering/              # api-contract, dev-setup, branching, test-strategy...
│   ├── training/
│   │   ├── QLORA_TRAINING.md
│   │   └── planRAG_Chat.md
│   ├── design UI/Web/MediSign_AI_UI_Web_Final.md
│   └── report/Quyển báo cáo tổng kết đề tài SV NCKH cấp Trường (1).doc
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Cài đặt & Chạy

### Yêu cầu

- Python 3.11+
- Node.js 20+
- Flutter SDK ≥3.4
- PostgreSQL 16
- Docker (tùy chọn)

### 1. Clone & cấu hình môi trường

```bash
git clone https://github.com/VNDT1625/MediSign_AI.git
cd MediSign_AI
cp .env.example .env
# Chỉnh sửa .env theo môi trường của bạn
```

### 2. Backend (FastAPI)

```bash
cd apps/backend_fastapi
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 3. Web Frontend (Next.js)

```bash
cd apps/web_next
npm install
cp .env.local.example .env.local   # tùy chọn: thêm GOOGLE_GEMINI_API_KEY cho Sign Mode fallback
npm run dev
```

Web app: http://localhost:3000

### 4. Mobile (Flutter)

```bash
cd apps/mobile_flutter
flutter pub get
flutter run
```

### 5. Docker (Backend + PostgreSQL)

```bash
docker-compose up -d
```

Backend: port 8000 · PostgreSQL: port 5432.

---

## Biến môi trường

Xem `.env.example` để biết đầy đủ.

### Database
```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/medisign
```

### Auth
```env
BACKEND_JWT_SECRET_KEY=change-this-secret-key-at-least-32-bytes
BACKEND_JWT_ACCESS_TOKEN_MINUTES=15
BACKEND_JWT_REFRESH_TOKEN_DAYS=30
```

### AI — MedGemma (khi đã train xong adapter)
```env
BACKEND_AI_PROVIDER=openai_compatible
BACKEND_AI_MODEL=google/medgemma-1.5-4b-it
BACKEND_AI_MEDICAL_MODEL=medisign-medgemma-medical
BACKEND_AI_PSYCHOLOGY_MODEL=medisign-medgemma-psychology
BACKEND_AI_BASE_URL=http://localhost:8080/v1
BACKEND_AI_API_KEY=
BACKEND_MEDGEMMA_BASE_MODEL=google/medgemma-1.5-4b-it
BACKEND_MEDGEMMA_MEDICAL_ADAPTER_PATH=../../output/medisign-medgemma4b-adapter
BACKEND_MEDGEMMA_PSYCHOLOGY_ADAPTER_PATH=../../output/medisign_medgemma4b_psychology/adapter
```

### AI — MVP (không cần GPU)
```env
BACKEND_AI_PROVIDER=rule_based
```

### RAG
```env
BACKEND_RAG_ENABLED=true
BACKEND_RAG_KNOWLEDGE_BASE_PATH=data/knowledge_base/knowledge_base.json
BACKEND_RAG_DEFAULT_TOP_K=5
BACKEND_RAG_MAX_CONTEXT_CHARS=6000
BACKEND_RAG_MIN_SCORE=0.15
```

### Triage AI (qua AI server, đã cấu hình ở `BACKEND_AI_*` phía trên)

Nếu `BACKEND_AI_PROVIDER=openai_compatible` thì triage tự động dùng MedGemma medical adapter qua AI server. Khi đặt về `rule_based` thì triage chạy hoàn toàn rule-based (vẫn hoạt động đầy đủ).

### Email (để trống = console mode)
```env
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_FROM_NAME=MediSign AI
FRONTEND_BASE_URL=http://localhost:3000
```

### Sign Mode (VSL) — Gemini Vision

Đặt trong `apps/web_next/.env.local` (không phải `.env` gốc) — chỉ web frontend dùng:
```env
# Server-only key cho route /api/sign/recognize. KHÔNG đặt prefix NEXT_PUBLIC_.
GOOGLE_GEMINI_API_KEY=
```
Nhận diện realtime on-device (TFJS + MediaPipe) không cần key này; key chỉ dùng cho đường fallback quay video.

---

## API Endpoints

### Auth (`/api/v1/auth/`)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/auth/register` | Đăng ký tài khoản |
| POST | `/auth/login` | Đăng nhập (email hoặc số điện thoại) |
| POST | `/auth/refresh` | Làm mới access token |
| POST | `/auth/logout` | Đăng xuất |
| GET | `/auth/me` | Thông tin user hiện tại |
| POST | `/auth/change-password` | Đổi mật khẩu |
| POST | `/auth/forgot-password` | Yêu cầu reset mật khẩu |
| POST | `/auth/reset-password` | Xác nhận reset với token |

### AI Chat (`/api/v1/ai/`)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/ai/chat` | Chat với MedGemma (medical hoặc psychology). Hỗ trợ cả JSON và `multipart/form-data` (kèm ảnh X-quang/da liễu). Khi gửi `conversation_id` → đi vào multi-turn diagnostic flow (yêu cầu auth). |
| GET | `/ai/status` | Trạng thái AI provider + adapter |
| GET | `/ai/rag/status` | Trạng thái RAG index |
| POST | `/ai/rag/search` | Tìm kiếm trực tiếp trong knowledge base |
| POST | `/ai/rag/rebuild` | Rebuild RAG index |
| GET | `/ai/conversations` | List hội thoại của user (paginated) |
| GET | `/ai/conversations/{id}` | Chi tiết hội thoại + DiagnosticState cuối cùng |
| DELETE | `/ai/conversations/{id}` | Soft-delete (archive) hội thoại |
| POST | `/ai/conversations/{id}/feedback` | Phản hồi đúng/sai sau khi đi khám thật |
| GET | `/ai/summary` | Quick Summary widget — projection từ DiagnosticState mới nhất |

Ví dụ request chat:
```json
POST /api/v1/ai/chat
{
  "message": "Tôi bị sốt và đau họng 2 ngày",
  "adapter": "medical",
  "use_rag": true,
  "rag_top_k": 5
}
```

SoulGarden:
```json
{
  "message": "Hôm nay tôi rất căng thẳng và khó ngủ",
  "adapter": "psychology"
}
```

### Tư vấn & Thuốc

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/v1/consult/triage` | Phân loại triệu chứng (rule-based + AI) — public |
| GET | `/api/v1/consult/triage/history` | Lịch sử triage (auth) |
| DELETE | `/api/v1/consult/triage/{id}` | Xoá một bản ghi triage (auth) |
| POST | `/api/v1/medicine/scan` | Tra cứu thuốc theo text (OCR + lookup) |
| POST | `/api/v1/medicine/scan-image` | Quét nhãn thuốc từ ảnh — MedGemma 4B vision đọc tên rồi lookup |
| GET | `/api/v1/medicine/cabinet` | Danh sách tủ thuốc cá nhân (auth) |
| POST | `/api/v1/medicine/cabinet` | Thêm thuốc vào tủ (auth) |
| PATCH/DELETE | `/api/v1/medicine/cabinet/{id}` | Sửa/xoá thuốc trong tủ |
| POST | `/api/v1/medicine/cabinet/{id}/dose` | Ghi nhận đã uống một liều |
| GET | `/api/v1/medicine/cabinet/today` | Lịch uống hôm nay (slots + next dose) |
| GET | `/api/v1/medicine/cabinet/upcoming` | Liều trong N giờ tới (cho push noti) |
| GET | `/api/v1/medicine/cabinet/{id}/history` | Lịch sử adherence của 1 thuốc |
| GET | `/api/v1/health` | Health check |

### Hồ sơ & Nhật ký (auth)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET/PUT/PATCH/DELETE | `/api/v1/profile` | CRUD hồ sơ cá nhân + cờ `consent_personal_context` |
| GET/POST | `/api/v1/journal` | List / tạo nhật ký Soul Garden |
| GET/PATCH/DELETE | `/api/v1/journal/{id}` | Đọc/sửa/xoá entry — kèm điểm `tree_points` gamification |

### Drug Lookup (`/api/drug/` — không có `/v1`)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/drug/` | Health check |
| GET | `/api/drug/list` | Danh sách tất cả thuốc (paginated) |
| POST | `/api/drug/search` | Tìm thuốc theo tên |
| GET | `/api/drug/search/{name}` | Tìm thuốc theo tên (GET) |
| GET | `/api/drug/suggestions/{keyword}` | Gợi ý tên thuốc |
| GET | `/api/drug/random/{count}` | Thuốc ngẫu nhiên |

### Admin (`/api/v1/admin/`) — yêu cầu `account_type=admin`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/admin/stats` | Thống kê tổng quan |
| GET | `/admin/stats/users` | Thống kê người dùng |
| GET | `/admin/stats/posts` | Thống kê bài viết cộng đồng |
| GET | `/admin/stats/workouts` | Thống kê tập luyện |
| GET/POST/PATCH/DELETE | `/admin/users` | Quản lý người dùng |
| GET/POST/PATCH/DELETE | `/admin/medicines` | Quản lý thuốc (medicine_registry) |
| GET/POST/PATCH/DELETE | `/admin/hospitals` | Quản lý bệnh viện |
| GET/PATCH/DELETE | `/admin/posts` | Kiểm duyệt bài viết cộng đồng |
| GET | `/admin/workouts` | Xem lịch sử tập luyện |
| GET | `/admin/goals` | Xem mục tiêu thể dục |
| GET | `/admin/kb-pending` | Danh sách KB record đợi duyệt |
| POST | `/admin/kb-pending/{id}/approve` | Duyệt → promote vào `data/knowledge_base/knowledge_base.json` + tạo edges |
| POST | `/admin/kb-pending/{id}/reject` | Từ chối record |
| GET | `/admin/kb-pending/stats` | Thống kê pending records |
| GET | `/admin/weight-proposals` | Đề xuất chỉnh trọng số bệnh-triệu chứng (sinh từ feedback loop) |
| POST | `/admin/weight-proposals/{id}/approve` | Duyệt đề xuất |

---

## Train MedGemma Adapter

### Cách dễ nhất — chạy trên FPT Cloud Notebook (H100)

Upload 2 notebook lên FPT Cloud Notebook hoặc Kaggle, sửa `HF_TOKEN`, Run All:

| Notebook | Thời gian H100 | Output |
|----------|---------------|--------|
| `notebooks/train_medical_adapter.ipynb` | ~1-1.5 giờ (3 epochs · r=16) | Push `thuaannn/medisign-medgemma4b-adapter` |
| `notebooks/train_psychology_adapter.ipynb` | ~30 phút (5 epochs · r=16) | Push `thuaannn/medisign-medgemma4b-psychology` |

Notebook tự động: cài deps + Flash-Attention 2, login HF, pull dataset từ HF, train QLoRA r=16 với BF16+TF32 (medical: 3 epochs, psychology: 5 epochs), smoke test, push adapter lên HF. Cấu hình notebook khác với `scripts/cloud/rtx4090_train_psychology.py` (LoRA r=8, 4 epochs, LR 1e-4) — chọn một entry point và stick với nó để có kết quả nhất quán.

Chi tiết workflow Train → Deploy: [`docs/training/QLORA_TRAINING.md`](docs/training/QLORA_TRAINING.md)
và [`scripts/cloud/train_dual_adapter.sh`](scripts/cloud/train_dual_adapter.sh).

### Sau khi train — Deploy lên FPT Cloud GPU VM

```bash
# 1. SSH vào VM, setup lần đầu
export HF_TOKEN='hf_YOUR_TOKEN'
bash setup-fpt-medgemma.sh

# 2. Pull cả 2 adapter từ HF (huggingface-cli — không phải git clone)
cd ~/MediSign_AI
huggingface-cli login
huggingface-cli download thuaannn/medisign-medgemma4b-adapter \
  --local-dir output/medisign-medgemma4b-adapter
huggingface-cli download thuaannn/medisign-medgemma4b-psychology \
  --local-dir output/medisign_medgemma4b_psychology/adapter

# 3. Start runtime server với cả 2 adapter
MEDISIGN_ADAPTER_PATH=$HOME/MediSign_AI/output/medisign-medgemma4b-adapter \
MEDISIGN_PSYCHOLOGY_ADAPTER_PATH=$HOME/MediSign_AI/output/medisign_medgemma4b_psychology/adapter \
bash scripts/cloud/start-fpt-medgemma.sh

# 4. Health check
curl http://FPT_VM_IP:8080/health
```

Server tự route theo field `model` trong request:
- `medisign-medgemma-medical` → Medical Adapter (preload khi start)
- `medisign-medgemma-psychology` → Psychology Adapter (lazy load)

Backend `.env` connect tới VM:
```env
BACKEND_AI_PROVIDER=openai_compatible
BACKEND_AI_BASE_URL=http://FPT_VM_IP:8080/v1
```

### Train manual (nâng cao)

Nếu muốn chạy script trực tiếp thay vì notebook:

```bash
pip install -r scripts/requirements_train.txt
huggingface-cli login

# Medical
python scripts/train_qlora_medgemma.py \
  --train_file data/training_clean/medgemma_4b/medical_train.jsonl \
  --eval_file  data/training_clean/medgemma_4b/medical_eval.jsonl \
  --num_epochs 3 \
  --adapter_dir output/medisign-medgemma4b-adapter

# Psychology
python scripts/train_qlora_medgemma.py \
  --train_file data/training_clean/medgemma_4b/psychology_train.jsonl \
  --eval_file  data/training_clean/medgemma_4b/psychology_eval.jsonl \
  --num_epochs 3 \
  --adapter_dir output/medisign_medgemma4b_psychology/adapter
```

---

## Trạng thái hiện tại

Các trạng thái dưới đây phản ánh mức độ hiện diện trong repository, không đồng nghĩa với chứng nhận production hoặc thẩm định lâm sàng.

| Component | Trạng thái | Ghi chú |
|-----------|-----------|---------|
| Rule-based triage | ✅ Implemented | Keyword matching, Vietnamese normalization; có benchmark định lượng |
| Drug lookup (DAV) | ✅ Implemented | 64.045 records, số đăng ký, hoạt chất, tương tác |
| RAG knowledge base | ✅ Implemented | 128.380 records, BM25 local, auto-reload |
| FastAPI backend | ✅ Implemented | Auth, triage, medicine, AI chat, admin |
| Next.js web app | ✅ Implemented | Auth flow, chat, medicine, soul-garden |
| Sign Mode VSL (realtime on-device) | 🧪 Prototype | TFJS Bi-LSTM + MediaPipe, wired vào chat (`VslRealtimeComposer`) |
| Sign Mode VSL (Gemini video fallback) | 🧪 Prototype | Route `/api/sign/recognize`, Gemini 2.5 Flash |
| Flutter mobile | 🔄 Partial | UI done, API integration một phần (mock mode) |
| MedGemma 1.5 4B Medical adapter | 🧪 Artifact available | Adapter và 15.693 training records có trong pipeline; cần quality benchmark cố định |
| MedGemma Psychology adapter | 🧪 Artifact available | Adapter và 1.201 OARS records có trong pipeline; cần quality benchmark cố định |
| Dual adapter runtime server | ✅ Implemented | Single endpoint, route theo `model` field |
| Vision drug classifier | ❌ Not ready | Cần 10k+ ảnh thuốc có nhãn |
| Fixed eval sets | ❌ Incomplete | `data/eval_sets` cần real cases |

---

## Đội ngũ

**Trưởng nhóm:** Nguyễn Duy Thuận — Kiến trúc & AI · Sinh viên 23DKTPM1A · MSSV 2311555799

**Giảng viên hướng dẫn:** ThS. Đỗ Gia Bảo

**Đề tài:** Nghiên cứu Khoa học Sinh viên cấp Trường · Trường Đại học Nguyễn Tất Thành · TP.HCM 2026

**Các tổ chuyên môn:** AI Research (ML & Vision-Language) · Backend & Data (FastAPI · PostgreSQL) · Mobile & Web (Flutter · Next.js) · UX & Accessibility

---

## Disclaimer

- AI chỉ đưa ra gợi ý sơ bộ, **không thay thế chẩn đoán hoặc chỉ định của bác sĩ**.
- Luôn tham khảo bác sĩ/dược sĩ trước khi dùng thuốc.
- Nếu có dấu hiệu nặng (khó thở, đau ngực, ngất, chảy máu, ý nghĩ tự hại), hãy **gọi cấp cứu 115** hoặc đến cơ sở y tế ngay lập tức.
