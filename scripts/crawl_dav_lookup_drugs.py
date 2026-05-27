"""Crawl DAV's HTML drug lookup pages into JSON.

Source:
    https://dav.gov.vn/tra-cuu-thuoc.html

Outputs:
    data/training_raw/dav_drug_lookup_html/page*.html
    data/training_clean/dav_lookup_drugs.json
    data/training_clean/drug_database_10k.json
    data/training_clean/dav_lookup_crawl_report.json
"""
from __future__ import annotations

import json
import os
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "training_raw" / "dav_drug_lookup_html"
CLEAN_DIR = ROOT / "data" / "training_clean"
LOOKUP_FILE = CLEAN_DIR / "dav_lookup_drugs.json"
DB_10K_FILE = CLEAN_DIR / "drug_database_10k.json"
DB_10K_FULL_FILE = CLEAN_DIR / "drug_database_10k_full.json"
REPORT_FILE = CLEAN_DIR / "dav_lookup_crawl_report.json"
EXPANDED_DB_FILE = CLEAN_DIR / "drug_database_expanded.json"
LEGACY_DB_FILE = CLEAN_DIR / "drug_database.json"

BASE_URL = "https://dav.gov.vn"
FIRST_PAGE_URL = f"{BASE_URL}/tra-cuu-thuoc.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (MediSign data pipeline)",
    "Accept": "text/html,*/*",
}


def _fetch(url: str, timeout: int = 45) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def _page_url(page: int) -> str:
    if page <= 1:
        return FIRST_PAGE_URL
    return f"{BASE_URL}/tra-cuu-thuoc-page{page}.html"


def _clean_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def detect_last_page(html: str) -> int:
    matches = re.findall(r"tra-cuu-thuoc-page(\d+)\.html", html)
    return max([1, *(int(match) for match in matches)])


def parse_lookup_rows(html: str, page: int, source_url: str) -> list[dict]:
    tbody_match = re.search(r"<tbody>(.*?)</tbody>", html, re.IGNORECASE | re.DOTALL)
    if not tbody_match:
        return []

    rows: list[dict] = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tbody_match.group(1), re.IGNORECASE | re.DOTALL):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.IGNORECASE | re.DOTALL)
        if len(cells) < 8:
            continue

        attachment_match = re.search(r'href=["\']([^"\']+)["\']', cells[7], re.IGNORECASE)
        attachment_url = ""
        if attachment_match:
            attachment_url = urllib.parse.urljoin(source_url, unescape(attachment_match.group(1)))

        record = {
            "source": "dav.gov.vn",
            "source_url": source_url,
            "source_page": page,
            "row_number": _clean_html(cells[0]),
            "receipt_number": _clean_html(cells[1]),
            "receipt_year": _clean_html(cells[2]),
            "name": _clean_html(cells[3]),
            "registrant_company": _clean_html(cells[4]),
            "advertising_info_type": _clean_html(cells[5]),
            "registration_number": _clean_html(cells[6]),
            "attachment_url": attachment_url,
        }
        if record["name"] or record["registration_number"]:
            rows.append(record)
    return rows


def _read_json_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    return data


def dedupe_lookup(records: list[dict]) -> list[dict]:
    seen: set[tuple[str, str, str, str]] = set()
    out: list[dict] = []
    for rec in records:
        key = (
            _normalize(rec.get("registration_number", "")),
            _normalize(rec.get("name", "")),
            _normalize(rec.get("receipt_number", "")),
            _normalize(rec.get("receipt_year", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(rec)
    return out


def build_drug_database_10k(lookup_records: list[dict]) -> list[dict]:
    base = _read_json_list(EXPANDED_DB_FILE) or _read_json_list(LEGACY_DB_FILE)
    db = list(base)
    seen = {
        (
            _normalize(item.get("registration_number", "")),
            _normalize(item.get("name", "")),
        )
        for item in db
    }

    for rec in lookup_records:
        name = rec.get("name", "")
        registration_number = rec.get("registration_number", "")
        if not name:
            continue
        key = (_normalize(registration_number), _normalize(name))
        if key in seen:
            continue
        description_parts = [
            f"Số đăng ký: {registration_number}" if registration_number else "",
            f"Công ty đăng ký thông tin/quảng cáo: {rec.get('registrant_company')}" if rec.get("registrant_company") else "",
            f"Loại hình thông tin/quảng cáo: {rec.get('advertising_info_type')}" if rec.get("advertising_info_type") else "",
            f"Số giấy tiếp nhận: {rec.get('receipt_number')}/{rec.get('receipt_year')}"
            if rec.get("receipt_number") or rec.get("receipt_year")
            else "",
        ]
        db.append(
            {
                "name": name,
                "description": ". ".join(part for part in description_parts if part),
                "source": "dav.gov.vn",
                "registration_number": registration_number,
                "registrant_company": rec.get("registrant_company", ""),
                "advertising_info_type": rec.get("advertising_info_type", ""),
                "receipt_number": rec.get("receipt_number", ""),
                "receipt_year": rec.get("receipt_year", ""),
                "source_url": rec.get("source_url", ""),
                "attachment_url": rec.get("attachment_url", ""),
            }
        )
        seen.add(key)
    return db


def build_drug_database_10k_full(lookup_records: list[dict]) -> list[dict]:
    """Build a lookup DB that preserves every DAV lookup row.

    ``drug_database_10k.json`` dedupes by name/registration for cleaner lookup.
    This full variant keeps each official DAV lookup row as a separate sample,
    which is useful when the requirement is 10k+ crawled medicine-name records.
    """
    base = _read_json_list(EXPANDED_DB_FILE) or _read_json_list(LEGACY_DB_FILE)
    db = list(base)

    for rec in lookup_records:
        name = rec.get("name", "")
        registration_number = rec.get("registration_number", "")
        if not name:
            continue
        description_parts = [
            f"Số đăng ký: {registration_number}" if registration_number else "",
            f"Công ty đăng ký thông tin/quảng cáo: {rec.get('registrant_company')}" if rec.get("registrant_company") else "",
            f"Loại hình thông tin/quảng cáo: {rec.get('advertising_info_type')}" if rec.get("advertising_info_type") else "",
            f"Số giấy tiếp nhận: {rec.get('receipt_number')}/{rec.get('receipt_year')}"
            if rec.get("receipt_number") or rec.get("receipt_year")
            else "",
        ]
        db.append(
            {
                "name": name,
                "description": ". ".join(part for part in description_parts if part),
                "source": "dav.gov.vn",
                "registration_number": registration_number,
                "registrant_company": rec.get("registrant_company", ""),
                "advertising_info_type": rec.get("advertising_info_type", ""),
                "receipt_number": rec.get("receipt_number", ""),
                "receipt_year": rec.get("receipt_year", ""),
                "source_url": rec.get("source_url", ""),
                "source_page": rec.get("source_page", ""),
                "row_number": rec.get("row_number", ""),
                "attachment_url": rec.get("attachment_url", ""),
                "lookup_record_id": (
                    f"dav-lookup-{rec.get('source_page', '')}-"
                    f"{rec.get('row_number', '')}-{rec.get('receipt_number', '')}-"
                    f"{rec.get('receipt_year', '')}"
                ),
            }
        )
    return db


def crawl(max_pages: int | None = None, delay_seconds: float = 0.05, refresh: bool = False) -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    first_page_path = RAW_DIR / "page1.html"
    if refresh or not first_page_path.exists():
        first_html = _fetch(FIRST_PAGE_URL)
        first_page_path.write_text(first_html, encoding="utf-8")
    else:
        first_html = first_page_path.read_text(encoding="utf-8")

    last_page = detect_last_page(first_html)
    if max_pages is not None:
        last_page = min(last_page, max_pages)

    all_rows: list[dict] = []
    pages_ok = 0
    pages_failed: list[dict] = []

    for page in range(1, last_page + 1):
        path = RAW_DIR / f"page{page}.html"
        url = _page_url(page)
        try:
            if refresh or not path.exists():
                html = _fetch(url)
                path.write_text(html, encoding="utf-8")
                if delay_seconds:
                    time.sleep(delay_seconds)
            else:
                html = path.read_text(encoding="utf-8")
            rows = parse_lookup_rows(html, page=page, source_url=url)
            all_rows.extend(rows)
            pages_ok += 1
            if page % 25 == 0 or page == last_page:
                print(f"page {page}/{last_page}: total rows {len(all_rows)}")
        except Exception as exc:  # keep the crawl resumable
            pages_failed.append({"page": page, "url": url, "error": str(exc)})
            print(f"WARN page {page}: {exc}")

    deduped = dedupe_lookup(all_rows)
    db_10k = build_drug_database_10k(deduped)
    db_10k_full = build_drug_database_10k_full(deduped)

    LOOKUP_FILE.write_text(json.dumps(deduped, ensure_ascii=False, indent=2), encoding="utf-8")
    DB_10K_FILE.write_text(json.dumps(db_10k, ensure_ascii=False, indent=2), encoding="utf-8")
    DB_10K_FULL_FILE.write_text(json.dumps(db_10k_full, ensure_ascii=False, indent=2), encoding="utf-8")

    report = {
        "source": FIRST_PAGE_URL,
        "last_page_detected": detect_last_page(first_html),
        "pages_attempted": last_page,
        "pages_ok": pages_ok,
        "pages_failed": pages_failed,
        "raw_rows": len(all_rows),
        "deduped_lookup_records": len(deduped),
        "drug_database_10k_records": len(db_10k),
        "drug_database_10k_full_records": len(db_10k_full),
        "outputs": {
            "lookup_records": str(LOOKUP_FILE.relative_to(ROOT)),
            "drug_database_10k": str(DB_10K_FILE.relative_to(ROOT)),
            "drug_database_10k_full": str(DB_10K_FULL_FILE.relative_to(ROOT)),
            "report": str(REPORT_FILE.relative_to(ROOT)),
            "raw_html_dir": str(RAW_DIR.relative_to(ROOT)),
        },
    }
    REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> None:
    max_pages_env = os.getenv("DAV_LOOKUP_MAX_PAGES")
    max_pages = int(max_pages_env) if max_pages_env else None
    refresh = os.getenv("DAV_LOOKUP_REFRESH", "").lower() in {"1", "true", "yes"}
    report = crawl(max_pages=max_pages, refresh=refresh)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
