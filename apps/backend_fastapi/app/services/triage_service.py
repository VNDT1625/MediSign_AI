from app.schemas.triage import TriageRequest, TriageResponse
from app.services.text_processing import find_phrase_starts, tokenize

_EMERGENCY_PHRASES = (
    # Hô hấp / Tim mạch
    ("kho", "tho"),
    ("dau", "nguc"),
    ("ngat",),
    ("kho", "khe"),          # khò khè nặng (hen phế quản)
    ("moi", "tim"),          # môi tím
    # Thần kinh / Đột quỵ
    ("co", "giat"),          # co giật
    ("noi", "ngong"),        # nói ngọng (đột quỵ)
    ("liet",),               # liệt
    ("bat", "tinh"),         # bất tỉnh
    ("hon", "me"),           # hôn mê
    ("khong", "tinh",),      # không tỉnh — NOTE: handled separately (negation exception)
    # Xuất huyết
    ("non", "mau"),          # nôn ra máu
    ("phan", "den"),         # phân đen (XH tiêu hóa)
    ("ra", "mau"),           # ra máu (nhiều ngữ cảnh)
    # Ngộ độc / Tai nạn
    ("ngo", "doc"),          # ngộ độc
    ("dien", "giat"),        # điện giật
    ("nuot", "pin"),         # nuốt dị vật nguy hiểm
    # Thần kinh / Não
    ("cung", "co"),          # cứng cổ (viêm màng não)
    ("xuat", "huyet"),       # xuất huyết
    # Nội tiết / Huyết áp
    ("duong", "huyet"),      # đường huyết (kết hợp với ngữ cảnh thấp)
    ("huyet", "ap"),         # huyết áp (kết hợp với ngữ cảnh cao)
    # Sản khoa
    ("mang", "thai"),        # mang thai + đau/ra máu — handled by context
    # Tổng quát
    ("khong", "phan", "xa"), # không phản xạ
    ("tho", "yeu"),          # thở yếu
    ("run", "tay"),          # run tay (hạ đường huyết)
    ("lo", "mo"),            # lơ mơ
    # Đột quỵ / Thần kinh bổ sung
    ("mat", "meo"),          # mặt méo (đột quỵ)
    ("tay", "yeu"),          # tay yếu (đột quỵ)
    ("noi", "kho"),          # nói khó (đột quỵ)
    # Bụng ngoại khoa
    ("bung", "cung"),        # bụng cứng (thủng tạng)
    ("bung", "goc"),         # bụng cứng như gỗ
    # Ngộ độc bổ sung
    ("thuoc", "tru", "sau"), # thuốc trừ sâu
    ("uong", "nham"),        # uống nhầm
    # Đau đầu dữ dội đột ngột
    ("dau", "dau", "du", "doi"), # đau đầu dữ dội
    ("dot", "ngot"),         # đột ngột (kết hợp với đau đầu)
)

# Các cụm từ đơn token cần match chính xác (không cần phrase)
_EMERGENCY_SINGLE_TOKENS = frozenset({
    "ngat",      # ngất
    "liet",      # liệt
    "dotquy",    # đột quỵ (sau normalize)
})

_URGENT_PHRASES = (
    ("sot", "cao"),
    ("dau", "nhieu"),
    ("met", "moi"),
    ("buon", "non"),
    ("tieu", "chay"),
    ("dau", "dau", "du", "doi"),  # đau đầu dữ dội
    ("vang", "da"),               # vàng da
    ("kho", "nuot"),              # khó nuốt
)
_NEGATION_TOKENS = {"khong", "ko", "chua"}

# Các token đặc biệt — LUÔN là emergency dù có negation hay không
# (vì "không tỉnh", "không phản xạ" vẫn là emergency)
_ALWAYS_EMERGENCY_TOKENS = frozenset({
    "ngat",
    "co", "giat",
    "liet",
    "hon", "me",
})


def _has_non_negated_phrase(tokens: list[str], phrase_tokens: tuple[str, ...]) -> bool:
    for start in find_phrase_starts(tokens, list(phrase_tokens)):
        left_window = tokens[max(0, start - 4) : start]
        if any(token in _NEGATION_TOKENS for token in left_window):
            continue
        return True
    return False


def _classify_urgency(symptom_text: str) -> str:
    tokens = tokenize(symptom_text)

    # Kiểm tra emergency phrases (có xét negation)
    if any(_has_non_negated_phrase(tokens, phrase) for phrase in _EMERGENCY_PHRASES):
        return "emergency"

    # Kiểm tra thêm: "không tỉnh", "không phản xạ" — vẫn là emergency
    token_set = set(tokens)
    if "tinh" in token_set and "khong" in token_set:
        return "emergency"
    if "phan" in token_set and "xa" in token_set and "khong" in token_set:
        return "emergency"

    # "đau đầu dữ dội" + "đột ngột" = xuất huyết não
    if "dau" in token_set and "doi" in token_set and "dot" in token_set:
        return "emergency"

    # "bụng cứng" = thủng tạng rỗng
    if "bung" in token_set and ("cung" in token_set or "goc" in token_set):
        return "emergency"

    # Ngộ độc: "uống nhầm" hoặc "thuốc trừ sâu"
    if "nham" in token_set and "uong" in token_set:
        return "emergency"
    if "sau" in token_set and "tru" in token_set:
        return "emergency"

    # Đột quỵ: "mặt méo" hoặc ("tay yếu" + "nói khó")
    if "meo" in token_set and ("mat" in token_set or "noi" in token_set):
        return "emergency"

    if any(_has_non_negated_phrase(tokens, phrase) for phrase in _URGENT_PHRASES):
        return "urgent"

    return "non_emergency"


def build_triage_result(payload: TriageRequest) -> TriageResponse:
    urgency_level = _classify_urgency(payload.symptom_text)

    # ── Mode-aware recommendations ────────────────────────────────────────────
    # local mode: minimal, privacy-first — no AI enrichment, shorter advice.
    # hybrid / cloud: full recommendations (same logic for now; cloud path
    # reserved for future Gemini/GPT integration).
    if payload.mode == "local":
        if urgency_level == "emergency":
            recommendations = [
                "Gọi cấp cứu 115 hoặc đến bệnh viện gần nhất ngay.",
                "Không tự ý dùng thuốc chưa rõ nguồn gốc.",
            ]
            summary = "⚠️ Triệu chứng nghiêm trọng — cần cấp cứu ngay. (Chế độ riêng tư)"
        elif urgency_level == "urgent":
            recommendations = [
                "Đến cơ sở y tế trong 1–2 ngày.",
                "Theo dõi triệu chứng và ghi lại diễn biến.",
            ]
            summary = "Triệu chứng cần được khám sớm. (Chế độ riêng tư)"
        else:
            recommendations = [
                "Theo dõi triệu chứng trong 24 giờ.",
                "Uống đủ nước và nghỉ ngơi.",
            ]
            summary = "Triệu chứng nhẹ, có thể theo dõi tại nhà. (Chế độ riêng tư)"
    else:
        # hybrid / cloud — full advice
        if urgency_level == "emergency":
            recommendations = [
                "Gọi cấp cứu 115 hoặc đến bệnh viện gần nhất ngay.",
                "Không tự ý dùng thuốc chưa rõ nguồn gốc.",
                "Nhờ người thân hoặc hàng xóm hỗ trợ ngay lập tức.",
            ]
            summary = "⚠️ Triệu chứng có dấu hiệu nghiêm trọng — cần cấp cứu ngay. Thông tin mang tính tham khảo, không thay thế chẩn đoán bác sĩ."
        elif urgency_level == "urgent":
            recommendations = [
                "Đến cơ sở y tế trong 1–2 ngày.",
                "Theo dõi triệu chứng và ghi lại diễn biến.",
                "Uống đủ nước, nghỉ ngơi và tránh tự ý dùng thuốc.",
                "Liên hệ cơ sở y tế nếu triệu chứng tăng lên.",
            ]
            summary = "Triệu chứng cần được khám sớm. Thông tin mang tính tham khảo, không thay thế chẩn đoán bác sĩ."
        else:
            recommendations = [
                "Theo dõi triệu chứng trong 24 giờ.",
                "Uống đủ nước và nghỉ ngơi.",
                "Liên hệ cơ sở y tế nếu triệu chứng tăng lên.",
            ]
            summary = "Triệu chứng nhẹ, có thể theo dõi tại nhà. Thông tin mang tính tham khảo, không thay thế chẩn đoán bác sĩ."

    return TriageResponse(
        urgency_level=urgency_level,
        summary=summary,
        recommendations=recommendations,
    )
