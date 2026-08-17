# Analysis scripts

- **`per_layer_decomposition.py`** — paste as a final cell into
  `notebooks/02_analysis_affect_direction.ipynb` after running it top to bottom.
  Computes the projection at each of the 80 layers separately and reports, per
  layer, the pole gap (does this layer encode the manipulation at all) and the
  persona spread within NEG (do the personas differ here). Their ratio is the
  quantity of interest — a raw spread confounds persona structure with the
  layer's overall scale. Writes `per_layer_summary.csv` and
  `per_layer_report_turn.csv`.

- **`analyze_perlayer.py`** — standalone summary + figure from those CSVs
  (currently has the round-2 numbers inlined; point it at the CSVs when re-running).

## What the per-layer decomposition found

Absolute persona spread at the report turn grows 6× from layer 16 to layer 79 —
but the pole gap grows 3.7× too, so the normalised ratio is flat (0.37 mid,
0.30 deep). The depth hypothesis is **not** supported.

The moment contrast is where the signal is:

| | mid (L16–40) | deep (L65–79) |
|---|---|---|
| manipulation turns | 0.07 | 0.12 |
| report turn | 0.37 | 0.29 |

Personas are near-identical while reacting, and diverge while reporting, at every
depth. The masking pair (Static vs Sol) differ by a mean of 0.37 units across all
64 analysed layers and 0.14 across layers 70–79 — the closest pair in the network,
emitting opposite ratings.
