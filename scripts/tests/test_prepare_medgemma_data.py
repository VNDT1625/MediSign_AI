"""Unit tests for scripts.prepare_medgemma_data (Task 1.1)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_medgemma_data as pmd  # noqa: E402


# ---------------------------------------------------------------------------
# 1.1.1 Loaders
# ---------------------------------------------------------------------------

def _write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def test_load_iio_keeps_required_fields(tmp_path: Path) -> None:
    src = tmp_path / "iio.json"
    _write_json(src, [
        {"instruction": "I", "input": " hi ", "output": "ans", "source": "x"},
        {"instruction": "", "input": "no instr", "output": "ans"},  # default instruction
        {"input": "missing output", "output": ""},                   # filtered
        {"input": "", "output": "missing input"},                    # filtered
        "not a dict",                                                # filtered
    ])
    rows = pmd.load_iio(src, source_tag="iio.json")
    assert len(rows) == 2
    assert rows[0] == {"instruction": "I", "input": "hi", "output": "ans", "source": "x"}
    assert rows[1]["instruction"] == pmd.SYSTEM_INSTRUCTION
    assert rows[1]["source"] == "iio.json"


def test_load_qa_converts_question_answer_to_iio(tmp_path: Path) -> None:
    src = tmp_path / "qa.json"
    _write_json(src, [
        {"question": "Q1?", "answer": "A1", "source": "tag"},
        {"question": "Q2?", "answer": ""},      # filtered
        {"question": "", "answer": "A3"},       # filtered
    ])
    rows = pmd.load_qa(src, source_tag="qa.json")
    assert [r["input"] for r in rows] == ["Q1?"]
    assert rows[0]["instruction"] == pmd.SYSTEM_INSTRUCTION
    assert rows[0]["output"] == "A1"
    assert rows[0]["source"] == "tag"


def test_loaders_raise_when_top_level_is_not_a_list(tmp_path: Path) -> None:
    src = tmp_path / "bad.json"
    _write_json(src, {"not": "a list"})
    with pytest.raises(ValueError):
        pmd.load_iio(src, source_tag="bad")


# ---------------------------------------------------------------------------
# 1.1.3 Deduplicate
# ---------------------------------------------------------------------------

def test_deduplicate_keeps_first_occurrence_case_and_whitespace_insensitive() -> None:
    records = [
        {"instruction": "I", "input": "Hello world", "output": "first"},
        {"instruction": "I", "input": "  hello   WORLD  ", "output": "dup"},
        {"instruction": "I", "input": "Different", "output": "kept"},
    ]
    out = pmd.deduplicate(records)
    assert len(out) == 2
    assert out[0]["output"] == "first"
    assert out[1]["input"] == "Different"


# ---------------------------------------------------------------------------
# 1.1.4 Validity filter + minimum guarantee
# ---------------------------------------------------------------------------

def test_filter_valid_drops_empty_or_non_string_fields() -> None:
    records = [
        {"instruction": "I", "input": "ok", "output": "ans"},
        {"instruction": "I", "input": "   ", "output": "ans"},
        {"instruction": "I", "input": "ok2", "output": ""},
        {"instruction": "", "input": "ok3", "output": "ans"},
        {"instruction": "I", "input": "ok4", "output": None},
    ]
    out = pmd.filter_valid(records)
    assert [r["input"] for r in out] == ["ok"]


def test_ensure_minimum_raises_when_below_threshold() -> None:
    with pytest.raises(RuntimeError, match="at least 5"):
        pmd.ensure_minimum([{}], minimum=5)


def test_ensure_minimum_passes_when_at_threshold() -> None:
    pmd.ensure_minimum([{}] * 5, minimum=5)  # does not raise
