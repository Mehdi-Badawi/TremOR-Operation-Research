import numpy as np
import pytest

from tremor_screen.calibration import SiteReference
from tremor_screen.features import as_matrix, extract_features
from tremor_screen.model import ABSTAIN, FLAG, NO_FLAG
from tremor_screen.synthetic import SAMPLE_RATE, synth_tap


def _taps(hollow, n, rng):
    return as_matrix([extract_features(synth_tap(hollow, rng), SAMPLE_RATE) for _ in range(n)])


def test_flags_hollow_spot_against_local_reference():
    rng = np.random.default_rng(0)
    site = SiteReference(_taps(False, 20, rng), "brick_masonry")
    hollow = site.screen_spot("A1", _taps(True, 5, rng))
    sound = site.screen_spot("A2", _taps(False, 5, rng))
    assert hollow.decision == FLAG and hollow.confidence > 0.5
    assert sound.decision == NO_FLAG
    assert hollow.material == "brick_masonry"


def test_abstains_with_too_few_taps():
    rng = np.random.default_rng(1)
    site = SiteReference(_taps(False, 10, rng), "concrete")
    r = site.screen_spot("B1", _taps(True, 2, rng))
    assert r.decision == ABSTAIN and r.confidence == 0.0


def test_abstains_in_the_grey_zone():
    site = SiteReference(np.random.default_rng(2).normal(0, 1, (50, 4)), "mortar")
    r = site.screen_spot("C1", np.full((4, 4), 2.2))
    assert r.decision == ABSTAIN


def test_rejects_unknown_material_and_tiny_reference():
    with pytest.raises(ValueError):
        SiteReference(np.zeros((10, 4)), "wood")
    with pytest.raises(ValueError):
        SiteReference(np.zeros((2, 4)), "concrete")
