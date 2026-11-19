"""Synthetic tap generator for demos and tests.

This is a toy physical caricature: a sound slab rings at higher frequency and
decays fast; a delaminated patch behaves like a thin plate, ringing lower and
longer ("hollow" sound). It is NOT measured data and results on it say nothing
about field performance.
"""

from __future__ import annotations

import numpy as np

SAMPLE_RATE = 44100


def synth_tap(delaminated: bool, rng: np.random.Generator, duration_s: float = 0.08) -> np.ndarray:
    t = np.arange(int(duration_s * SAMPLE_RATE)) / SAMPLE_RATE
    if delaminated:
        f0 = rng.uniform(600, 1400)
        tau = rng.uniform(0.012, 0.025)
    else:
        f0 = rng.uniform(2500, 4500)
        tau = rng.uniform(0.003, 0.007)
    tone = np.exp(-t / tau) * np.sin(2 * np.pi * f0 * t)
    tone += 0.5 * np.exp(-t / (tau * 0.6)) * np.sin(2 * np.pi * 2.3 * f0 * t)
    click = np.exp(-t / 0.0005) * rng.normal(0, 0.6, t.size)
    noise = rng.normal(0, 0.01, t.size)
    return rng.uniform(0.5, 1.0) * (tone + click) + noise


def synth_recording(labels: list[bool], rng: np.random.Generator, gap_s: float = 0.3) -> np.ndarray:
    gap = np.zeros(int(gap_s * SAMPLE_RATE))
    parts = []
    for label in labels:
        parts.extend([gap, synth_tap(label, rng)])
    parts.append(gap)
    return np.concatenate(parts)
