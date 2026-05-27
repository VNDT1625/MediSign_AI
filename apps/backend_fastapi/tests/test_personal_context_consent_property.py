"""Property test for personal-context consent gate (Property 6).

Validates Requirements 6.1, 6.2, 6.3, 6.4:
- retrieve_initial is called with non-empty PersonalContext if and only if
  BOTH use_personal_context==True AND consent_personal_context==True.
- In all other combinations, retrieve_initial receives an empty PersonalContext().

Task 15.2
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.schemas.ai import AIChatRequest
from app.schemas.diagnostic import (
    DiagnosticState,
    MyMedicineMini,
    PersonalContext,
    RankedDisease,
    UserProfileMini,
)
from app.services.diagnostic_orchestrator import _load_personal_context


# ─── Strategy definitions ────────────────────────────────────────────────────


consent_flags = st.booleans()


def personal_context_with_consent(consent: bool) -> PersonalContext:
    """Build a PersonalContext with the given consent flag and some data."""
    return PersonalContext(
        profile=UserProfileMini(age_range="30-40", gender="male", conditions=["tiểu đường"]),
        medications=[MyMedicineMini(name="Metformin", dosage="500mg")],
        recent_journal_summary="đang dùng kháng sinh amoxicillin 1 tuần",
        consent_personal_context=consent,
    )


# ─── Property test ───────────────────────────────────────────────────────────


class TestPersonalContextConsentGate:
    """Property 6: Personal-Context Consent.

    The orchestrator's _load_personal_context function implements the double
    opt-in gate. We test it directly as a pure function (it only depends on
    the payload flag and the loaded context's consent flag).
    """

    @given(
        use_personal_context=consent_flags,
        stored_consent=consent_flags,
    )
    def test_double_opt_in_gate(
        self,
        use_personal_context: bool,
        stored_consent: bool,
    ) -> None:
        """retrieve_initial gets non-empty PersonalContext iff both flags are True."""
        # Arrange: build a payload with the given use_personal_context flag
        payload = AIChatRequest(
            message="Tôi bị đau đầu",
            adapter="medical",
            use_personal_context=use_personal_context,
        )

        # Build a PersonalContext that the service would return
        loaded_ctx = personal_context_with_consent(stored_consent)

        # Mock the PersonalContextService.load to return our context
        from app.services import diagnostic_orchestrator as orch_module

        mock_service = MagicMock()
        mock_service.load = MagicMock(return_value=loaded_ctx)

        # Patch the module-level service instance
        original_service = orch_module._personal_context_service
        orch_module._personal_context_service = mock_service

        try:
            # Act
            db = MagicMock()
            result = _load_personal_context(db, payload, "user-123")

            # Assert
            if use_personal_context and stored_consent:
                # Both flags True → full context returned
                assert result.consent_personal_context is True
                assert result.profile is not None
                assert len(result.medications) > 0
                assert result.recent_journal_summary is not None
            else:
                # Any flag False → empty context
                assert result.consent_personal_context is False
                assert result.profile is None
                assert result.medications == []
                assert result.recent_journal_summary is None
        finally:
            orch_module._personal_context_service = original_service

    @given(use_personal_context=consent_flags)
    def test_request_opt_in_false_never_calls_load(
        self,
        use_personal_context: bool,
    ) -> None:
        """When use_personal_context is False, PersonalContextService.load is never called."""
        if use_personal_context:
            # Only test the False case here
            return

        payload = AIChatRequest(
            message="Tôi bị sốt",
            adapter="medical",
            use_personal_context=False,
        )

        from app.services import diagnostic_orchestrator as orch_module

        mock_service = MagicMock()
        mock_service.load = MagicMock(return_value=PersonalContext())

        original_service = orch_module._personal_context_service
        orch_module._personal_context_service = mock_service

        try:
            db = MagicMock()
            result = _load_personal_context(db, payload, "user-123")

            # Req 6.1: load is NOT called when use_personal_context is False
            mock_service.load.assert_not_called()
            assert result == PersonalContext()
        finally:
            orch_module._personal_context_service = original_service

    def test_both_true_returns_full_context(self) -> None:
        """Explicit test: both flags True → full PersonalContext passed through."""
        payload = AIChatRequest(
            message="Tôi bị đau bụng",
            adapter="medical",
            use_personal_context=True,
        )

        full_ctx = personal_context_with_consent(consent=True)

        from app.services import diagnostic_orchestrator as orch_module

        mock_service = MagicMock()
        mock_service.load = MagicMock(return_value=full_ctx)

        original_service = orch_module._personal_context_service
        orch_module._personal_context_service = mock_service

        try:
            db = MagicMock()
            result = _load_personal_context(db, payload, "user-123")

            mock_service.load.assert_called_once_with(db, "user-123")
            assert result.consent_personal_context is True
            assert result.profile is not None
            assert result.profile.conditions == ["tiểu đường"]
            assert result.medications[0].name == "Metformin"
        finally:
            orch_module._personal_context_service = original_service

    def test_request_true_stored_false_returns_empty(self) -> None:
        """Explicit test: request True but stored consent False → empty context."""
        payload = AIChatRequest(
            message="Tôi bị ho",
            adapter="medical",
            use_personal_context=True,
        )

        # User has data but consent is False
        ctx_no_consent = personal_context_with_consent(consent=False)

        from app.services import diagnostic_orchestrator as orch_module

        mock_service = MagicMock()
        mock_service.load = MagicMock(return_value=ctx_no_consent)

        original_service = orch_module._personal_context_service
        orch_module._personal_context_service = mock_service

        try:
            db = MagicMock()
            result = _load_personal_context(db, payload, "user-123")

            # Req 6.2: stored consent False → empty context
            mock_service.load.assert_called_once()
            assert result == PersonalContext()
        finally:
            orch_module._personal_context_service = original_service
