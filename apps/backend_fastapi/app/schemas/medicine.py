from pydantic import BaseModel, Field


class MedicineScanRequest(BaseModel):
    extracted_text: str = Field(min_length=2, max_length=500)
    current_medications: list[str] = Field(default_factory=list)


class MedicineScanResponse(BaseModel):
    normalized_name: str
    risk_level: str
    warnings: list[str]
    guidance: str
