"""Build disease-symptom graph for RAG #2 differential questioning.

Reads disease records from `data/knowledge_base/knowledge_base.json`, extracts
the `common_symptoms` field per disease, computes edge weights, and upserts
into the `disease_symptom_edges` table.

Usage:
    python scripts/build_disease_graph.py [--db-url URL]

Edge semantics:
    - weight: float in [0.0, 1.0] representing P(symptom | disease).
              Common symptoms get a base weight, with red-flag symptoms boosted.
    - is_discriminative: True when the symptom appears in <=2 diseases overall
                         (rare across the disease space, useful for differential).

The build is fully deterministic so it can be re-run idempotently.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# ---------------------------------------------------------------------------
# Setup paths so we can import app models
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "apps" / "backend_fastapi"
sys.path.insert(0, str(BACKEND_DIR))

from app.database.cloud_models import DiseaseSymptomEdge  # noqa: E402

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
KB_PATH = ROOT / "data" / "knowledge_base" / "knowledge_base.json"

# Edge weight policy
WEIGHT_COMMON = 0.7         # base weight for common symptoms
WEIGHT_RED_FLAG = 0.95      # boosted weight for red-flag (severe) symptoms
WEIGHT_BOTH = 0.98          # symptom appears in both common and red flags

# A symptom is discriminative if it appears in <= this many diseases.
DISCRIMINATIVE_MAX_DISEASES = 2

# Disease record types we accept
DISEASE_TYPES = {"vietnam_common_disease"}


def _get_database_url() -> str:
    """Resolve database URL from environment."""
    return (
        os.getenv("DATABASE_URL")
        or os.getenv("BACKEND_DATABASE_URL")
        or "postgresql+psycopg://postgres:postgres@localhost:5432/medisign"
    )


def _normalize_symptom(symptom: str) -> str:
    """Lowercase and strip whitespace for stable matching."""
    return (symptom or "").strip().lower()


def load_disease_records(kb_path: Path) -> list[dict[str, Any]]:
    """Load disease records from the knowledge base file."""
    logger.info("Loading knowledge base from %s ...", kb_path)
    with open(kb_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON list, got {type(data).__name__}")

    diseases = [r for r in data if r.get("type") in DISEASE_TYPES]
    logger.info("Found %d disease records (out of %d total)", len(diseases), len(data))
    return diseases


def extract_edges(diseases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Extract (disease_id, symptom, weight, is_discriminative) edges.

    Algorithm:
        1. For each disease, walk `structured.common_symptoms` and `structured.red_flags`.
        2. Compute a weight per (disease, symptom) pair using policy constants.
        3. Count global symptom occurrences to decide `is_discriminative`.
        4. Deduplicate (disease_id, symptom) pairs keeping the highest weight.
    """
    raw_edges: list[dict[str, Any]] = []
    skipped_no_id = 0
    skipped_no_symptoms = 0

    for record in diseases:
        disease_id = record.get("id")
        if not disease_id:
            skipped_no_id += 1
            continue

        structured = record.get("structured") or {}
        common = [s for s in (structured.get("common_symptoms") or []) if isinstance(s, str)]
        red_flags = [s for s in (structured.get("red_flags") or []) if isinstance(s, str)]

        if not common and not red_flags:
            logger.warning("Skipping disease '%s': no symptoms found", disease_id)
            skipped_no_symptoms += 1
            continue

        common_set = {_normalize_symptom(s) for s in common if _normalize_symptom(s)}
        red_set = {_normalize_symptom(s) for s in red_flags if _normalize_symptom(s)}

        # Deduplicate per disease while computing weight
        symptom_weights: dict[str, float] = {}
        for symptom in common_set | red_set:
            in_common = symptom in common_set
            in_red = symptom in red_set
            if in_common and in_red:
                weight = WEIGHT_BOTH
            elif in_red:
                weight = WEIGHT_RED_FLAG
            else:
                weight = WEIGHT_COMMON
            # Keep highest weight if duplicates somehow appear (defensive)
            symptom_weights[symptom] = max(symptom_weights.get(symptom, 0.0), weight)

        for symptom, weight in symptom_weights.items():
            raw_edges.append(
                {
                    "disease_id": disease_id,
                    "symptom": symptom,
                    "weight": weight,
                }
            )

    logger.info(
        "Extracted %d raw edges from %d diseases (skipped: %d no-id, %d no-symptoms)",
        len(raw_edges),
        len(diseases),
        skipped_no_id,
        skipped_no_symptoms,
    )

    # Compute discriminative flag based on global symptom -> disease count
    symptom_disease_count: Counter[str] = Counter()
    seen_pairs: set[tuple[str, str]] = set()
    for edge in raw_edges:
        pair = (edge["disease_id"], edge["symptom"])
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        symptom_disease_count[edge["symptom"]] += 1

    for edge in raw_edges:
        edge["is_discriminative"] = (
            symptom_disease_count[edge["symptom"]] <= DISCRIMINATIVE_MAX_DISEASES
        )

    discriminative_count = sum(1 for e in raw_edges if e["is_discriminative"])
    logger.info(
        "Discriminative edges: %d / %d (symptom seen in <=%d diseases)",
        discriminative_count,
        len(raw_edges),
        DISCRIMINATIVE_MAX_DISEASES,
    )
    return raw_edges


def upsert_edges(session: Session, edges: list[dict[str, Any]]) -> int:
    """Upsert edges into disease_symptom_edges table.

    Strategy: delete existing rows for the affected disease_ids first, then
    bulk insert new edges. This keeps the script idempotent without relying
    on a unique constraint that the schema does not yet declare.
    """
    if not edges:
        logger.info("No edges to upsert.")
        return 0

    affected_disease_ids = sorted({e["disease_id"] for e in edges})
    logger.info(
        "Replacing edges for %d diseases ...",
        len(affected_disease_ids),
    )

    # Delete existing rows for these diseases
    session.execute(
        text("DELETE FROM disease_symptom_edges WHERE disease_id = ANY(:ids)"),
        {"ids": affected_disease_ids},
    )

    # Bulk insert
    session.execute(
        text("""
            INSERT INTO disease_symptom_edges (disease_id, symptom, weight, is_discriminative)
            VALUES (:disease_id, :symptom, :weight, :is_discriminative)
        """),
        edges,
    )
    session.commit()

    logger.info("Upserted %d edges.", len(edges))
    return len(edges)


def print_summary(edges: list[dict[str, Any]]) -> None:
    """Log a small summary for inspection."""
    by_disease: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        by_disease[edge["disease_id"]].append(edge)

    logger.info("Edge summary per disease:")
    for disease_id in sorted(by_disease):
        d_edges = by_disease[disease_id]
        disc = sum(1 for e in d_edges if e["is_discriminative"])
        logger.info("  %s: %d edges (%d discriminative)", disease_id, len(d_edges), disc)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build disease-symptom graph")
    parser.add_argument("--db-url", type=str, default=None, help="Database URL override")
    parser.add_argument("--kb-path", type=str, default=None, help="Knowledge base JSON path override")
    parser.add_argument("--dry-run", action="store_true", help="Compute edges only, skip DB upsert")
    args = parser.parse_args()

    kb_path = Path(args.kb_path) if args.kb_path else KB_PATH
    if not kb_path.exists():
        logger.error("Knowledge base not found: %s", kb_path)
        sys.exit(1)

    # Load and extract
    diseases = load_disease_records(kb_path)
    if not diseases:
        logger.warning("No disease records found. Exiting.")
        sys.exit(0)

    edges = extract_edges(diseases)
    if not edges:
        logger.warning("No edges extracted. Exiting.")
        sys.exit(0)

    print_summary(edges)

    if args.dry_run:
        logger.info("Dry run complete. %d edges would be upserted.", len(edges))
        return

    # Database upsert
    db_url = args.db_url or _get_database_url()
    logger.info("Connecting to database ...")
    engine = create_engine(db_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine)

    # Touch DiseaseSymptomEdge to ensure the model module is imported
    _ = DiseaseSymptomEdge

    with SessionLocal() as session:
        upsert_edges(session, edges)

    logger.info("Done! %d edges in disease_symptom_edges.", len(edges))


if __name__ == "__main__":
    main()
