# MediSign AI – Kế hoạch Triển khai Kỹ thuật (Technical Tasks)

> **Dựa trên:** Required.md v1.0 & Design.md v1.0

---

## GIAI ĐOẠN 1: SETUP & FOUNDATION (Tuần 1-2)

- [ ] **Task 1.1: Setup Project Repository**
    - [ ] Create GitHub repo with branching strategy (main, dev, feature/*).
    - [ ] Setup Flutter project structure (Clean Architecture).
    - [ ] Setup FastAPI backend structure.
    - [ ] Configure CI/CD basic pipeline (GitHub Actions).

- [ ] **Task 1.2: Database Implementation**
    - [ ] Design & Implement SQLite schema (Local - Soul Garden).
    - [ ] Design & Implement PostgreSQL schema (Cloud - Medicine/User).
    - [ ] Write migration scripts.

- [ ] **Task 1.3: Basic UI Skeleton**
    - [ ] Create main layout with Bottom Navigation.
    - [ ] Implement onboarding flow (User Profile Setup + **Mode Selector**: Hybrid/Local/Cloud).
    - [ ] Implement `DeviceManager` auto-detect → recommend mode.
    - [ ] Implement "Emergency Call" button logic.

- [ ] **Task 1.4: Authentication & MFA**
    - [ ] Implement đăng ký/đăng nhập Email + Mật khẩu (bcrypt hash).
    - [ ] Implement đăng nhập SĐT + OTP SMS.
    - [ ] Implement xác thực sinh trắc (vân tay/FaceID) qua Android Keystore / iOS Keychain.
    - [ ] Implement TOTP Authenticator (QR code setup + mã 6 số).
    - [ ] Implement MFA 2 bước bắt buộc: Mật khẩu → Sinh trắc / OTP+Auth / Recovery Key.
    - [ ] Implement JWT session (Access Token 15 phút + Refresh Token 30 ngày).
    - [ ] Implement brute-force protection (5 lần sai → khóa 15 phút).
    - [ ] Implement Recovery Key (12 từ) + Recovery Codes (8 mã).
    - [ ] Implement quản lý thiết bị (xem/đăng xuất thiết bị).
---

## GIAI ĐOẠN 2: CORE AI MODULES (Tuần 3-4)

- [ ] **Task 2.1: Gemini Integration (Cloud)**
    - [ ] Setup Google Cloud Project & Enable Gemini API.
    - [ ] Create FastAPI endpoint `POST /api/v1/consult/triage`.
    - [ ] Implement prompt engineering for medical triage (Role: Dr. MediSign).
    - [ ] Implement Anonymization Layer (Strip PII before sending).

- [ ] **Task 2.2: Local LLM Integration (Mobile)**
    - [ ] Implement `DeviceManager` to check RAM/Chipset.
    - [ ] **High-end**: Integrate MediaPipe LLM (Gemma 2B).
    - [ ] **Low-end**: Disable Local LLM -> Force Cloud Mode.
    - [ ] Implement RAG pipeline: Query Local DB → Inject vào Prompt → LLM viết trả lời.
    - [ ] Implement logic to rewrite Cloud response based on Local Context (Soul Garden).
    - [ ] **(Sau MVP)**: LoRA fine-tune Gemma 2B với 5K-20K Q&A y tế VN → MediSign-Gemma.

- [ ] **Task 2.3: Medicine Scanner (OCR)**
    - [ ] Integrate Google ML Kit Text Recognition.
    - [ ] Implement logic to parse text from image -> extract medicine name.
    - [ ] Create `MedicineService` to query Cục Dược Data based on extracted name.
    - [ ] Implement Interaction Checker logic.

---

## GIAI ĐOẠN 3: ACCESSIBILITY & UI (Tuần 5-6)

- [ ] **Task 3.1: 3D Avatar Nurse**
    - [ ] Integrate Rive/Unity view into Flutter.
    - [ ] Create basic animations (Idle, Talking, Listening, Thumbs Up, Warn).
    - [ ] Sync lip-sync with TTS audio (Text-to-Speech).

- [ ] **Task 3.2: Voice Interaction (STT/TTS)**
    - [ ] Integrate Speech-to-Text (Google/System).
    - [ ] Integrate Text-to-Speech (Vietnamese).
    - [ ] Implement "Wake Word" listener ("Bác sĩ ơi").

- [ ] **Task 3.3: Sign Language Detection**
    - [ ] Integrate MediaPipe Hands.
    - [ ] Train/Fine-tune model for basic VSL medical terms (Đau, Sốt, Bụng, Đầu...).
    - [ ] Real-time detection & mapping to Text.

- [ ] **Task 3.4: Touch Interface (Illiterate Mode)**
    - [ ] Design 3D/2D Body Map clickable.
    - [ ] Implement flow: Click Body Part -> Click Symptom Icon -> Click Duration.

---

## GIAI ĐOẠN 4: SOUL GARDEN & TESTING (Tuần 7-8)

- [ ] **Task 4.1: Soul Garden Logic**
    - [ ] Create UI for Daily Journal (Gamified).
    - [ ] Implement Tree Growth logic based on Journal entries.
    - [ ] Implement "Context Awareness" engine to feed data to Local LLM.

- [ ] **Task 4.2: Integration Testing**
    - [ ] Test E2E flow: Voice Input -> Cloud Processing -> Local Rewrite -> Avatar Output.
    - [ ] Test Offline mode scenarios.

- [ ] **Task 4.3: User Acceptance Testing (UAT)**
    - [ ] Test with elderly users (UI size, clarity).
    - [ ] Test with deaf/mute users (Sign language accuracy).

- [ ] **Task 4.4: Care Connect Module (Family)**
    - [ ] Implement `FamilyConnection` API (Link relative to patient).
    - [ ] Create Read-only Dashboard for relatives (Status, Meds, Mood).
    - [ ] Implement Alert System (Push Notification on critical triage result).

---

> **Lưu ý:** Các task trên là ước lượng cho MVP. Cần ưu tiên Core AI & Accessibility trước.

---

## GIAI ĐOẠN 5: MEDISIGN LITE & OFFLINE (Tuần 9-10)

- [ ] **Task 5.1: MediSign Lite – SMS Gateway**
    - [ ] Setup SMS Gateway (Twilio / VNPT SMS API).
    - [ ] Implement `POST /api/v1/lite/sms` webhook endpoint.
    - [ ] Implement Gemini prompt for SMS-length responses (≤160 chars).
    - [ ] Test E2E: SMS gửi → Server xử lý → SMS trả về.

- [ ] **Task 5.2: MediSign Lite – Voicebot (IVR)**
    - [ ] Setup IVR system (Asterisk / Twilio Voice).
    - [ ] Implement Decision Tree voice flow ("Nhấn 1: đau đầu, 2: đau bụng...").
    - [ ] Implement TTS response in Vietnamese.

- [ ] **Task 5.3: Offline Fallback**
    - [ ] Build Decision Tree JSON (~200-500 luồng triệu chứng).
    - [ ] Bundle Medicine DB offline (~25MB) into app.
    - [ ] Implement Offline Triage UI (touch-only, no AI).
    - [ ] Implement network change listener → auto-switch mode.

---

## GIAI ĐOẠN 6: SELF-HOSTED SERVER & FINE-TUNING (Sau MVP)

### 6.1 Chiến Lược Đạt 85%+ Accuracy

> **Mục tiêu:** Đạt accuracy ≥85% trên benchmark MedQuAD bằng Hybrid Engine

```
┌─────────────────────────────────────────────────────────────────────┐
│  HYBRID ENGINE ARCHITECTURE                                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Layer 1: LLM (Qwen 72B + Medical LoRA)                         │
│  ├── Fine-tune với MedQuAD + ChatDoctor                          │
│  └── Ngôn ngữ tự nhiên, hiểu tiếng Việt                        │
│                                                                     │
│  Layer 2: RAG (Retrieval-Augmented Generation)                   │
│  ├── Medical Knowledge Base (10,000+ facts)                       │
│  ├── Vector DB (FAISS)                                            │
│  └── Grounding → Giảm hallucination                               │
│                                                                     │
│  Layer 3: Symptom-Disease Logic Layer                            │
│  ├── 500+ diseases, 2000+ symptoms                                │
│  ├── Probability scoring                                          │
│  └── Red flag detection                                           │
│                                                                     │
│  Layer 4: Safety Layer                                           │
│  ├── Drug interaction check                                       │
│  ├── Disclaimer enforcement                                       │
│  └── Human-in-the-loop for critical cases                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

- [ ] **Task 6.1: LoRA Fine-tuning – Dual Adapter**
    - [ ] Thu thập dataset: MedQuAD (47K) + ChatDoctor (100K) + tự tạo VN (5-10K).
    - [ ] Dịch dataset sang tiếng Việt bằng Gemini API.
    - [ ] Fine-tune Adapter #1 (MediSign-Med): Gemma 2B + dataset y tế → Google Colab.
    - [ ] Fine-tune Qwen 72B + Medical LoRA (server A100).
    - [ ] Implement Adapter #2 (MediSign-Personal): on-device training từ Soul Garden + chat history.
    - [ ] Implement LoRA adapter swap mechanism (~100-200ms) trong MediaPipe.
    - [ ] Export adapters → tích hợp vào app.

- [ ] **Task 6.2: MediSign-Server Setup**
    - [ ] Thuê GPU server (Vast.ai / RunPod: 1x A100 80GB).
    - [ ] Deploy Qwen 2.5 72B (4-bit quantized) bằng vLLM / TGI.
    - [ ] Setup FastAPI wrapper + Load Balancer.
    - [ ] LoRA fine-tune Qwen 72B với dataset y tế VN → MediSign-Qwen.

- [ ] **Task 6.3: RAG Implementation**
    - [ ] Xây dựng Medical Knowledge Base (10,000+ medical facts).
    - [ ] Setup Vector DB (FAISS/Chroma).
    - [ ] Implement retrieval pipeline.
    - [ ] Integrate RAG với LLM generation.
    - [ ] Đo lường accuracy improvement.

- [ ] **Task 6.4: Symptom-Disease Logic Layer**
    - [ ] Xây dựng Symptom-Disease DB (500+ diseases, 2000+ symptoms).
    - [ ] Implement probability scoring algorithm.
    - [ ] Implement red flag detection (đau ngực, khó thở, chảy máu...).
    - [ ] Drug interaction check.
    - [ ] Integrate với LLM response pipeline.

- [ ] **Task 6.5: Evaluation & Benchmarking**
    - [ ] Tạo test set từ MedQuAD (10% = 4,700 questions).
    - [ ] Implement evaluation script (Accuracy, F1, ROUGE).
    - [ ] Đo lường baseline (Qwen 72B không fine-tune).
    - [ ] Đo lường sau fine-tune.
    - [ ] Đo lường sau RAG.
    - [ ] Đo lường sau Logic Layer.
    - [ ] So sánh với benchmark (Med-PaLM 2: 86%, MedAlpaca: 72%).

- [ ] **Task 6.6: Migration từ Gemini → Self-hosted**
    - [ ] Chuyển app từ Gemini Flash API sang MediSign-Server API.
    - [ ] Giữ Gemini Flash làm fallback khi server quá tải.
    - [ ] Monitoring & auto-scaling.

- [ ] **Task 6.7: AI Memory Backup & Data Recovery**
    - [ ] Implement Encrypted Cloud Backup (AES-256 + Recovery Key 12 từ).
    - [ ] Implement P2P Transfer (WiFi Direct / Bluetooth) giữa 2 thiết bị.
    - [ ] Implement Adapter Personal backup (mã hóa) tự động mỗi tuần lên cloud.
    - [ ] Implement AI Memory Recovery: tải adapter → AI "nhớ lại" → tái tạo bối cảnh.
    - [ ] UI cảnh báo onboarding: "Bật backup mã hóa? Dữ liệu sẽ mất nếu không backup."

### 6.2 Accuracy Targets

| Phase | Method | Expected Accuracy |
|-------|--------|-------------------|
| Baseline | Qwen 72B (no fine-tune) | 55-65% |
| Phase 1 | Fine-tune + LoRA | 70-80% |
| Phase 2 | + RAG | 80-85% |
| Phase 3 | + Logic Layer | **85%+** |

### 6.3 Expected Timeline

| Task | Thời gian | Output |
|------|-----------|--------|
| Data preparation | 1 tuần | train.json, eval.json |
| Fine-tune Qwen 72B | 1-2 tuần | Medical Adapter |
| RAG Implementation | 1 tuần | Vector DB + retrieval |
| Logic Layer | 1 tuần | Symptom-Disease DB |
| Evaluation | 1 tuần | Accuracy report |

**Tổng:** 5-6 tuần để đạt 85%+ accuracy
