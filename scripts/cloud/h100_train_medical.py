#!/usr/bin/env python3
"""
MediSign Medical Adapter — H100 One-shot Training Script
=========================================================

Self-contained Python script — không cần clone repo, không cần notebook.
Bash wrapper (h100_train_medical.sh) sẽ:
  1. Cài deps + Flash Attention 2
  2. Download script này
  3. Chạy: HF_TOKEN=xxx python3 h100_train_medical.py

Script tự động:
  - Pull dataset từ HuggingFace
  - Train MedGemma 4B Medical Adapter (QLoRA + Flash-Attn 2)
  - Smoke test inference
  - Push adapter lên HuggingFace
  - Lưu zip backup

ETA: ~1-1.5h trên H100 80GB.
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
BASE_MODEL_ID   = "google/medgemma-1.5-4b-it"
ADAPTER_REPO_ID = os.environ.get("ADAPTER_REPO_ID", "thuaannn/medisign-medgemma4b-adapter")
DATA_REPO_ID    = os.environ.get("DATA_REPO_ID", "thuaannn/medisign-training-data")

# Paths
APP_DIR        = Path(os.environ.get("APP_DIR", str(Path.home() / "medisign")))
DATA_DIR       = APP_DIR / "data"
TRAIN_FILE     = DATA_DIR / "medical_train.jsonl"
EVAL_FILE      = DATA_DIR / "medical_eval.jsonl"
OUTPUT_DIR     = APP_DIR / "output"
CHECKPOINT_DIR = OUTPUT_DIR / "checkpoints"
ADAPTER_DIR    = OUTPUT_DIR / "adapter"
ZIP_DIR        = OUTPUT_DIR / "zips"

# Training hyperparams (auto-tuned cho H100 80GB)
NUM_EPOCHS    = int(os.environ.get("NUM_EPOCHS", "3"))
LEARNING_RATE = float(os.environ.get("LEARNING_RATE", "2e-4"))
MAX_SEQ_LEN   = int(os.environ.get("MAX_SEQ_LEN", "2048"))
LORA_R        = int(os.environ.get("LORA_R", "16"))
LORA_ALPHA    = int(os.environ.get("LORA_ALPHA", "32"))
LORA_DROPOUT  = 0.05
LOGGING_STEPS = 20
SAVE_STEPS    = 200
EVAL_STEPS    = 200
SEED          = 42

# ═══════════════════════════════════════════════════════════════════
#                         SETUP
# ═══════════════════════════════════════════════════════════════════

for d in [DATA_DIR, CHECKPOINT_DIR, ADAPTER_DIR, ZIP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

os.environ["HF_TOKEN"]               = HF_TOKEN
os.environ["HUGGING_FACE_HUB_TOKEN"] = HF_TOKEN
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import torch  # noqa: E402

if not torch.cuda.is_available():
    print("❌ CUDA không available", flush=True)
    sys.exit(1)

VRAM_GB = torch.cuda.get_device_properties(0).total_memory / 1024**3
GPU_NAME = torch.cuda.get_device_name(0)

USE_BF16 = torch.cuda.is_bf16_supported()
USE_TF32 = True

# Detect Flash Attention 2 availability FIRST (used in batch tuning below)
try:
    import flash_attn  # noqa: F401
    ATTN_IMPL = "flash_attention_2"
    FLASH_VER = flash_attn.__version__
except ImportError:
    ATTN_IMPL = "sdpa"
    FLASH_VER = None

# Auto-tune batch size theo VRAM + attention impl
# SDPA tốn O(n²) memory cho attention → cần batch nhỏ + grad checkpoint + no packing
# Flash-Attn 2 efficient → batch lớn + packing OK
if VRAM_GB >= 70:
    if ATTN_IMPL == "flash_attention_2":
        BATCH_SIZE, GRAD_ACCUM = 32, 1
        GRAD_CHECKPOINT = False
        USE_PACKING = True
    else:  # SDPA fallback
        BATCH_SIZE, GRAD_ACCUM = 4, 8
        GRAD_CHECKPOINT = True
        USE_PACKING = False
elif VRAM_GB >= 40:
    BATCH_SIZE, GRAD_ACCUM = 4, 8
    GRAD_CHECKPOINT = True
    USE_PACKING = ATTN_IMPL == "flash_attention_2"
elif VRAM_GB >= 20:
    BATCH_SIZE, GRAD_ACCUM = 2, 16
    GRAD_CHECKPOINT = True
    USE_PACKING = False
else:
    BATCH_SIZE, GRAD_ACCUM = 1, 32
    GRAD_CHECKPOINT = True
    USE_PACKING = False

torch.backends.cuda.matmul.allow_tf32 = USE_TF32
torch.backends.cudnn.allow_tf32       = USE_TF32

# ═══════════════════════════════════════════════════════════════════
#                         BANNER
# ═══════════════════════════════════════════════════════════════════

print("\n" + "═" * 70)
print("  MediSign Medical Adapter — H100 Training")
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
print(f"  Epochs         : {NUM_EPOCHS}")
print(f"  Max seq len    : {MAX_SEQ_LEN}")
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
    print(f"→ Vào https://huggingface.co/{BASE_MODEL_ID} accept terms trước", flush=True)
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════
#                   STEP 2 — PULL DATASET
# ═══════════════════════════════════════════════════════════════════

print("─── STEP 2/6 — Pull dataset ───", flush=True)
print(f"From: {DATA_REPO_ID}", flush=True)

snapshot_download(
    repo_id=DATA_REPO_ID,
    repo_type="dataset",
    local_dir=str(DATA_DIR),
    allow_patterns=["medical_train.jsonl", "medical_eval.jsonl"],
)

for fname, fpath in [("train", TRAIN_FILE), ("eval", EVAL_FILE)]:
    if not fpath.exists():
        print(f"❌ {fpath} không tồn tại", flush=True)
        sys.exit(1)
    n = sum(1 for _ in fpath.open(encoding="utf-8"))
    size_mb = fpath.stat().st_size / 1024 / 1024
    print(f"  {fname:>5}: {n:,} records ({size_mb:.1f} MB)", flush=True)

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
print(f"  Gradient checkpointing: {GRAD_CHECKPOINT}", flush=True)

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
    warmup_ratio=0.03,
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
    save_total_limit=3,
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

    def on_train_begin(self, args, state, control, **kw):
        self._t0 = time.time()
        print(f"\n{'═' * 60}", flush=True)
        print(f"  TRAINING STARTED — {state.max_steps:,} steps", flush=True)
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
               f"loss={loss} | {spd:.3f} step/s | ETA {eta_s}")
        if "eval_loss" in logs:
            msg += f" | eval={logs['eval_loss']:.4f}"
        print(msg, flush=True)

    def on_save(self, args, state, control, **kw):
        print(f"  💾 checkpoint at step {state.global_step}", flush=True)

    def on_train_end(self, args, state, control, **kw):
        elapsed = time.time() - self._t0
        print(f"\n{'═' * 60}", flush=True)
        print(f"  DONE — {elapsed / 3600:.2f}h ({elapsed / 60:.0f} min)", flush=True)
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

cfg_path = ADAPTER_DIR / "adapter_config.json"
if cfg_path.exists():
    cfg = json.loads(cfg_path.read_text())
    print(f"LoRA config: r={cfg.get('r')}, alpha={cfg.get('lora_alpha')}\n", flush=True)

# ═══════════════════════════════════════════════════════════════════
#                   STEP 5 — SMOKE TEST
# ═══════════════════════════════════════════════════════════════════

print("─── STEP 5/6 — Smoke test inference ───", flush=True)

# Free VRAM
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

test_prompts = [
    "Triệu chứng của bệnh tiểu đường type 2 là gì?",
    "Tôi bị đau đầu, sốt nhẹ 2 ngày. Có nên đi khám không?",
    "Paracetamol có tác dụng gì và liều dùng cho người lớn?",
]
for prompt in test_prompts:
    messages = [{"role": "user", "content": prompt}]
    input_ids = tok.apply_chat_template(
        messages,
        return_tensors="pt",
        add_generation_prompt=True,
    ).to(m.device)
    with torch.no_grad():
        out = m.generate(
            input_ids=input_ids,
            max_new_tokens=200,
            do_sample=False,
            pad_token_id=tok.pad_token_id,
        )
    resp = tok.decode(out[0][input_ids.shape[1]:], skip_special_tokens=True)
    print(f"\n{'━' * 60}", flush=True)
    print(f"Q: {prompt}", flush=True)
    print(f"A: {resp.strip()}", flush=True)

del m, base
gc.collect()
torch.cuda.empty_cache()
print("\n✅ Smoke test passed\n", flush=True)

# ═══════════════════════════════════════════════════════════════════
#                   STEP 6 — ZIP + PUSH HF
# ═══════════════════════════════════════════════════════════════════

print("─── STEP 6/6 — Zip + Push HuggingFace ───", flush=True)

zip_path = ZIP_DIR / "medisign-medgemma4b-adapter.zip"
zip_ok = False
try:
    print(f"Đóng gói → {zip_path}", flush=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(ADAPTER_DIR.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(ADAPTER_DIR))
    size_mb = zip_path.stat().st_size / 1024**2
    print(f"  ✅ Zip saved: {zip_path}  ({size_mb:.1f} MB)", flush=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        bad = zf.testzip()
        if bad:
            raise zipfile.BadZipFile(f"Corrupt: {bad}")
    print(f"  ✅ Zip integrity OK — {len(zf.namelist())} files", flush=True)
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
        commit_message=(f"medical adapter | bf16+{ATTN_IMPL} | "
                        f"lora_r={LORA_R} | {NUM_EPOCHS} epochs | H100"),
        token=HF_TOKEN,
    )
    print(f"  ✅ HF push OK", flush=True)
    hf_ok = True
except Exception as e:
    print(f"  ⚠️  HF push failed: {e}", flush=True)

# ═══════════════════════════════════════════════════════════════════
#                         FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════════

print("\n" + "═" * 70, flush=True)
print("  TRAINING SUMMARY", flush=True)
print("═" * 70, flush=True)
print(f"  Adapter dir : {ADAPTER_DIR}", flush=True)
print(f"  Zip backup  : {'✅ ' + str(zip_path) if zip_ok else '❌ failed'}", flush=True)
print(f"  HuggingFace : {'✅ https://huggingface.co/' + ADAPTER_REPO_ID if hf_ok else '❌ failed'}", flush=True)
print("═" * 70, flush=True)

if not zip_ok and not hf_ok:
    print("\n❌ Cả 2 backup methods đều fail — adapter vẫn ở local", flush=True)
    sys.exit(1)

print("\n🎉 ALL DONE — bạn có thể destroy VM ngay bây giờ.\n", flush=True)
