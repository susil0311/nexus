"""
NEXUS PM AI Service – Fuzzy / Semantic Matcher
Maps field report activity descriptions to baseline WBS schedule nodes.
"""
from __future__ import annotations

import logging
from typing import Any

from config import settings
from matcher.embedder import ActivityEmbedder
from mock_responses import MOCK_MATCHES

logger = logging.getLogger(__name__)

# Thresholds
SCORE_AUTO_ACCEPT = 0.85   # >= this: auto_accepted, no human review needed
SCORE_REVIEW_MIN = 0.50    # between 0.50 and 0.85: needs_review
# < 0.50: flagged as potential new activity


class FuzzyMatcher:
    """
    Semantic activity matcher that uses ChromaDB embeddings to match
    field descriptions to scheduled WBS nodes.
    """

    def __init__(self) -> None:
        self._embedder = ActivityEmbedder()

    # ── Core match logic ──────────────────────────────────────────────────────

    def match(
        self,
        field_description: str,
        project_id: str,
        discipline_hint: str | None = None,
    ) -> dict:
        """
        Match a single field description to the best baseline schedule node.

        Parameters
        ----------
        field_description:  Activity name/description from the field report.
        project_id:         Project identifier used for ChromaDB collection lookup.
        discipline_hint:    Optional discipline to improve match quality.

        Returns
        -------
        {
          top_match: {node_id, node_name, score, match_status, explanation},
          candidates: [{node_id, node_name, score}, ...],  # top 3
          needs_review: bool,
          is_new_activity: bool,
        }
        """
        if settings.MOCK_MODE:
            # Return first mock match entry
            mock = MOCK_MATCHES[0].copy()
            mock["field_description"] = field_description
            return mock

        # Build enriched query
        query = field_description
        if discipline_hint:
            query = f"{discipline_hint} {field_description}"

        try:
            candidates = self._embedder.search(query, project_id, n_results=5)
        except Exception as exc:
            logger.error("Embedding search failed: %s", exc)
            candidates = []

        if not candidates:
            return self._new_activity_result(field_description)

        top = candidates[0]
        score = top["score"]
        top3 = [
            {"node_id": c["node_id"], "node_name": c["node_name"], "score": round(c["score"], 4)}
            for c in candidates[:3]
        ]

        if score >= SCORE_AUTO_ACCEPT:
            status = "auto_accepted"
            needs_review = False
            is_new = False
            explanation = (
                f"Strong semantic match (score={score:.3f}). Activity automatically linked to schedule node."
            )
        elif score >= SCORE_REVIEW_MIN:
            status = "needs_review"
            needs_review = True
            is_new = False
            explanation = (
                f"Moderate match (score={score:.3f}). Human review recommended to confirm correct schedule node."
            )
        else:
            status = "flagged_new"
            needs_review = True
            is_new = True
            explanation = (
                f"Low confidence (score={score:.3f}). No close match in baseline schedule – "
                "this may be a new activity or out-of-scope work."
            )

        return {
            "field_description": field_description,
            "top_match": {
                "node_id": top["node_id"],
                "node_name": top["node_name"],
                "score": round(score, 4),
                "match_status": status,
                "explanation": explanation,
            },
            "candidates": top3,
            "needs_review": needs_review,
            "is_new_activity": is_new,
        }

    def _new_activity_result(self, field_description: str) -> dict:
        return {
            "field_description": field_description,
            "top_match": {
                "node_id": None,
                "node_name": None,
                "score": 0.0,
                "match_status": "flagged_new",
                "explanation": "No schedule nodes indexed for this project, or embedding search failed.",
            },
            "candidates": [],
            "needs_review": True,
            "is_new_activity": True,
        }

    # ── Batch processing ──────────────────────────────────────────────────────

    def match_batch(
        self,
        events: list[dict],
        project_id: str,
    ) -> list[dict]:
        """
        Match a list of extracted events to schedule nodes.

        Parameters
        ----------
        events:     List of event dicts from NLPExtractor (must have 'activity_name').
        project_id: Project identifier.

        Returns
        -------
        List of match result dicts, one per event.
        """
        if settings.MOCK_MODE:
            # Return varied mock results cycling through MOCK_MATCHES
            results = []
            for i, event in enumerate(events):
                mock = MOCK_MATCHES[i % len(MOCK_MATCHES)].copy()
                mock["field_description"] = event.get("activity_name", "")
                results.append(mock)
            return results

        results: list[dict] = []
        for event in events:
            activity_name = event.get("activity_name", "")
            discipline = event.get("discipline", None)
            match_result = self.match(activity_name, project_id, discipline_hint=discipline)
            # Attach original event metadata
            match_result["event"] = event
            results.append(match_result)

        return results
