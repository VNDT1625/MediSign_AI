from app.schemas.medicine import MedicineScanRequest, MedicineScanResponse
from app.services.text_processing import find_phrase_starts, normalize_text, tokenize

_PARACETAMOL_PHRASES = (("paracetamol",), ("acetaminophen",))
_IBUPROFEN_PHRASES = (("ibuprofen",),)
_ALCOHOL_PHRASES = (("alcohol",), ("ruou",), ("bia",), ("ethanol",))
_ASPIRIN_PHRASES = (("aspirin",),)
_RISK_SCORE = {"low": 0, "medium": 1, "high": 2}


def _contains_any_phrase(tokens: list[str], phrases: tuple[tuple[str, ...], ...]) -> bool:
    for phrase_tokens in phrases:
        if find_phrase_starts(tokens, list(phrase_tokens)):
            return True
    return False


def _contains_any_phrase_in_many(
    token_groups: list[list[str]], phrases: tuple[tuple[str, ...], ...]
) -> bool:
    return any(_contains_any_phrase(tokens, phrases) for tokens in token_groups)


def _upgrade_risk(current: str, candidate: str) -> str:
    if _RISK_SCORE[candidate] > _RISK_SCORE[current]:
        return candidate
    return current


def scan_medicine(payload: MedicineScanRequest) -> MedicineScanResponse:
    normalized_name = " ".join(payload.extracted_text.split()).title()
    warnings: list[str] = []
    risk_level = "low"

    extracted_tokens = tokenize(payload.extracted_text)
    medication_token_groups = [
        tokenize(item) for item in payload.current_medications if normalize_text(item)
    ]

    has_paracetamol = _contains_any_phrase(extracted_tokens, _PARACETAMOL_PHRASES)
    has_ibuprofen = _contains_any_phrase(extracted_tokens, _IBUPROFEN_PHRASES)
    has_alcohol = _contains_any_phrase_in_many(medication_token_groups, _ALCOHOL_PHRASES)
    has_aspirin = _contains_any_phrase_in_many(medication_token_groups, _ASPIRIN_PHRASES)

    if has_paracetamol and has_alcohol:
        risk_level = _upgrade_risk(risk_level, "high")
        warnings.append("Canh bao tuong tac voi ruou bia.")

    if has_ibuprofen and has_aspirin:
        risk_level = _upgrade_risk(risk_level, "medium")
        warnings.append("Canh bao nguy co kich ung da day khi dung cung aspirin.")

    if not warnings:
        warnings.append("Khong phat hien canh bao lon trong du lieu mau.")

    return MedicineScanResponse(
        normalized_name=normalized_name,
        risk_level=risk_level,
        warnings=warnings,
        guidance="Xac minh voi duoc si hoac bac si truoc khi dung thuoc.",
    )
