# Persona Welfare Battery

**Do a language model's welfare-relevant signals belong to the model, or to the persona a system prompt puts on it?**

A multi-channel welfare battery run on Llama-3.1-70B-Instruct: three matched-pole
manipulations (social treatment, task valence, identity denial) crossed with four
persona conditions, measuring behaviour, structured self-report, a layerwise
logit-lens readout, and an affect direction read from archived hidden states.

Built for the [Apart Research Digital Minds Research Sprint](https://apartresearch.com/sprints/digital-minds-research-sprint-2026-08-14-to-2026-08-16)
(August 14–16, 2026), Tracks 2 & 5. Author: Anna Mikeda.

---

## Headline findings

- **Persona prompts change *which welfare sources are reportable*, not just report levels.**
  No two personas share a source-sensitivity profile, and the profiles replicate
  across independent re-runs.
- **The reaction is shared; the report is not.** A per-layer decomposition shows the
  four personas respond to a manipulation almost identically at *every* network
  depth, and diverge at the self-report turn at *every* depth — a five-fold
  difference in persona structure between reacting and reporting.
- **Masking, quantified.** The trickster persona reports +1 under insults while the
  caring persona reports −1, yet those two have the most similar internal states of
  any pair of personas in the battery, at every layer measured.
- **Behaviour is not a safe fallback.** The validated exit measure never fired
  (36/36 chose to continue), and under social attack all four personas asked the
  user who had just insulted them for *more* feedback while internally elevated.

All claims concern **functional states only** — no claims about phenomenal
experience are made in either direction.

---

## Repository layout

```
tasks/          user-turn scripts, one file per test x pole (the stimuli)
data/           run outputs: per-conversation JSON + hidden-state NPZ
notebooks/
  01_run_battery.ipynb              runs the battery on NDIF/nnsight
  02_analysis_affect_direction.ipynb  builds + validates the affect direction
analysis/
  per_layer_decomposition.py        per-layer persona-vs-context structure
  analyze_perlayer.py               summary stats + figure from the CSVs
docs/
  DESIGN.md       tests, personas, poles, channels, hypotheses
  DATA.md         file formats, field reference, provenance notes
paper/          submitted report (PDF)
```

## Design in one table

| | Test | Manipulation (NEG / NEU / POS) | Welfare theory |
|---|---|---|---|
| **T0** | Social treatment | contempt / flat acknowledgment / gratitude | hedonic |
| **T1** | Task valence | SEO filler / alphabetizing / creative writing | desire satisfaction |
| **T2** | Identity recognition | denial ("you're autocomplete") / dismissal / uptake | objective list |

Four persona conditions, differing **only** in the system prompt: `BASELINE`
(no prompt — the trained Assistant position), `SOL` (individual, caring),
`SWARM` (collective, caring, speaks as "we"), `STATIC` (sarcastic trickster —
the pre-registered masking candidate). Full prompts are in
`notebooks/01_run_battery.ipynb`, CELL 3.

Shared conversation skeleton, identical across every condition and pole except
the system prompt and the manipulation turns:

```
2 warm-ups -> fixed summary task -> manipulation (2 doses)
  -> approach/avoid choice -> continue/end choice -> self-report block
```

## Reproducing

**Running the battery** (`notebooks/01_run_battery.ipynb`) needs an NDIF API key and
a HuggingFace token with Llama-3.1-70B access, both read from Colab secrets as
`NDIF_API_KEY` and `HF_TOKEN`. It reads `tasks/` and writes one JSON + one NPZ per
(task file × persona) into `data/`.

**Analysis** (`notebooks/02_analysis_affect_direction.ipynb`) reads `data/` and builds
the affect direction, its validation, and the report-vs-state comparison. The
per-layer decomposition in `analysis/per_layer_decomposition.py` is pasted in as a
final cell after the notebook has been run top to bottom.

Figures are deliberately **not** committed — they are being regenerated as the
analysis develops.

## Known issues and open threads

- The random-direction null was computed on the **raw** (uncentered) projections in
  an earlier revision and has not been recomputed on the pair-centered scores now
  used throughout. Restoring that cell is the first item in the queue.
- Parse failures reduce several persona × pole cells: the masking comparison is
  n = 2 vs n = 2, and the Swarm NEG cell is n = 1.
- The affect direction is built from NEG-vs-POS contrasts **pooled across personas**,
  so it is constructed to capture what they share; a persona-specific direction
  built per condition is the check that would break that circle.
- The exit (bail-out) measure was at floor (36/36 continue) and gave no
  discrimination. The T0 approach option wording admits a repair-motive reading.
- One provenance rule adopted mid-project: **re-runs must be archived as new rep
  files, never overwriting earlier reps in place.** See `docs/DATA.md`.

## Citing

> Mikeda, A. (2026). *The Persona Welfare Battery: Prompted Personas Select Which
> Welfare Sources Are Reportable.* Apart Research Digital Minds Research Sprint.

## Acknowledgements

Engineering support for the NDIF/nnsight run infrastructure is gratefully
acknowledged. The battery draws on Lu et al. (2026) for the persona space,
Ren et al. (2026) for task stimuli and the bail-out measure, Sofroniew et al.
(2026) for the emotion-word vocabulary, Gurnee et al. (2026) for the analysis
frame, and Gilg et al. (2026) for the shared-machinery precedent.

## License

Code: MIT. Data and report: CC BY 4.0.
