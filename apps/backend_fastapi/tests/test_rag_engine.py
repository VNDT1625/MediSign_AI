from __future__ import annotations

from types import SimpleNamespace

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.schemas.diagnostic import PersonalContext, RankedDisease
from app.services.embedding_client import EmbeddingUnavailableError
from app.services.rag_engine import RAGEngine
from app.services.rag_service import RAGHit


class SparseStub:
    def search(self, query: str, top_k: int | None = None, adapter: str = "medical"):
        return [
            RAGHit(
                record_id="flu",
                type="disease",
                title="Cúm mùa",
                content=f"{query} sốt ho đau họng",
                score=4.0,
                confidence="high",
                needs_medical_review=False,
                source={"name": "test"},
                structured={"severity": "medium"},
            ),
            RAGHit(
                record_id="cold",
                type="vietnam_common_disease",
                title="Cảm lạnh",
                content="sổ mũi ho nhẹ",
                score=3.0,
                confidence="high",
                needs_medical_review=False,
                source={"name": "test"},
                structured={"severity": "low"},
            ),
        ][: top_k or 2]


class EmbedderStub:
    async def search(self, query: str, top_k: int, kind: str = "disease"):
        return [
            {"record_id": "flu", "kind": "disease", "score": 0.9},
            {"record_id": "pharyngitis", "kind": "disease", "score": 0.8},
        ][:top_k]


class FailingEmbedderStub:
    async def search(self, query: str, top_k: int, kind: str = "disease"):
        raise EmbeddingUnavailableError()


class GraphStub:
    def __init__(self, edges):
        self.edges = edges

    async def edges_for(self, candidates):
        return self.edges


def engine(embedder=None, graph=None) -> RAGEngine:
    return RAGEngine(
        sparse=SparseStub(),
        embedder=embedder or EmbedderStub(),
        graph=graph or GraphStub([]),
    )


symptom_queries = st.sampled_from(
    [
        "sốt 38.5 độ và đau họng",
        "ho khan kèm mệt mỏi",
        "đau bụng âm ỉ buồn nôn",
        "đau đầu chóng mặt",
        "phát ban ngứa ngoài da",
    ]
)


@settings(max_examples=20)
@given(symptom_queries)
@pytest.mark.asyncio
async def test_retrieve_initial_probability_normalization(query: str) -> None:
    result = await engine().retrieve_initial(query, PersonalContext(), top_k=10)

    assert result
    assert sum(disease.probability for disease in result) <= 1.001
    assert result == sorted(result, key=lambda disease: disease.probability, reverse=True)
    assert all(disease.sources for disease in result)


@pytest.mark.asyncio
async def test_retrieve_initial_degrades_to_bm25_when_embedding_unavailable() -> None:
    result = await engine(embedder=FailingEmbedderStub()).retrieve_initial(
        "sốt đau họng",
        PersonalContext(),
        top_k=10,
    )

    assert result
    assert {disease.name for disease in result} == {"Cúm mùa", "Cảm lạnh"}


known_symptoms = st.lists(
    st.sampled_from(["sốt", "ho", "đau họng", "mệt mỏi"]),
    max_size=4,
    unique=True,
)


@settings(max_examples=20)
@given(known_symptoms)
@pytest.mark.asyncio
async def test_retrieve_differential_question_is_novel(symptoms_known: list[str]) -> None:
    candidates = [
        RankedDisease(name="Cúm mùa", probability=0.55, severity="medium", sources=["flu"]),
        RankedDisease(name="Cảm lạnh", probability=0.45, severity="low", sources=["cold"]),
    ]
    edges = [
        *[
            SimpleNamespace(disease_id="Cúm mùa", symptom=symptom, weight=0.7)
            for symptom in symptoms_known
        ],
        SimpleNamespace(disease_id="Cúm mùa", symptom="đau mỏi cơ", weight=0.9),
    ]

    result = await engine(graph=GraphStub(edges)).retrieve_differential(
        candidates,
        symptoms_known,
    )

    assert result.symptom.lower() not in {symptom.lower() for symptom in symptoms_known}
    assert result.expected_in
    assert result.expected_absent_in


@pytest.mark.asyncio
async def test_retrieve_conclusion_marks_high_severity_missing_red_flags_as_needs_test() -> None:
    top = RankedDisease(
        name="Bệnh cần cấp cứu",
        probability=0.9,
        severity="high",
        sources=["emergency"],
    )

    result = await engine(embedder=FailingEmbedderStub()).retrieve_conclusion(top)

    assert result.disease_name == top.name
    assert result.needs_test is True
    assert "emergency" in result.sources
