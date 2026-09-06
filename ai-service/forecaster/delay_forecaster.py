"""
NEXUS PM AI Service – Delay Forecaster
Uses XGBoost + scikit-learn to predict project delay in days, with Gemini narrative generation.
"""
from __future__ import annotations

import json
import logging
import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np

from config import settings
from mock_responses import MOCK_FORECAST
from prompts.extraction_prompt import FORECAST_NARRATIVE_PROMPT

logger = logging.getLogger(__name__)

# ── Feature definitions ───────────────────────────────────────────────────────

DISCIPLINE_CODES = {
    "Civil": 0,
    "Piping": 1,
    "Electrical": 2,
    "Mechanical": 3,
    "Instrumentation": 4,
    "Structural": 5,
    "General": 6,
}

SEASON_CODES = {
    "Q1": 0,   # Jan-Mar
    "Q2": 1,   # Apr-Jun (pre-monsoon)
    "Q3": 2,   # Jul-Sep (monsoon – lower productivity)
    "Q4": 3,   # Oct-Dec
}

FEATURE_NAMES = [
    "spi",
    "planned_duration_days",
    "elapsed_pct",
    "discipline_code",
    "float_days",
    "num_resources",
    "season_code",
]

MODEL_PATH = Path(settings.MODEL_SAVE_PATH) / "delay_xgb.pkl"


def _get_gemini_model():
    """Lazy-load Gemini model for narrative generation."""
    try:
        import google.generativeai as genai  # type: ignore

        if not settings.GEMINI_API_KEY:
            return None
        genai.configure(api_key=settings.GEMINI_API_KEY)
        return genai.GenerativeModel(settings.GEMINI_MODEL)
    except Exception as exc:
        logger.error("Gemini init failed in forecaster: %s", exc)
        return None


def _season_code_from_date(dt: datetime) -> int:
    m = dt.month
    if m <= 3:
        return 0
    if m <= 6:
        return 1
    if m <= 9:
        return 2
    return 3


class DelayForecaster:
    """
    XGBoost-based delay forecaster with Gemini narrative generation.

    Features used:
      spi, planned_duration_days, elapsed_pct, discipline_code,
      float_days, num_resources, season_code
    """

    def __init__(self) -> None:
        self._model = None
        self._trained = False
        self._ensure_model_dir()

    def _ensure_model_dir(self) -> None:
        Path(settings.MODEL_SAVE_PATH).mkdir(parents=True, exist_ok=True)

    # ── Training ──────────────────────────────────────────────────────────────

    def train_on_synthetic(self) -> None:
        """
        Generate 500 synthetic training samples and train an XGBoost regressor
        to predict delay_days.  Saves the model to disk.
        """
        from sklearn.model_selection import train_test_split  # type: ignore
        from xgboost import XGBRegressor  # type: ignore

        rng = np.random.default_rng(42)
        n = 500

        # ── Synthetic feature generation ──────────────────────────────────────
        spi = rng.uniform(0.55, 1.25, n)
        planned_duration = rng.integers(30, 400, n).astype(float)
        elapsed_pct = rng.uniform(10, 95, n)
        discipline_code = rng.integers(0, 7, n).astype(float)
        float_days = rng.uniform(-10, 60, n)
        num_resources = rng.integers(5, 150, n).astype(float)
        season_code = rng.integers(0, 4, n).astype(float)

        # ── Realistic delay target ────────────────────────────────────────────
        # delay_days increases as SPI drops, float decreases, monsoon season hits
        delay_days = (
            (1.0 - spi) * 80                        # SPI impact
            + np.where(float_days < 0, -float_days * 1.5, 0)   # negative float penalty
            + np.where(season_code == 2, 8, 0)       # monsoon penalty
            + np.where(discipline_code == 1, 5, 0)   # piping complexity
            + rng.normal(0, 4, n)                    # noise
        )
        delay_days = np.clip(delay_days, -15, 120)   # realistic range

        X = np.column_stack([
            spi, planned_duration, elapsed_pct,
            discipline_code, float_days, num_resources, season_code,
        ])
        y = delay_days

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = XGBRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.08,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

        self._model = model
        self._trained = True

        # Persist model
        try:
            with open(MODEL_PATH, "wb") as f:
                pickle.dump(model, f)
            logger.info("Delay XGBoost model saved to %s", MODEL_PATH)
        except Exception as exc:
            logger.warning("Could not save model: %s", exc)

        from sklearn.metrics import mean_absolute_error  # type: ignore

        mae = mean_absolute_error(y_test, model.predict(X_test))
        logger.info("Delay model trained – MAE on test set: %.2f days", mae)

    def _load_or_train(self) -> None:
        """Load persisted model or train fresh if not found."""
        if self._trained:
            return
        if MODEL_PATH.exists():
            try:
                with open(MODEL_PATH, "rb") as f:
                    self._model = pickle.load(f)
                self._trained = True
                logger.info("Loaded existing delay model from %s", MODEL_PATH)
                return
            except Exception as exc:
                logger.warning("Could not load model, retraining: %s", exc)
        self.train_on_synthetic()

    # ── Prediction ────────────────────────────────────────────────────────────

    def predict(self, project_metrics: dict) -> dict:
        """
        Predict project delay and generate a Gemini narrative.

        Parameters
        ----------
        project_metrics: dict with keys:
          spi (float), planned_duration_days (int), elapsed_pct (float),
          discipline (str), float_days (float), num_resources (int),
          planned_finish_date (str YYYY-MM-DD), productivity_notes (str, optional)

        Returns
        -------
        {
          predicted_finish_date: str,
          delay_days: int,
          confidence: 'high'|'medium'|'low',
          risk_factors: [{factor, impact, explanation}],
          narrative: str,
        }
        """
        if settings.MOCK_MODE:
            return MOCK_FORECAST

        self._load_or_train()

        # ── Extract features ──────────────────────────────────────────────────
        spi = float(project_metrics.get("spi", 1.0))
        planned_duration = float(project_metrics.get("planned_duration_days", 180))
        elapsed_pct = float(project_metrics.get("elapsed_pct", 50.0))
        discipline = str(project_metrics.get("discipline", "General"))
        discipline_code = float(DISCIPLINE_CODES.get(discipline, 6))
        float_days = float(project_metrics.get("float_days", 0))
        num_resources = float(project_metrics.get("num_resources", 30))

        today = datetime.now()
        season_code = float(_season_code_from_date(today))

        X = np.array([[spi, planned_duration, elapsed_pct,
                        discipline_code, float_days, num_resources, season_code]])

        try:
            delay_days_raw = float(self._model.predict(X)[0])
        except Exception as exc:
            logger.error("XGBoost predict failed: %s", exc)
            return MOCK_FORECAST

        delay_days = int(round(delay_days_raw))

        # ── Compute predicted finish date ──────────────────────────────────────
        planned_finish_str = project_metrics.get("planned_finish_date", "")
        try:
            planned_finish = datetime.strptime(planned_finish_str, "%Y-%m-%d")
        except Exception:
            # Estimate: today + remaining planned days
            remaining = planned_duration * (1 - elapsed_pct / 100)
            planned_finish = today + timedelta(days=remaining)

        predicted_finish = planned_finish + timedelta(days=delay_days)

        # ── Confidence ────────────────────────────────────────────────────────
        if elapsed_pct > 60 and float_days > -5:
            confidence = "high"
        elif elapsed_pct > 30:
            confidence = "medium"
        else:
            confidence = "low"

        # ── Risk factors ──────────────────────────────────────────────────────
        risk_factors = self._compute_risk_factors(
            spi, float_days, season_code, discipline, delay_days
        )

        # ── Narrative ─────────────────────────────────────────────────────────
        narrative = self._generate_narrative(
            spi=spi,
            elapsed_pct=elapsed_pct,
            delay_days=delay_days,
            predicted_finish=predicted_finish.strftime("%Y-%m-%d"),
            risk_factors=risk_factors,
            productivity_notes=str(project_metrics.get("productivity_notes", "")),
        )

        return {
            "predicted_finish_date": predicted_finish.strftime("%Y-%m-%d"),
            "delay_days": delay_days,
            "confidence": confidence,
            "risk_factors": risk_factors,
            "narrative": narrative,
        }

    def _compute_risk_factors(
        self,
        spi: float,
        float_days: float,
        season_code: float,
        discipline: str,
        delay_days: int,
    ) -> list[dict]:
        factors = []

        if spi < 0.85:
            factors.append({
                "factor": "Low Schedule Performance Index",
                "impact": "HIGH" if spi < 0.70 else "MEDIUM",
                "explanation": f"SPI of {spi:.2f} indicates the project is performing below planned schedule velocity.",
            })

        if float_days < 0:
            factors.append({
                "factor": "Negative Schedule Float",
                "impact": "HIGH",
                "explanation": f"Critical path has {abs(int(float_days))} days of negative float – any further slippage directly delays the project finish.",
            })

        if season_code == 2:
            factors.append({
                "factor": "Monsoon Season Productivity Loss",
                "impact": "MEDIUM",
                "explanation": "Current monsoon season (Jul–Sep) typically reduces outdoor civil and piping productivity by 10–20%.",
            })

        if discipline == "Piping" and delay_days > 10:
            factors.append({
                "factor": "Piping Critical Path Risk",
                "impact": "HIGH",
                "explanation": "Piping is often on the critical path in EPC projects; delays compound quickly across dependent activities.",
            })

        if not factors:
            factors.append({
                "factor": "General Schedule Pressure",
                "impact": "LOW",
                "explanation": f"Project shows minor schedule variance of {delay_days} days – manageable with resource optimisation.",
            })

        return factors[:3]

    def _generate_narrative(
        self,
        spi: float,
        elapsed_pct: float,
        delay_days: int,
        predicted_finish: str,
        risk_factors: list[dict],
        productivity_notes: str,
    ) -> str:
        model = _get_gemini_model()
        if model is None:
            return MOCK_FORECAST["narrative"]

        risk_str = "; ".join(f"{r['factor']} ({r['impact']})" for r in risk_factors)
        prompt = FORECAST_NARRATIVE_PROMPT.format(
            spi=f"{spi:.2f}",
            elapsed_pct=f"{elapsed_pct:.1f}",
            productivity_notes=productivity_notes or "No specific productivity data provided.",
            delay_days=delay_days,
            predicted_finish=predicted_finish,
            risk_factors=risk_str,
        )

        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as exc:
            logger.error("Gemini narrative generation failed: %s", exc)
            return MOCK_FORECAST["narrative"]
