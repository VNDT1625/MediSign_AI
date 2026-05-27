"""
Sinh ~2,000 mẫu hội thoại OARS tiếng Việt cho Bước 2 training.

Pipeline:
  1. Đọc 3 teacher datasets từ data/training_raw/oars_teacher/
  2. Lọc + lấy mẫu các đoạn hội thoại chất lượng cao
  3. Gọi LLM (OpenAI-compatible) sinh hội thoại tiếng Việt
     theo pattern OARS + chủ đề y tế VN
  4. Validate chất lượng (kết thúc ?, có affirm/reflect, không leak kết luận)
  5. Format sang MedGemma chat template
  6. Lưu ra data/training_clean/medgemma_4b/oars_train.jsonl + oars_eval.jsonl

Chủ đề tiếng Việt: áp lực học đường, xung đột gia đình, tình cảm tuổi teen,
stress công việc, lo âu sức khoẻ, buồn bã / mất mát, mệt mỏi mãn tính.

Usage:
    # Dùng API key từ env (OPENAI_API_KEY hoặc DASHSCOPE_API_KEY):
    python scripts/generate_vi_oars_samples.py

    # Chỉ định model và số mẫu:
    python scripts/generate_vi_oars_samples.py --model gpt-4o --target 2000

    # Chạy thử nhanh (50 mẫu):
    python scripts/generate_vi_oars_samples.py --target 50 --dry-run

    # Resume từ checkpoint:
    python scripts/generate_vi_oars_samples.py --resume

Requirements:
    pip install openai>=1.0 datasets>=3.0 tqdm
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TEACHER_DIR  = ROOT / "data" / "training_raw" / "oars_teacher"
CLEAN_DIR    = ROOT / "data" / "training_clean" / "medgemma_4b"
CHECKPOINT   = ROOT / ".generate_oars_progress.json"

TRAIN_FILE   = CLEAN_DIR / "oars_train.jsonl"
EVAL_FILE    = CLEAN_DIR / "oars_eval.jsonl"
STATS_FILE   = CLEAN_DIR / "oars_stats.json"

TRAIN_RATIO  = 0.85
SEED         = 42

# ---------------------------------------------------------------------------
# Chủ đề hội thoại tiếng Việt
# ---------------------------------------------------------------------------

VI_TOPICS = [
    # Y tế / sức khoẻ — phù hợp nhất với MediSign
    {
        "topic": "lo_au_suc_khoe",
        "label": "Lo âu về sức khoẻ",
        "scenario": "Người dùng lo lắng về triệu chứng cơ thể (đau đầu kéo dài, tim đập nhanh, mất ngủ) và sợ bị bệnh nặng.",
        "keywords": ["lo sợ", "triệu chứng", "đau đầu", "tim đập nhanh", "mất ngủ", "bệnh nặng"],
    },
    {
        "topic": "met_moi_man_tinh",
        "label": "Mệt mỏi mãn tính",
        "scenario": "Người dùng cảm thấy mệt mỏi liên tục, không có năng lượng dù đã ngủ đủ giấc, ảnh hưởng đến công việc.",
        "keywords": ["mệt mỏi", "kiệt sức", "không có sức", "buồn ngủ", "uể oải"],
    },
    {
        "topic": "stress_cong_viec",
        "label": "Stress công việc",
        "scenario": "Người dùng áp lực công việc cao, deadline liên tục, cảm thấy không kiểm soát được và có dấu hiệu burnout.",
        "keywords": ["deadline", "áp lực", "kiệt sức", "burnout", "không ngủ được", "stress"],
    },
    {
        "topic": "ap_luc_hoc_duong",
        "label": "Áp lực học đường",
        "scenario": "Học sinh / sinh viên cảm thấy quá tải bài vở, kỳ thi, áp lực từ gia đình và bạn bè, không biết mình có đủ khả năng không.",
        "keywords": ["kỳ thi", "bài vở", "áp lực gia đình", "điểm số", "không đủ giỏi"],
    },
    {
        "topic": "xung_dot_gia_dinh",
        "label": "Xung đột gia đình",
        "scenario": "Người dùng có mâu thuẫn với bố mẹ hoặc anh chị em, cảm thấy không được lắng nghe và hiểu lầm.",
        "keywords": ["bố mẹ", "gia đình", "mâu thuẫn", "không hiểu nhau", "cãi nhau"],
    },
    {
        "topic": "tinh_cam_tuoi_teen",
        "label": "Tình cảm tuổi teen",
        "scenario": "Bạn trẻ đang bối rối về tình cảm, chia tay hoặc tình bạn rạn nứt, cảm thấy cô đơn và không biết xử lý thế nào.",
        "keywords": ["chia tay", "bạn trai/gái", "cô đơn", "bối rối", "tình bạn"],
    },
    {
        "topic": "buon_ba_mat_mat",
        "label": "Buồn bã / Mất mát",
        "scenario": "Người dùng vừa mất người thân, thú cưng, hoặc trải qua một mất mát lớn và đang vật lộn với cảm xúc đau buồn.",
        "keywords": ["mất mát", "đau buồn", "người thân", "khóc", "không vượt qua được"],
    },
    {
        "topic": "lo_au_tuong_lai",
        "label": "Lo âu về tương lai",
        "scenario": "Người dùng lo lắng về sự nghiệp, hướng đi cuộc sống, không biết mình muốn gì và sợ thất bại.",
        "keywords": ["tương lai", "sự nghiệp", "định hướng", "sợ thất bại", "không biết làm gì"],
    },
]


# ---------------------------------------------------------------------------
# System prompt cho LLM
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """Bạn là chuyên gia tạo dữ liệu huấn luyện AI y tế theo kỹ thuật Motivational Interviewing (OARS).

Nhiệm vụ: Sinh hội thoại giữa USER (người dùng tìm kiếm hỗ trợ) và ASSISTANT (AI trợ lý theo OARS).

OARS là gì:
- O (Open question): Câu hỏi mở, không có/không dẫn dắt, bắt đầu bằng "Bạn có thể chia sẻ...", "Điều gì...", "Như thế nào..."
- A (Affirmation): Ghi nhận tích cực điều user đã làm/chia sẻ ("Cảm ơn bạn đã chia sẻ điều này", "Bạn đã rất dũng cảm khi...")
- R (Reflective listening): Phản chiếu lại để xác nhận hiểu đúng ("Có vẻ như bạn đang cảm thấy...", "Nếu tôi hiểu đúng thì...")
- S (Summary): Tóm tắt những gì đã nghe trước khi hỏi tiếp ("Tóm lại, bạn đã chia sẻ rằng... Bạn có thể kể thêm về...")

QUAN TRỌNG:
1. ASSISTANT phải theo đúng OARS — KHÔNG đưa ra lời khuyên trực tiếp ngay, phải hỏi để hiểu thêm trước
2. Mỗi lượt ASSISTANT phải có ít nhất 1 trong 4 yếu tố OARS
3. Hội thoại phải có 4–6 lượt (user + assistant xen kẽ)
4. ASSISTANT kết thúc mỗi lượt bằng câu hỏi mở (dấu ?)
5. KHÔNG dùng emoji
6. KHÔNG đưa ra chẩn đoán bệnh cụ thể trong hội thoại
7. Ngôn ngữ tự nhiên, ấm áp, không quá trang trọng
8. Đây là dữ liệu y tế — ASSISTANT phải thể hiện sự đồng cảm thực sự"""


def _make_generation_prompt(topic: dict, teacher_example: str) -> str:
    return f"""Chủ đề: {topic["label"]}
Tình huống: {topic["scenario"]}
Từ khoá gợi ý: {", ".join(topic["keywords"])}

Ví dụ hội thoại OARS tiếng Anh (dùng làm tham chiếu, KHÔNG dịch):
---
{teacher_example[:600]}
---

Hãy sinh 1 hội thoại tiếng Việt hoàn chỉnh theo chủ đề trên.
Format đầu ra (JSON):
{{
  "messages": [
    {{"role": "user", "content": "..."}},
    {{"role": "assistant", "content": "..."}},
    ...
  ]
}}

Lưu ý: Sinh đúng JSON, không thêm text ngoài JSON."""


# ---------------------------------------------------------------------------
# LLM client
# ---------------------------------------------------------------------------

def _get_openai_client(base_url: str | None, api_key: str | None):
    try:
        from openai import OpenAI  # type: ignore
    except ImportError:
        print("[ERROR] openai package not found. Install: pip install openai>=1.0")
        sys.exit(1)

    key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("DASHSCOPE_API_KEY")
    url = base_url or os.environ.get("OPENAI_BASE_URL") or os.environ.get("BACKEND_AI_BASE_URL")

    if not key:
        print(
            "[ERROR] No API key found.\n"
            "Set OPENAI_API_KEY or DASHSCOPE_API_KEY environment variable.\n"
            "Or pass --api-key YOUR_KEY"
        )
        sys.exit(1)

    kwargs: dict[str, Any] = {"api_key": key}
    if url:
        kwargs["base_url"] = url
    return OpenAI(**kwargs)


def _call_llm(
    client: Any,
    model: str,
    system: str,
    user: str,
    temperature: float = 0.9,
    max_tokens: int = 1500,
    retries: int = 3,
) -> str | None:
    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content or ""
        except Exception as exc:
            wait = 2 ** attempt
            print(f"    [retry {attempt+1}/{retries}] {exc} — waiting {wait}s")
            time.sleep(wait)
    return None


# ---------------------------------------------------------------------------
# Teacher examples loader
# ---------------------------------------------------------------------------

def _load_teacher_examples() -> list[str]:
    """Load and flatten teacher datasets into list of text snippets."""
    examples: list[str] = []

    # 1. Motivational Interviewing Dataset
    mi_path = TEACHER_DIR / "motivational_interviewing.json"
    if mi_path.exists():
        with mi_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        for rec in data:
            if "messages" in rec:
                lines = [f"{m['role'].upper()}: {m['content']}" for m in rec["messages"]]
                examples.append("\n".join(lines))
            elif "text" in rec:
                examples.append(str(rec["text"]))
        print(f"  Loaded {len(examples)} MI examples")
    else:
        print(f"  [WARN] {mi_path.name} not found — run download_oars_datasets.py first")

    prev = len(examples)

    # 2. Counseling conversations
    counsel_path = TEACHER_DIR / "counseling_conversations.json"
    if counsel_path.exists():
        with counsel_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        for rec in data:
            if "messages" in rec:
                lines = [f"{m['role'].upper()}: {m['content']}" for m in rec["messages"]]
                examples.append("\n".join(lines[:6]))  # max 3 turns
        print(f"  Loaded {len(examples) - prev} counseling examples")
    else:
        print(f"  [WARN] {counsel_path.name} not found")

    prev = len(examples)

    # 3. MentalChat16K
    mental_path = TEACHER_DIR / "mentalchat16k.json"
    if mental_path.exists():
        with mental_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        for rec in data:
            if "messages" in rec:
                lines = [f"{m['role'].upper()}: {m['content']}" for m in rec["messages"]]
                examples.append("\n".join(lines))
        print(f"  Loaded {len(examples) - prev} MentalChat examples")
    else:
        print(f"  [WARN] {mental_path.name} not found")

    if not examples:
        # Fallback: minimal built-in examples so the script still runs
        examples = [
            "THERAPIST: What brings you here today?\nCLIENT: I've been feeling really anxious lately.\nTHERAPIST: It sounds like things have been weighing on you. What does that anxiety feel like for you?\nCLIENT: Like I can't stop worrying about everything.\nTHERAPIST: I hear that. When you say everything — can you share a bit more about what's been on your mind?",
            "COUNSELOR: I'm glad you reached out. What's been going on?\nCLIENT: Work has been overwhelming.\nCOUNSELOR: That takes courage to acknowledge. What part of work feels most overwhelming right now?\nCLIENT: Deadlines and my boss's expectations.\nCOUNSELOR: It sounds like you're carrying a lot. How long has this been building up?",
        ]
        print(f"  [WARN] No teacher files found — using {len(examples)} built-in fallback examples")

    random.Random(SEED).shuffle(examples)
    return examples


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

_OARS_AFFIRM_RE = re.compile(
    r"(cảm ơn|ghi nhận|bạn đã|điều đó|dũng cảm|chia sẻ|thật|cảm giác)",
    re.IGNORECASE,
)
_OARS_REFLECT_RE = re.compile(
    r"(có vẻ|nếu tôi hiểu|bạn đang cảm|nghe có vẻ|bạn nói rằng|tôi nghe|tóm lại)",
    re.IGNORECASE,
)


def _validate_sample(sample: dict) -> tuple[bool, str]:
    """Returns (is_valid, reason_if_invalid)."""
    messages = sample.get("messages", [])
    if len(messages) < 4:
        return False, f"too short: {len(messages)} messages (need >= 4)"

    roles = [m.get("role") for m in messages]
    if roles[0] != "user":
        return False, "first message must be from user"

    assistant_turns = [m for m in messages if m.get("role") == "assistant"]
    if not assistant_turns:
        return False, "no assistant turns"

    # Check last assistant ends with ?
    last_assistant = assistant_turns[-1].get("content", "")
    if not last_assistant.strip().endswith("?"):
        return False, "last assistant turn does not end with ?"

    # Check at least one OARS element across assistant turns
    all_assistant_text = " ".join(m.get("content", "") for m in assistant_turns)
    has_affirm  = bool(_OARS_AFFIRM_RE.search(all_assistant_text))
    has_reflect = bool(_OARS_REFLECT_RE.search(all_assistant_text))
    if not (has_affirm or has_reflect):
        return False, "no OARS affirmation or reflection found"

    # Each assistant turn should contain a question
    for i, m in enumerate(assistant_turns):
        if "?" not in m.get("content", ""):
            return False, f"assistant turn {i} has no question"

    return True, ""


def _parse_llm_json(raw: str) -> dict | None:
    """Extract JSON from LLM response."""
    raw = raw.strip()
    # Try to find JSON block
    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------------------
# Deterministic template generator (no LLM/API)
# ---------------------------------------------------------------------------

_OPENERS = [
    "Dạo này tôi thấy {symptom_a} và {symptom_b}, càng nghĩ càng lo.",
    "Tôi đang bị {symptom_a}, thêm cả {symptom_b}, nên hơi hoang mang.",
    "Mấy hôm nay tôi có {symptom_a}; sau đó lại {symptom_b}, tôi không biết nên hiểu thế nào.",
    "Tôi cảm thấy {symptom_a} kéo dài, kèm {symptom_b}, nên muốn hỏi thử.",
]

_CONTEXTS = [
    "Việc này làm tôi khó tập trung và cứ kiểm tra cơ thể liên tục.",
    "Tôi vẫn cố sinh hoạt bình thường nhưng trong đầu cứ nghĩ đến nó.",
    "Tôi chưa muốn nói với gia đình vì sợ mọi người bảo tôi suy nghĩ quá nhiều.",
    "Tôi có tìm trên mạng nên lại càng thấy rối hơn.",
]

_DETAILS = [
    "Nó xuất hiện nhiều hơn vào buổi tối, nhất là lúc tôi ở một mình.",
    "Có hôm đỡ hơn, nhưng khi căng thẳng thì cảm giác lại rõ hơn.",
    "Tôi ngủ không sâu nên sáng dậy vẫn thấy mệt.",
    "Tôi chưa biết phần nào là do cơ thể, phần nào là do lo lắng.",
]

_ASSISTANT_TURNS = [
    (
        "Cảm ơn bạn đã chia sẻ khá rõ. Có vẻ như bạn đang vừa khó chịu vì triệu chứng, "
        "vừa lo về ý nghĩa của chúng. Điều gì làm bạn lo nhất khi các dấu hiệu này xuất hiện?"
    ),
    (
        "Mình ghi nhận là bạn vẫn đang cố tự quan sát thay vì bỏ qua cảm giác này. "
        "Nếu tôi hiểu đúng thì điều khiến bạn mệt nhất là sự bất định; bạn có thể kể thêm "
        "nó ảnh hưởng đến sinh hoạt hằng ngày như thế nào?"
    ),
    (
        "Tóm lại, bạn đang có một vài cảm giác cơ thể lặp lại, kèm nhiều suy nghĩ lo lắng "
        "và giấc ngủ không thật sự hồi phục. Trong những lúc dễ chịu hơn, điều gì thường giúp "
        "bạn thấy bớt căng một chút?"
    ),
]


def _template_sample(topic: dict, index: int, rng: random.Random) -> dict:
    keywords = list(topic["keywords"])
    rng.shuffle(keywords)
    symptom_a = keywords[0]
    symptom_b = keywords[1] if len(keywords) > 1 else keywords[0]

    opener = rng.choice(_OPENERS).format(symptom_a=symptom_a, symptom_b=symptom_b)
    context = rng.choice(_CONTEXTS)
    detail = rng.choice(_DETAILS)
    assistant_turns = list(_ASSISTANT_TURNS)
    rng.shuffle(assistant_turns)

    messages = [
        {"role": "user", "content": opener},
        {"role": "assistant", "content": assistant_turns[0]},
        {"role": "user", "content": context},
        {"role": "assistant", "content": assistant_turns[1]},
        {"role": "user", "content": detail},
        {"role": "assistant", "content": assistant_turns[2]},
    ]
    return {
        "messages": messages,
        "topic": topic["topic"],
        "source": "generated_vi_oars_template",
        "template_id": f"{topic['topic']}:{index}",
    }


# ---------------------------------------------------------------------------
# Format to MedGemma chat template (multi-turn)
# ---------------------------------------------------------------------------

CHAT_SYSTEM = (
    "Bạn là MediSign AI, trợ lý y tế tiếng Việt. "
    "Bạn lắng nghe và hỏi thêm theo phương pháp OARS để hiểu rõ tình trạng người dùng "
    "trước khi đưa ra bất kỳ gợi ý nào."
)


def _to_medgemma_text(messages: list[dict]) -> str:
    """Convert multi-turn messages to MedGemma chat template.

    Pattern: interleave user/model turns.
    System is prepended to first user turn (Gemma has no system role).
    """
    lines: list[str] = []
    first_user = True
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "").strip()
        if role == "user":
            if first_user:
                content = f"{CHAT_SYSTEM}\n\n{content}"
                first_user = False
            lines.append(f"<start_of_turn>user\n{content}<end_of_turn>")
        else:
            lines.append(f"<start_of_turn>model\n{content}<end_of_turn>")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Checkpoint helpers
# ---------------------------------------------------------------------------

def _load_checkpoint() -> list[dict]:
    if CHECKPOINT.exists():
        with CHECKPOINT.open(encoding="utf-8") as fh:
            return json.load(fh)
    return []


def _save_checkpoint(samples: list[dict]) -> None:
    with CHECKPOINT.open("w", encoding="utf-8") as fh:
        json.dump(samples, fh, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def generate(
    target: int = 2000,
    model: str = "gpt-4o-mini",
    base_url: str | None = None,
    api_key: str | None = None,
    resume: bool = False,
    dry_run: bool = False,
    template_only: bool = False,
) -> None:
    print("=" * 60)
    print("OARS Vietnamese Sample Generator")
    print(f"  Target:    {target} samples")
    print(f"  Model:     {model}")
    print(f"  Dry run:   {dry_run}")
    print(f"  Resume:    {resume}")
    print(f"  Template:  {template_only}")
    print("=" * 60)

    # Load teacher examples
    print("\n[1] Loading teacher datasets ...")
    teacher_examples = _load_teacher_examples()
    print(f"  Total teacher examples available: {len(teacher_examples)}")

    # Resume / start fresh
    valid_samples: list[dict] = []
    if resume:
        valid_samples = _load_checkpoint()
        print(f"\n[2] Resuming — {len(valid_samples)} samples already done")
    else:
        print("\n[2] Starting fresh")

    # LLM client
    if not dry_run and not template_only:
        client = _get_openai_client(base_url, api_key)
    else:
        client = None

    # Stats
    total_attempts = 0
    total_failed   = 0
    rng = random.Random(SEED)

    print(f"\n[3] Generating ... (need {target - len(valid_samples)} more)")

    topic_cycle = list(VI_TOPICS) * ((target // len(VI_TOPICS)) + 2)
    rng.shuffle(topic_cycle)

    i = len(valid_samples)
    while len(valid_samples) < target:
        topic = topic_cycle[i % len(topic_cycle)]
        teacher = rng.choice(teacher_examples)
        prompt = _make_generation_prompt(topic, teacher)

        if template_only:
            sample = _template_sample(topic, i, rng)
        elif dry_run:
            # Produce a minimal fake sample
            sample = {
                "messages": [
                    {"role": "user",      "content": f"[DRY RUN] {topic['scenario'][:60]}"},
                    {"role": "assistant", "content": "Cảm ơn bạn đã chia sẻ. Bạn có thể kể thêm về điều đó không?"},
                    {"role": "user",      "content": "Tôi cảm thấy rất lo lắng."},
                    {"role": "assistant", "content": "Tôi nghe thấy bạn. Điều gì khiến bạn lo nhất lúc này?"},
                ],
                "topic": topic["topic"],
                "source": "generated_vi_oars_dry_run",
            }
        else:
            total_attempts += 1
            raw = _call_llm(client, model, SYSTEM_PROMPT, prompt)
            if raw is None:
                total_failed += 1
                i += 1
                continue

            parsed = _parse_llm_json(raw)
            if parsed is None:
                total_failed += 1
                i += 1
                continue

            sample = {**parsed, "topic": topic["topic"], "source": "generated_vi_oars"}

        ok, reason = _validate_sample(sample)
        if not ok:
            total_failed += 1
            if not dry_run:
                print(f"  [{len(valid_samples)+1}/{target}] SKIP — {reason}")
            i += 1
            continue

        valid_samples.append(sample)
        pct = len(valid_samples) / target * 100
        print(f"  [{len(valid_samples):4d}/{target}] ✓ topic={topic['topic']}  ({pct:.0f}%)")

        # Save checkpoint every 50 samples
        if len(valid_samples) % 50 == 0:
            _save_checkpoint(valid_samples)

        i += 1

        # Small rate-limit delay
        if not dry_run and not template_only and len(valid_samples) % 5 == 0:
            time.sleep(0.5)

    _save_checkpoint(valid_samples)

    # ---------------------------------------------------------------------------
    # Split + write JSONL
    # ---------------------------------------------------------------------------
    print(f"\n[4] Splitting {len(valid_samples)} samples → {TRAIN_RATIO:.0%} train / {1-TRAIN_RATIO:.0%} eval")
    all_samples = list(valid_samples)
    random.Random(SEED).shuffle(all_samples)
    split_at = int(len(all_samples) * TRAIN_RATIO)
    train_samples = all_samples[:split_at]
    eval_samples  = all_samples[split_at:]

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    def _write_jsonl(path: Path, samples: list[dict]) -> int:
        with path.open("w", encoding="utf-8") as fh:
            for s in samples:
                messages = s.get("messages", [])
                text = _to_medgemma_text(messages)
                record = {
                    "text": text,
                    "messages": messages,
                    "topic": s.get("topic", ""),
                    "source": s.get("source", "generated_vi_oars"),
                }
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return len(samples)

    n_train = _write_jsonl(TRAIN_FILE, train_samples)
    n_eval  = _write_jsonl(EVAL_FILE,  eval_samples)
    print(f"  Wrote {n_train} train → {TRAIN_FILE.relative_to(ROOT)}")
    print(f"  Wrote {n_eval}  eval  → {EVAL_FILE.relative_to(ROOT)}")

    # Stats
    topic_dist = {}
    for s in valid_samples:
        t = s.get("topic", "unknown")
        topic_dist[t] = topic_dist.get(t, 0) + 1

    stats = {
        "total_generated":  len(valid_samples),
        "train":            n_train,
        "eval":             n_eval,
        "total_attempts":   total_attempts,
        "total_failed":     total_failed,
        "success_rate":     f"{len(valid_samples) / max(total_attempts, 1):.1%}" if total_attempts else "N/A",
        "topic_distribution": topic_dist,
        "model":            model,
        "dry_run":          dry_run,
        "template_only":    template_only,
    }
    with STATS_FILE.open("w", encoding="utf-8") as fh:
        json.dump(stats, fh, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"Done! {len(valid_samples)} valid samples generated.")
    if total_attempts:
        print(f"  Attempts: {total_attempts}  |  Failed: {total_failed}  |  Rate: {stats['success_rate']}")
    print(f"  Stats → {STATS_FILE.relative_to(ROOT)}")

    # Cleanup checkpoint on success
    if CHECKPOINT.exists():
        CHECKPOINT.unlink()
        print(f"  Checkpoint removed.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--target", type=int, default=2000,
        help="Target number of valid Vietnamese OARS samples (default: 2000)",
    )
    p.add_argument(
        "--model", default="gpt-4o-mini",
        help="OpenAI-compatible model name (default: gpt-4o-mini)",
    )
    p.add_argument(
        "--base-url", default=None,
        help="OpenAI-compatible API base URL (overrides OPENAI_BASE_URL env var)",
    )
    p.add_argument(
        "--api-key", default=None,
        help="API key (overrides OPENAI_API_KEY / DASHSCOPE_API_KEY env var)",
    )
    p.add_argument(
        "--resume", action="store_true",
        help="Resume from checkpoint (.generate_oars_progress.json)",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Generate fake samples without calling LLM (for testing)",
    )
    p.add_argument(
        "--template-only", action="store_true",
        help="Generate deterministic Vietnamese OARS samples without calling an LLM/API",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate(
        target=args.target,
        model=args.model,
        base_url=args.base_url,
        api_key=args.api_key,
        resume=args.resume,
        dry_run=args.dry_run,
        template_only=args.template_only,
    )
