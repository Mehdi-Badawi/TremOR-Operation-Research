"""Per-site calibration: compare taps with reference taps from sound areas.

The inspector first taps a few areas they consider sound on the same surface,
with the same phone. Every later spot is scored by how far its taps sit from
that local reference, in units of the reference's own spread. No central
model is needed, so the comparison adapts to each wall, material and phone.

Each result carries a confidence in [0, 1] and can abstain when the evidence
is weak. The output is a "look here next" flag for the engineer, who makes the
assessment.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tremor_screen.model import ABSTAIN, FLAG, NO_FLAG

MATERIALS = ("brick_masonry", "mortar", "concrete", "plaster", "tile", "drywall", "other")


@dataclass(frozen=True)
class SpotResult:
    spot: str
    material: str
    decision: str
    distance: float
    confidence: float
    n_taps: int


class SiteReference:
    """Robust reference built from taps on sound areas of one surface."""

    def __init__(
        self,
        reference: np.ndarray,
        material: str,
        *,
        flag_distance: float = 3.0,
        clear_distance: float = 1.5,
        min_taps: int = 3,
        min_reference: int = 5,
    ) -> None:
        if material not in MATERIALS:
            raise ValueError(f"material must be one of {MATERIALS}")
        reference = np.atleast_2d(np.asarray(reference, float))
        if len(reference) < min_reference:
            raise ValueError(f"need at least {min_reference} reference taps")
        if not clear_distance < flag_distance:
            raise ValueError("clear_distance must be below flag_distance")
        self.material = material
        self.flag_distance = flag_distance
        self.clear_distance = clear_distance
        self.min_taps = min_taps
        self.center = np.median(reference, axis=0)
        mad = np.median(np.abs(reference - self.center), axis=0)
        # Floor the spread: FFT-bin features can repeat exactly, giving zero MAD.
        self.scale = np.maximum(1.4826 * mad, 0.1)

    def distance(self, taps: np.ndarray) -> np.ndarray:
        z = (np.atleast_2d(np.asarray(taps, float)) - self.center) / self.scale
        return np.sqrt(np.mean(z**2, axis=1))

    def screen_spot(self, spot: str, taps: np.ndarray) -> SpotResult:
        taps = np.atleast_2d(np.asarray(taps, float))
        n = len(taps)
        if n < self.min_taps:
            return SpotResult(spot, self.material, ABSTAIN, float("nan"), 0.0, n)
        d = float(np.median(self.distance(taps)))
        mid = 0.5 * (self.flag_distance + self.clear_distance)
        half = 0.5 * (self.flag_distance - self.clear_distance)
        confidence = float(min(1.0, abs(d - mid) / half)) * min(1.0, n / (2 * self.min_taps))
        if d >= self.flag_distance:
            decision = FLAG
        elif d <= self.clear_distance:
            decision = NO_FLAG
        else:
            decision = ABSTAIN
        return SpotResult(spot, self.material, decision, d, round(confidence, 3), n)
