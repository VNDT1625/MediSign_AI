from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from app.schemas.diagnostic import DiagnosticState, DiscriminativeSignal, RankedDisease
from app.services.diagnostic_state_manager import DiagnosticStateManager


manager = DiagnosticStateManager()


def ranked_disease_strategy() -> st.SearchStrategy[RankedDisease]:
    return st.builds(
        RankedDisease,
        name=st.text(min_size=1, max_size=30).filter(lambda value: bool(value.strip())),
        probability=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        severity=st.sampled_from(["low", "medium", "high"]),
        sources=st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=3, unique=True),
    )


def signal_strategy(names: list[str]) -> st.SearchStrategy[DiscriminativeSignal]:
    return st.builds(
        DiscriminativeSignal,
        symptom=st.sampled_from(["sốt", "ho", "đau họng", "khó thở"]),
        expected_in=st.lists(st.sampled_from(names), max_size=max(1, len(names)), unique=True),
        expected_absent_in=st.lists(st.sampled_from(names), max_size=max(1, len(names)), unique=True),
    )


def disease_union(state: DiagnosticState) -> set[str]:
    return {disease.name.casefold() for disease in [*state.diseases_ranked, *state.eliminated]}


@given(
    diseases=st.lists(ranked_disease_strategy(), min_size=1, max_size=8, unique_by=lambda d: d.name),
    answers=st.lists(st.sampled_from(["có", "không"]), min_size=1, max_size=5),
    data=st.data(),
)
def test_apply_answer_preserves_turn_count_and_disease_union(
    diseases: list[RankedDisease],
    answers: list[str],
    data: st.DataObject,
) -> None:
    state = DiagnosticState(diseases_ranked=diseases)

    for answer in answers:
        before = state
        names = [disease.name for disease in before.diseases_ranked] or ["fallback"]
        signal = data.draw(signal_strategy(names))

        state = manager.apply_answer(before, "Bạn có triệu chứng này không?", answer, signal)

        assert state.turn_count == before.turn_count + 1
        assert disease_union(before).issubset(disease_union(state))


@given(
    rag=st.lists(ranked_disease_strategy(), min_size=1, max_size=8, unique_by=lambda d: d.name),
    ai=st.lists(ranked_disease_strategy(), max_size=8, unique_by=lambda d: d.name),
)
def test_merge_initial_keeps_all_rag_diseases_and_uses_max_probability(
    rag: list[RankedDisease],
    ai: list[RankedDisease],
) -> None:
    merged = manager.merge_initial(DiagnosticState(), rag, ai, [])
    by_name = {disease.name.casefold(): disease for disease in merged.diseases_ranked}

    for disease in rag:
        assert disease.name.casefold() in by_name

    rag_by_name = {disease.name.casefold(): disease for disease in rag}
    ai_by_name = {disease.name.casefold(): disease for disease in ai}
    for name in rag_by_name.keys() & ai_by_name.keys():
        assert by_name[name].probability == max(
            rag_by_name[name].probability,
            ai_by_name[name].probability,
        )


def test_merge_initial_assigns_ai_inferred_source_for_ai_only_diseases() -> None:
    state = manager.merge_initial(
        DiagnosticState(),
        [],
        [RankedDisease(name="Cảm lạnh", probability=0.4, sources=[])],
        ["sổ mũi"],
    )

    assert state.diseases_ranked[0].sources == ["ai_inferred"]
    assert state.symptoms_collected == ["sổ mũi"]
    assert state.turn_count == 1
