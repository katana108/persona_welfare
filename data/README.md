# Run outputs

One JSON envelope + one NPZ archive per (task file × persona). Field reference
and parsing notes are in `docs/DATA.md`.

Provenance rule: **a new repetition is a new file.** Never overwrite an existing
results file — early runs did, and three T0 runs partially clobbered each other
before it was caught.

NPZ files are large. `.gitattributes` tracks them with Git LFS; run
`git lfs install` once before the first commit, or host them separately and keep
only the JSON here.
