"""
Bước 3: Inference - Sử dụng Model đã Train
============================================

Hướng dẫn sử dụng Gemma/Qwen + Adapter đã train
"""

# ============================================================================
# INFERENCE VỚI GEMMA 2B + ADAPTER
# ============================================================================

"""
File: inference_gemma.py
Dùng để chạy inference local với model đã train

Usage:
    python inference_gemma.py --adapter ./output/medisign_gemma/adapter
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel, PeftConfig
import json

# ============================================================================
# CONFIG
# ============================================================================

BASE_MODEL = "google/gemma-2b-it"
ADAPTER_PATH = "./output/medisign_gemma/adapter"  # Đường dẫn tới adapter đã train
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ============================================================================
# LOAD MODEL
# ============================================================================

print("Loading base model...")
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map=DEVICE,
    torch_dtype=torch.float16,
)

print("Loading adapter...")
model = PeftModel.from_pretrained(
    base_model,
    ADAPTER_PATH,
    device_map=DEVICE,
)

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

print("✅ Model loaded!")

# ============================================================================
# INFERENCE FUNCTION
# ============================================================================

def generate_response(prompt: str, max_tokens: int = 512) -> str:
    """Generate response từ model."""

    # Format prompt theo Gemma format
    formatted_prompt = f"<start_of_turn>user\nBạn là MediSign AI - trợ lý y tế. Trả lời câu hỏi một cách ngắn gọn, có disclaimer.\n\n{prompt}<end_of_turn>\n<start_of_turn>model\n"

    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(DEVICE)

    outputs = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        eos_token_id=tokenizer.eos_token_id,
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract response
    if "<start_of_turn>model\n" in response:
        response = response.split("<start_of_turn>model\n")[-1]
    if "<end_of_turn>" in response:
        response = response.split("<end_of_turn>")[0]

    return response.strip()


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 MEDISIGN AI - INFERENCE TEST")
    print("="*60)

    test_questions = [
        "Tôi bị đau đầu kèm sốt 37.5 độ, có cần đi khám không?",
        "Uống thuốc tránh thai hàng ngày có uống được kháng sinh không?",
        "Tôi bị đau ngực trái kèm khó thở, phải làm sao?",
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"Câu {i}: {question}")
        print("-"*60)

        response = generate_response(question)
        print(response)

        print("-"*60)

    print("\n✅ Inference test hoàn tất!")


# ============================================================================
# INFERENCE VỚI QWEN 72B + ADAPTER
# ============================================================================

"""
File: inference_qwen.py
Dùng để chạy inference với Qwen model

Usage:
    python inference_qwen.py --adapter ./output/medisign_qwen72b/adapter
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def load_qwen_model(base_model="Qwen/Qwen2.5-72B-Instruct", adapter_path=None):
    """Load Qwen model với adapter."""

    # Load base model
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True,
    )

    # Load adapter nếu có
    if adapter_path:
        model = PeftModel.from_pretrained(model, adapter_path)

    tokenizer = AutoTokenizer.from_pretrained(
        base_model,
        trust_remote_code=True,
    )

    return model, tokenizer


def generate_qwen(prompt, model, tokenizer, max_tokens=512):
    """Generate response với Qwen."""

    # Format theo Qwen format
    formatted = f"<|im_start|>system\nBạn là MediSign AI - trợ lý y tế. Trả lời ngắn gọn, có disclaimer.<|im_end|>\n"
    formatted += f"<|im_start|>user\n{prompt}<|im_end|>\n"
    formatted += f"<|im_start|>assistant\n"

    inputs = tokenizer(formatted, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        do_sample=True,
        temperature=0.7,
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract
    if "<|im_start|>assistant\n" in response:
        response = response.split("<|im_start|>assistant\n")[-1]

    return response


# ============================================================================
# STREAMING API (cho production)
# ============================================================================

"""
Nếu muốn deploy thành API, có thể dùng FastAPI:

# File: api_inference.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    text: str
    max_tokens: int = 512

@app.post("/predict")
async def predict(query: Query):
    response = generate_response(query.text, query.max_tokens)
    return {"response": response}
"""


# ============================================================================
# MOBILE INFERENCE (ON-DEVICE)
# ============================================================================

"""
Để chạy inference trên mobile (Flutter), có thể:

1. Dùng flutter_langchain package
2. Hoặc export sang GGML/llama.cpp format

# Export sang GGML
from peft import PeftModel
# Merge adapter vào base model rồi export

Tuy nhiên với Gemma 2B:
- RAM yêu cầu: ~4-6GB
- Có thể chạy trên mobile mid-range
- Nhưng cần tối ưu thêm

Xem thêm: scripts/04_mobile_inference.py
"""
