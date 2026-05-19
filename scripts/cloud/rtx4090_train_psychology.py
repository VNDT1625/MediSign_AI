#!/usr/bin/env python3
"""
MediSign Psychology Adapter — RTX 4090 / Ada Lovelace Training Script
=====================================================================

Self-contained Python script. Bash wrapper (rtx4090_train_psychology.sh) sẽ:
  1. Cài deps + Flash Attention 2 (pre-built wheel cho Ada Lovelace)
  2. Download script này
  3. Chạy: HF_TOKEN=xxx python3 rtx4090_train_psychology.py

Khác biệt với medical adapter:
  - Dataset nhỏ hơn (~1500 samples vs 15K) → ETA ngắn hơn
  - Dùng base model có sẵn medical adapter (continual fine-tune) HOẶC base MedGemma trực tiếp
  - LoRA r=8 (nhỏ hơn) vì dataset ít, tránh overfit
  - Eval thường xuyên hơn (50 steps) vì training ngắn

ETA: ~1.5-2.5h trên RTX 4090 24GB (depending on flash-attn).
"""

from __future__ import annotations

import os
import sys
import time
import gc
import json
import zipfile
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════
#                         CONFIG
# ═══════════════════════════════════════════════════════════════════

HF_TOKEN = os.environ.get("HF_TOKEN", "")
if not HF_TOKEN:
    print("❌ HF_TOKEN không set. Chạy: export HF_TOKEN='hf_...'", flush=True)
    sys.exit(1)

# Model & repos
BASE_MODEL_ID    = "google/medgemma-1.5-4b-it"
ADAPTER_REPO_ID  = os.environ.get("ADAPTER_REPO_ID", "thuaannn/medisign-medgemma4b-psychology")
DATA_REPO_ID     = os.environ.get("DATA_REPO_ID", "thuaannn/medisign-training-data")

# Optional: stack on top of medical adapter (if MERGE_MEDICAL=1)
MERGE_MEDICAL       = os.environ.get("MERGE_MEDICAL", "0") == "1"
MEDICAL_ADAPTER_ID  = os.environ.get("MEDICAL_ADAPTER_ID", "thuaannn/medisign-medgemma4b-adapter")

# Paths
APP_DIR        = Path(os.environ.get("APP_DIR", str(Path.home() / "medisign")))
DATA_DIR       = APP_DIR / "data"
TRAIN_FILE     = DATA_DIR / "psychology_train.jsonl"
EVAL_FILE      = DATA_DIR / "psychology_eval.jsonl"
OUTPUT_DIR     = APP_DIR / "output_psych"
CHECKPOINT_DIR = OUTPUT_DIR / "checkpoints"
ADAPTER_DIR    = OUTPUT_DIR / "adapter"
ZIP_DIR        = OUTPUT_DIR / "zips"

# Training hyperparams (tuned cho dataset ~1500 samples)
NUM_EPOCHS    = int(os.environ.get("NUM_EPOCHS", "4"))   # data ít → train nhiều epoch hơn
LEARNING_RATE = float(os.environ.get("LEARNING_RATE", "1e-4"))  # nhỏ hơn medical (2e-4) để tránh overfit
MAX_SEQ_LEN   = int(os.environ.get("MAX_SEQ_LEN", "1024"))  # OARS turns ngắn → 1024 đủ
LORA_R        = int(os.environ.get("LORA_R", "8"))   # nhỏ hơn medical (16) vì data ít
LORA_ALPHA    = int(os.environ.get("LORA_ALPHA", "16"))
LORA_DROPOUT  = 0.1   # cao hơn medical (0.05) → regularize stronger
LOGGING_STEPS = 10
SAVE_STEPS    = 100
EVAL_STEPS    = 50    # eval thường xuyên hơn medical (200)
SEED          = 42

# ═══════════════════════════════════════════════════════════════════
#                         SETUP
# ═══════════════════════════════════════════════════════════════════

for d in [DATA_DIR, CHECKPOINT_DIR, ADAPTER_DIR, ZIP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

os.environ["HF_TOKEN"]                = HF_TOKEN
os.environ["HUGGING_FACE_HUB_TOKEN"]  = HF_TOKEN
os.environ["TOKENIZERS_PARALLELISM"]  = "false"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import torch  # noqa: E402

if not torch.cuda.is_available():
    print("❌ CUDA không available", flush=True)
    sys.exit(1)

VRAM_GB  = torch.cuda.get_device_properties(0).total_memory / 1024**3
GPU_NAME = torch.cuda.get_device_name(0)

USE_BF16 = torch.cuda.is_bf16_supported()
USE_TF32 = True

# Detect Flash Attention 2 (must be BEFORE batch tuning!)
try:
    import flash_attn  # noqa: F401
    ATTN_IMPL = "flash_attention_2"
    FLASH_VER = flash_attn.__version__
except ImportError:
    ATTN_IMPL = "sdpa"
    FLASH_VER = None

# Auto-tune batch theo VRAM + attention
# RTX 4090: 24GB, Ada Lovelace
if VRAM_GB >= 70:        # H100 80GB
    BATCH_SIZE, GRAD_ACCUM = (16, 2) if ATTN_IMPL == "flash_attention_2" else (4, 8)
    GRAD_CHECKPOINT = ATTN_IMPL != "flash_attention_2"
    USE_PACKING     = ATTN_IMPL == "flash_attention_2"
elif VRAM_GB >= 40:      # A100 40GB
    BATCH_SIZE, GRAD_ACCUM = (8, 4) if ATTN_IMPL == "flash_attention_2" else (4, 8)
    GRAD_CHECKPOINT = True
    USE_PACKING     = ATTN_IMPL == "flash_attention_2"
elif VRAM_GB >= 22:      # RTX 4090 24GB / A6000
    BATCH_SIZE, GRAD_ACCUM = (4, 8) if ATTN_IMPL == "flash_attention_2" else (2, 16)
    GRAD_CHECKPOINT = True
    USE_PACKING     = ATTN_IMPL == "flash_attention_2"
elif VRAM_GB >= 14:      # RTX 5070 Ti 16GB / 4070 Ti
    BATCH_SIZE, GRAD_ACCUM = (2, 16)
    GRAD_CHECKPOINT = True
    USE_PACKING     = False   # SDPA on Blackwell
else:                    # T4 16GB or smaller
    BATCH_SIZE, GRAD_ACCUM = (1, 32)
    GRAD_CHECKPOINT = True
    USE_PACKING     = False

torch.backends.cuda.matmul.allow_tf32 = USE_TF32
torch.backends.cudnn.allow_tf32       = USE_TF32

# ═══════════════════════════════════════════════════════════════════
#                         BANNER
# ═══════════════════════════════════════════════════════════════════

print("\n" + "═" * 70)
print("  MediSign Psychology Adapter — Training")
print("═" * 70)
print(f"  GPU            : {GPU_NAME}")
print(f"  VRAM           : {VRAM_GB:.1f} GB")
print(f"  BF16           : {USE_BF16}")
print(f"  Attention      : {ATTN_IMPL}" + (f" (v{FLASH_VER})" if FLASH_VER else ""))
print(f"  Batch size     : {BATCH_SIZE}")
print(f"  Grad accum     : {GRAD_ACCUM}  (effective batch = {BATCH_SIZE * GRAD_ACCUM})")
print(f"  Grad checkpoint: {GRAD_CHECKPOINT}")
print(f"  Packing        : {USE_PACKING}")
print(f"  LoRA r/alpha   : {LORA_R}/{LORA_ALPHA}")
print(f"  LoRA dropout   : {LORA_DROPOUT}")
print(f"  Epochs         : {NUM_EPOCHS}")
print(f"  Max seq len    : {MAX_SEQ_LEN}")
print(f"  Learning rate  : {LEARNING_RATE}")
print(f"  Merge medical  : {MERGE_MEDICAL}")
print(f"  Adapter repo   : {ADAPTER_REPO_ID}")
print(f"  App dir        : {APP_DIR}")
print("═" * 70 + "\n", flush=True)

# ═══════════════════════════════════════════════════════════════════
#                   STEP 1 — LOGIN HUGGINGFACE
# ═══════════════════════════════════════════════════════════════════

print("─── STEP 1/6 — Login HuggingFace ───", flush=True)
from huggingface_hub import login, whoami, model_info, snapshot_download, HfApi, upload_folder

login(token=HF_TOKEN, add_to_git_credential=False)
user = whoami(token=HF_TOKEN)
print(f"✅ Logged in as: {user['name']}", flush=True)

try:
    model_info(BASE_MODEL_ID, token=HF_TOKEN)
    print(f"✅ Base model accessible: {BASE_MODEL_ID}\n", flush=True)
except Exception as e:
    print(f"❌ Cannot access {BASE_MODEL_ID}: {e}", flush=True)
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════
#                   STEP 2 — PULL DATASET
# ═══════════════════════════════════════════════════════════════════

print("─── STEP 2/6 — Pull psychology dataset ───", flush=True)
print(f"From: {DATA_REPO_ID}", flush=True)

snapshot_download(
    repo_id=DATA_REPO_ID,
    repo_type="dataset",
    local_dir=str(DATA_DIR),
    allow_patterns=["psychology_train.jsonl", "psychology_eval.jsonl"],
)

for fname, fpath in [("train", TRAIN_FILE), ("eval", EVAL_FILE)]:
    if not fpath.exists():
        print(f"❌ {fpath} không tồn tại", flush=True)
        sys.exit(1)
    n = sum(1 for _ in fpath.open(encoding="utf-8"))
    size_kb = fpath.stat().st_size / 1024
    print(f"  {fname:>5}: {n:,} records ({size_kb:.0f} KB)", flush=True)

# Sanity check — psychology data should NOT be tiny templates
n_train = sum(1 for _ in TRAIN_FILE.open(encoding="utf-8"))
if n_train < 500:
    print(f"⚠️  Train set có {n_train} samples — có thể chưa regenerate xong.", flush=True)
    print(f"   Dừng lại nếu data chưa sẵn sàng. Continuing in 10s...", flush=True)
    time.sleep(10)

print()

# ═══════════════════════════════════════════════════════════════════
#                   STEP 3 — TRAINING
# ═══════════════════════════════════════════════════════════════════

print("─── STEP 3/6 — Training ───", flush=True)
t0 = time.time()

from transformers import (
    AutoModelForCausalLM, AutoTokenizer,
    BitsAndBytesConfig, set_seed, TrainerCallback,
)
from peft import LoraConfig, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset

set_seed(SEED)

print("[1/4] Loading datasets...", flush=True)
ds = load_dataset(
    "json",
    data_files={"train": str(TRAIN_FILE), "eval": str(EVAL_FILE)},
)
print(f"  train: {len(ds['train']):,}  |  eval: {len(ds['eval']):,}", flush=True)

print("\n[2/4] Loading tokenizer...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID, use_fast=True, token=HF_TOKEN)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print(f"\n[3/4] Loading base model (4-bit NF4 + {ATTN_IMPL})...", flush=True)
bnb = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16 if USE_BF16 else torch.float16,
    bnb_4bit_use_double_quant=True,
)
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID,
    quantization_config=bnb,
    device_map="auto",
    dtype=torch.bfloat16 if USE_BF16 else torch.float16,
    attn_implementation=ATTN_IMPL,
    token=HF_TOKEN,
)
model.config.use_cache = False
model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=GRAD_CHECKPOINT)
print(f"  Model loaded. VRAM used: {torch.cuda.memory_allocated()/1024**3:.2f} GB", flush=True)

# Optional: merge medical adapter first (continual fine-tune)
if MERGE_MEDICAL:
    print(f"\n[3.5] Loading medical adapter as starting point: {MEDICAL_ADAPTER_ID}", flush=True)
    from peft import PeftModel
    model = PeftModel.from_pretrained(model, MEDICAL_ADAPTER_ID, is_trainable=False, token=HF_TOKEN)
    model = model.merge_and_unload()
    print(f"  Medical adapter merged. VRAM: {torch.cuda.memory_allocated()/1024**3:.2f} GB", flush=True)

lora_config = LoraConfig(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    bias="none",
    task_type="CAUSAL_LM",
)

training_args = SFTConfig(
    output_dir=str(CHECKPOINT_DIR),
    num_train_epochs=NUM_EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUM,
    gradient_checkpointing=GRAD_CHECKPOINT,
    gradient_checkpointing_kwargs={"use_reentrant": False} if GRAD_CHECKPOINT else None,
    learning_rate=LEARNING_RATE,
    warmup_ratio=0.05,        # warmup dài hơn medical (0.03) cho training ngắn
    lr_scheduler_type="cosine",
    optim="paged_adamw_8bit",
    weight_decay=0.01,
    neftune_noise_alpha=5,
    bf16=USE_BF16,
    fp16=not USE_BF16,
    tf32=USE_TF32,
    logging_steps=LOGGING_STEPS,
    logging_first_step=True,
    save_steps=SAVE_STEPS,
    save_strategy="steps",
    save_total_limit=2,
    eval_steps=EVAL_STEPS,
    eval_strategy="steps",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    report_to="none",
    seed=SEED,
    dataloader_pin_memory=False,
    max_length=MAX_SEQ_LEN,
    dataset_text_field="text",
    packing=USE_PACKING,
)


class ProgressLogger(TrainerCallback):
    def __init__(self):
        self._t0 = None
        self._best_eval = float("inf")

    def on_train_begin(self, args, state, control, **kw):
        self._t0 = time.time()
        print(f"\n{'═' * 60}", flush=True)
        print(f"  PSYCHOLOGY TRAINING — {state.max_steps:,} steps", flush=True)
        print(f"{'═' * 60}\n", flush=True)

    def on_log(self, args, state, control, logs=None, **kw):
        if not logs or not self._t0:
            return
        step = state.global_step
        total = state.max_steps or 1
        elapsed = time.time() - self._t0
        eta = (elapsed / max(step, 1)) * (total - step)
        eta_s = f"{int(eta // 3600)}h{int((eta % 3600) // 60):02d}m"
        loss = logs.get("loss", logs.get("train_loss", "?"))
        spd = step / elapsed if elapsed > 0 else 0
        msg = (f"[{step / total * 100:5.1f}%] step {step:>5}/{total} | "
               f"loss={loss} | {spd:.2f} step/s | ETA {eta_s}")
        if "eval_loss" in logs:
            ev = logs["eval_loss"]
            star = " ★" if ev < self._best_eval else ""
            self._best_eval = min(self._best_eval, ev)
            msg += f" | eval={ev:.4f}{star}"
        print(msg, flush=True)

    def on_save(self, args, state, control, **kw):
        print(f"  💾 checkpoint at step {state.global_step}", flush=True)

    def on_train_end(self, args, state, control, **kw):
        elapsed = time.time() - self._t0
        print(f"\n{'═' * 60}", flush=True)
        print(f"  DONE — {elapsed / 3600:.2f}h ({elapsed / 60:.0f} min)", flush=True)
        print(f"  Best eval loss: {self._best_eval:.4f}", flush=True)
        print(f"{'═' * 60}\n", flush=True)


print("\n[4/4] Training...", flush=True)
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=ds["train"],
    eval_dataset=ds["eval"],
    peft_config=lora_config,
    processing_class=tokenizer,
    callbacks=[ProgressLogger()],
)
trainer.train()

print(f"\n💾 Saving adapter → {ADAPTER_DIR}", flush=True)
trainer.model.save_pretrained(str(ADAPTER_DIR))
tokenizer.save_pretrained(str(ADAPTER_DIR))
print(f"⏱  Training time: {(time.time() - t0) / 3600:.2f}h\n", flush=True)

# ═══════════════════════════════════════════════════════════════════
#                   STEP 4 — VERIFY ADAPTER
# ═══════════════════════════════════════════════════════════════════

print("─── STEP 4/6 — Verify adapter ───", flush=True)
total_mb = 0
for f in sorted(ADAPTER_DIR.iterdir()):
    if f.is_file():
        mb = f.stat().st_size / 1024**2
        total_mb += mb
        print(f"  {f.name:<42} {mb:>7.1f} MB", flush=True)
print(f"  {'TOTAL':<42} {total_mb:>7.1f} MB\n", flush=True)

# ═══════════════════════════════════════════════════════════════════
#                   STEP 5 — SMOKE TEST (OARS scenarios)
# ═══════════════════════════════════════════════════════════════════

print("─── STEP 5/6 — Smoke test inference ───", flush=True)

del trainer, model
gc.collect()
torch.cuda.empty_cache()
print(f"VRAM freed. Now: {torch.cuda.memory_allocated() / 1024**3:.2f} GB", flush=True)

from peft import PeftModel

bnb_test = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16 if USE_BF16 else torch.float16,
    bnb_4bit_use_double_quant=True,
)
tok = AutoTokenizer.from_pretrained(BASE_MODEL_ID, token=HF_TOKEN)
if tok.pad_token is None:
    tok.pad_token = tok.eos_token

print("Loading base + adapter ...", flush=True)
base = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID,
    token=HF_TOKEN,
    quantization_config=bnb_test,
    dtype=torch.bfloat16 if USE_BF16 else torch.float16,
    attn_implementation=ATTN_IMPL,
    device_map="auto",
)
m = PeftModel.from_pretrained(base, str(ADAPTER_DIR))
m.eval()
print(f"VRAM after load: {torch.cuda.memory_allocated() / 1024**3:.2f} GB\n", flush=True)

CHAT_SYSTEM = (
    "Bạn là MediSign AI, trợ lý y tế tiếng Việt. "
    "Bạn lắng nghe và hỏi thêm theo phương pháp OARS để hiểu rõ tình trạng người dùng "
    "trước khi đưa ra bất kỳ gợi ý nào."
)

test_prompts = [
    "Dạo này em hay mất ngủ và nghĩ về việc thi đại học sắp tới.",
    "Em mới chia tay người yêu, em không biết làm gì cả.",
    "Tôi 35 tuổi, đi làm về cảm thấy trống rỗng, không muốn làm gì.",
]
for prompt in test_prompts:
    messages = [
        {"role": "user", "content": f"{CHAT_SYSTEM}\n\n{prompt}"},
    ]
    inputs = tok.apply_chat_template(
        messages,
        return_tensors="pt",
        add_generation_prompt=True,
    ).to(m.device)
    with torch.no_grad():
        out = m.generate(
            inputs,
            max_new_tokens=200,
            do_sample=True,
            temperature=0.7,
            top_p=0.95,
            pad_token_id=tok.pad_token_id,
        )
    resp = tok.decode(out[0][inputs.shape[1]:], skip_special_tokens=True)
    print(f"\n{'━' * 60}", flush=True)
    print(f"USER: {prompt}", flush=True)
    print(f"AI  : {resp.strip()}", flush=True)

del m, base
gc.collect()
torch.cuda.empty_cache()
print("\n✅ Smoke test passed\n", flush=True)

# ═══════════════════════════════════════════════════════════════════
#                   STEP 6 — ZIP + PUSH HF
# ═══════════════════════════════════════════════════════════════════

print("─── STEP 6/6 — Zip + Push HuggingFace ───", flush=True)

zip_path = ZIP_DIR / "medisign-medgemma4b-psychology.zip"
zip_ok = False
try:
    print(f"Đóng gói → {zip_path}", flush=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(ADAPTER_DIR.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(ADAPTER_DIR))
    size_mb = zip_path.stat().st_size / 1024**2
    print(f"  ✅ Zip saved: {zip_path}  ({size_mb:.1f} MB)", flush=True)
    zip_ok = True
except Exception as e:
    print(f"  ⚠️  Zip failed: {e}", flush=True)

print(f"\nPushing → https://huggingface.co/{ADAPTER_REPO_ID} ...", flush=True)
hf_ok = False
try:
    api = HfApi(token=HF_TOKEN)
    api.create_repo(repo_id=ADAPTER_REPO_ID, exist_ok=True, private=False)
    upload_folder(
        folder_path=str(ADAPTER_DIR),
        repo_id=ADAPTER_REPO_ID,
        commit_message=(f"psychology adapter | {ATTN_IMPL} | "
                        f"lora_r={LORA_R} | {NUM_EPOCHS} epochs | "
                        f"medical_merged={MERGE_MEDICAL}"),
        token=HF_TOKEN,
    )
    print(f"  ✅ HF push OK", flush=True)
    hf_ok = True
except Exception as e:
    print(f"  ⚠️  HF push failed: {e}", flush=True)

print("\n" + "═" * 70, flush=True)
print("  PSYCHOLOGY ADAPTER — TRAINING SUMMARY", flush=True)
print("═" * 70, flush=True)
print(f"  Adapter dir : {ADAPTER_DIR}", flush=True)
print(f"  Zip backup  : {'✅ ' + str(zip_path) if zip_ok else '❌ failed'}", flush=True)
print(f"  HuggingFace : {'✅ https://huggingface.co/' + ADAPTER_REPO_ID if hf_ok else '❌ failed'}", flush=True)
print("═" * 70, flush=True)

if not zip_ok and not hf_ok:
    print("\n❌ Cả 2 backup methods đều fail — adapter vẫn ở local", flush=True)
    sys.exit(1)

print("\n🎉 ALL DONE — destroy VM ngay để dừng tính tiền.\n", flush=True)
