"""Unit tests for database models."""
import pytest
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.local_models import DailyJournal, UserProfile, MyMedicine
from app.database.cloud_models import MedicineRegistry, Hospital, FamilyConnection, TriageHistory


# Test fixtures
@pytest.fixture
def sqlite_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(sqlite_engine):
    """Create a database session for testing."""
    Session = sessionmaker(bind=sqlite_engine)
    session = Session()
    yield session
    session.close()


class TestDailyJournal:
    """Tests for DailyJournal model."""

    def test_create_journal_entry(self, db_session):
        """Test creating a journal entry."""
        journal = DailyJournal(
            id="test-journal-1",
            user_id="user-123",
            date=date(2026, 2, 14),
            mood=4,
            content="Hom nay cam thay khoe hon",
            tags='["tot", "khoe"]',
            tree_points=10,
        )
        db_session.add(journal)
        db_session.commit()

        # Query back
        result = db_session.query(DailyJournal).filter_by(id="test-journal-1").first()
        assert result is not None
        assert result.user_id == "user-123"
        assert result.mood == 4
        assert result.tree_points == 10

    def test_journal_defaults(self, db_session):
        """Test default values for journal entry."""
        journal = DailyJournal(
            id="test-journal-2",
            user_id="user-456",
            date=date(2026, 2, 14),
        )
        db_session.add(journal)
        db_session.commit()

        result = db_session.query(DailyJournal).filter_by(id="test-journal-2").first()
        assert result.mood is None
        assert result.tree_points == 0


class TestUserProfile:
    """Tests for UserProfile model."""

    def test_create_user_profile(self, db_session):
        """Test creating a user profile."""
        profile = UserProfile(
            id="profile-1",
            user_id="user-123",
            name="Nguyen Van A",
            yob=1990,
            gender="male",
            disability_type="NONE",
        )
        db_session.add(profile)
        db_session.commit()

        result = db_session.query(UserProfile).filter_by(user_id="user-123").first()
        assert result is not None
        assert result.name == "Nguyen Van A"
        assert result.yob == 1990
        assert result.disability_type == "NONE"

    def test_profile_optional_fields(self, db_session):
        """Test optional fields in profile."""
        profile = UserProfile(
            id="profile-2",
            user_id="user-789",
        )
        db_session.add(profile)
        db_session.commit()

        result = db_session.query(UserProfile).filter_by(user_id="user-789").first()
        assert result.name is None
        assert result.yob is None
        assert result.preferred_communication == "text"


class TestMyMedicine:
    """Tests for MyMedicine model."""

    def test_create_medicine(self, db_session):
        """Test creating a medicine entry."""
        medicine = MyMedicine(
            id="med-1",
            user_id="user-123",
            name="Paracetamol 650",
            dosage="650mg",
            schedule='{"times": ["08:00", "20:00"]}',
            remaining_pills=30,
            is_active=True,
        )
        db_session.add(medicine)
        db_session.commit()

        result = db_session.query(MyMedicine).filter_by(id="med-1").first()
        assert result is not None
        assert result.name == "Paracetamol 650"
        assert result.remaining_pills == 30

    def test_medicine_inactive(self, db_session):
        """Test setting medicine as inactive."""
        medicine = MyMedicine(
            id="med-2",
            user_id="user-123",
            name="Aspirin",
            is_active=False,
        )
        db_session.add(medicine)
        db_session.commit()

        result = db_session.query(MyMedicine).filter_by(id="med-2").first()
        assert result.is_active is False


class TestMedicineRegistry:
    """Tests for MedicineRegistry cloud model."""

    def test_create_medicine_registry(self, db_session):
        """Test creating a medicine registry entry."""
        medicine = MedicineRegistry(
            reg_number="VD-1234-22",
            name="Paracetamol",
            active_ingredient="Paracetamol",
            dosage_form="Tablet",
            strength="650mg",
            contraindications="Suy gan nang",
        )
        db_session.add(medicine)
        db_session.commit()

        result = db_session.query(MedicineRegistry).filter_by(reg_number="VD-1234-22").first()
        assert result is not None
        assert result.name == "Paracetamol"
        assert result.strength == "650mg"

    def test_medicine_interactions_json(self, db_session):
        """Test storing interactions as JSON."""
        medicine = MedicineRegistry(
            reg_number="VD-5678-22",
            name="Warfarin",
            interactions='["Aspirin", "Ibuprofen"]',
        )
        db_session.add(medicine)
        db_session.commit()

        result = db_session.query(MedicineRegistry).filter_by(reg_number="VD-5678-22").first()
        assert result is not None
        assert 'Aspirin' in result.interactions


class TestHospital:
    """Tests for Hospital cloud model."""

    def test_create_hospital(self, db_session):
        """Test creating a hospital entry."""
        hospital = Hospital(
            name="Benh Vien Quan 1",
            address="123 Le Loi, Quan 1, TP.HCM",
            district="Quan 1",
            city="TP.HCM",
            phone="02838291199",
            latitude=10.762,
            longitude=106.660,
            specialties='["Than kinh", "Tim mach"]',
            accepts_bhyt=True,
            has_emergency=True,
        )
        db_session.add(hospital)
        db_session.commit()

        result = db_session.query(Hospital).first()
        assert result is not None
        assert result.name == "Benh Vien Quan 1"
        assert result.has_emergency is True


class TestTriageHistory:
    """Tests for TriageHistory model."""

    def test_create_triage_history(self, db_session):
        """Test creating triage history (anonymous)."""
        triage = TriageHistory(
            session_id="session-abc123",
            age_range="18-30",
            gender="male",
            district="Quan 1",
            symptoms="dau dau, sot nhe",
            duration="2 ngay",
            triage_level="GREEN",
            advice="Uong nuoc, nghi ngoi",
        )
        db_session.add(triage)
        db_session.commit()

        result = db_session.query(TriageHistory).filter_by(session_id="session-abc123").first()
        assert result is not None
        assert result.age_range == "18-30"
        assert result.triage_level == "GREEN"
        # Should NOT have any user ID - it's anonymous
        assert result.session_id is not None

    def test_triage_emergency_flag(self, db_session):
        """Test emergency flag in triage history."""
        triage = TriageHistory(
            session_id="session-emergency",
            symptoms="dau nguc, kho tho",
            was_emergency=True,
            triage_level="RED",
        )
        db_session.add(triage)
        db_session.commit()

        result = db_session.query(TriageHistory).filter_by(session_id="session-emergency").first()
        assert result.was_emergency is True
        assert result.triage_level == "RED"


class TestFamilyConnection:
    """Tests for FamilyConnection model."""

    def test_create_family_connection(self, db_session):
        """Test creating a family connection."""
        connection = FamilyConnection(
            patient_id="patient-123",
            relative_id="relative-456",
            relationship="spouse",
            permissions='["view_medication", "receive_alerts"]',
            status="PENDING",
        )
        db_session.add(connection)
        db_session.commit()

        result = db_session.query(FamilyConnection).first()
        assert result is not None
        assert result.patient_id == "patient-123"
        assert result.status == "PENDING"

    def test_accept_connection(self, db_session):
        """Test accepting a family connection."""
        connection = FamilyConnection(
            patient_id="patient-123",
            relative_id="relative-456",
            status="PENDING",
        )
        db_session.add(connection)
        db_session.commit()

        # Simulate acceptance
        connection.status = "ACTIVE"
        connection.accepted_at = datetime.utcnow()
        db_session.commit()

        result = db_session.query(FamilyConnection).first()
        assert result.status == "ACTIVE"
        assert result.accepted_at is not None
