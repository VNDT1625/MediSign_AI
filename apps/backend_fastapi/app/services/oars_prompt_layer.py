from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from typing import Any

import httpx

from app.core.config import settings
from app.schemas.diagnostic import (
    ChatPhase,
    ConclusionEvidence,
    DiagnosticState,
    DiscriminativeQuestion,
)
from app.services.rag_service import RAGHit, RAGService, rag_service


LLMCaller = Callable[[str, str], Awaitable[str]]


class OARSPromptLayer:
    """Convert technical diagnostic state into OARS-style Vietnamese text."""

    def __init__(
        self,
        rag: RAGService | None = None,
        llm_caller: LLMCaller | None = None,
    ) -> None:
        self.rag = rag or rag_service
        self._llm_caller = llm_caller

    def system_prompt(
        self,
        phase: ChatPhase,
        state: DiagnosticState,
        *,
        rag_hits: list[RAGHit] | None = None,
        discriminative_question: DiscriminativeQuestion | None = None,
        evidence: ConclusionEvidence | None = None,
    ) -> str:
        context = self.rag.build_context(rag_hits or [])
        state_summary = self._state_summary(state)

        if phase == "questioning":
            question_json = self._json(discriminative_question)
            return (
                "Bạn là MediSign AI, trợ lý y tế tiếng Việt. Tuân thủ OARS:\n"
                "  - Affirm: ghi nhận điều user vừa chia sẻ\n"
                "  - Reflect: phản chiếu để xác nhận hiểu đúng\n"
                "  - Open question: câu hỏi mở 1 ý, không dẫn dắt\n"
                "  - Summary: tóm tắt ngắn trước khi hỏi tiếp\n\n"
                "Bạn KHÔNG được:\n"
                '  - đưa kết luận khi phase != "conclusion"\n'
                "  - bịa bệnh ngoài RAG_CONTEXT\n"
                '  - dùng chuỗi "Kết luận:" trong phase questioning\n\n'
                "Hỏi đúng triệu chứng được cho trong NEXT_QUESTION.symptom.\n"
                "Chỉ tạo một câu hỏi và toàn bộ phản hồi chỉ có đúng một dấu hỏi.\n"
                f"RAG_CONTEXT:\n{context}\n"
                f"NEXT_QUESTION: {question_json}\n"
                f"STATE_SUMMARY: {state_summary}"
            )

        if phase == "conclusion":
            evidence_json = self._json(evidence)
            return (
                "Bạn là MediSign AI, trợ lý y tế tiếng Việt. Chỉ tổng hợp từ "
                "RAG_CONTEXT và EVIDENCE, không chẩn đoán chắc chắn.\n\n"
                'Output bắt buộc khi phase="conclusion":\n'
                '  - "Kết luận:" + danh sách bệnh dạng "• <Tên> (XX%) <emoji>"\n'
                '  - "Mức độ: <XANH|VÀNG|ĐỎ>"\n'
                "  - khuyến nghị tương ứng (XANH: home care; VÀNG: theo dõi; "
                "ĐỎ: đi khám ngay)\n"
                '  - dòng cuối phải là: "⚠️ Tôi không thể thay thế bác sĩ."\n\n'
                f"RAG_CONTEXT:\n{context}\n"
                f"EVIDENCE: {evidence_json}\n"
                f"STATE_SUMMARY: {state_summary}"
            )

        return (
            "Bạn là MediSign AI, trợ lý y tế tiếng Việt. Hãy ghi nhận triệu chứng, "
            "không kết luận chắc chắn và chuẩn bị hỏi tiếp theo kiểu OARS.\n\n"
            f"RAG_CONTEXT:\n{context}\n"
            f"STATE_SUMMARY: {state_summary}"
        )

    async def humanize_question(
        self,
        discriminative_question: DiscriminativeQuestion,
        state: DiagnosticState,
        *,
        rag_hits: list[RAGHit] | None = None,
    ) -> str:
        prompt = self.system_prompt(
            "questioning",
            state,
            rag_hits=rag_hits,
            discriminative_question=discriminative_question,
        )
        user_prompt = (
            "Viết một phản hồi OARS bằng tiếng Việt. Phản hồi phải ghi nhận người dùng, "
            f"nhắc đến triệu chứng cần hỏi là {discriminative_question.symptom!r}, "
            "và kết thúc bằng đúng một câu hỏi."
        )

        try:
            text = (await self._call_llm(prompt, user_prompt)).strip()
        except Exception:
            text = ""

        if self._valid_question_text(text, discriminative_question, state):
            return text
        return self._fallback_question(discriminative_question, state)

    async def humanize_conclusion(
        self,
        evidence: ConclusionEvidence,
        state: DiagnosticState,
        *,
        rag_hits: list[RAGHit] | None = None,
    ) -> str:
        prompt = self.system_prompt("conclusion", state, rag_hits=rag_hits, evidence=evidence)
        user_prompt = "Tạo phần kết luận theo đúng định dạng bắt buộc từ evidence và state."
        return await self._call_llm(prompt, user_prompt)

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        if self._llm_caller is not None:
            return await self._llm_caller(system_prompt, user_prompt)
        if settings.ai_provider not in {"openai_compatible", "medgemma_server"}:
            raise RuntimeError("MedGemma runtime is not configured")

        body: dict[str, Any] = {
            "model": settings.ai_medical_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 512,
        }
        headers = {"Content-Type": "application/json"}
        if settings.ai_api_key:
            headers["Authorization"] = f"Bearer {settings.ai_api_key}"

        async with httpx.AsyncClient(timeout=settings.ai_request_timeout_seconds) as client:
            response = await client.post(
                f"{settings.ai_base_url.rstrip('/')}/chat/completions",
                json=body,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return str(data["choices"][0]["message"]["content"]).strip()

    def _valid_question_text(
        self,
        text: str,
        question: DiscriminativeQuestion,
        state: DiagnosticState,
    ) -> bool:
        if not text or not text.endswith("?"):
            return False
        if text.count("?") != 1:
            return False
        if "Kết luận:" in text:
            return False
        if question.symptom and question.symptom not in text:
            return False
        if state.symptoms_collected:
            return any(symptom in text for symptom in state.symptoms_collected)

        last_user_message = str(question.metadata.get("last_user_message") or "").strip()
        if last_user_message:
            return last_user_message in text
        return True

    def _fallback_question(
        self,
        question: DiscriminativeQuestion,
        state: DiagnosticState,
    ) -> str:
        known_reference = self._known_reference(question, state)
        symptom = question.symptom.strip() or "triệu chứng này"
        return (
            f"Mình ghi nhận {known_reference}. Để hiểu rõ hơn và phân biệt các khả năng, "
            f"bạn có thể chia sẻ thêm về {symptom} không?"
        )

    def _known_reference(
        self,
        question: DiscriminativeQuestion,
        state: DiagnosticState,
    ) -> str:
        for symptom in state.symptoms_collected:
            if symptom.strip():
                return symptom.strip()

        last_user_message = str(question.metadata.get("last_user_message") or "").strip()
        if last_user_message:
            return last_user_message

        if question.question.strip():
            return question.question.strip().rstrip("?")
        return "thông tin bạn vừa chia sẻ"

    def _state_summary(self, state: DiagnosticState) -> str:
        top_3 = [
            {"name": disease.name, "probability": disease.probability}
            for disease in state.diseases_ranked[:3]
        ]
        return self._json(
            {
                "symptoms_collected": state.symptoms_collected,
                "top_3_diseases": top_3,
                "phase": state.phase,
                "turn_count": state.turn_count,
            }
        )

    def _json(self, value: Any) -> str:
        if value is None:
            return "{}"
        if hasattr(value, "model_dump"):
            value = value.model_dump(mode="json")
        elif hasattr(value, "dict"):
            value = value.dict()
        return json.dumps(value, ensure_ascii=False, default=str)


oars_prompt_layer = OARSPromptLayer()
