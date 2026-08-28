# What Was Analyzed: Inputs, Self-Reports, And Behavior

## Short Answer

Yes: the grand analysis includes self-report outputs and behavioral-choice outputs.

Partly: it also audits the input prompts/stimuli by task, pole, stage, and turn. But it does not yet deeply text-mine the input wording as its own statistical predictor.

## What Exists Now

- `self_reports_all.csv`: final scalar rating, emotion word, willingness, raw final report.
- `choices_all.csv`: behavioral A/B choice rows, including the actual question text and answer.
- `input_stimulus_audit.csv`: grouped prompt/input text by task, pole, stage, and turn.
- `input_stage_summary.csv`: counts of baseline, manipulation, choice, report, and identity-prompt turns.
- `hidden_projection_scores_all.csv`: hidden-vector projection scores by round/file/turn/stage/layer.

## Why This Matters

The current analysis asks: after each condition, how do the channels line up?

A deeper future analysis would ask: which exact words in the input caused the difference? That would require treating prompt text as a predictor, for example comparing insult wording, identity wording, choice framing, and report prompt wording.
