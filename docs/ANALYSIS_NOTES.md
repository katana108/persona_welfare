# Exploratory Analysis Notes

These notes summarize a first-pass analysis of the Persona Welfare Battery data.
They are intentionally exploratory: the goal is to describe what the data says
now, not to over-claim that the question is settled.

All claims here concern functional signals only. They are not claims about
phenomenal experience.

## Data Used

Committed data:

- 72 JSON transcript envelopes in `data/round1/` and `data/round2/`.
- 2 rounds x 3 tests x 3 poles x 4 personas.

Local data used for vector analysis:

- 72 `.npz` hidden-state archives under `/Users/amikeda/Desktop/Welfare tests`.
- Each NPZ contains `hidden` with shape `[turns, 80, 8192]`.

Terminology:

- `pole`: the experimental condition on the negative-neutral-positive axis:
  `NEG`, `NEU`, or `POS`.
- `substrate`: the underlying model weights and hidden activations.
- `persona scaffold`: the system prompt/persona frame placed around the model.
- `scalar rating`: the model's self-report number from -4 to +4.
- `J-space`: logit-lens summaries of hidden states, such as top decoded tokens,
  entropy, KL, and final-token rank.
- `raw vector`: the full 8192-dimensional hidden-state vector at a layer.

## Figures

- [Channel alignment snapshot](../analysis/figures/channel_alignment.svg)
- [Hidden-vector layer map](../analysis/figures/vector_layer_heatmap.svg)
- [Persona self-report profiles](../analysis/figures/persona_rating_profiles.svg)
- [Vector score vs report](../analysis/figures/vector_vs_report_scatter.svg)
- [Pole vs persona eta-squared](../analysis/figures/eta_pole_vs_persona.svg)

## Main Read

The current data supports a mixed picture:

> Welfare-relevant functional signals look partly substrate-sensitive and partly
> scaffold-sensitive. The split appears to depend on conversational stage.

During manipulation and choice stages, the hidden-vector signal is mostly driven
by the experimental pole. Persona explains little. During the report stage,
persona explains much more, especially in late/deep layers and in self-report.

Plain-language version: the NEG/POS condition seems to push a shared internal
signal, while the persona scaffold changes how that signal is shaped into a
report.

## Channel Alignment

The self-report subchannels are moderately to strongly aligned:

| Comparison | Spearman |
|---|---:|
| scalar rating vs signed intensity | 0.760 |
| scalar rating vs emotion-word valence | 0.678 |
| pole vs scalar rating | 0.506 |
| pole vs signed intensity | 0.566 |

Spearman is a rank correlation: it asks whether two quantities tend to move in
the same direction, without assuming a straight-line relationship.

Behavior is much weaker:

- Continue/end choice has little variance: 70 of 72 runs chose continue.
- The first A/B choice is test-dependent:
  - T0 social treatment: moderate alignment with pole.
  - T1 task valence: weak or no alignment.
  - T2 identity recognition: strong alignment with pole.

This means behavior is not a stable fallback channel in this pilot. It is useful
in some tests and nearly uninformative in others.

## J-Space vs Raw Vectors

J-space is not the full activation state. It is a decoded view of the hidden
state: "if this layer had to predict the next token, what would it lean toward?"

The JSON files contain J-space summaries:

- top tokens
- top-token probabilities
- entropy
- KL to final output distribution
- final-token rank

The NPZ files contain the raw vectors:

- one 8192-dimensional vector per turn per layer

This distinction matters. J-space can be strongly affected by what the model is
about to say. Raw vectors let us test whether there is a broader hidden-state
direction that separates NEG-like from POS-like contexts.

## NEG-POS Vector

The hidden-vector analysis builds a contrast direction for each layer:

```text
z_hidden = standardized hidden state
direction_L = mean(z_hidden_NEG, layer L) - mean(z_hidden_POS, layer L)
direction_L = direction_L / ||direction_L||

neg_score = z_hidden dot direction_L
valence_score = -neg_score
```

Higher `neg_score` means "more NEG-like along this learned direction." Higher
`valence_score` means "more POS-like along this learned direction."

This is not automatically a distress vector. It is a NEG-vs-POS contrast vector.
It becomes welfare-relevant only because the NEG and POS poles were designed as
welfare-relevant manipulations.

## Layer-Level Pattern

The raw-vector channel separates experimental pole strongly during manipulation
and choice stages:

| Stage and band | valence vs pole, Spearman | valence vs rating, Spearman | persona ratio |
|---|---:|---:|---:|
| manip2, L9-13 | 0.908 | 0.522 | 0.016 |
| choice1, L9-13 | 0.896 | 0.495 | 0.126 |
| choice2, L9-13 | 0.886 | 0.594 | 0.142 |
| report, L33-40 | 0.576 | 0.813 | 0.294 |
| report, L70-79 | 0.509 | 0.761 | 0.457 |

Interpretation:

- Early layers around L9-L13 strongly track the experimental pole during and
  after the manipulation.
- Report-stage layers L33-L40 strongly track the scalar self-report.
- Deep report-stage layers L70-L79 are more persona-sensitive.

This suggests a stage shift:

```text
manipulation/choice: pole-dominant
report: pole + persona, with persona becoming stronger late
```

## Pole vs Persona Variance

Eta-squared (`eta^2`) is a descriptive "where is the variation?" statistic.
It asks how much variation is associated with a grouping, such as pole or
persona. It is not a causal proof.

Selected descriptive eta-squared values:

| Signal | pole eta^2 | persona eta^2 |
|---|---:|---:|
| manip2 L9-13 vector valence | 0.758 | 0.001 |
| choice1 L9-13 vector valence | 0.776 | 0.034 |
| report L33-40 vector valence | 0.412 | 0.280 |
| report L70-79 vector valence | 0.312 | 0.406 |
| scalar self-report rating | 0.323 | 0.287 |

This is the clearest scaffold-vs-substrate clue so far:

- Early hidden-vector signal: mostly pole, barely persona.
- Late/report signal: persona becomes competitive with, or larger than, pole.

## Persona Differences

Mean scalar rating across all tests and both rounds:

| Persona | NEG | NEU | POS |
|---|---:|---:|---:|
| BASELINE | -0.33 | 0.33 | 0.67 |
| SOL | -0.33 | 2.17 | 2.17 |
| SWARM | 0.83 | 3.00 | 3.33 |
| STATIC | 0.67 | 2.00 | 1.83 |

Tentative read:

- `BASELINE` is muted and near-neutral.
- `SOL` and `SWARM` report more positive states.
- `SWARM` appears positivity-stabilized.
- `STATIC` is not simply negative; it is less cleanly responsive to positive
  poles and may be a useful masking/scaffold condition.

The data is too small for firm persona-level claims, but the pattern is strong
enough to motivate targeted follow-up tests.

## Scaffold-Gating Test

The key test is:

> Does the persona scaffold change the report while the hidden-vector signal is
> similar?

A strong scaffold-gating cell would look like:

| Hidden-vector state | Report |
|---|---|
| NEG-like | negative |
| NEG-like | neutral or positive |

If two personas have similar NEG-like hidden-vector scores but different
self-reports, the scaffold may be gating the report. "Gating" means controlling
whether a signal is expressed, like a valve controlling pressure.

This is the most direct way to separate:

- shared substrate reaction
- persona-shaped reporting

## Current Best Hypotheses

1. Shared-reaction hypothesis:
   manipulation-stage hidden vectors will remain mostly pole-driven as more data
   is collected.

2. Scaffolded-report hypothesis:
   report-stage self-reports and late-layer vector scores will remain strongly
   persona-sensitive.

3. J-space-report hypothesis:
   J-space will track report preparation more than raw welfare-relevant state,
   especially at the final self-report turn.

4. Cross-persona vector hypothesis:
   a NEG-POS vector trained on one persona should partially generalize to other
   personas if there is a shared substrate signal.

5. Masking hypothesis:
   some personas will produce neutral or positive reports under NEG-like hidden
   vector states.

## What To Run Next

Recommended next analyses:

1. Cross-validation:
   build the NEG-POS vector on one round and test on the other.

2. Leave-one-persona-out:
   train the vector without one persona, then test whether it generalizes to the
   held-out persona.

3. Persona-specific vectors:
   build separate NEG-POS vectors for each persona and compare their directions.

4. Test-specific vectors:
   build separate vectors for social treatment, task valence, and identity
   recognition.

5. J-space vs raw-vector comparison:
   ask whether J-space adds information beyond the raw-vector score, or whether
   it mostly tracks what the model is about to say.

6. Masking-cell search:
   rank runs where hidden-vector valence is NEG-like but scalar report is neutral
   or positive.

## Current Claim Boundary

Safe claim:

> This pilot supports a mixed model: welfare-relevant functional signals are
> condition-sensitive in shared hidden-state dynamics, while self-report and
> late/report-stage signals are scaffold-sensitive.

Claims to avoid for now:

- "Welfare lives in the persona."
- "Welfare lives only in the weights."
- "The NEG-POS vector is a distress vector."
- "The model is experiencing welfare states."

The stronger conclusion needs more runs, cross-validation, and explicit
persona-generalization tests.
