"""Unit tests for schema validators.

Validates: Requirements 15.4, 15.5, 8.1
"""

import pytest
from pydantic import ValidationError

from app.schemas.ai import AIChatRequest
from app.schemas.diagnostic import DiagnosticState, RankedDisease


# ─── RankedDisease probability validation ────────────────────────────────────


class TestRankedDiseaseProbability:
    """Test that RankedDisease rejects probability outside [0.0, 1.0]."""

    def test_probability_above_one_rejected(self) -> None:
        with pytest.raises(ValidationError):
            RankedDisease(name="Test", probability=1.01)

    def test_probability_below_zero_rejected(self) -> None:
        with pytest.raises(ValidationError):
            RankedDisease(name="Test", probability=-0.01)

    def test_probability_at_zero_accepted(self) -> None:
        d = RankedDisease(name="Test", probability=0.0)
        assert d.probability == 0.0

    def test_probability_at_one_accepted(self) -> None:
        d = RankedDisease(name="Test", probability=1.0)
        assert d.probability == 1.0

    def test_probability_mid_range_accepted(self) -> None:
        d = RankedDisease(name="Test", probability=0.55)
        assert d.probability == 0.55


# ─── DiagnosticState default construction ────────────────────────────────────


class TestDiagnosticStateDefaults:
    """Test that DiagnosticState default construction produces correct zero-state."""

    def test_default_phase_is_initial(self) -> None:
        state = DiagnosticState()
        assert state.phase == "initial"

    def test_default_turn_count_is_zero(self) -> None:
        state = DiagnosticState()
        assert state.turn_count == 0

    def test_default_diseases_ranked_is_empty(self) -> None:
        state = DiagnosticState()
        assert state.diseases_ranked == []

    def test_default_eliminated_is_empty(self) -> None:
        state = DiagnosticState()
        assert state.eliminated == []

    def test_default_symptoms_collected_is_empty(self) -> None:
        state = DiagnosticState()
        assert state.symptoms_collected == []

    def test_default_questions_asked_is_empty(self) -> None:
        state = DiagnosticState()
        assert state.questions_asked == []

    def test_default_triage_level_is_none(self) -> None:
        state = DiagnosticState()
        assert state.triage_level is None


# ─── AIChatRequest backwards compatibility ───────────────────────────────────


class TestAIChatRequestBackwardsCompat:
    """Test that AIChatRequest without conversation_id is valid (backwards compat)."""

    def test_request_without_conversation_id_is_valid(self) -> None:
        req = AIChatRequest(message="sốt 38 độ")
        assert req.conversation_id is None

    def test_request_with_conversation_id_is_valid(self) -> None:
        req = AIChatRequest(
            message="sốt 38 độ",
            conversation_id="12345678-1234-1234-1234-123456789012",
        )
        assert req.conversation_id == "12345678-1234-1234-1234-123456789012"

    def test_request_preserves_existing_fields(self) -> None:
        req = AIChatRequest(
            message="đau đầu",
            adapter="medical",
            use_rag=True,
            rag_top_k=10,
        )
        assert req.message == "đau đầu"
        assert req.adapter == "medical"
        assert req.use_rag is True
        assert req.rag_top_k == 10
        assert req.conversation_id is None
        assert req.use_personal_context is False
        assert req.image is None
        assert req.image_type is None
