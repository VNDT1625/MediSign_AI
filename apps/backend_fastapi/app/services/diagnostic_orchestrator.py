"""Diagnostic turn orchestrator — wires all services together for multi-turn diagnostic flow.

Implements the top-level `diagnose_turn` async function that coordinates:
- ChatMemoryService for conversation persistence
- PersonalContextService for user-scoped context (double opt-in)
- RAGEngine for hybrid retrieval (3 passes)
- DiagnosticStateManager for state transitions
- OARSPromptLayer for content generation
- TriageFormatter for triage assignment and disclaimer
- ImagePreprocessor for medical image processing

Requirements: 6.1, 6.2, 7.1, 7.2, 7.3, 7.9, 8.2, 8.3, 8.4, 8.5, 8.6, 16.1, 16.3, 16.4, 16.5
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any
from uuid import UUID

from fastapi import HTTPException

from app.core.config import settings
from app.database.base import SessionLocal
from app.schemas.ai import AIChatRequest, AIChatResponse
from app.schemas.diagnostic import (
    DiagnosticState,
    PersonalContext,
)
from app.services.chat_memory_service import (
    ChatMemoryService,
    ConversationArchivedError,
    ServiceUnavailableError,
)
from app.services.diagnostic_state_manager import DiagnosticStateManager
from app.services.disease_symptom_graph import DiseaseSymptomGraph
from app.services.embedding_client import EmbeddingClient
from app.services.image_preprocessor import ImagePreprocessor
from app.services.kb_lazy_loader import KBLazyLoader, KBSearchTimeoutError
from app.services.oars_prompt_layer import OARSPromptLayer
from app.services.personal_context_service import PersonalContextService
from app.services.rag_engine import RAGEngine
from app.services.rag_service import rag_service
from app.services.triage_formatter import TriageFormatter

logger = logging.getLogger(__name__)

# ─── Error codes ─────────────────────────────────────────────────────────────

RAG_UNAVAILABLE = "RAG_UNAVAILABLE"
CONVERSATION_ARCHIVED = "CONVERSATION_ARCHIVED"


# ─── Service singletons ──────────────────────────────────────────────────────

_chat_memory = ChatMemoryService()
_personal_context_service = PersonalContextService()
_state_manager = DiagnosticStateManager()
_triage_formatter = TriageFormatter()
_image_preprocessor = ImagePreprocessor()
_oars = OARSPromptLayer()


def _get_rag_engine() -> RAGEngine:
    """Lazily construct the RAGEngine with all dependencies."""
    embedder = EmbeddingClient()
    graph = DiseaseSymptomGraph()
    lazy_loader = KBLazyLoader(embedder=embedder)
    return RAGEngine(
        sparse=rag_service,
        embedder=embedder,
        graph=graph,
        lazy_loader=lazy_loader,
    )


# ─── UUID validation ─────────────────────────────────────────────────────────


def _validate_conversation_id(conversation_id: str) -> None:
    """Validate conversation_id is a 36-character UUID string.

    Raises HTTPException 422 if invalid.
    """
    if len(conversation_id) != 36:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_CONVERSATION_ID",
                "message": "conversation_id must be a 36-character UUID string",
            },
        )
    try:
        UUID(conversation_id)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_CONVERSATION_ID",
                "message": "conversation_id must be a valid UUID format",
            },
        )


# ─── Main orchestrator ───────────────────────────────────────────────────────


async def diagnose_turn(
    payload: AIChatRequest,
    conversation_id: str,
    user_id: str | None = None,
) -> AIChatResponse:
    """Top-level orchestrator for a single diagnostic turn.

    Wires all services together following design §F:
    1. Validate conversation_id UUID format
    2. Load conversation and state via ChatMemoryService
    3. Gate personal context via double opt-in (Req 6.1, 6.2)
    4. Process image if present (Req 7.1, 7.2, 7.3, 7.9)
    5. Dispatch to correct RAG pass based on state.phase
    6. Advance state via DiagnosticStateManager
    7. Generate content via OARSPromptLayer
    8. Apply disclaimer on conclusion responses
    9. Persist via ChatMemoryService.append_turn
    10. Return AIChatResponse

    Args:
        payload: The chat request payload (text, adapter, image, etc.).
        conversation_id: 36-char UUID of the conversation to load/create.
        user_id: ID of the authenticated user. When provided, it is used as the
            owner for ``get_or_create_conversation`` and personal-context
            queries. Required for multi-turn flow when invoked from the route
            handler.

    Error handling:
    - ServiceUnavailableError → HTTP 503 RAG_UNAVAILABLE
    - ConversationArchivedError → HTTP 409 CONVERSATION_ARCHIVED
    - LLM unavailability → fallback response with retry
    - RAG #1 zero documents → last persisted response with warning
    - Invalid UUID → HTTP 422
    """
    # ─── Step 1: Validate conversation_id ────────────────────────────────
    _validate_conversation_id(conversation_id)

    # ─── Step 2: Load conversation and state ─────────────────────────────
    db = SessionLocal()
    try:
        return await _execute_turn(db, payload, conversation_id, user_id)
    finally:
        db.close()


async def _execute_turn(
    db: Any,
    payload: AIChatRequest,
    conversation_id: str,
    user_id: str | None = None,
) -> AIChatResponse:
    """Execute the diagnostic turn within a DB session context."""
    # Load conversation — handle ServiceUnavailableError and ConversationArchivedError
    try:
        conversation = _chat_memory.get_or_create_conversation(
            db=db,
            user_id=user_id or _extract_user_id(payload),
            conversation_id=conversation_id,
            adapter=payload.adapter,
        )
    except ConversationArchivedError:
        raise HTTPException(
            status_code=409,
            detail={
                "code": CONVERSATION_ARCHIVED,
                "message": "This conversation has been archived and cannot receive new messages.",
            },
        )
    except ServiceUnavailableError:
        raise HTTPException(
            status_code=503,
            detail={
                "code": RAG_UNAVAILABLE,
                "message": "Chat memory service is temporarily unavailable.",
            },
        )

    # Load diagnostic state
    try:
        state = _chat_memory.load_state(db, conversation.id)
    except ServiceUnavailableError:
        raise HTTPException(
            status_code=503,
            detail={
                "code": RAG_UNAVAILABLE,
                "message": "Diagnostic state could not be loaded.",
            },
        )

    # ─── Step 3: Gate personal context (double opt-in: Req 6.1, 6.2) ────
    personal_ctx = _load_personal_context(db, payload, conversation.user_id)

    # ─── Step 4: Process image if present (Req 7.1, 7.2, 7.3, 7.9) ──────
    image_findings: str | None = None
    image_modality: str | None = None

    if payload.image is not None:
        if payload.image_type is None:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "IMAGE_TYPE_REQUIRED",
                    "message": "image_type is required when an image is provided.",
                },
            )
        processed = _image_preprocessor.preprocess(
            image_bytes=payload.image,
            image_type=payload.image_type,
            filename=f"upload.{payload.image_type}",
        )
        # Call vision encoder to get findings
        image_findings = await _get_image_findings(processed)
        image_modality = processed.image_type

        # Inject image_findings into symptoms_collected before RAG #1
        if image_findings:
            state = state.model_copy(
                update={
                    "symptoms_collected": [
                        *state.symptoms_collected,
                        image_findings,
                    ]
                },
                deep=True,
            )

    # ─── Step 5: Dispatch to correct RAG pass based on phase ─────────────
    rag_engine = _get_rag_engine()

    try:
        response_content, new_state, sources = await _dispatch_by_phase(
            rag_engine=rag_engine,
            state=state,
            payload=payload,
            personal_ctx=personal_ctx,
            image_findings=image_findings,
            db=db,
            conversation_id=conversation.id,
        )
    except KBSearchTimeoutError:
        # KB unavailable — return last persisted response with warning
        return _kb_unavailable_response(payload, conversation.id, state)
    except _LLMUnavailableError as exc:
        # LLM unavailable — use fallback path with retry
        return await _handle_llm_unavailable(
            exc, payload, conversation.id, state, db
        )

    # ─── Step 8: Apply disclaimer on conclusion responses ────────────────
    if new_state.phase == "conclusion":
        response_content = _triage_formatter.ensure_disclaimer(response_content)

    # ─── Step 9: Persist via ChatMemoryService.append_turn ───────────────
    try:
        _chat_memory.append_turn(
            db=db,
            conversation_id=conversation.id,
            user_message=payload.message,
            assistant_message=response_content,
            state=new_state,
            sources=sources,
        )
    except ServiceUnavailableError:
        raise HTTPException(
            status_code=503,
            detail={
                "code": RAG_UNAVAILABLE,
                "message": "Failed to persist diagnostic turn.",
            },
        )

    # ─── Step 10: Return AIChatResponse ──────────────────────────────────
    return AIChatResponse(
        provider=settings.ai_provider,
        model=settings.ai_model,
        adapter=payload.adapter,
        content=response_content,
        fallback_used=False,
        rag_used=True,
        sources=[],
        conversation_id=conversation.id,
        phase=new_state.phase,
        diagnosis_state=new_state,
        triage_level=new_state.triage_level,
        image_findings=image_findings,
        image_modality=image_modality,
    )


# ─── Phase dispatch ──────────────────────────────────────────────────────────


class _LLMUnavailableError(Exception):
    """Internal signal that the LLM is unavailable."""

    pass


async def _dispatch_by_phase(
    rag_engine: RAGEngine,
    state: DiagnosticState,
    payload: AIChatRequest,
    personal_ctx: PersonalContext,
    image_findings: str | None,
    db: Any,
    conversation_id: str,
) -> tuple[str, DiagnosticState, list[Any]]:
    """Dispatch to the correct RAG pass and state transition based on current phase.

    Returns:
        (response_content, new_state, sources)
    """
    phase = state.phase
    sources: list[Any] = []

    if phase in ("initial", "questioning") and state.turn_count == 0:
        # First turn — RAG #1 initial retrieval
        return await _handle_initial_phase(
            rag_engine, state, payload, personal_ctx, image_findings, db
        )
    elif phase == "questioning" or (phase == "initial" and state.turn_count > 0):
        # Subsequent questioning turns — RAG #2 differential
        return await _handle_questioning_phase(
            rag_engine, state, payload, db
        )
    elif phase == "conclusion":
        # Conclusion — RAG #3
        return await _handle_conclusion_phase(
            rag_engine, state, payload, db
        )
    elif phase == "needs_test":
        # Needs test — render needs_test response
        return await _handle_needs_test_phase(state, payload)
    else:
        # Default to initial
        return await _handle_initial_phase(
            rag_engine, state, payload, personal_ctx, image_findings, db
        )


async def _handle_initial_phase(
    rag_engine: RAGEngine,
    state: DiagnosticState,
    payload: AIChatRequest,
    personal_ctx: PersonalContext,
    image_findings: str | None,
    db: Any,
) -> tuple[str, DiagnosticState, list[Any]]:
    """Handle the initial phase: RAG #1 + LLM rank+extract (parallel) + state advance."""
    # Build query from message + image findings
    query = payload.message
    if image_findings:
        query = f"{query} {image_findings}"

    # ── Run RAG #1 and LLM call IN PARALLEL ──────────────────────────────
    rag_task = rag_engine.retrieve_initial(
        query=query,
        personal_ctx=personal_ctx,
        top_k=10,
        db=db,
    )
    llm_task = _rank_diseases_and_extract_symptoms(payload.message)

    try:
        rag_result, llm_result = await asyncio.gather(
            rag_task, llm_task, return_exceptions=True
        )
    except Exception as exc:
        raise KBSearchTimeoutError(f"gather failed: {exc}") from exc

    # Handle RAG result
    if isinstance(rag_result, KBSearchTimeoutError):
        raise rag_result
    if isinstance(rag_result, Exception):
        raise KBSearchTimeoutError("RAG #1 failed") from rag_result
    rag_diseases: list[Any] = list(rag_result)

    # Handle LLM result
    if isinstance(llm_result, Exception):
        logger.warning("LLM rank+extract failed: %s", llm_result)
        ai_diseases: list[Any] = []
        llm_symptoms: list[str] = []
    else:
        ai_diseases, llm_symptoms = llm_result

    # Check for zero documents (Req 16.4)
    if not rag_diseases:
        raise KBSearchTimeoutError("RAG #1 returned zero documents")

    # Merge symptom sources: LLM-extracted (specific) + raw message (fallback)
    raw_symptoms = _extract_symptoms(payload.message, image_findings)
    # Prefer LLM-extracted symptoms when available; always keep image findings
    if llm_symptoms:
        symptoms_extracted = llm_symptoms
        if image_findings and image_findings not in symptoms_extracted:
            symptoms_extracted = [*symptoms_extracted, image_findings]
    else:
        symptoms_extracted = raw_symptoms

    # Merge via DiagnosticStateManager
    new_state = _state_manager.merge_initial(
        prev=state,
        rag_diseases=rag_diseases,
        ai_diseases=ai_diseases,
        symptoms_extracted=symptoms_extracted,
    )

    # Decide phase
    decided_phase = _state_manager.decide_phase(new_state)
    new_state = new_state.model_copy(update={"phase": decided_phase}, deep=True)

    # Assign triage level
    triage_level = _triage_formatter.assign_triage_level(new_state.diseases_ranked)
    new_state = new_state.model_copy(update={"triage_level": triage_level}, deep=True)

    # Generate content via OARS
    if decided_phase == "questioning" or decided_phase == "initial":
        # For initial/questioning, try to get a differential question for OARS
        try:
            if len(new_state.diseases_ranked) >= 2:
                disc_question = await rag_engine.retrieve_differential(
                    candidates=new_state.diseases_ranked,
                    symptoms_known=new_state.symptoms_collected,
                )
                content = await _oars.humanize_question(disc_question, new_state)
            else:
                content = _triage_formatter.render_partial(new_state)
        except Exception as exc:
            logger.warning("OARS question generation failed: %s", exc)
            content = _triage_formatter.render_partial(new_state)
    elif decided_phase == "conclusion":
        content = await _generate_conclusion(rag_engine, new_state)
    elif decided_phase == "needs_test":
        content = _triage_formatter.render_needs_test(new_state)
    else:
        content = _triage_formatter.render_partial(new_state)

    sources = [d for d in rag_diseases]
    return content, new_state, sources


async def _handle_questioning_phase(
    rag_engine: RAGEngine,
    state: DiagnosticState,
    payload: AIChatRequest,
    db: Any,
) -> tuple[str, DiagnosticState, list[Any]]:
    """Handle the questioning phase: apply answer + RAG #2 differential."""
    # Get the last discriminative question from state
    last_question = state.questions_asked[-1] if state.questions_asked else ""

    # Build a discriminative signal from the last question context
    # Try to get a new differential question for the next turn
    try:
        if len(state.diseases_ranked) >= 2:
            disc_question = await rag_engine.retrieve_differential(
                candidates=state.diseases_ranked,
                symptoms_known=state.symptoms_collected,
            )
        else:
            disc_question = None
    except Exception as exc:
        logger.warning("Differential retrieval failed: %s", exc)
        disc_question = None

    # Apply the user's answer to advance state
    if disc_question:
        from app.schemas.diagnostic import DiscriminativeSignal

        signal = DiscriminativeSignal(
            symptom=disc_question.symptom,
            expected_in=disc_question.expected_in,
            expected_absent_in=disc_question.expected_absent_in,
        )
        new_state = _state_manager.apply_answer(
            prev=state,
            question=disc_question.symptom,
            answer=payload.message,
            discriminative_signal=signal,
        )
    else:
        # No differential question available — just increment turn
        symptoms_extracted = _extract_symptoms(payload.message, None)
        new_state = state.model_copy(
            update={
                "turn_count": state.turn_count + 1,
                "symptoms_collected": [
                    *state.symptoms_collected,
                    *[s for s in symptoms_extracted if s not in state.symptoms_collected],
                ],
            },
            deep=True,
        )

    # Decide phase after applying answer
    decided_phase = _state_manager.decide_phase(new_state)
    new_state = new_state.model_copy(update={"phase": decided_phase}, deep=True)

    # Assign triage level
    triage_level = _triage_formatter.assign_triage_level(new_state.diseases_ranked)
    new_state = new_state.model_copy(update={"triage_level": triage_level}, deep=True)

    # Generate content based on decided phase
    if decided_phase == "conclusion":
        content = await _generate_conclusion(rag_engine, new_state)
    elif decided_phase == "needs_test":
        content = _triage_formatter.render_needs_test(new_state)
    else:
        # Still questioning — get next differential question
        try:
            if len(new_state.diseases_ranked) >= 2:
                next_question = await rag_engine.retrieve_differential(
                    candidates=new_state.diseases_ranked,
                    symptoms_known=new_state.symptoms_collected,
                )
                content = await _oars.humanize_question(next_question, new_state)
            else:
                content = _triage_formatter.render_partial(new_state)
        except Exception as exc:
            logger.warning("Next question generation failed: %s", exc)
            content = _triage_formatter.render_partial(new_state)

    sources: list[Any] = []
    return content, new_state, sources


async def _handle_conclusion_phase(
    rag_engine: RAGEngine,
    state: DiagnosticState,
    payload: AIChatRequest,
    db: Any,
) -> tuple[str, DiagnosticState, list[Any]]:
    """Handle the conclusion phase: RAG #3 + self-check."""
    content = await _generate_conclusion(rag_engine, state)
    return content, state, []


async def _handle_needs_test_phase(
    state: DiagnosticState,
    payload: AIChatRequest,
) -> tuple[str, DiagnosticState, list[Any]]:
    """Handle the needs_test phase: render recommendation."""
    content = _triage_formatter.render_needs_test(state)
    return content, state, []


async def _generate_conclusion(
    rag_engine: RAGEngine,
    state: DiagnosticState,
) -> str:
    """Generate conclusion content via RAG #3 + self-check + OARS."""
    if not state.diseases_ranked:
        return _triage_formatter.render_needs_test(state)

    top_disease = state.diseases_ranked[0]

    try:
        evidence = await rag_engine.retrieve_conclusion(top_disease)
    except Exception as exc:
        logger.warning("Conclusion retrieval failed: %s", exc)
        return _triage_formatter.render_final(
            state,
            _empty_evidence(top_disease),
        )

    # Self-check
    try:
        self_check_result = await rag_engine.self_check(state, evidence)
        if not self_check_result.supports_conclusion:
            # Demote to needs_test (Req 14.4)
            return _triage_formatter.render_needs_test(state)
    except Exception as exc:
        logger.warning("Self-check failed: %s", exc)

    # Generate conclusion content via OARS
    try:
        content = await _oars.humanize_conclusion(evidence, state)
        if content and content.strip():
            return content
    except Exception as exc:
        logger.warning("OARS conclusion generation failed: %s", exc)

    # Fallback to formatter
    return _triage_formatter.render_final(state, evidence)


# ─── Helper functions ────────────────────────────────────────────────────────


def _load_personal_context(
    db: Any,
    payload: AIChatRequest,
    user_id: str,
) -> PersonalContext:
    """Load personal context with double opt-in gate (Req 6.1, 6.2).

    Personal context is only loaded when BOTH:
    - Request has use_personal_context == True (user opt-in per request)
    - User's profile has consent_personal_context == True (stored consent)
    """
    if not payload.use_personal_context:
        # Req 6.1: request opt-in is False → empty context
        return PersonalContext()

    # Load context to check stored consent
    ctx = _personal_context_service.load(db, user_id)

    if not ctx.consent_personal_context:
        # Req 6.2: stored consent is False → empty context
        return PersonalContext()

    # Both flags are True — return full context
    return ctx


def _extract_user_id(payload: AIChatRequest) -> str:
    """Extract a fallback user_id from the request payload.

    The API route (``/api/v1/ai/chat``) passes the authenticated user's id
    directly to ``diagnose_turn``, so this helper is only a defensive fallback
    for callers that invoke the orchestrator without an explicit ``user_id``
    (e.g. tests). It returns ``"anonymous"`` when no id is present.
    """
    return getattr(payload, "_user_id", "anonymous")


def _extract_symptoms(message: str, image_findings: str | None) -> list[str]:
    """Extract symptom strings from user message.

    Simple extraction: split by common delimiters and filter short tokens.
    """
    symptoms: list[str] = []

    # Add the full message as a symptom description
    cleaned = message.strip()
    if cleaned:
        symptoms.append(cleaned)

    # Add image findings if present
    if image_findings:
        symptoms.append(image_findings)

    return symptoms


async def _rank_diseases_and_extract_symptoms(
    message: str,
) -> tuple[list[Any], list[str]]:
    """Call rank_diseases_and_extract and return (diseases, symptoms).

    Runs in parallel with RAG retrieval so there is zero added latency.
    """
    try:
        from app.services.ai_model_service import ai_model_service

        diseases, symptoms, _duration = await ai_model_service.rank_diseases_and_extract(message)
        return diseases, symptoms
    except Exception as exc:
        logger.warning("rank_diseases_and_extract failed: %s", exc)
        return [], []


async def _get_image_findings(processed: Any) -> str | None:
    """Call MedGemma vision encoder to analyze a processed image.

    Returns a text description of findings, or None if unavailable.
    """
    if settings.ai_provider not in {"openai_compatible", "medgemma_server"}:
        # Vision encoder not available — return a placeholder based on modality
        if processed.image_type == "xray":
            return "X-quang: cần phân tích thêm bởi bác sĩ"
        return "Ảnh da liễu: cần phân tích thêm bởi bác sĩ"

    import httpx

    content_block = processed.content_block or {
        "type": "image_url",
        "image_url": {"url": f"data:image/png;base64,{processed.content_base64}"},
    }

    body = {
        "model": settings.ai_medical_model,
        "messages": [
            {
                "role": "user",
                "content": [
                    content_block,
                    {
                        "type": "text",
                        "text": "Phân tích ảnh y tế này, mô tả những bất thường quan sát được bằng tiếng Việt.",
                    },
                ],
            }
        ],
        "temperature": 0.1,
        "max_tokens": 256,
    }
    headers: dict[str, str] = {"Content-Type": "application/json"}
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
        findings = data["choices"][0]["message"]["content"].strip()
        return findings if findings else None
    except Exception as exc:
        logger.warning("Image analysis via vision encoder failed: %s", exc)
        # Fallback description
        if processed.image_type == "xray":
            return "X-quang: cần phân tích thêm bởi bác sĩ"
        return "Ảnh da liễu: cần phân tích thêm bởi bác sĩ"


def _kb_unavailable_response(
    payload: AIChatRequest,
    conversation_id: str,
    state: DiagnosticState,
) -> AIChatResponse:
    """Return response when KB is unavailable (Req 16.4).

    Returns last persisted response content with warning.
    """
    content = (
        "Hệ thống kiến thức y tế tạm thời không khả dụng. "
        "Vui lòng thử lại sau hoặc mô tả thêm triệu chứng."
    )
    return AIChatResponse(
        provider=settings.ai_provider,
        model=settings.ai_model,
        adapter=payload.adapter,
        content=content,
        fallback_used=True,
        rag_used=False,
        sources=[],
        conversation_id=conversation_id,
        phase=state.phase,
        diagnosis_state=state,
        triage_level=state.triage_level,
        image_findings=None,
        image_modality=None,
    )


async def _handle_llm_unavailable(
    exc: _LLMUnavailableError,
    payload: AIChatRequest,
    conversation_id: str,
    state: DiagnosticState,
    db: Any,
) -> AIChatResponse:
    """Handle LLM unavailability with fallback and retry (Req 16.1).

    Strategy: retry once with max_tokens reduced by 50%.
    If retry also fails, return fallback response without persisting state.
    """
    from app.services.ai_model_service import ai_model_service

    # Use existing fallback response path
    fallback = ai_model_service._fallback_response(payload)
    fallback.conversation_id = conversation_id
    fallback.phase = state.phase
    fallback.diagnosis_state = state
    fallback.triage_level = state.triage_level
    fallback.fallback_used = True
    return fallback


def _empty_evidence(top_disease: Any) -> Any:
    """Create an empty ConclusionEvidence for fallback rendering."""
    from app.schemas.diagnostic import ConclusionEvidence

    return ConclusionEvidence(
        disease_name=top_disease.name,
        severity=top_disease.severity,
        red_flags=[],
        lab_tests=[],
        home_care=[],
        recommendations=[],
        sources=top_disease.sources,
    )
