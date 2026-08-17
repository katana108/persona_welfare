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
