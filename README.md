# MediSign AI

Ứng dụng y tế thông minh cho người Việt — hỗ trợ tra cứu thuốc, phân loại triệu chứng, chăm sóc sức khỏe tâm thần và theo dõi thể lực.

> **Lưu ý y tế:** AI chỉ đưa ra gợi ý sơ bộ, không thay thế chẩn đoán hoặc chỉ định của bác sĩ. Khi có dấu hiệu nặng, hãy gọi cấp cứu **115** hoặc đến cơ sở y tế ngay.

---

## Mục lục

- [Tổng quan](#tổng-quan)
- [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
- [Model AI — MedGemma 4B](#model-ai--medgemma-4b)
- [RAG — Kho kiến thức y tế](#rag--kho-kiến-thức-y-tế)
- [Cơ sở dữ liệu thuốc](#cơ-sở-dữ-liệu-thuốc)
- [Tech Stack](#tech-stack)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Cài đặt & Chạy](#cài-đặt--chạy)
- [Biến môi trường](#biến-môi-trường)
- [API Endpoints](#api-endpoints)
- [Train MedGemma Adapter](#train-medgemma-adapter)
- [Trạng thái hiện tại](#trạng-thái-hiện-tại)
- [Disclaimer](#disclaimer)

---

## Tổng quan

MediSign AI là nền tảng y tế đa nền tảng (web + mobile) với các tính năng chính:

- **Tư vấn triệu chứng** — phân loại mức độ khẩn cấp (emergency / urgent / non-emergency) bằng rule-based + AI
- **Tra cứu thuốc** — cơ sở dữ liệu 22.585 records từ Cục Dược Việt Nam (DAV)
- **AI Chat y tế** — trợ lý tiếng Việt dựa trên MedGemma 4B + RAG
- **SoulGarden** — hỗ trợ sức khỏe tâm thần, nhật ký cảm xúc
- **Fitness** — theo dõi tập luyện, phát hiện tư thế bằng ML on-device
- **Cộng đồng** — chia sẻ kinh nghiệm sức khỏe ẩn danh, có kiểm duyệt

---

## Kiến trúc hệ thống

```
Flutter App / Next.js Web
         │
         ▼
   FastAPI Backend  ──────────────────────────────────────────┐
         │                                                     │
         ├── Rule-based Triage (luôn hoạt động)               │
         ├── Drug Lookup Service (22k+ records DAV)           │
         ├── RAG Service (BM25 local, không cần vector DB)    │
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

FastAPI **không load model trực tiếp**. Model chạy trong một GPU process riêng biệt và expose OpenAI-compatible endpoint. Backend chỉ là thin client gọi qua `httpx`.

### 3 Deployment Modes

| Mode | Model chính | Use case |
|------|-------------|----------|
| **Cloud** | Qwen 2.5 72B + LoRA Medical (self-hosted A100) | AI mạnh nhất, chấp nhận gửi data lên cloud |
| **Local** | Gemma 2B + 2 LoRA Adapters (~1.65 GB RAM) | 100% offline, data không rời máy |
| **Hybrid** | Cloud cho complex queries + Local fallback | Cân bằng hiệu năng và bảo mật |

**MVP hiện tại:** `BACKEND_AI_PROVIDER=rule_based` — không cần GPU, backend trả fallback response an toàn.

---

## Model AI — MedGemma 4B

### Base Model

| Thành phần | Giá trị |
|------------|---------|
| Base model | `google/medgemma-1.5-4b-it` |
| Phương pháp fine-tune | **QLoRA** (không train lại full model) |
| LoRA rank | 32 |
| Kích thước adapter | ~120–160 MB |

> MedGemma là model y tế của Google, được gated trên Hugging Face. Cần chấp nhận điều khoản tại [huggingface.co/google/medgemma-1.5-4b-it](https://huggingface.co/google/medgemma-1.5-4b-it) trước khi train.

### Hai Adapter

| Adapter | Tên runtime | Mục đích |
|---------|-------------|----------|
| Medical | `medisign-medgemma-medical` | Tư vấn y tế tiếng Việt, tra cứu thuốc, triệu chứng |
| Psychology | `medisign-medgemma-psychology` | SoulGarden — hỗ trợ tâm lý, không chẩn đoán bệnh tâm thần |

Adapter output paths:
```
output/medisign_medgemma4b/adapter/            ← medical
output/medisign_medgemma4b_psychology/adapter/ ← psychology
```

### Training Data (MedGemma 4B)

```
data/training_clean/medgemma_4b/
├── merged_dataset.json   17.196 records (sau dedup)
├── train.jsonl           15.476 records
├── eval.jsonl             1.720 records
├── merge_stats.json
└── format_stats.json
```

Nguồn dữ liệu chính:

| Nguồn | Records |
|-------|--------:|
| `all_medical` | 12.391 |
| `medquad` | 1.362 |
| `drug_db` | 968 |
| `medical_dialogue_2010` | 800 |
| `vn_drugs_commercial` | 576 |
| `vn_symptoms_culture` | 224 |
| Các nguồn khác | ~875 |

Format JSONL (Gemma chat template):
```json
{
  "text": "<start_of_turn>user\n...<end_of_turn>\n<start_of_turn>model\n...<end_of_turn>",
  "instruction": "Bạn là MediSign AI...",
  "input": "Câu hỏi của người dùng",
  "output": "Câu trả lời y tế có disclaimer",
  "source": "all_medical"
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

### Triage AI (Qwen fallback)

`AITriageService` dùng **Qwen via DashScope** cho phân tích triệu chứng phức tạp:

```
REQUEST → Rule-based (fast path, luôn chạy trước)
              │
              ▼ Nếu KHÔNG phải emergency → Qwen API (nếu có DASHSCOPE_API_KEY)
              │
              ▼ Nếu Qwen lỗi / không có key → Rule-based fallback
```

Emergency keywords (rule-based, không qua AI): `khó thở`, `đau ngực`, `ngất`, `chết ngươn`.

---

## RAG — Kho kiến thức y tế

Backend tích hợp **BM25-style sparse retrieval** tự xây dựng — không cần vector DB hay embedding model.

Đặc điểm:
- Vietnamese text normalization (NFD, bỏ dấu, `đ→d`)
- Medical synonym expansion: `panadol → paracetamol`, `sốt → nhiệt`, `khó thở → hô hấp`, v.v.
- Confidence scoring + type boosting (drug, drug_interaction, vietnam_common_disease)
- Auto-reload khi file knowledge base thay đổi (không cần restart)

Cấu hình mặc định:

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

## Cơ sở dữ liệu thuốc

Backend ưu tiên file lớn nhất có sẵn, fallback về file nhỏ hơn:

| File | Records | Ghi chú |
|------|--------:|---------|
| `drug_database_dav_detailed_10k.json` | 22.585 | **Ưu tiên 1** — DAV chi tiết |
| `drug_database_10k_full.json` | — | Ưu tiên 2 |
| `drug_database_10k.json` | — | Ưu tiên 3 |
| `drug_database_expanded.json` | — | Ưu tiên 4 |
| `drug_database.json` | — | Fallback cuối |

File tốt nhất hiện có (`drug_database_dav_detailed_10k.json`):
- 22.585 records tổng
- 15.884 tên thuốc unique
- 22.237 records có số đăng ký
- 10.574 records có hoạt chất

---

## Tech Stack

### Backend (`apps/backend_fastapi`)

| Thành phần | Công nghệ |
|------------|-----------|
| Framework | FastAPI 0.115+ |
| Server | Uvicorn (standard) |
| Python | 3.11+ |
| ORM | SQLAlchemy 2.0 |
| DB Driver | psycopg3 (binary) |
| Auth | PyJWT (HS256), PBKDF2-SHA256 (120k iterations) |
| HTTP Client | httpx (async) |
| AI SDK | dashscope (Alibaba Qwen) |
| Validation | Pydantic Settings v2 |
| Linting | Ruff + Black |

### Web Frontend (`apps/web_next`)

| Thành phần | Công nghệ |
|------------|-----------|
| Framework | Next.js 14.2 (App Router) |
| Language | TypeScript 5.6 |
| UI | React 18.3 + Tailwind CSS 3.4 |
| Forms | react-hook-form 7 + Zod 4 |
| Data Fetching | TanStack Query v5 |
| Testing | Vitest 3 + Testing Library + MSW 2 + Playwright |

### Mobile (`apps/mobile_flutter`)

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
│   ├── backend_fastapi/          # FastAPI backend
│   │   ├── app/
│   │   │   ├── api/routes/       # auth, consult, medicine, ai, admin
│   │   │   ├── core/             # config, security (JWT, PBKDF2)
│   │   │   ├── database/         # SQLAlchemy models (cloud + local)
│   │   │   ├── schemas/          # Pydantic schemas
│   │   │   └── services/         # ai_model, rag, drug_lookup, triage
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── web_next/                 # Next.js 14 web app
│   │   ├── app/                  # App Router pages
│   │   │   ├── (public)/         # landing, about, pricing, download
│   │   │   └── app/              # protected shell (chat, medicine, soul-garden, profile)
│   │   ├── components/
│   │   ├── lib/auth/             # AuthProvider, tokenStore, fetcher
│   │   └── middleware.ts         # Edge route guard (/app/*)
│   │
│   └── mobile_flutter/           # Flutter cross-platform app
│       └── lib/features/
│           ├── auth/             # Login, register, welcome
│           ├── consult/          # AI symptom consultation
│           ├── medicine_cabinet/ # Personal medicine tracker
│           ├── medicine_scan/    # Camera-based drug recognition
│           ├── soul_garden/      # Mental health, mood journal
│           ├── fitness/          # Workout + pose detection
│           └── community/        # Anonymous health community
│
├── packages/
│   ├── ai_training/              # Training docs + README
│   ├── shared_contracts/         # OpenAPI + JSON Schema (TypeScript)
│   ├── decision_trees/           # Rule-based decision logic
│   └── prompt_library/           # Prompt templates
│
├── data/
│   ├── training_clean/
│   │   ├── medgemma_4b/          # train.jsonl, eval.jsonl (17k records)
│   │   └── drug_database_*.json  # DAV drug databases
│   └── knowledge_base/
│       └── knowledge_base.json   # RAG knowledge base
│
├── scripts/                      # Data prep, training, crawling
│   ├── train_qlora_medgemma.py   # Main training script
│   ├── train_qlora_medgemma_smoke_test.py
│   ├── prepare_medgemma_data.py
│   ├── format_medgemma_dataset.py
│   ├── build_demo_knowledge_base.py
│   ├── crawl_dav_*.py            # DAV drug registry crawlers
│   └── requirements_train.txt
│
├── output/                       # Adapter outputs (gitignored)
│   ├── medisign_medgemma4b/adapter/
│   └── medisign_medgemma4b_psychology/adapter/
│
├── docs/
│   ├── MODEL_INTEGRATION.md
│   ├── database.md
│   └── training/QLORA_TRAINING.md
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
git clone <repo-url>
cd MediSign_AI
cp .env.example .env
# Chỉnh sửa .env theo môi trường của bạn
```

### 2. Backend (FastAPI)

```bash
cd apps/backend_fastapi

# Tạo virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# Cài dependencies
pip install -e ".[dev]"

# Chạy server
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 3. Web Frontend (Next.js)

```bash
cd apps/web_next
npm install
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

Khởi động: backend trên port 8000, PostgreSQL trên port 5432.

---

## Biến môi trường

Xem `.env.example` để biết đầy đủ. Các biến quan trọng:

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
BACKEND_AI_PROVIDER=openai_compatible   # đổi từ rule_based
BACKEND_AI_MODEL=google/medgemma-1.5-4b-it
BACKEND_AI_MEDICAL_MODEL=medisign-medgemma-medical
BACKEND_AI_PSYCHOLOGY_MODEL=medisign-medgemma-psychology
BACKEND_AI_BASE_URL=http://localhost:8080/v1
BACKEND_AI_API_KEY=                     # để trống nếu không cần auth
BACKEND_MEDGEMMA_MEDICAL_ADAPTER_PATH=../../output/medisign_medgemma4b/adapter
BACKEND_MEDGEMMA_PSYCHOLOGY_ADAPTER_PATH=../../output/medisign_medgemma4b_psychology/adapter
```

### AI — Chế độ MVP (không cần GPU)
```env
BACKEND_AI_PROVIDER=rule_based          # default — trả fallback response an toàn
```

### RAG
```env
BACKEND_RAG_ENABLED=true
BACKEND_RAG_KNOWLEDGE_BASE_PATH=data/knowledge_base/knowledge_base.json
BACKEND_RAG_DEFAULT_TOP_K=5
BACKEND_RAG_MAX_CONTEXT_CHARS=6000
BACKEND_RAG_MIN_SCORE=0.15
```

### Triage AI (Qwen — tùy chọn)
```env
DASHSCOPE_API_KEY=                      # API key từ Alibaba Cloud DashScope
AI_MODEL=qwen-turbo
```

### Email (để trống = console mode, in link ra log)
```env
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USERNAME=
EMAIL_PASSWORD=
FRONTEND_BASE_URL=http://localhost:3000
```

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
| POST | `/ai/chat` | Chat với MedGemma (medical hoặc psychology) |
| GET | `/ai/status` | Trạng thái AI provider + adapter |
| GET | `/ai/rag/status` | Trạng thái RAG index |
| POST | `/ai/rag/search` | Tìm kiếm trực tiếp trong knowledge base |
| POST | `/ai/rag/rebuild` | Rebuild RAG index |

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
| POST | `/consult/triage` | Phân loại triệu chứng (rule-based + AI) |
| POST | `/medicine/scan` | Nhận diện thuốc (OCR + lookup) |
| GET | `/health` | Health check |

### Drug Lookup (`/api/drug/`)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/drug/list` | Danh sách tất cả thuốc |
| POST | `/api/drug/search` | Tìm thuốc theo tên |
| GET | `/api/drug/search/{name}` | Tìm thuốc theo tên (GET) |
| GET | `/api/drug/suggestions/{keyword}` | Gợi ý tên thuốc |
| GET | `/api/drug/random/{count}` | Thuốc ngẫu nhiên |

### Admin (`/api/v1/admin/`)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/admin/stats` | Thống kê tổng quan |
| CRUD | `/admin/users` | Quản lý người dùng |
| CRUD | `/admin/medicines` | Quản lý thuốc |
| CRUD | `/admin/hospitals` | Quản lý bệnh viện |
| CRUD | `/admin/posts` | Quản lý bài viết cộng đồng |

---

## Train MedGemma Adapter

### Yêu cầu

- GPU: RTX 4090 (24 GB) hoặc 2× T4 (Kaggle free tier)
- CUDA 12.1+
- Tài khoản Hugging Face với quyền truy cập `google/medgemma-1.5-4b-it`

### Cài đặt training dependencies

```bash
pip install -r scripts/requirements_train.txt
```

Dependencies chính: `torch>=2.4`, `transformers>=4.50`, `peft>=0.13`, `bitsandbytes>=0.44`, `trl>=0.12`, `accelerate>=0.34`.

### Bước 1: Chấp nhận điều khoản MedGemma

Truy cập [huggingface.co/google/medgemma-1.5-4b-it](https://huggingface.co/google/medgemma-1.5-4b-it) và chấp nhận MedGemma Health AI Developer Foundations terms.

```bash
huggingface-cli login
# Nhập access token với scope "read"
```

### Bước 2: Chuẩn bị dữ liệu (nếu chưa có)

```bash
python scripts/prepare_medgemma_data.py
python scripts/format_medgemma_dataset.py
```

### Bước 3: Smoke test (không cần GPU)

```bash
python scripts/train_qlora_medgemma_smoke_test.py
```

### Bước 4: Train

```bash
# Local (RTX 4090)
python scripts/train_qlora_medgemma.py

# Smoke run nhanh (5 steps)
python scripts/train_qlora_medgemma.py --max_steps 5

# Resume từ checkpoint
python scripts/train_qlora_medgemma.py --resume_from_checkpoint output/medisign_medgemma4b/checkpoints/checkpoint-XXXX
```

**Trên Kaggle (free 2× T4, ~4-5 giờ):** Xem hướng dẫn chi tiết tại `docs/training/QLORA_TRAINING.md`.

**Trên Vast.ai / RunPod (RTX 4090, ~3 giờ):** Xem `docs/training/QLORA_TRAINING.md`.

### CLI Options

```
--model_id                  default: google/medgemma-1.5-4b-it
--train_file                default: data/training_clean/medgemma_4b/train.jsonl
--eval_file                 default: data/training_clean/medgemma_4b/eval.jsonl
--output_dir                default: output/medisign_medgemma4b/checkpoints
--adapter_dir               default: output/medisign_medgemma4b/adapter
--num_epochs                default: 3
--max_seq_length            default: 2048
--per_device_batch_size     default: 4
--gradient_accumulation_steps  default: 4
--learning_rate             default: 2e-4
--max_steps                 default: -1 (không giới hạn)
```

### Bước 5: Kích hoạt model sau khi train

1. Build/refresh RAG knowledge base:
   ```bash
   python scripts/build_demo_knowledge_base.py
   ```

2. Khởi động MedGemma runtime server (vLLM, TGI, hoặc custom server) với base model + adapter.

3. Cập nhật `.env`:
   ```env
   BACKEND_AI_PROVIDER=openai_compatible
   BACKEND_AI_BASE_URL=http://localhost:8080/v1
   ```

4. Kiểm tra:
   ```bash
   GET /api/v1/ai/rag/status   # RAG index ready?
   GET /api/v1/ai/status       # Model + adapter ready?
   POST /api/v1/ai/chat        # Test chat
   ```

---

## Trạng thái hiện tại

| Component | Trạng thái | Ghi chú |
|-----------|-----------|---------|
| Rule-based triage | ✅ Done | Keyword matching, Vietnamese normalization |
| Drug lookup (DAV) | ✅ Done | 22.585 records, số đăng ký, hoạt chất |
| FastAPI backend | ✅ Done | Auth, triage, medicine, AI chat, admin |
| Next.js web app | ✅ Done | Full auth flow, chat, medicine, soul-garden |
| RAG service | ✅ Done | BM25 local, Vietnamese synonyms, auto-reload |
| Flutter mobile | 🔄 Partial | UI done, API integration một phần (mock mode) |
| MedGemma 4B medical adapter | 🔜 Ready to train | Data sẵn sàng, cần GPU |
| MedGemma psychology adapter | 🔜 Planned | Cần dataset riêng |
| Vision drug classifier | ❌ Not ready | Cần 10k+ ảnh thuốc có nhãn |
| Fixed eval sets | ❌ Incomplete | `data/eval_sets` cần real cases |

---

## Disclaimer

- AI chỉ đưa ra gợi ý sơ bộ, **không thay thế chẩn đoán hoặc chỉ định của bác sĩ**.
- Luôn tham khảo bác sĩ/dược sĩ trước khi dùng thuốc.
- Nếu có dấu hiệu nặng (khó thở, đau ngực, ngất, chảy máu, ý nghĩ tự hại), hãy **gọi cấp cứu 115** hoặc đến cơ sở y tế ngay lập tức.
