from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.diagnostic import ChatPhase, DiagnosticState, TriageLevel


class RAGSource(BaseModel):
    record_id: str
    type: str
    title: str
    score: float
    confidence: str
    needs_medical_review: bool = False
    source: dict = Field(default_factory=dict)


class RAGSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    adapter: str = "medical"
    top_k: int = Field(default=5, ge=1, le=20)


class RAGSearchResponse(BaseModel):
    query: str
    hits: list[RAGSource]
    context: str


class AIChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    system_prompt: str | None = None
    adapter: str = "medical"
    use_rag: bool = True
    rag_top_k: int = Field(default=5, ge=1, le=20)
    # New fields for multi-turn diagnostic chat (all optional for backwards compat)
    conversation_id: str | None = None
    use_personal_context: bool = False
    image: bytes | None = None
    image_type: Literal["xray", "dermatology"] | None = None


class AIChatResponse(BaseModel):
    provider: str
    model: str
    adapter: str
    content: str
    fallback_used: bool = False
    rag_used: bool = False
    sources: list[RAGSource] = Field(default_factory=list)
    # New fields for multi-turn diagnostic chat (all optional for backwards compat)
    conversation_id: str | None = None
    phase: ChatPhase | None = None
    diagnosis_state: DiagnosticState | None = None
    triage_level: TriageLevel | None = None
    image_findings: str | None = None
    image_modality: str | None = None


class AIStatusResponse(BaseModel):
    provider: str
    model: str
    base_url: str
    medical_adapter_path: str
    psychology_adapter_path: str
    ready: bool
    detail: str
    rag: dict = Field(default_factory=dict)
