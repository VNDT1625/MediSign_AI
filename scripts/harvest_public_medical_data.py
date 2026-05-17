"""Harvest public medical data for MediSign knowledge base.

This script fetches public/free sources that do not require a paid license:

- openFDA drug labels that contain drug interaction sections
- NIH ODS calcium/vitamin D reference tables (structured fallback)
- public Vietnamese guideline pages/PDFs from kcb.vn and selected BYT/NIN mirrors

It is resumable and writes normalized records under data/knowledge_base/public/.
DrugBank Clinical is intentionally not fetched here because it requires a paid
API/license key.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "data" / "knowledge_base" / "public"
RAW_DIR = PUBLIC_DIR / "raw"
PDF_DIR = RAW_DIR / "pdfs"
TEXT_DIR = RAW_DIR / "extracted_text"

USER_AGENT = "MediSignAIDataHarvester/1.0 (+public medical data research)"
OPENFDA_ENDPOINT = "https://api.fda.gov/drug/label.json"
OPENFDA_LIMIT = 100
OPENFDA_MAX_SKIP = 25_000
REQUEST_SLEEP = float(os.getenv("PUBLIC_DATA_REQUEST_SLEEP", "0.08"))
KCB_MAX_PAGES = int(os.getenv("KCB_MAX_PAGES", "600"))
DISCOVER_GUIDELINE_LINKS = os.getenv("DISCOVER_GUIDELINE_LINKS", "0") == "1"
WRITE_COMBINED_PUBLIC_KB = os.getenv("WRITE_COMBINED_PUBLIC_KB", "0") == "1"


KCB_SEED_URLS = [
    "https://kcb.vn/phac-do/huong-dan-chan-doan-va-dieu-tri-tang-huyet-ap.html",
    "https://kcb.vn/phac-do/h-uong-dan-chan-doan-va-dieu-tri-dai-thao-duong-type-2.html",
    "https://kcb.vn/thu-vien-tai-lieu/huong-dan-chan-doan-va-dieu-tri-benh-do-vi-rut-ebola.html",
    "https://kcb.vn/van-ban/huong-dan-chan-doan-va-dieu-tri-tang-huyet-ap.html",
    "https://kcb.vn/tin-tuc/cap-nhat-huong-dan-chan-doan-va-dieu-tri-covid-19-va-quan-ly-fo-tai-nha.html",
    "https://kcb.vn/tin-tuc/tap-huan-chan-doan-va-dieu-tri-benh-tay-chan-mieng-ung-pho-voi-dich-gia-tang.html",
    "https://kcb.vn/tin-tuc/tang-cuong-cong-tac-truyen-thong-kham-phan-loai-thu-dung-dieu-tri-va-kiem-soat-benh-tay-chan-mieng.html",
    "https://kcb.vn/tin-tuc/tang-cuong-cong-tac-dieu-tri-benh-tay-chan-mieng2.html",
]

NUTRITION_DOCUMENT_URLS = [
    "https://ods.od.nih.gov/factsheets/Calcium-HealthProfessional/",
    "https://ods.od.nih.gov/factsheets/VitaminD-HealthProfessional/",
    "https://file.hstatic.net/200000713511/file/nhu-cau-dinh-duong-khuyen-nghi-cho-nguoi-viet-nam-bo-y-te-2016_1351b03467f74a40a14580ae822b6e1c.pdf",
]


def _ensure_dirs() -> None:
    for path in [PUBLIC_DIR, RAW_DIR, PDF_DIR, TEXT_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _clean_text(value: Any, limit: int | None = None) -> str:
    if isinstance(value, list):
        value = "\n".join(str(item) for item in value)
    value = html.unescape(str(value or ""))
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    if limit and len(value) > limit:
        return value[:limit].rstrip()
    return value


def _request_json(url: str, retries: int = 4) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - retry network/API errors
            last_error = exc
            time.sleep((attempt + 1) * 1.5)
    raise RuntimeError(f"Failed JSON request: {url}") from last_error


def _request_bytes(url: str, retries: int = 4) -> bytes:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=90) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep((attempt + 1) * 1.5)
    raise RuntimeError(f"Failed byte request: {url}") from last_error


def _openfda_url(search: str, limit: int = 1, skip: int = 0) -> str:
    return f"{OPENFDA_ENDPOINT}?search={urllib.parse.quote(search, safe=':[]+')}&limit={limit}&skip={skip}"


def _openfda_total(search: str) -> int:
    url = _openfda_url(search, limit=1, skip=0)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return 0
        raise
    return int(data.get("meta", {}).get("results", {}).get("total") or 0)


def _date_to_int(date_value: dt.date) -> int:
    return int(date_value.strftime("%Y%m%d"))


def _split_date_range(start: dt.date, end: dt.date) -> tuple[tuple[dt.date, dt.date], tuple[dt.date, dt.date]]:
    days = (end - start).days
    mid = start + dt.timedelta(days=days // 2)
    return (start, mid), (mid + dt.timedelta(days=1), end)


def _build_openfda_ranges() -> list[dict[str, Any]]:
    ranges_path = PUBLIC_DIR / "openfda_interaction_ranges.json"
    cached = _read_json(ranges_path, [])
    if cached:
        return cached

    queue: list[tuple[dt.date, dt.date]] = [(dt.date(1900, 1, 1), dt.date(2026, 12, 31))]
    final: list[dict[str, Any]] = []
    while queue:
        start, end = queue.pop(0)
        search = f"_exists_:drug_interactions AND effective_time:[{_date_to_int(start)} TO {_date_to_int(end)}]"
        total = _openfda_total(search)
        if total == 0:
            continue
        if total > OPENFDA_MAX_SKIP + OPENFDA_LIMIT and start < end:
            left, right = _split_date_range(start, end)
            queue.extend([left, right])
            continue
        final.append({"start": start.isoformat(), "end": end.isoformat(), "search": search, "total": total})
        print(f"[openFDA] range {start}..{end}: {total}")
        time.sleep(REQUEST_SLEEP)
    _write_json(ranges_path, final)
    return final


def _normalize_openfda_label(row: dict[str, Any]) -> dict[str, Any]:
    openfda = row.get("openfda") or {}
    generic = _clean_text(openfda.get("generic_name") or row.get("generic_name"))
    brand = _clean_text(openfda.get("brand_name") or row.get("brand_name"))
    manufacturer = _clean_text(openfda.get("manufacturer_name") or row.get("labeler_name"))
    set_id = _clean_text(row.get("set_id") or row.get("id"))
    interaction_text = _clean_text(row.get("drug_interactions"), limit=12_000)
    contraindications = _clean_text(row.get("contraindications"), limit=6_000)
    warnings = _clean_text(row.get("warnings") or row.get("boxed_warning"), limit=8_000)
    title = " | ".join(part for part in [brand, generic, set_id] if part) or f"openFDA label {_sha(json.dumps(row, sort_keys=True))}"
    return {
        "id": f"openfda_interaction_label:{_sha(set_id or title)}",
        "type": "drug_interaction_label",
        "title": title,
        "aliases": [part for part in [brand, generic, manufacturer, set_id] if part],
        "content": interaction_text,
        "structured": {
            "brand_name": brand,
            "generic_name": generic,
            "manufacturer": manufacturer,
            "set_id": set_id,
            "effective_time": _clean_text(row.get("effective_time")),
            "version": _clean_text(row.get("version")),
            "drug_interactions": interaction_text,
            "contraindications": contraindications,
            "warnings": warnings,
            "rxcui": openfda.get("rxcui") or [],
            "unii": openfda.get("unii") or [],
            "spl_set_id": openfda.get("spl_set_id") or [],
        },
        "source": {
            "type": "public_drug_label",
            "name": "openFDA Drug Label API",
            "url": "https://api.fda.gov/drug/label.json",
        },
        "last_updated": "2026-05-17",
        "confidence": "medium",
        "needs_medical_review": True,
    }


def harvest_openfda_interaction_labels() -> list[dict[str, Any]]:
    raw_path = RAW_DIR / "openfda_interaction_labels_raw.jsonl"
    records_path = PUBLIC_DIR / "openfda_drug_interaction_labels.json"
    done_path = PUBLIC_DIR / "openfda_interaction_progress.json"
    progress = _read_json(done_path, {"done": []})
    done = set(progress.get("done") or [])
    records_by_id: dict[str, dict[str, Any]] = {
        item["id"]: item for item in _read_json(records_path, []) if isinstance(item, dict) and item.get("id")
    }

    ranges = _build_openfda_ranges()
    with raw_path.open("a", encoding="utf-8") as raw_fh:
        for range_info in ranges:
            search = range_info["search"]
            total = int(range_info["total"])
            for skip in range(0, total, OPENFDA_LIMIT):
                key = f"{range_info['start']}:{range_info['end']}:{skip}"
                if key in done:
                    continue
                url = _openfda_url(search, limit=OPENFDA_LIMIT, skip=skip)
                data = _request_json(url)
                results = data.get("results") or []
                for row in results:
                    raw_fh.write(json.dumps(row, ensure_ascii=False))
                    raw_fh.write("\n")
                    normalized = _normalize_openfda_label(row)
                    if normalized["content"]:
                        records_by_id[normalized["id"]] = normalized
                done.add(key)
                if len(done) % 100 == 0:
                    _write_json(records_path, list(records_by_id.values()))
                    _write_json(done_path, {"done": sorted(done), "record_count": len(records_by_id)})
                    print(f"[openFDA] pages={len(done)} labels={len(records_by_id)}")
                time.sleep(REQUEST_SLEEP)

    records = list(records_by_id.values())
    records.sort(key=lambda item: item["id"])
    _write_json(records_path, records)
    _write_json(done_path, {"done": sorted(done), "record_count": len(records)})
    return records


def build_nutrition_reference_records() -> list[dict[str, Any]]:
    # NIH ODS public tables, plus the Vietnam BYT/NIN PDF retained as a source
    # document for RAG. These rows are structured for lookup; PDF chunks below
    # preserve the full document context.
    rows = [
        ("calcium", "0-6 months", "all", 200, "mg/day", "AI", "NIH ODS Calcium Fact Sheet"),
        ("calcium", "7-12 months", "all", 260, "mg/day", "AI", "NIH ODS Calcium Fact Sheet"),
        ("calcium", "1-3 years", "all", 700, "mg/day", "RDA", "NIH ODS Calcium Fact Sheet"),
        ("calcium", "4-8 years", "all", 1000, "mg/day", "RDA", "NIH ODS Calcium Fact Sheet"),
        ("calcium", "9-13 years", "all", 1300, "mg/day", "RDA", "NIH ODS Calcium Fact Sheet"),
        ("calcium", "14-18 years", "male", 1300, "mg/day", "RDA", "NIH ODS Calcium Fact Sheet"),
        ("calcium", "14-18 years", "female", 1300, "mg/day", "RDA", "NIH ODS Calcium Fact Sheet"),
        ("calcium", "14-18 years pregnant", "female", 1300, "mg/day", "RDA", "NIH ODS Calcium Fact Sheet"),
        ("calcium", "14-18 years lactating", "female", 1300, "mg/day", "RDA", "NIH ODS Calcium Fact Sheet"),
        ("calcium", "19-50 years", "male", 1000, "mg/day", "RDA", "NIH ODS Calcium Fact Sheet"),
        ("calcium", "19-50 years", "female", 1000, "mg/day", "RDA", "NIH ODS Calcium Fact Sheet"),
        ("calcium", "19-50 years pregnant", "female", 1000, "mg/day", "RDA", "NIH ODS Calcium Fact Sheet"),
        ("calcium", "19-50 years lactating", "female", 1000, "mg/day", "RDA", "NIH ODS Calcium Fact Sheet"),
        ("calcium", "51-70 years", "male", 1000, "mg/day", "RDA", "NIH ODS Calcium Fact Sheet"),
        ("calcium", "51-70 years", "female", 1200, "mg/day", "RDA", "NIH ODS Calcium Fact Sheet"),
        ("calcium", ">70 years", "all", 1200, "mg/day", "RDA", "NIH ODS Calcium Fact Sheet"),
        ("vitamin_d", "0-12 months", "all", 10, "mcg/day", "AI", "NIH ODS Vitamin D Fact Sheet"),
        ("vitamin_d", "1-70 years", "all", 15, "mcg/day", "RDA", "NIH ODS Vitamin D Fact Sheet"),
        ("vitamin_d", ">70 years", "all", 20, "mcg/day", "RDA", "NIH ODS Vitamin D Fact Sheet"),
        ("vitamin_d", "pregnant/lactating", "female", 15, "mcg/day", "RDA", "NIH ODS Vitamin D Fact Sheet"),
    ]
    records = []
    for idx, (nutrient, age_group, sex, amount, unit, basis, source) in enumerate(rows, start=1):
        source_url = (
            "https://ods.od.nih.gov/factsheets/Calcium-HealthProfessional/"
            if nutrient == "calcium"
            else "https://ods.od.nih.gov/factsheets/VitaminD-HealthProfessional/"
        )
        records.append(
            {
                "id": f"nutrition_public:{nutrient}:{idx:03d}",
                "type": "nutrition_requirement",
                "title": f"{nutrient} {age_group} {sex}",
                "aliases": [nutrient, nutrient.replace("_", " "), age_group, "recommended intake"],
                "content": f"{source}: {nutrient} for {age_group}, {sex}: {amount} {unit} ({basis}).",
                "structured": {
                    "nutrient": nutrient,
                    "age_group": age_group,
                    "sex": sex,
                    "recommended_amount": amount,
                    "unit": unit,
                    "basis": basis,
                    "locale_basis": "international_fallback",
                },
                "source": {"type": "nutrition_fact_sheet", "name": source, "url": source_url},
                "last_updated": "2026-05-17",
                "confidence": "medium",
                "needs_medical_review": True,
            }
        )
    _write_json(PUBLIC_DIR / "nutrition_public_reference.json", records)
    return records


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.title_parts: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self._in_title = True
        if tag.lower() == "a":
            for key, value in attrs:
                if key.lower() == "href" and value:
                    self.links.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)


def _html_to_text(raw_html: str) -> str:
    text = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", raw_html)
    text = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h[1-6]>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _safe_name(url: str, suffix: str = "") -> str:
    parsed = urllib.parse.urlparse(url)
    base = Path(parsed.path).name or _sha(url)
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", urllib.parse.unquote(base)).strip("-")
    if suffix and not base.lower().endswith(suffix):
        base += suffix
    return f"{_sha(url)}_{base}"


def _extract_pdf_text(pdf_path: Path) -> str:
    text_path = TEXT_DIR / f"{pdf_path.stem}.txt"
    if text_path.exists():
        return text_path.read_text(encoding="utf-8", errors="ignore")
    try:
        reader = PdfReader(str(pdf_path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        text = "\n".join(pages)
    except Exception as exc:  # noqa: BLE001
        text = f"[PDF text extraction failed: {exc}]"
    text_path.write_text(text, encoding="utf-8", errors="ignore")
    return text


def _chunk_text(text: str, size: int = 1800, overlap: int = 180) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks


def _should_follow(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc and parsed.netloc != "kcb.vn":
        return False
    path = parsed.path.lower()
    text = urllib.parse.unquote(url.lower())
    return any(token in text for token in ["phac-do", "thu-vien-tai-lieu", "huong-dan", "chan-doan", "dieu-tri", "tin-tuc"])


def harvest_guideline_documents() -> list[dict[str, Any]]:
    visited: set[str] = set()
    queued: list[str] = list(dict.fromkeys(KCB_SEED_URLS + NUTRITION_DOCUMENT_URLS))
    records: list[dict[str, Any]] = []
    pdf_urls: set[str] = set()
    html_pages: list[dict[str, str]] = []

    while queued and len(visited) < KCB_MAX_PAGES:
        url = queued.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            content = _request_bytes(url)
        except Exception as exc:  # noqa: BLE001
            print(f"[guidelines] skip {url}: {exc}")
            continue
        lower_url = url.lower()
        if lower_url.endswith(".pdf") or content[:4] == b"%PDF":
            pdf_path = PDF_DIR / _safe_name(url, ".pdf")
            if not pdf_path.exists():
                pdf_path.write_bytes(content)
            pdf_urls.add(url)
            continue

        raw_html = content.decode("utf-8", errors="ignore")
        parser = LinkParser()
        parser.feed(raw_html)
        title = _clean_text(" ".join(parser.title_parts), limit=240) or url
        text = _html_to_text(raw_html)
        html_pages.append({"url": url, "title": title, "text": text})
        for link in parser.links:
            absolute = urllib.parse.urljoin(url, link)
            clean = absolute.split("#", 1)[0]
            if clean.lower().endswith(".pdf") or "/upload/" in clean.lower():
                pdf_urls.add(clean)
            elif DISCOVER_GUIDELINE_LINKS and _should_follow(clean) and clean not in visited and clean not in queued:
                queued.append(clean)
        time.sleep(REQUEST_SLEEP)

    for url in sorted(pdf_urls):
        try:
            content = _request_bytes(url)
            pdf_path = PDF_DIR / _safe_name(url, ".pdf")
            if not pdf_path.exists():
                pdf_path.write_bytes(content)
            text = _extract_pdf_text(pdf_path)
            chunks = _chunk_text(text)
            title = Path(urllib.parse.urlparse(url).path).name or url
            for idx, chunk in enumerate(chunks, start=1):
                records.append(
                    {
                        "id": f"guideline_pdf:{_sha(url)}:{idx:04d}",
                        "type": "guideline_chunk",
                        "title": f"{urllib.parse.unquote(title)} chunk {idx}",
                        "aliases": [urllib.parse.unquote(title), "hướng dẫn chẩn đoán điều trị"],
                        "content": chunk,
                        "structured": {"document_url": url, "chunk_index": idx, "format": "pdf"},
                        "source": {"type": "public_guideline_pdf", "name": "KCB/BYT/NIN public document", "url": url},
                        "last_updated": "2026-05-17",
                        "confidence": "medium",
                        "needs_medical_review": True,
                    }
                )
        except Exception as exc:  # noqa: BLE001
            print(f"[guidelines] pdf skip {url}: {exc}")
        time.sleep(REQUEST_SLEEP)

    for page in html_pages:
        for idx, chunk in enumerate(_chunk_text(page["text"]), start=1):
            records.append(
                {
                    "id": f"guideline_html:{_sha(page['url'])}:{idx:04d}",
                    "type": "guideline_chunk",
                    "title": f"{page['title']} chunk {idx}",
                    "aliases": [page["title"], "hướng dẫn chẩn đoán điều trị"],
                    "content": chunk,
                    "structured": {"document_url": page["url"], "chunk_index": idx, "format": "html"},
                    "source": {"type": "public_guideline_page", "name": "KCB/BYT/NIN public page", "url": page["url"]},
                    "last_updated": "2026-05-17",
                    "confidence": "medium",
                    "needs_medical_review": True,
                }
            )

    _write_json(PUBLIC_DIR / "public_guideline_chunks.json", records)
    _write_json(
        PUBLIC_DIR / "public_guideline_manifest.json",
        {"visited_pages": sorted(visited), "pdf_urls": sorted(pdf_urls), "record_count": len(records)},
    )
    return records


def main() -> dict[str, Any]:
    _ensure_dirs()
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    print("[1/3] Harvesting openFDA drug interaction labels")
    openfda_records = harvest_openfda_interaction_labels()
    print("[2/3] Building public nutrition reference rows and source document records")
    nutrition_records = build_nutrition_reference_records()
    print("[3/3] Harvesting KCB/BYT/NIN guideline documents")
    guideline_records = harvest_guideline_documents()

    combined_count = len(openfda_records) + len(nutrition_records) + len(guideline_records)
    if WRITE_COMBINED_PUBLIC_KB:
        _write_json(PUBLIC_DIR / "public_medical_knowledge_base.json", openfda_records + nutrition_records + guideline_records)
    report = {
        "started_at": started,
        "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "counts": {
            "openfda_drug_interaction_labels": len(openfda_records),
            "nutrition_public_reference": len(nutrition_records),
            "public_guideline_chunks": len(guideline_records),
            "public_total": combined_count,
        },
        "outputs": {
            "openfda_drug_interaction_labels": str((PUBLIC_DIR / "openfda_drug_interaction_labels.json").relative_to(ROOT)),
            "nutrition_public_reference": str((PUBLIC_DIR / "nutrition_public_reference.json").relative_to(ROOT)),
            "public_guideline_chunks": str((PUBLIC_DIR / "public_guideline_chunks.json").relative_to(ROOT)),
            "public_medical_knowledge_base": str((PUBLIC_DIR / "public_medical_knowledge_base.json").relative_to(ROOT)) if WRITE_COMBINED_PUBLIC_KB else "",
        },
        "limitations": [
            "DrugBank Clinical is paid/licensed and was not fetched without credentials.",
            "openFDA/DailyMed label interaction text is public but not fully structured into severity/mechanism pairs.",
            "PDF extraction quality depends on the source PDF text layer.",
        ],
    }
    _write_json(PUBLIC_DIR / "harvest_report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    main()
