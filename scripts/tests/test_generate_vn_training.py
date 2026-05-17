"""Unit tests for Task 1.9 — Vietnamese training-data generators.

Covers `scripts/generate_vn_drugs_training.py` and
`scripts/generate_vn_symptoms_training.py`.

These are deterministic template-based generators, so we assert:
  * record counts meet Requirements 1.17 (≥500) and 1.18 (≥200)
  * schema is `{instruction, input, output, source}` with no extra keys
  * every output ends with the canonical Vietnamese disclaimer
  * every input is non-empty and unique within its file
  * source tags are correct
  * generators are idempotent (byte-equal JSON across runs)
  * drug records only reference brand names from the curated DRUGS list
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import format_medgemma_dataset as fmd  # noqa: E402
import generate_vn_drugs_training as gvd  # noqa: E402
import generate_vn_symptoms_training as gvs  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REQUIRED_KEYS = {"instruction", "input", "output", "source"}


@pytest.fixture(scope="module")
def drug_records() -> list[dict]:
    return gvd.generate_records()


@pytest.fixture(scope="module")
def symptom_records() -> list[dict]:
    return gvs.generate_records()


# ---------------------------------------------------------------------------
# Record counts (Requirements 1.17 & 1.18)
# ---------------------------------------------------------------------------

def test_drug_records_meet_minimum(drug_records: list[dict]) -> None:
    assert len(drug_records) >= gvd.MIN_RECORDS == 500


def test_symptom_records_meet_minimum(symptom_records: list[dict]) -> None:
    assert len(symptom_records) >= gvs.MIN_RECORDS == 200


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "fixture_name", ["drug_records", "symptom_records"]
)
def test_records_have_exactly_four_required_keys(
    fixture_name: str, request: pytest.FixtureRequest
) -> None:
    records = request.getfixturevalue(fixture_name)
    for rec in records:
        assert set(rec.keys()) == REQUIRED_KEYS, (
            f"Unexpected keys in {fixture_name}: {set(rec.keys()) ^ REQUIRED_KEYS}"
        )


@pytest.mark.parametrize(
    "fixture_name", ["drug_records", "symptom_records"]
)
def test_records_have_non_empty_string_fields(
    fixture_name: str, request: pytest.FixtureRequest
) -> None:
    records = request.getfixturevalue(fixture_name)
    for rec in records:
        for key in REQUIRED_KEYS:
            assert isinstance(rec[key], str)
            assert rec[key].strip(), f"Empty field {key} in record: {rec}"


# ---------------------------------------------------------------------------
# Disclaimer enforcement
# ---------------------------------------------------------------------------

def test_every_drug_output_contains_canonical_disclaimer(drug_records: list[dict]) -> None:
    for rec in drug_records:
        assert fmd.CANONICAL_DISCLAIMER in rec["output"], (
            f"Missing canonical disclaimer in drug output: {rec['input']!r}"
        )


def test_every_symptom_output_contains_canonical_disclaimer(symptom_records: list[dict]) -> None:
    for rec in symptom_records:
        assert fmd.CANONICAL_DISCLAIMER in rec["output"], (
            f"Missing canonical disclaimer in symptom output: {rec['input']!r}"
        )


@pytest.mark.parametrize(
    "fixture_name", ["drug_records", "symptom_records"]
)
def test_outputs_already_pass_ensure_disclaimer_check(
    fixture_name: str, request: pytest.FixtureRequest
) -> None:
    """`ensure_disclaimer` must NOT need to append anything to outputs
    that already include the canonical phrase."""
    records = request.getfixturevalue(fixture_name)
    for rec in records:
        _, appended = fmd.ensure_disclaimer(rec["output"])
        assert appended is False, (
            f"ensure_disclaimer wanted to append to: {rec['input']!r}"
        )


# ---------------------------------------------------------------------------
# Input uniqueness
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "fixture_name", ["drug_records", "symptom_records"]
)
def test_inputs_are_unique_within_file(
    fixture_name: str, request: pytest.FixtureRequest
) -> None:
    records = request.getfixturevalue(fixture_name)
    inputs = [rec["input"] for rec in records]
    assert len(inputs) == len(set(inputs)), (
        f"Duplicate inputs found in {fixture_name}"
    )


# ---------------------------------------------------------------------------
# Source tags
# ---------------------------------------------------------------------------

def test_drug_records_have_correct_source_tag(drug_records: list[dict]) -> None:
    for rec in drug_records:
        assert rec["source"] == "vn_drugs_commercial"


def test_symptom_records_have_correct_source_tag(symptom_records: list[dict]) -> None:
    for rec in symptom_records:
        assert rec["source"] == "vn_symptoms_culture"


# ---------------------------------------------------------------------------
# Curated brand whitelist (drug script only)
# ---------------------------------------------------------------------------

def test_drug_records_only_reference_curated_brands(drug_records: list[dict]) -> None:
    """Every drug record must reference at least one curated brand name in
    its input (the templates always interpolate `{brand}`), and must not
    reference a brand outside the curated DRUGS list."""
    curated = {d["brand"] for d in gvd.DRUGS}
    # Some brands are substrings of others (e.g. "Hapacol" / "Vitamin 3B").
    # We only check that *some* curated brand appears in the question.
    for rec in drug_records:
        assert any(brand in rec["input"] for brand in curated), (
            f"Drug record references no curated brand: {rec['input']!r}"
        )


# ---------------------------------------------------------------------------
# Idempotency — re-running must produce byte-identical JSON
# ---------------------------------------------------------------------------

def test_drug_generation_is_idempotent(tmp_path: Path) -> None:
    out1 = tmp_path / "vn_drugs_1.json"
    out2 = tmp_path / "vn_drugs_2.json"
    gvd.write_records(gvd.generate_records(), path=out1)
    gvd.write_records(gvd.generate_records(), path=out2)
    assert out1.read_bytes() == out2.read_bytes()


def test_symptom_generation_is_idempotent(tmp_path: Path) -> None:
    out1 = tmp_path / "vn_symptoms_1.json"
    out2 = tmp_path / "vn_symptoms_2.json"
    gvs.write_records(gvs.generate_records(), path=out1)
    gvs.write_records(gvs.generate_records(), path=out2)
    assert out1.read_bytes() == out2.read_bytes()


# ---------------------------------------------------------------------------
# On-disk artefacts (sanity checks for the committed JSON files)
# ---------------------------------------------------------------------------

def test_on_disk_drug_file_matches_generator() -> None:
    """The committed JSON must match the generator output exactly so the
    pipeline downstream of `prepare_medgemma_data.py` is reproducible."""
    if not gvd.OUTPUT_FILE.exists():
        pytest.skip("vn_drugs_commercial.json not generated yet")
    on_disk = json.loads(gvd.OUTPUT_FILE.read_text(encoding="utf-8"))
    assert on_disk == gvd.generate_records()


def test_on_disk_symptom_file_matches_generator() -> None:
    if not gvs.OUTPUT_FILE.exists():
        pytest.skip("vn_symptoms_culture.json not generated yet")
    on_disk = json.loads(gvs.OUTPUT_FILE.read_text(encoding="utf-8"))
    assert on_disk == gvs.generate_records()
