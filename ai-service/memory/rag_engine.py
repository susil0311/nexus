"""
NEXUS PM AI Service – RAG Engine
ChromaDB-backed institutional memory with Gemini synthesis.
"""
from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from config import settings
from mock_responses import MOCK_MEMORY_ANSWER
from prompts.extraction_prompt import RAG_SYNTHESIS_PROMPT

logger = logging.getLogger(__name__)

COLLECTION_NAME = "institutional_memory"

# ── Seed records – realistic EPC institutional memory ─────────────────────────

SEED_RECORDS: list[dict] = [
    {
        "project_code": "REFINERY-ALPHA",
        "discipline": "Piping",
        "activity_type": "Large-bore spool fabrication and erection",
        "planned_duration": 180,
        "actual_duration": 172,
        "notes": (
            "Pre-fabrication strategy delivered 31% productivity improvement. Peak crew 42 welders. "
            "Benchmark achieved: 16.2 inch-dia meters per man-day for 12-inch and above."
        ),
    },
    {
        "project_code": "PETROGAS-DELTA",
        "discipline": "Piping",
        "activity_type": "Process piping installation – congested area",
        "planned_duration": 210,
        "actual_duration": 241,
        "notes": (
            "Congested work areas reduced productivity to 13.8 ID-m/MD. "
            "Phased area access and scaffold pre-planning recommended."
        ),
    },
    {
        "project_code": "LNG-TERMINAL-BRAVO",
        "discipline": "Piping",
        "activity_type": "Cryogenic piping – insulation and jacketing",
        "planned_duration": 90,
        "actual_duration": 95,
        "notes": "Specialist insulation crew mobilisation 5-day delay. Book specialist crews 8 weeks ahead.",
    },
    {
        "project_code": "COASTAL-REFINERY-3",
        "discipline": "Civil",
        "activity_type": "Piling works – large diameter bored piles",
        "planned_duration": 120,
        "actual_duration": 138,
        "notes": (
            "Monsoon season caused 18-day delay. Productivity 22% below benchmark during monsoon months. "
            "Schedule monsoon-sensitive civil work before July or after October."
        ),
    },
    {
        "project_code": "COASTAL-REFINERY-3",
        "discipline": "Civil",
        "activity_type": "Structural concrete works – equipment pads",
        "planned_duration": 60,
        "actual_duration": 58,
        "notes": "Achieved early completion by pre-arranging concrete batch plants on-site. Rebar pre-fabrication off-site saved 3 days.",
    },
    {
        "project_code": "GAS-PLANT-ECHO",
        "discipline": "Electrical",
        "activity_type": "MV cable laying and termination",
        "planned_duration": 75,
        "actual_duration": 82,
        "notes": (
            "7-day overrun due to MV cable delivery delay. Always maintain 30-day buffer stock. "
            "Termination productivity: 8 terminations per gang per day achievable."
        ),
    },
    {
        "project_code": "GAS-PLANT-ECHO",
        "discipline": "Instrumentation",
        "activity_type": "Field instrument loop calibration and testing",
        "planned_duration": 45,
        "actual_duration": 51,
        "notes": (
            "Loop count increased by 12% vs design. Always carry 15% loop count contingency. "
            "Peak productivity: 12 loops per day with 4 technicians."
        ),
    },
    {
        "project_code": "AMMONIA-PLANT-FOXTROT",
        "discipline": "Mechanical",
        "activity_type": "Rotating equipment installation and alignment",
        "planned_duration": 55,
        "actual_duration": 55,
        "notes": (
            "On-time delivery. Key success: vendor pre-commissioning support mobilised 2 weeks before mechanical completion. "
            "Use laser alignment tools to reduce re-alignment risk."
        ),
    },
    {
        "project_code": "PETROGAS-DELTA",
        "discipline": "Structural",
        "activity_type": "Steel erection – pipe racks and equipment platforms",
        "planned_duration": 90,
        "actual_duration": 101,
        "notes": (
            "11-day overrun due to crane availability conflicts. "
            "Recommend dedicated crane allocation for steel erection phase. "
            "Productivity benchmark: 18–22 tonnes per crane-day."
        ),
    },
    {
        "project_code": "AMMONIA-PLANT-FOXTROT",
        "discipline": "Piping",
        "activity_type": "Hydrostatic testing – high pressure systems",
        "planned_duration": 30,
        "actual_duration": 34,
        "notes": (
            "4-day overrun due to re-testing after failed welds. Weld rejection rate was 3.8% vs 1.5% target. "
            "Implement mandatory 100% RT for pressure class above 1500# to catch defects early."
        ),
    },
]


def _get_st_model():
    """Lazy-load SentenceTransformer."""
    from sentence_transformers import SentenceTransformer  # type: ignore

    return SentenceTransformer(settings.EMBEDDING_MODEL)


def _get_chroma_client():
    """Lazy-load ChromaDB persistent client."""
    import chromadb  # type: ignore

    return chromadb.PersistentClient(path=settings.CHROMADB_PATH)


def _get_gemini_model():
    """Lazy-load Gemini model."""
    try:
        import google.generativeai as genai  # type: ignore

        if not settings.GEMINI_API_KEY:
            return None
        genai.configure(api_key=settings.GEMINI_API_KEY)
        return genai.GenerativeModel(settings.GEMINI_MODEL)
    except Exception as exc:
        logger.error("Gemini init failed in RAG engine: %s", exc)
        return None


def _record_to_text(record: dict) -> str:
    """Convert a memory record to a searchable text string."""
    parts = [
        record.get("activity_type", ""),
        record.get("discipline", ""),
        record.get("project_code", ""),
        record.get("notes", ""),
    ]
    return " ".join(filter(None, parts))


class RAGEngine:
    """
    Retrieval-Augmented Generation engine backed by ChromaDB institutional memory.
    Stores past project records and uses Gemini to synthesize answers.
    """

    def __init__(self) -> None:
        self._st_model = None
        self._chroma_client = None
        self._collection = None

    def _ensure_initialized(self) -> None:
        if self._collection is not None:
            return
        self._st_model = _get_st_model()
        self._chroma_client = _get_chroma_client()
        self._collection = self._chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def _seed_if_empty(self) -> None:
        """Insert seed records if the collection is empty."""
        self._ensure_initialized()
        try:
            count = self._collection.count()
        except Exception:
            count = 0

        if count == 0:
            logger.info("Seeding institutional memory with %d records", len(SEED_RECORDS))
            self.index_memory(SEED_RECORDS)

    # ── Public API ─────────────────────────────────────────────────────────────

    def index_memory(self, records: list[dict]) -> int:
        """
        Embed and store institutional memory records in ChromaDB.

        Parameters
        ----------
        records:  List of dicts with keys:
                  project_code, discipline, activity_type,
                  planned_duration, actual_duration, notes

        Returns
        -------
        Number of records indexed.
        """
        self._ensure_initialized()

        texts: list[str] = []
        ids: list[str] = []
        metadatas: list[dict] = []

        for record in records:
            text = _record_to_text(record)
            rec_id = str(uuid.uuid4())
            texts.append(text)
            ids.append(rec_id)
            metadatas.append({
                "project_code": str(record.get("project_code", "")),
                "discipline": str(record.get("discipline", "")),
                "activity_type": str(record.get("activity_type", "")),
                "planned_duration": str(record.get("planned_duration", "")),
                "actual_duration": str(record.get("actual_duration", "")),
                "notes": str(record.get("notes", "")),
            })

        if not ids:
            return 0

        embeddings = self._st_model.encode(texts, show_progress_bar=False).tolist()
        self._collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas)
        logger.info("Indexed %d institutional memory records", len(ids))
        return len(ids)

    def query(self, question: str, context: dict | None = None) -> dict:
        """
        Retrieve relevant records and synthesize an answer with Gemini.

        Parameters
        ----------
        question:  Natural language question from the project engineer.
        context:   Optional dict with current project context.

        Returns
        -------
        {
          answer: str,
          sources: [{project_code, discipline, activity_type, planned_duration, actual_duration, notes}],
          confidence: str,
        }
        """
        if settings.MOCK_MODE:
            return MOCK_MEMORY_ANSWER

        self._seed_if_empty()

        # ── Semantic retrieval ─────────────────────────────────────────────────
        try:
            query_embedding = self._st_model.encode(question, show_progress_bar=False).tolist()
            count = self._collection.count()
            n_results = min(5, max(count, 1))
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["metadatas", "distances"],
            )
            retrieved = results["metadatas"][0]
        except Exception as exc:
            logger.error("ChromaDB query failed: %s", exc)
            retrieved = []

        if not retrieved:
            return {
                "answer": "No relevant institutional memory records found for this question.",
                "sources": [],
                "confidence": "low",
            }

        # ── Format sources ─────────────────────────────────────────────────────
        sources = [
            {
                "project_code": r.get("project_code", ""),
                "discipline": r.get("discipline", ""),
                "activity_type": r.get("activity_type", ""),
                "planned_duration": r.get("planned_duration", ""),
                "actual_duration": r.get("actual_duration", ""),
                "notes": r.get("notes", ""),
            }
            for r in retrieved
        ]

        # ── Gemini synthesis ───────────────────────────────────────────────────
        model = _get_gemini_model()
        if model is None:
            return MOCK_MEMORY_ANSWER

        records_str = "\n\n".join(
            f"[{s['project_code']} | {s['discipline']} | {s['activity_type']}]\n"
            f"Planned: {s['planned_duration']} days | Actual: {s['actual_duration']} days\n"
            f"Notes: {s['notes']}"
            for s in sources
        )
        context_str = json.dumps(context or {}, indent=2)

        prompt = RAG_SYNTHESIS_PROMPT.format(
            question=question,
            context=context_str,
            retrieved_records=records_str,
        )

        try:
            response = model.generate_content(prompt)
            answer = response.text.strip()
            confidence = "high" if len(sources) >= 3 else "medium"
        except Exception as exc:
            logger.error("Gemini RAG synthesis failed: %s", exc)
            answer = MOCK_MEMORY_ANSWER["answer"]
            confidence = "low"

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
        }

    def seed_memory(self) -> int:
        """Public method to force-seed institutional memory records."""
        self._ensure_initialized()
        return self.index_memory(SEED_RECORDS)
