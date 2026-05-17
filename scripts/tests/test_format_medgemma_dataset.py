"""Unit tests for scripts.format_medgemma_dataset (Tasks 1.3 & 1.4)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import format_medgemma_dataset as fmd  # noqa: E402

CHAT_RE = re.compile(
    r"^<start_of_turn>user\n.+?<end_of_turn>\n"
    r"<start_of_turn>model\n.+?<end_of_turn>$",
    re.DOTALL,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_records(n: int) -> list[dict]:
    """Build a tiny synthetic corpus. Half the records already include a
    disclaimer variant so we exercise both branches of `ensure_disclaimer`."""
    records: list[dict] = []
    for i in range(n):
        if i % 2 == 0:
            output = f"Trả lời {i}. Thông tin chỉ mang tính tham khảo."
        else:
            output = f"Trả lời {i}."
        records.append(
            {
                "instruction": "Bạn là MediSign AI - trợ lý y tế thông minh.",
                "input": f"Câu hỏi số {i}?",
                "output": output,
                "source": "synthetic",
            }
        )
    return records


# ---------------------------------------------------------------------------
# 1.3.1 Chat template formatting
# ---------------------------------------------------------------------------

def test_build_chat_text_matches_exact_regex() -> None:
    text = fmd.build_chat_text("INSTR", "INPUT", "OUTPUT")
    assert CHAT_RE.match(text), f"Chat template mismatch: {text!r}"


def test_build_chat_text_embeds_system_instruction_and_user_input() -> None:
    text = fmd.build_chat_text("System rule", "User question", "Model answer")
    assert "<start_of_turn>user\nSystem rule\n\nUser question<end_of_turn>" in text
    assert "<start_of_turn>model\nModel answer<end_of_turn>" in text


def test_build_chat_text_handles_empty_instruction() -> None:
    text = fmd.build_chat_text("", "Just a question", "Answer")
    assert text.startswith("<start_of_turn>user\nJust a question<end_of_turn>")


# ---------------------------------------------------------------------------
# 1.3.2 Disclaimer enforcement
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "existing",
    [
        "Bạn nên tham khảo ý kiến bác sĩ trước khi dùng.",
        "Đây là gợi ý sơ bộ, không thay thế chẩn đoán bác sĩ",
        "Information chỉ mang tính tham khảo, hãy hỏi bác sĩ.",
        "Please consult a doctor before taking this medication.",
        "This information is not a substitute for professional medical advice.",
    ],
)
def test_ensure_disclaimer_keeps_outputs_with_existing_variants(existing: str) -> None:
    out, appended = fmd.ensure_disclaimer(existing)
    assert appended is False
    assert out == existing.rstrip()


def test_ensure_disclaimer_appends_canonical_when_missing() -> None:
    src = "Uống Paracetamol 500mg mỗi 6 giờ khi sốt."
    out, appended = fmd.ensure_disclaimer(src)
    assert appended is True
    assert fmd.CANONICAL_DISCLAIMER in out
    assert out.startswith(src)


def test_ensure_disclaimer_does_not_double_append() -> None:
    src = f"Một trả lời.\n\n{fmd.CANONICAL_DISCLAIMER}"
    out, appended = fmd.ensure_disclaimer(src)
    assert appended is False
    assert out.count(fmd.CANONICAL_DISCLAIMER) == 1


def test_ensure_disclaimer_handles_empty_output() -> None:
    out, appended = fmd.ensure_disclaimer("")
    assert appended is True
    assert out == fmd.CANONICAL_DISCLAIMER


# ---------------------------------------------------------------------------
# 1.4 Train/eval split — ratios, determinism, no overlap
# ---------------------------------------------------------------------------

def test_split_ratios_are_90_10_within_rounding() -> None:
    records = _make_records(1000)
    train, eval_ = fmd.split_train_eval(records, train_ratio=0.9, seed=42)
    assert len(train) == 900
    assert len(eval_) == 100
    assert len(train) + len(eval_) == len(records)


def test_split_is_deterministic_for_same_seed() -> None:
    records = _make_records(257)  # not a multiple of 10 to exercise rounding
    train_a, eval_a = fmd.split_train_eval(records, seed=42)
    train_b, eval_b = fmd.split_train_eval(records, seed=42)
    assert [r["input"] for r in train_a] == [r["input"] for r in train_b]
    assert [r["input"] for r in eval_a] == [r["input"] for r in eval_b]


def test_split_changes_with_different_seed() -> None:
    records = _make_records(500)
    train_a, _ = fmd.split_train_eval(records, seed=42)
    train_b, _ = fmd.split_train_eval(records, seed=7)
    # Highly unlikely two different seeds produce identical orderings.
    assert [r["input"] for r in train_a] != [r["input"] for r in train_b]


def test_split_has_no_overlap_and_covers_every_record() -> None:
    records = _make_records(333)
    train, eval_ = fmd.split_train_eval(records, seed=42)
    train_keys = {r["input"] for r in train}
    eval_keys = {r["input"] for r in eval_}
    all_keys = {r["input"] for r in records}

    assert train_keys.isdisjoint(eval_keys)
    assert train_keys | eval_keys == all_keys
    assert len(train_keys) + len(eval_keys) == len(records)


def test_split_does_not_mutate_input_list() -> None:
    records = _make_records(50)
    snapshot = [r["input"] for r in records]
    fmd.split_train_eval(records, seed=42)
    assert [r["input"] for r in records] == snapshot


# ---------------------------------------------------------------------------
# End-to-end: every formatted record passes the chat regex AND has a disclaimer
# ---------------------------------------------------------------------------

def test_format_records_produces_chat_text_and_universal_disclaimer() -> None:
    records = _make_records(100)
    formatted, added, already = fmd.format_records(records)
    assert added + already == len(records)
    for rec in formatted:
        assert CHAT_RE.match(rec["text"]), rec["text"]
        # Each output must contain *some* disclaimer variant.
        assert fmd.has_disclaimer(rec["output"]), rec["output"]
        # Traceability fields preserved.
        assert {"instruction", "input", "output", "source"} <= rec.keys()


# ---------------------------------------------------------------------------
# format_dataset() — full pipeline writes to disk correctly
# ---------------------------------------------------------------------------

def test_format_dataset_writes_train_eval_and_stats(tmp_path: Path) -> None:
    src_records = _make_records(50)
    input_file = tmp_path / "merged.json"
    input_file.write_text(json.dumps(src_records, ensure_ascii=False), encoding="utf-8")

    train_file = tmp_path / "train.jsonl"
    eval_file = tmp_path / "eval.jsonl"
    stats_file = tmp_path / "format_stats.json"

    stats = fmd.format_dataset(
        input_file=input_file,
        train_file=train_file,
        eval_file=eval_file,
        stats_file=stats_file,
        train_ratio=0.9,
        seed=42,
    )

    train_lines = train_file.read_text(encoding="utf-8").strip().splitlines()
    eval_lines = eval_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(train_lines) == stats["train"] == 45
    assert len(eval_lines) == stats["eval"] == 5
    assert stats["total"] == 50
    assert stats["disclaimer_added"] + stats["disclaimer_already_present"] == 50

    # Every record line must be valid JSON and pass the regex.
    train_recs = [json.loads(line) for line in train_lines]
    eval_recs = [json.loads(line) for line in eval_lines]
    for rec in train_recs + eval_recs:
        assert CHAT_RE.match(rec["text"])
        assert fmd.has_disclaimer(rec["output"])

    # Stats file matches return value.
    on_disk = json.loads(stats_file.read_text(encoding="utf-8"))
    assert on_disk["total"] == stats["total"]
    assert on_disk["train"] == stats["train"]
    assert on_disk["eval"] == stats["eval"]


def test_format_dataset_is_byte_identical_across_runs(tmp_path: Path) -> None:
    src_records = _make_records(80)
    input_file = tmp_path / "merged.json"
    input_file.write_text(json.dumps(src_records, ensure_ascii=False), encoding="utf-8")

    def _run(out_dir: Path) -> tuple[str, str]:
        out_dir.mkdir(parents=True, exist_ok=True)
        fmd.format_dataset(
            input_file=input_file,
            train_file=out_dir / "train.jsonl",
            eval_file=out_dir / "eval.jsonl",
            stats_file=out_dir / "stats.json",
            train_ratio=0.9,
            seed=42,
        )
        return (
            (out_dir / "train.jsonl").read_text(encoding="utf-8"),
            (out_dir / "eval.jsonl").read_text(encoding="utf-8"),
        )

    train1, eval1 = _run(tmp_path / "run_a")
    train2, eval2 = _run(tmp_path / "run_b")
    assert train1 == train2
    assert eval1 == eval2
