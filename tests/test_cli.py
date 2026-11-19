import json
import math
import wave

import numpy as np
import pytest

from tremor_screen.cli import main
from tremor_screen.synthetic import SAMPLE_RATE, synth_recording


@pytest.mark.parametrize(
    ("labels", "seed", "decision", "score_bounds"),
    [
        pytest.param([], 42, "abstain", None, id="no-taps"),
        pytest.param([True], 42, "abstain", None, id="too-few-taps"),
        pytest.param([True] * 4, 42, "flag_for_followup", (0.5, math.inf), id="hollow"),
        pytest.param([False] * 6, 42, "no_flag", (-math.inf, -0.5), id="sound"),
        pytest.param([True, False] * 2, 2, "abstain", (-0.5, 0.5), id="low-margin"),
    ],
)
def test_screen_wav(tmp_path, capsys, labels, seed, decision, score_bounds):
    path = tmp_path / "taps.wav"
    signal = synth_recording(labels, np.random.default_rng(seed))
    pcm = np.rint(16000 * signal).astype("<i2")
    with wave.open(str(path), "wb") as recording:
        recording.setparams((1, 2, SAMPLE_RATE, 0, "NONE", "not compressed"))
        recording.writeframes(pcm.tobytes())

    assert main([str(path)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["score_reference"] == "synthetic_taps_only"
    assert "Comparison with synthetic taps only." in result["intended_use"]
    assert "Use established inspection methods for field decisions." in result["intended_use"]
    assert result["n_taps"] == len(result["features"]) == len(labels)
    for tap, hollow in zip(result["features"], labels, strict=True):
        assert set(tap) == {
            "dominant_hz",
            "spectral_centroid_hz",
            "low_high_energy_ratio",
            "decay_ms",
        }
        low_hz, high_hz = (600, 1400) if hollow else (2500, 4500)
        assert low_hz <= tap["dominant_hz"] <= high_hz
        assert all(math.isfinite(value) and value > 0 for value in tap.values())

    assert result["decision"] == decision
    if score_bounds is None:
        assert result["n_taps"] < 3
        assert result["score"] is None
    else:
        assert result["n_taps"] >= 3
        score = result["score"]
        assert isinstance(score, float) and math.isfinite(score)
        assert score_bounds[0] < score < score_bounds[1]
        if decision == "abstain":
            assert abs(score) < 0.5
        if decision == "no_flag":
            assert score < 0


def test_reject_invalid_wav(tmp_path, capsys):
    path = tmp_path / "invalid.wav"
    path.write_bytes(b"")

    with pytest.raises(SystemExit) as exc:
        main([str(path)])

    assert exc.value.code == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert str(path) in output.err
