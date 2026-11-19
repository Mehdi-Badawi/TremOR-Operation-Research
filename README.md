# TremOR: low-cost AI screening of hammer-tap sounds

TremOR is a research project building a low-cost screening aid for routine
building-maintenance inspection in the United States. An inspector taps a
surface (concrete first) with a hammer, a phone records the sound, and software
aims to flag zones that sound "hollow" for a closer look with established methods.

Hammer sounding is a century-old technique. It works, but it relies on one
person's ear, is hard to teach and leaves no record. TremOR aims to make it
measurable, repeatable and documented, using hardware inspectors already carry.

> **Status: early research prototype.** No field validation or pilot has been
> completed. Everything in this repository runs on synthetic data. TremOR is a
> screening aid that suggests where to look; it never decides whether a
> structure is safe, and it never replaces a qualified inspector.

## What is in this repository

| Path | What it does |
| --- | --- |
| `tremor_screen/features.py` | Tap detection and transparent acoustic features (dominant frequency, spectral centroid, low/high band energy ratio, decay time) |
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

The demo prints a decision per held-out zone. Because the data is synthetic,
the numbers say nothing about real-world accuracy.

## Design principles

- **Screening, not judgment.** Outputs are "look closer here" flags with an
  explicit abstain option. No safe/unsafe, damage-type or severity claims.
- **Honest evaluation.** Splits are grouped by specimen; results are labelled
  by data source (synthetic today).
- **Small and local.** Transparent features and small models that can run on a
  phone. No frontier-model API in the pipeline.
- **Open where it helps the field.** We plan to publish evaluation protocols
  and a consented tap-sound dataset as they mature.

See [docs/STATUS.md](docs/STATUS.md) for what exists today and
[docs/ROADMAP.md](docs/ROADMAP.md) for what comes next.

## Licence

Copyright © 2026 Mehdi Badawi. All rights reserved for now; an open licence
will be chosen and added. Until then, you may view and run the code to
evaluate the project; any other use needs written permission (see LICENSE).
