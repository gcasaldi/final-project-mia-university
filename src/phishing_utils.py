import re
from typing import Dict, Tuple

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

URL_RE = re.compile(r"(?:https?://|www\.)\S+", flags=re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", flags=re.IGNORECASE)
SPACE_RE = re.compile(r"\s+")


def preprocess_text(text: str) -> str:
    """Normalize message text while retaining URL/email presence as tokens."""
    text = str(text)
    text = URL_RE.sub(" URLTOKEN ", text)
    text = EMAIL_RE.sub(" EMAILTOKEN ", text)
    return SPACE_RE.sub(" ", text).strip()


def compute_metrics(y_true, proba, threshold: float = 0.5) -> Tuple[Dict[str, float], np.ndarray]:
    """Compute the metrics used by the Final Project at a chosen threshold."""
    pred = (np.asarray(proba) >= threshold).astype(int)
    metrics = {
        "threshold": float(threshold),
        "accuracy": accuracy_score(y_true, pred),
        "precision": precision_score(y_true, pred, zero_division=0),
        "recall": recall_score(y_true, pred, zero_division=0),
        "f1": f1_score(y_true, pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true, proba),
    }
    return metrics, pred
