"""Merge crawled disease records into the RAG knowledge base.

This script intentionally does not touch drug records. It only reads the
Vinmec/HelloBacsi disease crawl outputs and appends normalized
``vietnam_common_disease`` records that can feed RAG #1/#2/#3.

Usage:
    python scripts/merge_kb.py --dry-run
    python scripts/merge_kb.py
    python scripts/merge_kb.py --limit 100 --output data/knowledge_base/knowledge_base.preview.json
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
KB_PATH = ROOT / "data" / "knowledge_base" / "knowledge_base.json"
VINMEC_PATH = ROOT / "diseases_vinmec.json"
HELLOBACSI_PATH = ROOT / "diseases_hellobacsi.json"

DISEASE_TYPE = "vietnam_common_disease"
LAST_UPDATED = "2026-05-19"

RED_FLAG_PATTERNS = (
    "khó thở",
    "đau ngực",
    "lơ mơ",
    "li bì",
    "mất ý thức",
    "ngất",
    "co giật",
    "yếu liệt",
    "méo miệng",
    "nói khó",
    "ho ra máu",
    "nôn ra máu",
    "đi ngoài ra máu",
    "phân đen",
    "chảy máu",
    "sốt cao",
    "sốt trên 39",
    "đau dữ dội",
    "nôn liên tục",
    "sụt cân",
    "vàng da",
    "vàng mắt",
    "tiểu ít",
    "tay chân lạnh",
)

HIGH_SEVERITY_NAME_PATTERNS = (
    "ung thư",
    "đột quỵ",
    "nhồi máu",
    "suy tim",
    "suy thận",
    "sốc",
    "nhiễm trùng huyết",
    "viêm màng não",
)


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    return [item for item in data if isinstance(item, dict)]


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _fold(value: str) -> str:
    text = unicodedata.normalize("NFD", value.lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.replace("đ", "d")


def _slug(value: str) -> str:
    folded = _fold(value)
    folded = re.sub(r"[^a-z0-9]+", "-", folded).strip("-")
    return folded[:96] or "unknown"


def _dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        cleaned = _clean(value)
        key = _fold(cleaned)
        if not cleaned or key in seen:
            continue
        seen.add(key)
        out.append(cleaned)
    return out


def _extract_red_flags(symptoms: list[str]) -> list[str]:
    flags: list[str] = []
    for symptom in symptoms:
        folded = _fold(symptom)
        if any(_fold(pattern) in folded for pattern in RED_FLAG_PATTERNS):
            flags.append(symptom)
    return _dedupe_keep_order(flags)[:8]


def _severity(name: str, source_severity: str, red_flags: list[str]) -> str:
    folded_name = _fold(name)
    folded_source = _fold(source_severity)
    if any(_fold(pattern) in folded_name for pattern in HIGH_SEVERITY_NAME_PATTERNS):
        return "high"
    if red_flags and "nhe" not in folded_source:
        return "high"
    if "nhe" in folded_source and not red_flags:
        return "low"
    return "medium"


def _home_care(severity: str) -> list[str]:
    if severity == "high":
        return [
            "Không tự điều trị khi có dấu hiệu nặng; nên đi khám trực tiếp sớm.",
            "Theo dõi nhiệt độ, nhịp thở, mức độ tỉnh táo và triệu chứng tăng nhanh.",
        ]
    return [
        "Nghỉ ngơi, uống đủ nước và theo dõi diễn tiến triệu chứng.",
        "Đi khám nếu triệu chứng kéo dài, nặng hơn hoặc xuất hiện dấu hiệu cảnh báo.",
    ]


def _lab_tests(severity: str) -> list[str]:
    if severity == "high":
        return [
            "Khám bác sĩ để được chỉ định xét nghiệm hoặc chẩn đoán hình ảnh phù hợp.",
            "Đánh giá cấp cứu nếu có dấu hiệu nguy hiểm.",
        ]
    return ["Khám bác sĩ nếu triệu chứng không cải thiện để được chỉ định xét nghiệm phù hợp."]


def normalize_crawled_disease(raw: dict[str, Any]) -> dict[str, Any] | None:
    name = _clean(raw.get("name"))
    symptoms = _dedupe_keep_order([str(item) for item in raw.get("symptoms") or []])
    if not name or not symptoms:
        return None

    red_flags = _extract_red_flags(symptoms)
    source_severity = _clean(raw.get("severity"))
    severity = _severity(name, source_severity, red_flags)
    if severity == "high" and not red_flags:
        red_flags = ["Triệu chứng nặng lên nhanh hoặc ảnh hưởng hô hấp, tuần hoàn, ý thức."]

    source_name = _clean(raw.get("source")) or "crawled"
    url = _clean(raw.get("url"))
    causes = _clean(raw.get("causes"))
    home_care = _home_care(severity)
    lab_tests = _lab_tests(severity)
    record_id = f"disease:{_slug(name)}"

    content_parts = [
        f"{name}: triệu chứng thường gặp gồm {', '.join(symptoms[:8])}.",
        f"Dấu hiệu cần khám gấp: {', '.join(red_flags)}." if red_flags else "",
        f"Nguyên nhân/yếu tố liên quan: {causes}" if causes else "",
        f"Khuyến nghị: {home_care[0]}",
    ]

    structured = {
        "name": name,
        "severity": severity,
        "source_severity": source_severity,
        "common_symptoms": symptoms,
        "symptoms": symptoms,
        "red_flags": red_flags,
        "home_care": home_care,
        "lab_tests": lab_tests,
        "causes": causes,
    }

    return {
        "id": record_id,
        "type": DISEASE_TYPE,
        "title": name,
        "aliases": [name],
        "content": " ".join(part for part in content_parts if part),
        "severity": severity,
        "symptoms": symptoms,
        "red_flags": red_flags,
        "home_care": home_care,
        "lab_tests": lab_tests,
        "structured": structured,
        "source": {"type": "crawled_public_health", "name": source_name, "url": url},
        "last_updated": LAST_UPDATED,
        "confidence": "medium",
        "needs_medical_review": True,
    }


def load_crawled_diseases(
    vinmec_path: Path = VINMEC_PATH,
    hellobacsi_path: Path = HELLOBACSI_PATH,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in (vinmec_path, hellobacsi_path):
        for raw in _read_json_list(path):
            normalized = normalize_crawled_disease(raw)
            if normalized:
                records.append(normalized)
    return records


def merge_records(
    kb_records: list[dict[str, Any]],
    disease_records: list[dict[str, Any]],
    limit: int | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    existing_ids = {str(record.get("id")) for record in kb_records}
    existing_titles = {
        _fold(str(record.get("title") or record.get("structured", {}).get("name") or ""))
        for record in kb_records
        if record.get("type") == DISEASE_TYPE
    }

    merged = list(kb_records)
    added = 0
    skipped_duplicate = 0
    severity_counts: Counter[str] = Counter()

    for record in disease_records:
        if limit is not None and added >= limit:
            break
        title_key = _fold(record["title"])
        if record["id"] in existing_ids or title_key in existing_titles:
            skipped_duplicate += 1
            continue
        merged.append(record)
        existing_ids.add(record["id"])
        existing_titles.add(title_key)
        severity_counts[record["severity"]] += 1
        added += 1

    stats = {
        "input_kb_records": len(kb_records),
        "candidate_disease_records": len(disease_records),
        "added_disease_records": added,
        "skipped_duplicate_diseases": skipped_duplicate,
        "output_kb_records": len(merged),
        "severity_counts_added": dict(severity_counts),
    }
    return merged, stats


def merge_kb(
    kb_path: Path = KB_PATH,
    output_path: Path | None = None,
    dry_run: bool = False,
    limit: int | None = None,
) -> dict[str, Any]:
    kb_records = _read_json_list(kb_path)
    disease_records = load_crawled_diseases()
    merged, stats = merge_records(kb_records, disease_records, limit=limit)

    if not dry_run:
        _write_json(output_path or kb_path, merged)
    return stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kb-path", type=Path, default=KB_PATH)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stats = merge_kb(
        kb_path=args.kb_path,
        output_path=args.output,
        dry_run=args.dry_run,
        limit=args.limit,
    )
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    if args.dry_run:
        print("Dry run only; knowledge_base.json was not modified.")


if __name__ == "__main__":
    main()
