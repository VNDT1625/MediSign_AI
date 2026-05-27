"""Domain types for the RAG Diagnostic Chat feature.

Validates: Requirements 15.4, 15.5, 15.6
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


# ─── Type aliases ────────────────────────────────────────────────────────────

Severity = Literal["low", "medium", "high"]
ChatPhase = Literal["initial", "questioning", "conclusion", "needs_test"]
Phase = ChatPhase
TriageLevel = Literal["green", "yellow", "red"]
Adapter = Literal["medical", "psychology"]


# ─── Core domain models ──────────────────────────────────────────────────────


class RankedDisease(BaseModel):
    """A disease candidate with probability and provenance."""

    name: str
    icd10: str | None = None
    probability: float = Field(ge=0.0, le=1.0)
    severity: Severity = "medium"
    rationale: str | None = None
    sources: list[str] = Field(default_factory=list)

    @field_validator("probability")
    @classmethod
    def probability_in_range(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("probability must be between 0.0 and 1.0")
        return v


class EliminatedDisease(RankedDisease):
    """A disease that was ruled out with a reason."""

    reason: str


class DiscriminativeSignal(BaseModel):
    """Signal indicating which diseases a symptom discriminates between."""

    symptom: str
    expected_in: list[str] = Field(default_factory=list)
    expected_absent_in: list[str] = Field(default_factory=list)


class DiscriminativeQuestion(DiscriminativeSignal):
    """A question derived from discriminative signals for the OARS layer."""

    question: str = ""
    sources: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class TopDiseaseSnapshot(BaseModel):
    """Snapshot of top disease for history tracking (phase stability)."""

    name: str
    probability: float = Field(ge=0.0, le=1.0)


class DiagnosticState(BaseModel):
    """Full diagnostic state persisted in chat message metadata."""

    diseases_ranked: list[RankedDisease] = Field(default_factory=list)
    eliminated: list[EliminatedDisease] = Field(default_factory=list)
    symptoms_collected: list[str] = Field(default_factory=list)
    questions_asked: list[str] = Field(default_factory=list)
    phase: ChatPhase = "initial"
    turn_count: int = Field(default=0, ge=0)
    triage_level: TriageLevel | None = None
    top_disease_history: list[TopDiseaseSnapshot] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("phase")
    @classmethod
    def phase_must_be_valid(cls, v: str) -> str:
        allowed = {"initial", "questioning", "conclusion", "needs_test"}
        if v not in allowed:
            raise ValueError(f"phase must be one of {allowed}, got '{v}'")
        return v

    @field_validator("triage_level")
    @classmethod
    def triage_level_must_be_valid(cls, v: str | None) -> str | None:
        if v is not None:
            allowed = {"green", "yellow", "red"}
            if v not in allowed:
                raise ValueError(f"triage_level must be one of {allowed} or None, got '{v}'")
        return v


# ─── Personal context ────────────────────────────────────────────────────────


class UserProfileMini(BaseModel):
    """Minimal user profile for personal-context re-ranking."""

    age_range: str | None = None
    gender: str | None = None
    conditions: list[str] = Field(default_factory=list)


class MyMedicineMini(BaseModel):
    """Minimal medicine record for personal-context re-ranking."""

    name: str
    dosage: str | None = None
    frequency: str | None = None


class PersonalContext(BaseModel):
    """Aggregated personal context for RAG re-ranking (requires consent)."""

    profile: UserProfileMini | None = None
    medications: list[MyMedicineMini] = Field(default_factory=list)
    recent_journal_summary: str | None = None
    consent_personal_context: bool = False


# ─── Quick Summary ───────────────────────────────────────────────────────────


class QuickSummary(BaseModel):
    """Read-only projection of latest diagnostic state for the widget."""

    conversation_id: str
    symptoms_collected: list[str] = Field(default_factory=list)
    diseases_ranked: list[RankedDisease] = Field(default_factory=list)
    triage_level: TriageLevel | None = None
    recommendation: str
    updated_at: datetime


# ─── Conclusion & Self-check ─────────────────────────────────────────────────


class ConclusionEvidence(BaseModel):
    """Evidence gathered during RAG #3 for the conclusion phase."""

    disease_name: str = ""
    severity: Severity = "medium"
    red_flags: list[str] = Field(default_factory=list)
    lab_tests: list[str] = Field(default_factory=list)
    home_care: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    needs_test: bool = False
    supporting: list[str] = Field(default_factory=list)
    conflicting: list[str] = Field(default_factory=list)


class SelfCheckResult(BaseModel):
    """Result of LLM self-check against conclusion evidence."""

    supports_conclusion: bool = False
    missing_evidence: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    passed: bool = False
    issues: list[str] = Field(default_factory=list)


# ─── RAG source tracking ─────────────────────────────────────────────────────


class RAGSource(BaseModel):
    """A source record from the knowledge base used in retrieval."""

    record_id: str
    kind: str | None = None
    title: str | None = None
    score: float | None = None
    metadata: dict = Field(default_factory=dict)


# ─── Image processing ────────────────────────────────────────────────────────


class ProcessedImage(BaseModel):
    """Result of image preprocessing for MedGemma vision encoder."""

    image_type: Literal["xray", "dermatology"]
    modality: str | None = None
    content_base64: str | None = None
    content_block: dict = Field(default_factory=dict)
    findings: str | None = None
    width: int | None = None
    height: int | None = None
    metadata: dict = Field(default_factory=dict)
