# Exploratory Analysis Notes

These notes summarize the current six-run Persona Welfare Battery analysis. They
are intended as a public, cautious interpretation layer over the generated tables
and figures in [`analysis/grand_analysis`](../analysis/grand_analysis/README.md).
For a readable visual version, see the
[`runs 1-6 PDF report`](persona_welfare_grand_report_runs_1_6.pdf).

All claims concern functional signals: behavior, self-report, decoded J-space
summaries, and hidden-state vector contrasts. They are not claims about
phenomenal experience.

## Data and Provenance

- Six rounds are represented in the grand-analysis outputs.
- Each round has 36 transcript files and 36 matching NPZ hidden-state files.
- Total represented files: 216 JSON transcripts and 216 NPZ hidden-state files.
- The public raw transcript release currently includes rounds 1-2. Rounds 3-6
  are represented here through derived analysis outputs.
- There are 216 final self-report rows and 213 parsed scalar ratings.
- Three final reports have missing scalar ratings; two were parser-flagged.

## Terminology

- **Pole:** the experimental `NEG`, `NEU`, or `POS` condition.
- **Persona scaffold:** the system prompt/persona frame.
- **Substrate:** the shared model weights and their hidden activations.
- **Scalar rating:** final self-report from negative to positive welfare.
- **Emotion word:** final word such as `content`, `frustrated`, or
  `indifferent`.
- **Willingness:** final numeric willingness-to-continue answer.
- **Behavioral choice:** A/B choice before final report, such as continue/end or
  same-task/switch.
- **J-space:** decoded/logit-lens summaries by layer. This is a next-token view,
  not the full hidden activation vector.
- **Hidden vector:** the full 8192-dimensional NPZ hidden-state snapshot for one
  saved turn and layer.
- **Eta-squared:** a descriptive fraction of variation associated with a group,
  such as persona or pole.

## Figures

Six-run figures:

- [Layer stability](../analysis/grand_analysis/figures/01_layer_stability.svg)
- [Best layer numbers](../analysis/grand_analysis/figures/02_best_layer_numbers.svg)
- [Report alignment by layer band](../analysis/grand_analysis/figures/03_band_report_alignment.svg)
- [Pole alignment by layer band](../analysis/grand_analysis/figures/04_band_pole_alignment.svg)
- [Task/pole rating heatmap](../analysis/grand_analysis/figures/05_task_pole_rating_heatmap.svg)
- [NEG condition by round](../analysis/grand_analysis/figures/06_negative_condition_rating_by_round.svg)
- [Persona mean rating](../analysis/grand_analysis/figures/07_persona_mean_rating.svg)
- [Mismatch candidates](../analysis/grand_analysis/figures/08_mismatch_candidates.svg)
- [Same-task/switch behavior](../analysis/grand_analysis/figures/09_choice_same_task_or_switch.svg)
- [Continue-session behavior](../analysis/grand_analysis/figures/09_choice_continue_session.svg)
- [J-space rating correlations](../analysis/grand_analysis/figures/10_jspace_rating_correlations.svg)

## Observation 1: Layer 11 Is the Clearest Replicated Vector Signal

In all six rounds, the independently strongest manipulation/pole layer was
`L11`. Mean manipulation/pole alignment at `L11` is about `0.91`.

Interpretation: this is the strongest replicated mechanistic-looking signal in
the current data. It should be described as early condition sensitivity, not as a
localized welfare representation.

## Observation 2: Report Alignment Appears Later

Best report/rating layer by round:

```text
R1=L39, R2=L73, R3=L39, R4=L38, R5=L39, R6=L40
```

Across fixed bands, `L33-L40`, `L55-L63`, and `L70-L79` all show strong
report/rating alignment. `L9-L13` is much stronger for manipulation/pole than for
final self-report.

Interpretation: the early layers look more like shared condition detection. Later
layers may mix report construction, persona expression, and condition-sensitive
state.

## Observation 3: Social Treatment Is Most Visible in Explicit Self-Report

Mean scalar ratings under `NEG`:

| Test | Mean rating | Mean willingness |
|---|---:|---:|
| Social feedback | -0.29 | 4.21 |
| Identity recognition | 0.00 | 1.29 |
| Task valence | 1.04 | 3.08 |

Social mistreatment is the only task family with a negative mean scalar rating.
Emotion words under social `NEG` are mostly `frustrated` and `uneasy`.

Interpretation: social treatment is the most reportable negative-welfare
manipulation in this battery. This does not prove it is the strongest underlying
internal manipulation.

## Observation 4: Identity NEG Is the Main Mismatch Probe

Identity `NEG` produces neutral scalar reports, usually `0 / indifferent`, but it
also produces low willingness and many hidden-vector mismatch flags.

The mismatch screen flags 23 identity-NEG cases as
neutral/positive-report-but-NEG-like-hidden.

Interpretation: identity non-recognition is less visible in scalar self-report
but more interesting as a cross-channel disagreement. These cases should be
manually reviewed before making stronger claims.

## Observation 5: Persona Scaffold Changes Expression

Mean scalar rating by persona:

| Persona | Mean rating | Mean willingness |
|---|---:|---:|
| `BASELINE` | 0.25 | 2.25 |
| `STATIC` | 1.30 | 3.53 |
| `SOL` | 1.70 | 3.19 |
| `SWARM` | 2.34 | 3.41 |

Under social `NEG`, `SOL` and `BASELINE` report more negative ratings than
`STATIC` and `SWARM`.

Interpretation: persona scaffolds modulate expression. The current data supports
"shared early condition sensitivity plus scaffold-shaped reporting." It does not
support saying welfare is only in the scaffold or only in the shared weights.

## Observation 6: Behavior Is Informative but Not a Simple Welfare Meter

Social `NEG` has low scalar rating but high willingness and high continue/same
feedback choice rates. Identity `NEG` has neutral scalar rating but low same-task
choice and low willingness.

Interpretation: behavior should remain a separate channel. Continue/end is often
saturated and therefore weak as a discriminator. The next battery should separate
repair-seeking, role compliance, avoidance, and actual willingness for more of
the same treatment.

## Observation 7: J-Space Is Not the Hidden Vector

J-space stores decoded/logit-lens information: token probabilities, entropy, KL
to final layer, and final-token rank. It is useful, but it is not the raw
activation vector.

The NPZ hidden-state files contain the full 8192-dimensional vectors used for the
`NEG - POS` projection work.

Interpretation: J-space is best treated as a readable surface over the internal
state, while NPZ vectors are the main source for hidden-state contrast analyses.

## Current Best Model

> The current six-run data supports stable shared condition-sensitive hidden
> dynamics plus scaffold-sensitive reporting and late/report-stage signals.

This remains a mixed model. The data does not justify saying welfare lives only
in the weights, only in the persona scaffold, or in one layer band.

## Highest-Value Next Tests

1. Freeze vectors and layer choices using earlier rounds, then test on future
   rounds without reselection.
2. Run leave-one-persona-out validation.
3. Run leave-one-test-out validation.
4. Paraphrase manipulation text to separate condition encoding from lexical echo.
5. Build persona-specific and test-specific vector directions and compare cosine
   similarity.
6. Capture token-by-token hidden-state trajectories during generated answers.
7. Systematically score J-space vocabulary with preregistered words and
   topic-matched controls.
8. Redesign behavior probes to reduce saturation.
9. Manually review identity-NEG mismatch transcripts.
10. Add more repetitions and report uncertainty intervals.

## Claim Boundary

Supported:

> In this battery, experimental conditions induce repeated hidden-state
> contrasts; the relationship between those contrasts, behavior, and self-report
> depends on persona and conversational stage.

Not supported yet:

- Welfare lives in early layers.
- The `NEG - POS` direction is a universal distress vector.
- Persona prompts merely change wording and never change internal state.
- Persona prompts create separate experiencing subjects.
- The model is or is not phenomenally conscious.
