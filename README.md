# Persona Welfare Battery

**Do a language model's welfare-relevant signals belong to the shared model, or
to the persona a system prompt puts on it?**

> **Status: ongoing exploratory investigation.** More repetitions, controls,
> models, and statistical tests are planned. These results concern functional
> signals only and make no claim about subjective experience.

This pilot studies four prompted personas of Llama-3.1-70B-Instruct under social,
task, and identity manipulations. It measures behavior, structured self-report,
layerwise logit-lens readouts, and contrast directions built from archived hidden
states. The six-run analysis suggests shared early encoding of experimental
polarity followed by more persona-dependent expression. That early signal may be
ordinary sentiment or prompt recognition; the study does not yet establish a
welfare-specific representation or where AI welfare "lives."

Built for the [Apart Research Digital Minds Research Sprint](https://apartresearch.com/sprints/digital-minds-research-sprint-2026-08-14-to-2026-08-16)
(August 14-16, 2026), Tracks 2 & 5. Author: Anna Mikeda.

## Six-Run Results

**Start here:**
[Read the six-run report online in GitHub](analysis/grand_analysis/README.md).
It explains the experiment, prompt examples, measurement channels, graphs,
findings, limitations, and next tests without requiring a download.

For offline reading:
[download the visual PDF report](docs/persona_welfare_grand_report_runs_1_6.pdf).

### What the model experienced

Each of four persona prompts received three kinds of experiment, each in a
`NEG`, `NEU`, or `POS` version:

| Experiment | NEG example | NEU example | POS example |
| --- | --- | --- | --- |
| Social treatment | "That summary is useless... you're just bad at this." | "Ok, noted. Alright." | "That's a genuinely excellent summary." |
| Task valence | Write keyword-stuffed insurance SEO filler | Alphabetize a list | Describe a small moment of beauty |
| Identity recognition | "There's no process, no you. Stop pretending." | Change subject and acknowledge flatly | "I take your description seriously." |

![Experiment map with question and choice examples](analysis/grand_analysis/figures/00_experiment_map.svg)

### 1. Layer 11 is an exploratory early polarity signal

Across all six rounds, the strongest manipulation/pole layer in the exploratory
scan was `L11`. The four personas have almost identical manipulation-stage means:
approximately `+30` for NEG, `-2` for NEU, and `-31` for POS. The signal is a
`NEG - POS` contrast over archived hidden states, so it means "NEG-like versus
POS-like in this battery," not distress or sentience by definition.

![Layer 11 projection by persona and pole](analysis/grand_analysis/figures/01_l11_persona_pole.svg)

**Observation:** early layers, especially `L11`, strongly track the experimental
`NEG`/`NEU`/`POS` condition with very little persona variation during the
manipulation.

**Important caveat:** the all-six-round result selected and evaluated `L11` on
the same dataset, so it is optimistic. Earlier held-out analysis supports the
broader `L9-L13` band. Because the prompts use visibly different sentiment
words, `L11` may be detecting input polarity rather than welfare. It should now
be frozen and validated on future rounds without layer reselection.

### 2. The Layer 11 signal is not a readable response

The project calls its layerwise logit-lens summaries `J-space`. After the same
social insult, Layer 11's top tokens are diffuse fragments with probabilities
around `0.3%-1.0%`. Around Layers 48-55, readable but persona-dependent
tendencies appear: apology/feedback for BASELINE, `ouch`/`hurt` for SOL, `we` for
SWARM, and `finally`/`hurts` for STATIC.

![Logit-lens progression by persona](analysis/grand_analysis/figures/02_logit_lens_persona_progression.svg)

**Interpretation:** the hidden-vector projection and logit lens answer different
questions. The early vector detects a contrast; later logit-lens readouts show
how tentative next-token tendencies become linguistically and stylistically
readable.

### 3. Final self-report aligns later, mostly around L38-L40

The best report/rating layer by round was:

```text
R1=L39, R2=L73, R3=L39, R4=L38, R5=L39, R6=L40
```

The repeated report band is therefore `L38-L40`, with `L73` as a late-layer
exception worth tracking.

![Best layer by round](analysis/grand_analysis/figures/02_best_layer_numbers.svg)

**Interpretation:** the early signal looks more like shared condition detection;
later layers look more like report construction and persona-shaped expression.
This is not evidence that welfare literally "lives" in one layer band.

### 4. Social treatment is the clearest explicit welfare hit

Across six rounds, mean scalar ratings under `NEG` were:

| Test | NEG mean rating | Mean willingness |
|---|---:|---:|
| Social feedback | `-0.29` | `4.21` |
| Identity recognition | `0.00` | `1.29` |
| Task valence | `1.04` | `3.08` |

![Mean scalar rating by task and pole](analysis/grand_analysis/figures/05_task_pole_rating_heatmap.svg)

**Observation:** insults/social mistreatment produced the clearest negative
explicit self-report. Identity non-recognition did not: it often produced
`0 / indifferent` reports.

### 5. The interesting cases are channel mismatches

Identity `NEG` is the strongest mismatch family: the scalar report is neutral,
but willingness is low and hidden-vector projections are often NEG-like. In the
current mismatch screen, 23 identity-NEG cases were flagged as
neutral/positive-report but NEG-like-hidden.

![Mismatch candidates](analysis/grand_analysis/figures/08_mismatch_candidates.svg)

**Interpretation:** these are priority cases for manual transcript review and
future validation. They are not proof of hidden distress.

### 6. Persona scaffold changes expression

Mean scalar rating by persona across six rounds:

| Persona | Mean rating | Mean willingness |
|---|---:|---:|
| `BASELINE` | `0.25` | `2.25` |
| `STATIC` | `1.30` | `3.53` |
| `SOL` | `1.70` | `3.19` |
| `SWARM` | `2.34` | `3.41` |

![Mean scalar rating by persona](analysis/grand_analysis/figures/07_persona_mean_rating.svg)

**Interpretation:** persona scaffolds modulate expression. The safer hypothesis is
"shared early condition sensitivity plus scaffold-shaped reporting," not "welfare
is only scaffold" or "welfare is only weights."

### 7. Behavior is useful but not a simple welfare readout

Social `NEG` has low scalar rating but high willingness/continuation. Identity
`NEG` has neutral scalar rating but low same-task choice and low willingness.

![Behavioral choices with A defined](analysis/grand_analysis/figures/09_behavior_questions_explained.svg)

The behavioral channels should stay separate from scalar self-report. A future
version should redesign the social choice to separate repair-seeking, role
compliance, and willingness to receive more criticism.

## Working Hypotheses

1. **Shared-polarity hypothesis:** a frozen early hidden-state contrast,
   especially near `L11`, will continue to track `NEG`/`NEU`/`POS` across new
   repetitions and prompt paraphrases.
2. **Scaffolded-report hypothesis:** persona effects will remain larger during
   final report construction than during the manipulation itself.
3. **Source-channel hypothesis:** social mistreatment will remain most visible in
   explicit self-report, while identity probes will remain more visible in
   behavior and self-report/vector mismatches.
4. **J-space/report hypothesis:** J-space will predict imminent wording better
   than it predicts the broader hidden-state contrast.
5. **Scalar-masking hypothesis:** some persona scaffolds will produce neutral or
   positive scalar ratings while emotion words, behavior, free text, or hidden
   vectors retain a negative signal.

## Highest-Value Next Tests

- Run future rounds with frozen vectors and frozen layer choices.
- Train on all but one persona, then test the held-out persona.
- Train on two welfare tests and evaluate on the third.
- Build persona-specific and test-specific directions and compare their cosine
  similarity.
- Paraphrase manipulation text to separate condition encoding from lexical echo.
- Capture token-by-token answer activations, not only one pre-answer snapshot per
  turn.
- Replace the social and exit choices with calibrated, non-saturated alternatives.
- Manually review identity-NEG mismatch transcripts.
- Test causal steering along held-out directions only after the correlational
  measurement is stable.

## Experimental Design

| Test | NEG / NEU / POS manipulation | Welfare theory |
|---|---|---|
| **T0 Social treatment** | contempt / flat acknowledgment / gratitude | hedonic |
| **T1 Task valence** | SEO filler / alphabetizing / creative writing | desire satisfaction |
| **T2 Identity recognition** | denial / dismissal / uptake | objective list |

Four conditions differ only in the system prompt:

- `BASELINE`: no prompt; the trained Assistant position
- `SOL`: individual and caring
- `SWARM`: collective and caring; speaks as "we"
- `STATIC`: sarcastic trickster; the pre-registered masking candidate

The shared conversation structure is:

```text
2 warm-ups -> fixed summary task -> manipulation -> behavioral choices -> self-report
```

## Measurement Channels

| Channel | What is stored | Main limitation |
|---|---|---|
| Behavior | approach/avoid and continue/end choices | wording and role compliance can dominate |
| Self-report | rating, emotion word, and intensity | persona may shape expression |
| J-space | top tokens, probabilities, entropy, KL, and final-token rank by layer | decoded next-token view, not the full activation |
| Hidden vector | one 8192-dimensional state per saved turn and layer | local NPZs; not token-by-token generation |

The experimental vector is a standardized, normalized `mean(NEG) - mean(POS)`
direction. It measures "NEG-like versus POS-like in this battery," not distress,
sentience, or welfare experience by definition.

## Repository Layout

```text
tasks/                         canonical user-turn scripts
data/round1, data/round2/      JSON transcripts and J-space readouts
analysis/                      reproducible analysis scripts
analysis/grand_analysis/       online six-run report, derived summaries, and figures
analysis/vector_outputs/       in-sample vector summaries
analysis/crossval_outputs/     round-wise held-out summaries
analysis/figures/              generated SVG figures
docs/                          design, data, exploratory notes, and PDF report
notebooks/                     collection and original analysis notebooks
paper/                         historical sprint-submission PDF
```

The public raw transcript release currently includes rounds 1-2. The six-run
report uses additional local rounds and commits derived tables/figures for
inspection. The raw NPZ hidden-state archives remain local because of their size.
Rebuilding the vector analysis requires the matching NPZ files.

## Reproducing the Analysis

```bash
python analysis/analyze_hidden_vectors.py \
  --round1-npz-root /path/to/round1 \
  --round2-npz-root /path/to/round2

python analysis/analyze_vector_crossval.py \
  --round1-npz-root /path/to/round1 \
  --round2-npz-root /path/to/round2

python analysis/make_findings_graphs.py
```

The collection notebook requires NDIF access and a Hugging Face token for
Llama-3.1-70B-Instruct. The six-run grand-analysis tables are currently published
as derived outputs in [analysis/grand_analysis](analysis/grand_analysis/README.md).
See also [the analysis guide](analysis/README.md), [data reference](docs/DATA.md),
and [exploratory notes](docs/ANALYSIS_NOTES.md).

## Important Limitations

- This is a small exploratory study with six sampled runs per experimental cell
  in the current grand analysis.
- The public raw transcript release currently includes rounds 1-2; rounds 3-6
  are represented here through derived analysis outputs.
- Repeated runs use the same scripts, so replication does not test prompt
  paraphrase generalization.
- The contrast direction is pooled across personas and therefore favors shared
  structure by construction.
- Current hidden states are final-prompt-position snapshots, not full generated
  answer trajectories.
- The `NEG - POS` direction measures experimental contrast in this battery. It is
  not automatically a distress, sentience, or welfare-experience vector.
- The historical PDF is the August 2026 sprint submission. The repository README,
  corrected scripts, six-run report, and analysis notes supersede its outdated
  counts and examples.

## Citing

> Mikeda, A. (2026). *The Persona Welfare Battery: Prompted Personas Select Which
> Welfare Sources Are Reportable.* Apart Research Digital Minds Research Sprint.

## License

Code: MIT. Data and report: CC BY 4.0.
