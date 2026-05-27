from hypothesis import given
from hypothesis import strategies as st

from app.schemas.diagnostic import ConclusionEvidence, DiagnosticState, RankedDisease
from app.services.triage_formatter import DISCLAIMER, TriageFormatter


formatter = TriageFormatter()


@given(st.text())
def test_ensure_disclaimer_always_present_and_idempotent(content: str) -> None:
    once = formatter.ensure_disclaimer(content)

    assert DISCLAIMER in once
    assert formatter.ensure_disclaimer(once) == once


@given(
    st.lists(
        st.builds(
            RankedDisease,
            name=st.text(min_size=1),
            probability=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
            severity=st.sampled_from(["low", "medium", "high"]),
            sources=st.lists(st.text(min_size=1), max_size=3),
        )
    )
)
def test_assign_triage_level_no_miss_high_severity(diseases: list[RankedDisease]) -> None:
    result = formatter.assign_triage_level(diseases)

    if any(disease.severity == "high" and disease.probability >= 0.30 for disease in diseases):
        assert result == "red"
    if not diseases:
        assert result == "yellow"


def test_assign_triage_level_matrix_examples() -> None:
    assert formatter.assign_triage_level([]) == "yellow"
    assert (
        formatter.assign_triage_level(
            [RankedDisease(name="Danger", probability=0.30, severity="high")]
        )
        == "red"
    )
    assert (
        formatter.assign_triage_level(
            [RankedDisease(name="Unclear", probability=0.49, severity="low")]
        )
        == "yellow"
    )
    assert (
        formatter.assign_triage_level(
            [RankedDisease(name="Medium", probability=0.70, severity="medium")]
        )
        == "yellow"
    )
    assert (
        formatter.assign_triage_level(
            [RankedDisease(name="Low", probability=0.60, severity="low")]
        )
        == "green"
    )


def test_render_final_and_needs_test_include_disclaimer() -> None:
    state = DiagnosticState(
        diseases_ranked=[RankedDisease(name="Cảm lạnh", probability=0.72, severity="low")],
        triage_level="green",
    )
    evidence = ConclusionEvidence(
        disease_name="Cảm lạnh",
        recommendations=["Nghỉ ngơi và uống đủ nước."],
    )

    assert DISCLAIMER in formatter.render_final(state, evidence)
    assert DISCLAIMER in formatter.render_needs_test(state)
