"""
Bước 2: Train Qwen 2.5 72B với LoRA
====================================

Chạy trên: Server có GPU mạnh (A100 80GB)
Thời gian: ~8-12 giờ cho full training
Model: Qwen 2.5 72B

⚠️ YÊU CẦU:
- GPU: A100 80GB (hoặc 2x A100 40GB với tensor parallel)
- RAM: 64GB+
- Disk: 100GB+

Nếu không có GPU mạnh, có thể dùng:
- Colab Pro với A100 (đắt)
- RunPod / Vast.ai thuê theo giờ (~$1-2/giờ)

Để test, có thể dùng Qwen 7B thay vì 72B:
- GPU: RTX 4090 / A100 40GB
- Time: 2-4 giờ
"""

# ============================================================================
# SETUP - Chạy trên Server (RunPod/Vast.ai/Local)
# ============================================================================

# @title ## 📦 Cài đặt thư viện
# @markdown Chạy trên terminal:

"""
# Tạo virtual environment
python -m venv venv
source venv/bin/activate

# Cài đặt thư viện
pip install torch torchvision torchaudio
pip install transformers accelerate peft bitsandbytes
pip install datasets loralib sentencepiece
pip install openai  # For DashScope API (nếu dùng cloud)

# Clone MediSign repo nếu cần
git clone https://github.com/your-repo/MediSign.git
cd MediSign
"""

# ============================================================================
# SCRIPT: Train Qwen 72B với LoRA
# ============================================================================

"""
File: train_qwen_lora.py
Chạy: python train_qwen_lora.py

Script này train Qwen 72B với LoRA adapter cho medical domain.
"""

import os
import sys
import json
import torch
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ============================================================================
# CONFIG
# ============================================================================

@dataclass
class TrainingConfig:
    """Cấu hình training."""

    # Model
    model_name: str = "Qwen/Qwen2.5-72B-Instruct"
    # Thay = "Qwen/Qwen2.5-7B-Instruct" nếu không có A100

    # LoRA
    lora_r: int = 64  # Rank cao hơn cho model lớn
    lora_alpha: int = 128
    lora_dropout: float = 0.1
    target_modules: list = field(default_factory=lambda: [
        "q_proj", "v_proj", "k_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ])

    # Training
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 1  # Giảm nếu OOM
    gradient_accumulation_steps: int = 8  # Tương đương batch 8
    learning_rate: float = 1e-4
    max_seq_length: int = 2048
    warmup_steps: int = 100

    # Quantization (giảm VRAM)
    use_4bit: bool = True
    bnb_4bit_compute_dtype: str = "bfloat16"

    # Output
    output_dir: str = "./output/medisign_qwen72b"
    logging_steps: int = 10
    save_steps: int = 500
    eval_steps: int = 500

    # Data
    train_data_path: str = "../data/training_clean/qwen_72b/train.json"
    eval_data_path: str = "../data/training_clean/qwen_72b/eval.json"


# ============================================================================
# LOAD DATA
# ============================================================================

def load_jsonl(path: str):
    """Load JSONL file."""
    data = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def load_json(path: str):
    """Load JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_qwen_prompt(example):
    """Format prompt cho Qwen Instruct.

    Qwen format:
    <|im_start|>system
    {system_prompt}<|im_end|>
    <|im_start|>user
    {user_input}<|im_end|>
    <|im_start|>assistant
    {response}<|im_end|>
    """
    system = example.get('instruction', '')
    user = example.get('input', '')
    assistant = example.get('output', '')

    text = f"<|im_start|>system\n{system}<|im_end|>\n"
    text += f"<|im_start|>user\n{user}<|im_end|>\n"
    text += f"<|im_start|>assistant\n{assistant}<|im_end|>"

    return {"text": text}


# ============================================================================
# MAIN TRAINING SCRIPT
# ============================================================================

def main():
    print("="*60)
    print("TRAIN QWEN 72B + LORA (Medical Adapter)")
    print("="*60)

    # Load config
    config = TrainingConfig()

    print(f"\n📋 Cấu hình:")
    print(f"   Model: {config.model_name}")
    print(f"   LoRA r: {config.lora_r}")
    print(f"   Epochs: {config.num_train_epochs}")
    print(f"   Output: {config.output_dir}")

    # Check GPU
    if not torch.cuda.is_available():
        print("❌ Cần GPU để train! Không có CUDA.")
        return

    gpu_count = torch.cuda.device_count()
    print(f"✅ Có {gpu_count} GPU(s)")

    for i in range(gpu_count):
        print(f"   GPU {i}: {torch.cuda.get_device_name(i)}")
        print(f"   Memory: {torch.cuda.get_device_properties(i).total_memory / 1e9:.1f} GB")

    # ==========================================================================
    # LOAD MODEL
    # ==========================================================================
    print("\n📦 Loading model...")

    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import LoraConfig, get_peft_model, TaskType, PeftModel

    # Quantization config
    bnb_config = None
    if config.use_4bit:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=getattr(torch, config.bnb_4bit_compute_dtype),
            bnb_4bit_use_double_quant=True,
        )

    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        config.model_name,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=getattr(torch, config.bnb_4bit_compute_dtype),
        trust_remote_code=True,
    )

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        config.model_name,
        trust_remote_code=True,
        padding_side="right",
    )

    # Add special tokens nếu cần
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"✅ Model loaded: {config.model_name}")

    # ==========================================================================
    # PREPARE DATA
    # ==========================================================================
    print("\n📂 Loading training data...")

    train_data = load_json(config.train_data_path)
    eval_data = load_json(config.eval_data_path)

    print(f"   Train: {len(train_data)} samples")
    print(f"   Eval: {len(eval_data)} samples")

    # Format
    train_data = [format_qwen_prompt(x) for x in train_data]
    eval_data = [format_qwen_prompt(x) for x in eval_data]

    from datasets import Dataset

    train_dataset = Dataset.from_list(train_data)
    eval_dataset = Dataset.from_list(eval_data)

    # ==========================================================================
    # TOKENIZE
    # ==========================================================================
    print("\n🔧 Tokenizing...")

    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=config.max_seq_length,
            padding="max_length",
            return_tensors=None,
        )

    train_dataset = train_dataset.map(tokenize_function, batched=True, remove_columns=["text"])
    eval_dataset = eval_dataset.map(tokenize_function, batched=True, remove_columns=["text"])

    print(f"✅ Tokenized!")

    # ==========================================================================
    # SETUP LORA
    # ==========================================================================
    print("\n⚙️ Setting up LoRA...")

    lora_config = LoraConfig(
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=config.target_modules,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )

    model = get_peft_model(model, lora_config)

    # Print trainable params
    model.print_trainable_parameters()

    # ==========================================================================
    # TRAINING
    # ==========================================================================
    print("\n" + "="*60)
    print("🏋️ BẮT ĐẦU TRAINING")
    print("="*60)

    from transformers import Trainer, TrainingArguments

    # Create output dir
    os.makedirs(config.output_dir, exist_ok=True)

    # Training arguments
    training_args = TrainingArguments(
        output_dir=config.output_dir,
        num_train_epochs=config.num_train_epochs,
        per_device_train_batch_size=config.per_device_train_batch_size,
        per_device_eval_batch_size=config.per_device_train_batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        warmup_steps=config.warmup_steps,
        logging_steps=config.logging_steps,
        save_steps=config.save_steps,
        eval_steps=config.eval_steps,
        bf16=True,
        save_strategy="steps",
        eval_strategy="steps",
        load_best_model_at_end=True,
        report_to="none",
        gradient_checkpointing=True,  # Tiết kiệm RAM
        max_grad_norm=1.0,
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
    )

    # Train!
    trainer.train()

    # ==========================================================================
    # SAVE
    # ==========================================================================
    print("\n" + "="*60)
    print("💾 LƯU ADAPTER")
    print("="*60)

    model.save_pretrained(config.output_dir + "/adapter")
    tokenizer.save_pretrained(config.output_dir + "/adapter")

    print(f"✅ Adapter saved to: {config.output_dir}/adapter")

    # ==========================================================================
    # TEST
    # ==========================================================================
    print("\n" + "="*60)
    print("🧪 TEST MODEL")
    print("="*60)

    test_prompts = [
        "Tôi bị đau đầu và sốt nhẹ 37.5 độ, có nên đi khám không?",
    ]

    for prompt in test_prompts:
        print(f"\n👤 User: {prompt}")
        print("🤖 AI: ", end="")

        input_text = f"<|im_start|>system\nBạn là MediSign AI - trợ lý y tế. Trả lời ngắn gọn, có disclaimer.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

        inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if "<|im_start|>assistant\n" in response:
            response = response.split("<|im_start|>assistant\n")[-1]

        print(response[:500])

    print("\n" + "="*60)
    print("🎉 HOÀN TẤT!")
    print("="*60)
    print(f"""
Adapter đã được train và lưu tại: {config.output_dir}/adapter

Để sử dụng với vLLM server:
1. Load base model Qwen 72B
2. Load adapter
3. Deploy với vLLM

Xem chi tiết: scripts/04_deploy_server.py
    """)


if __name__ == "__main__":
    main()


# ============================================================================
# ALTERNATIVE: Train Qwen 7B (nếu không có A100)
# ============================================================================

"""
Nếu chỉ có RTX 4090 hoặc A100 40GB, dùng Qwen 7B thay vì 72B:

# Thay đổi trong config:
model_name: str = "Qwen/Qwen2.5-7B-Instruct"

# Giảm LoRA rank:
lora_r: int = 32

# Giảm batch size:
per_device_train_batch_size: int = 2

# Time: ~2-4 giờ thay vì 8-12 giờ
"""

# ============================================================================
# CLOUD OPTùng DashScope API đION: Dể fine-tune
# ============================================================================

"""
Nếu không muốn tự host, có thể dùng Alibaba Cloud DashScope:
- Managed fine-tuning service
- Không cần GPU local
- Chi phí: ~$50-100 cho một lần train

Xem: https://dashscope.console.aliyun.com/
"""
