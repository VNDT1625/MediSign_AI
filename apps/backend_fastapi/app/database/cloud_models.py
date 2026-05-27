"""Cloud database models - stored on PostgreSQL server."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Index, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None

from app.database.base import Base


class User(Base):
    """User account - stored on PostgreSQL server."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Unique username (for display)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    # Email (unique, for login)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    # Phone (optional, for login)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)

    # Hashed password
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Full name
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Is email verified
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Is phone verified
    is_phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Is account active
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Account type: user, doctor, admin
    account_type: Mapped[str] = mapped_column(String(20), default="user")

    # Last login
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class UserSession(Base):
    """User sessions/tokens - stored on PostgreSQL."""

    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # User ID
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Refresh token (hashed for security)
    refresh_token_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Device info
    device_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    device_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # IP address
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    # Expires at
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Is revoked
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


class PasswordReset(Base):
    """Password reset tokens."""

    __tablename__ = "password_resets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # User ID
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Reset token (hashed)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Expires at
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Is used
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


class EmailVerification(Base):
    """Email verification tokens."""

    __tablename__ = "email_verifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # User ID
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Verification token (hashed)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Expires at
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Is used
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


class MedicineRegistry(Base):
    """Central medicine database - public data from Cục Dược VN."""

    __tablename__ = "medicine_registry"

    # Registration number (e.g., VD-1234-22)
    reg_number: Mapped[str] = mapped_column(String(50), primary_key=True)

    # Medicine name
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)

    # Active ingredient
    active_ingredient: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Dosage form: tablet, capsule, syrup, injection, etc.
    dosage_form: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Strength e.g., "650mg", "500mg/5ml"
    strength: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Manufacturer
    manufacturer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Contraindications
    contraindications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Side effects
    side_effects: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Interactions as JSON array of medicine names
    interactions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Warnings
    warnings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Usage instructions
    usage: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Storage conditions
    storage: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Is active in registry
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Hospital(Base):
    """Hospital and clinic database."""

    __tablename__ = "hospitals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Hospital name
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)

    # Address
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # District
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # City/Province
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Phone number
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Website
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Coordinates (latitude, longitude)
    latitude: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    longitude: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Specialties as JSON array: ["Tiêu hóa", "Tim mạch"]
    specialties: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Accepts BHYT (health insurance)
    accepts_bhyt: Mapped[bool] = mapped_column(Boolean, default=False)

    # 24/7 availability
    is_24h: Mapped[bool] = mapped_column(Boolean, default=False)

    # Emergency services
    has_emergency: Mapped[bool] = mapped_column(Boolean, default=False)

    # Hospital type: government, private, clinic
    hospital_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class FamilyConnection(Base):
    """Family member connections for Care Connect feature."""

    __tablename__ = "family_connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Patient (main user)
    patient_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Relative (family member)
    relative_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Relationship: spouse, parent, child, sibling, other
    relationship: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Permissions as JSON: ["view_medication", "receive_alerts", "view_mood"]
    permissions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Connection status: PENDING, ACTIVE, REJECTED
    status: Mapped[str] = mapped_column(String(20), default="PENDING")

    # Who initiated the connection
    initiated_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Accepted at
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


class TriageHistory(Base):
    """Anonymous triage history for analytics (no PII)."""

    __tablename__ = "triage_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Session ID (temporary, not linked to user account)
    session_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Age range (anonymized): "0-5", "6-12", "13-17", "18-30", "31-50", "51-70", "70+"
    age_range: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Gender: male, female, other
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # District (anonymized location)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Symptoms (anonymized text)
    symptoms: Mapped[str] = mapped_column(Text, nullable=False)

    # Duration
    duration: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Triage result level: GREEN, YELLOW, RED
    triage_level: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # AI advice given
    advice: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Recommended specialty
    recommended_specialty: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Was emergency (called 115)
    was_emergency: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )


# ══════════════════════════════════════════════════════════════
# COMMUNITY MODELS
# ══════════════════════════════════════════════════════════════


class CommunityPost(Base):
    """Community posts for sharing health tips and experiences."""

    __tablename__ = "community_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Author (user_id)
    author_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Author display name (can be anonymous)
    author_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Post content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Category: general, health_tip, recipe, exercise, mental_health, question
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Tags as JSON array: ["tips", "vitamin"]
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Is anonymous (hide author name)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=True)

    # Post status: pending, approved, flagged, deleted
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)

    # Moderation notes
    moderation_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Like count
    like_count: Mapped[int] = mapped_column(Integer, default=0)

    # Comment count
    comment_count: Mapped[int] = mapped_column(Integer, default=0)

    # Has medical disclaimer
    has_medical_disclaimer: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class PostComment(Base):
    """Comments on community posts."""

    __tablename__ = "post_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Post ID
    post_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Author (user_id)
    author_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Author display name
    author_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Comment content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Is anonymous
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=True)

    # Status: active, deleted
    status: Mapped[str] = mapped_column(String(20), default="active")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


class PostLike(Base):
    """Likes on community posts."""

    __tablename__ = "post_likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Post ID
    post_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # User ID who liked
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


# ══════════════════════════════════════════════════════════════
# FITNESS/WORKOUT MODELS
# ══════════════════════════════════════════════════════════════


class WorkoutSession(Base):
    """User workout session history."""

    __tablename__ = "workout_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # User ID
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Exercise ID (from fitness model)
    exercise_id: Mapped[str] = mapped_column(String(50), nullable=False)

    # Exercise name
    exercise_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Target area: upper_body, lower_body, core, cardio, full_body
    target_area: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Duration in seconds
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)

    # Repetitions count
    repetitions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Sets count
    sets: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Calories burned (estimated)
    calories_burned: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Completion status: completed, partial, abandoned
    status: Mapped[str] = mapped_column(String(20), default="completed")

    # User feedback: easy, moderate, hard
    difficulty_rating: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )


class FitnessGoal(Base):
    """User fitness goals."""

    __tablename__ = "fitness_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # User ID
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Goal type: weight_loss, muscle_gain, endurance, flexibility, general
    goal_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Target value (e.g., 5 for 5kg, 10 for 10 reps)
    target_value: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Current progress
    current_progress: Mapped[float] = mapped_column(default=0.0)

    # Target date
    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Status: active, achieved, abandoned
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


# ══════════════════════════════════════════════════════════════
# RAG DIAGNOSTIC CHAT MODELS
# ══════════════════════════════════════════════════════════════


class ChatConversation(Base):
    """Multi-turn diagnostic chat conversation."""

    __tablename__ = "chat_conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Owner user ID
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Conversation title (auto-generated or user-set)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Adapter: medical | psychology
    adapter: Mapped[str] = mapped_column(String(20), default="medical")

    # Current diagnostic phase: initial | questioning | conclusion | needs_test
    phase: Mapped[str] = mapped_column(String(20), default="initial")

    # Soft-delete flag
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class ChatMessage(Base):
    """Individual message within a diagnostic chat conversation."""

    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Parent conversation
    conversation_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )

    # Message role: user | assistant
    role: Mapped[str] = mapped_column(String(20), nullable=False)

    # Message content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Metadata including diagnosis_state for assistant messages
    metadata_json: Mapped[dict] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    __table_args__ = (
        Index("ix_chat_messages_conv_created", "conversation_id", "created_at"),
    )


# ══════════════════════════════════════════════════════════════
# KNOWLEDGE BASE & RAG MODELS
# ══════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════
# KB PENDING & FEEDBACK MODELS
# ══════════════════════════════════════════════════════════════


class KBPendingRecord(Base):
    """Staging table for KBLazyLoader-generated records awaiting admin review.

    Records are generated when RAG misses (score < KB_MISS_THRESHOLD) and
    MedGemma produces structured disease info. They are used immediately for
    the current session but only promoted to the main KB after admin approval.
    """

    __tablename__ = "kb_pending_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # The user query that triggered the KB miss
    source_query: Mapped[str] = mapped_column(Text, nullable=False)

    # Disease info generated by MedGemma
    disease_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    symptoms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)       # JSON array
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    red_flags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)      # JSON array
    home_care: Mapped[Optional[str]] = mapped_column(Text, nullable=True)      # JSON array
    lab_tests: Mapped[Optional[str]] = mapped_column(Text, nullable=True)      # JSON array

    # Review workflow: pending → approved | rejected
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )


class DiagnosisFeedback(Base):
    """User feedback on AI diagnostic conclusions.

    Collected after user returns from actual doctor visit.
    Drives the feedback loop for weight updates in disease_symptom_edges.
    """

    __tablename__ = "diagnosis_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Which conversation this feedback is for
    conversation_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Was the AI prediction correct?
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # AI's top prediction at conclusion time
    ai_predicted_disease: Mapped[str] = mapped_column(String(255), nullable=False)
    ai_confidence: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Actual diagnosis (if AI was wrong)
    actual_disease: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Symptoms collected during the conversation (JSON array) — used for weight proposals
    symptoms_at_time: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Optional free-text notes from user
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )


class WeightUpdateProposal(Base):
    """Proposed update to disease_symptom_edges.weight based on feedback aggregate.

    Created automatically when feedback for a (disease, symptom) pair crosses
    the threshold (MIN_FEEDBACK_THRESHOLD). Applied only after admin approval.
    """

    __tablename__ = "weight_update_proposals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Target edge
    disease_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    symptom: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Weight change
    current_weight: Mapped[float] = mapped_column(nullable=False)
    proposed_weight: Mapped[float] = mapped_column(nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # "increase" | "decrease"

    # Evidence basis
    feedback_count: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_count: Mapped[int] = mapped_column(Integer, nullable=False)
    incorrect_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Review workflow: pending → approved | rejected
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )


if Vector is not None:

    class KBEmbedding(Base):
        """Knowledge base embedding index for hybrid RAG retrieval (pgvector)."""

        __tablename__ = "kb_embeddings"

        # Record ID from knowledge_base.json
        record_id: Mapped[str] = mapped_column(String(255), primary_key=True)

        # 384-dim embedding vector (intfloat/multilingual-e5-small)
        embedding = mapped_column(Vector(384).with_variant(Text(), "sqlite"), nullable=False)

        # Kind of record: disease, symptom, or evidence
        kind: Mapped[str] = mapped_column(String(20), nullable=False)

        __table_args__ = (
            CheckConstraint(
                "kind IN ('disease', 'symptom', 'evidence')",
                name="ck_kb_embeddings_kind",
            ),
        )


class DiseaseSymptomEdge(Base):
    """Disease-symptom graph edges for RAG #2 differential questioning."""

    __tablename__ = "disease_symptom_edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Disease identifier
    disease_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Symptom name
    symptom: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Edge weight constrained to [0.0, 1.0]
    weight: Mapped[float] = mapped_column(nullable=False)

    # Whether this symptom is discriminative for this disease
    is_discriminative: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        CheckConstraint(
            "weight >= 0.0 AND weight <= 1.0",
            name="ck_disease_symptom_edges_weight",
        ),
    )
