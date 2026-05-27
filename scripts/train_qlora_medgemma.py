"""
Task 1.5 — Configure & launch QLoRA fine-tuning for MedGemma 4B.

This script is the production entry point for training the Vietnamese
Medical Adapter on top of `google/medgemma-1.5-4b-it`. It is designed to
run unmodified on:

* Kaggle (free 2× T4 — 16 GB each)
* Vast.ai / RunPod (RTX 4090, 24 GB)
* Any local Linux / Windows machine with a recent NVIDIA GPU

> **Hugging Face access note**
>
> `google/medgemma-1.5-4b-it` is a gated model. Before running this
> script you must accept the MedGemma terms on
> <https://huggingface.co/google/medgemma-1.5-4b-it> and authenticate
> the host machine with `huggingface-cli login`.

Mapping to the spec
-------------------
* 1.5.1 Load MedGemma 4B with 4-bit NF4 quantization (bitsandbytes).
* 1.5.2 QLoRA: r=32, alpha=64, dropout=0.05,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"].
* 1.5.3 SFTTrainer with TrainingArguments / SFTConfig:
        max_seq_length=2048, num_train_epochs=3,
        per_device_train_batch_size=4, gradient_accumulation_steps=4,
        logging_steps=50, save_steps=500.
* 1.6.x Save adapter to `output/medisign_medgemma4b/adapter/`,
        then verify the final artifact size before release. Targeting
        attention + MLP projections improves adaptation quality but
        produces a larger adapter than attention-only QLoRA.

Usage
-----
    python scripts/train_qlora_medgemma.py

    # Smoke run (no real training):
    python scripts/train_qlora_medgemma.py --max_steps 5

    # Resume:
    python scripts/train_qlora_medgemma.py \\
        --resume_from_checkpoint output/medisign_medgemma4b/checkpoints/checkpoint-500
"""
from __future__ import annotations

import argparse
import inspect
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths / defaults — exposed at module level so the smoke test can import
# them without triggering a heavy model download.
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_MODEL_ID = "google/medgemma-1.5-4b-it"
DEFAULT_TRAIN_FILE = ROOT / "data/training_clean/medgemma_4b/train.jsonl"
DEFAULT_EVAL_FILE = ROOT / "data/training_clean/medgemma_4b/eval.jsonl"
DEFAULT_OUTPUT_DIR = ROOT / "output/medisign_medgemma4b/checkpoints"
DEFAULT_ADAPTER_DIR = ROOT / "output/medisign_medgemma4b/adapter"

# QLoRA hyper-parameters — Requirement 1.6
LORA_RANK = 32
LORA_ALPHA = 64
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = [
    "q_proj",
    "v_proj",
    "k_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
]

# Training hyper-parameters — Requirement 1.7 / Task 1.5.3
MAX_SEQ_LENGTH = 2048
NUM_TRAIN_EPOCHS = 3
PER_DEVICE_BATCH_SIZE = 4
GRADIENT_ACCUMULATION_STEPS = 4
LOGGING_STEPS = 50
SAVE_STEPS = 500
EVAL_STEPS = 500
LEARNING_RATE = 2e-4
WARMUP_RATIO = 0.05
WEIGHT_DECAY = 0.01
NEFTUNE_NOISE_ALPHA = 5
PACKING = True
SAVE_TOTAL_LIMIT = 3
SEED = 42


# ---------------------------------------------------------------------------
# Pure configuration builders — kept import-light so they can be unit-tested
# without `bitsandbytes`, GPU drivers, or a downloaded model.
# ---------------------------------------------------------------------------

@dataclass
class TrainConfig:
    """Resolved CLI configuration."""

    model_id: str
    train_file: Path
    eval_file: Path
    output_dir: Path
    adapter_dir: Path
    num_epochs: float
    max_seq_length: int
    per_device_batch_size: int
    gradient_accumulation_steps: int
    learning_rate: float
    max_steps: int  # -1 means "ignore, train for num_epochs"
    resume_from_checkpoint: str | None


def _require(module_name: str, install_hint: str) -> Any:
    """Import a module and raise a friendly error message if it is missing."""
    try:
        return __import__(module_name)
    except ImportError as exc:  # pragma: no cover - exercised in real runs
        raise SystemExit(
            f"Missing dependency '{module_name}'. {install_hint}"
        ) from exc


def build_bnb_config():
    """1.5.1 — 4-bit NF4 quantization config (bitsandbytes via transformers).

    Compute dtype is bf16 — MedGemma was trained in bf16, fp16 produces
    measurably worse perplexity for Gemma-family models.
    """
    _require("bitsandbytes", "Install with `pip install bitsandbytes>=0.44`.")
    import torch  # type: ignore
    from transformers import BitsAndBytesConfig  # type: ignore

    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )


def build_lora_config(resume_from_checkpoint: str | None = None):
    """1.5.2 — QLoRA adapter config with attention + MLP target modules.

    When resuming from an existing adapter checkpoint, load the LoraConfig
    directly from the checkpoint so r/alpha/target_modules stay consistent.
    """
    from peft import LoraConfig  # type: ignore

    if resume_from_checkpoint:
        import os
        adapter_cfg = os.path.join(resume_from_checkpoint, "adapter_config.json")
        if os.path.exists(adapter_cfg):
            import json
            with open(adapter_cfg) as f:
                saved = json.load(f)
            rank = saved.get("r", LORA_RANK)
            alpha = saved.get("lora_alpha", LORA_ALPHA)
            dropout = saved.get("lora_dropout", LORA_DROPOUT)
            targets = saved.get("target_modules", list(LORA_TARGET_MODULES))
            print(f"[resume] Loaded LoRA config from checkpoint: r={rank}, alpha={alpha}")
            return LoraConfig(
                r=rank,
                lora_alpha=alpha,
                lora_dropout=dropout,
                target_modules=targets,
                bias="none",
                task_type="CAUSAL_LM",
            )

    return LoraConfig(
        r=LORA_RANK,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=list(LORA_TARGET_MODULES),
        bias="none",
        task_type="CAUSAL_LM",
    )


def build_training_args(cfg: TrainConfig):
    """1.5.3 — Build SFTConfig (preferred) or TrainingArguments fallback.

    Returns an object that is accepted by `SFTTrainer.__init__(args=...)`.

    Newer ``trl`` releases (>= 0.12) require ``SFTConfig`` — its
    constructor accepts ``max_seq_length`` and ``dataset_text_field``
    directly. On older ``trl`` versions we fall back to
    ``transformers.TrainingArguments`` and pass those two fields to
    ``SFTTrainer.__init__`` instead (see :func:`run_training`).
    """
    common: dict[str, Any] = dict(
        output_dir=str(cfg.output_dir),
        num_train_epochs=cfg.num_epochs,
        per_device_train_batch_size=cfg.per_device_batch_size,
        per_device_eval_batch_size=cfg.per_device_batch_size,
        gradient_accumulation_steps=cfg.gradient_accumulation_steps,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        learning_rate=cfg.learning_rate,
        warmup_ratio=WARMUP_RATIO,
        lr_scheduler_type="cosine",
        optim="paged_adamw_8bit",
        weight_decay=WEIGHT_DECAY,
        neftune_noise_alpha=NEFTUNE_NOISE_ALPHA,
        bf16=True,
        fp16=False,
        logging_steps=LOGGING_STEPS,
        save_steps=SAVE_STEPS,
        save_strategy="steps",
        save_total_limit=SAVE_TOTAL_LIMIT,
        eval_steps=EVAL_STEPS,
        eval_strategy="steps",
        report_to="none",
        seed=SEED,
        max_steps=cfg.max_steps,
        dataloader_pin_memory=False,
    )

    try:
        from trl import SFTConfig  # type: ignore

        sft_signature = inspect.signature(SFTConfig.__init__)
        length_kwarg = (
            "max_length"
            if "max_length" in sft_signature.parameters
            else "max_seq_length"
        )

        return SFTConfig(
            **common,
            **{length_kwarg: cfg.max_seq_length},
            dataset_text_field="text",
            packing=PACKING,
        )
    except ImportError:
        from transformers import TrainingArguments  # type: ignore

        return TrainingArguments(**common)


# ---------------------------------------------------------------------------
# Heavy lifting — only called from the CLI / GPU host
# ---------------------------------------------------------------------------

def _gpu_summary() -> str:
    try:
        import torch  # type: ignore
    except ImportError:
        return "torch not installed"
    if not torch.cuda.is_available():
        return "no CUDA device — training will fail without a GPU"
    name = torch.cuda.get_device_name(0)
    total_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
    return f"GPU 0: {name} ({total_gb:.1f} GB VRAM)"


def load_datasets(train_file: Path, eval_file: Path):
    """Load the chat-templated JSONL files produced by Task 1.4."""
    from datasets import load_dataset  # type: ignore

    if not train_file.exists():
        raise FileNotFoundError(
            f"Train file not found: {train_file}. "
            "Run `python scripts/format_medgemma_dataset.py` first (Tasks 1.3/1.4)."
        )
    if not eval_file.exists():
        raise FileNotFoundError(
            f"Eval file not found: {eval_file}. "
            "Run `python scripts/format_medgemma_dataset.py` first (Tasks 1.3/1.4)."
        )

    return load_dataset(
        "json",
        data_files={"train": str(train_file), "eval": str(eval_file)},
    )


def load_model_and_tokenizer(model_id: str):
    """1.5.1 — Load MedGemma 4B in 4-bit NF4 and prep for k-bit training."""
    _require("bitsandbytes", "Install with `pip install bitsandbytes>=0.44`.")
    from peft import prepare_model_for_kbit_training  # type: ignore
    from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore

    bnb_config = build_bnb_config()

    tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)
    if tokenizer.pad_token is None:
        # Gemma tokenizer has no pad token by default; reuse EOS to keep
        # the loss mask aligned with the chat template.
        tokenizer.pad_token = tokenizer.eos_token

    # Use Flash Attention 2 if available (Ampere/Ada/Blackwell), else fall back
    # to eager. Flash-Attn 2 gives ~3-5× throughput improvement on H100/4090/5070Ti.
    _attn_impl = "eager"
    try:
        import flash_attn  # noqa: F401
        _attn_impl = "flash_attention_2"
        print("[1.5.1] Flash Attention 2 detected — using flash_attention_2")
    except ImportError:
        print("[1.5.1] flash-attn not installed — using eager attention (slower)")

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype="auto",
        attn_implementation=_attn_impl,
    )
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(
        model, use_gradient_checkpointing=True
    )
    return model, tokenizer


def run_training(cfg: TrainConfig) -> Path:
    """End-to-end QLoRA training run."""
    from transformers import set_seed  # type: ignore

    set_seed(SEED)

    print(f"[1.5] {_gpu_summary()}")
    print(f"[1.5] Loading datasets from {cfg.train_file} / {cfg.eval_file}")
    ds = load_datasets(cfg.train_file, cfg.eval_file)
    print(f"  train: {len(ds['train'])} records | eval: {len(ds['eval'])} records")

    print(f"[1.5.1] Loading {cfg.model_id} in 4-bit NF4 ...")
    model, tokenizer = load_model_and_tokenizer(cfg.model_id)

    print("[1.5.2] Building LoRA config (r=32, alpha=64, dropout=0.05)")
    lora_config = build_lora_config(resume_from_checkpoint=cfg.resume_from_checkpoint)

    print("[1.5.3] Building TrainingArguments / SFTConfig")
    training_args = build_training_args(cfg)

    from trl import SFTTrainer  # type: ignore

    sft_kwargs: dict[str, Any] = dict(
        model=model,
        args=training_args,
        train_dataset=ds["train"],
        eval_dataset=ds["eval"],
        peft_config=lora_config,
    )

    # Older trl (< 0.12) takes max_seq_length / tokenizer / dataset_text_field
    # as SFTTrainer kwargs; newer trl reads them off SFTConfig instead.
    if type(training_args).__name__ == "TrainingArguments":
        sft_kwargs.update(
            max_seq_length=cfg.max_seq_length,
            tokenizer=tokenizer,
            dataset_text_field="text",
            packing=PACKING,
        )
    else:
        # SFTConfig-aware trl still wants the tokenizer (renamed to
        # `processing_class` in trl >= 0.16; we pass both for safety).
        sft_kwargs["processing_class"] = tokenizer

    trainer = SFTTrainer(**sft_kwargs)

    print("[1.5] Starting training ...")
    trainer.train(resume_from_checkpoint=cfg.resume_from_checkpoint)

    print(f"[1.5] Saving adapter to {cfg.adapter_dir}")
    cfg.adapter_dir.mkdir(parents=True, exist_ok=True)
    trainer.model.save_pretrained(str(cfg.adapter_dir))
    tokenizer.save_pretrained(str(cfg.adapter_dir))

    return cfg.adapter_dir


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> TrainConfig:
    p = argparse.ArgumentParser(
        description="Train MedGemma 4B Medical Adapter with QLoRA (Task 1.5)."
    )
    p.add_argument("--model_id", default=DEFAULT_MODEL_ID)
    p.add_argument("--train_file", type=Path, default=DEFAULT_TRAIN_FILE)
    p.add_argument("--eval_file", type=Path, default=DEFAULT_EVAL_FILE)
    p.add_argument("--output_dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--adapter_dir", type=Path, default=DEFAULT_ADAPTER_DIR)
    p.add_argument("--num_epochs", type=float, default=NUM_TRAIN_EPOCHS)
    p.add_argument("--max_seq_length", type=int, default=MAX_SEQ_LENGTH)
    p.add_argument(
        "--per_device_batch_size", type=int, default=PER_DEVICE_BATCH_SIZE
    )
    p.add_argument(
        "--gradient_accumulation_steps",
        type=int,
        default=GRADIENT_ACCUMULATION_STEPS,
    )
    p.add_argument("--learning_rate", type=float, default=LEARNING_RATE)
    p.add_argument(
        "--max_steps",
        type=int,
        default=-1,
        help="Optional cap on training steps (use for smoke tests).",
    )
    p.add_argument("--resume_from_checkpoint", default=None)

    args = p.parse_args(argv)
    return TrainConfig(
        model_id=args.model_id,
        train_file=args.train_file,
        eval_file=args.eval_file,
        output_dir=args.output_dir,
        adapter_dir=args.adapter_dir,
        num_epochs=args.num_epochs,
        max_seq_length=args.max_seq_length,
        per_device_batch_size=args.per_device_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        max_steps=args.max_steps,
        resume_from_checkpoint=args.resume_from_checkpoint,
    )


def main(argv: list[str] | None = None) -> None:
    cfg = parse_args(argv)
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    cfg.adapter_dir.mkdir(parents=True, exist_ok=True)
    # Tokenizer parallelism warning is noisy on Kaggle/Vast.ai logs.
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    run_training(cfg)


if __name__ == "__main__":
    main()
