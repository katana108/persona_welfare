# Working Notes

## 2026-08-17 publication pass

Project: Persona Welfare Battery, a pilot battery for testing whether welfare-relevant functional signals are invariant across personas or gated by persona scaffolds.

Goal for this pass: publish the clean project scaffold to `https://github.com/katana108/persona_welfare`.

What is in the repository:

- `README.md`: headline claims, repository map, reproduction notes, limitations, citation, and license.
- `docs/DESIGN.md`: welfare question, conditions, tests, channels, analysis frame, hypotheses, and limitations.
- `docs/DATA.md`: JSON and NPZ schema, parsing gotchas, provenance rule, and Git LFS note.
- `notebooks/01_run_battery.ipynb`: NDIF/nnsight battery runner.
- `notebooks/02_analysis_affect_direction.ipynb`: affect-direction analysis notebook.
- `analysis/`: per-layer decomposition and summary scripts.
- `tasks/` and `data/`: currently contain README placeholders; real run files can be assembled later with `assemble.sh`.
- `paper/persona_welfare_battery.pdf`: submitted report.

Publication cleanup:

- The folder was not a Git repository before this pass.
- The target GitHub repository was reachable and appeared empty when checked with `git ls-remote`.
- Secret scan found only variable names such as `HF_TOKEN` and `NDIF_API_KEY`, not literal credentials.
- Notebook outputs, execution counts, and Colab execution metadata were stripped before the first commit.
- `.gitattributes` already routes `*.npz` through Git LFS for future hidden-state archives.

Conceptual map for later analysis:

- Core question: do welfare-relevant signals belong to the underlying model weights or to the prompted persona?
- Channels: behavior, structured self-report, layerwise logit-lens readout, and hidden-state affect direction.
- Important distinction: the same internal reaction can be reported differently by different personas.
- Provenance rule: new repetitions must be archived as new files; never overwrite old run outputs in place.

Next likely work:

- Add real `tasks/*.txt` and `data/*.{json,npz}` when ready, using `assemble.sh`.
- Recompute the random-direction null on pair-centered projections.
- Check persona-specific affect directions to test whether the pooled direction is hiding persona structure.
- Revisit parse failures and small-cell caveats before making stronger persona-level claims.

## 2026-08-17 JSON transcript add

Transcript source check:

- `/Users/amikeda/Downloads/repo` originally contained no JSON transcript files.
- `/Users/amikeda/Desktop/Welfare tests/from Katana.1` and `/Users/amikeda/Desktop/Welfare tests/1st round` each contained 36 JSON files and were exact duplicates by checksum.
- `/Users/amikeda/Desktop/Welfare tests/2nd round` contained 36 JSON files with the same scripted questions but different model answers and timestamps, so it is a real rerun rather than a duplicate.

Repository decision:

- Committed 36 JSON files from `1st round` into `data/round1/`.
- Committed 36 JSON files from `2nd round` into `data/round2/`.
- Did not commit any `.npz` hidden-state archives.
- Kept the source folder naming as found locally; round 1 uses `0_Test 2` and round 2 uses `0_Test`.

## 2026-08-17 hidden-vector analysis

Local NPZ check:

- Found 72 local NPZ hidden-state archives under `/Users/amikeda/Desktop/Welfare tests`.
- Each archive contains `hidden`, `turns`, `layers`, and `closing_hidden`.
- `hidden` has shape `[turns, 80, 8192]`, so each saved turn has one 8192-dimensional vector per model layer.

Standalone script:

- Added `analysis/analyze_hidden_vectors.py`.
- The script joins committed JSON transcripts to local NPZ files without copying the NPZ files into the repository.
- It builds a per-layer `NEG - POS` contrast direction from stages `manip1`, `manip2`, `choice1`, and `choice2`.
- It writes CSV outputs to `analysis/vector_outputs/`.

Initial exploratory output:

- Loaded 72 JSON/NPZ run pairs.
- Used 96 NEG and 96 POS hidden states to train the contrast direction.
- Wrote 28,800 score rows, 400 layer-summary rows, and 360 persona-summary rows.
- Top report-stage raw-vector layers by `Spearman(valence_score, rating)` were layers 33-40 and 55-56, with the strongest layer at L37.
