from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_output_format_samples as gofs  # noqa: E402
import generate_vi_oars_samples as oars  # noqa: E402
import merge_kb  # noqa: E402


def test_normalize_crawled_disease_produces_rag_schema() -> None:
    raw = {
        "name": "Bệnh thử nghiệm",
        "symptoms": ["sốt cao", "khó thở", "mệt"],
        "causes": "Nhiễm trùng",
        "severity": "nặng",
        "source": "test",
        "url": "https://example.test",
    }

    record = merge_kb.normalize_crawled_disease(raw)

    assert record is not None
    assert record["type"] == "vietnam_common_disease"
    assert record["severity"] == "high"
    assert record["red_flags"]
    assert record["home_care"]
    assert record["lab_tests"]
    assert record["structured"]["common_symptoms"] == ["sốt cao", "khó thở", "mệt"]


def test_merge_records_skips_existing_disease_titles() -> None:
    existing = [{"id": "disease:benh-a", "type": "vietnam_common_disease", "title": "Bệnh A"}]
    candidates = [
        {"id": "disease:benh-a", "type": "vietnam_common_disease", "title": "Bệnh A", "severity": "low"},
        {"id": "disease:benh-b", "type": "vietnam_common_disease", "title": "Bệnh B", "severity": "medium"},
    ]

    merged, stats = merge_kb.merge_records(existing, candidates)

    assert len(merged) == 2
    assert stats["added_disease_records"] == 1
    assert stats["skipped_duplicate_diseases"] == 1


def test_generate_output_format_records_from_minimal_kb(tmp_path: Path) -> None:
    kb = [
        {
            "id": "disease:test",
            "type": "vietnam_common_disease",
            "title": "Viêm họng thử nghiệm",
            "severity": "medium",
            "symptoms": ["đau họng", "sốt nhẹ", "ho khan"],
            "red_flags": ["khó thở"],
            "home_care": ["Uống đủ nước"],
            "lab_tests": ["Khám bác sĩ nếu kéo dài"],
            "structured": {
                "common_symptoms": ["đau họng", "sốt nhẹ", "ho khan"],
                "severity": "medium",
                "red_flags": ["khó thở"],
                "home_care": ["Uống đủ nước"],
                "lab_tests": ["Khám bác sĩ nếu kéo dài"],
            },
        }
    ]
    kb_path = tmp_path / "kb.json"
    kb_path.write_text(json.dumps(kb, ensure_ascii=False), encoding="utf-8")

    records = gofs.generate_records(target=3, kb_path=kb_path)

    assert len(records) == 3
    assert {record["triage_level"] for record in records} == {"green", "yellow"}
    for record in records:
        assert record["source"] == "generated_output_format"
        assert "Kết luận:" in record["output"]
        assert gofs.DISCLAIMER in record["output"]
        assert "<start_of_turn>user" in record["text"]
        assert "<start_of_turn>model" in record["text"]


def test_template_oars_sample_validates() -> None:
    sample = oars._template_sample(oars.VI_TOPICS[0], 0, oars.random.Random(42))

    ok, reason = oars._validate_sample(sample)

    assert ok, reason
    assert sample["source"] == "generated_vi_oars_template"
    assert oars._to_medgemma_text(sample["messages"]).startswith("<start_of_turn>user")
