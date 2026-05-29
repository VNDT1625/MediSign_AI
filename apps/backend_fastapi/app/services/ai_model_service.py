from __future__ import annotations

import json
import logging
import re
import unicodedata
from pathlib import Path
from typing import Any

import httpx

from app.core.config import settings
from app.schemas.ai import AIChatRequest, AIChatResponse, AIStatusResponse, RAGSource
from app.schemas.diagnostic import ChatPhase, RankedDisease
from app.services.rag_service import RAGHit, rag_service

logger = logging.getLogger(__name__)


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

    async def chat(
        self,
        payload: AIChatRequest,
        conversation_id: str | None = None,
        phase: str | None = None,
    ) -> AIChatResponse:
        """Process a chat request.

        When *conversation_id* is present, delegates to the diagnostic orchestrator
        (``diagnose_turn``) for multi-turn diagnostic flow. Otherwise, preserves the
        existing single-shot code path unchanged.

        Args:
            payload: The chat request payload.
            conversation_id: Optional conversation ID for multi-turn diagnostic mode.
            phase: Optional phase hint (unused in single-shot path).
        """
        # Use conversation_id from payload if not passed explicitly
        effective_conversation_id = conversation_id or payload.conversation_id

        if effective_conversation_id is not None:
            return await self._delegate_to_orchestrator(payload, effective_conversation_id)

        # ─── Existing single-shot path (unchanged) ───────────────────────────
        rag_hits: list[RAGHit] = []
        if payload.use_rag:
            try:
                rag_hits = rag_service.search(
                    payload.message,
                    top_k=payload.rag_top_k,
                    adapter=payload.adapter,
                )
            except Exception:
                rag_hits = []

        if settings.ai_provider not in {"openai_compatible", "medgemma_server"}:
            return self._fallback_response(payload, rag_hits)

        try:
            content = await self._call_openai_compatible(payload, rag_hits)
        except Exception:
            return self._fallback_response(payload, rag_hits)

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

    async def _delegate_to_orchestrator(
        self,
        payload: AIChatRequest,
        conversation_id: str,
    ) -> AIChatResponse:
        """Delegate to the diagnostic orchestrator for multi-turn flow.

        ``diagnose_turn`` lives in ``app.services.diagnostic_orchestrator``. If the
        orchestrator cannot be imported, this method falls back to the single-shot
        path with the conversation_id echoed back in the response.
        """
        try:
            from app.services.diagnostic_orchestrator import diagnose_turn  # noqa: F401

            return await diagnose_turn(payload, conversation_id)
        except ImportError:
            # Defensive fallback only — the orchestrator module is normally
            # importable. If it ever fails to import, degrade to single-shot
            # with conversation_id echoed so callers know multi-turn was requested.
            logger.info(
                "diagnostic_orchestrator not available, falling back to single-shot "
                "for conversation_id=%s",
                conversation_id,
            )
            rag_hits: list[RAGHit] = []
            if payload.use_rag:
                try:
                    rag_hits = rag_service.search(
                        payload.message,
                        top_k=payload.rag_top_k,
                        adapter=payload.adapter,
                    )
                except Exception:
                    rag_hits = []

            if settings.ai_provider not in {"openai_compatible", "medgemma_server"}:
                response = self._fallback_response(payload, rag_hits)
            else:
                try:
                    content = await self._call_openai_compatible(payload, rag_hits)
                    content = self._clean_model_content(content)
                    response = AIChatResponse(
                        provider=settings.ai_provider,
                        model=settings.ai_model,
                        adapter=payload.adapter,
                        content=content,
                        fallback_used=False,
                        rag_used=bool(rag_hits),
                        sources=self._rag_sources(rag_hits),
                    )
                except Exception:
                    response = self._fallback_response(payload, rag_hits)

            # Attach conversation_id to indicate multi-turn was acknowledged
            response.conversation_id = conversation_id
            return response

    async def rank_diseases_and_extract(
        self, message: str
    ) -> tuple[list[RankedDisease], list[str], str | None]:
        """Call MedGemma once to rank diseases AND extract symptoms simultaneously.

        Returns:
            Tuple of (diseases, symptoms, duration):
            - diseases: list of RankedDisease sorted by probability descending
            - symptoms: extracted symptom strings (e.g. ["đau đầu", "sốt nhẹ"])
            - duration: symptom duration string or None (e.g. "3 ngày")

        Returns ([], [], None) if the LLM is unavailable or returns invalid output.
        """
        if settings.ai_provider not in {"openai_compatible", "medgemma_server"}:
            return [], [], None

        system_prompt = (
            "Bạn là bác sĩ AI. Dựa trên mô tả của bệnh nhân, trả về JSON object duy nhất.\n"
            "Format bắt buộc (chỉ JSON, không giải thích):\n"
            '{\n'
            '  "diseases": [\n'
            '    {"name": "Tên bệnh", "probability": 0.XX, "severity": "low|medium|high", "rationale": "Lý do ngắn"}\n'
            '  ],\n'
            '  "symptoms": ["triệu chứng 1", "triệu chứng 2"],\n'
            '  "duration": "thời gian hoặc null"\n'
            '}\n\n'
            "Quy tắc:\n"
            "- diseases: tối đa 5 bệnh, tổng probability ≤ 1.0, sắp xếp giảm dần\n"
            "- severity phải là: low, medium, hoặc high\n"
            "- symptoms: tách thành từng triệu chứng riêng biệt (không gộp câu)\n"
            "- duration: thời gian xuất hiện triệu chứng nếu có, ngược lại null"
        )

        body: dict[str, Any] = {
            "model": settings.ai_medical_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            "temperature": 0.1,
            "max_tokens": 600,
        }
        headers = {"Content-Type": "application/json"}
        if settings.ai_api_key:
            headers["Authorization"] = f"Bearer {settings.ai_api_key}"

        try:
            async with httpx.AsyncClient(timeout=settings.ai_request_timeout_seconds) as client:
                response = await client.post(
                    f"{settings.ai_base_url.rstrip('/')}/chat/completions",
                    json=body,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

            content = data["choices"][0]["message"]["content"]
            return self._parse_rank_and_extract(content)
        except Exception as exc:
            logger.warning("rank_diseases_and_extract LLM call failed: %s", exc)
            return [], [], None

    def _parse_rank_and_extract(
        self, content: str
    ) -> tuple[list[RankedDisease], list[str], str | None]:
        """Parse combined LLM output into diseases + symptoms + duration."""
        text = content.strip()

        # Extract JSON object/array from potential markdown wrapping
        if "```" in text:
            match = re.search(r"```(?:json)?\s*([\[{].*?[\]}])\s*```", text, re.DOTALL)
            if match:
                text = match.group(1)
        if not (text.startswith("{") or text.startswith("[")):
            match = re.search(r"[\[{].*[\]}]", text, re.DOTALL)
            if match:
                text = match.group(0)

        try:
            raw = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            logger.warning("rank_diseases_and_extract: failed to parse JSON from LLM output")
            return [], [], None

        # Accept the legacy shape — a bare JSON array of disease dicts —
        # by treating it as the diseases list with no symptoms/duration.
        if isinstance(raw, list):
            raw = {"diseases": raw, "symptoms": [], "duration": None}

        if not isinstance(raw, dict):
            return [], [], None

        # Parse diseases
        diseases: list[RankedDisease] = []
        for item in raw.get("diseases") or []:
            if not isinstance(item, dict):
                continue
            try:
                disease = RankedDisease(
                    name=str(item.get("name") or "").strip(),
                    probability=float(item.get("probability", 0.0)),
                    severity=item.get("severity", "medium"),
                    rationale=item.get("rationale"),
                    sources=["ai_inferred"],
                )
                diseases.append(disease)
            except (ValueError, TypeError):
                continue
        diseases = sorted(diseases, key=lambda d: d.probability, reverse=True)[:5]

        # Parse symptoms
        raw_symptoms = raw.get("symptoms") or []
        symptoms = [str(s).strip() for s in raw_symptoms if str(s).strip()]

        # Parse duration
        raw_duration = raw.get("duration")
        duration = str(raw_duration).strip() if raw_duration and raw_duration != "null" else None

        return diseases, symptoms, duration

    # Keep backward-compatible alias for any callers that may use rank_diseases directly
    async def rank_diseases(self, message: str) -> list[RankedDisease]:
        """Backward-compatible wrapper — use rank_diseases_and_extract for new code."""
        diseases, _, _ = await self.rank_diseases_and_extract(message)
        return diseases

    def _parse_ranked_diseases(self, content: str) -> list[RankedDisease]:
        """Legacy alias kept for older tests/callers.

        The new implementation uses :meth:`_parse_rank_and_extract` which
        returns ``(diseases, symptoms, duration)``. This wrapper preserves
        the historical signature that returned only the disease list.
        Accepts both the old "JSON array of diseases" shape and the newer
        "JSON object with diseases/symptoms/duration" shape.
        """
        # Old callers passed a JSON array directly. Try parsing that first.
        text = content.strip()
        if "```" in text:
            match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
            if match:
                text = match.group(1)
        if text.lstrip().startswith("["):
            try:
                raw = json.loads(text)
            except (json.JSONDecodeError, ValueError):
                raw = []
            diseases: list[RankedDisease] = []
            for item in raw or []:
                if not isinstance(item, dict):
                    continue
                try:
                    diseases.append(
                        RankedDisease(
                            name=str(item.get("name") or "").strip(),
                            probability=float(item.get("probability", 0.0)),
                            severity=item.get("severity", "medium"),
                            rationale=item.get("rationale"),
                            sources=["ai_inferred"],
                        )
                    )
                except (ValueError, TypeError):
                    continue
            return sorted(diseases, key=lambda d: d.probability, reverse=True)[:5]

        # Fall through to the JSON-object parser.
        diseases, _, _ = self._parse_rank_and_extract(content)
        return diseases

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
            content = self._rule_based_medical_content(payload.message)

        return AIChatResponse(
            provider=settings.ai_provider,
            model=settings.ai_model,
            adapter=payload.adapter,
            content=content,
            fallback_used=True,
            rag_used=bool(rag_hits),
            sources=self._rag_sources(rag_hits),
        )

    def _rule_based_medical_content(self, message: str) -> str:
        normalized = f" {self._normalize_text(message)} "
        urgent_terms = (" kho tho ", " dau nguc ", " ngat ", " co giat ", " lo mo ", " cap cuu ")
        if any(term in normalized for term in urgent_terms):
            return (
                "Dấu hiệu chính: khó thở hoặc triệu chứng nặng. "
                "Ý chính: gọi cấp cứu 115 hoặc đến cơ sở y tế ngay. "
                "Không tự lái xe nếu đang choáng, khó thở hoặc đau ngực."
            )

        advice: list[str] = []
        if " sot " in normalized or " nong " in normalized:
            advice.append("sốt: đo nhiệt độ, uống đủ nước, nghỉ ngơi")
        if " ho " in normalized:
            advice.append("ho: uống nước ấm, theo dõi đờm và mức độ khó thở")
        if " dau dau " in normalized or " nhuc dau " in normalized:
            advice.append("đau đầu: nghỉ nơi yên tĩnh, theo dõi sốt, nôn ói hoặc yếu liệt")
        if " dau bung " in normalized or " bung " in normalized:
            advice.append("đau bụng: theo dõi vị trí đau, nôn, tiêu chảy hoặc sốt")
        if " chong mat " in normalized or " choang " in normalized:
            advice.append("chóng mặt: ngồi hoặc nằm nghỉ, tránh đứng dậy nhanh")

        if not advice:
            advice.append("triệu chứng chưa đủ rõ: cần thêm thời gian xuất hiện, mức độ nặng và bệnh nền")

        return (
            "MediSign AI đã ghi nhận triệu chứng. "
            f"Ý chính: {'; '.join(advice)}. "
            "Nếu triệu chứng nặng lên, sốt cao kéo dài, khó thở, đau ngực, lơ mơ hoặc mất nước, hãy đi khám ngay. "
            "Thông tin này chỉ hỗ trợ ban đầu, không thay thế bác sĩ."
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
        query_tokens = self._topic_tokens(self._normalize_text(message))

        candidates = [
            hit
            for hit in hits
            if not self._is_irrelevant_rag_hit(message, hit, query_tokens)
        ]
        if not candidates:
            return []

        top_score = max(hit.score for hit in candidates)
        filtered = []
        preferred_types = {"vietnam_common_disease", "guideline_chunk", "disease"}
        for hit in hits:
            if hit not in candidates:
                continue
            if hit.score < max(settings.rag_min_score, top_score * 0.55):
                continue
            if hit.type in preferred_types or self._mentions_drug_context(message):
                filtered.append(hit)
                continue
            if self._is_irrelevant_rag_hit(message, hit, query_tokens):
                continue
            filtered.append(hit)

        return filtered[:3]

    def _is_irrelevant_rag_hit(
        self, message: str, hit: RAGHit, query_tokens: set[str]
    ) -> bool:
        normalized_title = self._searchable_text(hit.title)
        normalized_content = self._searchable_text(hit.content[:1200])
        searchable = f" {normalized_title} {normalized_content} "

        if hit.type in {"drug", "drug_interaction"} and not self._mentions_drug_context(message):
            return True

        nutrition_markers = ("dinh duong", "nhu cau", "canxi", "calcium", "vitamin")
        if any(marker in normalized_title for marker in nutrition_markers) and not self._mentions_nutrition_context(message):
            return True

        if "tay chan mieng" in normalized_title and not self._contains_any(
            message, ("tay chan mieng", "phat ban", "mun nuoc", "loet mieng")
        ):
            return True

        if "ebola" in normalized_title and "ebola" not in self._normalize_text(message):
            return True

        if not query_tokens:
            return False

        overlap = sum(1 for token in query_tokens if token in searchable)
        return overlap == 0

    def _searchable_text(self, value: str) -> str:
        normalized = self._normalize_text(value)
        return re.sub(r"[^a-z0-9]+", " ", normalized).strip()

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

    def _mentions_nutrition_context(self, message: str) -> bool:
        return self._contains_any(
            message,
            (
                "dinh duong",
                "an gi",
                "nen an",
                "canxi",
                "calcium",
                "vitamin",
                "sat",
                "kem",
                "protein",
            ),
        )

    def _contains_any(self, message: str, phrases: tuple[str, ...]) -> bool:
        normalized = f" {self._normalize_text(message)} "
        return any(f" {phrase} " in normalized for phrase in phrases)

    def _topic_tokens(self, normalized: str) -> set[str]:
        stopwords = {
            "toi",
            "ban",
            "xin",
            "chao",
            "dang",
            "thi",
            "la",
            "bi",
            "gi",
            "co",
            "khong",
            "nhieu",
            "nen",
            "lam",
            "voi",
            "va",
            "hoac",
            "mot",
            "cac",
            "cho",
            "minh",
        }
        tokens = set(re.findall(r"[a-z0-9]+", normalized))
        return {token for token in tokens if len(token) >= 3 and token not in stopwords}

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
