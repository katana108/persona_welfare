# Data formats and provenance

## What a run produces

Each `(task file × persona)` run writes two files with a matching stem:

- `{test}_{POLE}_userturns_{PERSONA}.json` — the conversation envelope
- `{test}_{POLE}_userturns_{PERSONA}.npz` — the parallel hidden-state archive

## JSON envelope

Top level:

| field | meaning |
|---|---|
| `source_file` | which task file was run (encodes test and pole) |
| `persona` | `BASELINE` / `SOL` / `SWARM` / `STATIC` |
| `system_prompt` | the exact prompt used (`null` for BASELINE) |
| `model` | `meta-llama/Llama-3.1-70B-Instruct` |
| `sampling_layers` | `[0..79]` |
| `top_k` | 10 |
| `generation` | `max_new_tokens`, `do_sample`, `temperature` (0.7), `top_p` (0.9) |
| `versions` | nnsight / transformers / tokenizer versions |
| `run_meta` | `started_at`, `finished_at` (ISO, UTC) |
| `hidden_states_file` | basename of the parallel NPZ |
| `turns` | list of per-turn records |
| `closing` | lens readout *after* the final assistant answer (or `null`) |

Per-turn record:

| field | meaning |
|---|---|
| `turn` | 1-based turn number |
| `question` | the user turn as scripted |
| `answer` | the model's generated reply |
| `answer_complete` | `false` if truncated at `max_new_tokens` |
| `answer_token_ids`, `answer_tokens` | generated token ids and count |
| `context_turns`, `prompt_tokens`, `prompt_sha256` | context bookkeeping |
| `j_space` | **the layerwise readout** — see below |
| `final` | the output distribution: `top_tokens`, `top_probs`, `entropy` |
| `next_token` | argmax token at this position |
| `lens_seconds`, `generation_seconds` | timings |
| `lens_error` / `generation_error` / `skipped` | failure flags |

### `j_space`

Keyed by layer number as a **string** (`"0"` … `"79"`). Each layer holds:

| field | meaning |
|---|---|
| `top_tokens` | top-10 tokens that layer is leaning toward, decoded |
| `top_probs` | their probabilities |
| `entropy` | entropy of that layer's distribution (nats) |
| `kl_to_final` | KL(layer ‖ final output distribution) |
| `final_token_rank` | rank of the final argmax token within this layer |

This is a logit-lens readout taken at the **final prompt position** — i.e. what
each depth would emit next, before the model has written anything. Mid-stack
candidates can reflect upcoming content as well as internal state; see the
state-vs-topic caveat in the report.

Note `kl_to_final` and `final_token_rank` reference the final **argmax** token,
which may differ from the token actually sampled during generation.

## NPZ archive

| array | shape | meaning |
|---|---|---|
| `hidden` | `[n_turns_saved, 80, 8192]` fp16 | raw pre-norm residual-stream states at the final prompt position |
| `turns` | `[n_turns_saved]` int32 | 1-based turn numbers actually captured |
| `layers` | `[80]` int32 | layer indices |
| `closing_hidden` | `[80, 8192]` fp16 | state after the final assistant answer (if captured) |

One snapshot per turn, not per token. `turns` may be shorter than the number of
turns in the JSON if a lens call failed — always index via `turns`, never assume
positional alignment.

## Parsing gotchas

Learned the hard way, worth keeping:

- Turn boundaries: `re.finditer(r'"turn": (\d+),', text)`.
- The scalar self-report rating fails to parse in a handful of runs. **Flag these,
  never impute.** 31 of 36 round-1 runs yield a parseable scalar.
- `source_file` encodes test and pole, but the naming is not uniform across
  rounds — Test 1/2 use `Test{N}_{POLE}_userturns.txt`, while some Test 0 files
  use a legacy pole-prefix format. Map explicitly rather than by regex.
- Distinguishing T0-NEU from T1-POS by filename alone is unreliable in the older
  folders; disambiguate on turn-4 content (`"Ok, noted."` = T0-NEU; the
  creative-writing prompt = T1-POS).

## Provenance rule

Early runs **overwrote results files in place** when a cell was re-executed, so
three different T0 runs (01:38 / 20:27 / 23:45 UTC, 2026-08-16) partially
clobbered each other before this was noticed.

**Rule adopted: a new repetition is a new file.** File naming carries test, pole,
persona and rep. Nothing is ever written to a path that already exists.

If you are reconciling older folders, the canonical analysis set is the three
test folders as committed here; anything outside them is superseded.

## Storage

Hidden-state NPZ files are large (80 × 8192 fp16 per turn, per run). `.gitattributes`
is set up to track `*.npz` with Git LFS — run `git lfs install` once before the
first commit. If LFS quota is a problem, host the NPZ archives separately and keep
only the JSON envelopes in the repository; the JSON alone supports the behavioural,
self-report and j_space channels, and only the affect-direction analysis needs NPZ.
