# context.md — MediSign AI
> Tạo bởi AS | Cập nhật: 2026-05-27

## 1. TỔNG QUAN DỰ ÁN

**Tên:** MediSign AI
**Phiên bản:** 0.2.0
**Mục đích:** Nền tảng y tế đa nền tảng (web + mobile) phục vụ người Việt — tư vấn triệu chứng, tra cứu thuốc, chăm sóc sức khỏe tâm thần, theo dõi thể lực, hỗ trợ người khuyết tật.

**Tính năng chính:**
- Tư vấn triệu chứng — phân loại 3 mức khẩn cấp: Xanh / Vàng / Đỏ (rule-based + AI)
- Tra cứu thuốc — 60.472 records từ Cục Dược Việt Nam (DAV)
- AI Chat y tế — MedGemma 1.5 4B + RAG 128.380 records
- SoulGarden — sức khỏe tâm thần, nhật ký cảm xúc
- Fitness — theo dõi tập luyện, phát hiện tư thế ML on-device
- Cộng đồng — chia sẻ kinh nghiệm sức khỏe ẩn danh
- Hỗ trợ NKT — ngôn ngữ ký hiệu, voice tiếng Việt, Elderly Mode

**Disclaimer:** AI chỉ đưa ra gợi ý sơ bộ, không thay thế chẩn đoán bác sĩ.

---

## 2. KIẾN TRÚC MONOREPO

```
MediSign_AI - Copy/
├── apps/
│   ├── backend_fastapi/     # Python FastAPI backend
│   ├── mobile_flutter/      # Flutter mobile app
│   └── web_next/            # Next.js 14 web app
├── packages/
│   ├── ai_training/         # Scripts train MedGemma/Qwen
│   ├── data/                # Training data packages
│   ├── decision_trees/      # Rule-based triage trees
│   ├── prompt_library/      # Prompt templates
│   └── shared_contracts/    # JSON Schema API contracts
├── data/
│   ├── knowledge_base/      # RAG knowledge base JSON
│   ├── training_raw/        # Raw training data
│   ├── training_clean/      # Cleaned training data
│   ├── eval_sets/           # Evaluation datasets
│   └── external/            # External datasets
├── scripts/                 # Build, crawl, training scripts
├── docs/                    # Documentation
├── notebooks/               # Jupyter notebooks
├── output/                  # Model adapter outputs
└── docker-compose.yml
```

**3 Deployment Modes:**
| Mode | Model | Use case |
|------|-------|----------|
| Cloud | Qwen 2.5 72B + LoRA Medical (A100) | AI mạnh nhất |
| Local | Gemma 2B + 2 LoRA Adapters (~1.65GB RAM) | 100% offline |
| Hybrid | Cloud complex + Local fallback | Cân bằng |

**MVP hiện tại:** `BACKEND_AI_PROVIDER=rule_based` — không cần GPU.

---

## 3. BACKEND — FastAPI

**Vị trí:** `apps/backend_fastapi/`
**Version:** 0.2.0
**Python:** >=3.11
**Port:** 8000
**API Prefix:** `/api/v1`

### 3.1 Routes

| Route file | Prefix | Chức năng |
|-----------|--------|-----------|
| `auth.py` | `/auth` | Đăng ký, đăng nhập, refresh token, đổi mật khẩu |
| `profile.py` | `/profile` | Thông tin cá nhân, cập nhật hồ sơ |
| `consult.py` | `/consult` | Tư vấn triệu chứng AI |
| `triage.py` | `/triage` | Phân loại mức độ khẩn cấp |
| `medicine.py` | `/medicine` | Tra cứu thuốc, tủ thuốc cá nhân |
| `ai.py` | `/ai` | AI chat y tế, RAG |
| `conversations.py` | `/conversations` | Lịch sử hội thoại |
| `summary.py` | `/summary` | Tóm tắt nhanh sức khỏe |
| `journal.py` | `/journal` | Nhật ký sức khỏe/cảm xúc |
| `admin.py` | `/admin` | Quản trị hệ thống |
| `drug_router.py` | `/drugs` | Drug lookup DAV database |
| `health.py` | `/health` | Health check endpoint |

### 3.2 Services

| Service | Chức năng |
|---------|-----------|
| `ai_model_service.py` | Gọi AI model qua httpx (OpenAI-compatible) |
| `ai_triage_service.py` | Phân loại triệu chứng bằng AI |
| `rag_engine.py` | RAG engine BM25 local search |
| `rag_service.py` | RAG service wrapper |
| `diagnostic_orchestrator.py` | Điều phối luồng chẩn đoán |
| `diagnostic_state_manager.py` | Quản lý trạng thái chẩn đoán |
| `disease_symptom_graph.py` | Đồ thị bệnh-triệu chứng |
| `drug_lookup_service.py` | Tra cứu thuốc DAV |
| `medicine_service.py` | Quản lý tủ thuốc |
| `medicine_vision_service.py` | Nhận dạng thuốc qua ảnh |
| `auth_service.py` | JWT auth, password hashing |
| `embedding_client.py` | Vector embedding client |
| `oars_prompt_layer.py` | OARS prompt framework |
| `personal_context_service.py` | Context cá nhân hóa |
| `chat_memory_service.py` | Bộ nhớ hội thoại |
| `quick_summary_service.py` | Tóm tắt nhanh |
| `cabinet_service.py` | Tủ thuốc cá nhân |
| `feedback_service.py` | Thu thập feedback |
| `image_preprocessor.py` | Tiền xử lý ảnh (OpenCV, Pillow) |
| `text_processing.py` | Xử lý văn bản tiếng Việt |
| `triage_service.py` | Rule-based triage |
| `triage_formatter.py` | Format kết quả triage |
| `email_service.py` | Gửi email (SMTP) |
| `kb_lazy_loader.py` | Lazy load knowledge base |