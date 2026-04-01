from app.schemas.triage import TriageRequest, TriageResponse
from app.services.text_processing import find_phrase_starts, tokenize

_EMERGENCY_PHRASES = (
    ("kho", "tho"),
    ("dau", "nguc"),
    ("ngat",),
)
_URGENT_PHRASES = (
    ("sot", "cao"),
    ("dau", "nhieu"),
    ("met", "moi"),
)
_NEGATION_TOKENS = {"khong", "ko", "chua"}


def _has_non_negated_phrase(tokens: list[str], phrase_tokens: tuple[str, ...]) -> bool:
    for start in find_phrase_starts(tokens, list(phrase_tokens)):
        left_window = tokens[max(0, start - 4) : start]
        if any(token in _NEGATION_TOKENS for token in left_window):
            continue
        return True
    return False


def _classify_urgency(symptom_text: str) -> str:
    tokens = tokenize(symptom_text)

    if any(_has_non_negated_phrase(tokens, phrase) for phrase in _EMERGENCY_PHRASES):
        return "emergency"

    if any(_has_non_negated_phrase(tokens, phrase) for phrase in _URGENT_PHRASES):
        return "urgent"

    return "non_emergency"


def build_triage_result(payload: TriageRequest) -> TriageResponse:
    urgency_level = _classify_urgency(payload.symptom_text)

    recommendations = [
        "Theo doi trieu chung trong 24 gio.",
        "Uong du nuoc va nghi ngoi.",
        "Lien he co so y te neu trieu chung tang len.",
    ]

    if urgency_level == "emergency":
        recommendations = [
            "Goi cap cuu 115 hoac den benh vien gan nhat ngay.",
            "Khong tu y dung thuoc chua ro nguon goc.",
        ]

    return TriageResponse(
        urgency_level=urgency_level,
        summary="Thong tin mang tinh tham khao, khong thay the chan doan bac si.",
        recommendations=recommendations,
    )
