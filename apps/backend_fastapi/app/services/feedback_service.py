"""Feedback loop service for RAG diagnostic improvement.

Workflow:
1. User submits feedback after real doctor visit (correct / wrong + actual disease)
2. FeedbackService stores DiagnosisFeedback record
3. After each feedback, check if (disease, symptom) pair has enough feedback to
   generate a WeightUpdateProposal (MIN_FEEDBACK_THRESHOLD = 10)
4. Admin reviews proposals via admin API → approves → weight applied to disease_symptom_edges

Requirements: feedback loop level 3
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.database.cloud_models import (
    DiagnosisFeedback,
    DiseaseSymptomEdge,
    WeightUpdateProposal,
)

logger = logging.getLogger(__name__)

# Minimum number of feedback records needed before proposing a weight update
MIN_FEEDBACK_THRESHOLD = 10

# Maximum weight delta per update cycle to prevent wild swings
MAX_WEIGHT_DELTA = 0.15


class FeedbackService:
    """Handle user feedback and drive weight update proposals."""

    def submit_feedback(
        self,
        db: Session,
        conversation_id: str,
        user_id: str,
        is_correct: bool,
        ai_predicted_disease: str,
        ai_confidence: float | None,
        actual_disease: str | None,
        symptoms_at_time: list[str],
        notes: str | None = None,
    ) -> DiagnosisFeedback:
        """Store user feedback and trigger proposal check.

        Args:
            db: SQLAlchemy session.
            conversation_id: The conversation this feedback is for.
            user_id: User submitting feedback.
            is_correct: Whether AI prediction matched real diagnosis.
            ai_predicted_disease: Disease AI predicted at conclusion.
            ai_confidence: AI confidence (0-1) at conclusion.
            actual_disease: Real disease from doctor (only when is_correct=False).
            symptoms_at_time: Symptoms collected during the conversation.
            notes: Optional free-text notes.

        Returns:
            The created DiagnosisFeedback record.
        """
        feedback = DiagnosisFeedback(
            conversation_id=conversation_id,
            user_id=user_id,
            is_correct=is_correct,
            ai_predicted_disease=ai_predicted_disease,
            ai_confidence=ai_confidence,
            actual_disease=actual_disease if not is_correct else None,
            symptoms_at_time=json.dumps(symptoms_at_time, ensure_ascii=False),
            notes=notes,
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)

        logger.info(
            "Feedback submitted: conversation=%s correct=%s disease=%s",
            conversation_id,
            is_correct,
            ai_predicted_disease,
        )

        # Check if this triggers any weight update proposals
        self._maybe_propose_updates(db, ai_predicted_disease, symptoms_at_time)

        return feedback

    def _maybe_propose_updates(
        self,
        db: Session,
        disease: str,
        symptoms: list[str],
    ) -> None:
        """For each (disease, symptom) pair, check if feedback threshold is met.

        When met, generate a WeightUpdateProposal if one doesn't already exist.
        """
        for symptom in symptoms:
            if not symptom.strip():
                continue
            self._check_and_propose(db, disease.strip(), symptom.strip())

    def _check_and_propose(self, db: Session, disease: str, symptom: str) -> None:
        """Check feedback aggregate for a (disease, symptom) pair and propose if ready."""
        # Count all feedback records mentioning this disease
        all_feedback = db.execute(
            select(DiagnosisFeedback).where(
                DiagnosisFeedback.ai_predicted_disease == disease
            )
        ).scalars().all()

        # Filter to those that had this symptom
        relevant = [
            f for f in all_feedback
            if self._feedback_has_symptom(f, symptom)
        ]

        if len(relevant) < MIN_FEEDBACK_THRESHOLD:
            return  # Not enough data yet

        correct_count = sum(1 for f in relevant if f.is_correct)
        incorrect_count = len(relevant) - correct_count
        accuracy = correct_count / len(relevant)

        # Get current edge weight
        edge = db.execute(
            select(DiseaseSymptomEdge).where(
                and_(
                    DiseaseSymptomEdge.disease_id == disease,
                    DiseaseSymptomEdge.symptom == symptom,
                )
            )
        ).scalar_one_or_none()

        current_weight = edge.weight if edge else 0.5

        # Calculate proposed weight
        # High accuracy → increase weight; low accuracy → decrease weight
        # Neutral zone: accuracy 0.4-0.6 → no change
        if accuracy >= 0.7:
            delta = min(MAX_WEIGHT_DELTA, (accuracy - 0.6) * 0.3)
            proposed_weight = min(1.0, current_weight + delta)
            direction = "increase"
        elif accuracy <= 0.3:
            delta = min(MAX_WEIGHT_DELTA, (0.4 - accuracy) * 0.3)
            proposed_weight = max(0.0, current_weight - delta)
            direction = "decrease"
        else:
            return  # No significant signal

        # Round to 3 decimal places
        proposed_weight = round(proposed_weight, 3)

        if abs(proposed_weight - current_weight) < 0.01:
            return  # Change too small to matter

        # Check if a pending proposal already exists for this pair
        existing_proposal = db.execute(
            select(WeightUpdateProposal).where(
                and_(
                    WeightUpdateProposal.disease_id == disease,
                    WeightUpdateProposal.symptom == symptom,
                    WeightUpdateProposal.status == "pending",
                )
            )
        ).scalar_one_or_none()

        if existing_proposal:
            # Update existing proposal with latest data
            existing_proposal.current_weight = current_weight
            existing_proposal.proposed_weight = proposed_weight
            existing_proposal.direction = direction
            existing_proposal.feedback_count = len(relevant)
            existing_proposal.correct_count = correct_count
            existing_proposal.incorrect_count = incorrect_count
            db.commit()
            logger.info(
                "Updated weight proposal: %s / %s → %.3f (was %.3f)",
                disease, symptom, proposed_weight, current_weight,
            )
        else:
            proposal = WeightUpdateProposal(
                disease_id=disease,
                symptom=symptom,
                current_weight=current_weight,
                proposed_weight=proposed_weight,
                direction=direction,
                feedback_count=len(relevant),
                correct_count=correct_count,
                incorrect_count=incorrect_count,
                status="pending",
            )
            db.add(proposal)
            db.commit()
            logger.info(
                "Created weight proposal: %s / %s %.3f → %.3f (%s)",
                disease, symptom, current_weight, proposed_weight, direction,
            )

    def apply_proposal(
        self,
        db: Session,
        proposal_id: int,
        reviewed_by: str,
    ) -> dict[str, Any]:
        """Admin approves a proposal — apply weight change to disease_symptom_edges.

        Creates or updates the edge. Marks proposal as 'approved'.
        """
        proposal = db.get(WeightUpdateProposal, proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        if proposal.status != "pending":
            raise ValueError(f"Proposal {proposal_id} is already {proposal.status}")

        # Apply to edge
        edge = db.execute(
            select(DiseaseSymptomEdge).where(
                and_(
                    DiseaseSymptomEdge.disease_id == proposal.disease_id,
                    DiseaseSymptomEdge.symptom == proposal.symptom,
                )
            )
        ).scalar_one_or_none()

        if edge:
            old_weight = edge.weight
            edge.weight = proposal.proposed_weight
        else:
            old_weight = 0.0
            edge = DiseaseSymptomEdge(
                disease_id=proposal.disease_id,
                symptom=proposal.symptom,
                weight=proposal.proposed_weight,
                is_discriminative=proposal.proposed_weight >= 0.6,
            )
            db.add(edge)

        proposal.status = "approved"
        proposal.reviewed_by = reviewed_by
        proposal.reviewed_at = datetime.utcnow()
        db.commit()

        logger.info(
            "Applied weight update: %s / %s %.3f → %.3f (approved by %s)",
            proposal.disease_id, proposal.symptom,
            old_weight, proposal.proposed_weight, reviewed_by,
        )

        return {
            "disease_id": proposal.disease_id,
            "symptom": proposal.symptom,
            "old_weight": old_weight,
            "new_weight": proposal.proposed_weight,
            "direction": proposal.direction,
        }

    def reject_proposal(
        self,
        db: Session,
        proposal_id: int,
        reviewed_by: str,
    ) -> None:
        """Admin rejects a proposal — mark as rejected, no weight change."""
        proposal = db.get(WeightUpdateProposal, proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        if proposal.status != "pending":
            raise ValueError(f"Proposal {proposal_id} is already {proposal.status}")

        proposal.status = "rejected"
        proposal.reviewed_by = reviewed_by
        proposal.reviewed_at = datetime.utcnow()
        db.commit()

    def approve_kb_record(
        self,
        db: Session,
        record_id: int,
        reviewed_by: str,
        kb_path_str: str,
    ) -> dict[str, Any]:
        """Admin approves a KBPendingRecord — promote to main knowledge_base.json.

        Also inserts disease_symptom_edges for the record's symptoms.
        """
        from pathlib import Path

        from app.database.cloud_models import KBPendingRecord
        import uuid as uuid_mod

        record = db.get(KBPendingRecord, record_id)
        if not record:
            raise ValueError(f"KBPendingRecord {record_id} not found")
        if record.status != "pending":
            raise ValueError(f"KBPendingRecord {record_id} is already {record.status}")

        # Load symptoms from JSON
        symptoms: list[str] = json.loads(record.symptoms or "[]")
        red_flags: list[str] = json.loads(record.red_flags or "[]")
        home_care: list[str] = json.loads(record.home_care or "[]")
        lab_tests: list[str] = json.loads(record.lab_tests or "[]")

        # Build KB entry
        record_uuid = f"medgemma_{uuid_mod.uuid4().hex[:12]}"
        entry: dict[str, Any] = {
            "id": record_uuid,
            "type": "disease",
            "title": record.disease_name,
            "content": f"{record.disease_name}: {', '.join(symptoms)}",
            "source": {"name": "medgemma_search_approved"},
            "structured": {
                "severity": record.severity,
                "red_flags": red_flags,
                "home_care": home_care,
                "lab_tests": lab_tests,
                "symptoms": symptoms,
            },
            "confidence": "medium",
            "needs_medical_review": False,
        }

        # Append to knowledge_base.json
        kb_path = Path(kb_path_str)
        existing: list[dict[str, Any]] = []
        if kb_path.exists():
            try:
                existing = json.loads(kb_path.read_text(encoding="utf-8"))
                if not isinstance(existing, list):
                    existing = []
            except (json.JSONDecodeError, OSError):
                existing = []

        existing.append(entry)
        try:
            kb_path.parent.mkdir(parents=True, exist_ok=True)
            kb_path.write_text(
                json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except OSError as exc:
            raise RuntimeError(f"Failed to write knowledge_base.json: {exc}") from exc

        # Insert disease_symptom_edges
        for i, symptom in enumerate(symptoms):
            weight = max(0.1, 1.0 - (i * 0.15))
            existing_edge = db.execute(
                select(DiseaseSymptomEdge).where(
                    and_(
                        DiseaseSymptomEdge.disease_id == record.disease_name,
                        DiseaseSymptomEdge.symptom == symptom,
                    )
                )
            ).scalar_one_or_none()

            if existing_edge:
                existing_edge.weight = min(1.0, max(0.0, weight))
                existing_edge.is_discriminative = i < 3
            else:
                db.add(
                    DiseaseSymptomEdge(
                        disease_id=record.disease_name,
                        symptom=symptom,
                        weight=min(1.0, max(0.0, weight)),
                        is_discriminative=i < 3,
                    )
                )

        # Mark record as approved
        record.status = "approved"
        record.reviewed_by = reviewed_by
        record.reviewed_at = datetime.utcnow()
        db.commit()

        return {"record_id": record_uuid, "disease_name": record.disease_name, "symptoms": symptoms}

    def reject_kb_record(
        self,
        db: Session,
        record_id: int,
        reviewed_by: str,
        reason: str | None = None,
    ) -> None:
        """Admin rejects a KBPendingRecord."""
        from app.database.cloud_models import KBPendingRecord

        record = db.get(KBPendingRecord, record_id)
        if not record:
            raise ValueError(f"KBPendingRecord {record_id} not found")
        if record.status != "pending":
            raise ValueError(f"KBPendingRecord {record_id} is already {record.status}")

        record.status = "rejected"
        record.reviewed_by = reviewed_by
        record.reviewed_at = datetime.utcnow()
        record.rejection_reason = reason
        db.commit()

    @staticmethod
    def _feedback_has_symptom(feedback: DiagnosisFeedback, symptom: str) -> bool:
        """Check if a feedback record includes the given symptom."""
        if not feedback.symptoms_at_time:
            return False
        try:
            symptoms: list[str] = json.loads(feedback.symptoms_at_time)
            symptom_lower = symptom.lower()
            return any(symptom_lower in s.lower() for s in symptoms)
        except (json.JSONDecodeError, TypeError):
            return False


feedback_service = FeedbackService()
