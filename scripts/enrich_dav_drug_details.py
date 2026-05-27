"""Enrich DAV lookup rows with detailed registration data from congbothuoc API.

Input:
    data/training_clean/dav_lookup_drugs.json

Outputs:
    data/training_raw/dav_congbothuoc_api/raw_details.jsonl
    data/training_clean/dav_detailed_drugs.json
    data/training_clean/drug_database_dav_detailed.json
    data/training_clean/dav_detail_enrich_report.json
"""
from __future__ import annotations

import json
import os
import re
import time
import unicodedata
import urllib.request
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
CLEAN_DIR = ROOT / "data" / "training_clean"
RAW_DIR = ROOT / "data" / "training_raw" / "dav_congbothuoc_api"
LOOKUP_FILE = CLEAN_DIR / "dav_lookup_drugs.json"
EXPANDED_DB_FILE = CLEAN_DIR / "drug_database_10k_full.json"
DETAILS_JSONL = RAW_DIR / "raw_details.jsonl"
DETAILS_FILE = CLEAN_DIR / "dav_detailed_drugs.json"
DETAILED_DB_FILE = CLEAN_DIR / "drug_database_dav_detailed.json"
REPORT_FILE = CLEAN_DIR / "dav_detail_enrich_report.json"

API_URL = "https://dichvucong.dav.gov.vn/api/services/app/soDangKy/GetAllPublicServerPaging"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (MediSign data enrichment)",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def _clean(value: object) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def _read_json_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    return data


def _split_registration_numbers(value: str) -> list[str]:
    parts = re.split(r"[,;/\n]+", value or "")
    return [_clean(part) for part in parts if _clean(part)]


def build_query_seeds(limit: int | None = None) -> list[str]:
    lookup_rows = _read_json_list(LOOKUP_FILE)
    seeds: list[str] = []
    seen: set[str] = set()

    # Prefer registration numbers because the API maps legacy numbers to the
    # current registration object and returns precise details.
    for row in lookup_rows:
        for reg in _split_registration_numbers(row.get("registration_number", "")):
            key = _normalize(reg)
            if key and key not in seen:
                seen.add(key)
                seeds.append(reg)
                if limit and len(seeds) >= limit:
                    return seeds

    # Fallback to names for rows without registration numbers.
    for row in lookup_rows:
        name = _clean(row.get("name"))
        key = _normalize(name)
        if key and key not in seen:
            seen.add(key)
            seeds.append(name)
            if limit and len(seeds) >= limit:
                return seeds
    return seeds


def load_existing_raw() -> dict[str, dict]:
    existing: dict[str, dict] = {}
    if not DETAILS_JSONL.exists():
        return existing
    with DETAILS_JSONL.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            existing[rec["query"]] = rec
    return existing


def call_api(query: str, max_result_count: int = 20) -> dict:
    payload = {
        "filterText": query,
        "SoDangKyThuoc": {},
        "KichHoat": True,
        "skipCount": 0,
        "maxResultCount": max_result_count,
        "sorting": None,
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=HEADERS,
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        body = response.read().decode("utf-8", errors="replace")
    data = json.loads(body)
    result = data.get("result") or {}
    return {
        "query": query,
        "success": bool(data.get("success")),
        "total_count": int(result.get("totalCount") or 0),
        "items": result.get("items") or [],
    }


def enrich_raw(limit: int | None = None, delay_seconds: float = 0.03, refresh: bool = False) -> dict[str, dict]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    seeds = build_query_seeds(limit=limit)
    existing = {} if refresh else load_existing_raw()
    mode = "w" if refresh else "a"
    done = dict(existing)

    with DETAILS_JSONL.open(mode, encoding="utf-8") as fh:
        for idx, query in enumerate(seeds, start=1):
            if query in done:
                continue
            try:
                rec = call_api(query)
            except Exception as exc:
                rec = {"query": query, "success": False, "total_count": 0, "items": [], "error": str(exc)}
            fh.write(json.dumps(rec, ensure_ascii=False))
            fh.write("\n")
            fh.flush()
            done[query] = rec
            if idx % 250 == 0:
                print(f"{idx}/{len(seeds)} queries, details with hits: {sum(1 for r in done.values() if r.get('items'))}")
            if delay_seconds:
                time.sleep(delay_seconds)
    return done


def _get_nested(item: dict, *path: str) -> object:
    cur: object = item
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def flatten_item(item: dict, query: str) -> dict:
    basic = item.get("thongTinThuocCoBan") or {}
    reg_info = item.get("thongTinDangKyThuoc") or {}
    documents = item.get("thongTinTaiLieu") or {}
    manufacturer = item.get("congTySanXuat") or {}
    registrant = item.get("congTyDangKy") or {}
    vaccine = item.get("vacXinSinhPham") or {}

    return {
        "name": _clean(item.get("tenThuoc")),
        "registration_number": _clean(item.get("soDangKy")),
        "old_registration_number": _clean(item.get("soDangKyCu")),
        "active_ingredient": _clean(basic.get("hoatChatChinh") or item.get("hoatChatChinh")),
        "strength": _clean(basic.get("hamLuong") or item.get("hamLuong")),
        "dosage_form": _clean(basic.get("dangBaoChe") or item.get("dangBaoChe")),
        "package": _clean(basic.get("dongGoi") or item.get("dongGoi")),
        "standard": _clean(basic.get("tieuChuan") or item.get("tieuChuan")),
        "shelf_life": _clean(basic.get("tuoiTho") or item.get("tuoiTho")),
        "drug_type_id": basic.get("loaiThuocId"),
        "drug_group_id": basic.get("nhomThuocId"),
        "manufacturer": _clean(manufacturer.get("tenCongTySanXuat") or item.get("tenCongTySanXuat")),
        "manufacturer_address": _clean(manufacturer.get("diaChiSanXuat") or item.get("diaChiSanXuat")),
        "manufacturer_country": _clean(manufacturer.get("nuocSanXuat") or item.get("nuocSanXuat")),
        "registrant_company": _clean(registrant.get("tenCongTyDangKy") or item.get("tenCongTyDangKy")),
        "registrant_address": _clean(registrant.get("diaChiDangKy") or item.get("diaChiDangKy")),
        "registrant_country": _clean(registrant.get("nuocDangKy") or item.get("nuocDangKy")),
        "decision_number": _clean(reg_info.get("soQuyetDinh") or item.get("soQuyetDinh")),
        "registration_batch": _clean(reg_info.get("dotCap") or item.get("dotCap")),
        "registration_date": _clean(reg_info.get("ngayCapSoDangKy")),
        "expiration_date": _clean(reg_info.get("ngayHetHanSoDangKy")),
        "is_expired": bool(item.get("isHetHan")),
        "is_withdrawn": bool(item.get("isDaRutSoDangKy")),
        "is_active": bool(item.get("isActive")),
        "disease_prevention": _clean(vaccine.get("phongBenh")),
        "label_url": _clean(documents.get("urlNhan")),
        "instruction_url": _clean(documents.get("urlHuongDanSuDung")),
        "label_instruction_url": _clean(documents.get("urlNhanVaHDSD")),
        "source": "dichvucong.dav.gov.vn",
        "source_query": query,
        "source_id": item.get("id"),
    }


def flatten_details(raw_records: Iterable[dict]) -> list[dict]:
    flattened: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for raw in raw_records:
        query = raw.get("query", "")
        for item in raw.get("items") or []:
            rec = flatten_item(item, query=query)
            key = (
                _normalize(rec.get("registration_number", "")),
                _normalize(rec.get("old_registration_number", "")),
                _normalize(rec.get("name", "")),
            )
            if key in seen:
                continue
            seen.add(key)
            flattened.append(rec)
    return flattened


def build_detailed_drug_database(details: list[dict]) -> list[dict]:
    base = _read_json_list(EXPANDED_DB_FILE)
    db = list(base)
    index = {
        (
            _normalize(item.get("registration_number", "")),
            _normalize(item.get("name", "")),
        ): idx
        for idx, item in enumerate(db)
    }
    for rec in details:
        key = (_normalize(rec.get("registration_number", "")), _normalize(rec.get("name", "")))
        description_parts = [
            f"Hoạt chất: {rec.get('active_ingredient')}" if rec.get("active_ingredient") else "",
            f"Hàm lượng: {rec.get('strength')}" if rec.get("strength") else "",
            f"Dạng bào chế: {rec.get('dosage_form')}" if rec.get("dosage_form") else "",
            f"Quy cách đóng gói: {rec.get('package')}" if rec.get("package") else "",
            f"Số đăng ký: {rec.get('registration_number')}" if rec.get("registration_number") else "",
        ]
        enriched = {
            "name": rec.get("name", ""),
            "description": ". ".join(part for part in description_parts if part),
            "source": "dichvucong.dav.gov.vn",
            **rec,
        }
        if key in index:
            # Prefer official detailed API fields over the lightweight DAV
            # lookup row with only name/registration/advertising metadata.
            existing = db[index[key]]
            merged = {**existing, **{k: v for k, v in enriched.items() if v not in ("", None)}}
            db[index[key]] = merged
        else:
            db.append(enriched)
            index[key] = len(db) - 1
    return db


def main() -> None:
    limit_env = os.getenv("DAV_DETAIL_LIMIT")
    limit = int(limit_env) if limit_env else None
    refresh = os.getenv("DAV_DETAIL_REFRESH", "").lower() in {"1", "true", "yes"}
    delay = float(os.getenv("DAV_DETAIL_DELAY", "0.03"))
    finalize_only = os.getenv("DAV_DETAIL_FINALIZE_ONLY", "").lower() in {"1", "true", "yes"}

    raw_by_query = load_existing_raw() if finalize_only else enrich_raw(limit=limit, delay_seconds=delay, refresh=refresh)
    raw_records = list(raw_by_query.values())
    details = flatten_details(raw_records)
    detailed_db = build_detailed_drug_database(details)

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    DETAILS_FILE.write_text(json.dumps(details, ensure_ascii=False, indent=2), encoding="utf-8")
    DETAILED_DB_FILE.write_text(json.dumps(detailed_db, ensure_ascii=False, indent=2), encoding="utf-8")

    report = {
        "input_lookup_file": str(LOOKUP_FILE.relative_to(ROOT)),
        "raw_response_file": str(DETAILS_JSONL.relative_to(ROOT)),
        "queries_total": len(build_query_seeds(limit=limit)),
        "queries_completed": len(raw_records),
        "queries_with_hits": sum(1 for rec in raw_records if rec.get("items")),
        "raw_items": sum(len(rec.get("items") or []) for rec in raw_records),
        "detailed_records": len(details),
        "records_with_active_ingredient": sum(1 for rec in details if rec.get("active_ingredient")),
        "records_with_dosage_form": sum(1 for rec in details if rec.get("dosage_form")),
        "drug_database_dav_detailed_records": len(detailed_db),
        "outputs": {
            "details": str(DETAILS_FILE.relative_to(ROOT)),
            "drug_database": str(DETAILED_DB_FILE.relative_to(ROOT)),
            "report": str(REPORT_FILE.relative_to(ROOT)),
        },
    }
    REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
