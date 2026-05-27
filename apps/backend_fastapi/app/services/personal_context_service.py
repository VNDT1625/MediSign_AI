"""PersonalContextService — loads user-scoped personal context for RAG re-ranking.

Enforces mandatory WHERE user_id = :user_id on every query (Req 17.4).
Returns empty PersonalContext() when user has no stored profile data (Req 6.5).

Validates: Requirements 6.3, 6.5, 17.4
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.database.local_models import DailyJournal, MyMedicine, UserProfile
from app.schemas.diagnostic import (
    MyMedicineMini,
    PersonalContext,
    UserProfileMini,
)

logger = logging.getLogger(__name__)


class PersonalContextService:
    """Loads personal context with mandatory user-scoped queries."""

    # How far back to look for journal entries when building a summary
    _JOURNAL_LOOKBACK_DAYS: int = 7

    def load(self, db: Session, user_id: str) -> PersonalContext:
        """Load personal context for a user with mandatory user-scoped queries.

        Every database query includes a WHERE user_id = :user_id filter to
        prevent cross-user data access (Req 17.4).

        Returns an empty PersonalContext() if the user has no stored profile data.
        """
        # Query UserProfile with mandatory user_id filter
        profile_record = (
            db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )

        # If no profile exists, return empty context (Req 6.5)
        if profile_record is None:
            return PersonalContext()

        # Build UserProfileMini from profile record
        profile_mini = self._build_profile_mini(profile_record)

        # Query MyMedicine with mandatory user_id filter
        medications = self._load_medications(db, user_id)

        # Query DailyJournal with mandatory user_id filter
        journal_summary = self._load_journal_summary(db, user_id)

        # Read consent flag from UserProfile (defaults to False if column missing)
        consent = getattr(profile_record, "consent_personal_context", False) or False

        return PersonalContext(
            profile=profile_mini,
            medications=medications,
            recent_journal_summary=journal_summary,
            consent_personal_context=consent,
        )

    # ─── Private helpers ─────────────────────────────────────────────────────

    def _build_profile_mini(self, profile: UserProfile) -> UserProfileMini:
        """Convert a UserProfile ORM record to a minimal Pydantic model."""
        age_range = self._compute_age_range(profile.yob)

        # Extract conditions from medical_history (stored as text)
        conditions = self._extract_conditions(profile.medical_history)

        return UserProfileMini(
            age_range=age_range,
            gender=profile.gender,
            conditions=conditions,
        )

    def _load_medications(self, db: Session, user_id: str) -> list[MyMedicineMini]:
        """Query active medications with mandatory user_id filter."""
        medicines = (
            db.query(MyMedicine)
            .filter(
                MyMedicine.user_id == user_id,
                MyMedicine.is_active == True,  # noqa: E712
            )
            .all()
        )

        return [
            MyMedicineMini(
                name=med.name,
                dosage=med.dosage,
                frequency=self._parse_frequency(med.schedule),
            )
            for med in medicines
        ]

    def _load_journal_summary(self, db: Session, user_id: str) -> str | None:
        """Query recent journal entries with mandatory user_id filter.

        Returns a brief summary of recent journal content, or None if no entries.
        """
        cutoff = datetime.utcnow() - timedelta(days=self._JOURNAL_LOOKBACK_DAYS)

        journals = (
            db.query(DailyJournal)
            .filter(
                DailyJournal.user_id == user_id,
                DailyJournal.created_at >= cutoff,
            )
            .order_by(DailyJournal.created_at.desc())
            .limit(7)
            .all()
        )

        if not journals:
            return None

        # Build a concise summary from recent entries
        summaries: list[str] = []
        for entry in journals:
            parts: list[str] = []
            if entry.mood is not None:
                parts.append(f"mood:{entry.mood}/5")
            if entry.content:
                # Truncate long content to keep summary concise
                content_preview = entry.content[:100]
                parts.append(content_preview)
            if entry.tags:
                parts.append(f"tags:{entry.tags}")
            if parts:
                summaries.append(" | ".join(parts))

        if not summaries:
            return None

        return "; ".join(summaries)

    @staticmethod
    def _compute_age_range(yob: int | None) -> str | None:
        """Compute age range string from year of birth."""
        if yob is None:
            return None

        current_year = datetime.utcnow().year
        age = current_year - yob

        if age < 0:
            return None
        elif age <= 5:
            return "0-5"
        elif age <= 12:
            return "6-12"
        elif age <= 17:
            return "13-17"
        elif age <= 30:
            return "18-30"
        elif age <= 50:
            return "31-50"
        elif age <= 70:
            return "51-70"
        else:
            return "70+"

    @staticmethod
    def _extract_conditions(medical_history: str | None) -> list[str]:
        """Extract condition keywords from medical history text."""
        if not medical_history:
            return []

        # Split by common delimiters (commas, semicolons, newlines)
        conditions: list[str] = []
        for delimiter in [",", ";", "\n"]:
            if delimiter in medical_history:
                conditions = [
                    c.strip() for c in medical_history.split(delimiter) if c.strip()
                ]
                break

        # If no delimiter found, treat the whole text as a single condition
        if not conditions and medical_history.strip():
            conditions = [medical_history.strip()]

        return conditions

    @staticmethod
    def _parse_frequency(schedule: str | None) -> str | None:
        """Parse schedule JSON to extract a human-readable frequency string."""
        if not schedule:
            return None

        try:
            data = json.loads(schedule)
            times = data.get("times", [])
            days = data.get("days", [])

            parts: list[str] = []
            if times:
                parts.append(f"{len(times)}x/ngày")
            if days:
                parts.append(f"{len(days)} ngày/tuần")

            return " ".join(parts) if parts else None
        except (json.JSONDecodeError, TypeError, AttributeError):
            # If schedule is not valid JSON, return it as-is
            return schedule if schedule else None
