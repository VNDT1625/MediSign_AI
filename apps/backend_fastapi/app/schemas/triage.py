from pydantic import BaseModel, Field


class TriageRequest(BaseModel):
    symptom_text: str = Field(min_length=3, max_length=1000)
    locale: str = Field(default="vi-VN", min_length=2, max_length=10)


class TriageResponse(BaseModel):
    urgency_level: str
    summary: str
    recommendations: list[str]
