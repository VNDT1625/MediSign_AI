# MediSign AI — Báo cáo Kế hoạch RAG + Diagnostic Chat
> **Phiên bản:** 2.0 | **Ngày:** 2026 | **Dự án:** Nghiên cứu Khoa học Sinh viên — Trường ĐH Nguyễn Tất Thành

---

## Mục lục

1. [Tổng quan triết lý](#1-tổng-quan-triết-lý)
2. [Kiến trúc tổng thể](#2-kiến-trúc-tổng-thể)
3. [Flow Diagnostic Chat](#3-flow-diagnostic-chat)
4. [Chi tiết RAG #1 #2 #3](#4-chi-tiết-rag-1-2-3)
5. [Kỹ thuật RAG tổng hợp](#5-kỹ-thuật-rag-tổng-hợp)
6. [Format Output](#6-format-output)
7. [Tóm tắt nhanh — Quick Summary Widget](#7-tóm-tắt-nhanh--quick-summary-widget)
8. [Data Plan](#8-data-plan)
9. [Training Plan](#9-training-plan)
10. [Chat Memory](#10-chat-memory)
11. [Lộ trình Implement](#11-lộ-trình-implement)
12. [So sánh chuẩn quốc tế](#12-so-sánh-chuẩn-quốc-tế)

---

## 1. Tổng quan triết lý

### RAG-first, LLM-second
- Hệ thống tìm kiếm tài liệu là **trung tâm**, LLM chỉ tổng hợp và diễn đạt
- LLM không tự "biết" bệnh — hoàn toàn dựa vào RAG kéo ra
- Merge AI + RAG để không bỏ sót bệnh ngoài data

### Mục đích cuối
> Không phải đoán bệnh, mà là **xác định mức độ nguy hiểm** → người dùng có nên đi khám không

```
Xanh  — Bệnh nhẹ, tự điều trị tại nhà
Vàng  — Theo dõi, đi khám nếu nặng hơn
Đỏ    — Nguy hiểm, đi khám ngay
```

### Nguyên tắc OARS (Motivational Interviewing)
```
O — Open question      : Câu hỏi mở, không dẫn dắt
A — Affirmation        : Ghi nhận những gì user đã chia sẻ
R — Reflective listen  : Phản chiếu lại để xác nhận hiểu đúng
S — Summary            : Tóm tắt trước khi hỏi câu tiếp theo
```

---

## 2. Kiến trúc tổng thể

```
┌─────────────────────────────────────────────────────────┐
│                     User Interface                       │
│           Flutter App / Next.js Web                      │
│    ┌─────────────────────────────────────┐               │
│    │     Quick Summary Widget            │               │
│    │  • Triệu chứng đã ghi nhận          │               │
│    │  • Đánh giá sơ bộ                   │               │
│    │  • Khuyến nghị                      │               │
│    └─────────────────────────────────────┘               │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   FastAPI Backend                        │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Chat Memory │  │  RAG Engine  │  │   Diagnostic   │  │
│  │  DB Session │  │  #1 #2 #3    │  │  State Manager │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│             MedGemma 4B Runtime (H100)                   │
│        /v1/chat/completions (OpenAI-compatible)          │
│  ├── Adapter: medisign-medgemma-medical                  │
│  └── Adapter: medisign-medgemma-psychology               │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   Knowledge Base                         │
│  ├── 1,000 bệnh phổ biến (có triệu chứng đầy đủ)        │
│  ├── 60,472 records thuốc DAV                            │
│  ├── 67,493 records tương tác thuốc                      │
│  └── ICD-10 14,000 bệnh (fallback + lazy load)          │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Flow Diagnostic Chat

```
User nhập triệu chứng
        │
        ▼
┌───────────────────┐
│  Personal Context │  ← nếu user cho phép
│  • Nhật ký        │
│  • Tủ thuốc       │
│  • Bệnh nền       │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐       ┌──────────────────┐
│     RAG #1        │  +    │  AI nhận định    │
│  Kéo bệnh liên   │       │  (training know) │
│  quan             │       └────────┬─────────┘
└────────┬──────────┘                │
         └──────────────┬────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │  MERGE kết quả  │
              │  Ranking % bệnh │
              └────────┬────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  Chưa đủ thông tin kết luận  │
        │  + % bệnh sơ bộ              │
        │  + Hỏi: muốn hỏi thêm không?│
        └──────────────┬───────────────┘
                       │ User đồng ý
                       ▼
        ┌──────────────────────────────┐
        │          RAG #2              │
        │  Sinh câu hỏi loại trừ       │
        │  → AI OARS hóa → Hỏi user   │
        │  → Cập nhật % → Loại dần    │
        └──────────────┬───────────────┘
                       │
              Đủ thông tin?
             ╱            ╲
           Có               Không
            │                  │
  ┌─────────▼──────┐  ┌────────▼──────────────┐
  │    RAG #3      │  │  Yêu cầu xét nghiệm   │
  │  Kéo thông tin │  │  hoặc đi khám         │
  │  kết quả cuối  │  └───────────────────────┘
  └─────────┬──────┘
            │
            ▼
  ┌──────────────────┐
  │  AI Self-check   │
  └─────────┬────────┘
            │
            ▼
  ┌──────────────────────────────────┐
  │          KẾT QUẢ CUỐI           │
  │  % bệnh + Xanh/Vàng/Đỏ          │
  │  + Miễn trừ trách nhiệm         │
  └─────────────────┬────────────────┘
                    │
                    ▼
  ┌──────────────────────────────────┐
  │     Lưu vào Chat Session DB      │
  │  → Cập nhật Quick Summary Widget │
  └──────────────────────────────────┘
```

---

## 4. Chi tiết RAG #1 #2 #3

### RAG #1 — Kéo bệnh ban đầu

```
User: "sốt + đau họng"
        ↓
[Query Rewriting]
  "sốt đau họng" → "fever sore throat viêm họng nhiệt độ cao"
        ↓
[Hybrid Retrieval] — BM25 + Embedding song song
  BM25     : tìm khớp từ khóa (chính xác tên thuốc/bệnh)
  Embedding: tìm theo ngữ nghĩa ("nóng người" = "sốt")
        ↓
[Personal Context] — nếu user cho phép
        ↓
[Re-ranking]
  Chấm điểm lại có tính trọng số Personal Context
        ↓
Kết quả: [viêm họng 85%, cúm 70%, COVID 60%...]
```

**Ảnh hưởng Personal Context:**

| Thông tin có | Tác động lên kết quả |
|---|---|
| Đang dùng kháng sinh | Hạ % viêm họng vi khuẩn, tăng % kháng thuốc |
| Có tiểu đường | Tăng % nhiễm trùng cơ hội |
| Từng bị cúm tháng trước | Tăng % tái nhiễm hoặc biến chứng |
| Nhật ký: mệt 1 tuần | Gợi ý bệnh mạn tính hơn bệnh cấp |

---

### RAG #2 — Sinh câu hỏi loại trừ

```
Input: toàn bộ bệnh đã merge (RAG + AI)
        ↓
[Graph Traversal]
  Leo đồ thị: bệnh → triệu chứng đặc trưng → điểm khác biệt
  Ví dụ: viêm họng vs cúm → cúm có đau cơ, viêm họng không
        ↓
[Context Compression]
  Chỉ giữ "điểm phân biệt", bỏ thông tin trùng
        ↓
RAG sinh câu hỏi loại trừ tốt nhất
        ↓
[AI — OARS Layer]
  Biến câu hỏi kỹ thuật → câu hỏi tự nhiên kiểu bác sĩ
        ↓
Hỏi user 1-5 câu → Thu thập → Cập nhật % → Loại dần
```

**Nguyên tắc loại trừ:**
- Không loại bệnh hoàn toàn — chỉ đặt % thấp hơn
- Bệnh thường gặp ưu tiên hỏi trước
- Nếu hỏi đủ mà không kết luận → yêu cầu xét nghiệm

---

### RAG #3 — Kéo thông tin kết quả

```
Input: bệnh còn lại sau loại trừ
        ↓
[Hybrid Retrieval]
  Kéo: mức độ nguy hiểm, xét nghiệm cần, biến chứng
  Kéo: biện pháp tại nhà nếu bệnh nhẹ
        ↓
[AI Self-check]
  Kiểm tra: context đủ kết luận chưa?
  Kiểm tra: có mâu thuẫn giữa triệu chứng và kết luận?
        ↓
Kết quả cuối + Miễn trừ trách nhiệm
```

---

## 5. Kỹ thuật RAG tổng hợp

| Kỹ thuật | RAG #1 | RAG #2 | RAG #3 | Mục đích |
|---|:---:|:---:|:---:|---|
| Query Rewriting | ✅ | | | Làm rõ câu hỏi, thêm từ đồng nghĩa |
| BM25 | ✅ | | ✅ | Tìm khớp từ khóa chính xác |
| Embedding (Semantic) | ✅ | | ✅ | Tìm theo ngữ nghĩa |
| Personal Context | ✅ | | | Cá nhân hóa theo lịch sử user |
| Re-ranking | ✅ | | | Chấm điểm lại có trọng số |
| Graph Traversal | | ✅ | | Leo đồ thị bệnh-triệu chứng |
| Context Compression | | ✅ | | Giữ điểm khác biệt, bỏ trùng |
| Self-check | | | ✅ | AI tự kiểm tra kết luận |

---

## 6. Format Output

### Giữa chừng — Chưa đủ thông tin
```
Tôi chưa đủ thông tin để kết luận.
Hiện tại có thể là:
• Viêm họng virus (70%)
• Cúm mùa (40%)
• COVID-19 (25%)

Cho tôi hỏi thêm để chính xác hơn nhé?
```

### Kết luận cuối — 3 trường hợp

**Trường hợp 1: Không kết luận được**
```
Tôi chưa đủ thông tin để kết luận chính xác.
Hiện tại có thể là:
• Viêm họng virus (60%)
• Cúm mùa (35%)

Bạn nên thực hiện xét nghiệm: [xét nghiệm cụ thể]
và đến gặp bác sĩ để được khám trực tiếp.

⚠️ Tôi không thể thay thế bác sĩ.
```

**Trường hợp 2: Nhiều bệnh, có bệnh nặng**
```
Kết luận:
• Viêm phổi (65%) 🔴
• Viêm phế quản (40%) 🟡

Mức độ: ĐỎ
⚠️ Bạn có khả năng mắc bệnh nguy hiểm,
hãy đi khám bác sĩ ngay.
Tôi không thể thay thế bác sĩ.
```

**Trường hợp 3: Kết luận rõ, bệnh nhẹ**
```
Kết luận:
• Viêm họng virus (80%) 🟢
• Cúm nhẹ (30%) 🟢

Mức độ: XANH
Khuyến nghị: Nghỉ ngơi, uống nước ấm,
súc họng. Theo dõi thêm 1-2 ngày.

⚠️ Tôi không thể thay thế bác sĩ.
```

---

## 7. Tóm tắt nhanh — Quick Summary Widget

Widget hiển thị trên UI sau mỗi phiên chat, lấy dữ liệu từ **Chat Session DB**.

```
┌─────────────────────────────┐
│  Tóm tắt nhanh          ▲  │
├─────────────────────────────┤
│  Triệu chứng                │
│  Đau họng, ho khan,         │
│  sốt nhẹ 37.8°C, mệt nhẹ   │
├─────────────────────────────┤
│  Đánh giá sơ bộ             │
│  Khả năng cao là viêm       │
│  họng do virus              │
├─────────────────────────────┤
│  Khuyến nghị                │
│  Nghỉ ngơi, uống nước ấm,   │
│  súc họng.                  │
│  Theo dõi thêm 1-2 ngày.    │
├─────────────────────────────┤
│       [Xem chi tiết]        │
└─────────────────────────────┘
```

**Dữ liệu lưu trong session:**

```json
{
  "session_id": "uuid",
  "symptoms_collected": ["đau họng", "ho khan", "sốt 37.8°C"],
  "diseases_ranked": [
    {"name": "Viêm họng virus", "probability": 80, "level": "green"},
    {"name": "Cúm nhẹ", "probability": 30, "level": "green"}
  ],
  "questions_asked": ["Bạn có ho không?", "Sốt bao nhiêu độ?"],
  "recommendation": "Nghỉ ngơi, uống nước ấm, súc họng.",
  "triage_level": "green",
  "timestamp": "2026-01-01T10:00:00Z"
}
```

---

## 8. Data Plan

### Knowledge Base cho RAG

| Nguồn | Records | Trạng thái | Cách lấy |
|---|---|---|---|
| Thuốc DAV | 60,472 | ✅ Có sẵn | — |
| Tương tác thuốc | 67,493 | ✅ Có sẵn (cần clean) | — |
| 1,000 bệnh phổ biến | ~1,000 | 🔜 Cần crawl | Vinmec + Hello Bacsi |
| ICD-10 tiếng Việt | 14,000 | 🔜 Cần tải | GitHub + icd.kcb.vn |
| Dinh dưỡng | 38 | ✅ Có sẵn | — |
| Guideline BYT | 356 chunks | ✅ Có sẵn | — |

### Lazy Loading cho bệnh hiếm

```
User hỏi bệnh ngoài 1,000 bệnh phổ biến
        ↓
Tra ICD-10 → lấy tên chuẩn
        ↓
MedGemma search Google → bổ sung thông tin
        ↓
Lưu vào DB (lần sau không cần search nữa)
        ↓
DB tự lớn dần theo thực tế người dùng hỏi
```

### Pipeline crawl data bệnh

```
Claude Code 1: crawl Vinmec + Hello Bacsi
  → ~500-1,000 bệnh có triệu chứng đầy đủ
  → Output: diseases_vinmec.json
             diseases_hellobacsi.json

Claude Code 2: tải ICD-10 từ GitHub/icd.kcb.vn
  → 14,000 bệnh (tên chuẩn + mã ICD)
  → Output: icd10_vi.json

Merge:
  ICD-10 (tên chuẩn) + Vinmec/Hello Bacsi (triệu chứng)
  → knowledge_base_diseases.json
```

### Ước tính thời gian data pipeline

| Bước | Thời gian |
|---|---|
| Crawl Vinmec + Hello Bacsi | 1-3 ngày |
| Tải + xử lý ICD-10 | 0.5 ngày |
| Merge + clean data | 1 ngày |
| Build knowledge base | 0.5 ngày |
| **Tổng** | **3-5 ngày** |

---

## 9. Training Plan

### Tổng quan 3 bước train

```
MedGemma 4B Base Model
        ↓
[Bước 1] Medical QA — 15.693 samples
  Y tế tiếng Việt + Diagnostic reasoning
        ↓
[Bước 2] OARS Conversation — 1.201 samples
  Hỏi đúng kiểu bác sĩ (DeepSeek-regenerated, 20 chủ đề OARS)
        ↓
[Bước 3] Output Format — 500-1.000 samples
  % + Xanh/Vàng/Đỏ + Multi-turn >3 lượt
  + Miễn trừ trách nhiệm
        ↓
MediSign MedGemma 4B Medical Adapter v2
```

### Chi tiết từng bước

**Bước 1 — Medical QA (đã có)**

| Thông số | Giá trị |
|---|---|
| Số samples | 15.693 train / 2.770 eval |
| Nguồn | Corpus y tế VN + dịch từ tiếng Trung |
| Mục đích | Y tế tiếng Việt + reasoning bệnh |
| Trạng thái | ✅ Sẵn sàng train |

**Bước 2 — OARS Conversation**

| Thông số | Giá trị |
|---|---|
| Số samples | 1.201 train / 212 eval |
| Nguồn | Sinh bằng DeepSeek/FPT Cloud (`scripts/regenerate_psychology_data.py`), 20 chủ đề × 30+ persona, dedup giữa workers |
| Mục đích | Pattern hỏi lại kiểu bác sĩ theo OARS (Open / Affirm / Reflect / Summary) |
| Trạng thái | ✅ Sẵn sàng train |

Format mẫu:
```json
{
  "messages": [
    {"role": "user", "content": "tôi bị sốt và đau họng 2 ngày"},
    {"role": "assistant", "content": "Cảm ơn bạn đã chia sẻ. Bạn có ho không, và nếu có thì ho khan hay có đờm?"},
    {"role": "user", "content": "có ho khan nhẹ"},
    {"role": "assistant", "content": "Tôi ghi nhận rồi. Sốt bao nhiêu độ và bắt đầu từ khi nào?"}
  ]
}
```

**Bước 3 — Output Format**

| Thông số | Giá trị |
|---|---|
| Số samples | ~500-1,000 |
| Nguồn | Sinh từ 1,000 bệnh có sẵn |
| Mục đích | Format % + Xanh/Vàng/Đỏ + disclaimer |
| Yêu cầu | Multi-turn >3 lượt, có safety format |

Format output bắt buộc trong training data:
```
Chưa đủ thông tin:
  → % sơ bộ → xin hỏi thêm (không có disclaimer)

Kết luận cuối:
  → % bệnh + mức độ Xanh/Vàng/Đỏ
  → ⚠️ Tôi không thể thay thế bác sĩ
  → Hoặc nếu nguy hiểm:
     ⚠️ Bạn có khả năng mắc bệnh nguy hiểm, hãy đi khám ngay
     Tôi không thể thay thế bác sĩ
```

### Ước tính thời gian train (H100)

| Bước | Samples | Thời gian |
|---|---|---|
| Bước 1 (Medical) | 15.693 | ~1-1,5 giờ (3 epochs, r=16) |
| Bước 2 (Psychology / OARS) | 1.201 | ~30 phút (5 epochs, r=16) |
| Bước 3 (Output Format) | ~500-1.000 | ~10-15 phút |
| **Tổng** | **~17.500** | **~2-2,5 giờ** |

---

## 10. Chat Memory

### Schema DB cần thêm

> **Trạng thái:** đã hiện thực. Bảng `chat_conversations` và `chat_messages` đã có
> trong `app/database/cloud_models.py`; cùng các bảng meta phục vụ vòng đời tri thức
> (`kb_pending_records`, `disease_symptom_edges`, `kb_embeddings`,
> `weight_update_proposals`, `diagnosis_feedback`).

```sql
-- Bảng quản lý cuộc hội thoại
CREATE TABLE chat_conversations (
  id          UUID PRIMARY KEY,
  user_id     UUID REFERENCES users(id),
  title       VARCHAR(255),
  adapter     VARCHAR(50),   -- medical / psychology
  phase       VARCHAR(50),   -- initial / questioning / result
  created_at  TIMESTAMP,
  updated_at  TIMESTAMP
);

-- Bảng lưu từng tin nhắn
CREATE TABLE chat_messages (
  id                UUID PRIMARY KEY,
  conversation_id   UUID REFERENCES chat_conversations(id),
  role              VARCHAR(20),   -- user / assistant
  content           TEXT,
  metadata          JSONB,         -- diagnosis_state, % bệnh...
  created_at        TIMESTAMP
);
```

### Diagnostic State (lưu trong metadata)

```json
{
  "diagnosis_state": {
    "diseases_ranked": [
      {"name": "Viêm họng virus", "probability": 75},
      {"name": "Cúm mùa", "probability": 40}
    ],
    "eliminated": [
      {"name": "COVID-19", "probability": 10,
       "reason": "không có mất vị giác"}
    ],
    "symptoms_collected": ["sốt 38.5°C", "đau họng", "ho khan"],
    "questions_asked": ["Bạn có ho không?", "Sốt bao nhiêu độ?"],
    "phase": "questioning",
    "turn_count": 3
  }
}
```

### Thay đổi `/api/v1/ai/chat`

> **Trạng thái:** đã triển khai xong. Endpoint hỗ trợ cả JSON và `multipart/form-data`,
> nhận `conversation_id` để vào multi-turn diagnostic flow (yêu cầu auth) hoặc bỏ trống
> để giữ luồng single-shot cũ.

```python
# Schema cũ
class AIChatRequest:
    message: str
    adapter: str
    use_rag: bool
    rag_top_k: int

# Schema mới — đã có trong app/schemas/ai.py
class AIChatRequest:
    message: str
    system_prompt: str | None = None
    adapter: str = "medical"
    use_rag: bool = True
    rag_top_k: int = 5
    conversation_id: str | None = None       # MỚI — multi-turn
    use_personal_context: bool = False        # MỚI — yêu cầu consent
    image: bytes | None = None                # MỚI — multimodal (xray / dermatology)
    image_type: Literal["xray", "dermatology"] | None = None
```

---

## 11. Lộ trình Implement

| Phase | Việc cần làm | Ước tính |
|---|---|---|
| **Phase 1** Chat Memory | Tạo bảng DB, sửa /ai/chat, lưu diagnostic_state | 2-3 ngày |
| **Phase 2** Data Pipeline | Crawl Vinmec + Hello Bacsi, tải ICD-10, merge | 3-5 ngày |
| **Phase 3** RAG Nâng cấp | Thêm Embedding, Hybrid search, Graph index, RAG #2 logic | 5-7 ngày |
| **Phase 4** Training | Sinh OARS + format samples, train Bước 2+3, eval | 3-5 ngày |
| **Phase 5** OARS + Personal + Widget | OARS prompt, personal context, consent, Quick Summary UI | 3-4 ngày |
| **Tổng** | | **~3-4 tuần** |

---

## 12. So sánh chuẩn quốc tế

| Tiêu chí | Chuẩn quốc tế | MediSign (plan này) | Đánh giá |
|---|---|---|---|
| Retrieval | 1 lần, Hybrid | 3 lần, đúng ngữ cảnh | ✅ Vượt |
| AI role | Chỉ tổng hợp | Nhận định + merge + self-check | ✅ Vượt |
| Multi-turn | Có nhưng ít | Có + user chủ động chọn | ✅ Vượt |
| Loại trừ bệnh | Không có | Có, theo % không loại hẳn | ✅ Vượt |
| Safety net | Yếu | Merge AI+RAG tránh miss bệnh hiếm | ✅ Vượt |
| Giao tiếp | Trả lời thẳng | OARS — giống bác sĩ thật | ✅ Vượt |
| Cá nhân hóa | Ít hoặc không | Personal Context từ nhật ký + tủ thuốc | ✅ Vượt |
| Lazy loading | Không có | ICD-10 + web search khi cần | ✅ Mới |
| Quick Summary | Không có | Widget tóm tắt từ session DB | ✅ Mới |
| Mục đích cuối | Trả lời câu hỏi | Xanh/Vàng/Đỏ + disclaimer bắt buộc | ✅ Phù hợp y tế |

### Kết luận

> Flow này thuộc nhóm **Personalized Agentic RAG + Differential Diagnosis** — chuẩn cao nhất hiện tại quốc tế, được thiết kế đặc thù cho domain y tế tiếng Việt với **safety-first approach**.
