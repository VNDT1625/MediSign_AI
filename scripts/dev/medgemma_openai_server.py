from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Literal

import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parents[2]


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "medisign-medgemma-medical"
    messages: list[ChatMessage] = Field(default_factory=list)
    temperature: float = 0.2
    max_tokens: int = 1024
    top_p: float = 0.9


class ModelRuntime:
    def __init__(self) -> None:
        self.base_model = os.getenv("MEDISIGN_BASE_MODEL", "google/medgemma-1.5-4b-it")
        self.adapter_path = Path(
            os.getenv(
                "MEDISIGN_ADAPTER_PATH",
                str(ROOT / "output" / "medisign-medgemma4b-adapter"),
            )
        )
        self.load_in_4bit = os.getenv("MEDISIGN_LOAD_IN_4BIT", "1") != "0"
        self.max_input_tokens = int(os.getenv("MEDISIGN_MAX_INPUT_TOKENS", "4096"))
        self.tokenizer: Any | None = None
        self.model: Any | None = None
        self.loaded_at: float | None = None

    def status(self) -> dict[str, Any]:
        return {
            "base_model": self.base_model,
            "adapter_path": str(self.adapter_path),
            "adapter_exists": self.adapter_path.exists(),
            "loaded": self.model is not None,
            "loaded_at": self.loaded_at,
            "cuda": torch.cuda.is_available(),
            "gpu_count": torch.cuda.device_count(),
            "device": self._device_name(),
            "load_in_4bit": self.load_in_4bit,
        }

    def load(self) -> None:
        if self.model is not None:
            return
        if not self.adapter_path.exists():
            raise RuntimeError(f"Adapter path not found: {self.adapter_path}")
        if self.load_in_4bit and not torch.cuda.is_available():
            raise RuntimeError("MEDISIGN_LOAD_IN_4BIT=1 requires a CUDA GPU")

        self._patch_gemma3_token_type_ids()

        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        quantization_config = None
        if self.load_in_4bit:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
            )

        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model, use_fast=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self._load_adapter_chat_template()

        model = AutoModelForCausalLM.from_pretrained(
            self.base_model,
            device_map="auto",
            torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
            quantization_config=quantization_config,
            attn_implementation="eager",
        )
        self.model = PeftModel.from_pretrained(model, str(self.adapter_path))
        self.model.eval()
        self.loaded_at = time.time()

    def generate(self, request: ChatCompletionRequest) -> str:
        self.load()
        assert self.tokenizer is not None
        assert self.model is not None

        prompt = self._build_prompt(request.messages)
        inputs = self.tokenizer(
            text=prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_input_tokens,
        )
        input_device = self._input_device()
        inputs = {
            key: value.to(input_device) if hasattr(value, "to") else value
            for key, value in inputs.items()
        }

        with torch.inference_mode():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max(32, min(request.max_tokens, 2048)),
                do_sample=request.temperature > 0,
                temperature=max(request.temperature, 0.01),
                top_p=request.top_p,
                repetition_penalty=1.05,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        input_len = inputs["input_ids"].shape[-1]
        generated_ids = output_ids[0][input_len:]
        text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        return text.strip()

    def _build_prompt(self, messages: list[ChatMessage]) -> str:
        system_parts = [m.content.strip() for m in messages if m.role == "system" and m.content.strip()]
        user_parts = [m.content.strip() for m in messages if m.role == "user" and m.content.strip()]
        assistant_parts = [
            m.content.strip() for m in messages if m.role == "assistant" and m.content.strip()
        ]

        system_text = "\n\n".join(system_parts)
        user_text = user_parts[-1] if user_parts else ""
        prior_assistant = "\n\n".join(assistant_parts[-2:])
        merged_user = "\n\n".join(
            part
            for part in [
                f"Hệ thống:\n{system_text}" if system_text else "",
                f"Ngữ cảnh trả lời trước:\n{prior_assistant}" if prior_assistant else "",
                f"Người dùng:\n{user_text}",
            ]
            if part
        )

        assert self.tokenizer is not None
        chat = [{"role": "user", "content": merged_user}]
        return self.tokenizer.apply_chat_template(
            chat,
            add_generation_prompt=True,
            tokenize=False,
        )

    def _load_adapter_chat_template(self) -> None:
        template_path = self.adapter_path / "chat_template.jinja"
        if not template_path.exists() or self.tokenizer is None:
            return
        template = template_path.read_text(encoding="utf-8")
        self.tokenizer.chat_template = template

    def _device_name(self) -> str:
        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
        return "cpu"

    def _input_device(self) -> torch.device:
        assert self.model is not None
        try:
            return next(self.model.parameters()).device
        except StopIteration:
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @staticmethod
    def _patch_gemma3_token_type_ids() -> None:
        try:
            import inspect
            from transformers.models.gemma3 import modeling_gemma3

            def make_token_type_ids(input_ids=None, inputs_embeds=None):
                if input_ids is not None:
                    return torch.zeros_like(input_ids, dtype=torch.long)
                if inputs_embeds is not None:
                    return torch.zeros(
                        inputs_embeds.shape[:2],
                        dtype=torch.long,
                        device=inputs_embeds.device,
                    )
                return None

            if hasattr(modeling_gemma3, "Gemma3ForCausalLM"):
                cls = modeling_gemma3.Gemma3ForCausalLM
                if not hasattr(cls, "_medisign_original_forward"):
                    cls._medisign_original_forward = cls.forward

                    def forward(self, *args, **kwargs):
                        if kwargs.get("token_type_ids") is None:
                            token_type_ids = make_token_type_ids(
                                kwargs.get("input_ids"), kwargs.get("inputs_embeds")
                            )
                            if token_type_ids is not None:
                                kwargs["token_type_ids"] = token_type_ids
                        return cls._medisign_original_forward(self, *args, **kwargs)

                    cls.forward = forward

            if hasattr(modeling_gemma3, "Gemma3Model"):
                cls = modeling_gemma3.Gemma3Model
                if not hasattr(cls, "_medisign_original_forward"):
                    cls._medisign_original_forward = cls.forward

                    def forward(self, *args, **kwargs):
                        if kwargs.get("token_type_ids") is None:
                            token_type_ids = make_token_type_ids(
                                kwargs.get("input_ids"), kwargs.get("inputs_embeds")
                            )
                            if token_type_ids is not None:
                                kwargs["token_type_ids"] = token_type_ids
                        return cls._medisign_original_forward(self, *args, **kwargs)

                    cls.forward = forward

            if hasattr(modeling_gemma3, "create_causal_mask_mapping") and not hasattr(
                modeling_gemma3, "_medisign_original_create_causal_mask_mapping"
            ):
                original = modeling_gemma3.create_causal_mask_mapping
                signature = inspect.signature(original)
                modeling_gemma3._medisign_original_create_causal_mask_mapping = original

                def patched_create_causal_mask_mapping(*args, **kwargs):
                    try:
                        bound = signature.bind_partial(*args, **kwargs)
                        if bound.arguments.get("token_type_ids") is None:
                            token_type_ids = make_token_type_ids(
                                bound.arguments.get("input_ids"),
                                bound.arguments.get("inputs_embeds"),
                            )
                            if token_type_ids is not None:
                                bound.arguments["token_type_ids"] = token_type_ids
                                return original(*bound.args, **bound.kwargs)
                    except Exception:
                        pass
                    if kwargs.get("token_type_ids") is None:
                        token_type_ids = make_token_type_ids(
                            kwargs.get("input_ids"), kwargs.get("inputs_embeds")
                        )
                        if token_type_ids is not None:
                            kwargs["token_type_ids"] = token_type_ids
                    return original(*args, **kwargs)

                modeling_gemma3.create_causal_mask_mapping = patched_create_causal_mask_mapping
        except Exception as exc:
            print(f"MediSign Gemma3 token_type_ids patch skipped: {exc}")


runtime = ModelRuntime()
app = FastAPI(title="MediSign MedGemma OpenAI-Compatible Server")


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", **runtime.status()}


@app.on_event("startup")
def preload_on_startup() -> None:
    if os.getenv("MEDISIGN_PRELOAD_ON_START", "0") == "1":
        runtime.load()


@app.post("/v1/chat/completions")
def chat_completions(payload: ChatCompletionRequest) -> dict[str, Any]:
    try:
        content = runtime.generate(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "id": f"chatcmpl-medisign-{int(time.time())}",
        "object": "chat.completion",
        "model": payload.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
    }
