# MediSign AI - Dự án Y Tế Thông Minh

## Tổng quan

MediSign AI là ứng dụng y tế thông minh sử dụng AI để hỗ trợ:
- Chẩn đoán bệnh (gợi ý)
- Nhận diện thuốc từ ảnh
- Tương tác thuốc
- Tư vấn sức khỏe

## Model AI

### Qwen2.5-VL-72B

Model chính: **Qwen2.5-VL-72B** (Vision-Language)

**Điểm mạnh:**
- Đọc ảnh thuốc → Extract tên thuốc
- Xử lý text tiếng Việt tốt
- Self-hosted (không phụ thuộc API bên ngoài)
- 4-bit quantization (~40GB VRAM)

### Luồng xử lý

```
1. User gửi ảnh thuốc
2. Qwen2.5-VL-72B đọc ảnh → Extract tên thuốc
3. Tìm trong drug_database.json
4. Trả kết quả về cho user
```

## Drug Database

### Vị trí
```
data/training_clean/drug_database.json
```

### Format
```json
[
  {
    "name": "Paracetamol",
    "description": "Paracetamol là thuốc giảm đau, hạ sốt...",
    "source": "wikipedia"
  },
  ...
]
```

### Số lượng
- **242 thuốc** trong database

## API Endpoints

### Drug Lookup

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/drug/` | Health check |
| GET | `/api/drug/list` | List all drugs |
| POST | `/api/drug/search` | Search drug by name |
| GET | `/api/drug/search/{name}` | Search drug (GET) |
| GET | `/api/drug/suggestions/{keyword}` | Get suggestions |
| GET | `/api/drug/random/{count}` | Random drugs |

### Ví dụ

```bash
# Search drug
curl -X POST "http://localhost:8000/api/drug/search" \
     -H "Content-Type: application/json" \
     -d '{"drug_name": "Paracetamol"}'

# Response
{
  "status": "found",
  "drug": {
    "name": "Paracetamol",
    "description": "Paracetamol là thuốc giảm đau, hạ sốt...",
    "source": "wikipedia"
  }
}

# Get suggestions
curl "http://localhost:8000/api/drug/suggestions/Para?limit=5"
```

## Training Data

### Vị trí
```
data/training_clean/qwen_72b/
├── train.json  (16,888 records)
└── eval.json   (1,876 records)
```

### Format
```json
[
  {
    "instruction": "Bạn là MediSign AI - trợ lý y tế thông minh...",
    "input": "Thuốc Paracetamol có tác dụng gì?",
    "output": "Paracetamol có tác dụng hạ sốt, giảm đau...",
    "source": "all_medical"
  },
  ...
]
```

### Nguồn dữ liệu
- all_medical: 12,396
- medquad: 2,829
- drug_db: 852
- synthetic_v2: 223
- vn_drugs: 215
- drug_medicine: 170
- synthetic: 108
- drug_synthetic: 90
- Total: **18,764 records**

## Services

### Drug Lookup Service
```python
from app.services.drug_lookup_service import get_drug_info

# Tìm thuốc
result = get_drug_info("Paracetamol")

# Result
{
    "status": "found",
    "drug": {
        "name": "Paracetamol",
        "description": "..."
    }
}
```

## Files quan trọng

| File | Description |
|------|-------------|
| `data/training_clean/drug_database.json` | Drug database (242 drugs) |
| `data/training_clean/qwen_72b/train.json` | Training data |
| `docs/Qwen2.5-VL-Architecture.md` | Model architecture |
| `docs/DRUG_RECOGNITION_FLOW.md` | Drug recognition flow |
| `apps/backend_fastapi/app/services/drug_lookup_service.py` | Drug lookup service |
| `apps/backend_fastapi/app/routers/drug_router.py` | Drug API endpoints |

## Quick Start

### 1. Chạy Drug Lookup Service
```bash
cd apps/backend_fastapi/app/services
python drug_lookup_service.py
```

### 2. Chạy API Server
```bash
cd apps/backend_fastapi
uvicorn app.main:app --reload
```

### 3. Test API
```bash
curl http://localhost:8000/api/drug/search/Paracetamol
```

## Structure

- `apps/mobile_flutter`: Flutter client
- `apps/backend_fastapi`: FastAPI backend
- `packages/shared_contracts`: OpenAPI + JSON Schema contracts
- `data/training_clean/`: Training data & drug database

## Disclaimer

⚠️ **Lưu ý quan trọng:**
- AI chỉ đưa ra **gợi ý**, không thay thế chẩn đoán của bác sĩ
- Luôn tham khảo ý kiến bác sĩ trước khi sử dụng thuốc
- Không tự ý sử dụng thuốc dựa trên thông tin từ AI

---

**Updated:** 2026-03-15
**Version:** 1.0.0
