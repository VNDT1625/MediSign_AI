"""
Bước 2: Train Gemma 2B với LoRA
====================================

Chạy trên: Google Colab (miễn phí T4 GPU)
Thời gian: ~30-60 phút cho 1 epoch
Model: Gemma 2B (instruction tuning)

Usage:
    1. Upload script này lên Google Colab
    2. Upload data từ Bước 1
    3. Chạy cell by cell

Lưu ý: Script này dùng transformers + peft (LoRA)
"""

# ============================================================================
# SETUP - Chạy trên Google Colab
# ============================================================================

# @title ## 📦 Cài đặt thư viện
# @markdown Chạy cell này để cài đặt các thư viện cần thiết

# @markdown ---
# @markdown **Lưu ý quan trọng:**
# @markdown - Cần GPU để train (Colab miễn phí có T4)
# @markdown - RAM ~16GB là đủ cho Gemma 2B

%%capture
# Cài đặt thư viện
!pip install torch torchvision torchaudio
!pip install transformers accelerate peft bitsandbytes
!pip install datasets loralib
!pip install sentencepiece protobuf accelerate

# @title ## 📁 Upload dữ liệu training
# @markdown Upload file `train.json` và `eval.json` từ Bước 1

from google.colab import files
import os

# Tạo thư mục
os.makedirs('/content/data', exist_ok=True)

# Upload files
print("Upload train.json:")
uploaded = files.upload()
if 'train.json' in uploaded:
    !mv train.json /content/data/

print("\nUpload eval.json:")
uploaded = files.upload()
if 'eval.json' in uploaded:
    !mv eval.json /content/data/

# Verify
print("\n📂 Files in /content/data/:")
!ls -la /content/data/

# @title ## ⚙️ Cấu hình Training

# @markdown ---
# @markdown **Cấu hình mặc định:**
# @markdown - Model: google/gemma-2b-it (instruction tuned)
# @markdown - LoRA: rank=8, alpha=16, target=q_proj,v_proj
# @markdown - Epochs: 3 (đủ để có kết quả)

from dataclasses import dataclass, field
from typing import Optional
import json
import torch

# @markdown ---
# @markdown **Cấu hình:**
model_id = "google/gemma-2b-it"  # @param ["google/gemma-2b-it", "google/gemma-2b"] {type:"string"}
output_dir = "/content/medisign_gemma"  # @param {type:"string"}
num_train_epochs = 3  # @param {type:"integer"}
per_device_train_batch_size = 1  # @param {type:"integer"}
learning_rate = 2e-4  # @param {type:"number"}
lora_r = 8  # @param {type:"integer"}
lora_alpha = 16  # @param {type:"integer"}
lora_dropout = 0.05  # @param {type:"number"}
max_seq_length = 512  # @param {type:"integer"}

# LoRA config
LORA_CONFIG = {
    "r": lora_r,
    "lora_alpha": lora_alpha,
    "lora_dropout": lora_dropout,
    "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    "bias": "none",
    "task_type": "CAUSAL_LM"
}

# @title ## 🔧 Load Model và Data

print("Loading model...")
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset
import json

# Quantization config (giảm RAM)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# Load model
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.float16,
)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Load data
with open('/content/data/train.json', 'r') as f:
    train_data = json.load(f)

with open('/content/data/eval.json', 'r') as f:
    eval_data = json.load(f)

print(f"✅ Loaded model: {model_id}")
print(f"✅ Loaded {len(train_data)} train, {len(eval_data)} eval samples")

# Format data cho training
def format_prompt(example):
    """Format theo instruction tuning format."""
    text = f"<start_of_turn>user\n{example['instruction']}\n\n{example['input']}<end_of_turn>\n<start_of_turn>model\n{example['output']}<end_of_turn>"
    return {"text": text}

# Apply formatting
train_dataset = Dataset.from_list(train_data).map(format_prompt, remove_columns=train_data[0].keys())
eval_dataset = Dataset.from_list(eval_data).map(format_prompt, remove_columns=eval_data[0].keys())

# Tokenize
def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length=max_seq_length,
        padding="max_length",
        return_tensors=None,
    )

train_dataset = train_dataset.map(tokenize_function, batched=True, remove_columns=["text"])
eval_dataset = eval_dataset.map(tokenize_function, batched=True, remove_columns=["text"])

print(f"✅ Tokenized data ready")

# @title ## 🏋️ Train LoRA Adapter

print("\n" + "="*60)
print("BẮT ĐẦU TRAINING")
print("="*60)

from transformers import Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType

# Setup LoRA
lora_config = LoraConfig(
    r=LORA_CONFIG["r"],
    lora_alpha=LORA_CONFIG["lora_alpha"],
    lora_dropout=LORA_CONFIG["lora_dropout"],
    target_modules=LORA_CONFIG["target_modules"],
    bias=LORA_CONFIG["bias"],
    task_type=TaskType.CAUSAL_LM,
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# Training arguments
training_args = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=num_train_epochs,
    per_device_train_batch_size=per_device_train_batch_size,
    per_device_eval_batch_size=per_device_train_batch_size,
    learning_rate=learning_rate,
    fp16=True,
    save_strategy="epoch",
    save_total_limit=2,
    logging_steps=10,
    eval_strategy="epoch",
    load_best_model_at_end=True,
    report_to="none",
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

# Train!
trainer.train()

print("\n✅ Training hoàn tất!")

# @title ## 💾 Lưu Adapter

print("\n" + "="*60)
print("LƯU ADAPTER")
print("="*60)

# Lưu adapter
model.save_pretrained(output_dir + "/adapter")
tokenizer.save_pretrained(output_dir + "/adapter")

print(f"✅ Adapter saved to: {output_dir}/adapter")

# Download về máy
!zip -r {output_dir}.zip {output_dir}
files.download(f"{output_dir}.zip")

print("\n📦 Đã tạo file zip. Download về máy để sử dụng!")

# @title ## 🧪 Test Model

print("\n" + "="*60)
print("TEST MODEL")
print("="*60)

# Test prompt
test_prompts = [
    "Tôi bị đau đầu và sốt nhẹ 37.5 độ, có nên đi khám không?",
    "Uống thuốc tránh thai có uống được cà phê không?",
]

for prompt in test_prompts:
    print(f"\n👤 User: {prompt}")
    print("🤖 AI: ", end="")

    input_text = f"<start_of_turn>user\nBạn là MediSign AI. Trả lời câu hỏi y tế một cách ngắn gọn.\n\n{prompt}<end_of_turn>\n<start_of_turn>model\n"

    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract just the response
    if "<start_of_turn>model\n" in response:
        response = response.split("<start_of_turn>model\n")[-1]
    if "<end_of_turn>" in response:
        response = response.split("<end_of_turn>")[0]

    print(response[:500])

print("\n" + "="*60)
print("🎉 HOÀN TẤT!")
print("="*60)
print("""
Adapter đã được train và lưu.

Để sử dụng:
1. Load base model (Gemma 2B)
2. Load adapter đã train
3. Dùng cho inference

Xem hướng dẫn chi tiết trong: scripts/03_inference.py
""")
