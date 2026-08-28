#!/usr/bin/env python3
"""Cross-validate hidden-vector NEG-POS directions across battery rounds.

This is the stricter companion to analyze_hidden_vectors.py. It trains a
per-layer NEG-POS direction on one round and evaluates it on the other round,
then swaps train/test rounds.
"""

from __future__ import annotations

import argparse
import csv
import html
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np

from analyze_hidden_vectors import (
    compute_direction,
    compute_standardizer,
    load_records,
    score_records,
)


BANDS = {
    "L9-13": range(9, 14),
    "L20-32": range(20, 33),
    "L33-40": range(33, 41),
    "L55-63": range(55, 64),
    "L70-79": range(70, 80),
}

STAGES = ["manip1", "manip2", "choice1", "choice2", "report"]


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Train NEG-POS hidden-vector directions on one round and test on the other."
    )
    parser.add_argument("--repo-root", type=Path, default=repo_root)
    parser.add_argument(
        "--round1-npz-root",
        type=Path,
        required=True,
        help="Directory containing the round-1 NPZ hidden-state files.",
    )
    parser.add_argument(
        "--round2-npz-root",
        type=Path,
        required=True,
        help="Directory containing the round-2 NPZ hidden-state files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=repo_root / "analysis" / "crossval_outputs",
    )
    parser.add_argument(
        "--figure-dir",
        type=Path,
        default=repo_root / "analysis" / "figures",
    )
    parser.add_argument(
        "--train-stages",
        default="manip1,manip2,choice1,choice2",
        help="Comma-separated stages used to build the NEG-vs-POS direction.",
    )
    return parser.parse_args()


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
    xs = [float(x) for x in xs]
    ys = [float(y) for y in ys]
    if len(xs) < 3:
        return None
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0 or vy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(vx * vy)


def spearman(xs: Iterable[float], ys: Iterable[float]) -> float | None:
    pairs = [(float(x), float(y)) for x, y in zip(xs, ys)]
    if len(pairs) < 3:
        return None
    return pearson(ranks([x for x, _ in pairs]), ranks([y for _, y in pairs]))


def permutation_p(xs: list[float], ys: list[float], n_perm: int = 5000, seed: int = 7) -> tuple[float, float]:
    obs = spearman(xs, ys)
    if obs is None:
        return math.nan, math.nan
    rng = random.Random(seed)
    shuffled = ys[:]
    hits = 1
    for _ in range(n_perm):
        rng.shuffle(shuffled)
        stat = spearman(xs, shuffled)
        if stat is not None and abs(stat) >= abs(obs):
            hits += 1
    return obs, hits / (n_perm + 1)


def eta_squared(values: list[float], groups: list[str]) -> float | None:
    if len(values) < 2:
        return None
    grand = sum(values) / len(values)
    total = sum((value - grand) ** 2 for value in values)
    by_group: defaultdict[str, list[float]] = defaultdict(list)
    for value, group in zip(values, groups):
        by_group[str(group)].append(float(value))
    between = sum(
        len(group_values) * (sum(group_values) / len(group_values) - grand) ** 2
        for group_values in by_group.values()
    )
    return between / total if total else None


def mean(values: Iterable[float]) -> float:
    vals = [float(value) for value in values]
    return sum(vals) / len(vals)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=list(rows[0].keys()), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def band_rows(split: str, score_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: defaultdict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in score_rows:
        layer = int(row["layer"])
        for band, layers in BANDS.items():
            if layer in layers:
                grouped[(str(row["run_id"]), str(row["stage"]), band)].append(row)

    out = []
    for (run_id, stage, band), rows in sorted(grouped.items()):
        sample = rows[0]
        out.append({
            "split": split,
            "run_id": run_id,
            "round": sample["round"],
            "test": sample["test"],
            "pole": sample["pole"],
            "pole_num": sample["pole_num"],
            "persona": sample["persona"],
            "stage": stage,
            "band": band,
            "mean_valence_score": mean(float(row["valence_score"]) for row in rows),
            "rating": sample["rating"],
            "signed_intensity": sample["signed_intensity"],
            "c1": sample["c1"],
            "c2": sample["c2"],
        })
    return out


def summarize_band_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: defaultdict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["split"]), str(row["stage"]), str(row["band"]))].append(row)

    out = []
    for (split, stage, band), items in sorted(grouped.items()):
        values = [float(row["mean_valence_score"]) for row in items]
        pole_nums = [float(row["pole_num"]) for row in items]
        ratings = [float(row["rating"]) for row in items]
        signed = [float(row["signed_intensity"]) for row in items]
        poles = [str(row["pole"]) for row in items]
        personas = [str(row["persona"]) for row in items]
        rho_pole, p_pole = permutation_p(values, pole_nums)
        rho_rating, p_rating = permutation_p(values, ratings)
        rho_signed, p_signed = permutation_p(values, signed)
        out.append({
            "split": split,
            "stage": stage,
            "band": band,
            "n": len(items),
            "spearman_valence_vs_pole": rho_pole,
            "perm_p_valence_vs_pole": p_pole,
            "spearman_valence_vs_rating": rho_rating,
            "perm_p_valence_vs_rating": p_rating,
            "spearman_valence_vs_signed_intensity": rho_signed,
            "perm_p_valence_vs_signed_intensity": p_signed,
            "eta2_pole": eta_squared(values, poles),
            "eta2_persona": eta_squared(values, personas),
        })
    return out


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_crossval_svg(summary_rows: list[dict[str, object]], figure_dir: Path) -> None:
    selected = [
        ("manip2", "L9-13", "pole"),
        ("choice1", "L9-13", "pole"),
        ("choice2", "L9-13", "pole"),
        ("report", "L33-40", "rating"),
        ("report", "L55-63", "rating"),
        ("report", "L70-79", "rating"),
    ]
    width = 1120
    height = 500
    left = 230
    top = 68
    row_h = 46
    chart_w = 760

    lookup = {
        (str(row["split"]), str(row["stage"]), str(row["band"])): row
        for row in summary_rows
    }
    colors = {"round1_to_round2": "#4C78A8", "round2_to_round1": "#F58518"}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#222}.title{font-size:22px;font-weight:700}.label{font-size:12px}.tiny{font-size:10px;fill:#555}.grid{stroke:#ddd}.axis{stroke:#333}</style>',
        '<text x="32" y="34" class="title">Cross-Validated Hidden-Vector Generalization</text>',
    ]
    for tick in [0, 0.25, 0.5, 0.75, 1.0]:
        x = left + chart_w * tick
        parts.append(f'<line x1="{x:.1f}" y1="{top - 18}" x2="{x:.1f}" y2="{top + row_h * len(selected)}" class="grid"/>')
        parts.append(f'<text x="{x:.1f}" y="{top + row_h * len(selected) + 28}" class="tiny" text-anchor="middle">{tick:.2f}</text>')

    for i, (stage, band, target) in enumerate(selected):
        y = top + i * row_h
        label = f"{stage} {band} vs {target}"
        parts.append(f'<text x="{left - 12}" y="{y + 26}" class="label" text-anchor="end">{escape(label)}</text>')
        for j, split in enumerate(["round1_to_round2", "round2_to_round1"]):
            row = lookup[(split, stage, band)]
            metric = "spearman_valence_vs_pole" if target == "pole" else "spearman_valence_vs_rating"
            value = abs(float(row[metric]))
            bar_y = y + 5 + j * 18
            parts.append(f'<rect x="{left}" y="{bar_y}" width="{chart_w * value:.1f}" height="14" fill="{colors[split]}"/>')
            parts.append(f'<text x="{left + chart_w * value + 6:.1f}" y="{bar_y + 11}" class="tiny">{value:.3f}</text>')

    parts.append(f'<rect x="{left}" y="408" width="16" height="12" fill="{colors["round1_to_round2"]}"/><text x="{left + 22}" y="418" class="tiny">train round1, test round2</text>')
    parts.append(f'<rect x="{left + 180}" y="408" width="16" height="12" fill="{colors["round2_to_round1"]}"/><text x="{left + 202}" y="418" class="tiny">train round2, test round1</text>')
    parts.append(f'<text x="{left}" y="468" class="tiny">Bars show absolute Spearman correlations on held-out rounds. This is stricter than in-sample scoring.</text>')
    parts.append("</svg>")

    figure_dir.mkdir(parents=True, exist_ok=True)
    path = figure_dir / "crossval_vector_generalization.svg"
    path.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {path}")


def main() -> None:
    args = parse_args()
    train_stages = {stage.strip() for stage in args.train_stages.split(",") if stage.strip()}
    all_records = load_records(args.repo_root, args.round1_npz_root, args.round2_npz_root)

    all_band_rows: list[dict[str, object]] = []
    for train_round, test_round in [("round1", "round2"), ("round2", "round1")]:
        train_records = [record for record in all_records if record.round_id == train_round]
        test_records = [record for record in all_records if record.round_id == test_round]
        mean_arr, std_arr = compute_standardizer(train_records, train_stages)
        direction, counts = compute_direction(train_records, train_stages, mean_arr, std_arr)
        scores = score_records(test_records, mean_arr, std_arr, direction)
        split = f"{train_round}_to_{test_round}"
        rows = band_rows(split, scores)
        all_band_rows.extend(rows)
        print(f"{split}: trained on {dict(counts)}, scored {len(test_records)} held-out runs")

    summary_rows = summarize_band_rows(all_band_rows)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "crossval_band_scores.csv", all_band_rows)
    write_csv(args.output_dir / "crossval_summary.csv", summary_rows)
    render_crossval_svg(summary_rows, args.figure_dir)

    print("\nKey held-out results:")
    for row in summary_rows:
        if (row["stage"], row["band"]) in {
            ("manip2", "L9-13"),
            ("choice1", "L9-13"),
            ("choice2", "L9-13"),
            ("report", "L33-40"),
            ("report", "L70-79"),
        }:
            print(
                f"{row['split']} {row['stage']} {row['band']}: "
                f"rho_pole={row['spearman_valence_vs_pole']:+.3f} "
                f"p={row['perm_p_valence_vs_pole']:.4f}; "
                f"rho_rating={row['spearman_valence_vs_rating']:+.3f} "
                f"p={row['perm_p_valence_vs_rating']:.4f}; "
                f"eta_pole={row['eta2_pole']:.3f} "
                f"eta_persona={row['eta2_persona']:.3f}"
            )


if __name__ == "__main__":
    main()
