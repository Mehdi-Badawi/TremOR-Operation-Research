# Public datasets

## Annotated Impact Echo Dataset (bare decks)

*Annotated Impact Echo Dataset (bare decks)* (2020), version 1, Mendeley Data.
[DOI 10.17632/44rb96872r.1 and full author citation](https://doi.org/10.17632/44rb96872r.1).
[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

The dataset contains 2,016 impact-echo signals from eight laboratory-made
concrete specimens.

```python
from tremor_screen.datasets import load_bare_decks

paths = load_bare_decks()
```

The loader returns a one-element tuple containing the path to `BareAnnotated.zip`.
It verifies the archive against the published version 1 SHA-256. It can reuse
a verified cached archive offline. If the archive is missing or fails the
checksum, the loader fetches the version 1 file listing and downloads the archive.
The cache is under `$XDG_CACHE_HOME/tremor-screen`, or
`~/.cache/tremor-screen` if no absolute cache directory is configured.

No field validation or pilot has been completed.

- **Screening, not judgment.** Outputs are "look closer here" flags with an
  explicit abstain option. No safe/unsafe, damage-type or severity claims.
  Today the score compares taps with a synthetic reference only.
