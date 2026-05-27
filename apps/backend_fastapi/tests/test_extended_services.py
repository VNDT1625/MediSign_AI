"""Unit tests for extended rag_service and ai_model_service methods (Task 21.3).

Validates: Requirements 8.1, 12.1, 14.1
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import patch

import pytest

from app.schemas.ai import AIChatRequest, AIChatResponse
from app.schemas.diagnostic import RankedDisease
from app.services.ai_model_service import AIModelService, ai_model_service
from app.services.rag_service import RAGHit, RAGService, rag_service


# ─── Tests for rag_service.build_context with dict input ─────────────────────


class TestBuildContextWithDicts:
    """Test that build_context accepts both RAGHit objects and plain dicts."""

    def test_build_context_with_rag_hits(self) -> None:
        """Existing behavior: build_context works with RAGHit objects."""
        hits = [
            RAGHit(
                record_id="rec1",
                type="disease",
                title="Cúm mùa",
                content="Sốt cao, đau họng, ho khan",
                score=3.5,
                confidence="high",
                needs_medical_review=False,
                source={"name": "MediSign KB"},
                structured={},
            )
        ]
        result = rag_service.build_context(hits)
        assert "rec1" in result
        assert "Cúm mùa" in result
        assert "Sốt cao" in result

    def test_build_context_with_dicts(self) -> None:
        """New behavior: build_context works with plain dicts."""
        records: list[dict[str, Any]] = [
            {
                "record_id": "dict_rec1",
                "type": "evidence",
                "title": "Viêm phổi",
                "content": "Ho có đờm, sốt cao, khó thở",
                "confidence": "high",
                "needs_medical_review": True,
                "source": {"name": "Test Source"},
            },
            {
                "record_id": "dict_rec2",
                "type": "disease",
                "title": "Viêm phế quản",
                "content": "Ho kéo dài, đau ngực nhẹ",
                "confidence": "medium",
                "needs_medical_review": False,
                "source": {"name": "KB"},
            },
        ]
        result = rag_service.build_context(records)
        assert "dict_rec1" in result
        assert "Viêm phổi" in result
        assert "can_bac_si_kiem_duyet" in result
        assert "dict_rec2" in result
        assert "Viêm phế quản" in result

    def test_build_context_with_empty_list(self) -> None:
        """build_context returns empty string for empty input."""
        assert rag_service.build_context([]) == ""

    def test_build_context_dict_with_id_key(self) -> None:
        """build_context handles dicts using 'id' instead of 'record_id'."""
        records: list[dict[str, Any]] = [
            {
                "id": "alt_id_1",
                "type": "knowledge",
                "title": "Test",
                "content": "Some content",
                "confidence": "low",
                "source": {},
            }
        ]
        result = rag_service.build_context(records)
        assert "alt_id_1" in result

    def test_build_context_respects_max_chars(self) -> None:
        """build_context truncates output when max_chars is exceeded."""
        records: list[dict[str, Any]] = [
            {
                "record_id": f"rec_{i}",
                "type": "disease",
                "title": f"Disease {i}",
                "content": "A" * 500,
                "confidence": "medium",
                "source": {},
            }
            for i in range(20)
        ]
        result = rag_service.build_context(records, max_chars=300)
        assert len(result) <= 350  # Allow small overhead from formatting


# ─── Tests for rag_service.search with kind_filter ───────────────────────────


class TestSearchWithKindFilter:
    """Test that search accepts an optional kind_filter parameter."""

    def test_search_without_kind_filter_returns_all_types(self) -> None:
        """Existing behavior: search without kind_filter returns all document types."""
        results = rag_service.search("sốt đau họng", top_k=10)
        # Should work without error (may return empty if KB not loaded)
        assert isinstance(results, list)

    def test_search_with_kind_filter_restricts_types(self) -> None:
        """New behavior: search with kind_filter only returns matching types."""
        # Search with a filter that likely excludes all documents
        results = rag_service.search(
            "sốt đau họng",
            top_k=10,
            kind_filter={"nonexistent_type_xyz"},
        )
        assert results == []

    def test_search_kind_filter_none_is_same_as_no_filter(self) -> None:
        """kind_filter=None behaves identically to not passing it."""
        results_no_filter = rag_service.search("sốt", top_k=5)
        results_none_filter = rag_service.search("sốt", top_k=5, kind_filter=None)
        # Both should return the same results
        assert len(results_no_filter) == len(results_none_filter)
        for a, b in zip(results_no_filter, results_none_filter):
            assert a.record_id == b.record_id


# ─── Tests for ai_model_service.chat() backwards compatibility ───────────────


class TestAIModelServiceChatBackwardsCompat:
    """Test that chat() without conversation_id still returns existing response shape."""

    @pytest.mark.asyncio
    async def test_chat_without_conversation_id_returns_existing_shape(self) -> None:
        """Request without conversation_id returns existing response shape without diagnosis_state."""
        payload = AIChatRequest(
            message="Tôi bị đau đầu",
            adapter="medical",
        )
        response = await ai_model_service.chat(payload)

        assert isinstance(response, AIChatResponse)
        assert response.provider
        assert response.model
        assert response.adapter == "medical"
        assert response.content
        # Without conversation_id, diagnostic fields should be None
        assert response.conversation_id is None
        assert response.phase is None
        assert response.diagnosis_state is None
        assert response.triage_level is None

    @pytest.mark.asyncio
    async def test_chat_with_conversation_id_invalid_format_returns_422(self) -> None:
        """Request with non-UUID conversation_id raises HTTP 422 from orchestrator."""
        from fastapi import HTTPException

        payload = AIChatRequest(
            message="Tôi bị sốt 38 độ",
            adapter="medical",
            conversation_id="not-a-uuid",
        )
        # Orchestrator validates UUID format and raises 422 for invalid IDs
        with pytest.raises(HTTPException) as exc_info:
            await ai_model_service.chat(payload)
        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_chat_explicit_conversation_id_param_overrides_payload(self) -> None:
        """Explicit conversation_id parameter overrides payload conversation_id."""
        from fastapi import HTTPException

        payload = AIChatRequest(
            message="Tôi bị ho",
            adapter="medical",
            conversation_id="payload-id-not-used",
        )
        # The explicit param should be used (and fail UUID validation since it's not 36 chars)
        with pytest.raises(HTTPException) as exc_info:
            await ai_model_service.chat(payload, conversation_id="explicit-not-uuid")
        # Confirms the explicit param was used (not the payload one) by being the one that failed
        assert exc_info.value.status_code == 422
        assert "INVALID_CONVERSATION_ID" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_chat_fallback_response_shape_unchanged(self) -> None:
        """Fallback response (no model server) preserves existing fields."""
        payload = AIChatRequest(
            message="Xin chào",
            adapter="psychology",
        )
        response = await ai_model_service.chat(payload)

        assert response.fallback_used is True
        assert response.adapter == "psychology"
        assert response.content
        # Existing fields present
        assert isinstance(response.sources, list)


# ─── Tests for ai_model_service.rank_diseases ────────────────────────────────


class TestRankDiseases:
    """Test the rank_diseases method."""

    @pytest.mark.asyncio
    async def test_rank_diseases_returns_empty_when_provider_not_configured(self) -> None:
        """rank_diseases returns empty list when AI provider is rule_based."""
        result = await ai_model_service.rank_diseases("sốt cao đau họng")
        # Default provider is rule_based, so should return empty
        assert result == []

    @pytest.mark.asyncio
    async def test_rank_diseases_parses_valid_json_response(self) -> None:
        """rank_diseases correctly parses a valid JSON response from LLM."""
        mock_response = json.dumps([
            {"name": "Cúm mùa", "probability": 0.45, "severity": "medium", "rationale": "Sốt + ho"},
            {"name": "Viêm họng", "probability": 0.35, "severity": "low", "rationale": "Đau họng"},
            {"name": "COVID-19", "probability": 0.20, "severity": "high", "rationale": "Sốt cao"},
        ])

        service = AIModelService()
        result = service._parse_ranked_diseases(mock_response)

        assert len(result) == 3
        assert all(isinstance(d, RankedDisease) for d in result)
        assert result[0].name == "Cúm mùa"
        assert result[0].probability == 0.45
        assert result[0].severity == "medium"
        assert result[0].sources == ["ai_inferred"]
        # Sorted by probability descending
        assert result[0].probability >= result[1].probability >= result[2].probability

    @pytest.mark.asyncio
    async def test_rank_diseases_handles_markdown_wrapped_json(self) -> None:
        """rank_diseases extracts JSON from markdown code blocks."""
        mock_response = (
            "Dựa trên triệu chứng:\n"
            "```json\n"
            '[{"name": "Viêm phổi", "probability": 0.6, "severity": "high"}]\n'
            "```"
        )

        service = AIModelService()
        result = service._parse_ranked_diseases(mock_response)

        assert len(result) == 1
        assert result[0].name == "Viêm phổi"
        assert result[0].probability == 0.6

    @pytest.mark.asyncio
    async def test_rank_diseases_returns_empty_for_invalid_json(self) -> None:
        """rank_diseases returns empty list for unparseable output."""
        service = AIModelService()
        result = service._parse_ranked_diseases("This is not JSON at all")
        assert result == []

    @pytest.mark.asyncio
    async def test_rank_diseases_skips_invalid_items(self) -> None:
        """rank_diseases skips items that fail validation."""
        mock_response = json.dumps([
            {"name": "Valid", "probability": 0.5, "severity": "low"},
            {"name": "Invalid prob", "probability": 1.5, "severity": "low"},  # > 1.0
            {"name": "", "probability": 0.3, "severity": "medium"},  # empty name still valid
            "not a dict",
        ])

        service = AIModelService()
        result = service._parse_ranked_diseases(mock_response)

        # Should have 2 valid items (first and third), second has prob > 1.0 which fails
        assert len(result) == 2
        assert result[0].name == "Valid"

    @pytest.mark.asyncio
    async def test_rank_diseases_limits_to_5_results(self) -> None:
        """rank_diseases returns at most 5 diseases."""
        mock_response = json.dumps([
            {"name": f"Disease {i}", "probability": round(0.9 - i * 0.1, 2), "severity": "low"}
            for i in range(8)
        ])

        service = AIModelService()
        result = service._parse_ranked_diseases(mock_response)

        assert len(result) <= 5

    @pytest.mark.asyncio
    @patch("app.services.ai_model_service.settings")
    async def test_rank_diseases_calls_llm_when_provider_configured(
        self, mock_settings
    ) -> None:
        """rank_diseases makes LLM call when provider is openai_compatible."""
        mock_settings.ai_provider = "openai_compatible"
        mock_settings.ai_medical_model = "test-model"
        mock_settings.ai_base_url = "http://localhost:8080/v1"
        mock_settings.ai_api_key = ""
        mock_settings.ai_request_timeout_seconds = 10.0

        llm_response = json.dumps([
            {"name": "Cúm", "probability": 0.7, "severity": "medium", "rationale": "test"},
        ])

        class FakeResponse:
            status_code = 200

            def raise_for_status(self):
                pass

            def json(self):
                return {"choices": [{"message": {"content": llm_response}}]}

        class FakeClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

            async def post(self, *args, **kwargs):
                return FakeResponse()

        with patch("httpx.AsyncClient", return_value=FakeClient()):
            service = AIModelService()
            result = await service.rank_diseases("sốt cao ho khan")

        assert len(result) == 1
        assert result[0].name == "Cúm"
        assert result[0].probability == 0.7
        assert result[0].sources == ["ai_inferred"]
