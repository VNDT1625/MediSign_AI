#!/usr/bin/env python3
"""
MedGemma 4B Inference Server with Dual LoRA Adapters
=====================================================

Serves MedGemma 1.5 4B với 2 adapter (medical + psychology) qua OpenAI-compatible
REST API tại /v1/chat/completions.

Backend FastAPI chỉ cần set:
    BACKEND_AI_PROVIDER=openai_compatible
    BACKEND_AI_BASE_URL=http://localhost:8080/v1
    BACKEND_AI_API_KEY=any-string-works
    BACKEND_AI_MEDICAL_MODEL=medisign-medgemma-medical
    BACKEND_AI_PSYCHOLOGY_MODEL=medisign-medgemma-psychology

Server tự switch adapter dựa trên field "model" trong request:
    model="medisign-medgemma-medical"      → activate medical LoRA
    model="medisign-medgemma-psychology"   → activate psychology LoRA

Yêu cầu:
    pip install fastapi uvicorn transformers peft bitsandbytes accelerate \
                pydantic torch huggingface_hub

Cách chạy:
    HF_TOKEN=hf_xxx python scripts/serve_medgemma.py
    HF_TOKEN=hf_xxx python scripts/serve_medgemma.py --port 8080 --host 0.0.0.0

Endpoints:
    GET  /health                  — health check
    GET  /v1/models               — list available models (medical + psychology)
    POST /v1/chat/completions     — OpenAI-compatible chat (stream + non-stream)

Env vars:
    HF_TOKEN                     — HuggingFace token (required)
    BASE_MODEL_ID                — base model (default: google/medgemma-1.5-4b-it)
    MEDICAL_ADAPTER_ID           — medical adapter (default: thuaannn/medisign-medgemma4b-adapter)
    PSYCHOLOGY_ADAPTER_ID        — psychology adapter (default: thuaannn/medisign-medgemma4b-psychology)
    LOAD_4BIT                    — set "1" để load 4-bit (default: 1, recommended)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from uuid import uuid4

import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("medgemma-server")

# ── Config ──────────────────────────────────────────────────────────────
BASE_MODEL_ID         = os.environ.get("BASE_MODEL_ID", "google/medgemma-1.5-4b-it")
MEDICAL_ADAPTER_ID    = os.environ.get("MEDICAL_ADAPTER_ID", "thuaannn/medisign-medgemma4b-adapter")
PSYCHOLOGY_ADAPTER_ID = os.environ.get("PSYCHOLOGY_ADAPTER_ID", "thuaannn/medisign-medgemma4b-psychology")
LOAD_4BIT             = os.environ.get("LOAD_4BIT", "1") == "1"
HF_TOKEN              = (os.environ.get("HF_TOKEN") or "").strip()

# Model name → adapter name mapping
MODEL_ADAPTER_MAP = {
    "medisign-medgemma-medical":     "medical",
    "medisign-medgemma-psychology":  "psychology",
    "medical":                       "medical",
    "psychology":                    "psychology",
    BASE_MODEL_ID:                   "medical",  # default to medical for base ID
}

# ── Globals (initialized in lifespan) ───────────────────────────────────
MODEL = None
TOKENIZER = None
ACTIVE_ADAPTER: str | None = None
GENERATION_LOCK = asyncio.Lock()


# ── Schemas (subset of OpenAI API) ──────────────────────────────────────
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "medisign-medgemma-medical"
    messages: list[ChatMessage]
    temperature: float = 0.7
    top_p: float = 0.95
    max_tokens: int | None = Field(default=512, ge=1, le=4096)
    stream: bool = False
    stop: list[str] | str | None = None


class ChatCompletionChoice(BaseModel):
    index: int = 0
    message: ChatMessage
    finish_reason: str = "stop"


class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatCompletionChoice]
    usage: ChatCompletionUsage


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "medisign"


class ModelsList(BaseModel):
    object: str = "list"
    data: list[ModelInfo]


# ── Model loading ───────────────────────────────────────────────────────
def load_model_and_adapters() -> None:
    """Load base model + both LoRA adapters into a PeftModel."""
    global MODEL, TOKENIZER

    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import PeftModel

    if not torch.cuda.is_available():
        logger.warning("CUDA not available — running on CPU (sẽ rất chậm)")

    logger.info("Loading tokenizer ...")
    TOKENIZER = AutoTokenizer.from_pretrained(BASE_MODEL_ID, token=HF_TOKEN or None)
    if TOKENIZER.pad_token is None:
        TOKENIZER.pad_token = TOKENIZER.eos_token

    logger.info(
        "Loading base model: %s (4-bit=%s)",
        BASE_MODEL_ID, LOAD_4BIT,
    )

    use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    dtype = torch.bfloat16 if use_bf16 else torch.float16

    bnb = None
    if LOAD_4BIT:
        bnb = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=dtype,
            bnb_4bit_use_double_quant=True,
        )

    base = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID,
        quantization_config=bnb,
        device_map="auto" if torch.cuda.is_available() else None,
        dtype=dtype,
        token=HF_TOKEN or None,
    )

    logger.info("Loading medical adapter: %s", MEDICAL_ADAPTER_ID)
    MODEL = PeftModel.from_pretrained(
        base,
        MEDICAL_ADAPTER_ID,
        adapter_name="medical",
        token=HF_TOKEN or None,
    )

    logger.info("Loading psychology adapter: %s", PSYCHOLOGY_ADAPTER_ID)
    MODEL.load_adapter(
        PSYCHOLOGY_ADAPTER_ID,
        adapter_name="psychology",
        token=HF_TOKEN or None,
    )

    MODEL.set_adapter("medical")  # default
    MODEL.eval()

    if torch.cuda.is_available():
        vram_used = torch.cuda.memory_allocated() / 1024**3
        logger.info("✅ Model loaded. VRAM: %.2f GB", vram_used)
    else:
        logger.info("✅ Model loaded on CPU")


def switch_adapter(name: str) -> None:
    """Switch active LoRA adapter."""
    global ACTIVE_ADAPTER
    if ACTIVE_ADAPTER == name:
        return
    MODEL.set_adapter(name)
    ACTIVE_ADAPTER = name
    logger.info("Switched adapter → %s", name)


def resolve_adapter(model_name: str) -> str:
    """Map OpenAI 'model' field → internal adapter name."""
    return MODEL_ADAPTER_MAP.get(model_name, "medical")


# ── Generation ──────────────────────────────────────────────────────────
def build_prompt(messages: list[ChatMessage]) -> str:
    """Convert OpenAI-format messages → Gemma chat template string."""
    msgs = [{"role": m.role, "content": m.content} for m in messages]
    text = TOKENIZER.apply_chat_template(
        msgs,
        tokenize=False,
        add_generation_prompt=True,
    )
    return text


@torch.no_grad()
def generate_text(
    prompt: str,
    max_tokens: int,
    temperature: float,
    top_p: float,
) -> tuple[str, int, int]:
    """Run generation. Returns (text, prompt_tokens, completion_tokens)."""
    inputs = TOKENIZER(prompt, return_tensors="pt").to(MODEL.device)
    prompt_len = inputs["input_ids"].shape[1]

    do_sample = temperature > 0.0
    out = MODEL.generate(
        **inputs,
        max_new_tokens=max_tokens,
        do_sample=do_sample,
        temperature=max(temperature, 1e-5),
        top_p=top_p,
        pad_token_id=TOKENIZER.pad_token_id,
        repetition_penalty=1.05,
    )
    completion_ids = out[0][prompt_len:]
    completion_len = int(completion_ids.shape[0])
    text = TOKENIZER.decode(completion_ids, skip_special_tokens=True)
    return text.strip(), int(prompt_len), completion_len


async def generate_text_async(
    prompt: str, max_tokens: int, temperature: float, top_p: float,
) -> tuple[str, int, int]:
    """Run generation in a thread + adapter lock to avoid concurrent contention."""
    async with GENERATION_LOCK:
        return await asyncio.to_thread(
            generate_text, prompt, max_tokens, temperature, top_p,
        )


# ── App ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting MedGemma server ...")
    load_model_and_adapters()
    yield
    logger.info("Shutting down ...")


app = FastAPI(title="MedGemma Inference Server", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status":          "ok" if MODEL is not None else "loading",
        "base_model":      BASE_MODEL_ID,
        "medical_adapter": MEDICAL_ADAPTER_ID,
        "psychology_adapter": PSYCHOLOGY_ADAPTER_ID,
        "active_adapter":  ACTIVE_ADAPTER,
        "device":          str(MODEL.device) if MODEL is not None else "cpu",
        "load_4bit":       LOAD_4BIT,
    }


@app.get("/v1/models", response_model=ModelsList)
async def list_models() -> ModelsList:
    now = int(time.time())
    return ModelsList(data=[
        ModelInfo(id="medisign-medgemma-medical",    created=now),
        ModelInfo(id="medisign-medgemma-psychology", created=now),
    ])


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages must not be empty")

    adapter = resolve_adapter(req.model)
    switch_adapter(adapter)

    prompt = build_prompt(req.messages)
    max_tokens = req.max_tokens or 512

    if req.stream:
        return StreamingResponse(
            _stream_response(req, prompt, max_tokens),
            media_type="text/event-stream",
        )

    text, n_prompt, n_completion = await generate_text_async(
        prompt, max_tokens, req.temperature, req.top_p,
    )
    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid4().hex[:24]}",
        created=int(time.time()),
        model=req.model,
        choices=[ChatCompletionChoice(
            message=ChatMessage(role="assistant", content=text),
            finish_reason="stop",
        )],
        usage=ChatCompletionUsage(
            prompt_tokens=n_prompt,
            completion_tokens=n_completion,
            total_tokens=n_prompt + n_completion,
        ),
    )


async def _stream_response(
    req: ChatCompletionRequest, prompt: str, max_tokens: int,
) -> AsyncGenerator[str, None]:
    """Naive streaming: generate fully, then yield in small chunks.

    Real token-by-token streaming requires `TextIteratorStreamer` from transformers.
    Keeping this simple so backend gets working SSE without extra complexity.
    """
    text, _, _ = await generate_text_async(
        prompt, max_tokens, req.temperature, req.top_p,
    )
    cmpl_id = f"chatcmpl-{uuid4().hex[:24]}"
    created = int(time.time())

    chunk_size = 24
    for i in range(0, len(text), chunk_size):
        chunk_text = text[i:i + chunk_size]
        payload = {
            "id":      cmpl_id,
            "object":  "chat.completion.chunk",
            "created": created,
            "model":   req.model,
            "choices": [{
                "index": 0,
                "delta": {"role": "assistant", "content": chunk_text},
                "finish_reason": None,
            }],
        }
        yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    final = {
        "id":      cmpl_id,
        "object":  "chat.completion.chunk",
        "created": created,
        "model":   req.model,
        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
    }
    yield f"data: {json.dumps(final, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"


# ── Main ────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--workers", type=int, default=1, help="Phải =1 vì model singleton")
    args = p.parse_args()

    import uvicorn
    uvicorn.run(
        "scripts.serve_medgemma:app" if "scripts" in __name__ else "serve_medgemma:app",
        host=args.host,
        port=args.port,
        workers=args.workers,
        log_level="info",
    )


if __name__ == "__main__":
    main()
