"""Grouped train/test splits so taps from one specimen never leak across sets."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def grouped_split(
    groups: Sequence[str], test_fraction: float = 0.3, seed: int = 0
) -> tuple[np.ndarray, np.ndarray]:
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be between 0 and 1")
    groups = np.asarray(groups)
    unique = np.unique(groups)
    if unique.size < 2:
        raise ValueError("need at least two groups")
    rng = np.random.default_rng(seed)
    shuffled = rng.permutation(unique)
    n_test = max(1, int(round(test_fraction * unique.size)))
    test_groups = set(shuffled[:n_test])
    test_mask = np.array([g in test_groups for g in groups])
    return np.flatnonzero(~test_mask), np.flatnonzero(test_mask)
