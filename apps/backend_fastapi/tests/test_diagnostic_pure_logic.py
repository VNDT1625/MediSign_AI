import pytest

from app.schemas.ai import AIChatRequest, AIChatResponse
from app.schemas.diagnostic import (
    ConclusionEvidence,
    DiagnosticState,
    DiscriminativeSignal,
    RankedDisease,
)
from app.services.diagnostic_state_manager import DiagnosticStateManager
from app.services.triage_formatter import DISCLAIMER, TriageFormatter


def test_triage_disclaimer_is_present_and_idempotent() -> None:
    formatter = TriageFormatter()

    once = formatter.ensure_disclaimer("Kết luận: theo dõi thêm.")
    twice = formatter.ensure_disclaimer(once)

    assert DISCLAIMER in once
    assert twice == once


def test_triage_assigns_red_for_plausible_high_severity() -> None:
    formatter = TriageFormatter()

    assert (
        formatter.assign_triage_level(
            [
                RankedDisease(name="Cảm lạnh", probability=0.70, severity="low"),
                RankedDisease(name="Viêm phổi nặng", probability=0.30, severity="high"),
            ]
        )
        == "red"
    )


def test_triage_defaults_to_yellow_for_empty_or_uncertain_state() -> None:
    formatter = TriageFormatter()

    assert formatter.assign_triage_level([]) == "yellow"
    assert (
        formatter.assign_triage_level(
            [RankedDisease(name="Cảm lạnh", probability=0.49, severity="low")]
        )
        == "yellow"
    )


def test_render_final_adds_conclusion_header_and_disclaimer() -> None:
    formatter = TriageFormatter()
    state = DiagnosticState(
        diseases_ranked=[RankedDisease(name="Viêm họng", probability=0.88, severity="medium")]
    )
    evidence = ConclusionEvidence(
        disease_name="Viêm họng",
        recommendations=["Uống đủ nước", "Theo dõi sốt"],
        sources=["kb_1"],
    )

    content = formatter.render_final(state, evidence)

    assert content.startswith("Kết luận:")
    assert DISCLAIMER in content


def test_ranked_disease_probability_validator() -> None:
    with pytest.raises(ValueError):
        RankedDisease(name="Không hợp lệ", probability=1.2)


def test_diagnostic_state_default_zero_state() -> None:
    state = DiagnosticState()

    assert state.diseases_ranked == []
    assert state.eliminated == []
    assert state.symptoms_collected == []
    assert state.questions_asked == []
    assert state.phase == "initial"
    assert state.turn_count == 0
    assert state.triage_level is None


def test_ai_chat_schema_preserves_backwards_compatibility_and_diagnostic_fields() -> None:
    request = AIChatRequest(message="Tôi bị sốt")

    assert request.conversation_id is None
    assert request.use_personal_context is False
    assert request.image is None
    assert request.image_type is None

    response = AIChatResponse(
        provider="test",
        model="test-model",
        adapter="medical",
        content="Tôi cần hỏi thêm.",
    )

    assert response.conversation_id is None
    assert response.phase is None
    assert response.diagnosis_state is None
    assert response.triage_level is None
    assert response.image_findings is None
    assert response.image_modality is None


def test_merge_initial_keeps_rag_diseases_and_uses_max_probability() -> None:
    manager = DiagnosticStateManager()
    rag = [
        RankedDisease(name="Cảm cúm", probability=0.40, severity="low", sources=["rag_1"]),
        RankedDisease(name="Viêm họng", probability=0.30, sources=["rag_2"]),
    ]
    ai = [
        RankedDisease(name="Cảm cúm", probability=0.65, severity="medium"),
        RankedDisease(name="Dị ứng", probability=0.20),
    ]

    state = manager.merge_initial(DiagnosticState(), rag, ai, ["sốt", "đau họng"])

    by_name = {d.name: d for d in state.diseases_ranked}
    assert {"Cảm cúm", "Viêm họng", "Dị ứng"} <= set(by_name)
    assert by_name["Cảm cúm"].probability == 0.65
    assert by_name["Cảm cúm"].sources == ["rag_1", "ai_inferred"]
    assert state.symptoms_collected == ["sốt", "đau họng"]
    assert state.turn_count == 1


def test_apply_answer_increments_turn_and_preserves_union_with_eliminated() -> None:
    manager = DiagnosticStateManager()
    before = DiagnosticState(
        diseases_ranked=[
            RankedDisease(name="Viêm họng", probability=0.20),
            RankedDisease(name="Cảm lạnh", probability=0.20),
        ],
        turn_count=1,
    )
    signal = DiscriminativeSignal(symptom="ho khan", expected_in=["Viêm họng"], expected_absent_in=[])

    after = manager.apply_answer(before, "Bạn có ho khan không?", "không", signal)

    before_union = {d.name for d in before.diseases_ranked} | {d.name for d in before.eliminated}
    after_union = {d.name for d in after.diseases_ranked} | {d.name for d in after.eliminated}
    assert after.turn_count == before.turn_count + 1
    assert before_union <= after_union
    assert any(d.name == "Viêm họng" and d.reason for d in after.eliminated)


def test_decide_phase_priority_order() -> None:
    manager = DiagnosticStateManager()

    assert manager.decide_phase(DiagnosticState(turn_count=1)) == "initial"
    assert (
        manager.decide_phase(
            DiagnosticState(
                turn_count=2,
                diseases_ranked=[RankedDisease(name="Viêm họng", probability=0.86)],
            )
        )
        == "conclusion"
    )
    assert (
        manager.decide_phase(
            DiagnosticState(
                turn_count=7,
                diseases_ranked=[RankedDisease(name="Không rõ", probability=0.50)],
            )
        )
        == "needs_test"
    )
