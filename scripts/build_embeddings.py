"""Build embedding index for the knowledge base.

Reads enriched `data/knowledge_base/knowledge_base.json`, validates each record,
encodes with `intfloat/multilingual-e5-small` (384 dims), and upserts into the
`kb_embeddings` PostgreSQL table.

Usage:
    python scripts/build_embeddings.py [--batch-size 64] [--db-url URL]

Requirements:
    - sentence-transformers
    - sqlalchemy + psycopg
    - pgvector

Records are classified into kinds:
    - "disease"  : type in {vietnam_common_disease}
    - "symptom"  : type in {vietnamese_symptom_phrase}
    - "evidence" : type in {guideline_chunk, drug, drug_interaction, nutrition_requirement}
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, TYPE_CHECKING

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Setup paths so we can import app models
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "apps" / "backend_fastapi"
sys.path.insert(0, str(BACKEND_DIR))

from app.database.base import Base  # noqa: E402
from app.database.cloud_models import KBEmbedding  # noqa: E402

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
MODEL_NAME = "intfloat/multilingual-e5-small"
EMBEDDING_DIM = 384
BATCH_SIZE_DEFAULT = 64

# Map record types to embedding kinds
TYPE_TO_KIND: dict[str, str] = {
    "vietnam_common_disease": "disease",
    "vietnamese_symptom_phrase": "symptom",
    "guideline_chunk": "evidence",
    "drug": "evidence",
    "drug_interaction": "evidence",
    "nutrition_requirement": "evidence",
}

# Required fields for disease records (Req 18.3 validation)
DISEASE_REQUIRED_FIELDS = {"structured"}
DISEASE_STRUCTURED_FIELDS = {"common_symptoms", "red_flags"}


def _get_database_url() -> str:
    """Resolve database URL from environment."""
    return (
        os.getenv("DATABASE_URL")
        or os.getenv("BACKEND_DATABASE_URL")
        or "postgresql+psycopg://postgres:postgres@localhost:5432/medisign"
    )


def _validate_record(record: dict[str, Any]) -> tuple[bool, str]:
    """Validate a knowledge base record for embedding.

    Returns (is_valid, reason) tuple.
    """
    if not record.get("id"):
        return False, "missing 'id'"
    if not record.get("type"):
        return False, "missing 'type'"
    if not record.get("content"):
        return False, "missing 'content'"

    record_type = record.get("type", "")
    if record_type not in TYPE_TO_KIND:
        return False, f"unsupported type '{record_type}'"

    # Disease-specific validation (Req 18.3)
    if record_type == "vietnam_common_disease":
        structured = record.get("structured")
        if not isinstance(structured, dict):
            return False, "disease record missing 'structured' dict"
        if not structured.get("common_symptoms"):
            return False, "disease record missing 'common_symptoms'"
        severity = structured.get("severity") or record.get("severity")
        red_flags = structured.get("red_flags")
        # Req 18.3 only requires non-empty red_flags for high-severity records.
        if severity == "high" and not red_flags:
            return False, "disease record has empty 'red_flags' list"

    return True, ""


def _build_text_for_embedding(record: dict[str, Any]) -> str:
    """Build the text string to encode for a record.

    Uses the 'content' field as primary text, enriched with title and aliases
    for better retrieval quality.
    """
    parts = []
    title = record.get("title", "")
    if title:
        parts.append(title)

    content = record.get("content", "")
    if content:
        parts.append(content)

    # Add aliases for better recall
    aliases = record.get("aliases", [])
    if aliases:
        parts.append(" ".join(aliases))

    return " ".join(parts).strip()


def load_knowledge_base(kb_path: Path) -> list[dict[str, Any]]:
    """Load and parse the knowledge base JSON file."""
    logger.info("Loading knowledge base from %s ...", kb_path)
    with open(kb_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON list, got {type(data).__name__}")
    logger.info("Loaded %d total records", len(data))
    return data


def filter_and_validate(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter records to embeddable types and validate them."""
    valid_records = []
    skipped_type = 0
    skipped_invalid = 0

    for record in records:
        record_type = record.get("type", "")
        if record_type not in TYPE_TO_KIND:
            skipped_type += 1
            continue

        is_valid, reason = _validate_record(record)
        if not is_valid:
            logger.warning("Skipping record '%s': %s", record.get("id", "?"), reason)
            skipped_invalid += 1
            continue

        valid_records.append(record)

    logger.info(
        "Validation complete: %d valid, %d skipped (unsupported type), %d skipped (invalid)",
        len(valid_records),
        skipped_type,
        skipped_invalid,
    )
    return valid_records


def encode_records(
    model: "SentenceTransformer",
    records: list[dict[str, Any]],
    batch_size: int,
) -> list[tuple[str, str, list[float]]]:
    """Encode records into (record_id, kind, embedding) tuples."""
    texts = [_build_text_for_embedding(r) for r in records]
    record_ids = [r["id"] for r in records]
    kinds = [TYPE_TO_KIND[r["type"]] for r in records]

    logger.info("Encoding %d records with %s (batch_size=%d) ...", len(texts), MODEL_NAME, batch_size)
    start = time.time()

    # Encode in batches
    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        batch_embeddings = model.encode(batch_texts, normalize_embeddings=True, show_progress_bar=False)
        for emb in batch_embeddings:
            vec = emb.tolist() if hasattr(emb, "tolist") else list(emb)
            all_embeddings.append(vec)

        if (i + batch_size) % (batch_size * 10) == 0 or i + batch_size >= len(texts):
            logger.info("  Encoded %d / %d", min(i + batch_size, len(texts)), len(texts))

    elapsed = time.time() - start
    logger.info("Encoding complete in %.1fs (%.0f records/sec)", elapsed, len(texts) / max(elapsed, 0.001))

    results = []
    for record_id, kind, embedding in zip(record_ids, kinds, all_embeddings):
        if len(embedding) != EMBEDDING_DIM:
            logger.warning("Dimension mismatch for %s: got %d, expected %d", record_id, len(embedding), EMBEDDING_DIM)
            continue
        results.append((record_id, kind, embedding))

    return results


def upsert_embeddings(
    session: Session,
    embeddings: list[tuple[str, str, list[float]]],
    batch_size: int,
) -> int:
    """Upsert embeddings into kb_embeddings table.

    Uses PostgreSQL ON CONFLICT DO UPDATE for idempotent upserts.
    Returns number of upserted records.
    """
    logger.info("Upserting %d embeddings into kb_embeddings ...", len(embeddings))
    upserted = 0

    for i in range(0, len(embeddings), batch_size):
        batch = embeddings[i : i + batch_size]
        for record_id, kind, embedding in batch:
            # Use raw SQL for upsert with pgvector
            embedding_str = "[" + ",".join(f"{v:.8f}" for v in embedding) + "]"
            session.execute(
                text("""
                    INSERT INTO kb_embeddings (record_id, embedding, kind)
                    VALUES (:record_id, :embedding, :kind)
                    ON CONFLICT (record_id) DO UPDATE
                    SET embedding = EXCLUDED.embedding, kind = EXCLUDED.kind
                """),
                {
                    "record_id": record_id,
                    "embedding": embedding_str,
                    "kind": kind,
                },
            )
            upserted += 1

        session.commit()
        if (i + batch_size) % (batch_size * 5) == 0 or i + batch_size >= len(embeddings):
            logger.info("  Upserted %d / %d", min(i + batch_size, len(embeddings)), len(embeddings))

    logger.info("Upsert complete: %d records", upserted)
    return upserted


def main() -> None:
    parser = argparse.ArgumentParser(description="Build embedding index for knowledge base")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE_DEFAULT, help="Encoding batch size")
    parser.add_argument("--db-url", type=str, default=None, help="Database URL override")
    parser.add_argument("--kb-path", type=str, default=None, help="Knowledge base JSON path override")
    parser.add_argument("--dry-run", action="store_true", help="Validate and encode only, skip DB upsert")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate records, skip encoding and DB (no model load required)",
    )
    args = parser.parse_args()

    kb_path = Path(args.kb_path) if args.kb_path else KB_PATH
    if not kb_path.exists():
        logger.error("Knowledge base not found: %s", kb_path)
        sys.exit(1)

    # Load and validate
    records = load_knowledge_base(kb_path)
    valid_records = filter_and_validate(records)

    if not valid_records:
        logger.warning("No valid records to embed. Exiting.")
        sys.exit(0)

    if args.validate_only:
        logger.info("Validate-only mode: %d records would be encoded.", len(valid_records))
        return

    # Load model
    logger.info("Loading model %s ...", MODEL_NAME)
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        logger.error(
            "sentence-transformers not installed. Install backend dependencies: "
            "pip install sentence-transformers"
        )
        raise SystemExit(1) from exc
    model = SentenceTransformer(MODEL_NAME)

    # Encode
    embeddings = encode_records(model, valid_records, args.batch_size)

    if args.dry_run:
        logger.info("Dry run complete. %d embeddings would be upserted.", len(embeddings))
        return

    # Database upsert
    db_url = args.db_url or _get_database_url()
    logger.info("Connecting to database ...")
    engine = create_engine(db_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        upsert_embeddings(session, embeddings, args.batch_size)

    logger.info("Done! %d embeddings indexed.", len(embeddings))


if __name__ == "__main__":
    main()
