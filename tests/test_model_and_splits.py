import numpy as np
import pytest

from tremor_screen.model import ABSTAIN, FLAG, NO_FLAG, ScreeningModel
from tremor_screen.splits import grouped_split


def _toy():
    rng = np.random.default_rng(0)
    x0 = rng.normal(0, 0.3, (30, 4))
    x1 = rng.normal(3, 0.3, (30, 4))
    return np.vstack([x0, x1]), np.array([0] * 30 + [1] * 30)


def test_flags_and_clears():
    x, y = _toy()
    m = ScreeningModel().fit(x, y)
    assert m.screen_zone("a", np.full((4, 4), 3.0)).decision == FLAG
    assert m.screen_zone("b", np.zeros((4, 4))).decision == NO_FLAG


def test_abstains_when_ambiguous_or_too_few_taps():
    x, y = _toy()
    m = ScreeningModel().fit(x, y)
    assert m.screen_zone("mid", np.full((4, 4), 1.5)).decision == ABSTAIN
    assert m.screen_zone("few", np.full((2, 4), 3.0)).decision == ABSTAIN


def test_never_outputs_safety_language():
    x, y = _toy()
    m = ScreeningModel().fit(x, y)
    for point in (0.0, 1.5, 3.0):
        d = m.screen_zone("z", np.full((5, 4), point)).decision
        assert "safe" not in d


def test_requires_both_labels():
    with pytest.raises(ValueError):
        ScreeningModel().fit(np.zeros((3, 4)), np.zeros(3))


def test_grouped_split_has_no_leakage():
    groups = [f"g{i // 5}" for i in range(50)]
    train, test = grouped_split(groups, 0.3, seed=2)
    g = np.array(groups)
    assert not set(g[train]) & set(g[test])
    assert len(train) + len(test) == 50


def test_demo_runs(capsys):
    import pathlib
    import runpy

    demo = pathlib.Path(__file__).parents[1] / "examples" / "demo.py"
    runpy.run_path(str(demo), run_name="__main__")
    assert "Synthetic data only" in capsys.readouterr().out
