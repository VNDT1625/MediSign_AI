from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.schemas.diagnostic import DiagnosticState, DiscriminativeQuestion, RankedDisease
from app.services.oars_prompt_layer import OARSPromptLayer


symptom_text = st.sampled_from(
    [
        "sốt",
        "đau họng",
        "ho khan",
        "mệt mỏi",
        "đau đầu",
        "khó thở",
    ]
)


def diagnostic_state_strategy() -> st.SearchStrategy[DiagnosticState]:
    disease = st.builds(
        RankedDisease,
        name=st.sampled_from(["Cúm mùa", "Cảm lạnh", "Viêm họng"]),
        probability=st.floats(
            min_value=0.0,
            max_value=1.0,
            allow_nan=False,
            allow_infinity=False,
        ),
        severity=st.sampled_from(["low", "medium", "high"]),
        sources=st.lists(st.text(min_size=1, max_size=12), min_size=1, max_size=2),
    )
    return st.builds(
        DiagnosticState,
        symptoms_collected=st.lists(symptom_text, max_size=4, unique=True),
        diseases_ranked=st.lists(disease, max_size=3, unique_by=lambda item: item.name),
        phase=st.just("questioning"),
        turn_count=st.integers(min_value=1, max_value=6),
    )


def discriminative_question_strategy() -> st.SearchStrategy[DiscriminativeQuestion]:
    return st.builds(
        DiscriminativeQuestion,
        symptom=symptom_text,
        question=st.just("Bạn có triệu chứng này không?"),
        expected_in=st.lists(st.sampled_from(["Cúm mùa", "Viêm họng"]), min_size=1, max_size=2),
        expected_absent_in=st.lists(st.sampled_from(["Cảm lạnh"]), min_size=1, max_size=1),
        metadata=st.just({"last_user_message": "tôi đang thấy khó chịu"}),
    )


@settings(max_examples=20)
@given(state=diagnostic_state_strategy(), question=discriminative_question_strategy())
@pytest.mark.asyncio
async def test_humanize_question_oars_conversational_quality(
    state: DiagnosticState,
    question: DiscriminativeQuestion,
) -> None:
    reference = state.symptoms_collected[0] if state.symptoms_collected else "tôi đang thấy khó chịu"

    async def llm_stub(system_prompt: str, user_prompt: str) -> str:
        assert "RAG_CONTEXT:" in system_prompt
        assert "NEXT_QUESTION:" in system_prompt
        assert "STATE_SUMMARY:" in system_prompt
        return (
            f"Mình ghi nhận {reference}. Để hiểu rõ hơn, "
            f"bạn có thể chia sẻ thêm về {question.symptom} không?"
        )

    response = await OARSPromptLayer(llm_caller=llm_stub).humanize_question(question, state)

    assert response.endswith("?")
    assert response.count("?") == 1
    assert "Kết luận:" not in response
    assert question.symptom in response
    if state.symptoms_collected:
        assert any(symptom in response for symptom in state.symptoms_collected)


@pytest.mark.asyncio
async def test_humanize_question_falls_back_when_llm_leaks_conclusion() -> None:
    state = DiagnosticState(symptoms_collected=["sốt"], phase="questioning", turn_count=2)
    question = DiscriminativeQuestion(
        symptom="đau họng",
        question="Bạn có đau họng không?",
        expected_in=["Viêm họng"],
        expected_absent_in=["Cảm lạnh"],
    )

    async def bad_llm_stub(system_prompt: str, user_prompt: str) -> str:
        return "Kết luận: có thể viêm họng. Bạn đau họng không? Có sốt không?"

    response = await OARSPromptLayer(llm_caller=bad_llm_stub).humanize_question(question, state)

    assert response.endswith("?")
    assert response.count("?") == 1
    assert "Kết luận:" not in response
    assert "sốt" in response
    assert "đau họng" in response
