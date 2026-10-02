from __future__ import annotations
from pathlib import Path
import math
from datetime import datetime, timezone
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

FEATURES = [
    "typing_duration",
    "avg_key_interval",
    "backspace_count",
    "mouse_distance",
    "avg_mouse_speed",
    "login_hour",
]

from .db import DATA_DIR
MODEL_DIR = DATA_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def feature_vector(sample: dict) -> np.ndarray:
    vals=[]
    for key in FEATURES:
        v=float(sample.get(key, 0.0))
        if not math.isfinite(v):
            v=0.0
        vals.append(v)
    return np.array(vals, dtype=float)


def model_path(user_id: int) -> Path:
    return MODEL_DIR / f"user_{user_id}.joblib"


def has_model(user_id: int) -> bool:
    return model_path(user_id).exists()


def _deviation(X: np.ndarray, mean: np.ndarray, scale: np.ndarray) -> np.ndarray:
    # Absolute deviation from the user's baseline, in baseline-sized units.
    # A linear model can't separate a cluster that sits *between* impostor
    # samples, but it can separate "small deviation" from "large deviation".
    return np.abs(X - mean) / scale


def train_user_model(user_id: int, legitimate_samples: list[dict]) -> dict:
    if len(legitimate_samples) < 5:
        raise ValueError("At least 5 legitimate samples are required before training.")

    rng = np.random.default_rng(42 + user_id)
    X_pos = np.vstack([feature_vector(s) for s in legitimate_samples])
    mean = X_pos.mean(axis=0)
    # Floor the spread so near-constant features don't explode the deviation.
    floor = np.maximum(np.abs(mean) * 0.15, np.array([50.0, 10.0, 1.0, 50.0, 50.0, 1.0]))
    scale = np.maximum(X_pos.std(axis=0), floor)

    # Synthetic impostor class for academic/demo purposes only: each feature is
    # shifted 30-90% up or down with probability 0.6 (at least one changes).
    X_neg = []
    for x in X_pos:
        for _ in range(3):
            change = rng.random(x.shape) < 0.6
            change[rng.integers(len(x))] = True
            factor = 1 + rng.choice([-1.0, 1.0], size=x.shape) * rng.uniform(0.3, 0.9, size=x.shape)
            y = np.where(change, x * factor, x)
            y[2] = max(y[2], 0.0)  # backspace count can't be negative
            y[5] = y[5] % 24
            X_neg.append(y)
    X_neg = np.vstack(X_neg)

    X = _deviation(np.vstack([X_pos, X_neg]), mean, scale)
    y = np.concatenate([np.ones(len(X_pos)), np.zeros(len(X_neg))])

    clf = LogisticRegression(max_iter=1000, random_state=42)
    clf.fit(X, y)
    train_acc = float(clf.score(X, y))
    joblib.dump({"clf": clf, "mean": mean, "scale": scale, "training_accuracy": train_acc,
                 "samples": len(legitimate_samples),
                 "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}, model_path(user_id))
    return {"samples": len(legitimate_samples), "synthetic_negatives": len(X_neg), "training_accuracy": train_acc}


def trust_score(user_id: int, sample: dict) -> float:
    model = joblib.load(model_path(user_id))
    if not isinstance(model, dict):
        raise ValueError("Model file is from an older version; retrain the model.")
    x = _deviation(feature_vector(sample).reshape(1, -1), model["mean"], model["scale"])
    p = float(model["clf"].predict_proba(x)[0, 1])
    if not math.isfinite(p):
        return 0.0
    return round(min(max(p * 100, 0.0), 100.0), 2)


def model_info(user_id: int) -> dict | None:
    """Training metadata for the dashboard, or None if no usable model exists."""
    if not has_model(user_id):
        return None
    try:
        m = joblib.load(model_path(user_id))
    except Exception:
        return None
    if not isinstance(m, dict):
        return {"outdated": True}
    return {"training_accuracy": m.get("training_accuracy"), "samples": m.get("samples"),
            "trained_at": m.get("trained_at")}
