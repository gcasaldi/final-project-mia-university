from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import joblib
import kagglehub
import numpy as np
import pandas as pd
from kagglehub import KaggleDatasetAdapter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from src.phishing_utils import preprocess_text


RANDOM_STATE = 42
KAGGLE_DATASET = "naserabdullahalam/phishing-email-dataset"
KAGGLE_FILE = "phishing_email.csv"


@dataclass
class ModelBundle:
    vectorizer: TfidfVectorizer
    model: LogisticRegression
    source: str


def _dataset_key(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def load_training_data() -> pd.DataFrame:
    """Load and clean the same Kaggle aggregate used by the V3 notebook."""
    df = kagglehub.dataset_load(
        KaggleDatasetAdapter.PANDAS,
        KAGGLE_DATASET,
        KAGGLE_FILE,
    )

    required = {"text_combined", "label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {sorted(missing)}")

    df = df[["text_combined", "label"]].copy()
    df = df.dropna(subset=["text_combined", "label"])
    df["text_combined"] = df["text_combined"].astype(str)
    df["label"] = pd.to_numeric(df["label"], errors="coerce")
    df = df.dropna(subset=["label"])
    df["label"] = df["label"].astype(int)
    df = df[df["label"].isin([0, 1])].copy()

    df["_key"] = df["text_combined"].map(_dataset_key)

    conflicting_keys = (
        df.groupby("_key")["label"]
        .nunique()
        .loc[lambda s: s > 1]
        .index
    )
    if len(conflicting_keys):
        df = df[~df["_key"].isin(conflicting_keys)].copy()

    df = df.drop_duplicates(subset=["_key"]).reset_index(drop=True)
    df["processed_text"] = df["text_combined"].map(preprocess_text)
    df = df[df["processed_text"].str.len() > 0].reset_index(drop=True)
    return df


def train_model() -> ModelBundle:
    """Train the same TF-IDF + Logistic Regression baseline used by V3."""
    df = load_training_data()

    x_train_text, _, y_train, _ = train_test_split(
        df["processed_text"],
        df["label"],
        test_size=0.30,
        random_state=RANDOM_STATE,
        stratify=df["label"],
    )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        max_features=30000,
        min_df=2,
        sublinear_tf=True,
        dtype=np.float32,
    )
    x_train = vectorizer.fit_transform(x_train_text)

    model = LogisticRegression(
        solver="liblinear",
        max_iter=1000,
        random_state=RANDOM_STATE,
    )
    model.fit(x_train, y_train)

    return ModelBundle(
        vectorizer=vectorizer,
        model=model,
        source="runtime training on the V3 Kaggle dataset",
    )


def load_or_train_model(artifact_dir: Optional[Path] = None) -> ModelBundle:
    """
    Prefer reproducible local artifacts when present; otherwise train at runtime.

    This makes the dashboard usable after cloning the repository while also
    allowing a faster demo when V3 artifacts have been copied into artifacts/.
    """
    artifact_dir = artifact_dir or Path("artifacts")
    vectorizer_path = artifact_dir / "tfidf_vectorizer.joblib"
    model_path = artifact_dir / "logistic_regression.joblib"

    if vectorizer_path.exists() and model_path.exists():
        return ModelBundle(
            vectorizer=joblib.load(vectorizer_path),
            model=joblib.load(model_path),
            source="saved V3 model artifacts",
        )

    return train_model()


def predict_text(bundle: ModelBundle, text: str, threshold: float = 0.50) -> dict:
    raw = str(text).strip()
    word_count = len(raw.split())

    if word_count < 5:
        return {
            "status": "insufficient_input",
            "message": "Please paste a longer subject/body fragment (at least five words).",
        }

    processed = preprocess_text(raw)
    features = bundle.vectorizer.transform([processed])
    probability = float(bundle.model.predict_proba(features)[0, 1])
    label = "Phishing" if probability >= threshold else "Legitimate"

    return {
        "status": "ok",
        "prediction": label,
        "phishing_probability": probability,
        "threshold": float(threshold),
    }
