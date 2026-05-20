"""Generate missing RAG KB files via FPT Cloud (gemma-3-27b-it).

Sinh 2 file thiếu:
  - vietnam_common_diseases.json (mở rộng từ 10 → ~200 bệnh)
  - vietnamese_symptom_phrases.json (mở rộng từ 11 → ~500 cụm từ)

Usage:
  set FPT_API_KEY=sk-xxx
  python scripts/gen_rag_kb_data.py --target diseases --count 200
  python scripts/gen_rag_kb_data.py --target symptoms --count 500
  python scripts/gen_rag_kb_data.py --target all
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
KB_DIR = ROOT / "data" / "knowledge_base"

DISEASES_FILE = KB_DIR / "vietnam_common_diseases.json"
SYMPTOMS_FILE = KB_DIR / "vietnamese_symptom_phrases.json"


def _output_paths(worker_id: int | None) -> tuple[Path, Path]:
    """Return (diseases_path, symptoms_path), worker mode uses _w<id> suffix."""
    if worker_id is None:
        return DISEASES_FILE, SYMPTOMS_FILE
    return (
        KB_DIR / f"vietnam_common_diseases_w{worker_id}.json",
        KB_DIR / f"vietnamese_symptom_phrases_w{worker_id}.json",
    )

# ── DISEASE TOPICS — 200+ bệnh ────────────────────────────────────────
DISEASE_CATEGORIES = [
    ("hô_hấp",          "viêm họng, cảm cúm, viêm phế quản, viêm phổi, hen suyễn, viêm xoang, viêm mũi dị ứng, lao, ho gà, viêm thanh quản"),
    ("tiêu_hóa",        "viêm dạ dày, trào ngược, viêm ruột, hội chứng ruột kích thích, táo bón, tiêu chảy, viêm đại tràng, viêm gan, sỏi mật, đau bụng kinh"),
    ("tim_mạch",        "tăng huyết áp, suy tim, nhồi máu cơ tim, rối loạn nhịp tim, bệnh mạch vành, đột quỵ, viêm cơ tim, bệnh van tim"),
    ("nội_tiết",        "tiểu đường type 1, tiểu đường type 2, suy tuyến giáp, cường giáp, hội chứng Cushing, đái tháo nhạt, rối loạn kinh nguyệt"),
    ("da_liễu",         "mụn trứng cá, eczema, vảy nến, hắc lào, ghẻ, lang ben, nổi mề đay, viêm da cơ địa, zona, herpes"),
    ("xương_khớp",      "thoái hóa khớp, viêm khớp dạng thấp, gout, loãng xương, đau lưng, thoát vị đĩa đệm, đau vai gáy, hội chứng ống cổ tay"),
    ("thần_kinh",       "đau đầu migraine, đau dây thần kinh tọa, động kinh, Parkinson, Alzheimer, mất ngủ, suy nhược thần kinh"),
    ("mắt",             "viêm kết mạc, đục thủy tinh thể, glaucoma, cận thị, viễn thị, lẹo mắt, thoái hóa điểm vàng"),
    ("tai_mũi_họng",    "viêm tai giữa, ù tai, mất thính lực, viêm amidan, polyp mũi, lệch vách ngăn"),
    ("tiết_niệu",       "viêm đường tiết niệu, sỏi thận, suy thận, viêm bàng quang, phì đại tuyến tiền liệt"),
    ("phụ_khoa",        "viêm âm đạo, u xơ tử cung, lạc nội mạc tử cung, hội chứng buồng trứng đa nang, vô sinh nữ"),
    ("nam_khoa",        "rối loạn cương dương, xuất tinh sớm, viêm tinh hoàn, vô sinh nam"),
    ("ung_thư",         "ung thư phổi, ung thư gan, ung thư dạ dày, ung thư vú, ung thư cổ tử cung, ung thư đại trực tràng"),
    ("nhi_khoa",        "tay chân miệng, sốt xuất huyết, sởi, thủy đậu, quai bị, viêm tiểu phế quản trẻ em"),
    ("tâm_thần",        "trầm cảm, rối loạn lo âu, rối loạn lưỡng cực, tâm thần phân liệt, rối loạn ám ảnh cưỡng chế"),
    ("dinh_dưỡng",      "suy dinh dưỡng, thiếu máu thiếu sắt, thiếu vitamin D, béo phì, suy kiệt"),
    ("nhiễm_trùng",     "sốt rét, viêm màng não, nhiễm trùng máu, bệnh than, uốn ván"),
    ("máu",             "thiếu máu, bệnh thalassemia, bạch cầu cấp, rối loạn đông máu"),
]

# ── SYMPTOM CATEGORIES — 500+ cụm từ VN ───────────────────────────────
SYMPTOM_CATEGORIES = [
    ("đau_đầu",    "đau đầu, nhức đầu, choáng váng, đau nửa đầu, đau buốt đầu, đau như búa bổ, váng đầu, hoa mắt"),
    ("đau_bụng",   "đau bụng, đau quặn bụng, đầy hơi, chướng bụng, đau âm ỉ bụng, đau bụng dưới, đau bụng trên rốn"),
    ("đau_ngực",   "đau ngực, tức ngực, nặng ngực, đau nhói ngực, khó thở khi đau ngực, hồi hộp"),
    ("ho",         "ho khan, ho có đờm, ho ra máu, ho lâu ngày, ho dai dẳng, ho từng cơn, ho nhiều về đêm"),
    ("sốt",        "sốt cao, sốt nhẹ, sốt kéo dài, sốt từng cơn, ớn lạnh, rét run, vã mồ hôi"),
    ("mệt_mỏi",    "mệt mỏi, kiệt sức, đuối sức, uể oải, không có năng lượng, người rã rời, người ê ẩm"),
    ("ngủ",        "mất ngủ, khó vào giấc, hay tỉnh giấc, ác mộng, ngủ không sâu, dậy mệt, ngủ chập chờn"),
    ("tiêu_hóa",   "buồn nôn, nôn mửa, tiêu chảy, táo bón, đi cầu phân lỏng, đầy bụng, ợ chua, ợ nóng"),
    ("hô_hấp",     "khó thở, thở dốc, thở khò khè, nghẹt mũi, sổ mũi, đau họng, rát họng, ngứa họng"),
    ("da",         "ngứa, nổi mẩn, phát ban, da khô, da bong tróc, mụn nhọt, vết bầm, sưng đỏ"),
    ("tâm_lý",     "lo lắng, hồi hộp, căng thẳng, buồn bã, trống rỗng, mất hứng thú, dễ cáu gắt, hoang mang"),
    ("xương_khớp", "đau khớp, sưng khớp, cứng khớp, đau lưng, mỏi cơ, chuột rút, tê tay chân"),
    ("tiết_niệu",  "tiểu buốt, tiểu rắt, tiểu nhiều lần, tiểu đêm, nước tiểu vàng đậm, đái máu"),
    ("kinh_nguyệt","kinh không đều, đau bụng kinh, kinh nhiều, mất kinh, kinh nguyệt kéo dài"),
    ("mắt_tai",    "mờ mắt, đau mắt, chảy nước mắt, ù tai, đau tai, chảy mủ tai, nghe kém"),
    ("cân_nặng",   "sụt cân, tăng cân, ăn không ngon, chán ăn, ăn nhiều bất thường"),
]

# ── FPT Cloud ─────────────────────────────────────────────────────────
def get_client():
    try:
        from openai import OpenAI
    except ImportError:
        print("[ERROR] pip install openai")
        sys.exit(1)

    api_key = (
        os.environ.get("FPT_API_KEY")
        or os.environ.get("DEEPSEEK_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or ""
    ).strip()
    if not api_key:
        print("[ERROR] Set FPT_API_KEY trước. Ví dụ:")
        print("  set FPT_API_KEY=sk-xxx")
        sys.exit(1)

    base_url = (
        os.environ.get("DEEPSEEK_BASE_URL")
        or os.environ.get("OPENAI_BASE_URL")
        or "https://mkp-api.fptcloud.com/v1"
    )
    print(f"  Base URL: {base_url}")
    return OpenAI(api_key=api_key, base_url=base_url)


def call_llm(client, model, system, user, max_tokens=8000, retries=4):
    for attempt in range(retries):
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.7,
                max_tokens=max_tokens,
                top_p=0.95,
                timeout=180,
            )
            return r.choices[0].message.content or ""
        except Exception as e:
            wait = min(60, 2 ** attempt + 2)
            print(f"  [retry {attempt+1}] {type(e).__name__}: {str(e)[:120]} — {wait}s")
            time.sleep(wait)
    return None


# ── Disease generation ────────────────────────────────────────────────
DISEASE_SYSTEM = """Bạn là chuyên gia y tế Việt Nam tạo dữ liệu cho hệ thống AI tư vấn sức khỏe.

NHIỆM VỤ: Sinh các bệnh phổ biến tại Việt Nam dưới dạng JSON, mỗi bệnh 1 record với các field:
- id: snake_case unique (ví dụ "viem_hong_cap")
- type: "vietnam_common_disease"
- title: Tên bệnh tiếng Việt + tên y tế (ví dụ "Viêm họng cấp (Acute pharyngitis)")
- aliases: [3-6 tên gọi/tên khác bằng tiếng Việt]
- content: Mô tả 100-200 từ, bao gồm: triệu chứng chính, nguyên nhân thường gặp, mức độ nguy hiểm, khi nào cần đi khám
- confidence: "high" | "medium"
- source: {"name": "Vietnam common diseases — community knowledge"}
- structured: {"severity": "low|medium|high", "category": "category_name"}

YÊU CẦU:
1. Mỗi response sinh đúng số bệnh được yêu cầu, định dạng JSONL (mỗi dòng 1 JSON)
2. KHÔNG dùng markdown, KHÔNG ```json
3. Tránh trùng với danh sách đã có (sẽ cung cấp)
4. Ưu tiên bệnh phổ biến tại Việt Nam, có ngữ cảnh y tế VN
5. Content phải có triệu chứng cụ thể (giúp RAG match), không generic

VÍ DỤ:
{"id": "viem_hong_cap", "type": "vietnam_common_disease", "title": "Viêm họng cấp (Acute pharyngitis)", "aliases": ["viêm họng", "đau họng", "rát họng"], "content": "Viêm họng cấp là tình trạng viêm niêm mạc họng, thường do virus (80%) hoặc vi khuẩn liên cầu. Triệu chứng: đau rát họng, khó nuốt, sốt nhẹ, ho khan, có thể kèm sổ mũi. Bệnh tự khỏi trong 3-7 ngày với nghỉ ngơi, uống nước ấm. Cần đi khám nếu sốt >39°C kéo dài, đau họng dữ dội, có mủ amidan, khó thở.", "confidence": "high", "source": {"name": "Vietnam common diseases"}, "structured": {"severity": "low", "category": "hô_hấp"}}"""


def gen_diseases(client, model, target, batch=10, worker_id=None):
    diseases_file, _ = _output_paths(worker_id)
    existing = []
    if diseases_file.exists():
        try:
            existing = json.loads(diseases_file.read_text(encoding="utf-8"))
        except Exception:
            existing = []

    seen_ids = {item.get("id") for item in existing if isinstance(item, dict)}
    seen_titles = {item.get("title", "").lower() for item in existing if isinstance(item, dict)}

    label = f"W{worker_id}" if worker_id is not None else "M"
    print(f"\n=== [{label}] DISEASES — target {target}, existing {len(existing)} → {diseases_file.name} ===\n")

    rng = random.Random(42)
    while len(existing) < target:
        cat_name, examples = rng.choice(DISEASE_CATEGORIES)
        avoid = ", ".join(list(seen_titles)[-30:]) if seen_titles else "(none)"
        prompt = (
            f"Sinh {batch} bệnh thuộc nhóm '{cat_name}' phổ biến tại Việt Nam.\n"
            f"Ví dụ thuộc nhóm: {examples}\n\n"
            f"TRÁNH trùng với những bệnh đã có (lấy 30 cái gần nhất): {avoid}\n\n"
            f"Output: {batch} dòng JSONL hợp lệ."
        )

        progress = len(existing) / target * 100
        print(f"[{len(existing):3d}/{target}] ({progress:5.1f}%) gen '{cat_name}' batch={batch}", flush=True)

        raw = call_llm(client, model, DISEASE_SYSTEM, prompt, max_tokens=6000)
        if not raw:
            continue

        added = 0
        for line in raw.strip().split("\n"):
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            obj_id = obj.get("id", "")
            obj_title = obj.get("title", "").lower()
            if not obj_id or not obj_title:
                continue
            if obj_id in seen_ids or obj_title in seen_titles:
                continue
            if len(obj.get("content", "")) < 80:
                continue
            seen_ids.add(obj_id)
            seen_titles.add(obj_title)
            existing.append(obj)
            added += 1
            if len(existing) >= target:
                break
        print(f"  + {added} new (total {len(existing)})", flush=True)

        # Snapshot save every 20 records
        if len(existing) % 20 < batch:
            diseases_file.write_text(
                json.dumps(existing, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        time.sleep(0.5)

    diseases_file.write_text(
        json.dumps(existing, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n✅ [{label}] Wrote {len(existing)} diseases → {diseases_file.relative_to(ROOT)}\n")


# ── Symptom phrase generation ─────────────────────────────────────────
SYMPTOM_SYSTEM = """Bạn là chuyên gia ngôn ngữ y tế Việt Nam.

NHIỆM VỤ: Sinh CỤM TỪ TRIỆU CHỨNG tiếng Việt theo đa dạng cách diễn đạt.

Mỗi record JSONL gồm:
- id: snake_case unique từ phrase chính (ví dụ "dau_dau_du_doi")
- type: "vietnamese_symptom_phrase"
- title: phrase chính tiếng Việt phổ thông (ví dụ "Đau đầu dữ dội")
- aliases: [4-8 cách nói khác — bao gồm dialect miền Nam/Bắc/Trung, từ y học, từ thông tục, gen Z]
- content: 1-2 câu mô tả ngữ cảnh + có thể là dấu hiệu của bệnh gì (giúp RAG match)
- confidence: "high"
- source: {"name": "Vietnamese symptom phrases — patient-language"}
- structured: {"category": "category_name", "body_part": "..."}

YÊU CẦU:
1. Đa dạng ngôn ngữ Việt: y học (đau đầu), thông tục (nhức cái đầu), miền Nam (đầu nhức quá xá), gen Z (đầu đau muốn xỉu)
2. Mỗi response: số phrase đúng yêu cầu, JSONL valid, KHÔNG markdown
3. Content giải thích ngắn — có thể là dấu hiệu của những bệnh nào
4. Tránh trùng

VÍ DỤ:
{"id": "dau_dau_du_doi", "type": "vietnamese_symptom_phrase", "title": "Đau đầu dữ dội", "aliases": ["đau đầu kinh khủng", "nhức đầu chóng mặt", "đầu đau như búa bổ", "đầu nhức muốn nổ", "đau đầu không chịu nổi", "đầu đau quá xá"], "content": "Cảm giác đau dữ dội ở vùng đầu, có thể kèm chóng mặt, buồn nôn. Có thể là dấu hiệu của migraine, tăng huyết áp, viêm xoang, hoặc trong trường hợp nghiêm trọng là xuất huyết não.", "confidence": "high", "source": {"name": "Vietnamese symptom phrases"}, "structured": {"category": "đau_đầu", "body_part": "head"}}"""


def gen_symptoms(client, model, target, batch=15, worker_id=None):
    _, symptoms_file = _output_paths(worker_id)
    existing = []
    if symptoms_file.exists():
        try:
            existing = json.loads(symptoms_file.read_text(encoding="utf-8"))
        except Exception:
            existing = []

    seen_ids = {item.get("id") for item in existing if isinstance(item, dict)}
    seen_titles = {item.get("title", "").lower() for item in existing if isinstance(item, dict)}

    label = f"W{worker_id}" if worker_id is not None else "M"
    print(f"\n=== [{label}] SYMPTOM PHRASES — target {target}, existing {len(existing)} → {symptoms_file.name} ===\n")

    rng = random.Random(42)
    while len(existing) < target:
        cat_name, examples = rng.choice(SYMPTOM_CATEGORIES)
        avoid = ", ".join(list(seen_titles)[-40:]) if seen_titles else "(none)"
        prompt = (
            f"Sinh {batch} cụm từ triệu chứng nhóm '{cat_name}' tiếng Việt.\n"
            f"Ví dụ: {examples}\n\n"
            f"TRÁNH trùng (40 cái gần nhất): {avoid}\n\n"
            f"Output: {batch} dòng JSONL valid."
        )

        progress = len(existing) / target * 100
        print(f"[{len(existing):3d}/{target}] ({progress:5.1f}%) gen '{cat_name}' batch={batch}", flush=True)

        raw = call_llm(client, model, SYMPTOM_SYSTEM, prompt, max_tokens=5000)
        if not raw:
            continue

        added = 0
        for line in raw.strip().split("\n"):
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            obj_id = obj.get("id", "")
            obj_title = obj.get("title", "").lower()
            if not obj_id or not obj_title:
                continue
            if obj_id in seen_ids or obj_title in seen_titles:
                continue
            if len(obj.get("aliases", [])) < 3:
                continue
            seen_ids.add(obj_id)
            seen_titles.add(obj_title)
            existing.append(obj)
            added += 1
            if len(existing) >= target:
                break
        print(f"  + {added} new (total {len(existing)})", flush=True)

        if len(existing) % 30 < batch:
            symptoms_file.write_text(
                json.dumps(existing, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        time.sleep(0.5)

    symptoms_file.write_text(
        json.dumps(existing, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n✅ [{label}] Wrote {len(existing)} phrases → {symptoms_file.relative_to(ROOT)}\n")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--target", choices=["diseases", "symptoms", "all"], default="all")
    p.add_argument("--diseases-count", type=int, default=200)
    p.add_argument("--symptoms-count", type=int, default=500)
    p.add_argument("--model", default="gemma-3-27b-it")
    p.add_argument("--batch", type=int, default=10)
    p.add_argument("--worker-id", type=int, default=None,
                   help="0 hoặc 1 — chia category thành 2 nhóm khi chạy 2 worker song song")
    args = p.parse_args()

    print("=" * 60)
    print("  RAG KB Data Generator (FPT Cloud)")
    print(f"  Model     : {args.model}")
    print(f"  Worker ID : {args.worker_id if args.worker_id is not None else '(single)'}")
    print("=" * 60)

    # Worker mode: split categories into 2 halves
    global DISEASE_CATEGORIES, SYMPTOM_CATEGORIES
    if args.worker_id is not None:
        if args.worker_id == 0:
            DISEASE_CATEGORIES = DISEASE_CATEGORIES[::2]
            SYMPTOM_CATEGORIES = SYMPTOM_CATEGORIES[::2]
        elif args.worker_id == 1:
            DISEASE_CATEGORIES = DISEASE_CATEGORIES[1::2]
            SYMPTOM_CATEGORIES = SYMPTOM_CATEGORIES[1::2]
        print(f"  Disease categories assigned: {len(DISEASE_CATEGORIES)}")
        print(f"  Symptom categories assigned: {len(SYMPTOM_CATEGORIES)}")

    client = get_client()

    if args.target in ("diseases", "all"):
        gen_diseases(client, args.model, args.diseases_count, batch=args.batch,
                     worker_id=args.worker_id)
    if args.target in ("symptoms", "all"):
        gen_symptoms(client, args.model, args.symptoms_count, batch=args.batch + 5,
                     worker_id=args.worker_id)


if __name__ == "__main__":
    main()
