"""
Tests for `scripts.train_qlora_medgemma` config builders (Task 1.5).

These tests verify that the pure config-builder functions in the
production training script return objects with the **exact** values
mandated by the spec (Requirements 1.6 / 1.7). They do NOT load the
model, allocate GPU memory, or download anything from the
Hugging Face Hub, so they are safe to run on any CI host.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import train_qlora_medgemma as tqm  # noqa: E402

# ---------------------------------------------------------------------------
# Optional-dep gating — these tests exercise objects from peft / trl /
# bitsandbytes / transformers. If any of those are missing, skip the file
# rather than fail with an unhelpful ImportError.
# ---------------------------------------------------------------------------

pytest.importorskip("torch")
pytest.importorskip("peft")
pytest.importorskip("transformers")
pytest.importorskip("bitsandbytes")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_cfg(tmp_path: Path) -> tqm.TrainConfig:
    """Build a TrainConfig with the spec defaults but tmp_path output dirs."""
    return tqm.TrainConfig(
        model_id=tqm.DEFAULT_MODEL_ID,
        train_file=tmp_path / "train.jsonl",
        eval_file=tmp_path / "eval.jsonl",
        output_dir=tmp_path / "checkpoints",
        adapter_dir=tmp_path / "adapter",
        num_epochs=tqm.NUM_TRAIN_EPOCHS,
        max_seq_length=tqm.MAX_SEQ_LENGTH,
        per_device_batch_size=tqm.PER_DEVICE_BATCH_SIZE,
        gradient_accumulation_steps=tqm.GRADIENT_ACCUMULATION_STEPS,
        learning_rate=tqm.LEARNING_RATE,
        max_steps=-1,
        resume_from_checkpoint=None,
    )


# ---------------------------------------------------------------------------
# 1.5.1 — BitsAndBytesConfig (4-bit NF4, bf16 compute, double-quant)
# ---------------------------------------------------------------------------

def test_bnb_config_is_4bit_nf4_bf16_doublequant() -> None:
    import torch

    bnb = tqm.build_bnb_config()
    assert bnb.load_in_4bit is True
    assert bnb.bnb_4bit_quant_type == "nf4"
    assert bnb.bnb_4bit_compute_dtype is torch.bfloat16
    assert bnb.bnb_4bit_use_double_quant is True


# ---------------------------------------------------------------------------
# 1.5.2 — LoRA config (r=32, alpha=64, dropout=0.1, target modules)
# ---------------------------------------------------------------------------

def test_lora_config_rank_alpha_dropout_match_spec() -> None:
    lora = tqm.build_lora_config()
    assert lora.r == 32
    assert lora.lora_alpha == 64
    assert lora.lora_dropout == pytest.approx(0.1)
    assert lora.bias == "none"
    assert lora.task_type == "CAUSAL_LM"


def test_lora_config_target_modules_match_spec_set() -> None:
    lora = tqm.build_lora_config()
    expected = {"q_proj", "v_proj", "k_proj", "o_proj"}
    # peft normalises target_modules to a set when given a list; accept both.
    actual = (
        set(lora.target_modules)
        if isinstance(lora.target_modules, (list, tuple, set))
        else lora.target_modules
    )
    assert actual == expected


# ---------------------------------------------------------------------------
# 1.5.3 — TrainingArguments / SFTConfig hyper-parameters
# ---------------------------------------------------------------------------

def test_training_args_have_spec_hyperparameters(tmp_path: Path) -> None:
    cfg = _make_cfg(tmp_path)
    args = tqm.build_training_args(cfg)

    # Spec values from Task 1.5.3
    assert args.num_train_epochs == 3
    assert args.per_device_train_batch_size == 4
    assert args.gradient_accumulation_steps == 4
    assert args.logging_steps == 50
    assert args.save_steps == 500
    assert args.eval_steps == 500


def test_training_args_use_bf16_not_fp16(tmp_path: Path) -> None:
    """MedGemma was trained in bf16; fp16 hurts perplexity on Gemma-family."""
    args = tqm.build_training_args(_make_cfg(tmp_path))
    assert args.bf16 is True
    assert args.fp16 is False


def test_training_args_use_paged_adamw_and_cosine_schedule(tmp_path: Path) -> None:
    args = tqm.build_training_args(_make_cfg(tmp_path))
    assert args.optim == "paged_adamw_8bit"
    assert args.lr_scheduler_type == "cosine"
    assert args.warmup_ratio == pytest.approx(0.03)
    assert args.learning_rate == pytest.approx(2e-4)


def test_training_args_eval_and_save_strategy_steps(tmp_path: Path) -> None:
    args = tqm.build_training_args(_make_cfg(tmp_path))
    # transformers >= 4.46 normalises eval_strategy / save_strategy into
    # IntervalStrategy enums whose `.value` is the original string.
    eval_strategy = getattr(args.eval_strategy, "value", args.eval_strategy)
    save_strategy = getattr(args.save_strategy, "value", args.save_strategy)
    assert str(eval_strategy) == "steps"
    assert str(save_strategy) == "steps"
    assert args.save_total_limit == 3


def test_training_args_gradient_checkpointing_enabled(tmp_path: Path) -> None:
    args = tqm.build_training_args(_make_cfg(tmp_path))
    assert args.gradient_checkpointing is True


def test_training_args_report_to_none_for_offline_runs(tmp_path: Path) -> None:
    args = tqm.build_training_args(_make_cfg(tmp_path))
    # transformers normalises report_to to a list internally.
    report_to = args.report_to if isinstance(args.report_to, list) else [args.report_to]
    assert report_to == ["none"] or report_to == []


def test_training_args_seed_is_fixed_to_42(tmp_path: Path) -> None:
    args = tqm.build_training_args(_make_cfg(tmp_path))
    assert args.seed == 42


def test_training_args_max_seq_length_when_sftconfig_available(tmp_path: Path) -> None:
    """If trl is installed, SFTConfig must expose max_seq_length=2048."""
    trl = pytest.importorskip("trl")
    if not hasattr(trl, "SFTConfig"):
        pytest.skip("Older trl without SFTConfig — checked separately")
    args = tqm.build_training_args(_make_cfg(tmp_path))
    assert getattr(args, "max_seq_length", None) == 2048
    assert getattr(args, "dataset_text_field", None) == "text"


# ---------------------------------------------------------------------------
# CLI parsing — defaults must match the spec values
# ---------------------------------------------------------------------------

def test_parse_args_defaults_match_spec_constants() -> None:
    cfg = tqm.parse_args([])
    assert cfg.model_id == "google/medgemma-1.5-4b-it"
    assert cfg.num_epochs == 3
    assert cfg.max_seq_length == 2048
    assert cfg.per_device_batch_size == 4
    assert cfg.gradient_accumulation_steps == 4
    assert cfg.max_steps == -1


def test_parse_args_max_steps_override() -> None:
    cfg = tqm.parse_args(["--max_steps", "5"])
    assert cfg.max_steps == 5


def test_default_paths_resolve_under_repo_root() -> None:
    # train.jsonl must be the file produced by Task 1.4
    assert tqm.DEFAULT_TRAIN_FILE.name == "train.jsonl"
    assert tqm.DEFAULT_EVAL_FILE.name == "eval.jsonl"
    # adapter dir must match Requirement 1.8
    assert tqm.DEFAULT_ADAPTER_DIR.parts[-2:] == ("medisign_medgemma4b", "adapter")
