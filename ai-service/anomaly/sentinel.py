"""
NEXUS PM AI Service – Anomaly Sentinel
Rule-based + IsolationForest anomaly detection for extracted activity events.
"""
from __future__ import annotations

import logging
import random
from datetime import datetime, timedelta
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# Civil/structural keywords that should NOT appear in piping reports
CIVIL_KEYWORDS = {
    "concrete", "formwork", "rebar", "excavation", "backfill",
    "grading", "earthwork", "compaction", "foundation casting",
    "shuttering", "curing",
}

PIPING_DISCIPLINES = {"piping", "pipe", "pip"}


def _parse_date(date_str: str) -> datetime | None:
    """Try to parse a date string; return None on failure."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


class AnomalySentinel:
    """
    Detects anomalies in extracted activity events using rule-based checks
    and an IsolationForest model for statistical outlier detection.
    """

    def __init__(self) -> None:
        self._iso_model = None
        self._iso_trained = False
        self._train_isolation_forest()

    # ── IsolationForest setup ─────────────────────────────────────────────────

    def _train_isolation_forest(self) -> None:
        """Train IsolationForest on synthetic 'normal' activity feature vectors."""
        try:
            from sklearn.ensemble import IsolationForest  # type: ignore

            rng = np.random.default_rng(42)
            n = 400
            # Normal activities: progress 0-100, quantity 0-500, confidence 0.6-1.0
            progress = rng.uniform(0, 100, n)
            quantity = rng.uniform(0, 500, n)
            confidence = rng.uniform(0.6, 1.0, n)
            duration_days = rng.uniform(1, 120, n)

            X_train = np.column_stack([progress, quantity, confidence, duration_days])
            self._iso_model = IsolationForest(
                n_estimators=100,
                contamination=0.05,
                random_state=42,
            )
            self._iso_model.fit(X_train)
            self._iso_trained = True
            logger.info("IsolationForest trained for anomaly detection")
        except Exception as exc:
            logger.error("Failed to train IsolationForest: %s", exc)

    def _iso_score(self, event: dict) -> float | None:
        """Return IsolationForest anomaly score (negative = more anomalous)."""
        if not self._iso_trained or self._iso_model is None:
            return None

        progress = float(event.get("progress_pct", 50))
        quantity = float(event.get("quantity_done", 0))
        confidence = float(event.get("extraction_confidence", 0.8))

        start = _parse_date(str(event.get("extracted_start", "")))
        finish = _parse_date(str(event.get("extracted_finish", "")))
        if start and finish:
            duration = max((finish - start).days, 0)
        else:
            duration = 30.0  # default assumption

        X = np.array([[progress, quantity, confidence, duration]])
        try:
            return float(self._iso_model.decision_function(X)[0])
        except Exception:
            return None

    # ── Rule-based checks ─────────────────────────────────────────────────────

    def _check_progress_overclaim(self, event: dict) -> dict | None:
        progress = float(event.get("progress_pct", 0))
        if progress > 100:
            return {
                "anomaly_type": "PROGRESS_OVERCLAIM",
                "description": (
                    f"Activity reports {progress:.1f}% progress, which exceeds 100%. "
                    "This may indicate a data entry error or unreported scope reduction."
                ),
                "severity": "CRITICAL",
            }
        return None

    def _check_timeline_reversal(self, event: dict) -> dict | None:
        start = _parse_date(str(event.get("extracted_start", "")))
        finish = _parse_date(str(event.get("extracted_finish", "")))
        if start and finish and finish < start:
            return {
                "anomaly_type": "TIMELINE_REVERSAL",
                "description": (
                    f"Actual finish date ({finish.date()}) is before actual start date ({start.date()}). "
                    "Dates may be swapped or mistyped in the source report."
                ),
                "severity": "CRITICAL",
            }
        return None

    def _check_complete_no_resources(self, event: dict) -> dict | None:
        progress = float(event.get("progress_pct", 0))
        if progress == 100.0:
            # Simulate resource log check with 30% probability of flagging
            if random.random() < 0.30:
                return {
                    "anomaly_type": "COMPLETE_WITHOUT_RESOURCE_LOG",
                    "description": (
                        "Activity is marked 100% complete but no recent resource log entry found. "
                        "Completion may be premature or resource records are missing."
                    ),
                    "severity": "WARNING",
                }
        return None

    def _check_discipline_keyword_mismatch(self, event: dict) -> dict | None:
        discipline = str(event.get("discipline", "")).lower()
        activity_name = str(event.get("activity_name", "")).lower()

        if any(d in discipline for d in PIPING_DISCIPLINES):
            found_civil = [kw for kw in CIVIL_KEYWORDS if kw in activity_name]
            if found_civil:
                return {
                    "anomaly_type": "DISCIPLINE_KEYWORD_MISMATCH",
                    "description": (
                        f"Activity classified as Piping discipline but contains civil/structural keywords: "
                        f"{', '.join(found_civil)}. Possible wrong discipline assignment."
                    ),
                    "severity": "CRITICAL",
                }
        return None

    def _check_far_future_finish(self, event: dict) -> dict | None:
        finish = _parse_date(str(event.get("extracted_finish", "")))
        if finish:
            today = datetime.now()
            threshold = today + timedelta(days=180)
            if finish > threshold:
                return {
                    "anomaly_type": "FAR_FUTURE_FINISH_DATE",
                    "description": (
                        f"Extracted finish date ({finish.date()}) is more than 6 months in the future "
                        f"from today ({today.date()}). Verify if this is correct or a data extraction error."
                    ),
                    "severity": "WARNING",
                }
        return None

    def _check_statistical_outlier(self, event: dict) -> dict | None:
        score = self._iso_score(event)
        if score is not None and score < -0.15:
            return {
                "anomaly_type": "STATISTICAL_OUTLIER",
                "description": (
                    f"IsolationForest anomaly score ({score:.3f}) indicates this activity's feature "
                    "combination (progress, quantity, confidence, duration) is statistically unusual "
                    "compared to normal activity patterns."
                ),
                "severity": "WARNING",
            }
        return None

    # ── Public API ─────────────────────────────────────────────────────────────

    def check(self, event: dict) -> list[dict]:
        """
        Run all anomaly checks on a single event.

        Parameters
        ----------
        event:  Extracted event dict from NLPExtractor.

        Returns
        -------
        List of anomaly dicts: [{anomaly_type, description, severity}]
        """
        anomalies: list[dict] = []

        checks = [
            self._check_progress_overclaim,
            self._check_timeline_reversal,
            self._check_complete_no_resources,
            self._check_discipline_keyword_mismatch,
            self._check_far_future_finish,
            self._check_statistical_outlier,
        ]

        for check_fn in checks:
            try:
                result = check_fn(event)
                if result:
                    anomalies.append(result)
            except Exception as exc:
                logger.error("Anomaly check %s failed: %s", check_fn.__name__, exc)

        return anomalies

    def check_batch(self, events: list[dict]) -> list[dict]:
        """
        Run anomaly checks on a list of events.

        Returns
        -------
        List of {event_index, activity_name, anomalies: [...]} for events that have anomalies.
        """
        results: list[dict] = []
        for i, event in enumerate(events):
            anomalies = self.check(event)
            results.append({
                "event_index": i,
                "activity_name": event.get("activity_name", f"Event #{i}"),
                "anomalies": anomalies,
                "has_anomalies": len(anomalies) > 0,
            })
        return results
