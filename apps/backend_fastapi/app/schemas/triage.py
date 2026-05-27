from pydantic import BaseModel, Field
from typing import Literal


class TriageRequest(BaseModel):
    symptom_text: str = Field(min_length=3, max_length=1000)
    locale: str = Field(default="vi-VN", min_length=2, max_length=10)
    # Consult mode sent by the Flutter client.
    # - hybrid : rule-based emergency check + AI summary (default)
    # - local  : rule-based only, no AI enrichment (privacy mode)
    # - cloud  : same as hybrid; reserved for future cloud-only AI path
    mode: Literal["hybrid", "local", "cloud"] = Field(default="hybrid")


class TriageResponse(BaseModel):
    urgency_level: str
    summary: str
    recommendations: list[str]
