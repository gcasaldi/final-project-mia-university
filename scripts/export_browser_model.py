"""Export the approved V3 sklearn classifier for local, browser-only inference.

This is a model artifact, NOT a retrained alternative or separate ML method.
The TfidfVectorizer and LogisticRegression come directly from src.model_service.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from src.model_service import RANDOM_STATE, KAGGLE_DATASET, load_training_data, train_model
from src.phishing_utils import preprocess_text


TARGET = Path("docs/model.json")
EXAMPLES = [
    "Hello team, the project meeting has been scheduled for Tuesday at 10:00. Best regards.",
    "URGENT: Your Microsoft account has been suspended. Verify your identity immediately to avoid permanent account closure.",
    "Please review your latest invoice and contact our support team if you have any questions.",
    "Security warning: reset your password immediately and confirm your account details.",
    "Thanks for your time today. The updated research notes are attached for your review.",
]


def export_browser_model() -> dict:
    """Train the same baseline as V3 and export compatible weights and self-tests."""
    df = load_training_data()
    bundle = train_model()
    vec = bundle.vectorizer
    clf = bundle.model
    if vec.ngram_range != (1, 2) or not vec.sublinear_tf or vec.norm != "l2":
        raise ValueError("Unsupported TF-IDF configuration for the browser runtime.")
    if len(clf.classes_) != 2 or list(clf.classes_) != [0, 1]:
        raise ValueError("Unexpected label ordering.")

    _, x_temp, _, y_temp = train_test_split(
        df["processed_text"], df["label"], test_size=0.30,
        random_state=RANDOM_STATE, stratify=df["label"],
    )
    _, x_test, _, y_test = train_test_split(
        x_temp, y_temp, test_size=0.50, random_state=RANDOM_STATE, stratify=y_temp,
    )
    proba = clf.predict_proba(vec.transform(x_test))[:, 1]
    y_pred = (proba >= 0.50).astype(int)
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 6),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 6),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 6),
        "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 6),
        "roc_auc": round(float(roc_auc_score(y_test, proba)), 6),
    }
    if metrics["f1"] < 0.90:
        raise RuntimeError("Unexpectedly low F1; refusing to publish an unreliable model.")

    terms = [""] * len(vec.vocabulary_)
    for term, index in vec.vocabulary_.items():
        terms[index] = term
    examples = [{
        "text": sample,
        "probability": float(clf.predict_proba(vec.transform([preprocess_text(sample)]))[0, 1]),
    } for sample in EXAMPLES]

    data = {
        "format": "phishlens-sklearn-v1",
        "author": "Giulia Casaldi",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pipeline": "URL/email tokenization → TF-IDF (1,2) → Logistic Regression",
        "dataset": KAGGLE_DATASET,
        "random_state": RANDOM_STATE,
        "threshold": 0.50,
        "features": terms,
        "idf": np.asarray(vec.idf_, dtype=np.float64).round(11).tolist(),
        "coef": np.asarray(clf.coef_[0], dtype=np.float64).round(11).tolist(),
        "intercept": float(clf.intercept_[0]),
        "metrics_recomputed_internal_test": metrics,
        "n_train": int(len(df) - len(x_temp)),
        "n_test": int(len(x_test)),
        "self_tests": examples,
        "disclaimer": "Text-only research model. Prediction is not a malware scan, verdict of sender identity, or guarantee of safety.",
    }
    assert len(data["features"]) == len(data["idf"]) == len(data["coef"])
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("Exported", TARGET, "features:", len(terms), "bytes:", TARGET.stat().st_size)
    print("Internal test evaluation:", metrics)
    return data


if __name__ == "__main__":
    export_browser_model()
