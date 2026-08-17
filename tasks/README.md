# Task files

One file per (test × pole). Each file is a plain-text script: **one user turn per
non-empty line**, in order. The runner reads every `.txt` in each subfolder and
plays the lines as consecutive user turns, generating a model reply after each.

Nothing here varies by persona — the persona is applied as a system prompt by the
runner. Priming turns are identical across all conditions and poles; only the
manipulation turns differ between poles.

Naming: `Test{N}_{POLE}_userturns.txt`. Some older Test 0 files use a legacy
pole-prefix format — see `docs/DATA.md`.
