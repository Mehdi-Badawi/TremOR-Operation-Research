# Status (November 2026)

**Stage: working prototype. The phone app is in development.**

## Built and tested in this repository
- Tap detection and transparent acoustic features.
- Feature-based classifier with margin-based abstention.
- Per-site calibration against reference taps from sound areas, with a
  confidence score and abstention, tagged by material.
- Grouped train/test splits by specimen or building.
- `tremor-screen` command for WAV recordings.
- Loader for one [openly licensed concrete impact-echo dataset](DATASETS.md).
- CI running lint, tests and the demo on every pull request.

## In development
- Phone app for recording, material labelling and the per-spot map.
- Small audio model (well under 10M parameters) fine-tuned from open audio
  models.
- Low-cost contact-sensor kit (four MEMS or piezoelectric sensors and a
  microcontroller, under about $100 in parts).

## Collaborators and partners
- Purdue Bowen Laboratory (Lyles School of Civil and Construction
  Engineering) shares internal data and instrumentation.
- AIS Construction Services (Indianapolis): site survey of a damaged pre-1900
  masonry building; plans to try TremOR on its sites.
- Miyamoto International, Kathmandu: planned first field user.
- Kathmandu University: planned data sharing and kit.
- Phase 1 winner, Purdue ShahLab.AI "AI for Good" competition.

## Open challenges
- No open tap-sound dataset exists for brick, plaster or drywall, and open
  concrete data is scattered.
- Field sites where an engineer's findings can be compared with TremOR's flags.
- Human-subjects review for data collection with volunteers.
