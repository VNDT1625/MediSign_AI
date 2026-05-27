"""Generate Step 3 MedGemma output-format samples V2 — improved quality.

Improvements over V1:
- User input is natural Vietnamese (not copy-pasted from KB)
- Assistant turns follow OARS (affirm, reflect, open question)
- Triage distribution balanced: ~33% green, ~33% yellow, ~33% red
- Multi-turn conversations feel like real diagnostic chat
- Varied user speaking styles (formal, casual, worried, brief)

Usage:
    python scripts/generate_output_format_samples_v2.py --target 1200
    python scripts/generate_output_format_samples_v2.py --target 50 --dry-run
"""
from __future__ import annotations

import argparse
import json
import random
import re
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
TRAIN_RATIO = 0.85
SEED = 42


# ─── Natural user input templates ────────────────────────────────────────────

# Varied speaking styles for first message
USER_OPENERS = [
    # Worried style
    "Mấy hôm nay tôi bị {s1} với {s2}, lo quá không biết có sao không?",
    "Em bị {s1} rồi {s2} nữa, có cần đi khám không ạ?",
    "Tôi {s1} được {duration} rồi, giờ thêm {s2}, hơi lo.",
    # Casual style
    "Bị {s1} mấy ngày rồi, kèm {s2}, có nghiêm trọng không?",
    "Dạo này hay bị {s1}, hôm nay thêm {s2} nữa.",
    "{s1} từ {duration} trước, giờ {s2} thêm.",
    # Brief style
    "Tôi bị {s1} và {s2}.",
    "{s1}, {s2}, {duration} rồi.",
    # Descriptive style
    "Tôi muốn hỏi, tôi đang bị {s1} khoảng {duration}, kèm theo {s2}, không biết là bệnh gì?",
    "Chào bác sĩ, tôi bị {s1} và {s2} được {duration}, có cần lo lắng không?",
]

# Second user message — adds more symptoms or context
USER_FOLLOWUPS = [
    "Có thêm {s3} nữa, nhất là lúc {time}.",
    "Ngoài ra còn {s3}, mức độ {severity_desc}.",
    "Tôi còn thấy {s3}, đặc biệt {time}.",
    "Thêm {s3} nữa ạ, {severity_desc}.",
    "Vâng, còn {s3}, {time} thì nặng hơn.",
    "{s3} cũng có, {severity_desc}.",
]

# Third user message — answers assistant's question
USER_ANSWERS = [
    "Gần như liên tục, không giảm.",
    "Từng cơn, nhưng hôm nay nhiều hơn mọi khi.",
    "Nặng hơn về chiều tối.",
    "Lúc có lúc không, nhưng xu hướng tăng.",
    "Ban đầu nhẹ, giờ nặng hơn rõ.",
    "Liên tục luôn ạ, không có lúc nào đỡ.",
    "Sáng thì đỡ, chiều tối lại nặng.",
    "Mấy hôm đầu nhẹ, 2 ngày nay nặng hẳn.",
]

# ─── OARS assistant templates ────────────────────────────────────────────────

# First assistant response — Affirm + Reflect + Open question
ASSISTANT_TURN1 = [
    "Cảm ơn bạn đã chia sẻ. Có vẻ như {s1} và {s2} đang khiến bạn khá lo lắng. Bạn có thể cho mình biết thêm có triệu chứng nào khác đi kèm không?",
    "Mình ghi nhận bạn đang gặp {s1} kèm {s2}. Để hiểu rõ hơn, bạn có thể chia sẻ thêm mức độ nặng nhẹ và có triệu chứng nào khác không?",
    "Bạn đã mô tả rất rõ. Nghe có vẻ {s1} và {s2} đang ảnh hưởng đến sinh hoạt. Ngoài ra bạn có nhận thấy triệu chứng nào khác không?",
    "Mình hiểu, {s1} với {s2} chắc hẳn khó chịu lắm. Bạn có thể kể thêm về mức độ và thời điểm nào nặng nhất không?",
]

# Second assistant response — Reflect + Summarize + Open question
ASSISTANT_TURN2 = [
    "Mình ghi nhận thêm. Tóm lại bạn đang có {s1}, {s2} và {s3}. Các triệu chứng này xuất hiện liên tục hay từng cơn?",
    "Cảm ơn bạn. Vậy là ngoài {s1} và {s2}, bạn còn có {s3}. Triệu chứng có xu hướng tăng hay giảm theo thời gian trong ngày?",
    "Rõ rồi. Bạn đang có tổng cộng {s1}, {s2}, thêm {s3}. Mức độ có thay đổi theo ngày hay khá ổn định?",
    "Mình hiểu. Bạn đang trải qua {s1}, {s2} và giờ thêm {s3}. Triệu chứng nặng nhất vào lúc nào trong ngày?",
]

# ─── Time and severity phrases ───────────────────────────────────────────────

DURATIONS = ["2 ngày", "3 ngày", "gần 1 tuần", "từ hôm qua", "4-5 ngày", "khoảng 1 tuần"]
TIMES = ["buổi tối", "sáng sớm", "sau khi ăn", "khi nằm", "lúc vận động", "chiều tối"]
SEVERITY_DESCS = ["khá nặng", "nhẹ thôi", "tăng dần", "lúc có lúc không", "khó chịu lắm", "vừa phải"]


# ─── Symptom naturalizer ─────────────────────────────────────────────────────

def _naturalize_symptom(symptom: str) -> str:
    """Convert KB symptom text to natural Vietnamese phrasing.
    
    KB symptoms often contain full sentences, explanations, or medical jargon.
    This function extracts the core symptom phrase.
    """
    s = symptom.strip()
    
    # Remove leading explanatory text before colon
    if ":" in s:
        parts = s.split(":", 1)
        # Keep the part after colon if it's shorter (likely the actual symptom)
        if len(parts[1].strip()) > 5:
            s = parts[1].strip()
    
    # Remove parenthetical explanations
    s = re.sub(r"\s*\(.*?\)\s*", " ", s).strip()
    
    # Remove common KB noise phrases
    noise_patterns = [
        r"^(các |những |một số |triệu chứng |dấu hiệu |biểu hiện )",
        r"(thường |sẽ |có thể |bao gồm |là |gồm có )",
        r"(của bệnh \w+ )",
        r"(trong vòng \d+-\d+ ngày )",
        r"(ở giai đoạn \w+ )",
    ]
    for pattern in noise_patterns:
        s = re.sub(pattern, "", s, flags=re.IGNORECASE).strip()
    
    # If still too long, take first meaningful clause
    if len(s) > 50:
        # Split by comma or period, take first part
        for sep in [",", ".", ";", " và ", " hoặc "]:
            if sep in s:
                first_part = s.split(sep)[0].strip()
                if len(first_part) >= 8:
                    s = first_part
                    break
    
    # Final truncation
    if len(s) > 50:
        s = s[:47].rsplit(" ", 1)[0] + "..."
    
    # If result is too short or empty, return a generic version
    if len(s) < 4:
        return symptom[:40].strip()
    
    # Lowercase first char if not a proper noun
    if s and s[0].isupper() and not any(s.startswith(p) for p in ("X-", "CT", "MRI", "HIV")):
        s = s[0].lower() + s[1:]
    
    return s


# Fallback symptom pool for when KB symptoms are too noisy
COMMON_SYMPTOMS_POOL = [
    "đau đầu", "sốt", "ho", "mệt mỏi", "buồn nôn", "đau bụng",
    "tiêu chảy", "chóng mặt", "khó thở", "đau ngực", "sổ mũi",
    "đau họng", "phát ban", "ngứa", "sưng", "đau lưng", "đau khớp",
    "mất ngủ", "chán ăn", "sụt cân", "đau cơ", "ớn lạnh",
    "vàng da", "tê bì tay chân", "tim đập nhanh", "đổ mồ hôi đêm",
    "táo bón", "ợ chua", "đầy bụng", "khô miệng",
]


def _get_usable_symptoms(disease: dict[str, Any], rng: random.Random) -> tuple[str, str, str]:
    """Get 3 usable symptom phrases for user input.
    
    Strategy: Map disease to a symptom group based on severity and disease name keywords.
    This ensures symptoms are at least plausibly related to the disease category.
    """
    # Disease-category symptom mapping
    SYMPTOM_GROUPS = {
        "respiratory": [
            "ho", "ho có đờm", "khó thở", "đau họng", "sổ mũi", "nghẹt mũi",
            "hắt hơi", "khàn tiếng", "đau ngực khi hít sâu", "thở khò khè",
        ],
        "gastrointestinal": [
            "đau bụng", "buồn nôn", "nôn", "tiêu chảy", "táo bón",
            "đầy bụng", "ợ chua", "chán ăn", "đau thượng vị", "sụt cân",
        ],
        "neurological": [
            "đau đầu", "chóng mặt", "tê bì tay chân", "mờ mắt",
            "mất ngủ", "hay quên", "run tay", "yếu tay chân", "co giật",
        ],
        "musculoskeletal": [
            "đau lưng", "đau khớp", "đau cơ", "cứng khớp buổi sáng",
            "sưng khớp", "nhức mỏi", "hạn chế vận động", "đau vai gáy",
        ],
        "dermatological": [
            "phát ban", "ngứa", "nổi mẩn đỏ", "da khô bong tróc",
            "sưng đỏ", "mụn nước", "vết loét da", "rụng tóc",
        ],
        "cardiovascular": [
            "đau ngực", "tim đập nhanh", "khó thở khi gắng sức",
            "phù chân", "hoa mắt", "tức ngực", "mệt khi leo cầu thang",
        ],
        "infectious": [
            "sốt", "ớn lạnh", "đổ mồ hôi đêm", "mệt mỏi", "đau nhức người",
            "sưng hạch", "đau đầu", "chán ăn", "sụt cân",
        ],
        "general": [
            "mệt mỏi", "sốt nhẹ", "đau đầu", "chán ăn", "mất ngủ",
            "sụt cân", "đổ mồ hôi", "ớn lạnh", "buồn nôn",
        ],
    }
    
    # Detect disease category from name
    name_lower = disease.get("name", "").lower()
    if any(k in name_lower for k in ("phổi", "ho", "hô hấp", "viêm phế", "hen")):
        group = "respiratory"
    elif any(k in name_lower for k in ("dạ dày", "ruột", "gan", "tiêu", "bụng", "đại tràng")):
        group = "gastrointestinal"
    elif any(k in name_lower for k in ("não", "thần kinh", "đầu", "động kinh", "parkinson")):
        group = "neurological"
    elif any(k in name_lower for k in ("khớp", "xương", "cột sống", "cơ", "gout")):
        group = "musculoskeletal"
    elif any(k in name_lower for k in ("da", "ban", "chàm", "vẩy", "nấm da")):
        group = "dermatological"
    elif any(k in name_lower for k in ("tim", "mạch", "huyết áp", "nhồi máu")):
        group = "cardiovascular"
    elif any(k in name_lower for k in ("nhiễm", "virus", "vi khuẩn", "lây", "sốt")):
        group = "infectious"
    else:
        group = "general"
    
    pool = SYMPTOM_GROUPS[group]
    # Add 1-2 general symptoms for variety
    extras = SYMPTOM_GROUPS["general"]
    combined = pool + [s for s in extras if s not in pool][:3]
    
    chosen = rng.sample(combined, min(3, len(combined)))
    return chosen[0], chosen[1], chosen[2]


def _clean_disease_name(raw_name: str) -> str:
    """Extract short disease name from KB title (often SEO-style article titles).
    
    Examples:
        "Dấu hiệu bệnh bạch hầu có dễ nhận biết?" → "Bạch hầu"
        "U máu gan có nguy hiểm không? Bạn có cần..." → "U máu gan"
        "Bệnh xơ phổi ở trẻ sinh non: Triệu chứng..." → "Xơ phổi"
    """
    name = raw_name.strip()
    
    # Remove question marks and everything after
    if "?" in name:
        name = name.split("?")[0].strip()
    
    # Remove everything after colon
    if ":" in name:
        name = name.split(":")[0].strip()
    
    # Remove common prefixes
    prefixes_to_remove = [
        "Dấu hiệu ", "Triệu chứng ", "Nguyên nhân ", "Điều trị ",
        "Cách chữa ", "Phòng ngừa ", "Tìm hiểu về ", "Tổng quan về ",
        "Những điều cần biết về ", "Bạn biết gì về ",
    ]
    for prefix in prefixes_to_remove:
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    
    # Remove trailing noise
    trailing_noise = [
        " có nguy hiểm không", " có dễ nhận biết", " là gì",
        " ở trẻ sơ sinh", " ở trẻ em", " ở người lớn",
        " và cách điều trị", " và cách phòng ngừa",
    ]
    for noise in trailing_noise:
        if name.lower().endswith(noise):
            name = name[: -len(noise)].strip()
            break
    
    # Ensure starts with "Bệnh" prefix is clean
    if name.lower().startswith("bệnh "):
        name = name[5:].strip()
    
    # Capitalize first letter
    if name:
        name = name[0].upper() + name[1:]
    
    # Truncate if still too long
    if len(name) > 40:
        name = name[:37].rsplit(" ", 1)[0]
    
    return name or raw_name[:30]


# ─── Core generation ─────────────────────────────────────────────────────────

def _read_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    return [item for item in data if isinstance(item, dict)]


def _clean_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(item).strip() for item in values if str(item).strip()]


def _severity_to_triage(severity: str) -> str:
    return {"low": "green", "medium": "yellow", "high": "red"}.get(severity, "yellow")


def _triage_vi(triage: str) -> str:
    return {"green": "XANH", "yellow": "VÀNG", "red": "ĐỎ"}[triage]


def _triage_emoji(triage: str) -> str:
    return {"green": "🟢", "yellow": "🟡", "red": "🔴"}[triage]


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
        if len(symptoms) < 3:
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


def _build_conversation(
    disease: dict[str, Any],
    triage: str,
    rng: random.Random,
) -> tuple[list[dict[str, str]], str]:
    """Build a natural multi-turn conversation + conclusion output."""
    # Get 3 usable symptom phrases
    s1, s2, s3 = _get_usable_symptoms(disease, rng)

    duration = rng.choice(DURATIONS)
    time_phrase = rng.choice(TIMES)
    severity_desc = rng.choice(SEVERITY_DESCS)

    # Build user turn 1
    opener = rng.choice(USER_OPENERS).format(s1=s1, s2=s2, duration=duration)

    # Build assistant turn 1 (OARS: affirm + reflect + open question)
    assist1 = rng.choice(ASSISTANT_TURN1).format(s1=s1, s2=s2)

    # Build user turn 2
    followup = rng.choice(USER_FOLLOWUPS).format(
        s3=s3, time=time_phrase, severity_desc=severity_desc
    )

    # Build assistant turn 2 (OARS: summarize + open question)
    assist2 = rng.choice(ASSISTANT_TURN2).format(s1=s1, s2=s2, s3=s3)

    # Build user turn 3
    answer = rng.choice(USER_ANSWERS)

    messages = [
        {"role": "user", "content": opener},
        {"role": "assistant", "content": assist1},
        {"role": "user", "content": followup},
        {"role": "assistant", "content": assist2},
        {"role": "user", "content": answer},
    ]

    # Build conclusion output
    output = _build_conclusion(disease, triage, rng)
    return messages, output


def _build_conclusion(
    disease: dict[str, Any],
    triage: str,
    rng: random.Random,
) -> str:
    """Build the structured conclusion output."""
    probability = rng.randint(65, 88)
    secondary_prob = rng.randint(15, 35)
    clean_name = _clean_disease_name(disease["name"])

    lines = [
        "Kết luận:",
        f"• {clean_name} ({probability}%) {_triage_emoji(triage)}",
        f"• Nguyên nhân khác cần loại trừ ({secondary_prob}%) 🟡",
        "",
        f"Mức độ: {_triage_vi(triage)}",
    ]

    if triage == "red":
        lines.append(
            "⚠️ Triệu chứng của bạn cần được đánh giá y tế sớm. Hãy đi khám bác sĩ ngay."
        )
    elif triage == "yellow":
        lines.append(
            "Khuyến nghị: Theo dõi sát triệu chứng và đi khám nếu không cải thiện trong 2-3 ngày."
        )
    else:
        lines.append(
            "Khuyến nghị: Có thể chăm sóc tại nhà, theo dõi thêm. Đi khám nếu triệu chứng kéo dài."
        )

    # Home care
    home_care = disease.get("home_care") or []
    if home_care:
        lines.append("Chăm sóc tại nhà:")
        for item in home_care[:3]:
            lines.append(f"- {item}")

    # Lab tests (not for green)
    lab_tests = disease.get("lab_tests") or []
    if triage != "green" and lab_tests:
        lines.append("Xét nghiệm nên cân nhắc:")
        for item in lab_tests[:2]:
            lines.append(f"- {item}")

    # Red flags
    red_flags = disease.get("red_flags") or []
    if red_flags:
        lines.append("Dấu hiệu cần đi cấp cứu ngay:")
        for item in red_flags[:3]:
            lines.append(f"- {_naturalize_symptom(item)}")

    lines.append(DISCLAIMER)
    return "\n".join(lines)


def _to_medgemma_text(messages: list[dict[str, str]], output: str) -> str:
    """Convert to MedGemma chat template."""
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


def generate_records(target: int = 1200, kb_path: Path = KB_PATH) -> list[dict[str, Any]]:
    """Generate balanced output-format training records."""
    diseases = disease_records(kb_path)
    if not diseases:
        raise RuntimeError("No disease records available for output-format generation.")

    rng = random.Random(SEED)
    records: list[dict[str, Any]] = []

    # Force balanced triage distribution
    triage_cycle = ["green", "yellow", "red"]

    for index in range(target):
        disease = diseases[index % len(diseases)]
        # Balanced triage — cycle through green/yellow/red regardless of disease severity
        forced_triage = triage_cycle[index % 3]

        messages, output = _build_conversation(disease, forced_triage, rng)

        records.append(
            {
                "text": _to_medgemma_text(messages, output),
                "messages": [*messages, {"role": "assistant", "content": output}],
                "output": output,
                "disease": _clean_disease_name(disease["name"]),
                "triage_level": forced_triage,
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
        "source": "generated_output_format_v2",
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
    parser.add_argument("--target", type=int, default=1200)
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
    else:
        print(f"\nWrote {stats['train']} train + {stats['eval']} eval records.")
        print("Run `python scripts/build_medgemma_rag_training_set.py` to rebuild final dataset.")


if __name__ == "__main__":
    main()
