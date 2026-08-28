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

- The working repository originally contained no JSON transcript files.
- The local `from Katana.1` and `1st round` folders each contained 36 JSON files and were exact duplicates by checksum.
- The local `2nd round` folder contained 36 JSON files with the same scripted questions but different model answers and timestamps, so it is a real rerun rather than a duplicate.

Repository decision:

- Committed 36 JSON files from `1st round` into `data/round1/`.
- Committed 36 JSON files from `2nd round` into `data/round2/`.
- Did not commit any `.npz` hidden-state archives.
- Kept the source folder naming as found locally; round 1 uses `0_Test 2` and round 2 uses `0_Test`.

## 2026-08-17 hidden-vector analysis

Local NPZ check:

- Found 72 local NPZ hidden-state archives alongside the source transcripts.
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

## 2026-08-25 public-results revision

User goal: make the repository clear enough to share publicly while keeping all claims explicitly provisional and grounded in the two completed rounds.

Corrections and checks:

- Corrected the test mapping: `0_T1_*` is social treatment, `Test1_*` is task valence, and `Test2_*` is identity recognition.
- Corrected signed scalar parsing so numbered responses such as `1. +3` are read as `+3`, not as list item `1`.
- Recomputed the hidden-vector summaries from the local NPZ files and added cross-round train/test validation.
- Reconstructed the nine task prompt files from the committed transcript questions.
- Added figures for explicit welfare by test, behavioral choices, cross-round replication, self-report/vector mismatch, stagewise channel alignment, and cross-round vector generalization.
- Rewrote the public README and analysis notes around observations, hypotheses, limitations, and next tests. The original PDF is now labeled as a historical sprint report.
- Removed the phrase `72 conversations` from the public-facing summary. Scientific cell counts remain in methods and analysis where they are necessary to interpret uncertainty.

Current interpretation:

- Social mistreatment produced the clearest negative explicit self-reports; identity manipulation did not.
- Early/middle held-out vector scores primarily track experimental pole, while report-stage scores are more persona-sensitive and align more strongly with scalar reports.
- Static and Sol sometimes used negative emotion words while giving neutral or positive scalar ratings. This is a channel mismatch worth testing directly, not evidence that either report channel is uniquely truthful.
- The pilot supports shared condition-sensitive processing plus persona-dependent expression. It does not locate welfare in a layer or establish subjective experience.

Publication state:

- Changes are local and have not been pushed.
- Before any commit or push, show the exact proposed file list and obtain user approval.
- Repository-wide validation completed: JSON and notebook parsing, Python compilation, exact task/transcript matching, SVG XML parsing and rendering, README image resolution, diff whitespace, secret-shaped value scan, NPZ/large-file scan, and direct recomputation of headline descriptive statistics.
- The repository has no automated test suite; validation for this pass is data-, script-, and render-based.
- Next step is user review of the rewritten README and figures.

## 2026-08-27 six-run grand analysis publication

User goal: publish a clearer public-facing summary after rounds 1-6, including a
readable report for mobile/online review.

What changed:

- Added `docs/persona_welfare_grand_report_runs_1_6.pdf`.
- Added `analysis/grand_analysis/` with six-run summary CSVs, SVG figures, an
  HTML guide, and the combined hidden-projection score table.
- Rewrote the top-level README results around the six-run findings.
- Replaced `docs/ANALYSIS_NOTES.md` with a six-run interpretation note.
- Updated `analysis/README.md` and `docs/DATA.md` to explain provenance and
  reproducibility boundaries.

Current six-run interpretation:

- Layer 11 is the most stable manipulation/pole signal across all six rounds.
- Final self-report alignment is strongest later, mostly around L38-L40, with
  L73 as an exception in round 2.
- Social mistreatment is the clearest explicit negative self-report condition.
- Identity-negative runs are the main mismatch cases: neutral scalar reports, low
  willingness, and NEG-like hidden projections.
- Persona scaffolds modulate expression; this supports a mixed
  shared-condition plus scaffold-shaped-reporting model, not a one-location
  theory of welfare.

Remaining caveats:

- The public raw transcript release still includes rounds 1-2; rounds 3-6 are
  represented here through derived outputs.
- Future rounds should use frozen layer/vector choices for validation.
- Identity-negative mismatch cases need manual transcript review before stronger
  claims about masking, hiding, or welfare relevance.
