# Drug Recognition Flow - Tài liệu kỹ thuật

## Tổng quan

Khi sử dụng **Qwen2.5-VL-72B** để nhận diện thuốc từ ảnh:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     USER UPLOAD IMAGE                                │
│                 (Chụp ảnh nhãn/hộp thuốc)                        │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              QWEN2.5-VL-72B PROCESSES IMAGE                        │
│         - Đọc ảnh                                                │
│         - Extract tên thuốc: "Paracetamol 500mg"                 │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              CALL DRUG LOOKUP SERVICE                                │
│                                                                 │
│   get_drug_info("Paracetamol 500mg")                             │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              SEARCH IN DRUG DATABASE                                 │
│                                                                 │
│   drug_database.json (242 drugs)                                 │
│                                                                 │
│   ├── Exact match: "Paracetamol"                                  │
│   ├── Partial match: "Paracetamol + Clavulanic acid"           │
│   └── No match → Return suggestions                               │
└─────────────────────────────────────────────────────────────────────┘
                                │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
            ┌───────────────┐           ┌───────────────────┐
            │ FOUND         │           │ NOT FOUND         │
            │ Return drug  │           │ Return similar    │
            │ info          │           │ drugs as          │
            │               │           │ suggestions        │
            └───────────────┘           └───────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              RETURN RESULT TO USER                                   │
│                                                                 │
│   ✓ Tìm thấy: Paracetamol                                       │
│   Công dụng: Hạ sốt, giảm đau                                   │
│   Liều: 500-1000mg/lần                                          │
│   ⚠️ Lưu ý: ...                                                 │
└─────────────────────────────────────────────────────────────────────┘
```

## API Endpoints

### 1. Search Drug (POST)
```
POST /api/drug/search
{
    "drug_name": "Paracetamol 500mg"
}

Response:
{
    "status": "found",
    "drug": {
        "name": "Paracetamol",
        "description": "Paracetamol là thuốc giảm đau, hạ sốt...",
        ...
    }
}
```

### 2. Search Drug (GET)
```
GET /api/drug/search/Paracetamol
```

### 3. List All Drugs
```
GET /api/drug/list?limit=50&offset=0
```

### 4. Get Suggestions
```
GET /api/drug/suggestions/Para?limit=5
```

## Files

| File | Description |
|------|-------------|
| `drug_lookup_service.py` | Core service - tìm kiếm trong DB |
| `drug_router.py` | FastAPI endpoints |
| `drug_database.json` | 242 thuốc |

## Drug Database

**Location:** `data/training_clean/drug_database.json`

**Format:**
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

## Test

```bash
# Test drug lookup
python app/services/drug_lookup_service.py

# Test API
curl http://localhost:8000/api/drug/search/Paracetamol
```
