# TremOR: low-cost AI screening of hammer-tap sounds

TremOR is a research project building a low-cost screening aid for routine
building-maintenance inspection in the United States. An inspector taps a
surface (concrete first) with a hammer, a phone records the sound, and software
aims to flag zones that sound "hollow" for a closer look with established methods.

Hammer sounding is a century-old technique. It works, but it relies on one
person's ear, is hard to teach and leaves no record. TremOR aims to make it
measurable, repeatable and documented, using hardware inspectors already carry.

> **Status: early research prototype.** The demo and the scoring reference use
> synthetic taps only. A score from any WAV, including one you record, is a
> comparison with that synthetic reference. The printed JSON repeats the limit
> as `"score_reference": "synthetic_taps_only"`. Use established inspection
> methods for field decisions.

## What is in this repository

| Path | What it does |
| --- | --- |
| `tremor_screen/features.py` | Tap detection and transparent acoustic features (dominant frequency, spectral centroid, low/high band energy ratio, decay time) |
| `tremor_screen/cli.py` | Feature extraction and synthetic-reference scoring for WAV recordings |
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

The demo prints a decision per held-out synthetic zone.

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

## Design principles

- **Screening workflow.** The score compares taps with a synthetic reference
  and can flag a zone for follow-up or abstain. Use established inspection
  methods for field decisions.
- **Honest evaluation.** Splits are grouped by specimen; results are labelled
  by data source (synthetic today).
- **Small and local.** Transparent features and small models that can run on a
  phone. No frontier-model API in the pipeline.
- **Open where it helps the field.** We plan to publish evaluation protocols
  and a consented tap-sound dataset as they mature.

See [docs/STATUS.md](docs/STATUS.md) for what exists today and
[docs/ROADMAP.md](docs/ROADMAP.md) for what comes next.

## Licence

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
