"""
NEXUS PM AI Service – Activity Embedder
Uses sentence-transformers + ChromaDB for semantic activity indexing and retrieval.
"""
from __future__ import annotations

import logging
from typing import Any

from config import settings

logger = logging.getLogger(__name__)

# Lazy imports to avoid slow startup when not needed
_st_model = None
_chroma_client = None


def _get_st_model():
    """Lazy-load SentenceTransformer model."""
    global _st_model
    if _st_model is None:
        from sentence_transformers import SentenceTransformer  # type: ignore

        logger.info("Loading SentenceTransformer: %s", settings.EMBEDDING_MODEL)
        _st_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _st_model


def _get_chroma_client():
    """Lazy-load persistent ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        import chromadb  # type: ignore

        logger.info("Connecting to ChromaDB at: %s", settings.CHROMADB_PATH)
        _chroma_client = chromadb.PersistentClient(path=settings.CHROMADB_PATH)
    return _chroma_client


class ActivityEmbedder:
    """
    Semantic search index for WBS / schedule node names using
    sentence-transformers (all-MiniLM-L6-v2) + ChromaDB.
    """

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _collection_name(self, project_id: str) -> str:
        # ChromaDB collection names must be alphanum + underscores/hyphens
        safe = "".join(c if c.isalnum() else "_" for c in project_id)
        return f"project_{safe}"

    def _get_or_create_collection(self, project_id: str):
        client = _get_chroma_client()
        name = self._collection_name(project_id)
        return client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )

    # ── Public API ─────────────────────────────────────────────────────────────

    def index_schedule_nodes(self, nodes: list[dict], project_id: str) -> int:
        """
        Embed all schedule node names and store in ChromaDB.

        Parameters
        ----------
        nodes:       List of dicts with at least 'node_id' and 'node_name'.
                     Optional fields: discipline, activity_type, wbs_code.
        project_id:  Project identifier – used as collection name.

        Returns
        -------
        Number of nodes indexed.
        """
        if not nodes:
            logger.warning("index_schedule_nodes called with empty list")
            return 0

        model = _get_st_model()
        collection = self._get_or_create_collection(project_id)

        texts: list[str] = []
        ids: list[str] = []
        metadatas: list[dict] = []

        for node in nodes:
            node_id = str(node.get("node_id", node.get("id", "")))
            node_name = str(node.get("node_name", node.get("name", "")))
            if not node_id or not node_name:
                continue

            # Enrich text with optional metadata for better matching
            discipline = str(node.get("discipline", ""))
            activity_type = str(node.get("activity_type", ""))
            search_text = " ".join(filter(None, [node_name, discipline, activity_type]))

            ids.append(node_id)
            texts.append(search_text)
            metadatas.append(
                {
                    "node_id": node_id,
                    "node_name": node_name,
                    "discipline": discipline,
                    "activity_type": activity_type,
                    "wbs_code": str(node.get("wbs_code", "")),
                }
            )

        if not ids:
            logger.warning("No valid nodes to index (missing node_id or node_name)")
            return 0

        # Batch embed
        embeddings = model.encode(texts, show_progress_bar=False).tolist()

        # Upsert in batches of 100 (ChromaDB limit)
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            collection.upsert(
                ids=ids[i : i + batch_size],
                embeddings=embeddings[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
            )

        logger.info("Indexed %d nodes for project '%s'", len(ids), project_id)
        return len(ids)

    def search(
        self,
        query: str,
        project_id: str,
        n_results: int = 5,
    ) -> list[dict]:
        """
        Semantic search for schedule nodes matching the query.

        Parameters
        ----------
        query:      Field description or activity name from the report.
        project_id: Project identifier.
        n_results:  Number of top matches to return.

        Returns
        -------
        List of dicts: {node_id, node_name, discipline, activity_type, distance, score}
        score = 1 - cosine_distance  (1.0 = perfect match)
        """
        model = _get_st_model()
        collection = self._get_or_create_collection(project_id)

        try:
            count = collection.count()
        except Exception:
            count = 0

        if count == 0:
            logger.warning("Collection for project '%s' is empty", project_id)
            return []

        query_embedding = model.encode(query, show_progress_bar=False).tolist()

        actual_n = min(n_results, count)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=actual_n,
            include=["metadatas", "distances"],
        )

        matches: list[dict] = []
        for meta, dist in zip(
            results["metadatas"][0],
            results["distances"][0],
        ):
            matches.append(
                {
                    "node_id": meta.get("node_id", ""),
                    "node_name": meta.get("node_name", ""),
                    "discipline": meta.get("discipline", ""),
                    "activity_type": meta.get("activity_type", ""),
                    "distance": float(dist),
                    "score": float(1.0 - dist),  # cosine similarity
                }
            )

        # Sort by score descending
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches

    def clear_project_index(self, project_id: str) -> bool:
        """Delete the ChromaDB collection for a project."""
        client = _get_chroma_client()
        name = self._collection_name(project_id)
        try:
            client.delete_collection(name)
            logger.info("Deleted collection '%s'", name)
            return True
        except Exception as exc:
            logger.error("Failed to delete collection '%s': %s", name, exc)
            return False
