# MediSign AI – Tài liệu Yêu cầu Chi tiết (Requirements)

> **Phiên bản:** 1.0 | **Ngày:** 13/02/2026  
> **Slogan:** "Hiểu bạn, không chỉ bệnh của bạn"

---

## MỤC LỤC

1. [Tổng quan sản phẩm](#1-tổng-quan-sản-phẩm)
2. [Vấn đề giải quyết](#2-vấn-đề-giải-quyết)
3. [Đối tượng người dùng](#3-đối-tượng-người-dùng)
4. [Kiến trúc tổng thể](#4-kiến-trúc-tổng-thể)
5. [Module 1: AI Medical Assistant](#5-module-1-ai-medical-assistant)
6. [Module 2: Camera Quét Thuốc](#6-module-2-camera-quét-thuốc)
7. [Module 3: Hỗ trợ Người khuyết tật](#7-module-3-hỗ-trợ-người-khuyết-tật)
8. [Module 4: Hỗ trợ Người cao tuổi](#8-module-4-hỗ-trợ-người-cao-tuổi)
9. [Module 5: Vườn Tâm Hồn (Soul Garden)](#9-module-5-vườn-tâm-hồn-soul-garden)
10. [Module 6: Kết nối Yêu thương (Care Connect)](#10-module-6-kết-nối-yêu-thương-care-connect)
11. [Bảo mật & Quyền riêng tư](#11-bảo-mật--quyền-riêng-tư)
12. [Gợi ý Bệnh viện & Hệ thống Y tế](#12-gợi-ý-bệnh-viện--hệ-thống-y-tế)
13. [Mô hình Kinh doanh](#13-mô-hình-kinh-doanh)
14. [So sánh Cạnh tranh](#14-so-sánh-cạnh-tranh)
15. [Dữ liệu cần thu thập & Chứng thực](#15-dữ-liệu-cần-thu-thập--chứng-thực)
16. [Hạn chế & Giới hạn](#16-hạn-chế--giới-hạn)
17. [Kế hoạch Training AI](#17-kế-hoạch-training-ai---chiến-lược-đạt-85+-accuracy)

---

## 1. TỔNG QUAN SẢN PHẨM

### 1.1 MediSign AI là gì?

MediSign AI là **ứng dụng trợ lý y tế AI tại nhà** hoạt động 24/7, phục vụ **mọi người Việt Nam** – từ người bình thường đến người khuyết tật, người cao tuổi, người nghèo – với khả năng giao tiếp đa phương thức chưa từng có.

### 1.2 Tuyên bố giá trị cốt lõi

MediSign AI **KHÔNG phải bác sĩ**. MediSign AI là:

- **Trợ lý sàng lọc**: Giúp người dùng hiểu triệu chứng, quyết định có cần đi bệnh viện hay không
- **Trợ lý dùng thuốc**: Nhận diện thuốc, kiểm tra tương tác, hướng dẫn liều dùng
- **Người bạn đồng hành**: Hiểu bối cảnh sống qua nhật ký, đưa lời khuyên cá nhân hóa
- **Cầu nối y tế**: Kết nối người khuyết tật với hệ thống y tế bằng mọi phương thức giao tiếp

### 1.3 Điểm khác biệt duy nhất (USP)

| # | USP | Giải thích |
|---|-----|-----------|
| 1 | **Context-aware AI** | Nhờ Vườn Tâm Hồn (nhật ký), AI hiểu bối cảnh sống, tâm lý, thói quen → tư vấn cá nhân hóa sâu, không phải câu trả lời chung chung như ChatGPT |
| 2 | **True Accessibility** | Model 3D y tá hỏi bệnh bằng 4 phương thức đồng thời, người dùng trả lời bằng bất kỳ cách nào họ có thể |
| 3 | **Medicine Scanner** | Chụp ảnh vỉ thuốc → nhận diện → kiểm tra tương tác → hướng dẫn liều dùng bằng tiếng Việt |
| 4 | **Privacy-first** | 2 chế độ bảo mật: Local-only (cực đoan) và Cloud ẩn danh (tiện lợi) |

---

## 2. VẤN ĐỀ GIẢI QUYẾT

### 2.1 Quá tải bệnh viện & thiếu tiếp cận y tế

- **Bệnh viện công hoạt động 200-300% công suất** (Bộ Y tế 2024)
- Nhiều người bệnh nhẹ có thể xử lý tại nhà nhưng lo lắng → đổ dồn đến BV
- Nhiều người bệnh nặng thực sự nhưng chủ quan → không đi khám → nguy hiểm
- Chi phí khám: 300.000 - 1.000.000 VNĐ/lần → rào cản cho người nghèo

**MediSign AI giải quyết:** Sàng lọc ban đầu → "Bạn nên đi BV ngay" hoặc "Bạn có thể xử lý tại nhà bằng cách..."

### 2.2 Dùng thuốc sai & thuốc giả

- **72% người Việt tự mua thuốc không có đơn bác sĩ** (WHO)
- Không biết tương tác thuốc nguy hiểm (ví dụ: Paracetamol + rượu bia)
- Thuốc giả, thuốc kém chất lượng tràn lan
- Người già quên liều, quên giờ uống

**MediSign AI giải quyết:** Quét thuốc bằng camera → nhận diện → cảnh báo tương tác → nhắc liều

### 2.3 Người khuyết tật bị bỏ rơi bởi hệ thống y tế

- **6.2 triệu người khuyết tật tại Việt Nam** (Tổng cục Thống kê)
- Người điếc/câm không giao tiếp được với bác sĩ → chẩn đoán sai
- Người khiếm thị không đọc được đơn thuốc
- Không có ứng dụng y tế nào tại VN thực sự thiết kế cho NKT

**MediSign AI giải quyết:** Giao tiếp đa phương thức – bất kỳ ai, dù khuyết tật gì, đều dùng được

### 2.4 Sức khỏe tinh thần bị bỏ quên

- Trầm cảm, lo âu gia tăng mạnh ở giới trẻ và người cao tuổi
- Không thói quen theo dõi sức khỏe tinh thần
- Phát hiện muộn → hậu quả nghiêm trọng

**MediSign AI giải quyết:** Vườn Tâm Hồn theo dõi tâm lý hàng ngày như trò chơi tránh nhàm chán → phát hiện sớm → can thiệp kịp thời và biện pháp cải thiện nhẹ ( lờ khuyên và hành động thiết thực)

---

## 3. ĐỐI TƯỢNG NGƯỜI DÙNG

### 3.1 Nhóm chính (Primary Users)

| Nhóm | Mô tả | Nhu cầu chính | Cách tương tác |
|------|-------|--------------|----------------|
| **Người dân bình thường** | 18-55 tuổi, có smartphone | Hỏi triệu chứng, quét thuốc, theo dõi sức khỏe | Text + Voice |
| **Người cao tuổi** | 55+ tuổi, ít quen công nghệ | Tư vấn sức khỏe đơn giản, nhắc thuốc | Voice-only ("Bác sĩ ơi"), chữ to |
| **Người điếc/câm** | Không nghe được, thường cũng không nói được | Giao tiếp y tế | Sign language + chạm hình + text |
| **Người khiếm thị** | Không nhìn được màn hình | Đọc đơn thuốc, hỏi bệnh | Voice toàn bộ |
| **Người khuyết tật vận động** | Không cử động được tay/chân | Hỏi bệnh không cần chạm | Voice-only |
| **Người ít tiếp cận công nghệ** | Vùng sâu, vùng xa, ít internet | Nhu cầu y tế cơ bản, offline mode | Voice, giao diện tối giản |
| **Người suy giảm nhận thức** | Trí nhớ kém, tâm lý không ổn định | Nhắc nhở, an toàn, theo dõi cảm xúc | Voice, Soul Garden, tự động nhắc |

### 3.2 Nhóm phụ (Secondary Users)

| Nhóm | Mô tả |
|------|-------|
| **Người thân / Người giám hộ** | **Tính năng "Quan tâm"**: Theo dõi sức khỏe từ xa cho cha mẹ già, NKT. Nhận cảnh báo khi có bất thường (quên thuốc, nhịp tim lạ, té ngã...). |
| **Nhà thuốc** | **Trợ lý giao tiếp**: Dùng MediSign để hiểu khách hàng khiếm thính/người già. <br> **Giảm tải**: Cho khách hàng dùng MediSign sơ cứu/triage trong lúc chờ đợi. |
| **Bệnh viện / Phòng khám** | Nhận hồ sơ bệnh nhân từ MediSign trước khi khám. Tích hợp làm cổng tiếp đón thông minh cho NKT. |

---

## 4. KIẾN TRÚC TỔNG THỂ – HỆ THỐNG 4 CHẾ ĐỘ

### 4.1 Triết lý: "Ai cũng dùng được, dù điều kiện nào"

MediSign AI không chỉ là 1 app – mà là **hệ sinh thái 4 chế độ** phục vụ mọi hoàn cảnh:

| # | Chế độ | Ai dùng? | Thiết bị | Mạng | Bảo mật | AI |
|---|---|---|---|---|---|---|
| 🔀 | **Hybrid** (Mặc định) | Đa số người dùng | Trung bình+ (≥6GB RAM) | 3G/4G | Cao (ẩn danh) | Cloud xử lý chính + Local viết lại cá nhân hóa |
| 🔒 | **Local-Only** | Người cần bảo mật tuyệt đối | Máy tốt (≥6GB RAM) | **Không cần** | **Tối đa** | Hoàn toàn on-device (Gemma 2B) |
| ☁️ | **Cloud-Only** | Máy yếu nhưng có mạng | Bất kỳ | 3G/4G ổn | Trung bình (ẩn danh) | Cloud xử lý toàn bộ |
| 📱 | **SMS/Call (Lite)** | Vùng sâu vùng xa | **Kể cả điện thoại cục gạch** | Chỉ cần 2G | N/A | AI trên server, trả lời qua SMS/Call |
| ⚡ | **Offline Fallback** | Bất kỳ ai mất mạng đột ngột | Bất kỳ | **Không** | Cao (local) | **Không AI** – Decision Tree + DB thuốc tĩnh (~30MB) |

### 4.2 Quyền lựa chọn của người dùng

> **Nguyên tắc: "Gợi ý thông minh, không ép buộc"**

App **tự động nhận diện** thiết bị và mạng để **gợi ý** chế độ phù hợp, nhưng người dùng **luôn có quyền thay đổi**.

**Luồng Onboarding (lần đầu mở app):**

```
Bước 1: App kiểm tra RAM + Mạng
    ↓
Bước 2: Hiển thị màn hình "Chọn chế độ hoạt động"
    ┌──────────────────────────────────────────────┐
    │  🔀 Hybrid (GỢI Ý cho bạn)     ← Auto-detect│
    │     "AI mạnh + Bảo mật cao"                  │
    │                                               │
    │  � Local-Only                                │
    │     "Bảo mật tuyệt đối, cần tải AI (~1.5GB)" │
    │                                               │
    │  ☁️ Cloud-Only                                │
    │     "Nhẹ nhất, cần internet"                  │
    └──────────────────────────────────────────────┘
    ↓
Bước 3: Nếu chọn Local-Only hoặc Hybrid:
    → Hỏi: "Tải AI về máy (~1.5GB) để dùng offline?"
    → Nếu Đồng ý: Tải Gemma 2B về máy (cần WiFi 1 lần)
    → Nếu Từ chối: Vẫn dùng được, nhưng khi offline
      sẽ chuyển sang Offline Fallback (Decision Tree)
```

**Khi mất mạng đột ngột (đang dùng Hybrid hoặc Cloud):**

```
Mất mạng detected!
    ↓
Kiểm tra: Có Local LLM trên máy không?
    ├── CÓ (đã tải trước) → Chuyển sang Local-Only
    │   "Bạn đang offline. AI vẫn hoạt động (bản nhẹ)."
    │
    └── KHÔNG → Chuyển sang Offline Fallback
        "Bạn đang offline. Dùng chế độ tra cứu cơ bản."
        (Decision Tree + DB thuốc tĩnh)
```

**Người dùng có thể thay đổi chế độ BẤT CỨ LÚC NÀO** trong Cài đặt.

### 4.3 Kiến trúc kỹ thuật (Hybrid Mode – Mặc định)

```
 NGƯỜI DÙNG
 📱 Mobile App (Flutter)
 
 Đầu vào:              Đầu ra:
 ├── Text               ├── Text (chữ to cho người già)
 ├── Voice              ├── Voice (TTS tiếng Việt)
 ├── Camera (thuốc)     ├── Video sign language
 ├── Camera (sign)      ├── Hình ảnh minh họa
 ├── Chạm hình/icon     ├── Model 3D y tá ký hiệu
 └── Emoji              └── Thông báo / nhắc nhở
        │                         │
 ┌──────▼────────────┐  ┌────────▼───────────────┐
 │  LOCAL ENGINE      │  │  CLOUD ENGINE           │
 │                    │  │  (Ẩn danh hoàn toàn)    │
 │ • Local LLM       │  │                          │
 │   (Gemma 2B)      │  │ • LLM lớn (Gemini)      │
 │   - Tự trả lời    │  │   xử lý triệu chứng    │
 │     offline        │  │   phức tạp              │
 │   - Viết lại câu  │  │                          │
 │     từ Cloud       │  │ • Medicine DB            │
 │                    │  │   (Cục Dược VN)          │
 │ • Soul Garden DB   │  │                          │
 │   (nhật ký, mã    │  │ • Hospital DB            │
 │    hóa local)     │  │   (BV, BHYT, khoa)       │
 │                    │  │                          │
 │ • OCR Engine       │  │ • Interaction Checker    │
 │   (nhận diện      │  │   (tương tác thuốc)      │
 │    vỉ thuốc)      │  │                          │
 │                    │  │ • SMS Gateway            │
 │ • Medicine DB      │  │   (cho MediSign Lite)    │
 │   (offline, ~25MB)│  │                          │
 │                    │  │ • Voicebot IVR           │
 │ • Decision Tree    │  │   (cho MediSign Lite)    │
 │   (offline, ~3MB) │  │                          │
 └────────────────────┘  └──────────────────────────┘
```

### 4.4 MediSign Lite – Chế độ SMS/Call cho vùng sâu vùng xa

> **Dành cho người không có smartphone hoặc mạng internet, chỉ có sóng 2G cơ bản.**

**Cách hoạt động:**

```
📱 Nhắn SMS đến 1900xxxx:
   "Tôi bị đau bụng, sốt 2 ngày"
      ↓
📡 Mạng 2G → SMS Gateway (Server)
      ↓
🤖 Server xử lý bằng Gemini API
      ↓
📱 Trả lời SMS:
   "MediSign: Đau bụng + sốt 2 ngày có thể nghiêm trọng.
    Hãy đến trạm y tế gần nhất. Gọi 115 nếu đau dữ dội."

--- HOẶC ---

📞 Gọi điện đến 1900xxxx:
      ↓
🤖 Voicebot (IVR + AI) hỏi theo luồng:
   "Bạn bị đau ở đâu? Nhấn 1: đầu, 2: bụng, 3: ngực..."
      ↓
📞 Trả lời bằng giọng nói tự động
```

**Ưu điểm:**
- Chỉ cần sóng 2G (phủ ~99% dân số VN, kể cả vùng núi)
- Dùng được trên điện thoại cục gạch
- Không tốn data internet
- Chi phí SMS: ~300-600 VNĐ/lượt (có thể được B2G/NGO tài trợ)

### 4.5 Offline Fallback – Khi mất mạng và không có Local LLM

**Dung lượng Database tĩnh:**

| Database | Nội dung | Dung lượng |
|---|---|---|
| Thuốc (Cục Dược VN) | ~30.000 thuốc (tên, hoạt chất, liều, tương tác) | ~15-25MB |
| Decision Tree (Triage) | ~200-500 luồng triệu chứng | ~1-3MB |
| Sơ cứu cơ bản | ~30-50 tình huống + hình ảnh | ~5MB |
| **Tổng** | | **~25-35MB** |

→ Nhẹ hơn 1 video TikTok. Máy 32GB dư sức chứa.

**Cách hoạt động:** Không dùng AI, mà dùng **cây quyết định (Decision Tree)** – người dùng chạm hình theo luồng cố định để nhận kết quả sàng lọc.

### 4.6 Luồng xử lý chính (Hybrid Mode)

```
Bước 1: Người dùng nhập (text/voice/sign/chạm hình)
    ↓
Bước 2: App chuyển tất cả thành text chuẩn và mã hóa
    ↓
Bước 3: Gửi text ẩn danh lên Cloud LLM
         (chỉ gửi: "Nam, 35 tuổi, đau bụng phải dưới, 2 ngày, sốt nhẹ")
         (KHÔNG gửi: tên, SĐT, địa chỉ, ảnh...)
    ↓
Bước 4: Cloud LLM trả về câu trả lời y tế chuẩn
    ↓
Bước 5: Local LLM viết lại câu trả lời cho phù hợp bối cảnh
         (VD: biết user là SV đang stress deadline → điều chỉnh lời khuyên)
    ↓
Bước 6: Hiển thị kết quả theo phương thức phù hợp
         (text + voice + sign language video + hình ảnh)
```

### 4.7 Chiến lược AI: "AI không tự nhớ – mà tra cứu rồi giải thích"

#### Nguyên tắc cốt lõi

> **LLM (Gemma/Gemini) = Bộ não suy luận.** Nó hiểu ngôn ngữ, hiểu câu hỏi, biết cách giải thích.
> **Database = Sách giáo khoa.** Chứa dữ liệu chính xác về thuốc, bệnh, tương tác.
> **Khi trả lời:** AI tra Database → lấy dữ liệu → viết câu trả lời tự nhiên. **KHÔNG tự bịa.**

```
User: "Tôi uống Warfarin, có uống Aspirin được không?"
    ↓
Bước 1: App tra LOCAL DATABASE thuốc
    → Tìm: Warfarin + Aspirin = TƯƠNG TÁC ĐỎ (tăng xuất huyết)
    ↓
Bước 2: Đưa kết quả vào prompt cho AI
    Prompt: "Dữ liệu: [Warfarin + Aspirin: mức ĐỎ, xuất huyết]. Giải thích."
    ↓
Bước 3: AI viết tự nhiên:
    "⚠️ KHÔNG nên uống Aspirin khi dùng Warfarin! Tăng nguy cơ
    chảy máu. Hãy hỏi bác sĩ để được kê thuốc thay thế."
```

Kỹ thuật này gọi là **RAG (Retrieval-Augmented Generation)** – tiêu chuẩn ngành cho AI y tế.

#### Lộ trình phát triển AI (3 giai đoạn)

| Giai đoạn | Users | Cloud AI | Local AI | Chi phí Cloud |
|---|---|---|---|---|
| **MVP** (Thi SV_STARTUP) | Demo | 🏆 **MediSign-Server** (Qwen 72B + LoRA y tế VN) trên server thuê tạm | Gemma 2B gốc + Prompt + RAG | **~$3-5/buổi demo** |
| **Growth** | 1.000-10.000 | Gemini Flash trả phí + RAG (tiết kiệm, chạy 24/7) | MediSign-Gemma (LoRA fine-tune) | ~$30-100/tháng |
| **Scale** | 10.000+ | 🏆 **MediSign-Server** (Self-hosted Qwen 72B) chạy 24/7 | MediSign-Gemma tối ưu | ~$300/tháng **CỐ ĐỊNH** |

> **Chiến lược MVP:** Demo thi bằng **AI thật, model mạnh nhất** (Qwen 72B) trên server thuê tạm theo giờ (~$1/giờ). Bật trước khi demo, tắt sau khi xong. BGK thấy AI trả lời chất lượng ngang GPT-4 → **cực ấn tượng**.
> **Khi chạy thực tế (Growth):** Chuyển sang Gemini Flash (rẻ, ổn định 24/7) cho đến khi đủ user để justify server riêng.

#### Quy trình Demo thi SV_STARTUP

```
TRƯỚC THI 1 NGÀY:
  1. Thuê server Vast.ai (A100 spot, ~$1/giờ)
  2. Deploy MediSign-Qwen (Qwen 72B 4-bit + LoRA y tế VN) bằng vLLM
  3. Test thử vài câu hỏi y tế

NGÀY THI (trước 30 phút):
  4. Bật server → App kết nối → SẴN SÀNG

DEMO TRƯỚC BGK:
  5. BGK hỏi trực tiếp trên app
  6. AI trả lời chất lượng cao, tiếng Việt tự nhiên
  7. "AI này do chúng tôi tự fine-tune, tự host, toàn quyền dữ liệu"

SAU THI:
  8. Tắt server → DỪNG TRẢ TIỀN
```

#### Self-hosted Server: MediSign-Server

Thay vì phụ thuộc Google/OpenAI, MediSign tự vận hành AI trên server riêng:

```
User Request (ẩn danh)
    ↓
Load Balancer
    ├── MediSign-Server #1 (Qwen 72B + LoRA y tế VN) ← Chính
    ├── MediSign-Server #2 (backup / scale)
    └── Gemini Flash API (fallback khi server quá tải)
    ↓
RAG: Tra DB thuốc/bệnh → Inject vào prompt
    ↓
AI trả lời chính xác + tự nhiên
```

**Tại sao chọn Qwen 2.5 72B để Self-host:**

| Tiêu chí | Qwen 2.5 72B | Llama 3.1 70B | Meditron 70B |
|---|---|---|---|
| Tiếng Việt | ⭐⭐⭐⭐ (tốt nhất) | ⭐⭐⭐ | ⭐⭐ |
| Chất lượng y tế | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Ít bịa (hallucination) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| License thương mại | ✅ Apache 2.0 | ✅ Meta License | ✅ Llama License |
| Fine-tune dễ | ✅ LoRA/QLoRA | ✅ LoRA/QLoRA | ✅ LoRA |
| VRAM cần (4-bit) | 40GB | 38GB | 38GB |

**Chi phí server thực tế:**

| Nhà cung cấp | GPU | Chi phí/tháng | Phục vụ đồng thời |
|---|---|---|---|
| Vast.ai | 1x A100 80GB | ~$150-300 | ~50-100 users |
| RunPod | 1x A100 80GB | ~$250-400 | ~50-100 users |
| Lambda Labs | 1x A100 | ~$350 | ~50-100 users |

**So sánh kinh tế:** Dưới 10.000 câu/ngày → Gemini Flash rẻ hơn. Trên 10.000 câu/ngày → Self-hosted rẻ hơn nhiều.

**Lợi ích Self-hosted:**
- ✅ **0 đồng/câu hỏi** – người nghèo dùng thoải mái
- ✅ **Toàn quyền dữ liệu** – không ai đọc data bệnh nhân
- ✅ **Không phụ thuộc** bên thứ 3 (Google tăng giá/ngừng → không ảnh hưởng)
- ✅ **Fine-tune sâu** – train model chuyên y tế VN, không giới hạn

#### LoRA Fine-tuning: Tạo "Thạc sĩ Y tế AI"

> **Mục tiêu:** Biến model tổng quát thành chuyên gia y tế có **chuyên môn sâu về chẩn đoán bệnh**, nhưng **CHỈ GỢI Ý, KHÔNG quyết đoán**. AI đóng vai trò "thạc sĩ y tế tư vấn" – phân tích chuyên sâu nhưng luôn khuyên khám bác sĩ thật.

```
Model gốc (tổng quát)
    ↓ Fine-tune bằng LoRA
    ↓ Dữ liệu: 5.000-50.000 Q&A y khoa tiếng Việt
    ↓ Thời gian: 2-4 giờ (Gemma 2B), 8-12 giờ (Qwen 72B)
    ↓
MediSign-Qwen / MediSign-Gemma (Thạc sĩ Y tế AI)
    - Chuyên môn sâu về chẩn đoán bệnh qua triệu chứng
    - Hiểu thuốc VN, tương tác thuốc, chống chỉ định
    - Phân biệt mức độ nghiêm trọng (Xanh/Vàng/Đỏ)
    - NHƯNG: Luôn nói "Đây là GỢI Ý, không thay thế bác sĩ"
```

**Nguyên tắc "Gợi ý, không chẩn đoán" (trong training data):**

```
❌ SAI (Chẩn đoán quyết đoán):
   "Bạn bị viêm ruột thừa. Cần phẫu thuật ngay."

✅ ĐÚNG (Gợi ý chuyên sâu):
   "Dựa trên triệu chứng đau bụng dưới phải + sốt + 2 ngày,
    CÓ KHẢ NĂNG liên quan đến viêm ruột thừa hoặc viêm đại tràng.
    ⚠️ Mức VÀNG – Bạn NÊN đến khám bác sĩ ngoại khoa trong 24h.
    📍 Bệnh viện gần bạn: [Tìm BV]
    ⚕️ Lưu ý: Đây là gợi ý sơ bộ, KHÔNG thay thế chẩn đoán y khoa."
```

**Cách huấn luyện nguyên tắc này:**
- Training data luôn dùng từ: "có khả năng", "gợi ý", "nên đi khám", "không thay thế bác sĩ"
- System Prompt khóa cứng: Từ chối đưa chẩn đoán cuối cùng
- Reward model (RLHF): Phạt nặng nếu AI nói chắc chắn, thưởng nếu AI khuyên đi khám

#### Nguồn dữ liệu Fine-tuning

| Nguồn | Nội dung | Số lượng | Chi phí |
|---|---|---|---|
| MedQuAD (GitHub) | Q&A y khoa (Anh) | 47.000 cặp | Miễn phí |
| ChatDoctor (GitHub) | Hội thoại bệnh nhân-bác sĩ | 100.000 cặp | Miễn phí |
| Tự tạo (VN) | Dịch + viết Q&A y tế tiếng Việt | 5.000-10.000 cặp | Dùng Gemini dịch (~$5-10) |
| Dược thư Quốc gia VN | Thuốc, liều, tương tác | 30.000 thuốc | Dữ liệu công khai |

#### Kiến trúc Dual LoRA: 1 Model + 2 Adapter

> **Ý tưởng:** Thay vì tải 2 AI riêng biệt (tốn RAM), dùng **1 Gemma 2B** + swap 2 LoRA adapter nhỏ theo vai trò.

| Adapter | Tên | Kích thước | Chức năng | Nhạy cảm? |
|---|---|---|---|---|
| **#1 MediSign-Med** | AI Thạc sĩ Y tế | ~50MB | Chẩn đoán, thuốc, triage, kiến thức y khoa | ❌ Không (dùng chung) |
| **#2 MediSign-Personal** | AI Cá nhân | ~50-100MB | Hiểu người dùng, viết lại câu trả lời cho phù hợp | ✅ Có (riêng mỗi user) |

```
RAM thực tế:
    Gemma 2B (base)      = 1.5GB  ← Tải 1 lần
    Adapter Medical      = ~50MB  ← Gắn vào khi cần
    Adapter Personal     = ~100MB ← Swap khi cần
    ────────────────────────────
    Tổng                 = ~1.65GB ← Không tăng đáng kể!
```

**Luồng xử lý Dual LoRA:**

```
User hỏi: "Tôi bị đau đầu, uống gì được?"
    ↓
BƯỚC 1: Gắn Adapter #1 (Medical) → AI y tế trả lời chuẩn
    "Đau đầu có thể dùng Paracetamol 500mg, max 4 viên/ngày.
     Mức XANH. Kéo dài >3 ngày → đi khám."
    ↓
BƯỚC 2: Swap Adapter #2 (Personal) → Viết lại cho phù hợp
    Input: câu trả lời y tế + biết user là SV stress deadline
    Output: "Bạn hay đau đầu khi stress deadline đúng không? 😊
             Uống Paracetamol 500mg nhé, nhớ đừng quá 4 viên.
             Hôm nay nghỉ ngơi sớm nha!"
    ↓
BƯỚC 3: Hiển thị cho user (thời gian swap: ~100-200ms)
```

**Adapter Personal học từ đâu:**
- Đọc Soul Garden (nhật ký, cảm xúc, thói quen)
- Phân tích lịch sử chat (phong cách giao tiếp, từ ngữ hay dùng)
- Fine-tune định kỳ trên chính thiết bị (mỗi tuần, 5-10 phút)

#### AI Memory Backup: "Bác sĩ quen nhớ về bạn"

> **Vấn đề:** Local-Only mode → mất điện thoại = mất dữ liệu?
> **Giải pháp:** Backup Adapter Personal (mã hóa) lên cloud. Khi mất máy → tải adapter về → AI "nhớ lại" người dùng.

```
BACKUP (tự động mỗi tuần):
    Adapter Personal (~100MB)
        ↓ Mã hóa AES-256 bằng Recovery Key
        ↓ Upload lên MediSign Cloud
        → Server giữ: [████████] ← Không đọc được

KHÔI PHỤC (khi mất máy):
    Máy mới → Đăng nhập → Nhập Recovery Key (12 từ)
        ↓
    Tải Adapter Personal (mã hóa) → Giải mã → Gắn vào Gemma 2B
        ↓
    AI "nhớ lại": thói quen, thuốc, bệnh nền, phong cách giao tiếp
        ↓
    Hỏi: "Tóm tắt lịch sử sức khỏe của tôi"
        → AI viết lại ~30-50% nội dung nhật ký (khác câu chữ, cùng ý)
        → ⚠️ Đánh dấu: "Nội dung tái tạo bởi AI Memory"
```

**Bảo mật Adapter Personal:**

| Tình huống | Kẻ trộm có thể? | Lý do |
|---|---|---|
| Lấy file adapter từ điện thoại | ❌ Không đọc được | File mã hóa AES-256 |
| Giải mã adapter | ❌ Không có key | Key lưu trong Keystore, theo account |
| Dùng adapter trên máy khác | ❌ Không chạy được | Cần đăng nhập account + base model + prompt format |
| Đọc trực tiếp nội dung adapter | ❌ Không thể | Adapter chứa "trọng số neural", không phải text |

**Hệ thống backup 2 tầng:**

| Tầng | Loại | Khôi phục | Độ chính xác |
|---|---|---|---|
| **Tầng 1** | Encrypted Cloud Backup (DB gốc) | Toàn bộ dữ liệu | 100% |
| **Tầng 2** | AI Memory (Adapter Personal) | Bối cảnh, thói quen, phong cách | ~30-50% |

→ Tầng 1 là chính. Tầng 2 là backup phụ khi tầng 1 không có.
### 4.8 Scalability, High Availability & Disaster Recovery

> **Nguyên tắc: "Không bao giờ chết hoàn toàn"**

#### Chi phí Scale (Worst Case: 100% requests lên Cloud)

| Concurrent Users | Servers A100 cần | Chi phí/tháng | Chi phí/user/tháng |
|---|---|---|---|
| 10.000 | 3-5 | ~$1.000-1.500 | $0.10-0.15 |
| 100.000 | 30-50 | ~$9.000-15.000 | $0.09-0.15 |
| 500.000 | 150-250 | ~$45.000-75.000 | $0.09-0.15 |
| 1.000.000 | 300-500 | ~$90.000-150.000 | $0.09-0.15 |

> Khi đạt 500K+ users → MediSign trở thành **nền tảng y tế quốc gia** → chi phí chia sẻ qua B2G (Bộ Y tế tài trợ) hoặc B2B (Bệnh viện trả phí tích hợp).

#### Biện pháp chống quá tải

**1. Rate Limiting + Priority Queue:**
```
Request đến server
    ↓
Rate Limiter: Mỗi user tối đa 5 câu/phút
    ↓
Priority Queue (hàng đợi ưu tiên):
    ├── Mức ĐỎ (cấp cứu)  → XỬ LÝ NGAY
    ├── Mức VÀNG           → Chờ 10-30 giây
    └── Mức XANH           → Chờ 30-60 giây
```

**2. Graceful Degradation (Xuống cấp êm ái):**

| Mức tải server | Hành động |
|---|---|
| < 80% | Bình thường – Qwen 72B xử lý tất cả |
| 80-95% | Chuyển câu hỏi đơn giản sang model nhẹ (Qwen 7B, nhanh 10x) |
| 95-100% | Bật Gemini Flash API làm backup (trả tiền/request nhưng không sập) |
| 100% (quá tải) | Request Queue – "Đang xử lý, chờ 1-2 phút". Ưu tiên mức ĐỎ |

**3. Multi-region High Availability:**
```
Load Balancer
    ├── Server Pool A (Singapore)
    ├── Server Pool B (Japan) ← backup nếu A sập
    └── Gemini Flash API     ← fallback cuối cùng
```

#### Khi server SẬP HOÀN TOÀN – 4 lớp bảo vệ

```
LỚP 1: Server backup tự động tiếp quản (Multi-region)
    ↓ Nếu tất cả server sập:
LỚP 2: Gemini Flash API thay thế (Google lo hạ tầng)
    ↓ Nếu mất internet hoàn toàn:
LỚP 3: Local AI trên điện thoại (nếu đã tải) hoặc Offline Fallback (Decision Tree)
    ↓ Nếu mọi thứ đều hỏng:
LỚP 4: Nút GỌI CẤP CỨU 115 luôn hoạt động (dùng sóng GSM, không cần internet)
```

> **Kết luận:** App KHÔNG BAO GIỜ chết hoàn toàn. Chất lượng AI có thể giảm khi quá tải, nhưng người dùng LUÔN được hỗ trợ ở mức nào đó.

---

## 5. MODULE 1: AI MEDICAL ASSISTANT (Trợ lý Tư vấn Y tế)

### 5.1 Mô tả

Chatbot AI tư vấn sức khỏe bằng tiếng Việt, hỗ trợ đa phương thức nhập liệu, có khả năng phân tích triệu chứng và đưa ra lời khuyên sơ bộ.

### 5.2 Chức năng chi tiết

**a) Phân tích triệu chứng**
- Người dùng mô tả triệu chứng bằng text, voice, hoặc chạm hình
- AI hỏi thêm câu hỏi follow-up (giống bác sĩ thật): vị trí đau cụ thể, thời gian bao lâu, mức độ, triệu chứng kèm theo
- Đưa ra đánh giá: mức độ nghiêm trọng (nhẹ/trung bình/nặng)
- Lời khuyên: tự xử lý tại nhà HOẶC cần đi khám BV

**b) Tư vấn sơ cứu**
- Hướng dẫn sơ cứu cơ bản: bỏng, chảy máu, gãy xương, ngộ độc, đuối nước
- Hướng dẫn bằng hình ảnh minh họa + text + voice
- Gọi cấp cứu 115 nhanh chóng nếu cần

**c) Phân loại mức độ khẩn cấp (Triage)**

| Mức | Màu | Hành động | Ví dụ |
|-----|-----|-----------|-------|
| 🟢 Nhẹ | Xanh | Tự xử lý tại nhà | Cảm cúm nhẹ, đau đầu thông thường |
| 🟡 Trung bình | Vàng | Nên đi khám trong 1-2 ngày | Đau bụng kéo dài, sốt >3 ngày |
| 🔴 Khẩn cấp | Đỏ | ĐI BV NGAY hoặc gọi 115 | Đau ngực, khó thở, co giật |

**d) Disclaimer (Tuyên bố miễn trừ)**
- Mỗi lần tư vấn đều hiển thị: "Đây là tư vấn sơ bộ của AI, KHÔNG thay thế khám bác sĩ. Nếu triệu chứng nghiêm trọng, hãy đến cơ sở y tế ngay."
- App KHÔNG chẩn đoán bệnh, chỉ gợi ý khả năng và khuyên hành động tiếp theo

---

## 6. MODULE 2: CAMERA QUÉT THUỐC

### 6.1 Mô tả

Người dùng chụp ảnh vỉ thuốc / hộp thuốc → AI nhận diện tên thuốc → tra cứu thông tin → kiểm tra tương tác → hướng dẫn sử dụng.

### 6.2 Luồng hoạt động

```
📸 Chụp ảnh vỉ thuốc
    ↓
🔍 OCR nhận diện text trên vỉ (tên thuốc, hàm lượng, hạn sử dụng)
    ↓
🔎 Tra cứu trong Database Cục Dược VN (~30.000 thuốc)
    ↓
📋 Hiển thị thông tin:
    ├── Tên thuốc + hoạt chất
    ├── Công dụng
    ├── Liều dùng khuyến cáo
    ├── Tác dụng phụ
    ├── Chống chỉ định
    └── Hạn sử dụng (nếu đọc được)
    ↓
⚠️ Kiểm tra tương tác thuốc:
    - So sánh với danh sách thuốc người dùng đang uống (lưu trong app)
    - Cảnh báo nếu có tương tác nguy hiểm
    ↓
💬 Hướng dẫn dùng thuốc:
    - Text + Voice (cho người khiếm thị)
    - Video sign language (cho người điếc)
    - Hình ảnh minh họa (cho người mù chữ)
```

### 6.3 Ví dụ thực tế

```
Người dùng chụp ảnh vỉ thuốc Hapacol 650

App hiển thị:
┌─────────────────────────────────────┐
│ 💊 HAPACOL 650                       │
│ Hoạt chất: Paracetamol 650mg        │
│ Công dụng: Giảm đau, hạ sốt         │
│ Liều dùng: 1 viên / 6 tiếng         │
│ Tối đa: 4 viên / ngày               │
│                                      │
│ ⚠️ CẢNH BÁO:                        │
│ Bạn đang uống Warfarin (đã lưu).    │
│ Paracetamol + Warfarin → TĂNG NGUY  │
│ CƠ CHẢY MÁU. Hãy hỏi bác sĩ trước │
│ khi dùng.                            │
│                                      │
│ 🔔 Đặt nhắc uống thuốc?  [Có] [Không]│
└─────────────────────────────────────┘
```

### 6.4 Tính năng nhắc uống thuốc

- Sau khi quét thuốc → người dùng có thể bật nhắc nhở
- App nhắc đúng giờ, đúng liều
- Đặc biệt hữu ích cho người già hay quên
- Tích hợp với Soul Garden: nếu AI phát hiện người dùng hay quên qua nhật ký → tự động đề xuất bật nhắc nhở

---

## 7. MODULE 3: HỖ TRỢ NGƯỜI KHUYẾT TẬT

### 7.1 Triết lý thiết kế

> **"Dù bạn khuyết tật gì, app vẫn hiểu bạn."**

Thay vì thiết kế riêng cho từng loại khuyết tật, MediSign AI sử dụng **mô hình Y tá 3D** giao tiếp bằng **TẤT CẢ 4 phương thức ĐỒNG THỜI**, và người dùng trả lời bằng **bất kỳ cách nào họ có thể**.

### 7.2 Model 3D Y tá Ảo

**Hình thức:**
- Nhân vật 3D y tá thân thiện, luôn hiển thị trên màn hình khi hỏi bệnh
- Y tá giao tiếp với người dùng bằng 4 phương thức đồng thời

**4 phương thức đầu ra (Y tá → Người dùng):**

| # | Phương thức | Mô tả | Phục vụ ai |
|---|------------|-------|-----------|
| 1 | 📝 **Hiển thị chữ** | Text câu hỏi hiện trên màn hình | Người điếc biết đọc chữ |
| 2 | 🖼️ **Hình ảnh minh họa** | Icon/emoji/hình vẽ thể hiện ý (VD: mặt vui 😊 = ổn, mặt đau 😣 = khó chịu) | Người mù chữ, người điếc không biết đọc |
| 3 | 🔊 **Âm thanh từ loa** | Y tá nói câu hỏi bằng giọng Việt | Người bình thường, người khiếm thị |
| 4 | 🤟 **Model 3D ra ký hiệu** | Y tá 3D thực hiện ngôn ngữ ký hiệu Việt Nam | Người điếc biết ngôn ngữ ký hiệu |

**4 phương thức đầu vào (Người dùng → App):**

| # | Phương thức | Mô tả | Phục vụ ai |
|---|------------|-------|-----------|
| 1 | ⌨️ **Nhập text** | Gõ chữ mô tả triệu chứng | Người câm biết chữ |
| 2 | 🎤 **Voice** | Nói miệng | Người bình thường, người khiếm thị, NKT vận động |
| 3 | 👆 **Chọn ảnh/icon** | Chạm vào hình ảnh trên màn hình (hình cơ thể, emoji đau/sốt/buồn nôn) | Người mù chữ, người điếc không biết KH |
| 4 | 📹 **Camera ký hiệu tay** | Camera nhận diện ngôn ngữ ký hiệu real-time | Người điếc biết KH |

### 7.3 Ví dụ luồng hỏi bệnh cho người điếc mù chữ

Đây là trường hợp **khó nhất** – người không nghe được, không đọc được chữ, không biết ngôn ngữ ký hiệu:

```
Bước 1: Y tá 3D xuất hiện, đồng thời:
   - Hiện chữ: "Bạn cảm thấy thế nào?"
   - Hiện 2 hình lớn: [😊 Ổn] [😣 Khó chịu]
   - Phát âm thanh: "Bạn cảm thấy thế nào?"
   - Model 3D ra ký hiệu
   
   → Người dùng mù chữ nhìn hình → chạm [😣 Khó chịu]

Bước 2: Y tá 3D hiện hình cơ thể người:
   - Hiện chữ: "Đau ở đâu?"
   - Hiện hình cơ thể với các vùng có thể chạm: đầu, ngực, bụng, tay, chân
   - Phát âm + ký hiệu

   → Người dùng chạm vào vùng "bụng" trên hình

Bước 3: Y tá 3D hỏi tiếp:
   - Hiện hình: [🔥 Nóng/Sốt] [🤮 Buồn nôn] [💩 Tiêu chảy] [❌ Không có]
   
   → Người dùng chạm [🤮 Buồn nôn]

Bước 4: Y tá 3D hỏi thời gian:
   - Hiện hình: [1️⃣ ngày] [2️⃣ ngày] [3️⃣ ngày] [7️⃣+ ngày]
   
   → Người dùng chạm [2️⃣]

Bước 5: AI tổng hợp và trả lời:
   - Hiện kết quả bằng cả 4 phương thức
   - Hiện hình minh họa hành động cần làm
   - Nếu cần đi BV → hiện biểu tượng BV lớn + nút gọi người thân
```

### 7.4 Xử lý theo từng loại khuyết tật

**a) Người điếc (thường cũng câm vì không nghe được âm thanh mình nói):**

| Khả năng | Giải pháp MediSign |
|----------|-------------------|
| Biết đọc chữ + biết KH | Text + sign language camera (đầy đủ nhất) |
| Biết đọc chữ, không biết KH | Text chat + chạm hình |
| Không biết chữ, biết KH | Camera sign language + hình ảnh |
| Không biết chữ, không biết KH | **Chạm hình + emoji + icon** (tầng giao tiếp nguyên thủy nhất) |
| Có thể nói được (một số người điếc nói được) | Voice input cũng hỗ trợ |

**b) Người khiếm thị:**
- Toàn bộ điều khiển bằng voice
- AI đọc to mọi thông tin
- Hướng dẫn thuốc bằng giọng nói chi tiết

**c) Người khuyết tật vận động (không cử động tay/chân, dị tật):**
- Voice-only: nói để điều khiển mọi thứ
- Không cần chạm màn hình

**d) Người già:**
- Xem mục Module 4 bên dưới

### 7.5 Hạn chế bất khả kháng

> **App KHÔNG THỂ phục vụ người vừa câm, vừa điếc, vừa mù cùng lúc.** Đây là hạn chế vật lý – không có phương thức giao tiếp nào khả thi nếu người dùng không nhìn, không nghe, và không nói được.

Trong trường hợp này:
- App cần **sự hỗ trợ từ người thân** ở giai đoạn đầu làm quen
- Người thân setup app, thiết lập profile, hướng dẫn các thao tác cơ bản
- Đây là **trách nhiệm gia đình** mà app không thể thay thế hoàn toàn

---

## 8. MODULE 4: HỖ TRỢ NGƯỜI CAO TUỔI

### 8.1 Triết lý: "Như gọi video cho bác sĩ"

Người già quen với việc **nói chuyện**, không quen gõ chữ hay chạm nút. Giải pháp: biến app thành **cuộc gọi video với bác sĩ ảo**.

### 8.2 Wake Word – Kích hoạt bằng giọng nói

Giống Siri có "Hey Siri", MediSign AI có **wake word** người dùng tùy chọn:

```
Người già nói: "Bác sĩ ơi!"
    ↓
App tự động kích hoạt (không cần mở app, không cần chạm)
    ↓
Y tá 3D xuất hiện: "Dạ, con nghe ạ. Bác cảm thấy thế nào?"
    ↓
Người già nói: "Tôi bị đau đầu từ sáng tới giờ, uống thuốc gì đây?"
    ↓
AI xử lý + trả lời bằng giọng nói (không cần đọc chữ)
```

### 8.3 Giao diện dành cho người già

- **Chữ cực to** (font size 24+)
- **Nút lớn, ít nút** (tối đa 3-4 nút trên màn hình)
- **Màu sắc tương phản cao** (dễ nhìn cho mắt kém)
- **Toàn bộ điều khiển bằng voice** – không bắt buộc chạm
- **Nút gọi người thân khẩn cấp** luôn hiện trên màn hình

### 8.4 Tính năng dành cho người già

| Tính năng | Mô tả |
|-----------|-------|
| Nhắc uống thuốc | Báo giờ + đọc tên thuốc + liều dùng bằng giọng nói |
| Nhắc tái khám | Ghi nhớ lịch hẹn BV, nhắc trước 1 ngày |
| Gọi người thân | 1 nút bấm gọi con/cháu khi cần |
| Bản tin sức khỏe | Đọc to mẹo sức khỏe hàng ngày (giữ thói quen mở app) |

---

## 9. MODULE 5: VƯỜN TÂM HỒN (SOUL GARDEN)

### 9.1 Mô tả tổng quan

Vườn Tâm Hồn là tính năng **cốt lõi tạo sự khác biệt** của MediSign AI so với mọi ứng dụng y tế khác. Đây KHÔNG phải tính năng phụ, mà là **nền tảng** giúp AI hiểu sâu người dùng.

### 9.2 Cách hoạt động

**Bước 1: Viết nhật ký hàng ngày**
- Người dùng viết vài dòng về ngày hôm nay (cảm xúc, sức khỏe, hoạt động)
- Có thể viết text, nói voice, hoặc chọn emoji nhanh
- Không bắt buộc, nhưng được khuyến khích qua gamification

**Bước 2: AI phân tích & xây dựng profile**
- AI đọc nhật ký → hiểu bối cảnh: nghề nghiệp, stress level, thói quen ngủ, chế độ ăn, tâm lý
- Tích lũy qua nhiều ngày → profile ngày càng chính xác
- Dữ liệu này **CHỈ LƯU LOCAL** trên điện thoại người dùng

**Bước 3: Tư vấn cá nhân hóa**
- Khi người dùng hỏi bệnh, AI dùng bối cảnh từ nhật ký để tư vấn chính xác hơn

**Ví dụ so sánh:**

```
Câu hỏi: "Tôi bị đau đầu"

ChatGPT (không biết bối cảnh):
→ "Đau đầu có thể do nhiều nguyên nhân: stress, thiếu ngủ, 
   huyết áp cao... Bạn nên nghỉ ngơi và uống thuốc giảm đau."

MediSign AI (biết bối cảnh qua nhật ký):
→ Nhật ký 3 ngày gần đây: "deadline", "ngủ 4h", "quên ăn sáng"
→ "Đau đầu của bạn RẤT CÓ THỂ do 3 ngày liên tục thiếu ngủ
   và bỏ bữa sáng mà bạn đã viết trong nhật ký. 
   Không cần uống thuốc vội. Hãy:
   1. Ăn nhẹ ngay (chuối, bánh mì)
   2. Ngủ ít nhất 7 tiếng tối nay
   3. Nếu sau 2 ngày nghỉ ngơi vẫn đau → cần đi khám"
```

### 9.3 Gamification – Cây tâm hồn

- Mỗi lần viết nhật ký = **"tưới cây"** → cây ảo phát triển
- Nhật ký tích cực (vui, khỏe) → 🌸 Cây xanh tốt, nở hoa
- Nhật ký tiêu cực (stress, ốm) → 🍂 Cây héo, lá vàng
- Không viết → Cây không lớn
- Viết nhiều ngày liên tục → Mở khóa loại cây mới, thành tựu (achievement)
- **Mục đích**: Biến việc theo dõi sức khỏe thành thói quen vui, người dùng mở app mỗi ngày (không chỉ khi ốm)

### 9.4 Chức năng phụ của Soul Garden

**a) Hỗ trợ sức khỏe tinh thần**
- AI phát hiện xu hướng tiêu cực qua chuỗi nhật ký (stress kéo dài, buồn chán, mất ngủ nhiều ngày)
- Đưa ra can thiệp nhẹ: lời khuyên, bài tập thở, gợi ý hoạt động tích cực
- Nếu phát hiện dấu hiệu trầm cảm nghiêm trọng → khuyên gặp chuyên gia tâm lý

**b) Hỗ trợ trí nhớ**
- AI phát hiện dấu hiệu hay quên qua nhật ký (quên hẹn, quên thuốc, quên đồ)
- Tự động bật nhắc nhở thông minh
- Hiển thị ký ức đẹp từ nhật ký cũ → hỗ trợ hồi phục cho người có vấn đề trí nhớ
- Gợi ý kiểm tra sức khỏe nếu quên đột ngột nhiều bất thường

**c) Điều chỉnh trải nghiệm thiết bị**
- Nếu AI biết người dùng bị khó chịu mắt / cận thị → gợi ý điều chỉnh ánh sáng, màu sắc màn hình
- Nếu AI biết người dùng hay thức khuya → bật chế độ Night Shift tự động
- Tùy chỉnh theo bối cảnh sống thực tế

### 9.5 Lưu ý quan trọng

> Soul Garden **KHÔNG chữa bệnh tâm lý**. Soul Garden **hỗ trợ phát hiện sớm** và **cải thiện** bằng các biện pháp nhẹ. Trường hợp nghiêm trọng luôn được khuyên gặp chuyên gia.

---

## 10. MODULE 6: KẾT NỐI YÊU THƯƠNG (CARE CONNECT)

### 10.1 Vấn đề
Người khuyết tật hoặc người già suy giảm trí nhớ thường gặp khó khăn trong việc tự chăm sóc. Người thân muốn hỗ trợ nhưng không thể ở bên cạnh 24/7.

### 10.2 Giải pháp: Dashboard "Quan tâm"
Người thân (con cái, người giám hộ) được cấp quyền truy cập vào một **Dashboard theo dõi sức khỏe** của người dùng chính (bố mẹ, NKT).

**Tính năng chính:**
- **Theo dõi tuân thủ thuốc**: Xem bố mẹ đã uống thuốc chưa? (qua xác nhận trên app hoặc camera).
- **Cảnh báo bất thường**: Nhận thông báo ngay lập tức nếu nhịp tim tăng cao (qua smartwatch nếu có), ngã, hoặc AI triage mức độ "Đỏ".
- **Nhật ký cảm xúc**: Xem tóm tắt tâm trạng từ Soul Garden (Vui/Buồn/Mệt) để gọi điện hỏi thăm đúng lúc.

### 10.3 Câu trả lời cho lo ngại "Ôm đồm"
> **Lưu ý:** Để tránh phức tạp hóa (over-engineering), tính năng này trong giai đoạn đầu chỉ là **Read-only Dashboard** và **Notification**.
> - Không can thiệp vào luồng xử lý của người dùng chính.
> - Chỉ nhận dữ liệu thụ động.
> - Giúp tăng tỷ lệ retention (người thân sẽ nhắc người dùng chính dùng app).

---

## 11. BẢO MẬT & QUYỀN RIÊNG TƯ

### 11.1 Triết lý bảo mật

> **"Dữ liệu sức khỏe là dữ liệu nhạy cảm nhất. Người dùng có quyền kiểm soát tuyệt đối."**

Mỗi chế độ hoạt động (xem Mục 4) có mức bảo mật khác nhau. Dưới đây mô tả chi tiết cơ chế bảo mật cho 2 chế độ chính:

### 11.1.1 Bảo mật Tài khoản & Xác thực 2 bước (MFA)

**Đăng nhập 2 bước BẮT BUỘC:**

```
Bước 1: MẬT KHẨU (thứ bạn BIẾT)
    → Email/SĐT + Mật khẩu (bcrypt hash, ≥ 8 ký tự)

Bước 2: XÁC THỰC DANH TÍNH (chọn 1 trong 3):
    🔹 Sinh trắc [Vân tay / FaceID]    ← KHUYÊN DÙNG, gần như không bị hack
    🔹 OTP SMS + Authenticator (cả 2)   ← Mất SIM vẫn có Auth, mất Auth vẫn có SIM
    🔹 Recovery Key (12 từ)             ← Khẩn cấp, khi mất cả SIM + Auth
```

**So sánh bảo mật Bước 2:**

| Tấn công | OTP | Auth | OTP+Auth | Sinh trắc |
|---|---|---|---|---|
| Hacker có mật khẩu | ⚠️ Cần SIM | ⚠️ Cần ĐT | ⚠️ Cần cả 2 | ✅ **AN TOÀN** |
| Mất SIM | ❌ Nguy hiểm | ✅ An toàn | ✅ An toàn | ✅ An toàn |
| Mất TK Google | ✅ An toàn | ❌ Mất Auth | ✅ An toàn | ✅ An toàn |
| Mất cả SIM + Google | ❌ Kẹt | ❌ Kẹt | ❌ Kẹt | ✅ **VẪN AN TOÀN** |

> **Sinh trắc = "khóa không thể sao chép"** – kẻ trộm không lấy được vân tay/khuôn mặt từ xa.
> **OTP + Auth = "khóa kép"** – phải phá 2 hệ thống khác nhau cùng lúc.

**Session & Token:**
- Access Token (JWT): hết hạn 15 phút, dùng cho API.
- Refresh Token: hết hạn 30 ngày, lưu Keystore/Keychain.
- Đổi IP/vị trí → yêu cầu đăng nhập lại.

**Chống tấn công:**
- Brute-force: 5 lần sai → khóa 15 phút, 10 lần → khóa 24h.
- Token bị lộ: hết hạn nhanh (15 phút) + kiểm tra IP.
- SIM swap: cần xác nhận bằng Authenticator hoặc Recovery Key.
- Session hijacking: HTTPS only + HttpOnly + Secure flags.

**Khôi phục khi mất điện thoại:**
- Recovery Codes: 8 mã dùng 1 lần (ghi ra giấy khi bật 2FA).
- Recovery Key: 12 từ tiếng Việt (dùng chung AI Memory Recovery).
- Email khôi phục: link reset, chờ 24h xác nhận an toàn.

**Quản lý thiết bị:**
- Hybrid/Cloud: tối đa 3 thiết bị, cảnh báo đăng nhập lạ, "Đăng xuất tất cả" khi mất máy.
- Local-Only: 1 thiết bị duy nhất, sinh trắc là chính, Recovery Key khôi phục.

### 11.2 Chế độ Local-Only: BẢO MẬT CỰC ĐOAN

**Mô tả:** Toàn bộ dữ liệu và xử lý AI nằm trên điện thoại. Không có byte dữ liệu nào rời khỏi thiết bị.

**Cách hoạt động:**
```
┌──────────────────────────────────────┐
│          ĐIỆN THOẠI NGƯỜI DÙNG        │
│                                       │
│  ┌─────────────┐  ┌───────────────┐  │
│  │ Local LLM   │  │ Soul Garden   │  │
│  │ (on-device)  │  │ Database      │  │
│  │              │  │ (mã hóa)      │  │
│  └─────────────┘  └───────────────┘  │
│                                       │
│  ┌─────────────────────────────────┐  │
│  │ Medicine DB (offline)           │  │
│  │ OCR Engine (offline)            │  │
│  └─────────────────────────────────┘  │
│                                       │
│  🔒 KHÔNG truyền dữ liệu ra ngoài    │
│  🔒 Mã hóa toàn bộ dữ liệu local    │
│  🔒 Không chia sẻ với app khác        │
└──────────────────────────────────────┘
```

**Chuyển dữ liệu giữa thiết bị:**
- Chỉ cho phép khi **2 thiết bị ở gần nhau** (Bluetooth / NFC / WiFi Direct)
- Không cho phép chuyển qua internet
- Dùng khi đổi điện thoại mới

**Ưu điểm:**
- Bảo mật tuyệt đối, không thể bị hack từ xa
- Không phụ thuộc internet (dùng được ở vùng sâu)

**Nhược điểm:**
- AI kém thông minh hơn (LLM local nhỏ hơn LLM cloud)
- Bất tiện khi đổi thiết bị
- Tốn bộ nhớ điện thoại

### 11.3 Chế độ Hybrid/Cloud: BẢO MẬT ẨN DANH

**Mô tả:** Dùng Cloud LLM mạnh hơn, nhưng Cloud **KHÔNG BIẾT người dùng là ai**.

**Nguyên tắc phân tách dữ liệu:**

```
LOCAL (trên điện thoại):           CLOUD (trên server):
├── Tên thật                        ├── "User_7x8k2" (ID ẩn danh)
├── Số điện thoại                   ├── "Nam, 35 tuổi"
├── Địa chỉ                        ├── "Đau bụng phải dưới, 2 ngày"
├── Ảnh                             ├── "Đang uống Warfarin"
├── Nhật ký Soul Garden             │
├── Lịch sử bệnh đầy đủ            │
├── Danh sách thuốc                 │
└── Mọi thông tin cá nhân           └── CHỈ BIẾT TRIỆU CHỨNG + THUỐC
                                        KHÔNG BIẾT NGƯỜI NÀY LÀ AI
```

**Luồng xử lý:**
```
1. Người dùng hỏi: "Tôi đau đầu quá"
2. App gửi lên Cloud (ẩn danh): "Nam, 35t, đau đầu, 2 ngày"
3. Cloud LLM trả lời: "Có thể do stress/thiếu ngủ. Nên..."
4. Local LLM nhận câu trả lời + đối chiếu Soul Garden
5. Local LLM viết lại: "Anh Minh ơi, 3 ngày deadline liền
   anh ngủ có 4 tiếng. Đau đầu này chắc do thiếu ngủ đó..."
```

**An toàn khi bị rò rỉ:**
- Nếu Cloud bị hack → hacker chỉ thấy: "User ẩn danh, nam, 35t, đau đầu"
- KHÔNG THỂ biết đó là ai, ở đâu, SĐT bao nhiêu
- Dữ liệu vô giá trị cho hacker

**Tùy chọn của người dùng:**
- Bật/tắt Local LLM viết lại (context-aware) bất kỳ lúc nào
- Nếu tắt → câu trả lời giống chatbot thông thường nhưng vẫn chính xác y tế
- Nếu bật → câu trả lời cá nhân hóa sâu

---

## 12. GỢI Ý BỆNH VIỆN & HỆ THỐNG Y TẾ

### 12.1 Khi AI đánh giá cần đi khám

```
AI kết luận: "Triệu chứng của bạn cần được bác sĩ khám trực tiếp"
    ↓
Hiển thị:
┌──────────────────────────────────────┐
│ 🏥 BỆNH VIỆN GẦN BẠN                │
│                                       │
│ 1. BV Quận 7 (2.3km) ⭐ 4.2          │
│    Khoa: Tiêu hóa                     │
│    BHYT: Có hỗ trợ 80%               │
│    Giờ khám: 7:00 - 16:00             │
│    💡 Nên đi trước 7h để lấy số nhanh │
│                                       │
│ 2. BV Nguyễn Tất Thành (4.1km)       │
│    ...                                │
│                                       │
│ [📞 Gọi BV]  [🗺️ Chỉ đường]          │
│ [👨‍👩‍👧 Gọi người thân đưa đi]           │
└──────────────────────────────────────┘
```

### 11.2 Chia sẻ hồ sơ cho bác sĩ

- Trước khi đi khám, người dùng có thể tạo **bản tóm tắt** triệu chứng + lịch sử từ app
- Gửi cho bác sĩ qua QR code hoặc link (người dùng chủ động chia sẻ)
- Giúp bác sĩ hiểu nhanh tình trạng, tiết kiệm thời gian khám

---

## 13. MÔ HÌNH KINH DOANH

### 12.1 Thách thức đạo đức

> **Vấn đề**: MediSign AI phục vụ chủ yếu người yếu thế (người nghèo, NKT, người già). Thu phí từ họ → mâu thuẫn với sứ mệnh nhân đạo. Nhưng không thu phí → không tồn tại.

### 12.2 Chiến lược: "Miễn phí cho người cần, thu phí từ người hưởng lợi gián tiếp"

**a) Tầng Free (Mãi mãi miễn phí):**
- Tư vấn triệu chứng cơ bản
- Quét thuốc (5 lần/ngày)
- Nhắc uống thuốc
- Giao diện NKT / người già
- Soul Garden cơ bản

→ **Người nghèo, NKT, người già dùng FREE trọn đời**

**b) Tầng Premium – MediSign Plus (49.000 VNĐ/tháng):**
- Không giới hạn quét thuốc
- AI tư vấn chuyên sâu hơn (dùng Cloud LLM mạnh)
- Soul Garden đầy đủ (phân tích tâm lý sâu, nhiều loại cây)
- Theo dõi sức khỏe gia đình (tối đa 5 người)
- Ưu tiên hỗ trợ
- **Người dùng**: người có thu nhập, quan tâm sức khỏe gia đình

→ **Logic**: Người con mua Premium để theo dõi sức khỏe bố mẹ già → **Con trả tiền, bố mẹ dùng free**

**c) Tầng Family – MediSign Family (99.000 VNĐ/tháng):**
- Tất cả tính năng Premium
- Kết nối gia đình: con xem được tình trạng sức khỏe bố mẹ từ xa
- Nhận thông báo khi bố mẹ có triệu chứng đáng lo
- Dashboard sức khỏe gia đình

→ **Logic**: Người đi làm xa quê muốn biết bố mẹ ở quê có khỏe không

**d) B2B – Bệnh viện, Phòng khám & Nhà thuốc:**
- **Nhà thuốc:** Sử dụng MediSign như công cụ giao tiếp với khách hàng khiếm thính/người già (phiên dịch viên AI). Dùng làm công cụ Triage (sàng lọc) để tư vấn thuốc chính xác hơn hoặc giảm tải hàng đợi.
- **Bệnh viện:** Tích hợp hệ thống tiếp nhận NKT. Nhận hồ sơ bệnh nhân từ MediSign trước khi khám.

**e) B2G – Chính phủ & Sở Y tế:**
- Triển khai MediSign cho trạm y tế tuyến xã
- Chương trình sàng lọc sức khỏe cộng đồng
- Hợp đồng với Hội Người Khuyết Tật các tỉnh

**f) NGO – Tổ chức quốc tế:**
- Tài trợ từ WHO, UNICEF, USAID cho dự án hỗ trợ NKT tiếp cận y tế
- Báo cáo impact hàng quý

**g) Data Analytics (ẩn danh hoàn toàn):**
- Bản đồ sức khỏe cộng đồng ẩn danh: vùng nào đang có nhiều ca sốt, tiêu chảy...
- Bán cho Sở Y tế, CDC để phòng dịch sớm
- KHÔNG bao giờ bán dữ liệu cá nhân

### 12.3 Thị trường mục tiêu

| Phân khúc | TAM | SAM | SOM (năm 1) |
|-----------|-----|-----|-------------|
| Người dùng cá nhân VN | 70 triệu người internet | 10 triệu quan tâm SK | 50.000 users |
| NKT | 6.2 triệu | 2 triệu có smartphone | 10.000 users |
| Người cao tuổi | 12 triệu | 3 triệu có smartphone | 20.000 users |
| Bệnh viện/PK | 1.400 BV | 200 BV top | 5 BV pilot |

---

## 14. SO SÁNH CẠNH TRANH

| Tiêu chí | ChatGPT Health | Google Health | Ada Health | **MediSign AI** |
|----------|---------------|--------------|------------|-----------------|
| Tư vấn triệu chứng | ✅ Giỏi | ✅ Giỏi | ✅ Tốt | ✅ Đủ tốt (dùng Gemini API) |
| Tiếng Việt native | ⚠️ Dịch | ⚠️ Dịch | ❌ T.Anh | ✅ Tiếng Việt 100% |
| Hiểu bối cảnh người dùng | ❌ Hỏi lần nào biết lần đó | ❌ | ❌ | ✅ Soul Garden |
| Ngôn ngữ ký hiệu VN | ❌ | ❌ | ❌ | ✅ Model 3D + Camera |
| Giao diện người mù chữ | ❌ | ❌ | ❌ | ✅ Chạm hình |
| Voice-only cho người già | ❌ | ⚠️ Google Assistant | ❌ | ✅ Wake word "Bác sĩ ơi" |
| Quét thuốc camera | ❌ | ❌ | ❌ | ✅ OCR + DB Cục Dược |
| Kiểm tra tương tác thuốc | ❌ | ⚠️ Chung | ❌ | ✅ DB thuốc VN |
| Gợi ý BV + BHYT + khoa | ❌ | ⚠️ Maps | ❌ | ✅ Chi tiết |
| Bảo mật local-only | ❌ | ❌ | ❌ | ✅ LLM on-device |
| Giá | $20/tháng | Free hạn chế | $10/tháng | ✅ Free cơ bản |
| Gamification | ❌ | ❌ | ❌ | ✅ Cây tâm hồn |

**Tóm lại:** MediSign AI không cạnh tranh về chất lượng AI thuần túy. MediSign AI thắng ở **accessibility**, **localization Việt Nam**, **hiểu người dùng qua Soul Garden**, và **bảo mật**.

---

## 15. DỮ LIỆU CẦN THU THẬP & CHỨNG THỰC

### 15.1 Trước khi thi (tạo bằng chứng thuyết phục)

| Dữ liệu | Cách thu thập | Mục đích |
|----------|-------------|----------|
| Khảo sát nhu cầu | Google Form cho 100-500 SV + người thân NKT | Chứng minh nhu cầu thật |
| Phỏng vấn NKT | Liên hệ Hội NKT quận/TP, phỏng vấn 5-10 người | Câu chuyện thật, xúc động |
| Số liệu y tế VN | Bộ Y tế, WHO, TCTK (nguồn chính thống) | Chứng minh vấn đề lớn |
| Test prototype | Cho 20-30 người dùng thử MVP | Feedback thực tế |
| Ý kiến chuyên gia | Phỏng vấn 1-2 bác sĩ/dược sĩ về tính khả thi | Uy tín chuyên môn |

### 14.2 Sau khi launch (đo lường hiệu quả)

| KPI | Cách đo | Mục tiêu năm 1 |
|-----|---------|----------------|
| Số người dùng | Analytics | 50.000+ |
| % user quyết định đúng (đi BV / không đi) | Khảo sát follow-up | >70% hài lòng |
| Số lần quét thuốc | Tracking | 100.000+ lượt/tháng |
| % NKT dùng được app | Usability test | >80% hoàn thành luồng |
| Thời gian viết nhật ký / ngày | Analytics | Trung bình >1 phút |
| Retention D7 / D30 | Analytics | D7 >40%, D30 >20% |

### 14.3 Số liệu tham khảo từ sản phẩm tương tự (để dùng trong bài thi)

- **Babylon Health (Anh)**: AI triage giảm 25% lượt khám không cần thiết (nguồn: NHS report 2019)
- **Ada Health (Đức)**: 88% độ chính xác triage so với bác sĩ (nguồn: Ada Health published study)
- **K Health (Mỹ)**: Tiết kiệm trung bình $100/người/năm chi phí y tế

---

## 16. HẠN CHẾ & GIỚI HẠN

### 16.1 Hạn chế kỹ thuật
- AI có thể sai → luôn khuyến cáo đi khám bác sĩ
- Sign language recognition chưa hoàn hảo → cần cải thiện liên tục
- Local LLM kém hơn Cloud LLM → chế độ Local-only bị giới hạn
- Cần internet cho chế độ Cloud (trừ quét thuốc offline)

### 15.2 Hạn chế đạo đức & pháp lý
- App KHÔNG chẩn đoán bệnh, KHÔNG kê đơn thuốc
- Chỉ là trợ lý sàng lọc, tham khảo
- Cần disclaimer rõ ràng mỗi lần tư vấn
- Tuân thủ Nghị định 13/2023 về bảo vệ dữ liệu cá nhân

### 15.3 Hạn chế đối tượng
- Không hỗ trợ được người vừa câm + điếc + mù
- Người già rất lớn tuổi vẫn cần người thân hỗ trợ ban đầu
- Vùng không có internet → chỉ dùng được tính năng offline cơ bản

---

## 17. KẾ HOẠCH TRAINING AI - CHIẾN LƯỢC ĐẠT 85%+ ACCURACY

### 17.1 Tổng Quan Mục Tiêu

| Chỉ tiêu | Giá trị mục tiêu | Ghi chú |
|-----------|-------------------|----------|
| **Accuracy** | ≥85% | Trên benchmark MedQuAD |
| **F1-Score** | ≥80% | Precision & Recall |
| **Red Flag Detection** | ≥95% | Phát hiện triệu chứng nguy hiểm |
| **Vietnamese** | 100% | Ngôn ngữ tự nhiên |

### 17.2 Phương Pháp Tiếp Cận

#### Tại Sao Không Dùng Pure LLM?

```
┌─────────────────────────────────────────────────────────────────────┐
│  LLM THUẦN TÚY KHÔNG ĐẠT 85% ACCURACY                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  • Sinh text dựa trên xác suất → có thể hallucinate              │
│  • Không có "confidence score" chính xác                          │
│  • Không đảm bảo factual correctness                             │
│  • Accuracy chỉ đạt 55-70%                                        │
│                                                                     │
│  → CẦN KẾT HỢP VỚI RULE-BASED LAYER                            │
└─────────────────────────────────────────────────────────────────────┘
```

#### Giải Pháp: Hybrid Medical Engine

```
┌─────────────────────────────────────────────────────────────────────┐
│              HYBRID MEDICAL ENGINE                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  USER INPUT → ┌─────────────────┐                                  │
│               │  LLM (Qwen 72B) │ ← MedQuAD + ChatDoctor        │
│               │  + Medical LoRA  │   (Language Generation)         │
│               └────────┬────────┘                                  │
│                        │                                           │
│                        ▼                                           │
│               ┌─────────────────┐                                  │
│               │ Symptom-Disease │ ← Disease-Symptom, SympScan    │
│               │ Logic Layer     │   (Safety Check)               │
│               └────────┬────────┘                                  │
│                        │                                           │
│                        ▼                                           │
│               ┌─────────────────┐                                  │
│               │  Safety Layer  │ ← Warning, Red Flag            │
│               │  + Disclaimer   │                                 │
│               └────────┬────────┘                                  │
│                        │                                           │
│                        ▼                                           │
│                    RESPONSE                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 17.3 Nguồn Dữ Liệu Training

#### Dữ Liệu Cho LLM (Language Generation)

| Nguồn | Số lượng | Mục đích |
|-------|----------|-----------|
| **MedQuAD** | 47,000 Q&A | Medical Q&A benchmark |
| **ChatDoctor** | 100,000 dialogues | Hội thoại bệnh nhân-bác sĩ |
| **Dược thư VN** | 30,000 thuốc | Thuốc VN, tương tác |
| **Tự tạo (VN)** | 5,000-10,000 | Q&A tiếng Việt |

#### Dữ Liệu Cho Logic Layer (Rule-Based)

| Nguồn | Số lượng | Mục đích |
|-------|----------|-----------|
| **Disease-Symptom** | 500+ bệnh | Mapping triệu chứng-bệnh |
| **SympScan** | 2000+ triệu chứng | Logic check |
| **ICD-10 Vietnam** | 500+ codes | Standard codes |

### 17.4 Kiến Trúc Training

#### Bước 1: Fine-tune LLM

```
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1: FINE-TUNE QWEN 72B                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Model: Qwen/Qwen2.5-VL-72B-Instruct (Vision-Language)            │
│  Method: LoRA (Low-Rank Adaptation)                               │
│  Target: Medical domain                                            │
│  Data: MedQuAD + ChatDoctor (translate to VN)                    │
│  Time: 8-12 giờ (A100 80GB)                                      │
│  Expected Accuracy: 70-80%                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### Bước 2: Implement RAG

```
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: RAG - RETRIEVAL-AUGMENTED GENERATION                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Medical Knowledge Base (10,000+ facts)                         │
│  2. Vector DB (FAISS/Chroma)                                      │
│  3. Retrieve relevant context → Inject vào prompt                 │
│  4. Generate với grounding                                        │
│                                                                     │
│  Expected Accuracy: +10-15% → 80-88%                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### Bước 3: Logic Layer

```
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: SYMPTOM-DISEASE LOGIC LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Parse symptoms → Map to disease probabilities                 │
│  2. Calculate confidence scores                                    │
│  3. Check red flags (đau ngực, khó thở, chảy máu...)           │
│  4. Drug interaction check                                        │
│                                                                     │
│  Expected: Đảm bảo 85%+ accuracy                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 17.5 Evaluation Methodology

#### Test Protocol

```
┌─────────────────────────────────────────────────────────────────────┐
│  EVALUATION PROTOCOL                                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Test Set: MedQuAD test split (10% = ~4,700 questions)        │
│                                                                     │
│  2. Metrics:                                                      │
│     ├── Accuracy = (Correct / Total) × 100                        │
│     ├── Precision = TP / (TP + FP)                               │
│     ├── Recall = TP / (TP + FN)                                  │
│     └── F1-Score = 2×(P×R)/(P+R)                               │
│                                                                     │
│  3. Benchmark Comparison:                                          │
│     ├── Med-PaLM 2: 86%                                         │
│     ├── MedAlpaca-13B: 72%                                      │
│     ├── GPT-3.5: 60%                                            │
│     └── Our Target: 85%+                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 17.6 So Sánh Với Các Hệ Thống AI Y Tế

| AI | Accuracy | Ưu điểm | Nhược điểm |
|----|----------|----------|-------------|
| **MediSign (85%+)** | 85% | VN native, self-hosted | Mới |
| Med-PaLM 2 | 86% | Research state-of-art | Không public |
| Ada Health | 80% | Nổi tiếng | Tiếng Anh |
| Babylon | 75% | UK NHS partner | Hạn chế VN |
| K Health | 75% | Telehealth integration | Paid only |

### 17.7 Lộ Trình Triển Khai

| Phase | Nhiệm vụ | Thời gian | Accuracy target |
|-------|----------|-----------|-----------------|
| 1 | Fine-tune Qwen 72B + MedQuAD | 2 tuần | 70-80% |
| 2 | Implement RAG | 1 tuần | 80-85% |
| 3 | Add Symptom-Disease DB | 1 tuần | 85%+ |
| 4 | Evaluation & Testing | 1 tuần | 85%+ |

### 17.8 Giới Hạn & Disclaimer

```
┌─────────────────────────────────────────────────────────────────────┐
│  ⚠️  GIỚI HẠN CỦA HỆ THỐNG                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  • AI chỉ HỖ TRỢ, KHÔNG thay thế bác sĩ                          │
│  • Luôn có disclaimer: "Không thay thế chẩn đoán y khoa"        │
│  • Red flags → khuyến khích khám bác sĩ                          │
│  • Cần xét nghiệm để chẩn đoán chính xác                        │
│  • Đây là QA accuracy benchmark, không phải clinical diagnosis     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

> **Tài liệu này là nền tảng để phát triển Design Document và Technical Tasks tiếp theo.**
