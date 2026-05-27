"""
Regenerate Psychology Dataset using DeepSeek API
================================================

Sinh dataset OARS tiếng Việt chất lượng cao, đa dạng, không template.

Usage:
  # 1. Cài deps
  pip install openai

  # 2. Set API key (từ d2spi hoặc DeepSeek trực tiếp)
  set DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
  set DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
  # Hoặc nếu dùng d2spi/relay khác:
  # set DEEPSEEK_BASE_URL=https://api.d2spi.com/v1

  # 3. Chạy
  python scripts/regenerate_psychology_data.py --target 1500

  # Resume nếu crash
  python scripts/regenerate_psychology_data.py --resume

  # Test nhanh 40 samples
  python scripts/regenerate_psychology_data.py --target 40 --batch 10

Output:
  data/training_clean/medgemma_4b/psychology_train.jsonl  (85%)
  data/training_clean/medgemma_4b/psychology_eval.jsonl   (15%)
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
CLEAN_DIR  = ROOT / "data" / "training_clean" / "medgemma_4b"

TRAIN_FILE = CLEAN_DIR / "psychology_train.jsonl"
EVAL_FILE  = CLEAN_DIR / "psychology_eval.jsonl"
STATS_FILE = CLEAN_DIR / "psychology_regen_stats.json"

# ─── Per-model output token limits ─────────────────────────────────────
MODEL_MAX_TOKENS: dict[str, int] = {
    "gemma-3-27b-it":         128_000,
    "gemma-4-26B-A4B-it":     262_000,
    "gemma-4-31B-it":         262_000,
    "Llama-3.3-70B-Instruct":  32_000,
    "SaoLa4-medium":           32_000,
    "SaoLa4-small":            32_000,
    "Qwen3-32B":               65_000,
    "Qwen3.6-27B":            262_000,
    "gpt-oss-120b":           128_000,
}
# ~800 output tokens per dialogue (Vietnamese, 4-6 turns, ~60-80 words/assistant turn)
TOKENS_PER_SAMPLE = 800

TRAIN_RATIO = 0.85
SEED = 42


def _checkpoint_path(worker_id: int | None) -> Path:
    if worker_id is None:
        return ROOT / ".regenerate_psych_progress.json"
    return ROOT / f".regenerate_psych_progress_w{worker_id}.json"


def _part_path(worker_id: int) -> Path:
    return CLEAN_DIR / f"psychology_part_{worker_id}.jsonl"

# ─── Topics — 20 topic đa dạng ─────────────────────────────────────────
TOPICS = [
    ("lo_au_suc_khoe",       "Lo âu sức khỏe (đau đầu, tim đập nhanh, mất ngủ, sợ bệnh nặng)"),
    ("met_moi_man_tinh",     "Mệt mỏi mãn tính (kiệt sức kéo dài, không có năng lượng)"),
    ("ap_luc_cong_viec",     "Áp lực công việc (deadline, sếp khó, burnout)"),
    ("ap_luc_hoc_duong",     "Áp lực học đường (kỳ thi, điểm số, kỳ vọng gia đình)"),
    ("xung_dot_gia_dinh",    "Xung đột gia đình (cãi nhau với bố mẹ, không được hiểu)"),
    ("tinh_cam_tuoi_teen",   "Tình cảm tuổi teen (chia tay, tình bạn rạn nứt, cô đơn)"),
    ("buon_ba_mat_mat",      "Buồn bã/Mất mát (mất người thân, thú cưng)"),
    ("lo_au_tuong_lai",      "Lo âu tương lai (sự nghiệp, định hướng, sợ thất bại)"),
    ("tram_cam_nhe",         "Trầm cảm nhẹ (mất hứng thú, ngủ nhiều/ít, trống rỗng)"),
    ("roi_loan_an_uong",     "Rối loạn ăn uống (ám ảnh cân nặng, ăn quá nhiều/ít)"),
    ("co_don_xa_hoi",        "Cô đơn xã hội (khó kết bạn, không ai hiểu)"),
    ("sang_chan_qua_khu",    "Sang chấn quá khứ (bị bắt nạt, biến cố)"),
    ("van_de_ngu",           "Vấn đề ngủ (mất ngủ, ác mộng, thức khuya)"),
    ("mau_thuan_tinh_ban",   "Mâu thuẫn tình bạn (bạn thân phản bội, hiểu lầm)"),
    ("ap_luc_ngoai_hinh",    "Áp lực ngoại hình (tự ti, so sánh với người khác)"),
    ("kho_kiem_soat_cam_xuc","Khó kiểm soát cảm xúc (dễ giận, khóc, hoảng loạn)"),
    ("nghien_cong_nghe",     "Nghiện công nghệ (TikTok, game, mạng xã hội)"),
    ("mat_phuong_huong",     "Mất phương hướng tuổi trung niên (chán việc, hôn nhân nguội)"),
    ("lo_lang_lam_cha_me",   "Lo lắng làm cha/mẹ (con nhỏ, hôn nhân, tài chính)"),
    ("sang_chan_chia_tay",   "Sang chấn sau chia tay (không thể quên, đau dai dẳng)"),
]

# Persona để tăng đa dạng
PERSONAS = [
    # Độ tuổi
    "users 18-22 tuổi, sinh viên đại học",
    "users 23-30 tuổi, mới đi làm",
    "users 30-45 tuổi, đã có gia đình",
    "users 45-60 tuổi, trung niên",
    "users teen 14-17 tuổi, học sinh cấp 3",
    "users 60+ tuổi, người cao tuổi, gần hưu hoặc đã hưu",
    "users 25-35 tuổi, độc thân, sống một mình",
    "users 35-50 tuổi, phụ huynh đơn thân",
    # Giọng vùng miền / phong cách
    "users dùng giọng miền Nam (kêu, nè, hông, đó, vậy)",
    "users dùng giọng miền Bắc (nhỉ, ơi, đấy, à, thật à)",
    "users dùng giọng miền Trung (răng, rứa, mô, tề)",
    "users formal, trang trọng, viết đầy đủ câu",
    "users casual, gen Z slang (oke bro, kiểu, chill, vibe)",
    "users nội tâm, ít chia sẻ, câu ngắn, dè dặt",
    # Hoàn cảnh cụ thể
    "users là giáo viên hoặc nhân viên văn phòng",
    "users là sinh viên xa nhà, ở trọ",
    "users là người lao động phổ thông, công nhân",
    "users là dân kinh doanh, tự làm chủ",
    "users đang đi du học hoặc làm việc ở nước ngoài",
    # Không rõ thông tin — AI phải tự suy luận từ ngữ cảnh
    "unknown: không có thông tin về độ tuổi, giới tính hay hoàn cảnh — user chỉ mô tả vấn đề, không tự giới thiệu",
    # Tình trạng sức khỏe tâm thần
"users đang trong giai đoạn khủng hoảng cấp (panic, khóc nhiều, không ngủ được)",
"users có tiền sử trầm cảm hoặc lo âu, đang điều trị",
"users nghi ngờ bản thân có vấn đề tâm lý nhưng chưa đi khám",

# Giới tính & bản dạng
"users là nữ giới, nhạy cảm với cảm xúc, hay tự trách bản thân",
"users là nam giới, ít bộc lộ cảm xúc, dùng lý trí để giải thích vấn đề",
"users thuộc cộng đồng LGBTQ+, đang đối mặt với áp lực gia đình hoặc xã hội",

# Hoàn cảnh đặc biệt
"users vừa trải qua mất mát (người thân mất, chia tay, thất nghiệp)",
"users đang có ý nghĩ tiêu cực về bản thân hoặc tự làm hại",  # ⚠️ cần xử lý đặc biệt
"users chăm sóc người thân bệnh nặng, kiệt sức cảm xúc (caregiver burnout)",

# Phong cách giao tiếp bổ sung
"users hay dùng humor/meme để che giấu cảm xúc thật",
"users rất lý trí, phân tích nhiều, khó chạm vào cảm xúc",
"users hay hỏi ngược lại, thử thách hoặc không tin tưởng AI",

# Bối cảnh văn hóa
"users chịu áp lực gia đình kiểu Á Đông (hiếu thảo, kỳ vọng, so sánh)",
"users là người Việt ở nước ngoài, lạc lõng văn hóa, không thuộc về đâu",
]

# ─── System prompt cho DeepSeek ────────────────────────────────────────

SYSTEM_PROMPT = """Bạn là chuyên gia tạo dữ liệu huấn luyện AI tâm lý tiếng Việt theo phương pháp OARS (Motivational Interviewing).

NHIỆM VỤ: Sinh hội thoại Việt Nam giữa USER (người tìm hỗ trợ tâm lý) và ASSISTANT (trợ lý AI dùng OARS), 4-6 lượt nói chuyện.

OARS bắt buộc — ASSISTANT phải dùng đa dạng:
- Open question: "Bạn có thể chia sẻ thêm về...?", "Điều gì khiến...?", "Như thế nào...?"
- Affirmation: "Mình thấy bạn đã rất...", "Không dễ để chia sẻ điều này", "Bạn đã làm tốt khi..."
- Reflective listening: "Có vẻ bạn đang cảm thấy...", "Nếu mình hiểu đúng...", "Nghe bạn nói, mình cảm nhận..."
- Summary: "Tóm lại, bạn đã chia sẻ rằng...", "Cho mình xem lại — bạn đang vừa... vừa..."

YÊU CẦU NGHIÊM NGẶT:
1. ASSISTANT KHÔNG chẩn đoán, KHÔNG kê đơn, KHÔNG bảo "bạn nên...". Chỉ lắng nghe + hỏi mở.
2. Mỗi lượt ASSISTANT KHÔNG được trùng câu chữ với hội thoại khác — ĐA DẠNG TỐI ĐA.
3. USER nói tự nhiên, có chi tiết cá nhân (tuổi, công việc, hoàn cảnh), có thể vụng về.
4. ASSISTANT trả lời 30-80 từ, ấm áp nhưng KHÔNG sến súa, KHÔNG emoji.
5. Mỗi hội thoại 4-6 lượt: user → assistant → user → assistant → ...
6. Lượt assistant CUỐI CÙNG kết thúc bằng câu hỏi mở (?).
7. KHÔNG dùng từ "stress" — dùng "áp lực", "căng thẳng" tiếng Việt thuần.
8. Đa dạng độ dài, mức độ cảm xúc, hoàn cảnh.

OUTPUT FORMAT: JSON Lines (mỗi dòng 1 hội thoại JSON valid), KHÔNG markdown, KHÔNG ```json:

{"topic": "lo_au_suc_khoe", "messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]}
{"topic": "...", "messages": [...]}

Mỗi response tôi yêu cầu N hội thoại = N dòng JSON Lines."""


def make_user_prompt(batch_size: int, topics_in_batch: list[tuple], persona: str) -> str:
    topic_list = "\n".join(f"{i+1}. [{t[0]}] {t[1]}" for i, t in enumerate(topics_in_batch))
    return f"""Sinh {batch_size} hội thoại OARS tiếng Việt.

Persona: {persona}

Mỗi hội thoại lấy 1 topic theo thứ tự sau (lấy đúng tên topic làm "topic" field):
{topic_list}

Output đúng {batch_size} dòng JSON Lines. Bắt đầu."""


# ─── DeepSeek client ───────────────────────────────────────────────────

def get_client():
    try:
        from openai import OpenAI
    except ImportError:
        print("[ERROR] openai package missing. Run: pip install openai")
        sys.exit(1)

    # Support both FPT Cloud and DeepSeek/ds2api keys
    api_key = (
        os.environ.get("FPT_API_KEY")
        or os.environ.get("DEEPSEEK_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
    )
    if not api_key:
        print("[ERROR] Set FPT_API_KEY env var first.")
        print("  Windows CMD : set FPT_API_KEY=sk-xxxx")
        sys.exit(1)

    # Default base_url: FPT Cloud if using FPT key, else DeepSeek
    base_url = (
        os.environ.get("DEEPSEEK_BASE_URL")
        or os.environ.get("OPENAI_BASE_URL")
        or "https://mkp-api.fptcloud.com/v1"
    )
    print(f"  Base URL : {base_url}")
    return OpenAI(api_key=api_key, base_url=base_url)


def call_llm(client, model: str, system: str, user: str,
             temperature: float = 0.95, max_tokens: int = 2500,
             retries: int = 5) -> str | None:
    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.95,
                timeout=300,  # long timeout for big batches
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            base = min(60, 2 ** attempt + 2)
            wait = base + random.uniform(0, 3)
            msg = str(e)[:200]
            print(f"    [retry {attempt+1}/{retries}] {type(e).__name__}: {msg} — wait {wait:.1f}s")
            time.sleep(wait)
    return None


# ─── Parsing & Validation ──────────────────────────────────────────────

def parse_jsonl(raw: str) -> list[dict]:
    """Extract JSON objects from response (1 per line).

    Robust to truncated last line (when response hits max_tokens) — silently drops
    incomplete trailing JSON instead of raising.
    """
    samples = []
    raw = re.sub(r"```(?:json|jsonl)?\s*", "", raw)
    raw = re.sub(r"```\s*$", "", raw, flags=re.MULTILINE)

    lines = [ln.strip() for ln in raw.strip().split("\n") if ln.strip()]
    for line in lines:
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            # Probably the truncated last line — skip silently
            continue
        if isinstance(obj, dict) and "messages" in obj and "topic" in obj:
            samples.append(obj)
    return samples


_OARS_QUESTION_RE = re.compile(r"\?")
_FORBIDDEN_WORDS  = re.compile(r"(stress|💕|❤️|🌸|😊|😢|🤗)", re.IGNORECASE)
_DIAGNOSIS_RE     = re.compile(
    r"(bạn bị|bạn mắc|chẩn đoán|kê đơn|uống thuốc|liều dùng|nên uống)",
    re.IGNORECASE,
)


def validate_sample(sample: dict, seen_assistant_lines: set) -> tuple[bool, str]:
    messages = sample.get("messages", [])
    if not isinstance(messages, list) or len(messages) < 4:
        return False, f"too short: {len(messages)} messages"
    if len(messages) % 2 != 0:
        return False, "odd number of messages"

    # Every message must be a dict with role + content
    for i, m in enumerate(messages):
        if not isinstance(m, dict):
            return False, f"message {i} not a dict"
        if "role" not in m or "content" not in m:
            return False, f"message {i} missing role or content"
        if not isinstance(m.get("content"), str):
            return False, f"message {i} content not a string"

    roles = [m.get("role") for m in messages]
    if roles[0] != "user":
        return False, "must start with user"

    expected = ["user", "assistant"] * (len(messages) // 2)
    if roles != expected:
        return False, "wrong role pattern"

    assistant_msgs = [m["content"] for m in messages if m["role"] == "assistant"]

    # Check forbidden
    for content in assistant_msgs:
        if not isinstance(content, str) or len(content.strip()) < 20:
            return False, "assistant message too short"
        if _FORBIDDEN_WORDS.search(content):
            return False, "contains forbidden word/emoji"
        if _DIAGNOSIS_RE.search(content):
            return False, "assistant gives diagnosis"

    # Last assistant must end with ?
    if not assistant_msgs[-1].rstrip().endswith("?"):
        return False, "last assistant doesn't end with ?"

    # Each assistant turn should have a question (mostly)
    questions_count = sum(1 for m in assistant_msgs if "?" in m)
    if questions_count < len(assistant_msgs) - 1:  # allow last to be summary
        return False, "too few questions in assistant turns"

    # Length check
    for content in assistant_msgs:
        word_count = len(content.split())
        if word_count > 150:
            return False, f"assistant too long ({word_count} words)"
        if word_count < 8:
            return False, f"assistant too short ({word_count} words)"

    # ★ Anti-template: check if assistant lines are too similar to seen ones
    for content in assistant_msgs:
        # Check first 50 chars exact match
        prefix = content.strip()[:50]
        if prefix in seen_assistant_lines:
            return False, "duplicate assistant prefix (template repeat)"

    return True, ""


# ─── Format to Gemma chat template ─────────────────────────────────────

CHAT_SYSTEM = (
    "Bạn là MediSign AI, trợ lý y tế tiếng Việt. "
    "Bạn lắng nghe và hỏi thêm theo phương pháp OARS để hiểu rõ tình trạng người dùng "
    "trước khi đưa ra bất kỳ gợi ý nào."
)


def to_gemma_text(messages: list[dict]) -> str:
    lines = []
    first_user = True
    for m in messages:
        role = m["role"]
        content = m["content"].strip()
        if role == "user":
            if first_user:
                content = f"{CHAT_SYSTEM}\n\n{content}"
                first_user = False
            lines.append(f"<start_of_turn>user\n{content}<end_of_turn>")
        else:
            lines.append(f"<start_of_turn>model\n{content}<end_of_turn>")
    return "\n".join(lines)


# ─── Checkpoint ────────────────────────────────────────────────────────

def save_checkpoint(samples: list[dict], seen: set, worker_id: int | None) -> None:
    _checkpoint_path(worker_id).write_text(
        json.dumps({"samples": samples, "seen": list(seen)}, ensure_ascii=False),
        encoding="utf-8",
    )


def load_checkpoint(worker_id: int | None) -> tuple[list[dict], set]:
    cp = _checkpoint_path(worker_id)
    if not cp.exists():
        return [], set()
    data = json.loads(cp.read_text(encoding="utf-8"))
    return data.get("samples", []), set(data.get("seen", []))


# ─── Main ──────────────────────────────────────────────────────────────

def _eta(start: float, base: int, current: int, target: int) -> str:
    """Return human-readable ETA string."""
    generated = current - base
    elapsed = time.time() - start
    if generated <= 0 or elapsed <= 0:
        return "?"
    rate = generated / elapsed
    remaining = target - current
    secs = remaining / rate
    speed = f"{rate * 60:.1f}/min"
    if secs < 60:
        return f"~{secs:.0f}s ({speed})"
    if secs < 3600:
        return f"~{secs/60:.1f}min ({speed})"
    return f"~{secs/3600:.1f}h ({speed})"


def generate(target: int, batch_size: int, model: str, resume: bool,
             worker_id: int | None = None) -> None:
    print("=" * 60)
    print("Psychology Dataset Regenerator (DeepSeek)")
    print(f"  Target     : {target} samples")
    print(f"  Batch size : {batch_size}")
    print(f"  Model      : {model}")
    print(f"  Resume     : {resume}")
    print(f"  Worker ID  : {worker_id if worker_id is not None else '(single)'}")
    print("=" * 60 + "\n")

    client = get_client()

    # Stagger workers so they don't all hit upstream at the same instant
    if worker_id is not None and worker_id > 0:
        stagger = worker_id * 4.0
        print(f"[W{worker_id}] staggering start by {stagger:.0f}s...")
        time.sleep(stagger)

    samples: list[dict] = []
    seen: set = set()
    if resume:
        samples, seen = load_checkpoint(worker_id)
        print(f"[Resume] Loaded {len(samples)} existing samples\n")

    seed_offset = (worker_id or 0) * 1000
    rng = random.Random(SEED + seed_offset + len(samples))
    total_attempts = 0
    total_failed = 0
    consecutive_failures = 0
    label = f"W{worker_id}" if worker_id is not None else "M"
    start_time = time.time()
    samples_at_start = len(samples)  # for ETA calc (exclude resumed samples)

    while len(samples) < target:
        topics_batch = rng.sample(TOPICS, min(batch_size, len(TOPICS)))
        # If batch_size > number of topics, allow repeats
        if batch_size > len(TOPICS):
            extra_needed = batch_size - len(TOPICS)
            topics_batch = topics_batch + rng.choices(TOPICS, k=extra_needed)
        persona = rng.choice(PERSONAS)

        user_prompt = make_user_prompt(batch_size, topics_batch, persona)

        # Auto-scale max_tokens based on model's actual limit
        model_limit = MODEL_MAX_TOKENS.get(model, 8_000)
        max_toks = min(model_limit, TOKENS_PER_SAMPLE * batch_size + 500)

        total_attempts += 1
        progress = len(samples) / target * 100
        print(f"[{label}][{len(samples):4d}/{target}] ({progress:5.1f}%) calling DeepSeek "
              f"(batch={batch_size}, max_tok={max_toks}, persona: {persona[:30]}...)", flush=True)

        raw = call_llm(client, model, SYSTEM_PROMPT, user_prompt, max_tokens=max_toks)
        if raw is None:
            total_failed += 1
            consecutive_failures += 1
            cooldown = min(90, 10 * consecutive_failures)
            print(f"    [{label}] cooling down {cooldown}s (consec fails: {consecutive_failures})",
                  flush=True)
            time.sleep(cooldown)
            continue

        parsed = parse_jsonl(raw)
        if not parsed:
            total_failed += 1
            consecutive_failures += 1
            print(f"    [{label}][parse fail] no valid JSON in response (len={len(raw)} chars)",
                  flush=True)
            time.sleep(2)
            continue

        consecutive_failures = 0

        added = 0
        reject_reasons = {}
        for sample in parsed:
            try:
                ok, reason = validate_sample(sample, seen)
            except Exception as e:
                print(f"    [{label}][validator error] {type(e).__name__}: {e}", flush=True)
                continue
            if not ok:
                reject_reasons[reason] = reject_reasons.get(reason, 0) + 1
                continue
            try:
                for m in sample["messages"]:
                    if m["role"] == "assistant":
                        seen.add(m["content"].strip()[:50])
            except Exception:
                continue
            sample["source"] = "deepseek_oars_vi_v2"
            samples.append(sample)
            added += 1
            if len(samples) >= target:
                break

        if reject_reasons:
            top = sorted(reject_reasons.items(), key=lambda x: -x[1])[:3]
            reason_str = ", ".join(f"{r}×{n}" for r, n in top)
            print(f"    [{label}] + {added}/{len(parsed)} valid (total: {len(samples)}) "
                  f"| ETA: {_eta(start_time, samples_at_start, len(samples), target)} "
                  f"| rejected: {reason_str}", flush=True)
        else:
            print(f"    [{label}] + {added}/{len(parsed)} valid (total: {len(samples)}) "
                  f"| ETA: {_eta(start_time, samples_at_start, len(samples), target)}",
                  flush=True)

        save_checkpoint(samples, seen, worker_id)
        if worker_id is not None:
            _flush_part_file(worker_id, samples)

        # Short delay (large batches mean fewer calls anyway)
        time.sleep(0.5 + random.uniform(0, 0.5))

    save_checkpoint(samples, seen, worker_id)

    if worker_id is not None:
        _flush_part_file(worker_id, samples)
        print(f"\n[W{worker_id}] DONE → {_part_path(worker_id).relative_to(ROOT)} "
              f"({len(samples)} samples, {total_attempts} attempts, {total_failed} failed)")
        return

    _split_and_write(samples, total_attempts, total_failed, model)


def _flush_part_file(worker_id: int, samples: list[dict]) -> None:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    path = _part_path(worker_id)
    with path.open("w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")


def _split_and_write(samples: list[dict], total_attempts: int,
                     total_failed: int, model: str) -> None:
    print(f"\n[Split] {len(samples)} samples → {TRAIN_RATIO:.0%} train / {1-TRAIN_RATIO:.0%} eval")
    rng2 = random.Random(SEED)
    rng2.shuffle(samples)
    split = int(len(samples) * TRAIN_RATIO)
    train, eva = samples[:split], samples[split:]

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    def write_jsonl(path: Path, data: list[dict]) -> int:
        with path.open("w", encoding="utf-8") as f:
            for s in data:
                rec = {
                    "text": to_gemma_text(s["messages"]),
                    "messages": s["messages"],
                    "topic": s.get("topic", ""),
                    "source": s.get("source", "deepseek_oars_vi_v2"),
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return len(data)

    n_train = write_jsonl(TRAIN_FILE, train)
    n_eval  = write_jsonl(EVAL_FILE, eva)
    print(f"  Train: {n_train} → {TRAIN_FILE.relative_to(ROOT)}")
    print(f"  Eval : {n_eval} → {EVAL_FILE.relative_to(ROOT)}")

    topic_dist = {}
    for s in samples:
        t = s.get("topic", "unknown")
        topic_dist[t] = topic_dist.get(t, 0) + 1

    stats = {
        "total":           len(samples),
        "train":           n_train,
        "eval":            n_eval,
        "total_attempts":  total_attempts,
        "total_failed":    total_failed,
        "model":           model,
        "topic_distribution": dict(sorted(topic_dist.items(), key=lambda x: -x[1])),
    }
    STATS_FILE.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Stats: {STATS_FILE.relative_to(ROOT)}\n")

    cp = _checkpoint_path(None)
    if cp.exists():
        cp.unlink()

    print("=" * 60)
    print(f"DONE — {len(samples)} valid samples")
    print(f"  Topic distribution:")
    for t, n in sorted(topic_dist.items(), key=lambda x: -x[1])[:10]:
        print(f"    {t:<25} {n}")
    print("=" * 60)


def merge_parts(num_workers: int, model_label: str) -> None:
    """Merge psychology_part_*.jsonl from multiple workers, dedup, split, write."""
    print("=" * 60)
    print(f"Merging {num_workers} worker output files...")
    print("=" * 60)

    all_samples: list[dict] = []
    seen_prefix: set = set()
    per_worker = {}

    for w in range(num_workers):
        path = _part_path(w)
        if not path.exists():
            print(f"  [W{w}] {path.name} — NOT FOUND, skip")
            continue
        loaded_w = 0
        kept_w   = 0
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                loaded_w += 1
                # Cross-worker dedup using assistant prefix
                msgs = obj.get("messages", [])
                if not msgs:
                    continue
                first_assist = next(
                    (m["content"].strip()[:50] for m in msgs if m["role"] == "assistant"),
                    None,
                )
                if first_assist and first_assist in seen_prefix:
                    continue
                if first_assist:
                    seen_prefix.add(first_assist)
                all_samples.append(obj)
                kept_w += 1
        per_worker[w] = (loaded_w, kept_w)
        print(f"  [W{w}] loaded={loaded_w}  kept_after_dedup={kept_w}")

    print(f"\nTotal merged: {len(all_samples)} unique samples")
    if not all_samples:
        print("Nothing to merge.")
        return

    _split_and_write(all_samples, total_attempts=0, total_failed=0, model=model_label)

    # Write merge stats
    merge_stats = {
        "merged_total": len(all_samples),
        "per_worker": {f"w{w}": {"loaded": v[0], "kept": v[1]} for w, v in per_worker.items()},
    }
    (CLEAN_DIR / "psychology_merge_stats.json").write_text(
        json.dumps(merge_stats, ensure_ascii=False, indent=2), encoding="utf-8",
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--target", type=int, default=1500, help="Number of valid samples (per worker if --worker-id set)")
    p.add_argument("--batch", type=int, default=10, help="Samples per API call")
    p.add_argument("--model", default="gemma-3-27b-it", help="Model name")
    p.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    p.add_argument("--worker-id", type=int, default=None,
                   help="Worker ID for parallel mode (0-based). When set, writes to psychology_part_<id>.jsonl")
    p.add_argument("--merge", type=int, default=None, metavar="N",
                   help="Merge N worker output files into final train/eval, then exit")
    args = p.parse_args()

    if args.merge is not None:
        merge_parts(args.merge, args.model)
        return

    generate(args.target, args.batch, args.model, args.resume, args.worker_id)


if __name__ == "__main__":
    main()
