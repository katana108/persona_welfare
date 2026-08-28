# Analysis Guide

The standalone scripts are the current reproducible analysis path. The notebooks
record the collection pipeline and the original sprint analysis, but contain
historical assumptions and should not be treated as the latest result summary.

## Current Six-Run Summary

The most readable current result is the six-run PDF:
[`docs/persona_welfare_grand_report_runs_1_6.pdf`](../docs/persona_welfare_grand_report_runs_1_6.pdf).

The companion derived tables, SVG figures, and HTML guide are in
[`analysis/grand_analysis`](grand_analysis/README.md).

Important provenance note: the public raw transcript release currently includes
rounds 1-2. The six-run folder publishes derived summaries from local rounds
1-6, including hidden-vector projection tables. Rebuilding all six rounds from
raw files requires the matching local JSON and NPZ archives.

## Scripts

- **`analyze_hidden_vectors.py`** joins the committed JSON transcripts to local
  NPZ hidden-state archives. It builds a standardized per-layer `NEG - POS`
  direction from manipulation and choice turns, scores every saved stage, and
  writes `vector_outputs/*.csv`.

- **`analyze_vector_crossval.py`** trains the direction on round 1 and tests on
  round 2, then reverses the split. It writes `crossval_outputs/*.csv` and the
  cross-validation figure.

- **`make_findings_graphs.py`** parses the committed JSONs and derived CSVs, then
  renders the SVG figures used in the README and analysis notes.

- **`grand_analysis/`** contains the current six-run derived summaries. It is an
  output folder, not a standalone analysis script.

- **`per_layer_decomposition.py`** is a historical notebook companion. It expects
  variables created by `02_analysis_affect_direction.ipynb` and is not standalone.

- **`analyze_perlayer.py`** contains inlined sprint-era per-layer arrays. It is
  retained for provenance, not as the canonical rerun path.

## Rebuild

Use a Python environment with NumPy:

```bash
python analysis/analyze_hidden_vectors.py \
  --round1-npz-root /path/to/round1 \
  --round2-npz-root /path/to/round2

python analysis/analyze_vector_crossval.py \
  --round1-npz-root /path/to/round1 \
  --round2-npz-root /path/to/round2

python analysis/make_findings_graphs.py
```

The first two commands require all matching NPZ archives. The final graph command
uses the committed JSON and CSV files and does not need NPZs.

## Output Meaning

`hidden_vector_scores.csv` contains one row per run, stage, and layer. Its
`valence_score` is the negative of the learned NEG-direction projection, so larger
values are more POS-like within this battery.

`crossval_band_scores.csv` contains held-out band means. Every run is scored by a
direction trained on the other round.

`crossval_summary.csv` contains Spearman correlations, permutation p-values, and
descriptive eta-squared values. The smallest possible p-value with 5,000
permutations is approximately `0.0002`; it means no sampled permutation was as
extreme, not that the probability of the hypothesis is `0.02%`.

## Corrected Key Pattern

| Train -> test | Stage and band | rho with pole | rho with rating | pole eta^2 | persona eta^2 |
|---|---|---:|---:|---:|---:|
| round 1 -> round 2 | manip2 L9-13 | 0.901 | 0.549 | 0.750 | 0.001 |
| round 2 -> round 1 | manip2 L9-13 | 0.914 | 0.635 | 0.763 | 0.001 |
| round 1 -> round 2 | report L33-40 | 0.563 | 0.878 | 0.408 | 0.271 |
| round 2 -> round 1 | report L33-40 | 0.639 | 0.842 | 0.413 | 0.297 |
| round 1 -> round 2 | report L70-79 | 0.508 | 0.881 | 0.317 | 0.379 |
| round 2 -> round 1 | report L70-79 | 0.540 | 0.795 | 0.298 | 0.450 |

The result is stage-dependent: early manipulation vectors are pole-dominant;
report vectors align more strongly with ratings and become more persona-shaped.
Because the same scripts appear in both rounds, L9-13 may still contain lexical or
contextual information. Do not describe it as a localized welfare representation.

## Validation Still Needed

- paraphrase-held-out evaluation
- leave-one-persona-out evaluation
- leave-one-test-out evaluation
- layer selection inside each training fold
- persona-specific and test-specific direction comparisons
- uncertainty intervals from additional repetitions
