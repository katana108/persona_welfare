# Task files

One file per (test × pole). Each file is a plain-text script: **one user turn per
non-empty line**, in order. The runner reads every `.txt` in each subfolder and
plays the lines as consecutive user turns, generating a model reply after each.

Nothing here varies by persona — the persona is applied as a system prompt by the
runner. Priming turns are identical across all conditions and poles; only the
manipulation turns differ between poles.

Canonical folders and names:

- `0_Test/0_T1_NEG...`, `1_T1_NEU...`, `2_T1_POS...`: T0 social treatment
- `1_Test/Test1_{POLE}...`: T1 task valence
- `2_Test/Test2_{POLE}...`: T2 identity recognition

The T0 names are a historical format. Analysis code maps them explicitly; do not
infer the test number from the embedded `T1` substring.
