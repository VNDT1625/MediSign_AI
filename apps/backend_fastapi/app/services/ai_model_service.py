from __future__ import annotations

from pathlib import Path
from typing import Any
import re
import unicodedata

import httpx

from app.core.config import settings
from app.schemas.ai import AIChatRequest, AIChatResponse, AIStatusResponse, RAGSource
from app.services.rag_service import RAGHit, rag_service


MEDICAL_SYSTEM_PROMPT = (
    "Bạn là MediSign AI, trợ lý y tế tiếng Việt. "
    "QUAN TRỌNG: Luôn trả lời bằng tiếng Việt. "
    "Tuyệt đối KHÔNG dịch câu hỏi sang tiếng Anh hay ngôn ngữ khác. "
    "Chỉ đưa gợi ý sơ bộ, không chẩn đoán chắc chắn, "
    "luôn khuyên gặp bác sĩ khi có dấu hiệu nặng."
)

PSYCHOLOGY_SYSTEM_PROMPT = (
    "Bạn là MediSign SoulGarden, trợ lý hỗ trợ tinh thần bằng tiếng Việt. "
    "Phản hồi nhẹ nhàng, không chẩn đoán bệnh tâm thần, khuyến khích tìm "
    "chuyên gia khi có nguy cơ tự hại hoặc khủng hoảng."
)


class AIModelService:
    """Thin client for the model runtime.

    FastAPI stays lightweight. MedGemma 4B plus LoRA adapters should run in a
    separate GPU process exposed as an OpenAI-compatible `/v1/chat/completions`
    endpoint by vLLM, TGI, or a small custom server.
    """

    def status(self) -> AIStatusResponse:
        medical_path = Path(settings.medgemma_medical_adapter_path)
        psychology_path = Path(settings.medgemma_psychology_adapter_path)
        provider_ready = settings.ai_provider in {"openai_compatible", "medgemma_server"}

        details = [
            "AI provider configured" if provider_ready else "Using rule-based/mock fallback",
            (
                "medical adapter present"
                if medical_path.exists()
                else "medical adapter not found locally"
            ),
            (
                "psychology adapter present"
                if psychology_path.exists()
                else "psychology adapter not found locally"
            ),
        ]

        return AIStatusResponse(
            provider=settings.ai_provider,
            model=settings.ai_model,
            base_url=settings.ai_base_url,
            medical_adapter_path=str(medical_path),
            psychology_adapter_path=str(psychology_path),
            ready=provider_ready,
            detail="; ".join(details),
            rag=rag_service.status(),
        )

    async def chat(self, payload: AIChatRequest) -> AIChatResponse:
        if self._is_greeting(payload.message):
            return AIChatResponse(
                provider=settings.ai_provider,
                model=settings.ai_model,
                adapter=payload.adapter,
                content=(
                    "Xin chào, mình là MediSign AI. Bạn có thể mô tả triệu chứng, "
                    "thuốc đang dùng, độ tuổi, giới tính, bệnh nền hoặc dị ứng thuốc "
                    "để mình hỗ trợ tra cứu và gợi ý bước tiếp theo an toàn hơn."
                ),
                fallback_used=False,
                rag_used=False,
                sources=[],
            )

        if not self._needs_medical_ai(payload.message, payload.adapter):
            return AIChatResponse(
                provider=settings.ai_provider,
                model=settings.ai_model,
                adapter=payload.adapter,
                content=(
                    "Mình hiểu. Nội dung này chưa đủ rõ là vấn đề y tế cần tra cứu. "
                    "Nếu bạn chỉ đang đói, hãy ăn nhẹ và uống nước; nếu đói kèm run tay, "
                    "vã mồ hôi, chóng mặt, đau bụng, buồn nôn, bệnh nền hoặc đang dùng thuốc, "
                    "hãy mô tả thêm để mình hỗ trợ an toàn hơn."
                ),
                fallback_used=False,
                rag_used=False,
                sources=[],
            )

        rag_hits = (
            rag_service.search(
                payload.message,
                top_k=payload.rag_top_k,
                adapter=payload.adapter,
            )
            if payload.use_rag
            else []
        )
        rag_hits = self._filter_rag_hits(payload.message, rag_hits)

        if settings.ai_provider not in {"openai_compatible", "medgemma_server"}:
            return self._fallback_response(payload, rag_hits)

        try:
            content = await self._call_openai_compatible(payload, rag_hits)
        except Exception:
            return self._fallback_response(payload, rag_hits)

        if self._is_bad_model_response(content):
            return self._safe_clarifying_response(payload)
        content = self._clean_model_content(content)

        return AIChatResponse(
            provider=settings.ai_provider,
            model=settings.ai_model,
            adapter=payload.adapter,
            content=content,
            fallback_used=False,
            rag_used=bool(rag_hits),
            sources=self._rag_sources(rag_hits),
        )

    async def _call_openai_compatible(self, payload: AIChatRequest, rag_hits: list[RAGHit]) -> str:
        system_prompt = self._compose_system_prompt(payload, rag_hits)
        body: dict[str, Any] = {
            "model": self._model_for_adapter(payload.adapter),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": payload.message},
            ],
            "temperature": 0.2,
            "max_tokens": 1024,
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

        return data["choices"][0]["message"]["content"]

    def _fallback_response(
        self, payload: AIChatRequest, rag_hits: list[RAGHit] | None = None
    ) -> AIChatResponse:
        rag_hits = rag_hits or []
        if rag_hits:
            content = self._rag_fallback_content(payload, rag_hits)
        elif payload.adapter == "psychology":
            content = (
                "Mình đã ghi nhận chia sẻ của bạn. Đây là phản hồi mẫu khi model "
                "SoulGarden chưa được bật. Nếu bạn đang thấy quá tải hoặc có ý nghĩ "
                "làm hại bản thân, hãy liên hệ người thân hoặc chuyên gia ngay."
            )
        else:
            content = (
                "Đây là phản hồi mẫu khi MedGemma chưa được bật. Vui lòng mô tả rõ "
                "triệu chứng, thời gian xuất hiện và mức độ nặng. Thông tin chỉ mang "
                "tính tham khảo, không thay thế chẩn đoán bác sĩ."
            )

        return AIChatResponse(
            provider=settings.ai_provider,
            model=settings.ai_model,
            adapter=payload.adapter,
            content=content,
            fallback_used=True,
            rag_used=bool(rag_hits),
            sources=self._rag_sources(rag_hits),
        )

    def _safe_clarifying_response(self, payload: AIChatRequest) -> AIChatResponse:
        if payload.adapter == "psychology":
            content = (
                "Mình đã ghi nhận chia sẻ của bạn. Bạn có thể nói rõ hơn cảm xúc chính, "
                "mức độ ảnh hưởng tới ngủ/ăn/làm việc và điều gì làm bạn thấy nặng hơn không? "
                "Nếu có ý nghĩ tự hại hoặc mất an toàn, hãy liên hệ người thân hoặc cấp cứu ngay."
            )
        else:
            content = self._safe_medical_clarifying_content(payload.message)

        return AIChatResponse(
            provider=settings.ai_provider,
            model=settings.ai_model,
            adapter=payload.adapter,
            content=content,
            fallback_used=True,
            rag_used=False,
            sources=[],
        )

    def _safe_medical_clarifying_content(self, message: str) -> str:
        normalized = f" {self._normalize_text(message)} "

        if any(term in normalized for term in (" dau hong ", " viem hong ", " ho ", " nuot vuong ")):
            return (
                "Mình chưa thể kết luận chắc chắn chỉ từ mô tả này. Đau họng, ho khan hoặc nuốt vướng "
                "thường gặp trong viêm họng do virus, cảm cúm, kích ứng họng hoặc viêm amidan. Bạn nên "
                "nghỉ ngơi, uống nước ấm, súc họng nước muối sinh lý và theo dõi 1-2 ngày. Cho mình biết "
                "thêm: bạn bao nhiêu tuổi, có sốt bao nhiêu độ, ho có đờm không, đau một bên họng không, "
                "có khó thở hoặc khó nuốt nước bọt không, và đã dùng thuốc gì chưa. Nếu khó thở, sốt cao "
                "kéo dài, đau họng tăng nhanh, không nuốt được nước bọt hoặc đau lệch một bên cổ, hãy đi khám sớm."
            )

        if any(
            term in normalized
            for term in (" dau bung ", " di tieu ", " tieu chay ", " phan long ", " phan nhao ")
        ):
            return (
                "Mình chưa thể kết luận nguyên nhân chỉ từ mô tả này. Các triệu chứng như đau bụng, "
                "đi tiểu nhiều hoặc đi ngoài phân lỏng có thể liên quan tiêu hóa, tiết niệu, ăn uống, "
                "nhiễm khuẩn hoặc vấn đề chuyển hóa. Bạn cho mình biết thêm: tuổi, giới tính, triệu chứng "
                "bắt đầu từ khi nào, số lần đi ngoài/đi tiểu mỗi ngày, có sốt/nôn/đau khi tiểu/khát nhiều "
                "không, và thuốc đang dùng. Nếu đau bụng dữ dội, sốt cao, mất nước, đi ngoài ra máu, "
                "lơ mơ hoặc tiểu buốt kèm sốt, hãy đi khám sớm."
            )

        if any(term in normalized for term in (" dau dau ", " nhuc dau ", " chong mat ", " nong ")):
            return (
                "Mình chưa thể kết luận chắc chắn chỉ từ mô tả này. Nhức đầu hoặc cảm giác nóng có thể liên quan "
                "thiếu ngủ, căng thẳng, mất nước, sốt, viêm xoang, say nắng hoặc huyết áp. Bạn nên đo nhiệt độ, "
                "uống nước, nghỉ ngơi nơi thoáng mát và theo dõi. Cho mình biết thêm: đau từ khi nào, đau vùng nào, "
                "có sốt/ói/chóng mặt/cứng gáy/yếu tay chân hoặc nhìn mờ không. Nếu đau đầu dữ dội đột ngột, lơ mơ, "
                "yếu liệt, cứng gáy, sốt cao hoặc nôn nhiều, hãy đi khám/cấp cứu ngay."
            )

        return (
            "Mình chưa thể kết luận nguyên nhân chỉ từ mô tả này. Bạn cho mình biết thêm: tuổi, giới tính, "
            "triệu chứng bắt đầu từ khi nào, mức độ nặng, có sốt/đau/khó thở/nôn/tiêu chảy/phát ban không, "
            "thuốc đang dùng, bệnh nền và dị ứng thuốc. Nếu có khó thở, đau ngực, lơ mơ, yếu liệt, sốt cao, "
            "mất nước, chảy máu hoặc triệu chứng tăng nhanh, hãy đi khám/cấp cứu ngay."
        )

    def _compose_system_prompt(self, payload: AIChatRequest, rag_hits: list[RAGHit]) -> str:
        base_prompt = payload.system_prompt or self._default_system_prompt(payload.adapter)
        if not rag_hits:
            return base_prompt

        context = rag_service.build_context(rag_hits)
        return (
            f"{base_prompt}\n\n"
            "Quy tắc RAG bắt buộc:\n"
            "- Chỉ dùng RAG_CONTEXT như tài liệu tham khảo, không bịa nguồn.\n"
            "- Khi trả lời thông tin thuốc, tương tác, dinh dưỡng hoặc bệnh thường gặp, "
            "hãy nêu ngắn gọn nguồn bằng record_id trong ngoặc vuông nếu phù hợp.\n"
            "- Nếu context không đủ, nói rõ cần thêm thông tin hoặc cần hỏi bác sĩ/dược sĩ.\n"
            "- Luôn giữ cảnh báo an toàn: thông tin tham khảo, không thay thế khám trực tiếp.\n\n"
            f"RAG_CONTEXT:\n{context}"
        )

    def _rag_fallback_content(self, payload: AIChatRequest, rag_hits: list[RAGHit]) -> str:
        if not rag_hits:
            return (
                "Mình chưa có đủ thông tin để đánh giá chính xác. Bạn cho mình biết thêm: "
                "tuổi, giới tính, triệu chứng bắt đầu từ khi nào, mức độ nặng, nhiệt độ nếu có, "
                "thuốc đang dùng, bệnh nền và dị ứng thuốc. Nếu có khó thở, đau ngực, lơ mơ, "
                "yếu liệt, sốt cao hoặc triệu chứng tăng nhanh, hãy đi khám/cấp cứu ngay."
            )

        lead = (
            "MediSign đã tra cứu kho kiến thức nội bộ, nhưng model runtime chưa được bật. "
            "Dưới đây là thông tin tham khảo tìm được:"
        )
        bullets = []
        for hit in rag_hits[:3]:
            text = hit.content.strip()
            if len(text) > 420:
                text = f"{text[:417].rstrip()}..."
            bullets.append(f"- [{hit.record_id}] {hit.title}: {text}")

        safety = (
            "Thông tin này không thay thế chẩn đoán hoặc tư vấn trực tiếp. "
            "Nếu có dấu hiệu nặng như khó thở, đau ngực, lơ mơ, chảy máu, "
            "ý nghĩ tự hại hoặc triệu chứng tăng nhanh, hãy gọi cấp cứu 115 hoặc đi khám ngay."
        )
        return "\n".join([lead, *bullets, safety])

    def _rag_sources(self, rag_hits: list[RAGHit]) -> list[RAGSource]:
        return [
            RAGSource(
                record_id=hit.record_id,
                type=hit.type,
                title=hit.title,
                score=hit.score,
                confidence=hit.confidence,
                needs_medical_review=hit.needs_medical_review,
                source=hit.source,
            )
            for hit in rag_hits
        ]

    def _default_system_prompt(self, adapter: str) -> str:
        if adapter == "psychology":
            return PSYCHOLOGY_SYSTEM_PROMPT
        return MEDICAL_SYSTEM_PROMPT

    def _model_for_adapter(self, adapter: str) -> str:
        if adapter == "psychology":
            return settings.ai_psychology_model
        if adapter == "medical":
            return settings.ai_medical_model
        return settings.ai_model

    def _is_greeting(self, message: str) -> bool:
        normalized = self._normalize_text(message)
        compact = re.sub(r"[^a-z0-9 ]+", " ", normalized)
        compact = re.sub(r"\s+", " ", compact).strip()
        greetings = {
            "hi",
            "hello",
            "hey",
            "chao",
            "xin chao",
            "chao ban",
            "alo",
            "alo bac si",
        }
        return compact in greetings

    def _normalize_text(self, value: str) -> str:
        text = unicodedata.normalize("NFD", value.lower())
        text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
        text = text.replace("đ", "d")
        return text.strip()

    def _needs_medical_ai(self, message: str, adapter: str) -> bool:
        if adapter == "psychology":
            return True

        normalized = f" {self._normalize_text(message)} "
        medical_terms = (
            " dau ",
            " nhuc ",
            " dau dau ",
            " nhuc dau ",
            " nong ",
            " nong trong nguoi ",
            " sot ",
            " ho ",
            " met ",
            " non ",
            " buon non ",
            " tieu chay ",
            " kho tho ",
            " dau nguc ",
            " dau bung ",
            " chong mat ",
            " run tay ",
            " va mo hoi ",
            " di ung ",
            " phat ban ",
            " sung ",
            " viem ",
            " nhiem ",
            " thuoc ",
            " uong thuoc ",
            " lieu ",
            " tuong tac ",
            " paracetamol ",
            " ibuprofen ",
            " khang sinh ",
            " vitamin ",
            " canxi ",
            " calcium ",
            " dinh duong ",
            " an gi ",
            " nen an ",
            " tieu duong ",
            " huyet ap ",
            " mang thai ",
            " tre em ",
            " nguoi gia ",
            " benh nen ",
        )
        if any(term in normalized for term in medical_terms):
            return True

        # Longer Vietnamese messages are likely health descriptions even if
        # they do not hit the small keyword set. Short casual messages should
        # not trigger RAG/model because they retrieve noisy medical records.
        return len(normalized.split()) >= 10

    def _filter_rag_hits(self, message: str, hits: list[RAGHit]) -> list[RAGHit]:
        if not hits:
            return []
        if self._mentions_drug_context(message):
            return hits

        filtered = [
            hit
            for hit in hits
            if hit.type
            not in {
                "drug",
                "drug_interaction",
            }
        ]
        return filtered[: len(hits)]

    def _mentions_drug_context(self, message: str) -> bool:
        normalized = f" {self._normalize_text(message)} "
        drug_terms = (
            " thuoc ",
            " vien ",
            " uong ",
            " lieu ",
            " tuong tac ",
            " paracetamol ",
            " ibuprofen ",
            " aspirin ",
            " khang sinh ",
            " vitamin ",
            " canxi ",
            " calcium ",
            " don thuoc ",
        )
        return any(term in normalized for term in drug_terms)

    def _is_bad_model_response(self, content: str) -> bool:
        normalized = self._normalize_text(content)
        bad_markers = (
            "dich sang tieng anh",
            "dich sang tieng viet",
            "dich cau hoi sang tieng anh",
            "dich cau hoi sang tieng viet",
            "ban dich tieng anh",
            "ban dich tieng viet",
            "translate to english",
            "translate to vietnamese",
            "english translation",
            "here is the translation",
            "translated question",
        )
        return any(marker in normalized for marker in bad_markers)

    def _clean_model_content(self, content: str) -> str:
        replacements = {
            "chuyênist": "bác sĩ/chuyên gia y tế",
            "chuyên giaist": "chuyên gia y tế",
        }
        cleaned = content
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        return cleaned.strip()


ai_model_service = AIModelService()
