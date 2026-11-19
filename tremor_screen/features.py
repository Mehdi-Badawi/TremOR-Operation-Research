"""Generic acoustic features for hammer-tap recordings.

These are textbook signal descriptors (spectral centroid, band energy ratio,
decay time, dominant frequency). They are a transparent public baseline, not
the project's final feature set.
"""

from __future__ import annotations

from dataclasses import astuple, dataclass

import numpy as np

LOW_BAND_HZ = (100.0, 1500.0)
HIGH_BAND_HZ = (1500.0, 8000.0)


@dataclass(frozen=True)
class TapFeatures:
    dominant_hz: float
    spectral_centroid_hz: float
    low_high_energy_ratio: float
    decay_ms: float

    def vector(self) -> np.ndarray:
        return np.array(
            [
                np.log(self.dominant_hz),
                np.log(self.spectral_centroid_hz),
                np.log(self.low_high_energy_ratio),
                np.log(self.decay_ms),
            ]
        )


def _validate(signal: np.ndarray, sample_rate: int) -> np.ndarray:
    signal = np.asarray(signal, dtype=float)
    if signal.ndim != 1 or signal.size < 64:
        raise ValueError("signal must be 1-D with at least 64 samples")
    if sample_rate < 16000:
        raise ValueError("sample rate must be at least 16 kHz")
    if not np.all(np.isfinite(signal)):
        raise ValueError("signal contains non-finite values")
    return signal


def detect_taps(
    signal: np.ndarray,
    sample_rate: int,
    *,
    threshold_ratio: float = 0.3,
    min_gap_s: float = 0.15,
) -> list[int]:
    """Return sample indices where taps start, by simple envelope thresholding."""
    signal = _validate(signal, sample_rate)
    peak = np.max(np.abs(signal))
    if peak == 0:
        return []
    above = np.flatnonzero(np.abs(signal) >= threshold_ratio * peak)
    gap = int(min_gap_s * sample_rate)
    onsets: list[int] = []
    for index in above:
        if not onsets or index - onsets[-1] >= gap:
            onsets.append(int(index))
    return onsets


def extract_features(segment: np.ndarray, sample_rate: int) -> TapFeatures:
    """Compute features for one tap segment that starts at the impact."""
    segment = _validate(segment, sample_rate)
    windowed = segment * np.hanning(segment.size)
    spectrum = np.abs(np.fft.rfft(windowed)) ** 2
    freqs = np.fft.rfftfreq(segment.size, 1.0 / sample_rate)
    usable = freqs >= LOW_BAND_HZ[0]
    if spectrum[usable].sum() <= 0:
        raise ValueError("segment has no energy above the low-band floor")

    dominant = float(freqs[usable][np.argmax(spectrum[usable])])
    centroid = float(np.sum(freqs[usable] * spectrum[usable]) / spectrum[usable].sum())

    def band(lo: float, hi: float) -> float:
        mask = (freqs >= lo) & (freqs < hi)
        return float(spectrum[mask].sum())

    ratio = (band(*LOW_BAND_HZ) + 1e-12) / (band(*HIGH_BAND_HZ) + 1e-12)

    envelope = np.abs(segment)
    peak_index = int(np.argmax(envelope))
    target = envelope[peak_index] * 10 ** (-20 / 20)  # -20 dB point
    after = np.flatnonzero(envelope[peak_index:] < target)
    decay_samples = after[0] if after.size else segment.size - peak_index
    decay_ms = max(1000.0 * decay_samples / sample_rate, 0.1)

    return TapFeatures(max(dominant, 1.0), max(centroid, 1.0), ratio, decay_ms)


def as_matrix(features: list[TapFeatures]) -> np.ndarray:
    return np.vstack([f.vector() for f in features])


__all__ = ["TapFeatures", "detect_taps", "extract_features", "as_matrix", "astuple"]
