# Run outputs

This repository currently commits JSON transcript envelopes only:

- `round1/` — 36 JSON runs from the first round.
- `round2/` — 36 JSON runs from the second round.

Each JSON envelope contains the scripted user turns, model answers, self-report
block, logit-lens readout, and run metadata. Field reference and parsing notes
are in `docs/DATA.md`.

Provenance rule: **a new repetition is a new file.** Never overwrite an existing
results file — early runs did, and three T0 runs partially clobbered each other
before it was caught.

NPZ hidden-state archives are intentionally not committed here. They are large;
`.gitattributes` tracks future `*.npz` files with Git LFS if they are later added.
