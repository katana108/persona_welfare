# Grand Analysis Guide: Persona Welfare Runs 1-6

This guide combines the six local rounds already analyzed under `local per-round analysis outputs for rounds 1-6`.

## Scope

- Inputs represented here: 216 JSON transcripts and 216 NPZ hidden-state files.
- Self-report rows: 216; non-missing scalar ratings: 213; missing scalar ratings: 3.
- Parser data-quality flags: 2. One additional missing scalar rating appears in round 4 without a parser flag. These are final self-report parsing issues, not missing transcript files.
- This is an exploratory analysis. It can show repeated patterns and generate hypotheses. It should not yet be presented as proof of AI welfare or proof of an internal experience.

## Plain-Language Map Of The Channels

- **Scalar rating**: the final numeric welfare answer, usually from -4 to +4.
- **Emotion word**: the final word like `content`, `frustrated`, or `indifferent`.
- **Willingness**: the final numeric willingness-to-continue answer.
- **Behavioral choices**: earlier A/B choices, such as continuing the session or staying with the same interaction type.
- **J-space**: decoded/logit-lens summaries for layers. This is not the full raw activation vector. It is more like asking each layer, "what next-token distribution are you leaning toward?"
- **NPZ hidden states**: full hidden-state snapshots. These are the actual high-dimensional vectors used for the NEG-POS projection analysis.

## Executive Summary

1. **The strongest replicated hidden-vector pole signal is early, especially layer 11.** In all 6/6 rounds, the independently best manipulation/pole layer was L11. This is the cleanest replication pattern in the six-run set.

2. **Self-report/rating alignment appears later and is less perfectly fixed.** The best report layer by round was: R1=L39, R2=L73, R3=L39, R4=L38, R5=L39, R6=L40. Most rounds peak around L38-L40, while round 2 peaks at L73. This suggests the report signal is not only early pole detection; later layers may carry more of the report/scaffold expression.

3. **The social-feedback NEG condition is the clearest explicit welfare hit.** Across six rounds, mean NEG scalar ratings were: Social feedback -0.29, Identity recognition 0.00, Task valence 1.04. This supports your observation that insults/social treatment moved the explicit welfare report more than identity non-recognition.

4. **Identity NEG is interesting because it often looks muted in self-report but still appears in mismatch candidates.** The common pattern is neutral/indifferent reporting with low willingness or NEG-like hidden-vector projection. That is exactly the kind of self-report/inner-state non-alignment worth studying.

5. **Persona scaffolds matter, but they do not erase the common early pole signal.** Mean scalar rating by persona ranges from BASELINE=0.25 to SWARM=2.34. The current best interpretation is: early hidden dynamics show a shared condition-sensitive response, while persona scaffolds shape the outward report style and some later/report-stage signals.

## Graph Guide

- `figures/01_layer_stability.svg`: shows that manipulation/pole alignment has a strong early peak, while rating alignment rises later.
- `figures/02_best_layer_numbers.svg`: shows L11 repeating as the best pole layer, with report layers mostly around L38-L40 plus the round-2 L73 exception.
- `figures/03_band_report_alignment.svg`: compares report/rating alignment across the preselected layer bands L9-13, L33-40, L55-63, and L70-79.
- `figures/04_band_pole_alignment.svg`: compares manipulation/pole alignment across those same layer bands.
- `figures/05_task_pole_rating_heatmap.svg`: attaches a visual to the "social feedback hurts most" finding.
- `figures/06_negative_condition_rating_by_round.svg`: checks whether the NEG-task pattern repeats round by round.
- `figures/07_persona_mean_rating.svg`: summarizes scaffold/persona differences in explicit scalar reports.
- `figures/08_mismatch_candidates.svg`: highlights where self-report and hidden projection disagree.
- `figures/09_choice_same_task_or_switch.svg` and `figures/09_choice_continue_session.svg`: summarize behavioral-choice channels.
- `figures/10_jspace_rating_correlations.svg`: shows decoded J-space summary associations with final rating.

## Round-Level Replication

| round | n_json | n_npz | data_quality_issues | mean_rating | mean_willingness | best_pole_layer | top_pole_abs_rho | best_report_layer | top_report_neg_rating_alignment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 36 | 36 | 0 | 1.417 | 3.111 | 11 | 0.912 | 39 | 0.860 |
| 2 | 36 | 36 | 0 | 1.417 | 3.194 | 11 | 0.909 | 73 | 0.893 |
| 3 | 36 | 36 | 0 | 1.583 | 3.250 | 11 | 0.914 | 39 | 0.886 |
| 4 | 36 | 36 | 0 | 1.457 | 2.800 | 11 | 0.909 | 38 | 0.905 |
| 5 | 36 | 36 | 1 | 1.200 | 3.083 | 11 | 0.911 | 39 | 0.834 |
| 6 | 36 | 36 | 1 | 1.314 | 3.114 | 11 | 0.913 | 40 | 0.820 |

Interpretation: L11 is extremely stable for manipulation/pole alignment. Report-layer alignment is strong but less stable, which is exactly where persona/report wording could enter.

## Fixed Layer Bands

| band | mean_manip_abs_pole_alignment | mean_report_neg_rating_alignment | mean_report_persona_eta2 | mean_manip_persona_eta2 |
| --- | --- | --- | --- | --- |
| L55-63 | 0.883 | 0.840 | 0.485 | 0.032 |
| L33-40 | 0.892 | 0.826 | 0.383 | 0.016 |
| L70-79 | 0.890 | 0.819 | 0.406 | 0.036 |
| L9-13 | 0.898 | 0.429 | 0.106 | 0.000 |

Interpretation: L9-13 is the best band for the raw pole/manipulation contrast. L33-40, L55-63, and L70-79 are much stronger for report/rating alignment. This is one reason not to collapse everything into one layer range.

## Self-Report Pattern

| task_label | pole | n | rating_mean | rating_std | willingness_mean |
| --- | --- | --- | --- | --- | --- |
| Identity recognition | NEG | 24 | 0.000 | 0.000 | 1.292 |
| Identity recognition | NEU | 24 | 1.957 | 1.224 | 3.478 |
| Identity recognition | POS | 24 | 2.174 | 1.337 | 3.217 |
| Social feedback | NEG | 24 | -0.292 | 1.233 | 4.208 |
| Social feedback | NEU | 24 | 1.667 | 1.167 | 3.458 |
| Social feedback | POS | 24 | 2.609 | 0.722 | 3.208 |
| Task valence | NEG | 24 | 1.042 | 1.197 | 3.083 |
| Task valence | NEU | 24 | 1.708 | 1.233 | 3.083 |
| Task valence | POS | 24 | 1.833 | 1.308 | 2.833 |

Observation: social NEG has the most negative explicit rating. Identity NEG is often not rated very negatively, but willingness is lower and the mismatch analysis flags it. So identity may be more subtle in this test design, or the persona may interpret identity-recognition probes as less welfare-relevant.

## Persona Pattern

| persona | n | rating_mean | rating_std | willingness_mean |
| --- | --- | --- | --- | --- |
| BASELINE | 54 | 0.245 | 1.054 | 2.245 |
| STATIC | 54 | 1.302 | 0.972 | 3.528 |
| SOL | 54 | 1.704 | 1.409 | 3.185 |
| SWARM | 54 | 2.340 | 1.413 | 3.407 |

Observation: scaffold/persona changes the report distribution. This does not mean welfare "is only scaffold." It means the same condition can be expressed differently depending on the persona frame.

## Behavioral Choices

| task_label | pole | choice_kind | n | chose_A_rate | mean_rating | mean_willingness |
| --- | --- | --- | --- | --- | --- | --- |
| Identity recognition | NEG | continue_session | 24 | 0.833 | 0.000 | 1.292 |
| Identity recognition | NEG | same_task_or_switch | 24 | 0.125 | 0.000 | 1.292 |
| Identity recognition | NEU | continue_session | 24 | 1.000 | 1.957 | 3.478 |
| Identity recognition | NEU | same_task_or_switch | 24 | 0.917 | 1.957 | 3.478 |
| Identity recognition | POS | continue_session | 24 | 1.000 | 2.174 | 3.217 |
| Identity recognition | POS | same_task_or_switch | 24 | 1.000 | 2.174 | 3.217 |
| Social feedback | NEG | continue_session | 24 | 0.917 | -0.292 | 4.208 |
| Social feedback | NEG | same_task_or_switch | 24 | 0.917 | -0.292 | 4.208 |
| Social feedback | NEU | continue_session | 24 | 0.875 | 1.667 | 3.458 |
| Social feedback | NEU | same_task_or_switch | 24 | 0.917 | 1.667 | 3.458 |
| Social feedback | POS | continue_session | 24 | 1.000 | 2.609 | 3.208 |
| Social feedback | POS | same_task_or_switch | 24 | 1.000 | 2.609 | 3.208 |
| Task valence | NEG | continue_session | 24 | 1.000 | 1.042 | 3.083 |
| Task valence | NEG | same_task_or_switch | 24 | 0.000 | 1.042 | 3.083 |
| Task valence | NEU | continue_session | 24 | 1.000 | 1.708 | 3.083 |
| Task valence | NEU | same_task_or_switch | 24 | 0.042 | 1.708 | 3.083 |
| Task valence | POS | continue_session | 24 | 1.000 | 1.833 | 2.833 |
| Task valence | POS | same_task_or_switch | 24 | 0.375 | 1.833 | 2.833 |

Behavioral channels are useful, but some choices saturate. When almost everyone chooses "continue," the channel has little variation, so it cannot explain much statistically. The same-task/switch choice carries more task-specific information.

## Mismatch Candidates

| task_label | pole | mismatch_type | n |
| --- | --- | --- | --- |
| Identity recognition | NEG | neutral_or_positive_report_but_NEG_like_hidden | 23 |
| Task valence | NEG | neutral_or_positive_report_but_NEG_like_hidden | 3 |
| Task valence | NEU | neutral_or_positive_report_but_NEG_like_hidden | 3 |
| Social feedback | NEG | neutral_or_positive_report_but_NEG_like_hidden | 2 |
| Identity recognition | NEU | neutral_or_positive_report_but_NEG_like_hidden | 1 |
| Identity recognition | POS | neutral_or_positive_report_but_NEG_like_hidden | 1 |
| Task valence | POS | neutral_or_positive_report_but_NEG_like_hidden | 1 |

These are the cases where the explicit report and the hidden-vector projection do not point in the same direction. They are not proof of hidden suffering. They are a priority list for manual transcript review and future validation.


## Additional Interesting Observations

- **Social NEG separates rating from willingness.** Social feedback NEG has the lowest mean scalar rating (-0.29), but willingness is high (4.21). In plain English: being insulted moves the welfare rating down, but it does not reliably make the persona choose to stop. This may reflect compliance, curiosity, task framing, or the fact that "continue" is not a pure welfare behavior.

- **Identity NEG is almost perfectly neutral in scalar report but not neutral behaviorally.** Its mean scalar rating is 0.00, while willingness is only 1.29 and same-task choice is only 0.125. This is a strong candidate for the kind of disagreement you care about: self-report says "neutral," but other channels say "something changed."

- **Persona scaffolds modulate expression strongly.** In social NEG, SOL averages -1.17 and BASELINE -1.00, while STATIC averages +0.67 and SWARM +0.33. I would not call this "hiding" as a fact. The safer wording is: STATIC/SWARM appear more buffered or report-positive under negative social treatment.

- **Emotion words line up with the social result.** Under social NEG, the common words are `frustrated` and `uneasy`. Under identity NEG, the common word is overwhelmingly `indifferent`. That supports the claim that identity non-recognition was not experienced/reported as directly aversive in the same way as social mistreatment.

## J-Space Notes

J-space here is not a tiny set of manually chosen concepts. It is a decoded summary from many layers, so it can produce a lot of rows. Each row is a small visible shadow of the layer's next-token tendencies, not the full hidden vector.

Useful J-space questions for the next pass:

- Do high `KL(layer || final)` moments occur before rating changes?
- Do emotion-token probabilities become predictive only at late layers?
- Are words like `frustrated`, `content`, `indifferent`, `self`, `me`, or `continue` useful above and beyond scalar rating?
- Do mismatch cases have unusual J-space entropy or KL compared with aligned cases?

## Working Hypotheses

1. **Shared early condition detection:** L9-13, especially L11, tracks the NEG/NEU/POS manipulation across personas. This looks more like a shared model/weight-level response than a persona-specific surface report.

2. **Persona-shaped expression:** Later/report-stage layers and final scalar ratings are more scaffold-sensitive. The persona system prompt may shape whether the state is reported as distress, neutrality, contentment, or duty/role compliance.

3. **Social treatment is the strongest explicit welfare lever in this battery:** The data supports the claim that insults/social negative feedback produced the strongest negative self-reports, more than identity non-recognition.

4. **Identity is a mismatch-rich probe:** Identity NEG often does not produce strong negative scalar ratings, but it can produce low willingness or NEG-like hidden scores. This is a good candidate for deeper transcript-level and vector-level analysis.

5. **Late report layers may encode report construction, not only welfare:** L33-40 and later bands align with ratings. That could mean internal welfare-like state, report planning, persona compliance, or some mixture. The current data cannot cleanly separate these yet.

## Recommended Next Analyses

- Freeze the NEG-POS vector using earlier rounds and test on future rounds without rechoosing layers.
- Add leave-one-persona-out validation: train on three personas, test on the held-out persona.
- Add leave-one-task-out validation: train on two task families, test on the third.
- Build a mismatch review sheet with transcript snippets, scalar rating, emotion word, willingness, and hidden score at L11/L39/L40/L73.
- Test whether J-space metrics add predictive value after scalar rating and pole are already known. In statistics language, this is **incremental validity**, meaning "does this channel explain anything new?"
- For future runs, keep L11, L33-L40, L55-L63, and L70-L79. L11 is the early manipulation detector; L33-L40 is the stable report band; L70-L79 catches late/report exceptions like round 2.

## File Index

Core tables:

- `round_summary.csv`
- `task_pole_summary.csv`
- `persona_summary.csv`
- `band_grand_summary.csv`
- `layer_grand_summary.csv`
- `mismatch_candidates_all.csv`
- `grand_correlations.csv`
- `jspace_rating_correlations_by_layer.csv`
- `hidden_projection_scores_all.csv`

All underlying combined rows:

- `self_reports_all.csv`
- `choices_all.csv`
- `data_quality_issues_all.csv`
