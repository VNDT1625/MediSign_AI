"""Unit tests for PersonalContextService.

Validates: Requirements 6.3, 6.5, 17.4
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.local_models import DailyJournal, MyMedicine, UserProfile
from app.schemas.diagnostic import PersonalContext
from app.services.personal_context_service import PersonalContextService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def _user_id() -> str:
    return str(uuid4())


class TestLoadReturnsEmptyWhenNoProfile:
    """Req 6.5: Return empty PersonalContext() if user has no stored profile data."""

    def test_no_profile_returns_empty_context(self, db_session) -> None:
        service = PersonalContextService()
        user_id = _user_id()

        result = service.load(db_session, user_id)

        assert result == PersonalContext()
        assert result.profile is None
        assert result.medications == []
        assert result.recent_journal_summary is None
        assert result.consent_personal_context is False


class TestUserScopedQueries:
    """Req 17.4: Every query must have WHERE user_id = :user_id."""

    def test_does_not_return_other_users_profile(self, db_session) -> None:
        service = PersonalContextService()
        user_a = _user_id()
        user_b = _user_id()

        # Create profile for user_a
        profile = UserProfile(
            id=str(uuid4()),
            user_id=user_a,
            gender="male",
            yob=1990,
        )
        db_session.add(profile)
        db_session.commit()

        # Query for user_b should return empty
        result = service.load(db_session, user_b)
        assert result == PersonalContext()

    def test_does_not_return_other_users_medications(self, db_session) -> None:
        service = PersonalContextService()
        user_a = _user_id()
        user_b = _user_id()

        # Create profile for user_b (so load doesn't short-circuit)
        profile_b = UserProfile(
            id=str(uuid4()),
            user_id=user_b,
            gender="female",
            yob=1985,
        )
        db_session.add(profile_b)

        # Create medicine for user_a
        med = MyMedicine(
            id=str(uuid4()),
            user_id=user_a,
            name="Amoxicillin",
            dosage="500mg",
            is_active=True,
        )
        db_session.add(med)
        db_session.commit()

        # Query for user_b should not see user_a's medicine
        result = service.load(db_session, user_b)
        assert result.medications == []

    def test_does_not_return_other_users_journals(self, db_session) -> None:
        service = PersonalContextService()
        user_a = _user_id()
        user_b = _user_id()

        # Create profile for user_b
        profile_b = UserProfile(
            id=str(uuid4()),
            user_id=user_b,
            gender="male",
            yob=2000,
        )
        db_session.add(profile_b)

        # Create journal for user_a
        journal = DailyJournal(
            id=str(uuid4()),
            user_id=user_a,
            date=datetime.utcnow().date(),
            mood=3,
            content="Mệt mỏi cả ngày",
            created_at=datetime.utcnow(),
        )
        db_session.add(journal)
        db_session.commit()

        # Query for user_b should not see user_a's journal
        result = service.load(db_session, user_b)
        assert result.recent_journal_summary is None


class TestLoadBuildsFullContext:
    """Req 6.3: Load full PersonalContext when user has data."""

    def test_loads_profile_medications_and_journal(self, db_session) -> None:
        service = PersonalContextService()
        user_id = _user_id()

        # Create profile
        profile = UserProfile(
            id=str(uuid4()),
            user_id=user_id,
            gender="female",
            yob=1990,
            medical_history="Tiểu đường, Cao huyết áp",
        )
        db_session.add(profile)

        # Create active medication
        med = MyMedicine(
            id=str(uuid4()),
            user_id=user_id,
            name="Metformin",
            dosage="850mg",
            schedule=json.dumps({"times": ["08:00", "20:00"], "days": ["Mon", "Tue", "Wed", "Thu", "Fri"]}),
            is_active=True,
        )
        db_session.add(med)

        # Create recent journal entry
        journal = DailyJournal(
            id=str(uuid4()),
            user_id=user_id,
            date=datetime.utcnow().date(),
            mood=2,
            content="Mệt mỏi, đau đầu liên tục",
            created_at=datetime.utcnow(),
        )
        db_session.add(journal)
        db_session.commit()

        result = service.load(db_session, user_id)

        # Profile loaded
        assert result.profile is not None
        assert result.profile.gender == "female"
        assert result.profile.age_range is not None
        assert "Tiểu đường" in result.profile.conditions
        assert "Cao huyết áp" in result.profile.conditions

        # Medications loaded
        assert len(result.medications) == 1
        assert result.medications[0].name == "Metformin"
        assert result.medications[0].dosage == "850mg"
        assert result.medications[0].frequency is not None

        # Journal summary loaded
        assert result.recent_journal_summary is not None
        assert "Mệt mỏi" in result.recent_journal_summary

    def test_only_loads_active_medications(self, db_session) -> None:
        service = PersonalContextService()
        user_id = _user_id()

        profile = UserProfile(
            id=str(uuid4()),
            user_id=user_id,
            gender="male",
            yob=1985,
        )
        db_session.add(profile)

        # Active medicine
        active_med = MyMedicine(
            id=str(uuid4()),
            user_id=user_id,
            name="Aspirin",
            dosage="100mg",
            is_active=True,
        )
        # Inactive medicine
        inactive_med = MyMedicine(
            id=str(uuid4()),
            user_id=user_id,
            name="OldDrug",
            dosage="200mg",
            is_active=False,
        )
        db_session.add_all([active_med, inactive_med])
        db_session.commit()

        result = service.load(db_session, user_id)

        assert len(result.medications) == 1
        assert result.medications[0].name == "Aspirin"

    def test_old_journal_entries_excluded(self, db_session) -> None:
        service = PersonalContextService()
        user_id = _user_id()

        profile = UserProfile(
            id=str(uuid4()),
            user_id=user_id,
            gender="male",
            yob=1995,
        )
        db_session.add(profile)

        # Old journal entry (> 7 days ago)
        old_journal = DailyJournal(
            id=str(uuid4()),
            user_id=user_id,
            date=(datetime.utcnow() - timedelta(days=10)).date(),
            mood=4,
            content="Cảm thấy tốt",
            created_at=datetime.utcnow() - timedelta(days=10),
        )
        db_session.add(old_journal)
        db_session.commit()

        result = service.load(db_session, user_id)

        assert result.recent_journal_summary is None

    def test_consent_defaults_to_false_when_column_missing(self, db_session) -> None:
        """consent_personal_context defaults to False if not on the model."""
        service = PersonalContextService()
        user_id = _user_id()

        profile = UserProfile(
            id=str(uuid4()),
            user_id=user_id,
            gender="male",
            yob=1990,
        )
        db_session.add(profile)
        db_session.commit()

        result = service.load(db_session, user_id)

        assert result.consent_personal_context is False
