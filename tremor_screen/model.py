"""Nearest-centroid screening with abstention.

Outputs are per-zone flags for follow-up inspection by established methods:
"flag_for_followup", "no_flag", or "abstain". The model never states that a
structure is safe or unsafe, and never states damage type or severity.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

FLAG = "flag_for_followup"
NO_FLAG = "no_flag"
ABSTAIN = "abstain"


@dataclass(frozen=True)
class ZoneResult:
    zone: str
    decision: str
    margin: float
    n_taps: int


class ScreeningModel:
    def __init__(self, abstain_margin: float = 0.5, min_taps: int = 3) -> None:
        self.abstain_margin = abstain_margin
        self.min_taps = min_taps
        self._mean: np.ndarray | None = None
        self._scale: np.ndarray | None = None
        self._centroids: dict[int, np.ndarray] = {}

    def fit(self, x: np.ndarray, y: np.ndarray) -> ScreeningModel:
        x = np.asarray(x, float)
        y = np.asarray(y, int)
        if set(np.unique(y)) != {0, 1}:
            raise ValueError("training labels must include both 0 (reference) and 1 (suspect)")
        self._mean = x.mean(axis=0)
        self._scale = x.std(axis=0) + 1e-9
        z = (x - self._mean) / self._scale
        self._centroids = {label: z[y == label].mean(axis=0) for label in (0, 1)}
        return self

    def margins(self, x: np.ndarray) -> np.ndarray:
        """Positive means closer to the suspect centroid, in standardized units."""
        if self._mean is None:
            raise RuntimeError("model is not fitted")
        z = (np.asarray(x, float) - self._mean) / self._scale
        d0 = np.linalg.norm(z - self._centroids[0], axis=1)
        d1 = np.linalg.norm(z - self._centroids[1], axis=1)
        return d0 - d1

    def screen_zone(self, zone: str, x: np.ndarray) -> ZoneResult:
        x = np.atleast_2d(x)
        if len(x) < self.min_taps:
            return ZoneResult(zone, ABSTAIN, 0.0, len(x))
        margin = float(np.median(self.margins(x)))
        if abs(margin) < self.abstain_margin:
            decision = ABSTAIN
        else:
            decision = FLAG if margin > 0 else NO_FLAG
        return ZoneResult(zone, decision, margin, len(x))
