"""
ml_service.py
Loads model.pkl once at startup and exposes run_prediction() (one call)
and run_predictions() (batch, used by the bulk dataset loader).
"""
import os
from typing import List

import joblib
import pandas as pd

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "ml", "model.pkl")

_payload    = joblib.load(_MODEL_PATH)
_model      = _payload["model"]
_encoders   = _payload["encoders"]
_features   = _payload["features"]

_CATEGORICAL = ["outcome", "interest", "customer_status"]

# Small requests: spawning worker processes costs far more than the prediction
# itself (the model may have been trained with n_jobs=-1).
if hasattr(_model, "n_jobs"):
    _model.n_jobs = 1


def _classify(probability: float) -> tuple[str, str]:
    """Return (classification, recommendation) based on probability score."""
    if probability >= 0.65:
        return "High",   "Prioritize immediate follow-up"
    if probability >= 0.35:
        return "Medium", "Schedule follow-up in 7 days"
    return "Low", "Do not prioritize in this campaign"


def _encode(value, encoder) -> int:
    """Label-encode a category; unseen values fall back to class 0."""
    return int(encoder.transform([value])[0]) if value in encoder.classes_ else 0


def run_predictions(rows: List[dict]) -> List[dict]:
    """Predict a batch of calls. Each row has the raw (un-encoded) input variables."""
    frame = pd.DataFrame(rows)
    for col in _CATEGORICAL:
        encoder = _encoders[col]
        frame[col + "_enc"] = [_encode(v, encoder) for v in frame[col]]

    probabilities = _model.predict_proba(frame[_features])[:, 1]

    results = []
    for probability in probabilities:
        classification, recommendation = _classify(float(probability))
        results.append({
            "probability":    round(float(probability), 4),
            "classification": classification,
            "recommendation": recommendation,
        })
    return results


def run_prediction(data: dict) -> dict:
    """Predict a single call: returns probability + classification + recommendation."""
    return run_predictions([data])[0]
