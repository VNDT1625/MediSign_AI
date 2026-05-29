"""Async crawler for Vinmec disease/health articles.

Start URL:
    https://www.vinmec.com/vi/tin-tuc/thong-tin-suc-khoe/

Output:
    diseases_vinmec.json

The crawler saves a progress file so it can resume after interruption.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import random
import re
import unicodedata
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup, Tag


ROOT = Path(__file__).resolve().parents[1]
SOURCE = "vinmec"
START_URL = "https://www.vinmec.com/vi/tin-tuc/thong-tin-suc-khoe/"
FALLBACK_SEEDS = [
    "https://www.vinmec.com/vie/chuyen-trang-suc-khoe/",
]
OUTPUT_FILE = ROOT / "diseases_vinmec.json"
PROGRESS_FILE = ROOT / ".crawl_vinmec_progress.json"
RETRY_ATTEMPTS = 3
MIN_DELAY_SECONDS = 1.0
MAX_DELAY_SECONDS = 2.0
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi,en;q=0.8",
}


def clean_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value or "")
    return value.strip(" \t\r\n:-–—")


def fold_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return value.lower()


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    parsed = parsed._replace(fragment="", query="")
    path = re.sub(r"/+", "/", parsed.path)
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return urlunparse(parsed._replace(path=path))


def same_domain(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return host.endswith("vinmec.com")


def looks_like_article(url: str) -> bool:
    path = urlparse(url).path.lower()
    listing_paths = {
        "/vi/tin-tuc/thong-tin-suc-khoe",
        "/vie/tin-tuc/thong-tin-suc-khoe",
        "/vie/chuyen-trang-suc-khoe",
    }
    if path.rstrip("/") in listing_paths:
        return False
    if any(skip in path for skip in ("/chuyen-gia-y-te", "/dang-ky-kham", "/cham-soc-khach-hang")):
        return False
    if path.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".pdf", ".zip")):
        return False
    parts = [part for part in path.split("/") if part]
    return len(parts) >= 3 and not path.endswith(("/tin-tuc", "/chuyen-trang-suc-khoe"))


async def fetch_html(client: httpx.AsyncClient, url: str) -> str | None:
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        await asyncio.sleep(random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS))
        try:
            response = await client.get(url)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "html" not in content_type.lower():
                return None
            return response.text
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            if attempt == RETRY_ATTEMPTS:
                print(f"[WARN] fetch failed after {attempt} attempts: {url} ({exc})")
                return None
            await asyncio.sleep(2 * attempt)
    return None


def load_progress(refresh: bool) -> dict:
    if refresh or not PROGRESS_FILE.exists():
        return {
            "pending_urls": [START_URL],
            "seen_urls": [START_URL],
            "done_urls": [],
            "failed_urls": [],
            "records": [],
        }
    data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    data.setdefault("pending_urls", [])
    data.setdefault("seen_urls", [])
    data.setdefault("done_urls", [])
    data.setdefault("failed_urls", [])
    data.setdefault("records", [])
    return data


def sanitize_str(value: str) -> str:
    """Remove null bytes and lone surrogates that cause Windows write failures."""
    return value.replace("\x00", "").encode("utf-8", errors="replace").decode("utf-8")


def sanitize_value(value: object) -> object:
    """Recursively sanitize strings in dicts/lists."""
    if isinstance(value, str):
        return sanitize_str(value)
    if isinstance(value, dict):
        return {k: sanitize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_value(item) for item in value]
    return value


def save_json(path: Path, value: object) -> None:
    """Atomic write: serialize to a .tmp file then rename to avoid partial writes and Windows file locks."""
    clean = sanitize_value(value)
    text = json.dumps(clean, ensure_ascii=False, indent=2)
    tmp_path = path.with_suffix(".tmp")
    try:
        tmp_path.write_text(text, encoding="utf-8")
        tmp_path.replace(path)
    except OSError as exc:
        print(f"[WARN] save_json failed for {path}: {exc}")
        try:
            path.write_text(text, encoding="utf-8")
        except OSError as exc2:
            print(f"[ERROR] save_json fallback also failed: {exc2}")


def save_progress(progress: dict) -> None:
    # Reconstruct seen_urls from done + pending + failed to avoid unbounded growth
    compact = {
        "pending_urls": progress["pending_urls"],
        "seen_urls": list(set(progress["done_urls"]) | set(progress["pending_urls"]) | set(progress.get("failed_urls", []))),
        "done_urls": progress["done_urls"],
        "failed_urls": progress.get("failed_urls", []),
        "records": progress["records"],
    }
    save_json(PROGRESS_FILE, compact)
    save_json(OUTPUT_FILE, progress["records"])


def collect_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    for anchor in soup.select("a[href]"):
        href = anchor.get("href")
        if not href:
            continue
        url = normalize_url(urljoin(base_url, href))
        if same_domain(url):
            links.append(url)
    return sorted(set(links))


def extract_name(soup: BeautifulSoup) -> str:
    for selector in ("h1", "meta[property='og:title']", "title"):
        node = soup.select_one(selector)
        if not node:
            continue
        text = node.get("content", "") if node.name == "meta" else node.get_text(" ", strip=True)
        text = re.sub(r"\s*\|\s*Vinmec.*$", "", text, flags=re.I)
        text = re.sub(r"\s*-\s*Vinmec.*$", "", text, flags=re.I)
        text = clean_text(text)
        if len(text) >= 6:
            return text
    return ""


def main_content(soup: BeautifulSoup) -> Tag:
    for selector in ("article", "main", ".detail-content", ".entry-content", ".post-content"):
        node = soup.select_one(selector)
        if isinstance(node, Tag):
            return node
    return soup.body if isinstance(soup.body, Tag) else soup


def heading_matches(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = fold_text(text)
    return any(fold_text(keyword) in lowered for keyword in keywords)


def section_after_heading(content: Tag, keywords: tuple[str, ...], max_nodes: int = 12) -> list[str]:
    values: list[str] = []
    headings = content.find_all(re.compile(r"^h[2-6]$"))
    for heading in headings:
        if not heading_matches(heading.get_text(" ", strip=True), keywords):
            continue
        for node in heading.find_all_next(["h1", "h2", "h3", "h4", "h5", "h6", "li", "p"]):
            if node is heading:
                continue
            if re.fullmatch(r"h[1-6]", node.name or ""):
                break
            text = clean_text(node.get_text(" ", strip=True))
            if len(text) >= 8:
                values.append(text)
            if len(values) >= max_nodes:
                break
        if values:
            break
    return values


def split_symptoms(texts: list[str]) -> list[str]:
    symptoms: list[str] = []
    for text in texts:
        chunks = re.split(r";|•|\n|(?<=[.!?])\s+", text)
        for chunk in chunks:
            chunk = clean_text(re.sub(r"^(bao gồm|gồm|như|các triệu chứng|triệu chứng)\s*:?", "", chunk, flags=re.I))
            if 4 <= len(chunk) <= 160 and chunk.lower() not in {"triệu chứng", "dấu hiệu"}:
                symptoms.append(chunk)
    seen: set[str] = set()
    result: list[str] = []
    for item in symptoms:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result[:12]


def infer_severity(text: str) -> str:
    lowered = fold_text(text)
    severe_terms = ("cấp cứu", "tử vong", "đe dọa tính mạng", "nguy hiểm", "biến chứng nặng", "suy hô hấp", "ung thư")
    moderate_terms = ("biến chứng", "điều trị", "mạn tính", "phẫu thuật", "nhập viện", "nhiễm trùng")
    if any(fold_text(term) in lowered for term in severe_terms):
        return "nặng"
    if any(fold_text(term) in lowered for term in moderate_terms):
        return "trung bình"
    return "nhẹ"


def parse_record(html: str, url: str) -> dict | None:
    soup = BeautifulSoup(html, "html.parser")
    name = extract_name(soup)
    if not name:
        return None

    content = main_content(soup)
    full_text = clean_text(content.get_text(" ", strip=True))
    if len(full_text) < 200:
        return None

    symptom_texts = section_after_heading(content, ("triệu chứng", "dấu hiệu", "biểu hiện"))
    cause_texts = section_after_heading(content, ("nguyên nhân", "lý do", "vì sao"))
    symptoms = split_symptoms(symptom_texts)
    causes = clean_text(" ".join(cause_texts))[:1200]

    if not symptoms:
        return None

    return {
        "name": name,
        "symptoms": symptoms,
        "causes": causes,
        "severity": infer_severity(full_text),
        "source": SOURCE,
        "url": url,
    }


async def crawl(max_pages: int, max_articles: int | None, refresh: bool) -> list[dict]:
    progress = load_progress(refresh=refresh)
    if len(progress["pending_urls"]) == 1 and progress["pending_urls"][0] == START_URL:
        for seed in FALLBACK_SEEDS:
            if seed not in progress["seen_urls"]:
                progress["seen_urls"].append(seed)
                progress["pending_urls"].append(seed)

    processed_pages = 0
    timeout = httpx.Timeout(30.0, connect=15.0)
    async with httpx.AsyncClient(headers=HEADERS, timeout=timeout, follow_redirects=True) as client:
        while progress["pending_urls"]:
            if processed_pages >= max_pages:
                break
            if max_articles is not None and len(progress["records"]) >= max_articles:
                break

            url = progress["pending_urls"].pop(0)
            if url in progress["done_urls"]:
                continue
            html = await fetch_html(client, url)
            processed_pages += 1
            if html is None:
                progress["failed_urls"].append(url)
                save_progress(progress)
                continue

            for link in collect_links(html, url):
                if link not in progress["seen_urls"] and looks_like_article(link):
                    progress["seen_urls"].append(link)
                    progress["pending_urls"].append(link)

            if looks_like_article(url):
                record = parse_record(html, url)
                if record and not any(item["url"] == record["url"] for item in progress["records"]):
                    progress["records"].append(record)

            progress["done_urls"].append(url)
            save_progress(progress)
            print(
                f"[{SOURCE}] crawled records={len(progress['records'])} "
                f"done={len(progress['done_urls'])} pending={len(progress['pending_urls'])}"
            )

    save_progress(progress)
    return progress["records"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crawl Vinmec disease data.")
    parser.add_argument("--max-pages", type=int, default=300, help="Maximum fetched pages this run.")
    parser.add_argument("--max-articles", type=int, default=None, help="Stop after N records.")
    parser.add_argument("--refresh", action="store_true", help="Ignore saved progress and crawl from scratch.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = asyncio.run(
        crawl(max_pages=args.max_pages, max_articles=args.max_articles, refresh=args.refresh)
    )
    print(f"Saved {len(records)} records to {OUTPUT_FILE}")
    print(f"Progress file: {PROGRESS_FILE}")


if __name__ == "__main__":
    main()
