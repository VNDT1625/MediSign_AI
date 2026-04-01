# MediSign AI - Model Architecture

## Model: Qwen2.5-VL-72B

### Tổng quan

**Qwen2.5-VL-72B** là phiên bản Vision-Language của Qwen2.5 72B, được phát triển bởi Alibaba Cloud.

### Điểm khác biệt với Qwen2.5-72B

| Feature | Qwen2.5-72B | Qwen2.5-VL-72B |
|---------|-------------|-----------------|
| Text only | ✅ | ✅ |
| **Image input** | ❌ | ✅ |
| OCR | ❌ | ✅ |
| Image understanding | ❌ | ✅ |

### Luồng hoạt động trong MediSign

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUY TRÌNH XỬ LÝ                             │
└─────────────────────────────────────────────────────────────────┘

1. USER GỬI ẢNH THUỐC
       │
       ▼
2. Qwen2.5-VL-72B ĐỌC ẢNH
   - Nhận diện tên thuốc trên nhãn
   - Trích xuất thông tin: hàm lượng, nhà sản xuất, hạn sử dụng
       │
       ▼
3. ĐỐI CHIẾU VỚI JSON DATABASE
   - Tìm kiếm thuốc trong database
   - Kiểm tra thông tin: tên, thành phần, chỉ định, chống chỉ định
   - Kiểm tra tương tác thuốc (nếu user đang dùng thuốc khác)
       │
       ▼
4. ĐƯA RA KẾT LUẬN
   - Thông tin thuốc: Công dụng, liều dùng, tác dụng phụ
   - Cảnh báo: Tương tác, chống chỉ định
   - Gợi ý: Nên gặp bác sĩ nếu cần
       │
       ▼
5. RESPONSE CHO USER
```

### Chi tiết từng bước

#### Bước 1: Nhận ảnh từ user
- User chụp ảnh thuốc (nhãn, vỉ, hộp)
- Gửi qua mobile app hoặc web

#### Bước 2: AI đọc ảnh (Vision)
```python
# Ví dụ prompt cho VL model
prompt = """
Bạn là bác sĩ MediSign AI. Hãy đọc ảnh này và trích xuất:
1. Tên thuốc
2. Hàm lượng
3. Nhà sản xuất
4. Hạn sử dụng
5. Hoạt chất (nếu có)
"""
```

#### Bước 3: Đối chiếu JSON
```python
# Tìm thuốc trong database
drug_name = extracted_info["name"]
drug_data = search_drug_in_json(drug_name)

if drug_data:
    # Kiểm tra thông tin
    uses = drug_data["uses"]
    interactions = drug_data["interactions"]
    side_effects = drug_data["side_effects"]
```

#### Bước 4: Đưa ra kết luận
- Tổng hợp thông tin từ:
  - Ảnh (OCR)
  - JSON database (thông tin chi tiết)
  - Medical knowledge (tương tác, cảnh báo)

### Dữ liệu JSON cần thiết

```json
{
  "drugs": [
    {
      "name": "Paracetamol 500mg",
      "brand": "Hapacol",
      "uses": "Hạ sốt, giảm đau",
      "dose": "500-1000mg/lần",
      "interactions": ["Warfarin", "Rượu"],
      "side_effects": "Tổn thương gan nếu quá liều"
    }
  ]
}
```

### Lợi ích của Qwen2.5-VL-72B

1. **Đọc ảnh thuốc** - Nhận diện tên thuốc từ nhãn
2. **OCR tích hợp** - Trích xuất thông tin chính xác
3. **So sánh database** - Đối chiếu với JSON data
4. **Đa ngôn ngữ** - Hỗ trợ tiếng Việt tốt
5. **Self-hosted** - Không phụ thuộc API bên ngoài

### Yêu cầu hệ thống

| Component | Requirement |
|-----------|-------------|
| GPU | A100 80GB (hoặc 2x A100 40GB) |
| VRAM | ~40GB (4-bit quantization) |
| RAM | 64GB+ system |
| Storage | 200GB+ |

### Thay thế fallback

Nếu Qwen2.5-VL quá tải:
1. **Qwen2.5-7B** - Xử lý text (nhanh hơn 10x)
2. **Gemini Flash API** - Vision + text (trả phí)

### Training data cần thiết

Để fine-tune hiệu quả:

| Loại data | Số lượng | Nguồn |
|-----------|----------|--------|
| Drug Q&A | 50,000+ | Crawl + Synthetic |
| Drug interactions | 10,000+ | DrugBank |
| Medical images | 10,000+ | Chụp thực tế |
| Image-text pairs | 50,000+ | OCR + annotation |

---

**Tóm tắt:** Qwen2.5-VL-72B có thể đọc ảnh thuốc → Extract tên → Đối chiếu JSON → Đưa ra kết luận y tế. Đây là model vision-language mạnh nhất hiện có cho use case này.
