"""
NEXUS PM AI Service – NLP Extractor
Uses Gemini 1.5 Flash to extract structured activity data from DPR text / Excel files.
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

import pandas as pd

from config import settings
from prompts.extraction_prompt import EXTRACTION_PROMPT, EXCEL_INTERPRETATION_PROMPT
from mock_responses import MOCK_EXTRACTION

logger = logging.getLogger(__name__)

# ── Gemini setup ─────────────────────────────────────────────────────────────
_gemini_model = None


def _get_gemini_model():
    """Lazy-load Gemini model; returns None if not configured."""
    global _gemini_model
    if _gemini_model is not None:
        return _gemini_model
    try:
        import google.generativeai as genai  # type: ignore

        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set – AI extraction unavailable")
            return None
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
        return _gemini_model
    except Exception as exc:
        logger.error("Failed to initialize Gemini: %s", exc)
        return None


def _parse_json_from_response(text: str) -> list[dict]:
    """Robustly extract a JSON array from Gemini's free-text response."""
    # Remove markdown fences if present
    cleaned = re.sub(r"```(?:json)?", "", text).strip().strip("`").strip()

    # Try direct parse
    try:
        result = json.loads(cleaned)
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            # Some models wrap in {"events": [...]}
            for key in ("events", "activities", "data", "results"):
                if key in result and isinstance(result[key], list):
                    return result[key]
        return []
    except json.JSONDecodeError:
        pass

    # Fallback: extract first [...] block
    match = re.search(r"\[.*?\]", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    logger.error("Could not parse JSON from Gemini response: %s", text[:500])
    return []


def _sanitize_event(raw: dict) -> dict:
    """Ensure every event has the expected keys with safe defaults."""
    return {
        "activity_name": str(raw.get("activity_name", raw.get("name", "Unknown Activity"))),
        "discipline": str(raw.get("discipline", "Unknown")),
        "extracted_start": str(raw.get("extracted_start", raw.get("start_date", ""))),
        "extracted_finish": str(raw.get("extracted_finish", raw.get("end_date", raw.get("finish_date", "")))),
        "progress_pct": float(raw.get("progress_pct", raw.get("progress", raw.get("completion_percentage", 0)))),
        "quantity_done": float(raw.get("quantity_done", raw.get("quantity", 0))),
        "location_tag": str(raw.get("location_tag", raw.get("location", ""))),
        "supervisor_name": str(raw.get("supervisor_name", raw.get("supervisor", ""))),
        "extraction_confidence": float(raw.get("extraction_confidence", raw.get("confidence", 0.75))),
    }


class NLPExtractor:
    """
    Extract structured activity events from DPR text or Excel reports
    using Gemini 1.5 Flash with graceful fallback to mock data.
    """

    # ─────────────────────────────── Text extraction ──────────────────────────

    def extract_from_text(
        self,
        text: str,
        discipline: str = "General",
        project_context: dict | None = None,
    ) -> list[dict]:
        """
        Extract activity events from free-form DPR / field-report text.

        Parameters
        ----------
        text:             Raw DPR or progress report text.
        discipline:       Hint for which discipline this report belongs to.
        project_context:  Optional dict with project metadata (name, start_date, etc.)

        Returns
        -------
        List of dicts each containing:
          activity_name, discipline, extracted_start, extracted_finish,
          progress_pct, quantity_done, location_tag, supervisor_name,
          extraction_confidence
        """
        if settings.MOCK_MODE:
            logger.info("MOCK_MODE: returning mock extraction results")
            return MOCK_EXTRACTION

        model = _get_gemini_model()
        if model is None:
            logger.warning("Gemini unavailable – returning mock extraction")
            return MOCK_EXTRACTION

        context_str = json.dumps(project_context or {}, indent=2)
        prompt = EXTRACTION_PROMPT.format(
            discipline=discipline,
            project_context=context_str,
            report_text=text,
        )

        try:
            response = model.generate_content(prompt)
            raw_events = _parse_json_from_response(response.text)
            if not raw_events:
                logger.warning("Gemini returned no parseable events; using mock")
                return MOCK_EXTRACTION
            return [_sanitize_event(e) for e in raw_events]
        except Exception as exc:
            logger.error("Gemini extraction failed: %s", exc)
            return MOCK_EXTRACTION

    # ─────────────────────────────── Excel extraction ─────────────────────────

    def extract_from_excel(
        self,
        file_path: str,
        discipline: str = "General",
    ) -> list[dict]:
        """
        Read an Excel file with pandas, then ask Gemini to interpret the rows.

        Parameters
        ----------
        file_path:   Absolute path to the .xlsx / .xls file.
        discipline:  Discipline hint.

        Returns
        -------
        List of extracted event dicts (same schema as extract_from_text).
        """
        if settings.MOCK_MODE:
            return MOCK_EXTRACTION

        path = Path(file_path)
        if not path.exists():
            logger.error("Excel file not found: %s", file_path)
            return []

        try:
            df = pd.read_excel(path, nrows=200)
        except Exception as exc:
            logger.error("Failed to read Excel file: %s", exc)
            return MOCK_EXTRACTION

        # Convert to a compact markdown-like table string for Gemini
        columns = list(df.columns)
        sample_rows = df.head(20).fillna("").to_dict(orient="records")
        table_text = f"Columns: {columns}\n\nFirst {len(sample_rows)} rows:\n"
        for i, row in enumerate(sample_rows):
            table_text += f"Row {i+1}: {row}\n"

        model = _get_gemini_model()
        if model is None:
            logger.warning("Gemini unavailable – returning mock extraction from Excel")
            return MOCK_EXTRACTION

        prompt = EXCEL_INTERPRETATION_PROMPT.format(
            discipline=discipline,
            table_text=table_text,
        )

        try:
            response = model.generate_content(prompt)
            raw_events = _parse_json_from_response(response.text)
            if not raw_events:
                logger.warning("Gemini returned no events from Excel; using mock")
                return MOCK_EXTRACTION
            return [_sanitize_event(e) for e in raw_events]
        except Exception as exc:
            logger.error("Gemini Excel extraction failed: %s", exc)
            return MOCK_EXTRACTION
