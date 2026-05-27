from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime

from app.schemas.diagnostic import (
    ChatPhase,
    DiagnosticState,
    DiscriminativeSignal,
    EliminatedDisease,
    RankedDisease,
    TopDiseaseSnapshot,
)


SourceLookup = Callable[[RankedDisease], list[str]]


class DiagnosticStateManager:
    """Pure state transitions for the multi-turn diagnostic loop."""

    def __init__(self, source_lookup: SourceLookup | None = None) -> None:
        self._source_lookup = source_lookup

    def merge_initial(
        self,
        prev: DiagnosticState,
        rag_diseases: list[RankedDisease],
        ai_diseases: list[RankedDisease],
        symptoms_extracted: list[str],
    ) -> DiagnosticState:
        merged: dict[str, RankedDisease] = {}

        for disease, from_ai in [
            *[(item, False) for item in prev.diseases_ranked],
            *[(item, False) for item in rag_diseases],
            *[(item, True) for item in ai_diseases],
        ]:
            key = self._key(disease.name)
            existing = merged.get(key)
            candidate = disease.model_copy(deep=True)
            if from_ai and not candidate.sources:
                candidate.sources = self._lookup_sources(candidate)

            if existing is None:
                merged[key] = candidate
                continue

            merged[key] = existing.model_copy(
                update={
                    "probability": max(existing.probability, candidate.probability),
                    "severity": self._highest_severity(existing.severity, candidate.severity),
                    "rationale": existing.rationale or candidate.rationale,
                    "sources": self._merge_sources(existing.sources, candidate.sources),
                },
                deep=True,
            )

        symptoms = self._append_unique(prev.symptoms_collected, symptoms_extracted)
        ranked = sorted(merged.values(), key=lambda item: item.probability, reverse=True)
        next_state = prev.model_copy(
            update={
                "diseases_ranked": ranked,
                "symptoms_collected": symptoms,
                "turn_count": prev.turn_count + 1,
                "last_updated": datetime.utcnow(),
            },
            deep=True,
        )
        return self._with_top_history(next_state)

    def apply_answer(
        self,
        prev: DiagnosticState,
        question: str,
        answer: str,
        discriminative_signal: DiscriminativeSignal,
    ) -> DiagnosticState:
        answer_is_present = self._answer_affirms_symptom(answer, discriminative_signal.symptom)
        expected_in = {self._key(name) for name in discriminative_signal.expected_in}
        expected_absent = {self._key(name) for name in discriminative_signal.expected_absent_in}

        kept: list[RankedDisease] = []
        newly_eliminated: list[EliminatedDisease] = []
        already_eliminated = {self._key(item.name): item for item in prev.eliminated}

        for disease in prev.diseases_ranked:
            key = self._key(disease.name)
            probability = self._updated_probability(
                disease.probability,
                key,
                answer_is_present,
                expected_in,
                expected_absent,
            )
            updated = disease.model_copy(update={"probability": probability}, deep=True)
            if updated.probability < 0.10:
                if key not in already_eliminated:
                    newly_eliminated.append(
                        EliminatedDisease(
                            **updated.model_dump(),
                            reason=(
                                f"Xác suất giảm dưới 0.10 sau câu trả lời cho triệu chứng "
                                f"'{discriminative_signal.symptom}'."
                            ),
                        )
                    )
                continue
            kept.append(updated)

        ranked = sorted(kept, key=lambda item: item.probability, reverse=True)
        next_state = prev.model_copy(
            update={
                "diseases_ranked": ranked,
                "eliminated": [*prev.eliminated, *newly_eliminated],
                "questions_asked": self._append_unique(prev.questions_asked, [question]),
                "turn_count": prev.turn_count + 1,
                "last_updated": datetime.utcnow(),
            },
            deep=True,
        )
        return self._with_top_history(next_state)

    def decide_phase(self, state: DiagnosticState) -> ChatPhase:
        if state.turn_count == 1:
            return "initial"

        top = state.diseases_ranked[0] if state.diseases_ranked else None
        stable = self._is_stable_for_two_turns(state)
        converged = bool(top and top.probability >= 0.85) or stable

        if state.turn_count >= 7 and not converged:
            return "needs_test"
        if top and top.probability >= 0.85:
            return "conclusion"
        if stable:
            return "conclusion"
        return "questioning"

    def _lookup_sources(self, disease: RankedDisease) -> list[str]:
        if self._source_lookup is not None:
            sources = [source for source in self._source_lookup(disease) if source]
            if sources:
                return sources
        return ["ai_inferred"]

    def _with_top_history(self, state: DiagnosticState) -> DiagnosticState:
        if not state.diseases_ranked:
            return state

        top = state.diseases_ranked[0]
        history = [
            *state.top_disease_history,
            TopDiseaseSnapshot(name=top.name, probability=top.probability),
        ][-2:]
        return state.model_copy(update={"top_disease_history": history}, deep=True)

    @staticmethod
    def _updated_probability(
        probability: float,
        disease_key: str,
        answer_is_present: bool,
        expected_in: set[str],
        expected_absent: set[str],
    ) -> float:
        delta = 0.0
        if answer_is_present:
            if disease_key in expected_in:
                delta += 0.15
            if disease_key in expected_absent:
                delta -= 0.20
        else:
            if disease_key in expected_in:
                delta -= 0.20
            if disease_key in expected_absent:
                delta += 0.10
        return max(0.0, min(1.0, probability + delta))

    @staticmethod
    def _answer_affirms_symptom(answer: str, symptom: str) -> bool:
        lowered = f" {answer.casefold()} "
        negative_markers = (" không ", " khong ", " chưa ", " chua ", " no ", " nope ")
        positive_markers = (" có ", " co ", " yes ", " đúng ", " dung ", " phải ", " phai ")
        if any(marker in lowered for marker in negative_markers):
            return False
        if any(marker in lowered for marker in positive_markers):
            return True
        return symptom.casefold() in lowered

    @staticmethod
    def _is_stable_for_two_turns(state: DiagnosticState) -> bool:
        if len(state.top_disease_history) < 2:
            return False
        previous, current = state.top_disease_history[-2], state.top_disease_history[-1]
        return (
            previous.name.casefold() == current.name.casefold()
            and abs(previous.probability - current.probability) <= 0.01
        )

    @staticmethod
    def _append_unique(existing: Iterable[str], new_values: Iterable[str]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for value in [*existing, *new_values]:
            cleaned = str(value).strip()
            if not cleaned:
                continue
            key = cleaned.casefold()
            if key not in seen:
                seen.add(key)
                result.append(cleaned)
        return result

    @staticmethod
    def _merge_sources(left: list[str], right: list[str]) -> list[str]:
        return DiagnosticStateManager._append_unique(left, right)

    @staticmethod
    def _highest_severity(left: str, right: str) -> str:
        rank = {"low": 0, "medium": 1, "high": 2}
        return left if rank.get(left, 1) >= rank.get(right, 1) else right

    @staticmethod
    def _key(name: str) -> str:
        return " ".join(name.casefold().split())
