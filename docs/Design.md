# MediSign AI – Tài liệu Thiết kế Hệ thống (System Design)

> **Phiên bản:** 1.0 | **Dựa trên:** Required.md v1.0

---

## 1. KIẾN TRÚC HỆ THỐNG (SYSTEM ARCHITECTURE)

Hệ thống sử dụng kiến trúc **Hybrid Local-Cloud** để đảm bảo tính riêng tư và khả năng truy cập offline.

### 1.1 Sơ đồ khối (High-Level Diagram)

```mermaid
graph TD
    User[Người dùng] --> MobileApp[Mobile App (Flutter)]
    
    subgraph "Mobile Device (Local)"
        MobileApp --> LocalLLM[Local LLM (MediSign-Tiny)]
        MobileApp --> SoulDB[(Soul Garden DB - SQLite/Realm)]
        MobileApp --> OCR[OCR Engine (Tesseract/MLKit)]
        MobileApp --> OfflineMedDB[(Medicine DB Offline)]
        LocalLLM <--> SoulDB
    end
    
    subgraph "Cloud Server (Secure & Anonymous)"
        MobileApp -- "Encrypted & Anonymous Data" --> APIGateway[API Gateway (FastAPI)]
        APIGateway --> CloudLLM[Cloud LLM Service (Gemini Pro)]
        APIGateway --> MedService[Medicine Service]
        APIGateway --> HospitalService[Hospital Service]
        
        MedService --> MedDB[(Central Medicine DB)]
        HospitalService --> HospitalDB[(Hospital & Map DB)]
    end
```

### 1.2 Phân tích các thành phần

| Thành phần | Công nghệ | Chức năng chính |
|---|---|---|
| **Mobile App** | Flutter | Giao diện đa phương thức (Touch, Voice, Sign, Text). Xử lý logic hiển thị 3D Avatar. |
| **Local LLM** | TensorFlow Lite / MediaPipe LLM | Xử lý ngôn ngữ tự nhiên offline. **Tự trả lời** câu hỏi cơ bản (Local-Only mode) hoặc viết lại câu trả lời Cloud cho cá nhân hóa (Hybrid mode). |
| **Soul DB** | SQLite (Encrypted) | Lưu trữ nhật ký, hồ sơ sức khỏe, thói quen. Dữ liệu KHÔNG BAO GIỜ rời khỏi thiết bị ở chế độ Local-only. |
| **Cloud LLM** | Google Gemini API | Xử lý các câu hỏi y tế phức tạp, phân tích triệu chứng sâu. |
| **Medicine Service** | Python/FastAPI | Tra cứu thuốc, kiểm tra tương tác thuốc từ Cục Dược VN data. |
| **SMS Gateway** | Twilio / VNPT SMS API | Nhận và gửi SMS cho MediSign Lite (vùng sâu vùng xa). |
| **Voicebot IVR** | Asterisk / Twilio Voice | Tiếp nhận cuộc gọi, hướng dẫn bằng giọng nói cho MediSign Lite. |

### 1.3 Chiến lược Phân tầng Thiết bị (Device Tiering)

Để đảm bảo khả năng chạy trên máy yếu (Low-end Android):

1. **High-end Device:**
    - Run `MediSign-Tiny` (Gemma 2B int4) in background.
    - Full Offline Capabilities (Chat & Triage).

2. **Low-end Device:**
    - **Disable Local LLM**.
    - Use Cloud API for all logic.
    - Offline Mode chỉ hỗ trợ tra cứu thuốc (Hard-coded DB lookup), không có AI chat.

### 1.4 Chiến lược AI – RAG + LoRA + Self-hosted

**Kiến trúc RAG (Retrieval-Augmented Generation):**

```
User Input → NLP Parse → Query Local DB (thuốc/bệnh)
                              ↓
                     DB trả về dữ liệu chính xác
                              ↓
                     Inject vào LLM Prompt
                              ↓
                     LLM viết câu trả lời tự nhiên
```

**Lộ trình AI Model:**

| Phase | Cloud AI | Local AI | Chi phí Cloud |
|---|---|---|---|
| MVP | Gemini Flash Free Tier + RAG | Gemma 2B gốc + Prompt + RAG | ~$0 |
| Growth | Gemini Flash trả phí + RAG | MediSign-Gemma (LoRA) | ~$30-100/tháng |
| Scale | **MediSign-Server** (Self-hosted Qwen 72B + LoRA y tế VN) | MediSign-Gemma tối ưu | ~$300/tháng cố định |

**Self-hosted Server Architecture (Scale Phase):**

```
User → Load Balancer → MediSign-Server (Qwen 72B + LoRA) → RAG (DB thuốc/bệnh) → Response
                    └→ Gemini Flash API (fallback khi quá tải)
```

- **Infrastructure:** 1x A100 80GB (Vast.ai / RunPod, ~$150-400/tháng)
- **Model:** Qwen2.5-VL-72B (4-bit quantized, 40GB VRAM) + LoRA adapter y tế VN
  - **Vision Capability:** Đọc ảnh thuốc → Extract tên thuốc → Đối chiếu JSON data → Đưa ra kết luận
- **Lợi ích:** 0 đồng/câu hỏi, toàn quyền dữ liệu, không phụ thuộc bên thứ 3

**Nguồn dữ liệu fine-tune:** MedQuAD (47K), ChatDoctor (100K), tự tạo Q&A y tế VN (5-10K).

### 1.5 Scalability & High Availability

**Auto-scaling Architecture:**

```
Load Balancer (Nginx)
    ├── Server Pool A (Singapore) ─── Qwen 72B (chính)
    ├── Server Pool B (Japan)     ─── Qwen 72B (backup)
    └── Gemini Flash API          ─── Fallback cuối cùng
```

**Graceful Degradation:** Tải < 80% → Qwen 72B. Tải 80-95% → Chuyển câu đơn giản sang Qwen 7B. Tải > 95% → Bật Gemini Flash backup. Tải 100% → Request Queue + ưu tiên cấp cứu.

**Disaster Recovery (4 lớp):** Server backup → Gemini API → Local AI → Offline Fallback + Nút 115.

### 1.6 Dual LoRA Architecture

**Kiến trúc:** 1 Base Model (Gemma 2B) + 2 LoRA Adapters swap theo vai trò:

| Adapter | Vai trò | Train từ | Backup |
|---|---|---|---|
| **MediSign-Med** | Y tế, chẩn đoán, thuốc | Dataset y khoa (MedQuAD, ChatDoctor, Dược thư VN) | Không cần (tải lại được) |
| **MediSign-Personal** | Cá nhân hóa, viết lại câu trả lời | Soul Garden + Chat history (on-device) | ✅ Mã hóa lên cloud |

```
Luồng xử lý:
    User Input
        ↓
    [Adapter #1: Medical] → Câu trả lời y tế chuẩn
        ↓ swap (~100-200ms)
    [Adapter #2: Personal] → Viết lại phù hợp người dùng
        ↓
    Output cá nhân hóa

RAM total: ~1.65GB (base 1.5GB + adapters ~150MB)
```

**AI Memory Backup:** Adapter Personal được backup mã hóa (AES-256) lên cloud mỗi tuần. Khi mất máy → tải adapter + nhập Recovery Key (12 từ) → AI "nhớ lại" thói quen, bệnh nền, phong cách. Tái tạo ~30-50% bối cảnh nhật ký.

**2 tầng backup:** Tầng 1 = Encrypted DB Backup (100% chính xác). Tầng 2 = AI Memory (30-50%, backup phụ).

---

## 2. CƠ SỞ DỮ LIỆU (DATABASE SCHEMA)

### 2.1 Soul Garden (Local SQLite)

Chỉ lưu trên thiết bị người dùng.

```sql
-- Nhật ký người dùng
CREATE TABLE DailyJournal (
    id TEXT PRIMARY KEY,
    date DATE NOT NULL,
    mood INTEGER, -- 1: Rất tệ, 5: Rất tốt
    content TEXT, -- Text hoặc voice-to-text
    tags TEXT, -- JSON: ["stress", "mất ngủ", "quên"]
    ai_analysis TEXT -- Kết quả phân tích tâm lý từ Local LLM
);

-- Hồ sơ sức khỏe cá nhân
CREATE TABLE UserProfile (
    id TEXT PRIMARY KEY,
    name TEXT,
    yob INTEGER,
    gender TEXT,
    medical_history TEXT, -- Tiền sử bệnh
    allergies TEXT, -- Dị ứng
    disability_type TEXT -- "DEAF", "BLIND", "ELDERLY", "NONE"
);

-- Tủ thuốc cá nhân
CREATE TABLE MyMedicine (
    id TEXT PRIMARY KEY,
    name TEXT,
    dosage TEXT,
    schedule TEXT, -- JSON: {"times": ["08:00", "20:00"]}
    remaining_pills INTEGER
);
```

### 2.2 Cloud Database (PostgreSQL - Ẩn danh)

Lưu trữ dữ liệu dùng chung (thuốc, bệnh viện) và log ẩn danh.

```sql
-- Danh mục thuốc (Dữ liệu công khai)
CREATE TABLE MedicineRegistry (
    reg_number TEXT PRIMARY KEY, -- Số đăng ký (VD: VD-1234-22)
    name TEXT NOT NULL,
    active_ingredient TEXT,
    dosage_form TEXT,
    contraindications TEXT, -- Chống chỉ định
    interactions TEXT -- JSON: danh sách thuốc tương tác
);

-- Mạng lưới y tế
CREATE TABLE Hospitals (
    id SERIAL PRIMARY KEY,
    name TEXT,
    address TEXT,
    coordinates GEOMETRY(Point),
    specialties TEXT[], -- ["Tiêu hóa", "Tim mạch"]
    accepts_bhyt BOOLEAN
);

-- Kết nối Gia đình (Care Connect)
CREATE TABLE FamilyConnection (
    id SERIAL PRIMARY KEY,
    patient_id TEXT, -- User chính
    relative_id TEXT, -- Người thân
    permissions TEXT, -- JSON: ["view_medication", "receive_alerts", "view_mood"]
    status TEXT -- "PENDING", "ACTIVE"
);
```

---

## 3. API SPECIFICATIONS (FastAPI)

### 3.1 AI Consultation

`POST /api/v1/consult/triage`

- **Input:**

  ```json
  {
    "symptoms": "đau bụng dưới bên phải, sốt nhẹ",
    "duration": "2 ngày",
    "age": 35,
    "gender": "male"
    // KHÔNG gửi tên, KHÔNG gửi nhật ký
  }
  ```

- **Output:**

  ```json
  {
    "triage_level": "YELLOW", // Cần đi khám
    "advice": "Có khả năng viêm ruột thừa...",
    "recommended_specialty": "Tiêu hóa"
  }
  ```

### 3.2 Medicine Scanner

`POST /api/v1/medicine/scan`

- **Input:** Upload ảnh vỉ thuốc (Multipart)
- **Output:**

  ```json
  {
    "name": "Hapacol 650",
    "active_ingredient": "Paracetamol 650mg",
    "warnings": ["Không dùng quá 4 viên/ngày", "Hại gan nếu uống rượu"]
  }
  ```

### 3.3 Care Connect (Family)

`GET /api/v1/care/dashboard/{patient_id}`

- **Auth:** Require `relative_jwt_token`
- **Output:**

  ```json
  {
    "patient_status": "NORMAL", // or "ALERT"
    "last_checkin": "2023-10-27T08:00:00Z",
    "medication_today": {
      "taken": ["Hapacol"],
      "missed": []
    },
    "mood_summary": "Vui vẻ"
  }
  ```

### 3.4 MediSign Lite (SMS/Call)

`POST /api/v1/lite/sms` (Webhook từ SMS Gateway)

- **Input:**

  ```json
  {
    "from": "+84912345678",
    "body": "Tôi bị đau bụng, sốt 2 ngày"
  }
  ```

- **Output:** SMS trả về cho người dùng (qua SMS Gateway)

  ```
  MediSign: Đau bụng + sốt 2 ngày có thể nghiêm trọng.
  Hãy đến trạm y tế gần nhất. Gọi 115 nếu đau dữ dội.
  ```

---

## 4. UI/UX FLOWS (ĐA PHƯƠNG THỨC)

### 4.1 Flow Chính: Hỏi bệnh (Triage)

1. **Home Screen**:
    - Nút to "Bác sĩ ơi" (giữa)
    - Nút "Quét thuốc" (trái)
    - Nút "Nhật ký" (phải)
    - Avatar Y tá 3D (góc dưới)

2. **Input Screen (Đa phương thức)**:
    - **Voice**: "Tôi bị đau đầu" (Waveform hiển thị)
    - **Touch**: Hình cơ thể người → Chạm vào Đầu
    - **Sign**: Camera mở → User ra ký hiệu → App hiện text nhận diện real-time

3. **Result Screen**:
    - **Text**: Lời khuyên ngắn gọn
    - **Visual**: Icon mức độ nguy hiểm (Xanh/Vàng/Đỏ)
    - **Action**: Nút "Tìm BV gần nhất" hoặc "Gọi người thân"

### 4.2 Accessibility Modes

- **Mode Người Mù Chữ / Điếc**:
  - Ẩn toàn bộ text nhỏ.
  - Chỉ dùng Icon to + Hình ảnh minh họa.
  - Y tá 3D dùng ngôn ngữ ký hiệu cho mọi thông báo.

- **Mode Người Già**:
  - Font size 30px.
  - Độ tương phản cao (Đen/Vàng hoặc Trắng/Đen).
  - Auto-read (đọc to) mọi thứ xuất hiện trên màn hình.

---

## 5. BẢO MẬT & QUYỀN RIÊNG TƯ (IMPLEMENTATION)

### 5.1 Mã hóa Dữ liệu Cục bộ (Data at Rest)

Tất cả dữ liệu trên điện thoại đều được mã hóa, kể cả khi thiết bị bị mất hoặc bị root:

| Thành phần | Thuật toán | Cơ chế | Ghi chú |
|---|---|---|---|
| **Soul Garden DB** | AES-256-CBC (SQLCipher) | Toàn bộ database mã hóa | Không đọc được nếu không có key |
| **Medicine DB offline** | AES-256 | File-level encryption | Giải mã khi cần tra cứu |
| **LoRA model cache** | Không mã hóa | Model chung, không chứa PII | Công khai, không nhạy cảm |
| **Key lưu trữ** | RSA-2048 / ECDSA | Android Keystore / iOS Keychain | Key KHÔNG BAO GIỜ rời khỏi hardware |
| **Ảnh thuốc (OCR)** | AES-256 | Mã hóa tạm → xử lý OCR → XÓA NGAY | Không lưu ảnh vĩnh viễn |

```
Luồng mã hóa cục bộ:
    App khởi động
        ↓
    Kiểm tra Encryption Key trong Keystore
        ├── Có key → Giải mã DB → Sẵn sàng
        └── Chưa có (lần đầu) → Sinh key ngẫu nhiên → Lưu Keystore
        
    Khi ghi dữ liệu:
        Data → SQLCipher tự mã hóa (AES-256) → Lưu file .db
    
    Khi đọc dữ liệu:
        File .db → SQLCipher giải mã bằng key từ Keystore → Hiển thị
```

### 5.2 Mã hóa Dữ liệu Truyền đi (Data in Transit)

Mọi dữ liệu gửi từ app lên server đều được mã hóa **2 lớp**:

| Lớp | Công nghệ | Bảo vệ khỏi | Ghi chú |
|---|---|---|---|
| **Lớp 1: TLS 1.3** | HTTPS + TLS 1.3 | Man-in-the-Middle (MITM), ISP sniffing | Tiêu chuẩn mọi app |
| **Lớp 2: Certificate Pinning** | Pin SHA-256 fingerprint | Fake certificate, proxy attack | Chống hack WiFi công cộng |
| **Lớp 3 (nhạy cảm): E2E Encryption** | AES-256-GCM + RSA-2048 | Server admin cũng không đọc được | Chỉ cho Soul Garden sync (nếu có) |

```
Luồng truyền dữ liệu (Hybrid/Cloud mode):

App → [Anonymization Layer] → [TLS 1.3 + Cert Pinning] → Server
         ↓
    1. Strip PII (tên, SĐT, email, địa chỉ)
    2. Generalize (tuổi 27 → "25-30", GPS → "Quận/Huyện")
    3. Session ID tạm (reset mỗi phiên)
         ↓
    Server CHỈ nhận: "Nam, 25-30 tuổi, đau bụng phải, sốt nhẹ, 2 ngày"
    Server KHÔNG biết: ai gửi, ở đâu, số điện thoại bao nhiêu
```

### 5.3 Cơ chế Ẩn danh Chi tiết (Anonymization Pipeline)

```
Dữ liệu gốc (trên điện thoại):
{
    "name": "Nguyễn Văn A",          ← STRIP
    "phone": "0912345678",            ← STRIP
    "age": 27,                        ← GENERALIZE → "25-30"
    "address": "123 Lê Lợi, Q1",     ← STRIP
    "gps": [10.762, 106.660],         ← GENERALIZE → "Quận 1"
    "symptoms": "đau bụng phải",      ← GIỮ NGUYÊN
    "medications": ["Warfarin"],      ← GIỮ NGUYÊN
    "soul_garden": "Hôm nay stress"   ← KHÔNG BAO GIỜ gửi lên
}

Dữ liệu gửi lên server:
{
    "session_id": "tmp_a8f2k9",       ← ID tạm, tự hủy
    "age_range": "25-30",
    "gender": "male",
    "district": "Quận 1",
    "symptoms": "đau bụng phải",
    "medications": ["Warfarin"]
}
```

### 5.4 Quản lý Key & Backup

| Tình huống | Xử lý |
|---|---|
| **Mất điện thoại** | Dữ liệu mã hóa → không ai đọc được |
| **Đổi điện thoại** | Chuyển qua Bluetooth/NFC (Local-Only) hoặc Cloud sync mã hóa E2E (Hybrid) |
| **Quên mật khẩu app** | Xác thực sinh trắc (vân tay/khuôn mặt) → khôi phục key từ Keystore |
| **App bị gỡ** | Keystore tự xóa key → dữ liệu .db trở thành rác không giải mã được |

### 5.5 P2P Transfer Protocol (Chuyển máy có kế hoạch)

> **Nguyên tắc:** Dữ liệu KHÔNG BAO GIỜ truyền dạng plaintext, kể cả khi 2 máy kề nhau. Mã hóa TRƯỚC khi truyền, giải mã SAU khi nhận đủ 100%.

**Giao thức truyền 6 bước:**

```
MÁY CŨ                                     MÁY MỚI
  │                                           │
  ├── Bước 1: Mở "Chuyển dữ liệu"            │
  │   Tạo QR Code (chứa session key)          │
  │           ──────── QR ────────→            ├── Bước 2: Quét QR
  │                                           │   Nhận session key
  │                                           │
  ├── Bước 3: Kết nối WiFi Direct / Bluetooth │
  │   ◄───── ECDH Key Exchange ─────►         │
  │   (Trao đổi khóa an toàn, chống MITM)     │
  │                                           │
  ├── Bước 4: Mã hóa + Truyền từng chunk      │
  │   Data → AES-256-GCM encrypt               │
  │   → Chia thành chunks 1MB                  │
  │   → Gửi chunk + SHA-256 hash ─────►       ├── Nhận chunk
  │                                           │   Verify hash ✓
  │   Chunk 1/50 ████░░░░░░░░ 2%              │   Chunk 1/50 ✓
  │   Chunk 2/50 ████████░░░░ 4%              │   Chunk 2/50 ✓
  │   ...                                     │   ...
  │   Chunk 50/50 ████████████ 100%           │   Chunk 50/50 ✓
  │                                           │
  │           ◄─── ACK "Nhận đủ" ─────        ├── Bước 5: Verify toàn bộ
  │                                           │   SHA-256 toàn file ✓
  │                                           │   Giải mã AES-256-GCM
  │                                           │   Import vào app ✓
  │                                           │
  ├── Bước 6: Xác nhận hoàn tất               │
  │   "Dữ liệu đã chuyển thành công.         │
  │    Xóa dữ liệu trên máy cũ?"             │
  │   [Xóa] [Giữ lại]                         │
  └───────────────────────────────────────────┘
```

**Đảm bảo 100% không mất dữ liệu:**

| Rủi ro | Bảo vệ | Cơ chế |
|---|---|---|
| Mất kết nối giữa chừng | **Chunk-based + Resume** | Nếu đứt → tiếp tục từ chunk cuối, không truyền lại từ đầu |
| Dữ liệu bị hỏng khi truyền | **SHA-256 per chunk** | Mỗi chunk có hash riêng, sai → truyền lại chunk đó |
| Dữ liệu bị thiếu | **SHA-256 toàn file** | Sau khi nhận đủ, verify hash toàn bộ file |
| Bị nghe lén (sniffing) | **AES-256-GCM** | Dữ liệu mã hóa hoàn toàn trong quá trình truyền |
| MITM attack | **ECDH + QR verification** | QR code xác nhận 2 máy đúng, key exchange an toàn |
| Máy cũ xóa trước khi máy mới nhận xong | **Không xóa tự động** | Chỉ hỏi xóa SAU KHI máy mới xác nhận 100% ✓ |

**Dữ liệu được truyền:**

| Dữ liệu | Kích thước | Ghi chú |
|---|---|---|
| Soul Garden DB (mã hóa) | ~5-50MB | Nhật ký, hồ sơ, tủ thuốc |
| Adapter Personal (LoRA) | ~50-100MB | AI Memory cá nhân |
| Encryption Key | ~256 bytes | Chuyển qua QR code |
| App settings | ~1KB | Chế độ, ngôn ngữ, accessibility |
| **Tổng** | **~60-150MB** | Truyền WiFi Direct: ~30-60 giây |

### 5.6 Bảo mật Tài khoản (Account Security)

**Đăng nhập 2 bước bắt buộc (MFA – Multi-Factor Authentication):**

```
BƯỚC 1: MẬT KHẨU (thứ bạn BIẾT)
    Email/SĐT + Mật khẩu
        ↓ Đúng

BƯỚC 2: XÁC THỰC DANH TÍNH (thứ bạn CÓ / thứ bạn LÀ)
    Chọn 1 trong 3:

    🔹 Sinh trắc học [Vân tay / FaceID]  ← KHUYÊN DÙNG
       → Gần như KHÔNG THỂ bị đánh cắp
       → Không cần SIM, không cần internet
       → Key nằm trong hardware (Keystore)

    🔹 OTP SMS + Authenticator (DÙNG CẢ 2 CÙNG LÚC)
       → Nhập mã OTP từ SMS + mã 6 số từ Authenticator
       → Mất SIM? → Vẫn có Authenticator
       → Mất tài khoản Google? → Vẫn có OTP SMS
       → Phải mất CẢ 2 mới bị hack → xác suất cực thấp

    🔹 Recovery Key (12 từ)  ← CHỈ KHẨN CẤP
       → Dùng khi mất cả SIM + Authenticator + điện thoại
       → "xoài biển trăng sách cá voi bầu trời hoa sen gió mây"
       → Ghi ra giấy / nhờ người thân giữ

        ↓ Xác thực thành công
    ĐĂNG NHẬP THÀNH CÔNG ✅
```

**So sánh mức bảo mật các phương thức Bước 2:**

| Kịch bản tấn công | MK + OTP | MK + Auth | MK + OTP+Auth | MK + Sinh trắc |
|---|---|---|---|---|
| Hacker biết mật khẩu | ⚠️ Cần thêm SIM | ⚠️ Cần thêm ĐT | ⚠️ Cần cả 2 | ✅ **AN TOÀN** |
| Bị mất SIM | ❌ Nguy hiểm | ✅ An toàn | ✅ An toàn | ✅ An toàn |
| Bị mất tài khoản Google | ✅ An toàn | ❌ Mất Auth | ✅ An toàn | ✅ An toàn |
| Bị mất cả SIM + Google | ❌ Kẹt | ❌ Kẹt | ❌ Kẹt | ✅ **VẪN AN TOÀN** |
| Bị cướp vân tay (cực hiếm) | – | – | – | ⚠️ Rủi ro lý thuyết |

> **Sinh trắc = "khóa không thể sao chép"** → kẻ trộm không thể lấy vân tay/khuôn mặt từ xa.
> **OTP + Auth = "khóa kép"** → phải phá 2 hệ thống khác nhau cùng lúc.

**Mã hóa mật khẩu (bcrypt):**

```
User nhập: "MyPassword123"
    ↓ Thêm Salt (ngẫu nhiên): + "x9k2m..."
    ↓ Hash bcrypt (12 rounds): "$2b$12$LJ3..."
    ↓ Lưu DB: { hash: "$2b$12$LJ3...", salt: "x9k2m..." }
→ Hacker lấy DB → KHÔNG giải ngược được
```

**Thiết lập TOTP Authenticator (1 lần):**

```
Cài đặt → Bảo mật → Bật Authenticator
    ↓
App tạo TOTP Secret Key → Hiện QR Code
    ↓
User quét QR bằng Google Authenticator / Authy
    ↓
Nhập mã 6 số xác nhận → Authenticator được bật ✓
→ Mã đổi mỗi 30 giây, chỉ hiện trên điện thoại user
```

**Khôi phục khi mất điện thoại:**

| Phương pháp | Cách dùng |
|---|---|
| **Recovery Codes** | 8 mã dùng 1 lần, hiện khi bật 2FA → ghi ra giấy |
| **Recovery Key (12 từ)** | Dùng chung với AI Memory Recovery |
| **Email khôi phục** | Gửi link reset 2FA qua email đã xác thực (cần 24h chờ) |

**Chống tấn công:**

| Tấn công | Bảo vệ |
|---|---|
| Brute-force mật khẩu | 5 lần sai → khóa 15 phút. 10 lần → khóa 24h |
| Token bị đánh cắp | Access Token hết hạn 15 phút + kiểm tra IP |
| SIM swap (cướp SĐT) | OTP + cần xác nhận email hoặc Recovery Key |
| Session hijacking | HTTPS only + HttpOnly + Secure cookie flags |
| Replay attack | Nonce + Timestamp mỗi request |

**Quản lý thiết bị:**

```
Hybrid/Cloud mode:
    ├── Xem danh sách thiết bị đang đăng nhập
    ├── "Đăng xuất tất cả" (khi mất máy)
    ├── Cảnh báo đăng nhập lạ (IP/vị trí mới)
    └── Tối đa 3 thiết bị đồng thời

Local-Only mode:
    ├── CHỈ 1 thiết bị duy nhất
    ├── Mật khẩu hash lưu trong Keystore
    ├── Sinh trắc là đăng nhập chính
    └── Recovery qua Recovery Key (12 từ)
```

---

## 6. CÔNG NGHỆ CHI TIẾT

| Hạng mục | Công nghệ lựa chọn | Lý do |
|---|---|---|
| **Frontend** | **Flutter** | Cross-platform, performance tốt cho 3D & Animation (Y tá ảo). |
| **3D Avatar** | **Rive / Unity as Library** | Nhẹ, tương tác reactive tốt trên mobile. |
| **Backend** | **Python (FastAPI)** | Dễ tích hợp AI libraries, tốc độ cao (async). |
| **AI LLM** | **Gemini Flash (Cloud) + Gemma 2B (Local)** | Gemini Flash rẻ & nhanh. Gemma 2B đủ nhỏ để chạy trên mobile (qua MediaPipe). |
| **OCR** | **Google ML Kit** | Offline on-device, nhận diện text latinh cực tốt và miễn phí. |
| **Pose Estimation** | **MediaPipe Pose (BlazePose)** | Free, offline, 33 keypoints, real-time. |
| **Database** | **PostgreSQL (Cloud) + SQLite (Local)** | Tiêu chuẩn công nghiệp. |

---

## 7. MODULE 6: AI FITNESS COACH

### 7.1 Mô tả tính năng

AI Fitness Coach là module hỗ trợ tập luyện với khả năng:

- **Nhận diện tư thế real-time** qua camera
- **Phát hiện sai lệch** so với tư thế chuẩn
- **Feedback ngay lập tức** bằng text/voice
- **Theo dõi tiến độ** và lịch sử tập luyện

> **Lưu ý pháp lý:** AI chỉ mang tính **tham khảo và hỗ trợ**, KHÔNG thay thế huấn luyện viên chuyên nghiệp. Luôn hiển thị disclaimer rõ ràng.

### 7.2 User Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. HOME                                                   │
│     [Tập thể dục] button                                   │
│                    ↓                                        │
│  2. SELECT GOAL                                            │
│     ┌──────────┬──────────┬──────────┐                     │
│     │ Giảm cân  │ Tăng cơ  │ Duy trì  │                     │
│     └──────────┴──────────┴──────────┘                     │
│                    ↓                                        │
│  3. SELECT EXERCISE                                        │
│     ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐                     │
│     │Squat│ │Push│ │Plank│ │Lunge│ │Dead│                   │
│     │    │ │-up │ │    │ │    │ │lift│                     │
│     └────┘ └────┘ └────┘ └────┘ └────┘                     │
│     [Xem video hướng dẫn]                                  │
│                    ↓                                        │
│  4. WORKOUT SESSION                                        │
│     ┌─────────────────────────────┐                         │
│     │    Camera Preview (front)   │                         │
│     │    ┌───────────────┐        │                         │
│     │    │   Skeleton    │        │                         │
│     │    │   Overlay     │        │                         │
│     │    └───────────────┘        │                         │
│     │                             │                         │
│     │   "Knee angle: 95°         │                         │
│     │    → Xuống thêm một chút!" │                         │
│     │                             │                         │
│     │   Rep: 5/12   ⏱ 00:45      │                         │
│     └─────────────────────────────┘                         │
│                    ↓                                        │
│  5. SUMMARY                                                │
│     - Reps hoàn thành                                      │
│     - Form score (0-100%)                                  │
│     - Gợi ý cải thiện                                      │
└─────────────────────────────────────────────────────────────┘
```

### 7.3 Exercise Library (MVP)

| # | Bài tập | Target | Keypoints check |
|---|---------|--------|-----------------|
| 1 | Squat | Lower body | Knee angle, hip angle, back angle |
| 2 | Push-up | Upper body (chest) | Elbow angle, body alignment |
| 3 | Plank | Core | Body line (shoulder-hip-ankle) |
| 4 | Lunge | Lower body | Front knee angle, back knee position |
| 5 | Deadlift | Lower back, hamstring | Back angle, hip hinge |

### 7.4 Angle Reference (Pre-defined)

```python
# MVP: Predefined ideal angles (dựa trên sports science)
EXERCISE_REFERENCES = {
    "squat": {
        "description": "Hạ người xuống, đùi song song sàn",
        "ideal_angles": {
            "knee": (85, 95),      # degrees - đùi song song
            "hip": (70, 90),       # hip flexion
            "back": (30, 60),      # forward lean
        },
        "common_mistakes": [
            "knee_valgus": "Đầu gối hướng vào trong",
            "heel_rise": "Gót chân nhấc lên",
            "lumbar_flexion": "Lưng quá cong",
        ]
    },
    "pushup": {
        "description": "Hạ người xuống, khuỷu tay 90°",
        "ideal_angles": {
            "elbow": (80, 100),    # 90 độ là lý tưởng
            "body": (170, 180),    # body straight line
        },
        "common_mistakes": [
            "flared_elbows": "Khuỷu tay bay ra ngoài quá xa",
            "sagging_hip": "Mông hạ thấp",
            "piked_hip": "Mông cao quá",
        ]
    },
    "plank": {
        "description": "Giữ body thẳng như một đường thẳng",
        "ideal_angles": {
            "shoulder_hip": (170, 180),  # nearly straight
            "hip_ankle": (170, 180),
        },
        "common_mistakes": [
            "sagging_hip": "Mông hạ xuống (common)",
            "piked_hip": "Mông cao lên",
            "head_up": "Đầu ngước lên",
        ]
    },
    "lunge": {
        "description": "Bước một chân ra, hạ đùi song song sàn",
        "ideal_angles": {
            "front_knee": (85, 95),
            "back_knee": (80, 100),   # nearly floor
        },
        "common_mistakes": [
            "front_heel_up": "Gót chân trước nhấc",
            "narrow_stance": "Chân quá hẹp",
            "torso_forward": "Thân người nghiêng quá",
        ]
    },
    "deadlift": {
        "description": "Nhấc tạ từ sàn, giữ lưng thẳng",
        "ideal_angles": {
            "hip": (45, 70),         # hip hinge
            "knee": (130, 160),      # slight bend
            "back": (0, 15),         # nearly flat (neutral spine)
        },
        "common_mistakes": [
            "rounded_back": "Lưng tròn (NGUY HIỂM)",
            "squatting": "Ngồi xổm thay vì hip hinge",
            "hyperextension": "Quá arch lưng",
        ]
    }
}
```

### 7.5 Real-time Processing Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMERA FRAME (30fps)                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  MEDIA PIPE POSE (BlazePose)                               │
│  - Extract 33 keypoints                                    │
│  - Body part: x, y, z (confidence)                        │
│  - Processing time: <20ms/frame                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  ANGLE CALCULATION                                         │
│  - Calculate joint angles using vector math               │
│  - knee_angle = angle(A_hip, B_knee, C_ankle)            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  MISTAKE DETECTION                                         │
│  - Compare current vs ideal angles                        │
│  - Detect common mistakes from lookup table               │
│  - Threshold: ±15° = "cần cải thiện"                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  FEEDBACK GENERATION                                       │
│  - Text: "Đầu gối hướng vào trong - nên hướng ra ngoài"  │
│  - Voice: Text-to-speech feedback                         │
│  - Visual: Color-coded skeleton (green=good, red=bad)     │
└─────────────────────────────────────────────────────────────┘
```

### 7.6 Data Models

```python
# Flutter/Dart models
class Exercise {
  final String id;
  final String name;
  final String description;
  final String targetArea; // "lower_body", "upper_body", "core"
  final List<String> muscleGroups;
  final ExerciseReference reference;
}

class ExerciseReference {
  final Map<String, (double, double)> idealAngles; // "knee": (85, 95)
  final List<String> commonMistakes;
}

class WorkoutSession {
  final String id;
  final String exerciseId;
  final DateTime startTime;
  final DateTime? endTime;
  final int totalReps;
  final int goodReps;
  final double formScore; // 0-100
  final List<RepData> repHistory;
}

class RepData {
  final int repNumber;
  final double minAngle;
  final double maxAngle;
  final bool isGoodForm;
  final List<String> mistakes;
}
```

### 7.7 Công nghệ Implementation

| Thành phần | Công nghệ | Chi tiết |
|------------|-----------|----------|
| **Pose Detection** | MediaPipe Pose | 33 keypoints, 30fps, offline |
| **Camera** | camera package (Flutter) | Front camera, 720p |
| **Angle Math** | vector_math | Tính góc giữa 3 điểm |
| **Voice Feedback** | flutter_tts | Text-to-speech cho audio cue |
| **Storage** | SQLite (local) | Lưu workout history |
| **Visualization** | Custom Painter | Vẽ skeleton overlay |

### 7.8 Scoring System

```
Form Score = (Good Reps / Total Reps) × 100

Rep classification:
├── ✅ Good Form: Tất cả angles trong ±10° của ideal
├── ⚠️  Okay Form: Tất cả angles trong ±15° của ideal
└── ❌ Bad Form: Ít nhất 1 angle >±15° từ ideal

Feedback thresholds:
├── Score > 80%: "Tuyệt vời! Form tốt lắm!"
├── Score 60-80%: "Khá tốt, cần cải thiện..."
└── Score < 60%: "Cần chú ý form hơn, dễ bị chấn thương"
```

### 7.9 Privacy & Legal

| Yếu tố | Xử lý |
|--------|-------|
| **Video data** | Xử lý local, KHÔNG upload lên cloud |
| **User consent** | Hiển thị consent trước khi quay |
| **Disclaimer** | "AI chỉ mang tính tham khảo, KHÔNG thay thế PT" |
| **Liability** | User tự chịu trách nhiệm an toàn |
| **No medical claim** | Không dùng từ "chẩn đoán", "điều trị" |

### 7.10 Offline Capability

```
┌─────────────────────────────────────────┐
│         FULLY OFFLINE                    │
│                                         │
│  MediaPipe Pose    → Downloaded model  │
│  Angle calculation → Local math        │
│  Exercise DB       → Hardcoded JSON   │
│  Workout history   → Local SQLite     │
│                                         │
│  → Không cần internet khi tập          │
└─────────────────────────────────────────┘
```

---

## 8. Module 7: 3D Doctor Hub (Talking Tom Style)

### 8.1 Tổng quan

Màn hình tương tác 3D — bác sĩ AI đứng giữa màn hình, xung quanh là các nút điều hướng.
Lấy cảm hứng từ game Talking Tom: nhân vật hoạt hình ở trung tâm, phản hồi khi chạm,
nhại giọng nói, và hỗ trợ ngôn ngữ ký hiệu cho người khuyết tật.

**Đối tượng chính:** Trẻ em, người khuyết tật (câm/điếc), người lớn tuổi ít quen công nghệ.

### 8.2 Layout

```
┌────────────────────────────────┐
│  ← Bác sĩ AI          ⚙️     │  ← App bar
├────────────────────────────────┤
│  ┌──────────────────────────┐  │
│  │ 💬 "Xin chào! Tôi là    │  │  ← Speech bubble
│  │    bác sĩ AI..."         │  │
│  └──────────────────────────┘  │
│                                │
│       🩺(Hỏi bệnh)            │
│                                │
│  💊(Quét)  ┌──────┐  🏋️(Tập)  │
│            │ 🩺   │           │  ← 3D Model center
│            │Doctor │           │
│  🌱(Vườn)  └──────┘  🏆(TT)   │
│                                │
│       👤(Hồ sơ)               │
│                                │
│  ┌──────────────────────────┐  │
│  │ 🤟 Ngôn ngữ ký hiệu    │  │  ← Sign language bar
│  │    Beta                  │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
```

### 8.3 Lazy Download Architecture

```
App cài đặt (~30MB)  →  KHÔNG có model 3D
                          ↓
User mở Doctor Hub lần đầu
                          ↓
┌─────────────────────────────────────┐
│  Bạn muốn tải Bác sĩ 3D?          │
│  📦 ~25MB  🌐 Cần mạng  💾 Cache  │
│                                     │
│  [Tải Bác sĩ 3D]                  │
│  [Dùng phiên bản đơn giản]         │
└─────────────────────────────────────┘
                          ↓
Tải từ CDN → Cache local → Sẵn sàng
                          ↓
Lần sau mở → Load trực tiếp từ cache
```

### 8.4 3D Model Spec (USER tự xử lý)

| Yêu cầu | Chi tiết |
|----------|----------|
| **Format** | `.glb` (GLTF Binary) — tương thích model_viewer_plus |
| **Kích thước** | ≤ 25MB (sau optimize) |
| **Nhân vật** | Bác sĩ cartoon friendly, phong cách dễ thương, phù hợp trẻ em |
| **Skeleton** | Humanoid rig, hỗ trợ blend shapes cho facial expressions |
| **Animation set** | `idle` (thở, nhìn xung quanh), `wave` (vẫy tay chào), `talk` (mở miệng khi TTS phát), `sign_language_*` (bộ cử chỉ VSL), `point_*` (chỉ vào các nút xung quanh) |
| **Texture** | Baked lighting, PBR materials, tối ưu cho mobile |
| **LOD** | 2 levels: High (≤15k polygons), Low (≤5k polygons cho máy yếu) |

### 8.5 Flutter Integration

```dart
// pubspec.yaml — thêm khi có model thật
dependencies:
  model_viewer_plus: ^1.7.0  # Render .glb trên Flutter

// Thay thế placeholder trong doctor_hub_page.dart:
ModelViewer(
  src: localModelPath,       // Path từ ModelDownloadService
  autoRotate: false,
  cameraControls: true,
  ar: false,
  animationName: 'idle',     // Chuyển animation theo context
)
```

### 8.6 Voice Mimic (Nhại giọng)

```
User nói → Speech-to-Text → Text → flutter_tts (pitch cao hơn) → Phát lại
```

- Pitch shift: +20% so với giọng gốc (tạo hiệu ứng cartoon)
- Delay: 0.5s sau khi user ngừng nói
- Toggle on/off trong Settings bottom sheet

### 8.7 Sign Language Integration

- Sử dụng `sign_language_service.dart` (đã có skeleton)
- Khi bác sĩ "nói", đồng thời phát animation sign language tương ứng
- Bộ cử chỉ cần tạo: các triệu chứng phổ biến (đau, sốt, ho, mệt, buồn nôn...)
- Hiển thị subtitle text song song với animation

---

## 9. Module 8: Achievement & Streak System

### 9.1 Tổng quan

Hệ thống thành tựu gamification để khuyến khích người dùng sử dụng app đều đặn.
Theo dõi chuỗi hoạt động (streak) và trao huy chương khi đạt mốc.

### 9.2 Categories

| Category | Emoji | Ví dụ thành tựu |
|----------|-------|-----------------|
| Fitness | 🏋️ | Chuỗi 3/7/30 ngày tập, 10 bài tập |
| Health | ❤️ | Chuỗi 7/30 ngày check-in sức khỏe |
| Consult | 🩺 | Lần đầu hỏi bệnh, 5 cuộc tư vấn |
| Medicine | 💊 | Quét thuốc đầu tiên, 10 lần quét |
| Soul Garden | 🌱 | Nhật ký đầu tiên, chuỗi 7/30 ngày |
| Profile | 👤 | Hồ sơ đầy đủ |

### 9.3 Tier System

| Tier | Emoji | Level |
|------|-------|-------|
| Đồng | 🥉 | 1 |
| Bạc | 🥈 | 2 |
| Vàng | 🥇 | 3 |
| Kim cương | 💎 | 4 |

### 9.4 XP & Level

```
XP = Tổng rewardXp từ các achievement đã mở khóa
Level = floor(XP / 100) + 1
Progress = (XP - currentLevelXP) / (nextLevelXP - currentLevelXP)
```

### 9.5 Storage

- **Local-first**: SharedPreferences (JSON serialized)
- **Future**: Sync lên backend khi có API

### 9.6 Integration Points

```dart
// Khi user hoàn thành workout:
achievementService.recordActivity(AchievementCategory.fitness);

// Khi user viết nhật ký Soul Garden:
achievementService.recordActivity(AchievementCategory.soulGarden);

// Khi user hoàn thành consult:
achievementService.recordActivity(AchievementCategory.consult);

// Khi user quét thuốc:
achievementService.recordActivity(AchievementCategory.medicine);
```

---

> Tài liệu này làm cơ sở để phân chia task trong Tasks.md.
