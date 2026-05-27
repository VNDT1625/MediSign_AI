from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.cloud_models import DiseaseSymptomEdge
from app.schemas.diagnostic import RankedDisease


class DiseaseSymptomGraph:
    """Synchronous RAG #2 disease-symptom graph access."""

    def __init__(self, db: Session | None = None) -> None:
        self.db = db

    def edges_for(
        self,
        candidates: list[RankedDisease],
        db: Session | None = None,
    ) -> list[DiseaseSymptomEdge]:
        session = db or self.db
        if session is None or not candidates:
            return []

        disease_ids: list[str] = []
        seen: set[str] = set()
        for candidate in candidates:
            disease_id = candidate.name.strip()
            key = disease_id.casefold()
            if disease_id and key not in seen:
                seen.add(key)
                disease_ids.append(disease_id)
        if not disease_ids:
            return []

        return list(
            session.scalars(
                select(DiseaseSymptomEdge).where(DiseaseSymptomEdge.disease_id.in_(disease_ids))
            ).all()
        )
