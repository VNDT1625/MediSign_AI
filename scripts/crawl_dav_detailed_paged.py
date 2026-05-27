"""Crawl 10k+ detailed DAV drug registration records via the public paging API.

This is faster and more complete than enriching one registration number at a
time because the public grid endpoint already returns ingredient, strength,
dosage form, package, manufacturer, registrant, and registration dates.

Outputs:
    data/training_raw/dav_congbothuoc_api_paged/raw_pages.jsonl
    data/training_clean/dav_detailed_drugs_10k.json
    data/training_clean/drug_database_dav_detailed_10k.json
    data/training_clean/dav_detailed_paged_report.json
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
from pathlib import Path

from enrich_dav_drug_details import (
    CLEAN_DIR,
    ROOT,
    build_detailed_drug_database,
    flatten_item,
)


RAW_DIR = ROOT / "data" / "training_raw" / "dav_congbothuoc_api_paged"
RAW_PAGES_FILE = RAW_DIR / "raw_pages.jsonl"
DETAILS_FILE = CLEAN_DIR / "dav_detailed_drugs_10k.json"
DETAILED_DB_FILE = CLEAN_DIR / "drug_database_dav_detailed_10k.json"
REPORT_FILE = CLEAN_DIR / "dav_detailed_paged_report.json"

API_URL = "https://dichvucong.dav.gov.vn/api/services/app/soDangKy/GetAllPublicServerPaging"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (MediSign detailed data crawl)",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def load_pages() -> dict[int, dict]:
    pages: dict[int, dict] = {}
    if not RAW_PAGES_FILE.exists():
        return pages
    with RAW_PAGES_FILE.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            pages[int(rec["skip_count"])] = rec
    return pages


def call_page(skip_count: int, page_size: int) -> dict:
    payload = {
        "filterText": "",
        "SoDangKyThuoc": {},
        "KichHoat": True,
        "skipCount": skip_count,
        "maxResultCount": page_size,
        "sorting": None,
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=HEADERS,
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        body = response.read().decode("utf-8", errors="replace")
    data = json.loads(body)
    result = data.get("result") or {}
    return {
        "skip_count": skip_count,
        "page_size": page_size,
        "success": bool(data.get("success")),
        "total_count": int(result.get("totalCount") or 0),
        "items": result.get("items") or [],
    }


def flatten_pages(pages: dict[int, dict]) -> list[dict]:
    details: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for skip in sorted(pages):
        page = pages[skip]
        for item in page.get("items") or []:
            rec = flatten_item(item, query=f"paged:{skip}")
            key = (
                str(rec.get("registration_number", "")).lower(),
                str(rec.get("old_registration_number", "")).lower(),
                str(rec.get("name", "")).lower(),
            )
            if key in seen:
                continue
            seen.add(key)
            details.append(rec)
    return details


def count_complete(details: list[dict]) -> int:
    return sum(1 for rec in details if rec.get("active_ingredient") and rec.get("dosage_form"))


def write_outputs(pages: dict[int, dict], target_complete: int, page_size: int) -> dict:
    details = flatten_pages(pages)
    detailed_db = build_detailed_drug_database(details)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    DETAILS_FILE.write_text(json.dumps(details, ensure_ascii=False, indent=2), encoding="utf-8")
    DETAILED_DB_FILE.write_text(json.dumps(detailed_db, ensure_ascii=False, indent=2), encoding="utf-8")
    report = {
        "source": API_URL,
        "target_complete_records": target_complete,
        "page_size": page_size,
        "pages_cached": len(pages),
        "api_total_count": max((page.get("total_count", 0) for page in pages.values()), default=0),
        "raw_items": sum(len(page.get("items") or []) for page in pages.values()),
        "detailed_records": len(details),
        "records_with_active_ingredient": sum(1 for rec in details if rec.get("active_ingredient")),
        "records_with_dosage_form": sum(1 for rec in details if rec.get("dosage_form")),
        "records_with_active_ingredient_and_dosage_form": count_complete(details),
        "drug_database_dav_detailed_10k_records": len(detailed_db),
        "outputs": {
            "raw_pages": str(RAW_PAGES_FILE.relative_to(ROOT)),
            "details": str(DETAILS_FILE.relative_to(ROOT)),
            "drug_database": str(DETAILED_DB_FILE.relative_to(ROOT)),
            "report": str(REPORT_FILE.relative_to(ROOT)),
        },
    }
    REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> None:
    target_complete = int(os.getenv("DAV_DETAILED_TARGET", "10000"))
    page_size = int(os.getenv("DAV_DETAILED_PAGE_SIZE", "200"))
    delay = float(os.getenv("DAV_DETAILED_DELAY", "0.02"))
    refresh = os.getenv("DAV_DETAILED_REFRESH", "").lower() in {"1", "true", "yes"}

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    pages = {} if refresh else load_pages()
    mode = "w" if refresh else "a"

    details = flatten_pages(pages)
    complete = count_complete(details)
    next_skip = 0
    if pages:
        next_skip = max(pages) + page_size

    with RAW_PAGES_FILE.open(mode, encoding="utf-8") as fh:
        while complete < target_complete:
            if next_skip in pages:
                next_skip += page_size
                continue
            page = call_page(next_skip, page_size)
            pages[next_skip] = page
            fh.write(json.dumps(page, ensure_ascii=False))
            fh.write("\n")
            fh.flush()

            details = flatten_pages(pages)
            complete = count_complete(details)
            total = page.get("total_count", 0)
            print(
                f"skip={next_skip} raw_items={sum(len(p.get('items') or []) for p in pages.values())} "
                f"details={len(details)} complete={complete}/{target_complete} total={total}"
            )
            if not page.get("items") or (total and next_skip + page_size >= total):
                break
            next_skip += page_size
            if delay:
                time.sleep(delay)

    report = write_outputs(pages, target_complete=target_complete, page_size=page_size)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
