"""Local database models - stored on device (SQLite)."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class DailyJournal(Base):
    """Daily journal entries for Soul Garden gamification."""

    __tablename__ = "daily_journals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)

    # Mood: 1 (very bad) to 5 (very good)
    mood: Mapped[int] = mapped_column(Integer, nullable=True)

    # Content can be text or voice-to-text
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Tags as JSON string: ["stress", "mat ngu", "quen"]
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # AI analysis result from local LLM
    ai_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Tree growth points (gamification)
    tree_points: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class UserProfile(Base):
    """User health profile - stored locally only."""

    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)

    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Year of birth (not full date for privacy)
    yob: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Gender: male, female, other
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Medical history as text
    medical_history: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Allergies as text
    allergies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Disability type: DEAF, BLIND, ELDERLY, NONE
    disability_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Communication preferences
    preferred_communication: Mapped[Optional[str]] = mapped_column(
        String(50), default="text"
    )  # text, voice, sign

    # Emergency contact
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class MyMedicine(Base):
    """User's personal medicine cabinet."""

    __tablename__ = "my_medicines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Medicine name as registered
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Dosage e.g., "650mg", "500mg"
    dosage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Schedule as JSON: {"times": ["08:00", "20:00"], "days": ["Mon","Wed","Fri"]}
    schedule: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Remaining pills/capsules
    remaining_pills: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Notes from doctor
    doctor_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Is active medicine
    is_active: Mapped[bool] = mapped_column(default=True)

    # Start and end dates
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
