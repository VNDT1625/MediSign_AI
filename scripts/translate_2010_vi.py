"""Translate the Chinese Q&A in `data/training_clean/qwen_72b/2010_vi.json`
to Vietnamese using FPT Cloud AI marketplace (Qwen3.6-27B).

Features:
- API key + endpoint hard-coded as requested.
- Concurrent translation with bounded thread pool.
- Per-record progress file => safe to Ctrl+C and rerun.
- Retries with exponential backoff for transient errors.
- Final output written to a sibling file (does NOT overwrite the input).

Run:
    python scripts/translate_2010_vi.py

Optional flags:
    --workers N      Number of concurrent requests (default 6).
    --limit N        Translate only first N records (smoke test).
    --start N        Start index (0-based) -- use with --limit for chunked runs.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import urllib.request
import urllib.error

# ============================== CONFIG (HARD-CODED) ============================
FPT_API_KEY = "sk-Sn2MChJ8HeO8GcZvg4HMizirOXapHUzuH9J4x2Bgj1k="
FPT_BASE_URL = "https://mkp-api.fptcloud.com/v1"
MODEL_ID = "Qwen3.6-27B"

ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = ROOT / "data" / "training_clean" / "qwen_72b" / "2010_vi.json"
OUTPUT_PATH = ROOT / "data" / "training_clean" / "qwen_72b" / "2010_vi_translated.json"
PROGRESS_PATH = ROOT / "data" / "training_clean" / "qwen_72b" / ".2010_vi_translate_progress.jsonl"
# ==============================================================================

SYSTEM_PROMPT = """Bạn là dịch giả y khoa chuyên nghiệp với 20 năm kinh nghiệm dịch tài liệu y tế Trung - Việt cho bệnh viện và sách giáo khoa Y dược Việt Nam. Nhiệm vụ: dịch đoạn hội thoại y tế tiếng Trung sang tiếng Việt CHUẨN Y KHOA.

YÊU CẦU TUYỆT ĐỐI VỀ THUẬT NGỮ:

A. TÊN BỆNH / CHẨN ĐOÁN
- Dùng thuật ngữ trong "Danh mục bệnh quốc tế ICD-10 phiên bản tiếng Việt" của Bộ Y tế.
- Ưu tiên Hán-Việt chuẩn đã thông dụng trong y học Việt Nam, KHÔNG dịch nôm na hay thuần Việt hóa.
- Ví dụ chuẩn:
    新生儿黄疸 → "vàng da sơ sinh" (KHÔNG dịch "vàng da trẻ mới đẻ")
    高血压 → "tăng huyết áp" (KHÔNG "huyết áp cao")
    糖尿病 → "đái tháo đường" (KHÔNG "tiểu đường" trong văn cảnh học thuật, có thể dùng "tiểu đường" khi BS giải thích cho BN)
    冠心病 → "bệnh động mạch vành" / "bệnh tim mạch vành"
    脑梗塞/脑梗死 → "nhồi máu não"
    脑出血 → "xuất huyết não"
    心肌梗死 → "nhồi máu cơ tim"
    肺炎 → "viêm phổi"
    支气管炎 → "viêm phế quản"
    胃炎 → "viêm dạ dày"
    肝硬化 → "xơ gan"
    乙肝 → "viêm gan B"; 丙肝 → "viêm gan C"
    白血病 → "bệnh bạch cầu" (lưu ý: trong văn cảnh học thuật là "leukemia/bệnh bạch cầu", trong giao tiếp với BN có thể dùng "ung thư máu")
    毛囊炎 → "viêm nang lông" (KHÔNG "viêm chân lông")
    疱疹 → "herpes" / "mụn rộp"; 生殖器疱疹 → "herpes sinh dục"
    早泄 → "xuất tinh sớm"
    宫颈糜烂 → "loét cổ tử cung" / "lộ tuyến cổ tử cung"
    输卵管 → "vòi trứng" / "vòi tử cung"
    子宫 → "tử cung"; 卵巢 → "buồng trứng"
    胆囊炎 → "viêm túi mật"; 胰腺炎 → "viêm tụy"

B. TRIỆU CHỨNG
- Dùng thuật ngữ y khoa, KHÔNG dịch văn nói:
    咳嗽 → "ho"; 干咳 → "ho khan"; 咳痰 → "ho khạc đờm"
    痰堵 → "tắc đờm" / "đờm ứ đọng"; 雾化 → "khí dung"
    扣背吸痰 → "vỗ rung lồng ngực, hút đờm"
    黄疸 → "vàng da, vàng mắt"; 肝功能异常 → "rối loạn chức năng gan"
    胸闷 → "tức ngực"; 心悸 → "đánh trống ngực"
    头晕 → "chóng mặt"; 眩晕 → "hoa mắt chóng mặt" / "rối loạn tiền đình"
    乏力 → "mệt mỏi"; 食欲不振 → "chán ăn"
    腹泻 → "tiêu chảy"; 便秘 → "táo bón"; 便血 → "đi ngoài ra máu"
    呕吐 → "nôn"; 恶心 → "buồn nôn"
    皮疹 → "phát ban"; 瘙痒 → "ngứa"
    水肿 → "phù"; 浮肿 → "phù"

C. THUỐC & XÉT NGHIỆM
- Giữ nguyên tên hoạt chất theo INN tiếng Anh hoặc phiên âm Hán-Việt chuẩn:
    阿司匹林 → "aspirin"; 青霉素 → "penicillin"; 头孢 → "cephalosporin"
    阿莫西林 → "amoxicillin"; 奥美拉唑 → "omeprazole"
    胰岛素 → "insulin"; 二甲双胍 → "metformin"
    阿德福韦/阿德福韦酯 → "adefovir"; 拉米夫定 → "lamivudine"; 恩替卡韦 → "entecavir"
    消炎药 → "thuốc kháng viêm" / "kháng sinh" (tùy ngữ cảnh, lưu ý 消炎药 thường được hiểu là kháng sinh trong tiếng Trung dù không chính xác về mặt y học)
    转氨酶 → "men gan / transaminase"; ALT/AST giữ nguyên
    血常规 → "công thức máu"; 尿常规 → "tổng phân tích nước tiểu"
    B超 → "siêu âm"; CT/MRI/X-quang giữ nguyên
- Đơn vị: mg, ml, kg, mmHg, mmol/L giữ nguyên.

D. CHUYÊN KHOA
    内科 → "nội khoa"; 外科 → "ngoại khoa"; 儿科 → "nhi khoa"
    妇产科 → "sản phụ khoa"; 皮肤科 → "da liễu"
    眼科 → "nhãn khoa"; 耳鼻喉科 → "tai mũi họng"
    心内科 → "tim mạch"; 神经内科 → "nội thần kinh"
    肿瘤科 → "ung bướu"; 急诊 → "cấp cứu"

E. XƯNG HÔ & VAI
- 医生 / 大夫 → "Bác sĩ"; 主任 → "Chủ nhiệm" / "Bác sĩ trưởng"; 专家 → "chuyên gia"
- 病人 → "Bệnh nhân"; xưng hô của BN với BS giữ tự nhiên (cô / bác / anh / chị tùy ngữ cảnh).
- Marker đối thoại: 医生： → "Bác sĩ:"; 病人： → "Bệnh nhân:"; giữ format xuống dòng và dấu hai chấm.

QUY TẮC FORMAT TUYỆT ĐỐI:
1. Giữ nguyên cấu trúc, KHÔNG tóm tắt, KHÔNG bỏ thông tin, KHÔNG bịa thêm.
2. Dịch ĐẦY ĐỦ. Nếu input có "Dialogue\\n医生：\\n..." thì output cũng phải có cấu trúc tương tự bằng tiếng Việt.
3. Giữ ký tự xuống dòng (\\n) đúng vị trí input.
4. Nếu input có lẫn ký tự lạ (无, ?), giữ nguyên hoặc thay bằng "không có" / "không rõ" cho hợp ngữ cảnh.
5. KHÔNG thêm lời mở đầu kiểu "Bản dịch:", "Đây là bản dịch:", KHÔNG thêm lời giải thích cuối.
6. KHÔNG kèm phần tiếng Trung gốc trong output.
7. Trả về DUY NHẤT văn bản tiếng Việt đã dịch.
8. Nếu nội dung input đã hoàn toàn là tiếng Việt, copy nguyên văn không sửa.
9. Văn phong: tự nhiên, dùng thuật ngữ y khoa Việt Nam đúng chuẩn, không Trung-hóa câu chữ (ví dụ KHÔNG viết "tôi nghĩ rằng có lẽ là..." kiểu dịch máy).

KIỂM TRA TRƯỚC KHI TRẢ LỜI:
- Mỗi tên bệnh đã đúng theo từ điển y khoa Việt Nam chưa?
- Mỗi tên thuốc đã đúng INN/phiên âm chuẩn chưa?
- Có còn ký tự Hán nào sót lại không (ngoài 医生：/病人： nếu giữ nguyên)?
- Có thêm lời giải thích thừa không?

Bây giờ dịch đoạn sau:"""


def _post(payload: dict, timeout: int = 90) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{FPT_BASE_URL}/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {FPT_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            # Cloudflare on mkp-api.fptcloud.com blocks default Python urllib UA.
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return json.loads(body)


def translate_text(text: str, label: str = "") -> str:
    """Translate one piece of text. Empty/whitespace input is passed through."""
    if not text or not text.strip():
        return text
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        "temperature": 0.2,
        "top_p": 0.9,
        "max_tokens": 4096,
        "stream": False,
        # Disable Qwen3 "thinking" so the model returns the translation directly.
        # Saves ~25s/request. Both keys are accepted by OpenAI-compatible Qwen routers.
        "enable_thinking": False,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    last_err: Exception | None = None
    for attempt in range(8):
        try:
            data = _post(payload)
            choice = (data.get("choices") or [{}])[0]
            msg = choice.get("message") or {}
            content = msg.get("content") or ""
            # Strip any <think>...</think> blocks if the model still emitted them.
            if "<think>" in content:
                import re as _re
                content = _re.sub(r"<think>.*?</think>", "", content, flags=_re.DOTALL).strip()
            if not content.strip():
                raise RuntimeError(f"empty content from API (label={label})")
            return content.strip()
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="replace")[:500]
            except Exception:
                pass
            last_err = RuntimeError(f"HTTP {e.code}: {body}")
            if e.code in (400, 401, 403):
                # not retryable
                raise last_err
            # 429 / 5xx: longer backoff
            if e.code == 429:
                time.sleep(min(60, 5 + 5 * attempt))
                continue
        except Exception as e:
            last_err = e
        # default backoff: 1s, 2s, 4s, 8s, 16s, 32s, 60s, 60s
        time.sleep(min(60, 2 ** attempt))
    raise last_err  # type: ignore[misc]


def load_progress() -> dict[int, dict]:
    """Read the progress JSONL into {idx: translated_record}."""
    done: dict[int, dict] = {}
    if not PROGRESS_PATH.exists():
        return done
    with PROGRESS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                idx = row.get("idx")
                if isinstance(idx, int):
                    done[idx] = row["record"]
            except Exception:
                continue
    return done


_progress_lock_file = None


def append_progress(idx: int, record: dict) -> None:
    line = json.dumps({"idx": idx, "record": record}, ensure_ascii=False)
    # Atomic append (single line < 4KB block boundary on Windows is fine for ASCII; here we may exceed -> use rename trick? simple append is OK because writes <16KB are typically atomic to the same FD on Windows).
    with PROGRESS_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()
        try:
            os.fsync(f.fileno())
        except Exception:
            pass


def translate_record(idx: int, rec: dict) -> tuple[int, dict]:
    out = dict(rec)
    # The header `instruction` is already Vietnamese -- keep as-is.
    if "input" in rec:
        out["input"] = translate_text(rec.get("input") or "", label=f"#{idx}.input")
    if "output" in rec:
        out["output"] = translate_text(rec.get("output") or "", label=f"#{idx}.output")
    out["translation_model"] = MODEL_ID
    return idx, out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--limit", type=int, default=0, help="Translate only first N (after --start). 0 = all.")
    parser.add_argument("--start", type=int, default=0)
    args = parser.parse_args()

    if not INPUT_PATH.exists():
        print(f"ERROR: input not found: {INPUT_PATH}", file=sys.stderr)
        return 1

    print(f"[load] {INPUT_PATH}")
    items: list[dict] = json.loads(INPUT_PATH.read_text(encoding="utf-8", errors="replace"))
    print(f"[load] {len(items)} records")

    end = len(items) if args.limit <= 0 else min(len(items), args.start + args.limit)
    work_indices = list(range(args.start, end))

    done = load_progress()
    pending = [i for i in work_indices if i not in done]
    print(f"[resume] already done: {len(done)} | pending now: {len(pending)} | range: {args.start}..{end - 1}")

    if not pending:
        print("[done] nothing to translate; writing output")
    else:
        # Quick smoke test on first record for early failure detection.
        first = pending[0]
        try:
            print(f"[smoke] translating idx {first} synchronously to verify API reachable...")
            idx, rec = translate_record(first, items[first])
            append_progress(idx, rec)
            done[idx] = rec
            pending.remove(first)
            print(f"[smoke] OK. sample translated input head: {rec.get('input', '')[:120]!r}")
        except Exception as e:
            print(f"[FATAL] smoke test failed: {e}", file=sys.stderr)
            return 2

        t0 = time.time()
        completed = 0
        total = len(pending)
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futures = {pool.submit(translate_record, i, items[i]): i for i in pending}
            for fut in as_completed(futures):
                i = futures[fut]
                try:
                    idx, rec = fut.result()
                    append_progress(idx, rec)
                    done[idx] = rec
                    completed += 1
                    elapsed = time.time() - t0
                    rate = completed / max(elapsed, 0.01)
                    eta = (total - completed) / max(rate, 0.001)
                    print(
                        f"[ok] {completed:4d}/{total} (idx={idx:4d}) "
                        f"rate={rate:.2f}/s ETA={eta/60:.1f}m",
                        flush=True,
                    )
                except Exception as e:
                    print(f"[ERR] idx={i}: {e}", file=sys.stderr, flush=True)
                    # leave it pending; rerun will retry
        if any(i not in done for i in work_indices):
            print("[warn] some indices still pending; rerun the script to continue", file=sys.stderr)

    # Stitch final output preserving original order (only the indices we processed are in done).
    print(f"[stitch] writing final output: {OUTPUT_PATH}")
    final = []
    for i, rec in enumerate(items):
        if i in done:
            final.append(done[i])
        else:
            final.append(rec)  # untouched (only relevant when --limit/--start used)
    OUTPUT_PATH.write_text(
        json.dumps(final, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[done] wrote {len(final)} records to {OUTPUT_PATH}")
    print(f"[note] progress file kept at {PROGRESS_PATH} (delete to start fresh)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
