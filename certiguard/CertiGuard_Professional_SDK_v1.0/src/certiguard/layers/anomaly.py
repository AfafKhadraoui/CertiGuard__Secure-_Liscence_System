from __future__ import annotations

"""
L6 — local behavioral anomaly scoring (Isolation Forest + drift).

The model is trained on **synthetic normal traffic** shaped to match the **dimensionality**
of the feature vector you pass in (typically **4** application metrics, or **6** when
using ``layers.behavior_probe`` machine snapshots). The first ``score()`` call fits the
forest for that dimension count; changing dimensions resets the persisted baseline
(``sum_vec`` / ``sessions``) in ``update_customer_baseline``.
"""

from pathlib import Path

import numpy as np
from sklearn.ensemble import IsolationForest

from certiguard.layers.storage import read_json, secure_write_json


class BehaviorDetector:
    def __init__(self, model_seed: int = 42, baseline_state_path: Path | None = None) -> None:
        self.model = IsolationForest(contamination=0.05, random_state=model_seed)
        self.fitted = False
        self.baseline_state_path = baseline_state_path
        self._state = read_json(baseline_state_path) if baseline_state_path else {}
        self._last_dim: int | None = None

    def fit_synthetic_baseline(self, dim: int | None = None) -> None:
        """Fit IsolationForest on synthetic data matching ``dim`` columns."""
        rng = np.random.default_rng(42)
        d = dim or self._last_dim or 4
        self._last_dim = d

        if d == 4:
            active_users = rng.normal(loc=35, scale=8, size=2000).clip(1, 50)
            hour = rng.integers(8, 19, size=2000).astype(float)
            machines = rng.normal(loc=3, scale=1, size=2000).clip(1, 6)
            api_rate = rng.normal(loc=40, scale=12, size=2000).clip(1, 140)
            X = np.column_stack([active_users, hour, machines, api_rate])
        elif d == 6:
            # Aligned with ``behavior_probe.probe_to_feature_vector`` scales.
            cpu = rng.normal(35, 22, size=2000).clip(0, 100)
            cores = rng.integers(2, 33, size=2000).astype(float)
            mem = rng.normal(60, 15, size=2000).clip(5, 100)
            procs = rng.normal(80, 35, size=2000).clip(10, 200)
            gpu = rng.normal(20, 18, size=2000).clip(0, 120)
            hod = rng.integers(0, 24, size=2000).astype(float)
            X = np.column_stack([cpu, cores, mem, procs, gpu, hod])
        else:
            cols = [rng.normal(40, 25, size=2000).clip(0, 200) for _ in range(d)]
            X = np.column_stack(cols)

        self.model.fit(X)
        self.fitted = True

    def score(self, features: list[float]) -> tuple[bool, float]:
        d = len(features)
        if not self.fitted or self._last_dim != d:
            self.fit_synthetic_baseline(dim=d)
        X = np.array([features], dtype=float)
        prediction = self.model.predict(X)[0]
        score = float(self.model.score_samples(X)[0])
        return bool(prediction == -1), float(score)

    def update_customer_baseline(self, features: list[float], learning_days: int = 30) -> dict:
        d = len(features)
        prev_sessions = int(self._state.get("sessions", 0))
        prev_sum = self._state.get("sum_vec")
        if not isinstance(prev_sum, list) or len(prev_sum) != d:
            sessions = 1
            sum_vec = np.array(features, dtype=float)
        else:
            sessions = prev_sessions + 1
            sum_vec = np.array(prev_sum, dtype=float) + np.array(features, dtype=float)
        mean_vec = (sum_vec / sessions).tolist()
        self._state.update(
            {
                "sessions": sessions,
                "sum_vec": sum_vec.tolist(),
                "mean_vec": mean_vec,
                "feature_dim": d,
                "learning_complete": sessions >= learning_days,
            }
        )
        if self.baseline_state_path:
            secure_write_json(self.baseline_state_path, self._state)
        return self._state

    def detect_drift(self, features: list[float], threshold: float = 2.5) -> tuple[bool, float]:
        mean_vec = self._state.get("mean_vec")
        if not mean_vec or len(mean_vec) != len(features):
            return False, 0.0
        diff = np.linalg.norm(np.array(features, dtype=float) - np.array(mean_vec, dtype=float))
        return bool(diff > threshold), float(diff)
