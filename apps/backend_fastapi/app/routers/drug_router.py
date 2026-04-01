# -*- coding: utf-8 -*-
"""
Drug Recognition API
FastAPI endpoint cho Qwen2.5-VL-72B
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
import os

# Import drug lookup service
from app.services.drug_lookup_service import (
    get_drug_info,
    search_drugs_by_keyword,
    load_drug_database
)

router = APIRouter(prefix="/api/drug", tags=["drug"])

# ============================================================
# MODELS
# ============================================================

class DrugSearchRequest(BaseModel):
    drug_name: str
    language: Optional[str] = "vi"

class DrugSearchResponse(BaseModel):
    status: str
    drug: Optional[dict] = None
    suggestions: Optional[List[dict]] = None
    message: Optional[str] = None

class DrugListResponse(BaseModel):
    total: int
    drugs: List[dict]

# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Drug Recognition API",
        "version": "1.0.0",
        "status": "running"
    }

@router.get("/list", response_model=DrugListResponse)
async def list_drugs(limit: int = 50, offset: int = 0):
    """
    Lấy danh sách tất cả thuốc trong database.
    """
    drug_database = load_drug_database()
    total = len(drug_database)

    drugs = drug_database[offset:offset + limit]

    return DrugListResponse(
        total=total,
        drugs=drugs
    )

@router.post("/search", response_model=DrugSearchResponse)
async def search_drug(request: DrugSearchRequest):
    """
    Tìm kiếm thuốc theo tên.

    Args:
        drug_name: Tên thuốc được nhận diện từ ảnh (Qwen2.5-VL)

    Returns:
        DrugSearchResponse: Thông tin thuốc hoặc gợi ý
    """
    if not request.drug_name or len(request.drug_name.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Drug name must be at least 2 characters"
        )

    result = get_drug_info(request.drug_name)

    return DrugSearchResponse(
        status=result["status"],
        drug=result.get("drug"),
        suggestions=result.get("suggestions"),
        message=result.get("message")
    )

@router.get("/search/{drug_name}", response_model=DrugSearchResponse)
async def search_drug_get(drug_name: str):
    """
    Tìm kiếm thuốc (GET method).
    """
    result = get_drug_info(drug_name)

    return DrugSearchResponse(
        status=result["status"],
        drug=result.get("drug"),
        suggestions=result.get("suggestions"),
        message=result.get("message")
    )

@router.get("/suggestions/{keyword}")
async def get_suggestions(keyword: str, limit: int = 5):
    """
    Lấy gợi ý thuốc theo keyword.
    """
    drug_database = load_drug_database()
    suggestions = search_drugs_by_keyword(keyword, drug_database, limit=limit)

    return {
        "keyword": keyword,
        "count": len(suggestions),
        "suggestions": suggestions
    }

@router.get("/random/{count}")
async def get_random_drugs(count: int = 5):
    """
    Lấy ngẫu nhiên N thuốc từ database.
    """
    import random
    drug_database = load_drug_database()
    random.shuffle(drug_database)

    drugs = drug_database[:count]

    return {
        "count": len(drugs),
        "drugs": drugs
    }

# ============================================================
# VÍ DỤ SỬ DỤNG
# ============================================================

"""
LUỒNG TÍCH HỢP VỚI QWEN2.5-VL-72B:

1. User gửi ảnh thuốc lên API
2. Qwen2.5-VL-72B extract tên thuốc từ ảnh
3. Gọi POST /api/drug/search với drug_name
4. Nhận kết quả và trả lời user

Ví dụ API Call:
--------------
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

Ví dụ curl:
-----------
curl -X POST "http://localhost:8000/api/drug/search" \
     -H "Content-Type: application/json" \
     -d '{"drug_name": "Paracetamol"}'
"""
