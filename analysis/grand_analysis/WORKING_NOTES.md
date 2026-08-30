# Working Notes: Grand Analysis Runs 1-6

Created from existing per-round analysis CSVs under `local per-round analysis outputs for rounds 1-6`.

Current claim boundary: these are exploratory repeated-run patterns, not final
welfare claims. The all-layer scan identifies L11 as a nearly persona-invariant
early polarity detector, but that result is partly in-sample and may reflect
prompt sentiment or lexical cues. Earlier held-out analysis supports the broader
L9-L13 band. Freeze L11 before using it as a future validation target.

The outside-reader revision adds real prompt examples, exact behavioral choice
definitions, Layer 11 means by persona/pole, and a Round-1 social-NEG logit-lens
progression. The latter demonstrates that Layer 11 vector separation is not the
same as a readable or shared response: readable persona-specific tendencies
emerge later, around Layers 48-55 in the selected example.

The most interesting open question remains the mismatch between neutral/positive
self-report and NEG-like hidden projections, especially in identity-recognition
NEG cases.

Round inputs were not re-parsed from raw JSON/NPZ in this grand pass; this pass aggregates the already-generated round-level outputs. For publication-grade refresh, rerun each round from raw files first, then rerun this combined guide.

`analysis/make_grand_report.py` regenerates the outside-reader SVG figures and
the single canonical `docs/` PDF from committed derived tables plus one published
Round-1 JSON example.
