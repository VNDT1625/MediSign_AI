"""Convert Vietnamese ICD-10 JSONL data to the app schema.

Input is expected from the cloned brightohir repository. The script prefers
the full `icd10_vn.jsonl` file when present and falls back to the committed
sample file.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


DEFAULT_INPUTS = (
    Path("data/external/brightohir/src/brightohir/data/vn/icd10_vn.jsonl"),
    Path("data/external/brightohir/src/brightohir/data/vn/icd10_vn.sample.jsonl"),
)
DEFAULT_JSON_OUTPUT = Path("data/processed/icd10_vn_schema.json")
DEFAULT_CSV_OUTPUT = Path("data/processed/icd10_vn_schema.csv")


def resolve_input(explicit_input: str | None) -> Path:
    if explicit_input:
        path = Path(explicit_input)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")
        return path

    for path in DEFAULT_INPUTS:
        if path.exists():
            return path

    expected = ", ".join(str(path) for path in DEFAULT_INPUTS)
    raise FileNotFoundError(f"No ICD-10 input found. Expected one of: {expected}")


def convert_row(row: dict[str, object]) -> dict[str, str]:
    return {
        "icd_code": str(row.get("code") or "").strip(),
        "name_vi": str(row.get("display_vi") or "").strip(),
        "name_en": str(row.get("display_en") or "").strip(),
        "category": str(row.get("block_name") or row.get("chapter_name") or "").strip(),
    }


def load_jsonl(path: Path) -> list[dict[str, str]]:
    converted: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on {path}:{line_number}: {exc}") from exc

            item = convert_row(row)
            if not item["icd_code"] or not item["name_vi"]:
                raise ValueError(f"Missing required code/name_vi on {path}:{line_number}")
            converted.append(item)

    return converted


def write_json(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(rows, file, ensure_ascii=False, indent=2)
        file.write("\n")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=("icd_code", "name_vi", "name_en", "category"),
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="Path to icd10_vn JSONL input")
    parser.add_argument("--json-output", default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--csv-output", default=DEFAULT_CSV_OUTPUT)
    args = parser.parse_args()

    input_path = resolve_input(args.input)
    rows = load_jsonl(input_path)
    write_json(Path(args.json_output), rows)
    write_csv(Path(args.csv_output), rows)
    print(f"Converted {len(rows)} ICD-10 rows from {input_path}")
    print(f"JSON: {args.json_output}")
    print(f"CSV: {args.csv_output}")


if __name__ == "__main__":
    main()
