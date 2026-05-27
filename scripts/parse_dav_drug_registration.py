"""Parse DAV drug-registration PDFs into structured JSON.

The raw PDFs are downloaded under:
    data/training_raw/dav_drug_registration_2026/

Outputs:
    data/training_clean/dav_drug_records.json
    data/training_clean/dav_registered_drugs.json
    data/training_clean/dav_drug_parse_report.json

This parser is intentionally conservative. It keeps ``raw_row`` and source
metadata for every parsed table row so downstream cleaning can correct fields
without going back to the PDFs.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "training_raw" / "dav_drug_registration_2026"
MANIFEST_FILE = RAW_DIR / "manifest.json"
CLEAN_DIR = ROOT / "data" / "training_clean"
DRUG_DATABASE_FILE = CLEAN_DIR / "drug_database.json"
ALL_RECORDS_FILE = CLEAN_DIR / "dav_drug_records.json"
REGISTERED_FILE = CLEAN_DIR / "dav_registered_drugs.json"
HIGH_CONFIDENCE_FILE = CLEAN_DIR / "dav_registered_drugs_high_confidence.json"
EXPANDED_DRUG_DATABASE_FILE = CLEAN_DIR / "drug_database_expanded.json"
REPORT_FILE = CLEAN_DIR / "dav_drug_parse_report.json"


REGISTRATION_RE = re.compile(
    r"\b(?:\d{9,12}|VN-\d{1,5}-\d{2}|VD-\d{1,5}-\d{2}|QLSP-\d{1,5}-\d{2}|GC-\d{1,5}-\d{2})\b",
    re.IGNORECASE,
)
ROW_START_RE = re.compile(r"^\s*(\d{1,4})\s{2,}(?!Cơ sở|Phụ lục|DANH MỤC)(.*\S)?\s*$")
EXPECTED_COUNT_RE = re.compile(r"danh mục\s+(\d{1,4})\s+(?:thuốc|vắc xin|sinh phẩm)", re.IGNORECASE)


@dataclass(frozen=True)
class Columns:
    name: int
    ingredient: int
    dosage_form: int
    package: int
    standard: int | None
    shelf_life: int | None
    registration: int | None


def _clean_text(value: str) -> str:
    value = value.replace("\x00", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip(" -;\n\t")


def _append_field(record: dict, key: str, value: str) -> None:
    value = _clean_text(value)
    if not value:
        return
    if record.get(key):
        record[key] = _clean_text(f"{record[key]} {value}")
    else:
        record[key] = value


def _detect_columns(line: str, previous_line: str = "") -> Columns | None:
    if "STT" not in line or "Tên" not in line:
        return None
    header_context = f"{previous_line}\n{line}"
    name = line.find("Tên thuốc")
    if name < 0:
        name = line.find("Tên")
    ingredient = line.find("Hoạt chất")
    if ingredient < 0:
        # Some DAV tables wrap "Hoạt chất chính - Hàm" onto the line above
        # and leave only "lượng" on the STT line. In those cases the
        # ingredient column starts shortly after the name column.
        prev_ingredient = previous_line.find("Hoạt chất")
        ingredient = prev_ingredient if prev_ingredient >= 0 else name + 20
    dosage_form = line.find("Dạng", ingredient + 1)
    package = line.find("Quy cách", dosage_form + 1)
    standard = line.find("Tiêu", package + 1)
    shelf_life = line.find("Tuổi", package + 1)
    registration = line.find("Số đăng ký", package + 1)
    if min(name, ingredient, dosage_form, package) < 0:
        if "Hoạt chất" not in header_context and "Hàm" not in header_context:
            return None
        return None
    return Columns(
        name=name,
        ingredient=ingredient,
        dosage_form=dosage_form,
        package=package,
        standard=standard if standard >= 0 else None,
        shelf_life=shelf_life if shelf_life >= 0 else None,
        registration=registration if registration >= 0 else None,
    )


def _slice(line: str, start: int | None, end: int | None) -> str:
    if start is None or start < 0 or start >= len(line):
        return ""
    if end is None or end < 0:
        return line[start:]
    return line[start:end]


FIELD_ORDER = (
    "name",
    "active_ingredient_strength",
    "dosage_form",
    "package",
    "standard",
    "shelf_life_months",
    "registration_number",
)


def _column_positions(cols: Columns) -> list[tuple[str, int]]:
    positions: list[tuple[str, int]] = [
        ("name", cols.name),
        ("active_ingredient_strength", cols.ingredient),
        ("dosage_form", cols.dosage_form),
        ("package", cols.package),
    ]
    if cols.standard is not None:
        positions.append(("standard", cols.standard))
    if cols.shelf_life is not None:
        positions.append(("shelf_life_months", cols.shelf_life))
    if cols.registration is not None:
        positions.append(("registration_number", cols.registration))
    return sorted(positions, key=lambda item: item[1])


def _chunks_by_spacing(line: str) -> list[tuple[int, str]]:
    chunks: list[tuple[int, str]] = []
    for match in re.finditer(r"\S.*?(?=\s{2,}\S|\s*$)", line):
        text = match.group(0).strip()
        if text:
            chunks.append((match.start(), text))
    return chunks


def _assign_chunks_to_fields(line: str, cols: Columns, skip_stt: str | None = None) -> dict[str, str]:
    positions = _column_positions(cols)
    out = {field: "" for field in FIELD_ORDER}

    for start, text in _chunks_by_spacing(line):
        if skip_stt and text == skip_stt:
            continue
        if text in {"NSX", "TCNSX", "BP", "USP", "EP"}:
            field = "standard"
        elif REGISTRATION_RE.fullmatch(text):
            field = "registration_number"
        elif re.fullmatch(r"\d{1,3}", text) and start >= (cols.shelf_life or 10_000) - 8:
            field = "shelf_life_months"
        else:
            field = positions[0][0]
            for idx, (candidate, pos) in enumerate(positions):
                next_pos = positions[idx + 1][1] if idx + 1 < len(positions) else 10_000
                midpoint = (pos + next_pos) / 2
                if start < midpoint:
                    field = candidate
                    break
                field = candidate
        out[field] = _clean_text(f"{out[field]} {text}")

    return out


def _field_slices(line: str, cols: Columns, name_start: int | None = None) -> dict[str, str]:
    effective_name_start = cols.name if name_start is None else name_start
    return {
        "name": _slice(line, effective_name_start, cols.ingredient),
        "active_ingredient_strength": _slice(line, cols.ingredient, cols.dosage_form),
        "dosage_form": _slice(line, cols.dosage_form, cols.package),
        "package": _slice(line, cols.package, cols.standard or cols.shelf_life or cols.registration),
        "standard": _slice(line, cols.standard, cols.shelf_life) if cols.standard is not None else "",
        "shelf_life_months": _slice(line, cols.shelf_life, cols.registration) if cols.shelf_life is not None else "",
        "registration_number": _slice(line, cols.registration, None) if cols.registration is not None else "",
    }


def _continuation_slices(line: str, cols: Columns) -> dict[str, str]:
    """Slice a wrapped row line, allowing small PDF layout drift.

    pypdf's layout mode sometimes places continuation text a few characters
    before the detected column start. Without a tolerance, fragments like
    "4mg" from the ingredient column can be appended to the drug name.
    """
    return _assign_chunks_to_fields(line, cols)


def _row_start_fields(line: str, cols: Columns, stt: str) -> dict[str, str]:
    return _assign_chunks_to_fields(line, cols, skip_stt=stt)


def _document_category(title: str) -> tuple[str, str]:
    low = re.sub(r"\s+", " ", title.lower())
    if "thu hồi" in low:
        return "withdrawn", "revocation"
    if "tương đương sinh học" in low:
        return "reference", "bioequivalence"
    if "biệt dược gốc" in low:
        return "reference", "originator_brand"
    if "sinh phẩm tham chiếu" in low:
        return "reference", "reference_biologic"
    if "cấp" in low and "giấy đăng ký lưu hành" in low:
        return "active", "marketing_authorization_granted"
    if "gia hạn" in low and "giấy đăng ký lưu hành" in low:
        return "active", "marketing_authorization_renewed"
    return "unknown", "regulatory_list"


def _expected_count(title: str) -> int | None:
    match = EXPECTED_COUNT_RE.search(title)
    return int(match.group(1)) if match else None


def _extract_layout_text(pdf_path: Path) -> list[str]:
    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text(extraction_mode="layout") or "")
        except TypeError:
            pages.append(page.extract_text() or "")
    return pages


def _finalize_record(record: dict) -> dict | None:
    if not record:
        return None
    for key in (
        "name",
        "active_ingredient_strength",
        "dosage_form",
        "package",
        "standard",
        "shelf_life_months",
        "registration_number",
    ):
        record[key] = _clean_text(str(record.get(key, "")))

    reg_match = REGISTRATION_RE.search(record.get("registration_number", ""))
    if not reg_match:
        reg_match = REGISTRATION_RE.search(record.get("raw_row", ""))
    if reg_match:
        record["registration_number"] = reg_match.group(0)

    if record.get("shelf_life_months"):
        month_match = re.search(r"\b(\d{1,3})\b", record["shelf_life_months"])
        if month_match:
            record["shelf_life_months"] = int(month_match.group(1))

    if not record.get("name") and not record.get("registration_number"):
        return None
    record["parse_quality"] = _parse_quality(record)
    return record


def _parse_quality(record: dict) -> str:
    name = str(record.get("name", ""))
    ingredient = str(record.get("active_ingredient_strength", ""))
    dosage = str(record.get("dosage_form", ""))
    reg = str(record.get("registration_number", ""))

    suspicious_fragments = (
        "ng ký",
        "sản xuất",
        "địa chỉ",
        "công ty",
        "joint stock",
        "trách nhiệm",
        "phụ lục",
        "ghi chú",
    )
    if not REGISTRATION_RE.fullmatch(reg):
        return "low"
    if reg.isdigit() and len(reg) != 12:
        return "low"
    if not name or len(name) > 90 or any(fragment in name.lower() for fragment in suspicious_fragments):
        return "low"
    if not ingredient or not dosage:
        return "medium"
    return "high"


def parse_pdf_rows(item: dict) -> list[dict]:
    pdf_name = item.get("attachment_file")
    if not pdf_name or not pdf_name.lower().endswith(".pdf"):
        return []

    pdf_path = RAW_DIR / pdf_name
    if not pdf_path.exists():
        return []

    status, category = _document_category(item["title"])
    records: list[dict] = []
    next_id = 1

    for page_number, page_text in enumerate(_extract_layout_text(pdf_path), start=1):
        cols: Columns | None = None
        current: dict | None = None

        previous_line = ""
        for line in page_text.splitlines():
            if not line.strip():
                previous_line = line
                continue
            detected = _detect_columns(line, previous_line)
            if detected:
                if current:
                    final = _finalize_record(current)
                    if final:
                        records.append(final)
                    current = None
                cols = detected
                previous_line = line
                continue
            if cols is None:
                previous_line = line
                continue

            row_match = ROW_START_RE.match(line)
            if row_match and current is not None:
                candidate_stt = int(row_match.group(1))
                if candidate_stt != int(current["stt"]) + 1:
                    row_match = None
            if row_match:
                if current:
                    final = _finalize_record(current)
                    if final:
                        records.append(final)

                current = {
                    "id": f"dav-{Path(pdf_name).stem}-{next_id:04d}",
                    "stt": int(row_match.group(1)),
                    "source": "dav.gov.vn",
                    "source_title": item["title"],
                    "source_url": item.get("url"),
                    "source_pdf": pdf_name,
                    "source_page": page_number,
                    "record_status": status,
                    "regulatory_category": category,
                    "raw_row": _clean_text(line),
                }
                next_id += 1
                for key, value in _row_start_fields(line, cols, row_match.group(1)).items():
                    _append_field(current, key, value)
                previous_line = line
                continue

            if current is None:
                previous_line = line
                continue

            # Continuation lines are appended by column position. This keeps
            # wrapped ingredients, dosage forms, and package text together.
            current["raw_row"] = _clean_text(f"{current['raw_row']} {line}")
            for key, value in _continuation_slices(line, cols).items():
                _append_field(current, key, value)
            previous_line = line

        if current:
            final = _finalize_record(current)
            if final:
                records.append(final)

    return records


def dedupe_records(records: list[dict]) -> list[dict]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[dict] = []
    for rec in records:
        key = (
            str(rec.get("registration_number", "")).lower(),
            str(rec.get("name", "")).lower(),
            str(rec.get("source_pdf", "")).lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(rec)
    return deduped


def build_expanded_drug_database(dav_records: list[dict]) -> list[dict]:
    existing: list[dict] = []
    if DRUG_DATABASE_FILE.exists():
        existing = json.loads(DRUG_DATABASE_FILE.read_text(encoding="utf-8"))
        if not isinstance(existing, list):
            raise ValueError(f"{DRUG_DATABASE_FILE} must contain a JSON list")

    expanded: list[dict] = list(existing)
    seen_names = {str(item.get("name", "")).strip().lower() for item in expanded}
    seen_registration_numbers = {
        str(item.get("registration_number", "")).strip().lower()
        for item in expanded
        if item.get("registration_number")
    }

    for rec in dav_records:
        name = _clean_text(str(rec.get("name", "")))
        registration_number = _clean_text(str(rec.get("registration_number", "")))
        if not name:
            continue
        name_key = name.lower()
        reg_key = registration_number.lower()
        if reg_key and reg_key in seen_registration_numbers:
            continue
        if not reg_key and name_key in seen_names:
            continue

        description_parts = [
            f"Hoạt chất/hàm lượng: {rec.get('active_ingredient_strength')}" if rec.get("active_ingredient_strength") else "",
            f"Dạng bào chế: {rec.get('dosage_form')}" if rec.get("dosage_form") else "",
            f"Quy cách đóng gói: {rec.get('package')}" if rec.get("package") else "",
            f"Số đăng ký: {registration_number}" if registration_number else "",
            f"Nguồn: {rec.get('source_title')}" if rec.get("source_title") else "",
        ]
        expanded.append(
            {
                "name": name,
                "description": ". ".join(part for part in description_parts if part),
                "source": "dav.gov.vn",
                "active_ingredient_strength": rec.get("active_ingredient_strength", ""),
                "dosage_form": rec.get("dosage_form", ""),
                "package": rec.get("package", ""),
                "registration_number": registration_number,
                "record_status": rec.get("record_status", ""),
                "regulatory_category": rec.get("regulatory_category", ""),
                "parse_quality": rec.get("parse_quality", ""),
                "source_pdf": rec.get("source_pdf", ""),
                "source_url": rec.get("source_url", ""),
            }
        )
        seen_names.add(name_key)
        if reg_key:
            seen_registration_numbers.add(reg_key)

    return expanded


def main() -> None:
    if not MANIFEST_FILE.exists():
        raise FileNotFoundError(f"Missing manifest: {MANIFEST_FILE}")
    manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))

    all_records: list[dict] = []
    per_file: list[dict] = []
    for item in manifest.get("items", []):
        records = parse_pdf_rows(item)
        expected = _expected_count(item.get("title", ""))
        per_file.append(
            {
                "title": item.get("title"),
                "pdf": item.get("attachment_file"),
                "expected_count_from_title": expected,
                "parsed_count": len(records),
                "record_status": _document_category(item.get("title", ""))[0],
                "regulatory_category": _document_category(item.get("title", ""))[1],
            }
        )
        all_records.extend(records)

    all_records = dedupe_records(all_records)
    registered_records = [
        rec for rec in all_records if rec.get("record_status") == "active" and rec.get("registration_number")
    ]
    high_confidence_records = [
        rec for rec in registered_records if rec.get("parse_quality") == "high"
    ]

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    ALL_RECORDS_FILE.write_text(json.dumps(all_records, ensure_ascii=False, indent=2), encoding="utf-8")
    REGISTERED_FILE.write_text(json.dumps(registered_records, ensure_ascii=False, indent=2), encoding="utf-8")
    HIGH_CONFIDENCE_FILE.write_text(
        json.dumps(high_confidence_records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    expanded_database = build_expanded_drug_database(high_confidence_records)
    EXPANDED_DRUG_DATABASE_FILE.write_text(
        json.dumps(expanded_database, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    report = {
        "source_manifest": str(MANIFEST_FILE.relative_to(ROOT)),
        "all_records": len(all_records),
        "active_registered_records": len(registered_records),
        "active_registered_high_confidence_records": len(high_confidence_records),
        "expanded_drug_database_records": len(expanded_database),
        "records_with_registration_number": sum(1 for rec in all_records if rec.get("registration_number")),
        "records_by_parse_quality": {
            quality: sum(1 for rec in all_records if rec.get("parse_quality") == quality)
            for quality in sorted({str(rec.get("parse_quality")) for rec in all_records})
        },
        "records_by_status": {
            status: sum(1 for rec in all_records if rec.get("record_status") == status)
            for status in sorted({str(rec.get("record_status")) for rec in all_records})
        },
        "records_by_category": {
            category: sum(1 for rec in all_records if rec.get("regulatory_category") == category)
            for category in sorted({str(rec.get("regulatory_category")) for rec in all_records})
        },
        "per_file": per_file,
        "outputs": {
            "all_records": str(ALL_RECORDS_FILE.relative_to(ROOT)),
            "active_registered": str(REGISTERED_FILE.relative_to(ROOT)),
            "active_registered_high_confidence": str(HIGH_CONFIDENCE_FILE.relative_to(ROOT)),
            "expanded_drug_database": str(EXPANDED_DRUG_DATABASE_FILE.relative_to(ROOT)),
            "report": str(REPORT_FILE.relative_to(ROOT)),
        },
        "notes": [
            "Fields are parsed from PDF layout text and should be treated as best-effort.",
            "raw_row and source metadata are preserved for audit and manual correction.",
            "dav_registered_drugs.json excludes revocation/reference-only documents.",
        ],
    }
    REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
