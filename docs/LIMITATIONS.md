# Known limitations

We publish where the model struggles so others can see what still needs work.

- The bundled demos and the CLI's default reference use synthetic taps.
  Performance on real structures has not yet been measured.
- Per-site calibration assumes the reference areas are sound. A bad reference
  shifts every score.
- FFT-bin features can repeat exactly between taps, so the reference spread
  has a floor; very consistent surfaces may be scored conservatively.
- On synthetic data, some sound spots land in the abstain band or are flagged.
  That is why the abstain option exists.
- Each new material, phone and hammer needs its own validation.
