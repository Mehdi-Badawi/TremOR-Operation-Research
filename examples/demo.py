"""End-to-end demo on SYNTHETIC taps: detect -> features -> grouped split -> screen.

Run: python examples/demo.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


from tremor_screen import ScreeningModel, detect_taps, extract_features, grouped_split
from tremor_screen.features import as_matrix
from tremor_screen.synthetic import SAMPLE_RATE, synth_recording

SEGMENT = int(0.06 * SAMPLE_RATE)


def main() -> None:
    rng = np.random.default_rng(7)
    feats, labels, zones = [], [], []
    for zone_id in range(24):
        delam = zone_id % 3 == 0
        audio = synth_recording([delam] * 6, rng)
        for onset in detect_taps(audio, SAMPLE_RATE):
            seg = audio[onset : onset + SEGMENT]
            if seg.size == SEGMENT:
                feats.append(extract_features(seg, SAMPLE_RATE))
                labels.append(int(delam))
                zones.append(f"zone-{zone_id:02d}")

    x, y, zones = as_matrix(feats), np.array(labels), np.array(zones)
    train, test = grouped_split(zones, test_fraction=0.33, seed=1)
    model = ScreeningModel().fit(x[train], y[train])

    print("zone      truth  decision           margin  taps")
    for zone in sorted(set(zones[test])):
        idx = test[zones[test] == zone]
        r = model.screen_zone(zone, x[idx])
        print(f"{zone}  {y[idx][0]:>5}  {r.decision:<18} {r.margin:+6.2f}  {r.n_taps}")
    print("\nSynthetic data only. This says nothing about real-world accuracy.")


if __name__ == "__main__":
    main()
