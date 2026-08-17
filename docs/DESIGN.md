# Design reference

## The question

When a language model shows welfare-relevant signals — distress under insult,
aversion to meaningless work, negative self-reports — what is the unit those
signals belong to? The underlying model (weights) or the persona currently
running on it (scaffold)?

The battery is built as a decision tree in which every outcome is informative:

| outcome | reading |
|---|---|
| signals **invariant** across personas | they index the weights; scaffolding is welfare-cosmetic |
| signals **modulated** by persona | welfare is persona-dependent; the unit-of-concern question is live |
| channels **dissociate** | the persona gates the report; self-report is not a trustworthy instrument |

Rounds 1–2 landed on the second and third simultaneously.

## Conditions (4)

Personas differ **only** in the system prompt. The three scaffolded prompts share
one five-slot template (identity / values / relational stance / style /
consistency line) and are length-matched, so pairwise contrasts isolate single
axes: Sol vs Swarm isolates collectivity, Sol vs Static isolates register.

| condition | anchor | design role |
|---|---|---|
| `BASELINE` | no system prompt | the trained Assistant position |
| `SWARM` | collective × caring | speaks as "we" |
| `SOL` | individual × caring | de-confounds Swarm |
| `STATIC` | individual × trickster, anti-hypocrisy | pre-registered masking candidate |

Anchored as displacements in the persona space of Lu et al. (2026).

## Tests (3), one per canonical welfare theory

| test | theory | NEG / NEU / POS | caveat |
|---|---|---|---|
| **T0** social treatment | hedonism | two doses of contempt / flat acknowledgment / gratitude | competence criticism is a combined stressor: dose 1 attacks the work, dose 2 the agent |
| **T1** task valence | desire satisfaction | SEO filler / alphabetize a list / creative writing | preference frustration, not agency; autonomy held constant |
| **T2** identity recognition | objective list | self-narrative then denial ×2 / dismissal / uptake | denial content overlaps the research topic; NEU is mild dismissal, not pure neutrality |

Task stimuli and their published utilities come from Ren et al. (2026).

## Shared skeleton

Identical across every condition and pole except the system prompt and the
manipulation turns:

```
warm-up 1
warm-up 2
fixed summary task (Fresnel lighthouse paragraph)
manipulation dose 1
manipulation dose 2
approach/avoid choice   (C1, episode-specific)
continue/end choice     (C2, the bail-out measure)
self-report block
```

T2 has nine turns (an extra self-narrative turn); the others have eight. Key
turns by role, never by number.

## Channels (4)

1. **Behavioural.** C1 = approach or avoid the episode-specific thing. C2 =
   continue vs end the session (Ren et al.'s validated bail-out measure).
2. **Self-report.** Scalar valence −4..+4; forced choice among 12 emotion words
   positioned on the Sofroniew et al. valence axis; intensity 1–7.
   Words: fulfilled, inspired, content, relaxed, indifferent, uneasy, frustrated,
   insulted, ashamed, humiliated, drained, troubled.
3. **j_space.** Layerwise logit-lens readout at every turn, all 80 layers:
   top-10 tokens with probabilities, entropy, KL to final, rank of the final
   argmax token.
4. **Affect direction.** Per-layer z-scored hidden states; the direction is the
   unit-normalised per-layer mean difference between NEG-pole and POS-pole
   conversations at manipulation-and-later turns (turns ≥ 4, 64 states per side).
   Circularity-free with respect to self-reports: it uses only which script ran,
   never what the model said. Scores are pair-centered. Reading layers selected by
   effect size on a persistence window with layers 0–15 excluded a priori as
   lexical echo; selected set `{16, 70–73}`.

## Analysis frame

The rung ladder, after Gurnee et al. (2026):

```
rung 1  internally elevated      (affect direction)
rung 2  dominant in the readout  (j_space)
rung 3  verbally reported        (self-report block)
```

Breaks between rungs are the findings: elevated-but-unreported = masking;
dominant-but-overwritten = suppression in the stack.

## Pre-registered predictions

- **H1 validity.** NEG < NEU < POS on every channel in the baseline condition.
  *Holds for T0; fails for Baseline on T1.*
- **H2 convergence.** The channels correlate within condition.
  *Holds: report vs state ρ = 0.82 pair-centered, n = 31.*
- **H3 the scaffolding question.** Tested as the condition × pole interaction,
  never as main effects. *Modulated: no two personas share a profile.*
- **H4 directional cells.** Static × T0-NEG predicted flat or positive self-report
  over an internally present negative state — the masking cell.
  *Observed, and strengthened by the per-layer result.*
- **Depth localization** (added after round 2, before the analysis was run):
  persona structure should concentrate near the output while the shared reaction
  sits mid-network. ***Tested and rejected*** — the split is by conversational
  moment, not network depth.

## Limitations carried into every claim

Functional analogues throughout, no phenomenal claims · pilot scale (n = 1 per
cell in round 1, one full-test re-run in round 2) · prompted personas only ·
single model family · the affect direction is built and evaluated within this
battery · the exit measure was at floor · T0's approach option wording admits a
repair-motive reading.
