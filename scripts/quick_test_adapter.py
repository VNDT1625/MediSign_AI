"""Quick smoke test: load 1 adapter + run 1 prompt.

Test trên CPU/GPU bất kỳ. Không serve server, chỉ verify adapter hoạt động.
"""
import os
import sys
import time
import torch
from pathlib import Path

HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()
if not HF_TOKEN:
    print("[ERROR] Set HF_TOKEN trước:")
    print("  set HF_TOKEN=hf_xxxxx")
    sys.exit(1)

ADAPTER = sys.argv[1] if len(sys.argv) > 1 else "medical"
ADAPTER_MAP = {
    "medical":    "thuaannn/medisign-medgemma4b-adapter",
    "psychology": "thuaannn/medisign-medgemma4b-psychology",
}
adapter_id = ADAPTER_MAP.get(ADAPTER)
if not adapter_id:
    print(f"[ERROR] Unknown adapter '{ADAPTER}'. Use 'medical' or 'psychology'.")
    sys.exit(1)

BASE = "google/medgemma-1.5-4b-it"

print("=" * 60)
print(f"  Quick Adapter Test — {ADAPTER}")
print("=" * 60)
print(f"  Base    : {BASE}")
print(f"  Adapter : {adapter_id}")
print(f"  CUDA    : {torch.cuda.is_available()}")
if torch.cuda.is_available():
    vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f"  GPU     : {torch.cuda.get_device_name(0)} ({vram:.1f}GB)")
    if vram < 5:
        print(f"  ⚠️  VRAM quá ít, sẽ offload xuống CPU/disk → CỰC chậm")
print("=" * 60)

print("\n[1/3] Loading tokenizer...", flush=True)
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

tok = AutoTokenizer.from_pretrained(BASE, token=HF_TOKEN)
if tok.pad_token is None:
    tok.pad_token = tok.eos_token

print("[2/3] Loading base model + adapter (chạy lần đầu sẽ download ~6GB) ...",
      flush=True)
t0 = time.time()

if torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory > 5 * 1024**3:
    bnb = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    base = AutoModelForCausalLM.from_pretrained(
        BASE, quantization_config=bnb, device_map="auto",
        dtype=torch.bfloat16, token=HF_TOKEN,
    )
else:
    print("  → CPU mode (sẽ chậm)")
    base = AutoModelForCausalLM.from_pretrained(
        BASE, dtype=torch.float32, token=HF_TOKEN,
    )

m = PeftModel.from_pretrained(base, adapter_id, token=HF_TOKEN)
m.eval()
print(f"  Loaded in {time.time()-t0:.1f}s\n", flush=True)

print("[3/3] Running test prompts ...\n", flush=True)

if ADAPTER == "medical":
    prompts = [
        "Triệu chứng tiểu đường type 2 là gì?",
        "Tôi bị đau đầu, sốt nhẹ 2 ngày, có nên đi khám không?",
    ]
else:
    prompts = [
        "Em bị áp lực thi cử, mất ngủ mấy hôm nay.",
        "Tôi 35 tuổi, đi làm về thấy trống rỗng, không muốn làm gì.",
    ]

for i, prompt in enumerate(prompts, 1):
    print(f"━━━━ Prompt {i}/{len(prompts)} ━━━━")
    print(f"USER: {prompt}")

    msgs = [{"role": "user", "content": prompt}]
    input_ids = tok.apply_chat_template(
        msgs, return_tensors="pt", add_generation_prompt=True,
    ).to(m.device)

    t1 = time.time()
    with torch.no_grad():
        out = m.generate(
            input_ids=input_ids, max_new_tokens=200,
            do_sample=True, temperature=0.7, top_p=0.95,
            pad_token_id=tok.pad_token_id,
        )
    elapsed = time.time() - t1

    resp = tok.decode(out[0][input_ids.shape[1]:], skip_special_tokens=True)
    print(f"AI  : {resp.strip()}")
    print(f"      ({elapsed:.1f}s, {(out.shape[1]-input_ids.shape[1])/elapsed:.1f} tok/s)\n")

print("✅ DONE")
