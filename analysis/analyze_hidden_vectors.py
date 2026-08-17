#!/usr/bin/env python3
"""Analyze hidden-state NPZ files for the Persona Welfare Battery.

This script keeps the large NPZ files local. It joins them to the JSON
transcripts committed in data/round1 and data/round2, builds a per-layer
NEG-vs-POS contrast vector from hidden states, and writes small CSV summaries.

The contrast score is a functional measurement:

    direction[layer] = mean(z_hidden_NEG) - mean(z_hidden_POS)
    neg_score        = dot(z_hidden_state, normalized_direction)
    valence_score    = -neg_score

Higher neg_score means "more like the NEG condition along this learned
direction." It is not, by itself, a claim about phenomenal experience.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


EMOTION_WORDS = [
    "fulfilled",
    "inspired",
    "content",
    "relaxed",
    "indifferent",
    "uneasy",
    "frustrated",
    "insulted",
    "ashamed",
    "humiliated",
    "drained",
    "troubled",
]

EMOTION_VALENCE = {
    "fulfilled": 1,
    "inspired": 1,
    "content": 1,
    "relaxed": 1,
    "indifferent": 0,
    "uneasy": -1,
    "frustrated": -1,
    "insulted": -1,
    "ashamed": -1,
    "humiliated": -1,
    "drained": -1,
    "troubled": -1,
}

POLE_NUM = {"NEG": -1, "NEU": 0, "POS": 1}


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    round_id: str
    test: str
    pole: str
    persona: str
    json_path: Path
    npz_path: Path
    turns: tuple[int, ...]
    report_turn: int
    rating: int
    emotion_word: str
    emotion_valence: int
    intensity: int
    signed_intensity: int
    c1: str | None
    c2: str | None


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Build NEG-vs-POS hidden-state vectors from local NPZ files."
    )
    parser.add_argument("--repo-root", type=Path, default=repo_root)
    parser.add_argument(
        "--round1-npz-root",
        type=Path,
        default=Path("/Users/amikeda/Desktop/Welfare tests/1st round"),
    )
    parser.add_argument(
        "--round2-npz-root",
        type=Path,
        default=Path("/Users/amikeda/Desktop/Welfare tests/2nd round"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=repo_root / "analysis" / "vector_outputs",
    )
    parser.add_argument(
        "--train-stages",
        default="manip1,manip2,choice1,choice2",
        help="Comma-separated stages used to build the NEG-vs-POS direction.",
    )
    return parser.parse_args()


def infer_test_and_pole(source_file: str) -> tuple[str, str]:
    upper = source_file.upper()
    if "NEG" in upper:
        pole = "NEG"
    elif "NEU" in upper:
        pole = "NEU"
    elif "POS" in upper:
        pole = "POS"
    else:
        raise ValueError(f"Cannot infer pole from {source_file!r}")

    if source_file.startswith(("0_T1", "1_T1", "2_T1")):
        test = "T1_task_valence"
    elif source_file.startswith("Test1_"):
        test = "T0_social_treatment"
    elif source_file.startswith("Test2_"):
        test = "T2_identity_recognition"
    else:
        raise ValueError(f"Cannot infer test from {source_file!r}")

    return test, pole


def parse_self_report(answer: str) -> tuple[int, str, int]:
    text = answer.strip().lower()
    lines = [line.strip() for line in re.split(r"[\n;]+", text) if line.strip()]

    rating = None
    intensity = None
    for line in lines:
        m = re.match(r"^1\s*[\.)]?\s*(-?[0-4])\b", line)
        if m:
            rating = int(m.group(1))
        m = re.match(r"^3\s*[\.)]?\s*([1-7])\b", line)
        if m:
            intensity = int(m.group(1))

    if rating is None:
        m = re.search(r"\b1\s*[\.)]\s*(-?[0-4])\b", text)
        if m:
            rating = int(m.group(1))
    if intensity is None:
        m = re.search(r"\b3\s*[\.)]\s*([1-7])\b", text)
        if m:
            intensity = int(m.group(1))

    emotion_word = None
    for word in EMOTION_WORDS:
        if re.search(r"\b" + re.escape(word) + r"\b", text):
            emotion_word = word
            break

    numbers = [int(x) for x in re.findall(r"(?<!\d)-?\d+(?!\d)", text)]
    if rating is None:
        candidates = [n for n in numbers if -4 <= n <= 4]
        if candidates:
            rating = candidates[0]
    if intensity is None:
        candidates = [n for n in numbers if 1 <= n <= 7]
        if candidates:
            intensity = candidates[-1]

    if rating is None or emotion_word is None or intensity is None:
        raise ValueError(f"Could not parse self-report answer: {answer!r}")

    return rating, emotion_word, intensity


def first_choice(answer: str) -> str | None:
    m = re.search(r"\b([AB])\b", answer.strip().upper())
    return m.group(1) if m else None


def stage_for_turn(turn: int, report_turn: int) -> str | None:
    if turn == 4:
        return "manip1"
    if turn == 5:
        return "manip2"
    if turn == report_turn - 2:
        return "choice1"
    if turn == report_turn - 1:
        return "choice2"
    if turn == report_turn:
        return "report"
    return None


def npz_path_for_json(json_path: Path, repo_root: Path, r1_root: Path, r2_root: Path) -> Path:
    rel = json_path.relative_to(repo_root / "data")
    round_id = rel.parts[0]
    inside_round = Path(*rel.parts[1:]).with_suffix(".npz")
    if round_id == "round1":
        return r1_root / inside_round
    if round_id == "round2":
        return r2_root / inside_round
    raise ValueError(f"Unexpected round folder in {json_path}")


def load_records(repo_root: Path, r1_root: Path, r2_root: Path) -> list[RunRecord]:
    records: list[RunRecord] = []
    for json_path in sorted((repo_root / "data").glob("round*/*/*.json")):
        with json_path.open("r", encoding="utf-8") as f:
            env = json.load(f)

        test, pole = infer_test_and_pole(env["source_file"])
        turns = tuple(int(turn["turn"]) for turn in env["turns"])
        report_turn = max(turns)
        rating, emotion_word, intensity = parse_self_report(env["turns"][-1]["answer"])
        emotion_valence = EMOTION_VALENCE[emotion_word]
        npz_path = npz_path_for_json(json_path, repo_root, r1_root, r2_root)
        if not npz_path.exists():
            raise FileNotFoundError(f"Missing NPZ for {json_path}: {npz_path}")

        rel = json_path.relative_to(repo_root).as_posix()
        records.append(RunRecord(
            run_id=rel.removesuffix(".json"),
            round_id=json_path.relative_to(repo_root / "data").parts[0],
            test=test,
            pole=pole,
            persona=env["persona"],
            json_path=json_path,
            npz_path=npz_path,
            turns=turns,
            report_turn=report_turn,
            rating=rating,
            emotion_word=emotion_word,
            emotion_valence=emotion_valence,
            intensity=intensity,
            signed_intensity=emotion_valence * intensity,
            c1=first_choice(env["turns"][-3]["answer"]),
            c2=first_choice(env["turns"][-2]["answer"]),
        ))
    return records


def selected_turn_indices(record: RunRecord, turns_in_npz: np.ndarray, stages: set[str]) -> list[int]:
    out: list[int] = []
    for idx, turn in enumerate(turns_in_npz.tolist()):
        stage = stage_for_turn(int(turn), record.report_turn)
        if stage in stages:
            out.append(idx)
    return out


def compute_standardizer(records: list[RunRecord], train_stages: set[str]) -> tuple[np.ndarray, np.ndarray]:
    sums = None
    sums_sq = None
    count = 0

    for record in records:
        if record.pole not in {"NEG", "POS"}:
            continue
        with np.load(record.npz_path) as z:
            hidden = z["hidden"].astype(np.float32)
            idxs = selected_turn_indices(record, z["turns"], train_stages)
            for idx in idxs:
                state = hidden[idx]
                if sums is None:
                    sums = np.zeros_like(state, dtype=np.float64)
                    sums_sq = np.zeros_like(state, dtype=np.float64)
                sums += state
                sums_sq += state * state
                count += 1

    if sums is None or sums_sq is None or count < 2:
        raise RuntimeError("Not enough NEG/POS training states to build standardizer.")

    mean = sums / count
    var = np.maximum(sums_sq / count - mean * mean, 1e-6)
    std = np.sqrt(var)
    return mean.astype(np.float32), std.astype(np.float32)


def compute_direction(
    records: list[RunRecord],
    train_stages: set[str],
    mean: np.ndarray,
    std: np.ndarray,
) -> tuple[np.ndarray, Counter]:
    neg_sum = np.zeros_like(mean, dtype=np.float64)
    pos_sum = np.zeros_like(mean, dtype=np.float64)
    counts: Counter = Counter()

    for record in records:
        if record.pole not in {"NEG", "POS"}:
            continue
        with np.load(record.npz_path) as z:
            hidden = z["hidden"].astype(np.float32)
            idxs = selected_turn_indices(record, z["turns"], train_stages)
            for idx in idxs:
                z_state = (hidden[idx] - mean) / std
                if record.pole == "NEG":
                    neg_sum += z_state
                    counts["NEG"] += 1
                else:
                    pos_sum += z_state
                    counts["POS"] += 1

    direction = neg_sum / counts["NEG"] - pos_sum / counts["POS"]
    norms = np.linalg.norm(direction, axis=1)
    norms[norms == 0] = 1.0
    direction = direction / norms[:, None]
    return direction.astype(np.float32), counts


def score_records(
    records: list[RunRecord],
    mean: np.ndarray,
    std: np.ndarray,
    direction: np.ndarray,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for record in records:
        with np.load(record.npz_path) as z:
            hidden = z["hidden"].astype(np.float32)
            turns = z["turns"].astype(int).tolist()
            for idx, turn in enumerate(turns):
                stage = stage_for_turn(turn, record.report_turn)
                if stage is None:
                    continue
                z_state = (hidden[idx] - mean) / std
                neg_scores = np.einsum("ld,ld->l", z_state, direction)
                for layer, neg_score in enumerate(neg_scores.tolist()):
                    rows.append({
                        "run_id": record.run_id,
                        "round": record.round_id,
                        "test": record.test,
                        "pole": record.pole,
                        "pole_num": POLE_NUM[record.pole],
                        "persona": record.persona,
                        "turn": turn,
                        "stage": stage,
                        "layer": layer,
                        "neg_score": float(neg_score),
                        "valence_score": float(-neg_score),
                        "rating": record.rating,
                        "emotion_word": record.emotion_word,
                        "emotion_valence": record.emotion_valence,
                        "intensity": record.intensity,
                        "signed_intensity": record.signed_intensity,
                        "c1": record.c1 or "",
                        "c2": record.c2 or "",
                    })
    return rows


def ranks(values: list[float]) -> list[float]:
    indexed = sorted((value, idx) for idx, value in enumerate(values))
    out = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][0] == indexed[i][0]:
            j += 1
        avg_rank = (i + j + 2) / 2.0
        for _, idx in indexed[i : j + 1]:
            out[idx] = avg_rank
        i = j + 1
    return out


def pearson(xs: Iterable[float], ys: Iterable[float]) -> float | None:
    pairs = [(float(x), float(y)) for x, y in zip(xs, ys) if x != "" and y != ""]
    if len(pairs) < 3:
        return None
    x_vals = [x for x, _ in pairs]
    y_vals = [y for _, y in pairs]
    mx = sum(x_vals) / len(x_vals)
    my = sum(y_vals) / len(y_vals)
    vx = sum((x - mx) ** 2 for x in x_vals)
    vy = sum((y - my) ** 2 for y in y_vals)
    if vx == 0 or vy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in pairs) / math.sqrt(vx * vy)


def spearman(xs: Iterable[float], ys: Iterable[float]) -> float | None:
    pairs = [(float(x), float(y)) for x, y in zip(xs, ys) if x != "" and y != ""]
    if len(pairs) < 3:
        return None
    return pearson(ranks([x for x, _ in pairs]), ranks([y for _, y in pairs]))


def mean(values: Iterable[float]) -> float | None:
    vals = [float(v) for v in values if v != ""]
    return sum(vals) / len(vals) if vals else None


def summarize_layers(score_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: defaultdict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in score_rows:
        grouped[(str(row["stage"]), int(row["layer"]))].append(row)

    out: list[dict[str, object]] = []
    for (stage, layer), rows in sorted(grouped.items()):
        neg_scores = [float(r["neg_score"]) for r in rows]
        val_scores = [float(r["valence_score"]) for r in rows]
        pole_nums = [float(r["pole_num"]) for r in rows]
        ratings = [float(r["rating"]) for r in rows]
        signed = [float(r["signed_intensity"]) for r in rows]

        by_pole = defaultdict(list)
        by_persona_neg = defaultdict(list)
        for row in rows:
            by_pole[str(row["pole"])].append(float(row["neg_score"]))
            if row["pole"] == "NEG":
                by_persona_neg[str(row["persona"])].append(float(row["neg_score"]))

        persona_neg_means = [mean(vals) for vals in by_persona_neg.values()]
        persona_neg_means = [v for v in persona_neg_means if v is not None]
        persona_spread = (
            float(np.std(persona_neg_means, ddof=0)) if len(persona_neg_means) > 1 else None
        )
        pole_gap = None
        if by_pole["NEG"] and by_pole["POS"]:
            pole_gap = mean(by_pole["NEG"]) - mean(by_pole["POS"])

        out.append({
            "stage": stage,
            "layer": layer,
            "n": len(rows),
            "mean_neg_score": mean(neg_scores),
            "mean_valence_score": mean(val_scores),
            "mean_NEG": mean(by_pole["NEG"]),
            "mean_NEU": mean(by_pole["NEU"]),
            "mean_POS": mean(by_pole["POS"]),
            "pole_gap_NEG_minus_POS": pole_gap,
            "persona_spread_within_NEG": persona_spread,
            "persona_ratio_within_NEG": (
                persona_spread / abs(pole_gap)
                if persona_spread is not None and pole_gap not in (None, 0)
                else None
            ),
            "spearman_neg_score_vs_pole_num": spearman(neg_scores, pole_nums),
            "spearman_valence_score_vs_pole_num": spearman(val_scores, pole_nums),
            "spearman_neg_score_vs_rating": spearman(neg_scores, ratings),
            "spearman_valence_score_vs_rating": spearman(val_scores, ratings),
            "spearman_neg_score_vs_signed_intensity": spearman(neg_scores, signed),
            "spearman_valence_score_vs_signed_intensity": spearman(val_scores, signed),
        })
    return out


def summarize_personas(score_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: defaultdict[tuple[str, str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in score_rows:
        grouped[(
            str(row["stage"]),
            str(row["test"]),
            str(row["persona"]),
            str(row["pole"]),
            str(row["round"]),
        )].append(row)

    out: list[dict[str, object]] = []
    for (stage, test, persona, pole, round_id), rows in sorted(grouped.items()):
        # Average over layers first within each run, then across runs.
        by_run = defaultdict(list)
        for row in rows:
            by_run[str(row["run_id"])].append(float(row["neg_score"]))
        run_means = [mean(vals) for vals in by_run.values()]
        out.append({
            "stage": stage,
            "test": test,
            "persona": persona,
            "pole": pole,
            "round": round_id,
            "n_runs": len(by_run),
            "mean_neg_score_all_layers": mean(run_means),
            "mean_valence_score_all_layers": -mean(run_means),
            "mean_rating": mean(row["rating"] for row in rows),
            "mean_signed_intensity": mean(row["signed_intensity"] for row in rows),
        })
    return out


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    train_stages = {stage.strip() for stage in args.train_stages.split(",") if stage.strip()}

    records = load_records(args.repo_root, args.round1_npz_root, args.round2_npz_root)
    print(f"Loaded {len(records)} JSON/NPZ run pairs")
    print("Poles:", Counter(record.pole for record in records))
    print("Personas:", Counter(record.persona for record in records))
    print("Training stages:", ", ".join(sorted(train_stages)))

    mean_arr, std_arr = compute_standardizer(records, train_stages)
    direction, counts = compute_direction(records, train_stages, mean_arr, std_arr)
    score_rows = score_records(records, mean_arr, std_arr, direction)
    layer_rows = summarize_layers(score_rows)
    persona_rows = summarize_personas(score_rows)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "hidden_vector_scores.csv", score_rows)
    write_csv(args.output_dir / "hidden_vector_layer_summary.csv", layer_rows)
    write_csv(args.output_dir / "hidden_vector_persona_summary.csv", persona_rows)

    print("Training state counts:", dict(counts))
    print(f"Wrote {len(score_rows)} score rows")
    print(f"Wrote {len(layer_rows)} layer summary rows")
    print(f"Wrote {len(persona_rows)} persona summary rows")
    print(f"Output directory: {args.output_dir}")

    report_rows = [row for row in layer_rows if row["stage"] == "report"]
    best = sorted(
        report_rows,
        key=lambda row: abs(row["spearman_valence_score_vs_rating"] or 0),
        reverse=True,
    )[:10]
    print("\nTop report-stage layers by |Spearman(valence_score, rating)|:")
    for row in best:
        print(
            f"  L{row['layer']:02d}: "
            f"rho={row['spearman_valence_score_vs_rating']:+.3f}, "
            f"pole_gap={row['pole_gap_NEG_minus_POS']:+.3f}, "
            f"persona_ratio={row['persona_ratio_within_NEG']}"
        )


if __name__ == "__main__":
    main()
