# TremOR: hearing the damage we can't see

Building inspectors have found hidden damage for generations by tapping a
surface and listening for a change in the sound. It takes years of practice,
and once the inspection is over there is usually no recording anyone can go
back to. TremOR is built around the hammer inspectors already carry and the
phone already in their pocket: the phone records each tap, a small offline
model compares each spot with nearby reference taps from sound areas, and
spots that sound different are flagged on a map so the engineer can decide
where to look next.

We start with fired-clay brick and mortar. Concrete garages and decks,
plaster, tile and drywall follow, each with its own validation.

> **Status: working prototype; the phone app is in development.** The
> transparent feature-based classifier with margin-based abstention, per-site
> calibration and grouped evaluation are built and tested here. The bundled
> demos use synthetic taps; the JSON from `tremor-screen` labels its scores
> `"score_reference": "synthetic_taps_only"`.

## How it works

1. **Record.** The phone records each hammer tap and asks what the surface is
   made of (`brick_masonry`, `mortar`, `concrete`, `plaster`, `tile`,
   `drywall`, `other`).
2. **Calibrate per site.** The inspector taps a few sound areas on the same
   wall with the same phone. That local reference absorbs differences between
   walls, materials and phones without a large central model.
3. **Compare.** Each spot's taps are scored by their distance from the local
   reference (`tremor_screen/calibration.py`).
4. **Flag, with confidence.** Every result is `flag_for_followup`, `no_flag`
   or `abstain`, with a confidence score. When the evidence is weak, the model
   abstains instead of guessing.
5. **Map.** Flags are placed on a map of the surface so the engineer has a
   clear place to start. The engineer always makes the assessment.

## What is in this repository

| Path | What it does |
| --- | --- |
| `tremor_screen/features.py` | Tap detection and transparent acoustic features (dominant frequency, spectral centroid, low/high band energy ratio, decay time) |
| `tremor_screen/cli.py` | Feature extraction and synthetic-reference scoring for WAV recordings |
| `tremor_screen/calibration.py` | Per-site calibration: scores each spot against reference taps from sound areas on the same surface and phone, with a confidence score and abstention |
| `tremor_screen/zone_map.py` | Draws a per-zone map (PNG) from a CSV of scores and abstentions |
| `tremor_screen/model.py` | Nearest-centroid screening per zone with abstention: `flag_for_followup`, `no_flag` or `abstain` |
| `tremor_screen/splits.py` | Grouped train/test splits so taps from one specimen never leak between sets |
| `tremor_screen/synthetic.py` | A toy tap generator (sound vs. hollow) for demos and tests. Not measured data |
| `examples/demo.py` | End-to-end pipeline: recording → taps → features → grouped split → zone decisions |
| `tests/` | Unit tests, run in CI on every pull request |

This is a public reference implementation of the general approach. It will
grow as research results mature.

## Quick start

```sh
python -m pip install -r requirements-dev.txt
pytest -q
python examples/demo.py
```

The demo prints a decision per held-out synthetic zone. Because the data is
synthetic, the numbers say nothing about real-world accuracy.

## Screen a WAV recording

```sh
python -m pip install .
tremor-screen recording.wav
```

The command reads one mono 16-bit PCM WAV, sampled at 16 kHz or higher, as a
single zone. It prints features and a signed score against a synthetic tap
reference fitted when the command runs. That score is a workflow
demonstration. Use established inspection methods for field decisions,
including when the decision is `no_flag`.

Space taps at least 150 ms apart and leave at least 60 ms after the last tap
onset so the command can extract a full window.

The JSON includes the four acoustic features per usable tap, the tap count,
the score, and a decision. Positive scores favor the synthetic suspect
reference. Negative scores favor the synthetic comparison reference. The
decisions are `flag_for_followup`, `no_flag`, and `abstain`. With at least
three usable taps and an absolute score below 0.5, the command prints the
score and abstains. With fewer than three usable taps, it prints a `null`
score and abstains. Every result also includes
`"score_reference": "synthetic_taps_only"` and an `intended_use` message, so
a saved result carries the same limits.

## Draw a zone screening map

Save one row per zone in a CSV. Use integer grid coordinates with one zone per
position. Use a finite numeric score for each scored zone. Set `abstain` to
`true` or `1` for an abstained zone and `false` or `0` for a scored zone.
The score can be blank for abstained zones.

```csv
zone,x,y,score,abstain
A1,0,0,0.2,false
A2,1,0,,true
B1,0,1,0.8,false
```

```sh
python -m tremor_screen.zone_map zones.csv --png zones.png
```

The map colors scored zones using the score range in the CSV and hatches
abstained zones. Coordinates increase to the right and up. To generate a map
from Python, import `draw_zone_map` from `tremor_screen.zone_map` and pass
the CSV path and PNG path.

## Design principles

- **Small.** Transparent features and models well under 10 million
  parameters, designed to run offline on a mid-range phone. Training runs on
  CPUs. No frontier-model API at any step.
- **Intentional.** Recordings stay on the phone unless the user chooses to
  share them. No account, no tracking. Users label their own data and decide
  whether it joins the open dataset. See [docs/DATA-GOVERNANCE.md](docs/DATA-GOVERNANCE.md).
- **Honest evaluation.** Taps from the same specimen or building always stay
  together when data is split (`tremor_screen/splits.py`), and we report how
  often the model abstains. We publish where it struggles:
  [docs/LIMITATIONS.md](docs/LIMITATIONS.md).
- **The engineer decides.** TremOR adds a low-cost piece of evidence; it never
  replaces the engineer's assessment.

See [docs/STATUS.md](docs/STATUS.md) for what exists today and
[docs/ROADMAP.md](docs/ROADMAP.md) for what comes next.

## Licence

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
