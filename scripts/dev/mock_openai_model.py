from __future__ import annotations

import re
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(title="MediSign Mock OpenAI-Compatible Model")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage] = Field(default_factory=list)
    temperature: float | None = None
    max_tokens: int | None = None


def _extract_user_message(messages: list[ChatMessage]) -> str:
    for message in reversed(messages):
        if message.role == "user":
            return message.content.strip()
    return ""


def _extract_rag_context(messages: list[ChatMessage]) -> str:
    system_text = "\n\n".join(message.content for message in messages if message.role == "system")
    marker = "RAG_CONTEXT:"
    if marker not in system_text:
        return ""
    return system_text.split(marker, 1)[1].strip()


def _summarize_context(context: str) -> tuple[list[str], list[str]]:
    source_ids = re.findall(r"record_id=([^;]+);", context)
    blocks = [block.strip() for block in re.split(r"\n\s*\n", context) if block.strip()]
    snippets: list[str] = []
    for block in blocks[:3]:
        lines = block.splitlines()
        if len(lines) > 1:
            snippets.append(lines[-1].strip())
    return source_ids[:5], snippets


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/chat/completions")
def chat_completions(payload: ChatCompletionRequest) -> dict[str, Any]:
    user_message = _extract_user_message(payload.messages)
    rag_context = _extract_rag_context(payload.messages)
    source_ids, snippets = _summarize_context(rag_context)

    if snippets:
        content = (
            "Đây là phản hồi từ model server giả lập để test luồng web → backend → "
            "RAG → model.\n\n"
            f"Câu hỏi: {user_message}\n\n"
            "Thông tin RAG tìm được:\n"
            + "\n".join(f"- {snippet}" for snippet in snippets)
            + "\n\nNguồn: "
            + ", ".join(f"[{source_id}]" for source_id in source_ids)
            + "\n\nLưu ý: Đây là server giả lập, chưa phải model y tế thật."
        )
    else:
        content = (
            "Đây là phản hồi từ model server giả lập. Backend đã gọi model thành công, "
            "nhưng request này không có RAG context phù hợp."
        )

    return {
        "id": "chatcmpl-medisign-mock",
        "object": "chat.completion",
        "model": payload.model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content}}],
    }
