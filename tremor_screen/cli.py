"""Extract tap features and print a synthetic-reference screening result."""

from __future__ import annotations

import argparse
import json
import wave
from dataclasses import asdict
from pathlib import Path

import numpy as np

from tremor_screen.features import TapFeatures, as_matrix, detect_taps, extract_features
from tremor_screen.model import ScreeningModel
from tremor_screen.synthetic import SAMPLE_RATE, synth_recording


def _read_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as recording:
        if recording.getnchannels() != 1 or recording.getsampwidth() != 2:
            raise ValueError("expected a mono 16-bit PCM WAV")
        sample_rate = recording.getframerate()
        if sample_rate < 16000:
            raise ValueError("sample rate must be at least 16 kHz")
        frames = recording.getnframes()
        data = recording.readframes(frames)
        if len(data) != frames * 2:
            raise ValueError("WAV sample data is truncated")
    return np.frombuffer(data, dtype="<i2") / 32768.0, sample_rate


def _tap_features(signal: np.ndarray, sample_rate: int) -> list[TapFeatures]:
    segment_samples = int(0.06 * sample_rate)
    if signal.size < segment_samples:
        return []
    return [
        extract_features(signal[start : start + segment_samples], sample_rate)
        for start in detect_taps(signal, sample_rate)
        if start + segment_samples <= signal.size
    ]


def _fit_synthetic_reference() -> ScreeningModel:
    rng = np.random.default_rng(7)
    reference = _tap_features(synth_recording([False] * 24, rng), SAMPLE_RATE)
    suspect = _tap_features(synth_recording([True] * 24, rng), SAMPLE_RATE)
    labels = [0] * len(reference) + [1] * len(suspect)
    return ScreeningModel().fit(as_matrix(reference + suspect), np.asarray(labels))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wav", type=Path, help="mono 16-bit PCM WAV at 16 kHz or higher")
    args = parser.parse_args(argv)
    try:
        signal, sample_rate = _read_wav(args.wav)
        features = _tap_features(signal, sample_rate)
    except (OSError, EOFError, ValueError, wave.Error) as exc:
        parser.error(f"{args.wav}: {exc}")

    model = _fit_synthetic_reference()
    matrix = as_matrix(features) if features else np.empty((0, 4))
    result = model.screen_zone(args.wav.stem, matrix)
    print(json.dumps({
        "score_reference": "synthetic_taps_only",
        "intended_use": (
            "Comparison with synthetic taps only. "
            "Use established inspection methods for field decisions."
        ),
        "features": [asdict(tap) for tap in features],
        "score": result.margin if result.n_taps >= model.min_taps else None,
        "decision": result.decision,
        "n_taps": result.n_taps,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
