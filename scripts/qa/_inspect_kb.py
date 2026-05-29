"""Quick inspector for KB data shapes (temporary)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sample_first_records(rel: str, n: int = 2) -> None:
    """Stream first n dict records from a possibly-huge JSON array."""
    p = ROOT / rel
    if not p.exists():
        print(f"--- {rel}: MISSING ---")
        return
    size_mb = p.stat().st_size / 1024**2
    print(f"=== {rel} | {size_mb:.2f} MB ===")
    items = []
    with p.open("r", encoding="utf-8", errors="replace") as f:
        buf = ""
        depth = 0
        in_str = False
        esc = False
        start = -1
        seen = False
        while len(items) < n:
            chunk = f.read(65536)
            if not chunk:
                break
            buf += chunk
            i = 0
            while i < len(buf) and len(items) < n:
                c = buf[i]
                if not seen:
                    if c == "[":
                        seen = True
                    i += 1
                    continue
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = not in_str
                elif not in_str:
                    if c == "{":
                        if depth == 0:
                            start = i
                        depth += 1
                    elif c == "}":
                        depth -= 1
                        if depth == 0 and start >= 0:
                            try:
                                items.append(json.loads(buf[start : i + 1]))
                            except json.JSONDecodeError:
                                pass
                            start = -1
                i += 1
            if depth == 0 and start < 0:
                buf = buf[i:]
    for idx, item in enumerate(items):
        print(f"[{idx}] keys={list(item.keys())}")
        print(json.dumps(item, ensure_ascii=False, indent=2)[:1500])
    print()


sample_first_records("data/knowledge_base/drug_interactions.json", 2)

# build_report is small
br = ROOT / "data/knowledge_base/build_report.json"
if br.exists():
    print("=== build_report.json ===")
    print(json.dumps(json.loads(br.read_text(encoding="utf-8")), ensure_ascii=False, indent=2)[:2000])

# Check openpyxl availability
try:
    import openpyxl  # noqa: F401
    print("\nopenpyxl: AVAILABLE", openpyxl.__version__)
except ImportError:
    print("\nopenpyxl: NOT INSTALLED")
