"""Generate Step 3 MedGemma output-format samples from disease KB records.

The records train MediSign MedGemma v2 to produce diagnostic-chat style
outputs: multi-turn context, disease probabilities, Xanh/Vàng/Đỏ triage, and
the mandatory disclaimer.

Usage:
    python scripts/generate_output_format_samples.py --target 800
    python scripts/generate_output_format_samples.py --target 50 --dry-run
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
KB_PATH = ROOT / "data" / "knowledge_base" / "knowledge_base.json"
OUTPUT_DIR = ROOT / "data" / "training_clean" / "medgemma_4b"
TRAIN_FILE = OUTPUT_DIR / "output_format_train.jsonl"
EVAL_FILE = OUTPUT_DIR / "output_format_eval.jsonl"
STATS_FILE = OUTPUT_DIR / "output_format_stats.json"

DISCLAIMER = "⚠️ Tôi không thể thay thế bác sĩ."
SYSTEM = (
    "Bạn là MediSign AI, trợ lý y tế tiếng Việt. Bạn phân loại mức độ "
    "Xanh/Vàng/Đỏ dựa trên triệu chứng đã thu thập, không chẩn đoán chắc chắn, "
    "và luôn trình bày kết luận đúng format."
)
TRAIN_RATIO = 0.9
SEED = 42


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    return [item for item in data if isinstance(item, dict)]


def _severity_to_triage(severity: str) -> str:
    return {"low": "green", "medium": "yellow", "high": "red"}.get(severity, "yellow")


def _triage_vi(triage: str) -> str:
    return {"green": "XANH", "yellow": "VÀNG", "red": "ĐỎ"}[triage]


def _triage_emoji(triage: str) -> str:
    return {"green": "🟢", "yellow": "🟡", "red": "🔴"}[triage]


def _clean_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(item).strip() for item in values if str(item).strip()]


def disease_records(kb_path: Path = KB_PATH) -> list[dict[str, Any]]:
    rows = []
    for record in _read_json_list(kb_path):
        if record.get("type") != "vietnam_common_disease":
            continue
        structured = record.get("structured") or {}
        symptoms = _clean_list(
            structured.get("common_symptoms")
            or structured.get("symptoms")
            or record.get("symptoms")
        )
        if len(symptoms) < 2:
            continue
        severity = str(structured.get("severity") or record.get("severity") or "medium")
        rows.append(
            {
                "name": str(structured.get("name") or record.get("title") or "").strip(),
                "symptoms": symptoms,
                "severity": severity if severity in {"low", "medium", "high"} else "medium",
                "red_flags": _clean_list(structured.get("red_flags") or record.get("red_flags")),
                "home_care": _clean_list(structured.get("home_care") or record.get("home_care")),
                "lab_tests": _clean_list(structured.get("lab_tests") or record.get("lab_tests")),
                "source_id": record.get("id", ""),
            }
        )
    return [row for row in rows if row["name"]]


def _turns_for_disease(disease: dict[str, Any], rng: random.Random) -> list[dict[str, str]]:
    symptoms = list(disease["symptoms"])
    rng.shuffle(symptoms)
    first = ", ".join(symptoms[:2])
    third = symptoms[2] if len(symptoms) > 2 else symptoms[-1]
    duration = rng.choice(["2 ngày", "3 ngày", "gần 1 tuần", "từ hôm qua"])
    severity_phrase = rng.choice(["khá khó chịu", "tăng dần", "lúc có lúc không"])
    return [
        {"role": "user", "content": f"Tôi bị {first} {duration}, không biết có nguy hiểm không?"},
        {
            "role": "assistant",
            "content": f"Mình ghi nhận bạn đang có {first}. Bạn có thể chia sẻ thêm mức độ và triệu chứng nào đi kèm không?",
        },
        {"role": "user", "content": f"Tôi còn thấy {third}, mức độ {severity_phrase}."},
        {
            "role": "assistant",
            "content": "Cảm ơn bạn đã mô tả thêm. Các triệu chứng này xuất hiện liên tục hay từng cơn?",
        },
        {"role": "user", "content": rng.choice(["Gần như liên tục.", "Từng cơn nhưng hôm nay nhiều hơn.", "Nặng hơn về chiều."])},
    ]


def _assistant_output(
    disease: dict[str, Any],
    probability: int,
    triage_override: str | None = None,
) -> str:
    triage = triage_override or _severity_to_triage(disease["severity"])
    secondary_probability = max(15, probability - 35)
    lines = [
        "Kết luận:",
        f"• {disease['name']} ({probability}%) {_triage_emoji(triage)}",
        f"• Một nguyên nhân khác cần loại trừ ({secondary_probability}%) 🟡",
        "",
        f"Mức độ: {_triage_vi(triage)}",
    ]

    if triage == "red":
        lines.extend(
            [
                "⚠️ Bạn có khả năng mắc tình trạng cần được đánh giá y tế sớm, hãy đi khám bác sĩ ngay.",
            ]
        )
    elif triage == "yellow":
        lines.append("Khuyến nghị: Bạn nên theo dõi sát và đi khám nếu triệu chứng kéo dài hoặc nặng hơn.")
    else:
        lines.append("Khuyến nghị: Có thể chăm sóc tại nhà và theo dõi thêm nếu không có dấu hiệu nặng.")

    home_care = disease.get("home_care") or []
    if home_care:
        lines.append("Chăm sóc/khuyến nghị:")
        lines.extend(f"- {item}" for item in home_care[:3])

    lab_tests = disease.get("lab_tests") or []
    if triage != "green" and lab_tests:
        lines.append("Khám hoặc xét nghiệm nên cân nhắc:")
        lines.extend(f"- {item}" for item in lab_tests[:2])

    red_flags = disease.get("red_flags") or []
    if red_flags:
        lines.append("Dấu hiệu cần đi khám gấp:")
        lines.extend(f"- {item}" for item in red_flags[:4])

    lines.append(DISCLAIMER)
    return "\n".join(lines)


def _to_medgemma_text(messages: list[dict[str, str]], output: str) -> str:
    rendered: list[str] = []
    first_user = True
    for message in messages:
        role = message["role"]
        content = message["content"].strip()
        if role == "user":
            if first_user:
                content = f"{SYSTEM}\n\n{content}"
                first_user = False
            rendered.append(f"<start_of_turn>user\n{content}<end_of_turn>")
        else:
            rendered.append(f"<start_of_turn>model\n{content}<end_of_turn>")
    rendered.append(f"<start_of_turn>model\n{output}<end_of_turn>")
    return "\n".join(rendered)


def generate_records(target: int = 800, kb_path: Path = KB_PATH) -> list[dict[str, Any]]:
    diseases = disease_records(kb_path)
    if not diseases:
        raise RuntimeError("No disease records available for output-format generation.")

    rng = random.Random(SEED)
    records: list[dict[str, Any]] = []
    for index in range(target):
        disease = diseases[index % len(diseases)]
        base_triage = _severity_to_triage(disease["severity"])
        # Step 3 needs all three output formats. Crawled public disease pages
        # skew medium/high, so medium records are used to produce both mild
        # green presentations and follow-up yellow presentations.
        if base_triage == "yellow" and index % 2 == 0:
            triage = "green"
            probability = rng.randint(62, 78)
        else:
            triage = base_triage
            probability = rng.randint(72, 88)
        messages = _turns_for_disease(disease, rng)
        output = _assistant_output(disease, probability, triage_override=triage)
        records.append(
            {
                "text": _to_medgemma_text(messages, output),
                "messages": [*messages, {"role": "assistant", "content": output}],
                "output": output,
                "disease": disease["name"],
                "triage_level": triage,
                "source": "generated_output_format",
                "source_id": disease["source_id"],
            }
        )
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return len(records)


def write_split(records: list[dict[str, Any]], dry_run: bool = False) -> dict[str, Any]:
    shuffled = list(records)
    random.Random(SEED).shuffle(shuffled)
    split_at = int(len(shuffled) * TRAIN_RATIO)
    train = shuffled[:split_at]
    eval_ = shuffled[split_at:]

    stats = {
        "total": len(records),
        "train": len(train),
        "eval": len(eval_),
        "triage_distribution": {},
        "source": "generated_output_format",
    }
    for record in records:
        triage = record["triage_level"]
        stats["triage_distribution"][triage] = stats["triage_distribution"].get(triage, 0) + 1

    if not dry_run:
        write_jsonl(TRAIN_FILE, train)
        write_jsonl(EVAL_FILE, eval_)
        STATS_FILE.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    return stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=int, default=800)
    parser.add_argument("--kb-path", type=Path, default=KB_PATH)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = generate_records(target=args.target, kb_path=args.kb_path)
    stats = write_split(records, dry_run=args.dry_run)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    if args.dry_run:
        print("Dry run only; output_format_train/eval files were not written.")


if __name__ == "__main__":
    main()
