"""Unit tests for KBLazyLoader.

Tests:
- _validate_and_parse skips records missing required fields and returns only valid ones.
- search_and_enrich returns empty list when LLM output is not valid JSON.
- search_and_enrich is NOT called when RAG #1 returns candidates above threshold.
- _upsert_to_kb sets source="medgemma_search" on all upserted records.

Requirements: 19.2, 19.4
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.diagnostic import PersonalContext, RankedDisease
from app.services.kb_lazy_loader import (
    KB_MISS_THRESHOLD,
    KBLazyLoader,
    KBRecord,
    KBSearchTimeoutError,
)
from app.services.rag_engine import RAGEngine
from app.services.rag_service import RAGHit


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def loader() -> KBLazyLoader:
    return KBLazyLoader(embedder=None, timeout_seconds=15.0)


@pytest.fixture
def mock_db() -> MagicMock:
    db = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = None
    db.commit.return_value = None
    db.rollback.return_value = None
    return db


# ─── Test _validate_and_parse ────────────────────────────────────────────────


class TestValidateAndParse:
    """Test _validate_and_parse skips invalid records and returns only valid ones."""

    def test_valid_records_are_returned(self, loader: KBLazyLoader) -> None:
        llm_output = json.dumps([
            {
                "name": "Viêm họng",
                "symptoms": ["đau họng", "sốt", "khó nuốt"],
                "severity": "medium",
                "red_flags": [],
                "home_care": ["uống nhiều nước"],
                "lab_tests": ["xét nghiệm máu"],
            }
        ])
        result = loader._validate_and_parse(llm_output)
        assert len(result) == 1
        assert result[0].name == "Viêm họng"
        assert result[0].severity == "medium"

    def test_skips_records_missing_required_fields(self, loader: KBLazyLoader) -> None:
        llm_output = json.dumps([
            # Valid record
            {
                "name": "Cúm",
                "symptoms": ["sốt", "ho"],
                "severity": "medium",
                "red_flags": [],
                "home_care": [],
                "lab_tests": [],
            },
            # Missing 'name' field
            {
                "symptoms": ["đau bụng"],
                "severity": "low",
                "red_flags": [],
                "home_care": [],
                "lab_tests": [],
            },
            # Missing 'symptoms' field
            {
                "name": "Viêm dạ dày",
                "severity": "medium",
                "red_flags": [],
                "home_care": [],
                "lab_tests": [],
            },
            # Empty symptoms list (min_length=1 violation)
            {
                "name": "Bệnh X",
                "symptoms": [],
                "severity": "low",
                "red_flags": [],
                "home_care": [],
                "lab_tests": [],
            },
            # Invalid severity
            {
                "name": "Bệnh Y",
                "symptoms": ["triệu chứng"],
                "severity": "critical",
                "red_flags": [],
                "home_care": [],
                "lab_tests": [],
            },
        ])
        result = loader._validate_and_parse(llm_output)
        assert len(result) == 1
        assert result[0].name == "Cúm"

    def test_returns_empty_for_non_json(self, loader: KBLazyLoader) -> None:
        result = loader._validate_and_parse("This is not JSON at all")
        assert result == []

    def test_returns_empty_for_invalid_json(self, loader: KBLazyLoader) -> None:
        result = loader._validate_and_parse("{invalid json[")
        assert result == []

    def test_handles_single_object_wrapped_in_list(self, loader: KBLazyLoader) -> None:
        llm_output = json.dumps({
            "name": "Viêm phổi",
            "symptoms": ["ho", "sốt cao", "khó thở"],
            "severity": "high",
            "red_flags": ["khó thở nặng"],
            "home_care": ["nghỉ ngơi"],
            "lab_tests": ["X-quang phổi"],
        })
        result = loader._validate_and_parse(llm_output)
        assert len(result) == 1
        assert result[0].name == "Viêm phổi"

    def test_handles_json_in_markdown_code_block(self, loader: KBLazyLoader) -> None:
        llm_output = '```json\n[{"name": "Cảm lạnh", "symptoms": ["sổ mũi"], "severity": "low", "red_flags": [], "home_care": [], "lab_tests": []}]\n```'
        result = loader._validate_and_parse(llm_output)
        assert len(result) == 1
        assert result[0].name == "Cảm lạnh"

    def test_non_dict_items_are_skipped(self, loader: KBLazyLoader) -> None:
        llm_output = json.dumps([
            "not a dict",
            42,
            {
                "name": "Cúm",
                "symptoms": ["sốt"],
                "severity": "medium",
                "red_flags": [],
                "home_care": [],
                "lab_tests": [],
            },
        ])
        result = loader._validate_and_parse(llm_output)
        assert len(result) == 1
        assert result[0].name == "Cúm"


# ─── Test search_and_enrich returns empty on invalid JSON ────────────────────


class TestSearchAndEnrich:
    """Test search_and_enrich returns empty list when LLM output is not valid JSON."""

    @pytest.mark.asyncio
    async def test_returns_empty_when_llm_returns_invalid_json(
        self, loader: KBLazyLoader, mock_db: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "I cannot help with that request."}}]
        }

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            result = await loader.search_and_enrich("đau đầu chóng mặt", mock_db)

        assert result == []

    @pytest.mark.asyncio
    async def test_returns_empty_when_http_error(
        self, loader: KBLazyLoader, mock_db: MagicMock
    ) -> None:
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(side_effect=Exception("Connection refused"))
            mock_client_cls.return_value = mock_client

            result = await loader.search_and_enrich("đau đầu", mock_db)

        assert result == []

    @pytest.mark.asyncio
    async def test_raises_timeout_error(
        self, loader: KBLazyLoader, mock_db: MagicMock
    ) -> None:
        import httpx as httpx_mod

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(
                side_effect=httpx_mod.TimeoutException("timed out")
            )
            mock_client_cls.return_value = mock_client

            with pytest.raises(KBSearchTimeoutError):
                await loader.search_and_enrich("đau đầu", mock_db)

    @pytest.mark.asyncio
    async def test_returns_ranked_diseases_on_valid_response(
        self, loader: KBLazyLoader, mock_db: MagicMock
    ) -> None:
        valid_output = json.dumps([
            {
                "name": "Viêm xoang",
                "symptoms": ["đau đầu", "nghẹt mũi", "chảy dịch mũi"],
                "severity": "medium",
                "red_flags": [],
                "home_care": ["rửa mũi bằng nước muối"],
                "lab_tests": ["CT scan xoang"],
            },
            {
                "name": "Đau nửa đầu",
                "symptoms": ["đau đầu một bên", "buồn nôn"],
                "severity": "medium",
                "red_flags": ["đau đầu đột ngột dữ dội"],
                "home_care": ["nghỉ ngơi trong phòng tối"],
                "lab_tests": [],
            },
        ])

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": valid_output}}]
        }

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            # Patch file I/O to avoid writing to disk
            with patch("pathlib.Path.exists", return_value=False):
                with patch("pathlib.Path.write_text"):
                    with patch("pathlib.Path.mkdir"):
                        result = await loader.search_and_enrich("đau đầu nghẹt mũi", mock_db)

        assert len(result) == 2
        assert all(isinstance(d, RankedDisease) for d in result)
        assert all(d.sources == ["medgemma_search"] for d in result)
        assert sum(d.probability for d in result) <= 1.001


# ─── Test lazy loader NOT called when RAG #1 returns above threshold ─────────


class SparseStubAboveThreshold:
    """Sparse stub that returns high-scoring results."""

    def search(self, query: str, top_k: int | None = None, adapter: str = "medical"):
        return [
            RAGHit(
                record_id="flu",
                type="disease",
                title="Cúm mùa",
                content="sốt ho đau họng",
                score=4.0,
                confidence="high",
                needs_medical_review=False,
                source={"name": "test"},
                structured={"severity": "medium"},
            ),
        ][: top_k or 1]


class EmbedderStubAboveThreshold:
    async def search(self, query: str, top_k: int, kind: str = "disease"):
        return [
            {"record_id": "flu", "kind": "disease", "score": 0.9},
        ][:top_k]


class GraphStubEmpty:
    async def edges_for(self, candidates):
        return []


class TestLazyLoaderNotCalledAboveThreshold:
    """Test that lazy loader is NOT called when RAG #1 returns candidates above threshold."""

    @pytest.mark.asyncio
    async def test_lazy_loader_not_called_when_db_is_none(self) -> None:
        """When db is None, lazy loader should never be called regardless of scores."""
        mock_lazy_loader = AsyncMock(spec=KBLazyLoader)
        mock_lazy_loader.search_and_enrich = AsyncMock(return_value=[])

        engine = RAGEngine(
            sparse=SparseStubAboveThreshold(),
            embedder=EmbedderStubAboveThreshold(),
            graph=GraphStubEmpty(),
            lazy_loader=mock_lazy_loader,
        )

        result = await engine.retrieve_initial(
            "sốt đau họng",
            PersonalContext(),
            top_k=10,
            db=None,  # No DB session → lazy loader should not be called
        )

        # Should have results from RAG #1
        assert result
        # Lazy loader should NOT have been called
        mock_lazy_loader.search_and_enrich.assert_not_called()

    @pytest.mark.asyncio
    async def test_lazy_loader_not_called_when_candidates_above_threshold(self) -> None:
        """When _to_disease_candidates returns high-probability candidates, lazy loader skipped."""
        mock_lazy_loader = AsyncMock(spec=KBLazyLoader)
        mock_lazy_loader.search_and_enrich = AsyncMock(return_value=[])

        engine = RAGEngine(
            sparse=SparseStubAboveThreshold(),
            embedder=EmbedderStubAboveThreshold(),
            graph=GraphStubEmpty(),
            lazy_loader=mock_lazy_loader,
        )

        # Patch _to_disease_candidates to return candidates above threshold
        high_prob_candidates = [
            RankedDisease(
                name="Cúm mùa",
                probability=0.6,
                severity="medium",
                sources=["flu"],
            ),
        ]
        with patch.object(engine, "_to_disease_candidates", return_value=high_prob_candidates):
            mock_db = MagicMock()
            result = await engine.retrieve_initial(
                "sốt đau họng",
                PersonalContext(),
                top_k=10,
                db=mock_db,
            )

        # Lazy loader should NOT have been called because max probability > threshold
        mock_lazy_loader.search_and_enrich.assert_not_called()
        assert result


class SparseStubEmpty:
    """Sparse stub that returns no results."""

    def search(self, query: str, top_k: int | None = None, adapter: str = "medical"):
        return []


class EmbedderStubEmpty:
    async def search(self, query: str, top_k: int, kind: str = "disease"):
        return []


class TestLazyLoaderCalledBelowThreshold:
    """Test that lazy loader IS called when RAG #1 returns no candidates."""

    @pytest.mark.asyncio
    async def test_lazy_loader_called_when_no_candidates(self) -> None:
        lazy_results = [
            RankedDisease(
                name="Bệnh mới",
                probability=0.6,
                severity="medium",
                sources=["medgemma_search"],
            ),
        ]
        mock_lazy_loader = AsyncMock(spec=KBLazyLoader)
        mock_lazy_loader.search_and_enrich = AsyncMock(return_value=lazy_results)

        engine = RAGEngine(
            sparse=SparseStubEmpty(),
            embedder=EmbedderStubEmpty(),
            graph=GraphStubEmpty(),
            lazy_loader=mock_lazy_loader,
        )

        mock_db = MagicMock()
        result = await engine.retrieve_initial(
            "triệu chứng lạ hiếm gặp",
            PersonalContext(),
            top_k=10,
            db=mock_db,
        )

        # Lazy loader should have been called
        mock_lazy_loader.search_and_enrich.assert_called_once()
        # Results should come from lazy loader
        assert result
        assert any("medgemma_search" in d.sources for d in result)


# ─── Test _upsert_to_kb sets source="medgemma_search" ────────────────────────


class TestUpsertToKB:
    """Test _upsert_to_kb sets source='medgemma_search' on all upserted records."""

    @pytest.mark.skip(
        reason=(
            "Outdated: _upsert_to_kb no longer writes to knowledge_base.json. "
            "It now stages records in the kb_pending_records table for admin "
            "review (see KBPendingRecord). Rewrite the test against the DB "
            "instead of patching pathlib.Path.write_text."
        )
    )
    @pytest.mark.asyncio
    async def test_upsert_marks_source_as_medgemma_search(
        self, loader: KBLazyLoader, mock_db: MagicMock
    ) -> None:
        records = [
            KBRecord(
                name="Viêm phế quản",
                symptoms=["ho", "đờm", "sốt nhẹ"],
                severity="medium",
                red_flags=[],
                home_care=["uống nhiều nước"],
                lab_tests=["X-quang phổi"],
            ),
        ]

        written_data: list[str] = []

        def capture_write(content, encoding="utf-8"):
            written_data.append(content)

        with patch("pathlib.Path.exists", return_value=False):
            with patch("pathlib.Path.write_text", side_effect=capture_write):
                with patch("pathlib.Path.mkdir"):
                    await loader._upsert_to_kb(records, mock_db)

        # Verify the written JSON contains source="medgemma_search"
        assert written_data
        parsed = json.loads(written_data[0])
        assert isinstance(parsed, list)
        assert len(parsed) == 1
        assert parsed[0]["source"]["name"] == "medgemma_search"
        assert parsed[0]["type"] == "disease"
        assert parsed[0]["record_id"].startswith("medgemma_")

    @pytest.mark.skip(
        reason=(
            "Outdated: _upsert_to_kb no longer calls the embedder directly. "
            "The embedding workflow lives in EmbeddingClient/EmbeddingService "
            "and runs on approved KBPendingRecord rows."
        )
    )
    @pytest.mark.asyncio
    async def test_upsert_with_embedder_encodes_content(self, mock_db: MagicMock) -> None:
        mock_embedder = MagicMock()
        mock_embedder.encode.return_value = [0.1] * 384

        loader_with_embedder = KBLazyLoader(embedder=mock_embedder, timeout_seconds=15.0)

        records = [
            KBRecord(
                name="Cảm cúm",
                symptoms=["sốt", "ho", "mệt mỏi"],
                severity="low",
                red_flags=[],
                home_care=["nghỉ ngơi"],
                lab_tests=[],
            ),
        ]

        with patch("pathlib.Path.exists", return_value=False):
            with patch("pathlib.Path.write_text"):
                with patch("pathlib.Path.mkdir"):
                    await loader_with_embedder._upsert_to_kb(records, mock_db)

        # Embedder should have been called
        mock_embedder.encode.assert_called_once()
        # DB add should have been called for embedding and edges
        assert mock_db.add.called
        mock_db.commit.assert_called_once()


# ─── Test _to_ranked_diseases ────────────────────────────────────────────────


class TestToRankedDiseases:
    """Test conversion from KBRecords to RankedDisease candidates."""

    def test_converts_records_to_ranked_diseases(self, loader: KBLazyLoader) -> None:
        records = [
            KBRecord(
                name="Bệnh A",
                symptoms=["triệu chứng 1", "triệu chứng 2"],
                severity="high",
                red_flags=["nguy hiểm"],
                home_care=[],
                lab_tests=[],
            ),
            KBRecord(
                name="Bệnh B",
                symptoms=["triệu chứng 3"],
                severity="low",
                red_flags=[],
                home_care=[],
                lab_tests=[],
            ),
        ]
        result = loader._to_ranked_diseases(records)

        assert len(result) == 2
        assert all(isinstance(d, RankedDisease) for d in result)
        assert all(d.sources == ["medgemma_search"] for d in result)
        assert sum(d.probability for d in result) <= 1.001
        # Should be sorted by probability descending
        assert result[0].probability >= result[1].probability

    def test_empty_records_returns_empty(self, loader: KBLazyLoader) -> None:
        result = loader._to_ranked_diseases([])
        assert result == []
