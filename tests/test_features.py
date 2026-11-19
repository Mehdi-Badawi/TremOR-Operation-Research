import numpy as np
import pytest

from tremor_screen.features import detect_taps, extract_features
from tremor_screen.synthetic import SAMPLE_RATE, synth_recording, synth_tap


def test_detects_each_tap():
    rng = np.random.default_rng(0)
    audio = synth_recording([False, True, False, True], rng)
    assert len(detect_taps(audio, SAMPLE_RATE)) == 4


def test_hollow_tap_is_lower_and_longer():
    rng = np.random.default_rng(1)
    sound = extract_features(synth_tap(False, rng), SAMPLE_RATE)
    hollow = extract_features(synth_tap(True, rng), SAMPLE_RATE)
    assert hollow.dominant_hz < sound.dominant_hz
    assert hollow.decay_ms > sound.decay_ms
    assert hollow.low_high_energy_ratio > sound.low_high_energy_ratio


@pytest.mark.parametrize(
    "signal,rate",
    [(np.zeros(10), SAMPLE_RATE), (np.ones(1000), 8000), (np.full(1000, np.nan), SAMPLE_RATE)],
)
def test_rejects_bad_input(signal, rate):
    with pytest.raises(ValueError):
        extract_features(signal, rate)


def test_silence_has_no_taps():
    assert detect_taps(np.zeros(5000), SAMPLE_RATE) == []
