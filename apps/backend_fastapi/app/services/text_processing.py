from __future__ import annotations

import re
import unicodedata

_WORD_RE = re.compile(r"[a-z0-9]+")


def normalize_text(text: str) -> str:
    lowered = text.strip().lower().replace("đ", "d")
    without_marks = "".join(
        char for char in unicodedata.normalize("NFD", lowered) if unicodedata.category(char) != "Mn"
    )
    words = _WORD_RE.findall(without_marks)
    return " ".join(words)


def tokenize(text: str) -> list[str]:
    normalized = normalize_text(text)
    if not normalized:
        return []
    return normalized.split(" ")


def find_phrase_starts(tokens: list[str], phrase_tokens: list[str]) -> list[int]:
    if not tokens or not phrase_tokens or len(tokens) < len(phrase_tokens):
        return []

    phrase_size = len(phrase_tokens)
    starts: list[int] = []
    for index in range(len(tokens) - phrase_size + 1):
        if tokens[index : index + phrase_size] == phrase_tokens:
            starts.append(index)
    return starts
