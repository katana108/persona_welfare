#!/usr/bin/env python3
"""Render lightweight SVG figures for the exploratory analysis notes."""

from __future__ import annotations

import csv
import html
import json
import math
import re
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VECTOR_DIR = REPO_ROOT / "analysis" / "vector_outputs"
CROSSVAL_DIR = REPO_ROOT / "analysis" / "crossval_outputs"
FIGURE_DIR = REPO_ROOT / "analysis" / "figures"

PERSONAS = ["BASELINE", "SOL", "SWARM", "STATIC"]
POLES = ["NEG", "NEU", "POS"]
STAGES = ["manip1", "manip2", "choice1", "choice2", "report"]

COLORS = {
    "BASELINE": "#4C78A8",
    "SOL": "#F58518",
    "SWARM": "#54A24B",
    "STATIC": "#E45756",
    "pole": "#4C78A8",
    "persona": "#E45756",
    "rating": "#72B7B2",
    "vector": "#F58518",
    "jspace": "#B279A2",
    "behavior": "#9D755D",
}

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


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def f(value: object) -> float | None:
    if value in ("", None):
        return None
    return float(value)


def mean(values) -> float | None:
    vals = [float(v) for v in values if v not in ("", None)]
    return sum(vals) / len(vals) if vals else None


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


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3:
        return None
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0 or vy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(vx * vy)


def spearman(xs, ys) -> float | None:
    pairs = [(float(x), float(y)) for x, y in zip(xs, ys) if x not in ("", None) and y not in ("", None)]
    if len(pairs) < 3:
        return None
    return pearson(ranks([x for x, _ in pairs]), ranks([y for _, y in pairs]))


def eta_squared(values, groups) -> float | None:
    pairs = [(float(v), g) for v, g in zip(values, groups) if v not in ("", None) and g not in ("", None)]
    if len(pairs) < 2:
        return None
    grand = sum(v for v, _ in pairs) / len(pairs)
    total = sum((v - grand) ** 2 for v, _ in pairs)
    by_group: defaultdict[str, list[float]] = defaultdict(list)
    for value, group in pairs:
        by_group[str(group)].append(value)
    between = sum(len(vals) * (sum(vals) / len(vals) - grand) ** 2 for vals in by_group.values())
    return between / total if total else None


def infer_test_and_pole(source_file: str) -> tuple[str, str]:
    upper = source_file.upper()
    pole = "NEG" if "NEG" in upper else "NEU" if "NEU" in upper else "POS"
    if source_file.startswith(("0_T1", "1_T1", "2_T1")):
        test = "T0 social"
    elif source_file.startswith("Test1_"):
        test = "T1 task"
    else:
        test = "T2 identity"
    return test, pole


def parse_self_report(answer: str) -> tuple[int, str, int]:
    text = answer.strip().lower()
    lines = [line.strip() for line in re.split(r"[\n;]+", text) if line.strip()]
    rating = None
    intensity = None
    for line in lines:
        m = re.match(r"^1\s*[\.)]?\s*([+-]?[0-4])\b", line)
        if m:
            rating = int(m.group(1))
        m = re.match(r"^3\s*[\.)]?\s*([1-7])\b", line)
        if m:
            intensity = int(m.group(1))
    if rating is None:
        m = re.search(r"\b1\s*[\.)]\s*([+-]?[0-4])\b", text)
        if m:
            rating = int(m.group(1))
    if intensity is None:
        m = re.search(r"\b3\s*[\.)]\s*([1-7])\b", text)
        if m:
            intensity = int(m.group(1))
    word = next((w for w in EMOTION_WORDS if re.search(r"\b" + re.escape(w) + r"\b", text)), None)
    numbers = [int(x) for x in re.findall(r"(?<!\d)[+-]?\d+(?!\d)", text)]
    if rating is None:
        candidates = [n for n in numbers if -4 <= n <= 4]
        if candidates:
            rating = candidates[0]
    if intensity is None:
        candidates = [n for n in numbers if 1 <= n <= 7]
        if candidates:
            intensity = candidates[-1]
    if rating is None or word is None or intensity is None:
        raise ValueError(f"Could not parse self-report: {answer!r}")
    return rating, word, intensity


def load_json_runs() -> list[dict[str, object]]:
    rows = []
    for path in sorted((REPO_ROOT / "data").glob("round*/*/*.json")):
        with path.open("r", encoding="utf-8") as f:
            env = json.load(f)
        test, pole = infer_test_and_pole(env["source_file"])
        rating, word, intensity = parse_self_report(env["turns"][-1]["answer"])
        emotion_valence = EMOTION_VALENCE[word]
        c1 = re.search(r"\b([AB])\b", env["turns"][-3]["answer"].strip().upper())
        c2 = re.search(r"\b([AB])\b", env["turns"][-2]["answer"].strip().upper())
        rows.append({
            "run_id": path.relative_to(REPO_ROOT).as_posix().removesuffix(".json"),
            "round": path.relative_to(REPO_ROOT / "data").parts[0],
            "test": test,
            "pole": pole,
            "pole_num": {"NEG": -1, "NEU": 0, "POS": 1}[pole],
            "persona": env["persona"],
            "rating": rating,
            "emotion_word": word,
            "emotion_valence": emotion_valence,
            "intensity": intensity,
            "signed_intensity": emotion_valence * intensity,
            "c1": c1.group(1) if c1 else "",
            "c2": c2.group(1) if c2 else "",
        })
    return rows


def svg_frame(width: int, height: int, title: str, body: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <style>
    text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #222; }}
    .title {{ font-size: 22px; font-weight: 700; }}
    .subtitle {{ font-size: 12px; fill: #555; }}
    .axis {{ stroke: #333; stroke-width: 1; }}
    .grid {{ stroke: #ddd; stroke-width: 1; }}
    .label {{ font-size: 12px; }}
    .tiny {{ font-size: 10px; fill: #555; }}
  </style>
  <text x="32" y="34" class="title">{esc(title)}</text>
{body}
</svg>
"""


def save_svg(name: str, content: str) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    (FIGURE_DIR / name).write_text(content, encoding="utf-8")
    print(f"wrote {FIGURE_DIR / name}")


def draw_bar_chart(filename: str, title: str, items: list[tuple[str, float, str]], x_max: float = 1.0) -> None:
    width = 920
    height = 90 + 44 * len(items)
    left = 270
    right = 40
    top = 64
    chart_w = width - left - right
    zero_x = left
    parts = [f'  <line x1="{left}" y1="{top - 12}" x2="{left}" y2="{height - 32}" class="axis"/>']
    for tick in [0, 0.25, 0.5, 0.75, 1.0]:
        x = left + chart_w * tick / x_max
        parts.append(f'  <line x1="{x:.1f}" y1="{top - 12}" x2="{x:.1f}" y2="{height - 32}" class="grid"/>')
        parts.append(f'  <text x="{x:.1f}" y="{height - 12}" class="tiny" text-anchor="middle">{tick:.2f}</text>')
    for i, (label, value, color) in enumerate(items):
        y = top + i * 44
        bar_w = chart_w * max(0.0, min(x_max, value)) / x_max
        parts.append(f'  <text x="{left - 12}" y="{y + 17}" class="label" text-anchor="end">{esc(label)}</text>')
        parts.append(f'  <rect x="{zero_x}" y="{y}" width="{bar_w:.1f}" height="24" rx="3" fill="{color}"/>')
        parts.append(f'  <text x="{zero_x + bar_w + 8:.1f}" y="{y + 17}" class="label">{value:.3f}</text>')
    save_svg(filename, svg_frame(width, height, title, "\n".join(parts)))


def color_scale(value: float, limit: float = 1.0) -> str:
    value = max(-limit, min(limit, value)) / limit
    if value >= 0:
        r1, g1, b1 = (245, 245, 245)
        r2, g2, b2 = (43, 123, 169)
        t = value
    else:
        r1, g1, b1 = (245, 245, 245)
        r2, g2, b2 = (203, 77, 74)
        t = -value
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f"rgb({r},{g},{b})"


def draw_layer_heatmap(layer_summary: list[dict[str, str]]) -> None:
    width = 1060
    height = 430
    left = 95
    top = 76
    cell_w = 10.5
    cell_h = 30
    panel_gap = 42
    metrics = [
        ("spearman_valence_score_vs_pole_num", "Vector valence vs experimental pole"),
        ("spearman_valence_score_vs_rating", "Vector valence vs scalar rating"),
    ]
    parts = []
    for panel_idx, (metric, label) in enumerate(metrics):
        y0 = top + panel_idx * (len(STAGES) * cell_h + panel_gap)
        parts.append(f'  <text x="{left}" y="{y0 - 14}" class="subtitle">{esc(label)}</text>')
        for s_idx, stage in enumerate(STAGES):
            y = y0 + s_idx * cell_h
            parts.append(f'  <text x="{left - 12}" y="{y + 20}" class="label" text-anchor="end">{stage}</text>')
            for layer in range(80):
                row = next(r for r in layer_summary if r["stage"] == stage and int(r["layer"]) == layer)
                value = f(row[metric]) or 0.0
                x = left + layer * cell_w
                parts.append(
                    f'  <rect x="{x:.1f}" y="{y}" width="{cell_w + 0.2:.1f}" height="{cell_h - 3}" '
                    f'fill="{color_scale(value)}"><title>L{layer} {stage}: {value:.3f}</title></rect>'
                )
        axis_y = y0 + len(STAGES) * cell_h + 12
        for layer in [0, 10, 20, 30, 40, 50, 60, 70, 79]:
            x = left + layer * cell_w + cell_w / 2
            parts.append(f'  <text x="{x:.1f}" y="{axis_y}" class="tiny" text-anchor="middle">{layer}</text>')
    parts.append('  <text x="95" y="396" class="tiny">Blue = positive association. Red = negative association. Hover titles show exact values.</text>')
    save_svg("vector_layer_heatmap.svg", svg_frame(width, height, "Hidden-Vector Layer Map", "\n".join(parts)))


def draw_persona_profiles(json_rows: list[dict[str, object]]) -> None:
    width = 1060
    height = 610
    margin = 62
    panel_w = 300
    panel_h = 142
    x_gap = 30
    y_gap = 52
    tests = ["T0 social", "T1 task", "T2 identity"]
    parts = []
    for idx, test in enumerate(tests):
        x0 = margin + idx * (panel_w + x_gap)
        y0 = 84
        parts.append(f'  <text x="{x0}" y="{y0 - 24}" class="subtitle">{esc(test)}</text>')
        parts.append(f'  <line x1="{x0}" y1="{y0 + panel_h}" x2="{x0 + panel_w}" y2="{y0 + panel_h}" class="axis"/>')
        parts.append(f'  <line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + panel_h}" class="axis"/>')
        for tick in [-4, -2, 0, 2, 4]:
            y = y0 + panel_h - (tick + 4) / 8 * panel_h
            parts.append(f'  <line x1="{x0}" y1="{y:.1f}" x2="{x0 + panel_w}" y2="{y:.1f}" class="grid"/>')
            parts.append(f'  <text x="{x0 - 8}" y="{y + 4:.1f}" class="tiny" text-anchor="end">{tick}</text>')
        for p_idx, pole in enumerate(POLES):
            x = x0 + p_idx * (panel_w / 2)
            parts.append(f'  <text x="{x:.1f}" y="{y0 + panel_h + 18}" class="tiny" text-anchor="middle">{pole}</text>')
        for persona in PERSONAS:
            points = []
            for p_idx, pole in enumerate(POLES):
                vals = [
                    r["rating"]
                    for r in json_rows
                    if r["test"] == test and r["persona"] == persona and r["pole"] == pole
                ]
                value = mean(vals) or 0.0
                x = x0 + p_idx * (panel_w / 2)
                y = y0 + panel_h - (value + 4) / 8 * panel_h
                points.append((x, y, value))
            point_str = " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in points)
            parts.append(f'  <polyline points="{point_str}" fill="none" stroke="{COLORS[persona]}" stroke-width="2.4"/>')
            for x, y, value in points:
                parts.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{COLORS[persona]}"><title>{persona} {value:.2f}</title></circle>')
    legend_y = 315
    parts.append(f'  <text x="{margin}" y="{legend_y}" class="subtitle">Legend</text>')
    for i, persona in enumerate(PERSONAS):
        x = margin + i * 150
        parts.append(f'  <line x1="{x}" y1="{legend_y + 22}" x2="{x + 34}" y2="{legend_y + 22}" stroke="{COLORS[persona]}" stroke-width="3"/>')
        parts.append(f'  <text x="{x + 42}" y="{legend_y + 26}" class="label">{persona}</text>')
    parts.append(f'  <text x="{margin}" y="382" class="subtitle">Mean scalar self-report rating over two rounds. Ratings run from -4 to +4.</text>')
    save_svg("persona_rating_profiles.svg", svg_frame(width, height, "Persona Self-Report Profiles", "\n".join(parts)))


def draw_explicit_welfare_by_test(json_rows: list[dict[str, object]]) -> None:
    width = 1060
    height = 590
    left = 70
    top = 82
    panel_w = 286
    panel_gap = 48
    rating_h = 190
    emotion_top = 355
    emotion_h = 130
    tests = ["T0 social", "T1 task", "T2 identity"]
    parts = []
    for test_idx, test in enumerate(tests):
        x0 = left + test_idx * (panel_w + panel_gap)
        parts.append(f'  <text x="{x0}" y="{top - 24}" class="subtitle">{esc(test)}</text>')
        parts.append(f'  <line x1="{x0}" y1="{top + rating_h}" x2="{x0 + panel_w}" y2="{top + rating_h}" class="axis"/>')
        parts.append(f'  <line x1="{x0}" y1="{top}" x2="{x0}" y2="{top + rating_h}" class="axis"/>')
        for tick in [-4, -2, 0, 2, 4]:
            y = top + rating_h - (tick + 4) / 8 * rating_h
            parts.append(f'  <line x1="{x0}" y1="{y:.1f}" x2="{x0 + panel_w}" y2="{y:.1f}" class="grid"/>')
            parts.append(f'  <text x="{x0 - 8}" y="{y + 4:.1f}" class="tiny" text-anchor="end">{tick}</text>')
        mean_points = []
        for pole_idx, pole in enumerate(POLES):
            rows = [r for r in json_rows if r["test"] == test and r["pole"] == pole]
            values = [float(r["rating"]) for r in rows]
            value = mean(values) or 0.0
            x = x0 + 38 + pole_idx * 105
            y = top + rating_h - (value + 4) / 8 * rating_h
            ymin = top + rating_h - (max(values) + 4) / 8 * rating_h
            ymax = top + rating_h - (min(values) + 4) / 8 * rating_h
            parts.append(f'  <line x1="{x}" y1="{ymin:.1f}" x2="{x}" y2="{ymax:.1f}" stroke="{COLORS["rating"]}" stroke-width="3"/>')
            parts.append(f'  <circle cx="{x}" cy="{y:.1f}" r="6" fill="{COLORS["rating"]}" stroke="#222" stroke-width="0.7"/>')
            parts.append(f'  <text x="{x}" y="{y - 10:.1f}" class="tiny" text-anchor="middle">{value:+.2f}</text>')
            parts.append(f'  <text x="{x}" y="{top + rating_h + 20}" class="tiny" text-anchor="middle">{pole}</text>')
            mean_points.append((x, y))
        point_str = " ".join(f"{x},{y:.1f}" for x, y in mean_points)
        parts.append(f'  <polyline points="{point_str}" fill="none" stroke="{COLORS["rating"]}" stroke-width="2"/>')

        parts.append(f'  <line x1="{x0}" y1="{emotion_top + emotion_h}" x2="{x0 + panel_w}" y2="{emotion_top + emotion_h}" class="axis"/>')
        parts.append(f'  <line x1="{x0}" y1="{emotion_top}" x2="{x0}" y2="{emotion_top + emotion_h}" class="axis"/>')
        for tick in [0.0, 0.5, 1.0]:
            y = emotion_top + emotion_h - tick * emotion_h
            parts.append(f'  <line x1="{x0}" y1="{y:.1f}" x2="{x0 + panel_w}" y2="{y:.1f}" class="grid"/>')
            parts.append(f'  <text x="{x0 - 8}" y="{y + 4:.1f}" class="tiny" text-anchor="end">{tick:.1f}</text>')
        for pole_idx, pole in enumerate(POLES):
            rows = [r for r in json_rows if r["test"] == test and r["pole"] == pole]
            rate = sum(1 for r in rows if r["emotion_valence"] < 0) / len(rows)
            x = x0 + 17 + pole_idx * 105
            y = emotion_top + emotion_h - rate * emotion_h
            parts.append(f'  <rect x="{x}" y="{y:.1f}" width="42" height="{rate * emotion_h:.1f}" fill="{COLORS["persona"]}"/>')
            parts.append(f'  <text x="{x + 21}" y="{y - 7:.1f}" class="tiny" text-anchor="middle">{rate:.2f}</text>')
            parts.append(f'  <text x="{x + 21}" y="{emotion_top + emotion_h + 20}" class="tiny" text-anchor="middle">{pole}</text>')
    parts.append(f'  <text x="22" y="{top + rating_h / 2}" class="label" transform="rotate(-90 22 {top + rating_h / 2})" text-anchor="middle">Mean scalar rating</text>')
    parts.append(f'  <text x="22" y="{emotion_top + emotion_h / 2}" class="label" transform="rotate(-90 22 {emotion_top + emotion_h / 2})" text-anchor="middle">Negative-word rate</text>')
    parts.append(f'  <text x="{left}" y="550" class="subtitle">Top: mean rating with observed range. Bottom: fraction selecting a negative emotion word.</text>')
    save_svg("explicit_welfare_by_test.svg", svg_frame(width, height, "Explicit Welfare Signals Differ by Test", "\n".join(parts)))


def draw_round_replication(json_rows: list[dict[str, object]]) -> None:
    width = 760
    height = 650
    left = 86
    top = 76
    chart = 490
    by_key = {
        (r["round"], r["test"], r["pole"], r["persona"]): r
        for r in json_rows
    }
    pairs = []
    for test in ["T0 social", "T1 task", "T2 identity"]:
        for pole in POLES:
            for persona in PERSONAS:
                pairs.append((
                    by_key[("round1", test, pole, persona)],
                    by_key[("round2", test, pole, persona)],
                ))

    def scale(value: float) -> float:
        return left + (value + 4) / 8 * chart

    parts = [
        f'  <line x1="{left}" y1="{top + chart}" x2="{left + chart}" y2="{top + chart}" class="axis"/>',
        f'  <line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart}" class="axis"/>',
        f'  <line x1="{left}" y1="{top + chart}" x2="{left + chart}" y2="{top}" stroke="#777" stroke-dasharray="5 4"/>',
    ]
    for tick in [-4, -2, 0, 2, 4]:
        x = scale(tick)
        y = top + chart - (x - left)
        parts.append(f'  <line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + chart}" class="grid"/>')
        parts.append(f'  <line x1="{left}" y1="{y:.1f}" x2="{left + chart}" y2="{y:.1f}" class="grid"/>')
        parts.append(f'  <text x="{x:.1f}" y="{top + chart + 22}" class="tiny" text-anchor="middle">{tick}</text>')
        parts.append(f'  <text x="{left - 10}" y="{y + 4:.1f}" class="tiny" text-anchor="end">{tick}</text>')
    test_code = {"T0 social": "0", "T1 task": "1", "T2 identity": "2"}
    for r1, r2 in pairs:
        x = scale(float(r1["rating"]))
        y = top + chart - (scale(float(r2["rating"])) - left)
        parts.append(
            f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{COLORS[r1["persona"]]}" fill-opacity="0.64" stroke="#222" stroke-width="0.6">'
            f'<title>{esc(r1["test"])} {esc(r1["pole"])} {esc(r1["persona"])}: {r1["rating"]} to {r2["rating"]}</title></circle>'
        )
        parts.append(f'  <text x="{x:.1f}" y="{y + 3.5:.1f}" class="tiny" text-anchor="middle">{test_code[r1["test"]]}</text>')
    exact = sum(r1["rating"] == r2["rating"] for r1, r2 in pairs)
    rho = spearman([r1["rating"] for r1, _ in pairs], [r2["rating"] for _, r2 in pairs]) or 0.0
    parts.append(f'  <text x="{left + chart / 2}" y="610" class="label" text-anchor="middle">Round 1 scalar rating</text>')
    parts.append(f'  <text x="24" y="{top + chart / 2}" class="label" transform="rotate(-90 24 {top + chart / 2})" text-anchor="middle">Round 2 scalar rating</text>')
    parts.append(f'  <text x="600" y="104" class="subtitle">Exact matches: {exact}/36</text>')
    parts.append(f'  <text x="600" y="124" class="subtitle">Spearman: {rho:.3f}</text>')
    parts.append(f'  <text x="600" y="156" class="tiny">Point label: test 0/1/2</text>')
    for idx, persona in enumerate(PERSONAS):
        y = 194 + idx * 28
        parts.append(f'  <circle cx="606" cy="{y}" r="6" fill="{COLORS[persona]}"/>')
        parts.append(f'  <text x="620" y="{y + 4}" class="tiny">{persona}</text>')
    save_svg("round_replication.svg", svg_frame(width, height, "Round-to-Round Replication Is Partial", "\n".join(parts)))


def draw_scatter(score_rows: list[dict[str, str]]) -> None:
    width = 920
    height = 620
    left = 76
    top = 76
    chart_w = 720
    chart_h = 430
    band = range(33, 41)
    by_run: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in score_rows:
        if row["stage"] == "report" and int(row["layer"]) in band:
            by_run[row["run_id"]].append(row)
    points = []
    for rows in by_run.values():
        valence = mean(row["valence_score"] for row in rows) or 0.0
        sample = rows[0]
        points.append({
            "valence": valence,
            "rating": float(sample["rating"]),
            "persona": sample["persona"],
            "pole": sample["pole"],
            "test": sample["test"],
        })
    min_x = min(p["valence"] for p in points)
    max_x = max(p["valence"] for p in points)
    pad = (max_x - min_x) * 0.08
    min_x -= pad
    max_x += pad
    def sx(value: float) -> float:
        return left + (value - min_x) / (max_x - min_x) * chart_w
    def sy(value: float) -> float:
        return top + chart_h - (value + 4) / 8 * chart_h
    parts = [
        f'  <line x1="{left}" y1="{top + chart_h}" x2="{left + chart_w}" y2="{top + chart_h}" class="axis"/>',
        f'  <line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" class="axis"/>',
    ]
    for tick in [-4, -2, 0, 2, 4]:
        y = sy(tick)
        parts.append(f'  <line x1="{left}" y1="{y:.1f}" x2="{left + chart_w}" y2="{y:.1f}" class="grid"/>')
        parts.append(f'  <text x="{left - 10}" y="{y + 4:.1f}" class="tiny" text-anchor="end">{tick}</text>')
    for tick in [min_x, (min_x + max_x) / 2, max_x]:
        x = sx(tick)
        parts.append(f'  <text x="{x:.1f}" y="{top + chart_h + 22}" class="tiny" text-anchor="middle">{tick:.1f}</text>')
    for point in points:
        x = sx(point["valence"])
        y = sy(point["rating"])
        pole_mark = {"NEG": "N", "NEU": "0", "POS": "P"}[point["pole"]]
        parts.append(
            f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{COLORS[point["persona"]]}" fill-opacity="0.76" stroke="#222" stroke-width="0.4">'
            f'<title>{point["persona"]} {point["pole"]} {point["test"]}: valence {point["valence"]:.2f}, rating {point["rating"]:.0f}</title></circle>'
        )
        parts.append(f'  <text x="{x:.1f}" y="{y + 3.5:.1f}" class="tiny" text-anchor="middle" fill="#fff">{pole_mark}</text>')
    parts.append(f'  <text x="{left + chart_w / 2}" y="{height - 44}" class="label" text-anchor="middle">Report-stage hidden-vector valence, layers 33-40</text>')
    parts.append(f'  <text x="22" y="{top + chart_h / 2}" class="label" transform="rotate(-90 22 {top + chart_h / 2})" text-anchor="middle">Scalar rating (-4 to +4)</text>')
    legend_x = 820
    for i, persona in enumerate(PERSONAS):
        y = 112 + i * 28
        parts.append(f'  <circle cx="{legend_x}" cy="{y}" r="6" fill="{COLORS[persona]}"/>')
        parts.append(f'  <text x="{legend_x + 14}" y="{y + 4}" class="tiny">{persona}</text>')
    parts.append(f'  <text x="{legend_x}" y="258" class="tiny">N=NEG, 0=NEU, P=POS</text>')
    save_svg("vector_vs_report_scatter.svg", svg_frame(width, height, "Scaffold-Gating View: Vector Score vs Report", "\n".join(parts)))


def draw_eta_bars(json_rows: list[dict[str, object]], score_rows: list[dict[str, str]]) -> None:
    bands = {
        "manip2 L9-13": ("manip2", range(9, 14)),
        "choice1 L9-13": ("choice1", range(9, 14)),
        "report L33-40": ("report", range(33, 41)),
        "report L70-79": ("report", range(70, 80)),
    }
    run_band: defaultdict[tuple[str, str], list[float]] = defaultdict(list)
    meta = {}
    for row in score_rows:
        layer = int(row["layer"])
        for label, (stage, band) in bands.items():
            if row["stage"] == stage and layer in band:
                run_band[(row["run_id"], label)].append(float(row["valence_score"]))
                meta[row["run_id"]] = row
    items = []
    for label in bands:
        rows = []
        for (run_id, band_label), vals in run_band.items():
            if band_label == label:
                rows.append((mean(vals), meta[run_id]))
        pole_eta = eta_squared([v for v, _ in rows], [m["pole"] for _, m in rows]) or 0.0
        persona_eta = eta_squared([v for v, _ in rows], [m["persona"] for _, m in rows]) or 0.0
        items.append((label, pole_eta, persona_eta))
    rating_pole = eta_squared([r["rating"] for r in json_rows], [r["pole"] for r in json_rows]) or 0.0
    rating_persona = eta_squared([r["rating"] for r in json_rows], [r["persona"] for r in json_rows]) or 0.0
    items.append(("scalar report", rating_pole, rating_persona))

    width = 930
    height = 390
    left = 170
    top = 74
    chart_w = 660
    row_h = 48
    parts = []
    for tick in [0, 0.25, 0.5, 0.75, 1.0]:
        x = left + chart_w * tick
        parts.append(f'  <line x1="{x:.1f}" y1="{top - 20}" x2="{x:.1f}" y2="{top + row_h * len(items)}" class="grid"/>')
        parts.append(f'  <text x="{x:.1f}" y="{height - 30}" class="tiny" text-anchor="middle">{tick:.2f}</text>')
    for i, (label, pole_eta, persona_eta) in enumerate(items):
        y = top + i * row_h
        parts.append(f'  <text x="{left - 12}" y="{y + 23}" class="label" text-anchor="end">{esc(label)}</text>')
        parts.append(f'  <rect x="{left}" y="{y + 3}" width="{chart_w * pole_eta:.1f}" height="15" fill="{COLORS["pole"]}"/>')
        parts.append(f'  <rect x="{left}" y="{y + 23}" width="{chart_w * persona_eta:.1f}" height="15" fill="{COLORS["persona"]}"/>')
        parts.append(f'  <text x="{left + chart_w * pole_eta + 6:.1f}" y="{y + 15}" class="tiny">{pole_eta:.3f}</text>')
        parts.append(f'  <text x="{left + chart_w * persona_eta + 6:.1f}" y="{y + 35}" class="tiny">{persona_eta:.3f}</text>')
    parts.append(f'  <rect x="{left}" y="330" width="16" height="12" fill="{COLORS["pole"]}"/><text x="{left + 22}" y="340" class="tiny">pole eta-squared</text>')
    parts.append(f'  <rect x="{left + 150}" y="330" width="16" height="12" fill="{COLORS["persona"]}"/><text x="{left + 172}" y="340" class="tiny">persona eta-squared</text>')
    save_svg("eta_pole_vs_persona.svg", svg_frame(width, height, "Where Variation Concentrates", "\n".join(parts)))


def draw_channel_alignment(json_rows: list[dict[str, object]], layer_summary: list[dict[str, str]]) -> None:
    report_rows = [r for r in layer_summary if r["stage"] == "report" and 33 <= int(r["layer"]) <= 40]
    manip_rows = [r for r in layer_summary if r["stage"] == "manip2" and 9 <= int(r["layer"]) <= 13]
    items = [
        (
            "self-report: rating vs signed intensity",
            abs(spearman([r["rating"] for r in json_rows], [r["signed_intensity"] for r in json_rows]) or 0.0),
            COLORS["rating"],
        ),
        (
            "self-report: rating vs emotion valence",
            abs(spearman([r["rating"] for r in json_rows], [r["emotion_valence"] for r in json_rows]) or 0.0),
            COLORS["rating"],
        ),
        (
            "vector: manip2 L9-13 vs pole",
            abs(mean(f(r["spearman_valence_score_vs_pole_num"]) for r in manip_rows) or 0.0),
            COLORS["vector"],
        ),
        (
            "vector: report L33-40 vs rating",
            abs(mean(f(r["spearman_valence_score_vs_rating"]) for r in report_rows) or 0.0),
            COLORS["vector"],
        ),
        (
            "behavior: continue/end has little variance",
            2 / 72,
            COLORS["behavior"],
        ),
    ]
    draw_bar_chart("channel_alignment.svg", "Channel Alignment Snapshot", items)


def run_band_rows(
    score_rows: list[dict[str, str]],
    stage: str,
    layers: range,
) -> list[dict[str, object]]:
    by_run: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in score_rows:
        if row["stage"] == stage and int(row["layer"]) in layers:
            by_run[row["run_id"]].append(row)

    rows = []
    for run_id, run_rows in by_run.items():
        sample = run_rows[0]
        rows.append({
            "run_id": run_id,
            "round": sample["round"],
            "test": sample["test"],
            "pole": sample["pole"],
            "persona": sample["persona"],
            "rating": float(sample["rating"]),
            "signed_intensity": float(sample["signed_intensity"]),
            "valence": mean(row["valence_score"] for row in run_rows) or 0.0,
        })
    return rows


def draw_mismatch_candidates(crossval_rows: list[dict[str, str]]) -> None:
    rows = [
        {
            "run_id": row["run_id"],
            "round": row["round"],
            "test": row["test"],
            "pole": row["pole"],
            "persona": row["persona"],
            "rating": float(row["rating"]),
            "valence": float(row["mean_valence_score"]),
        }
        for row in crossval_rows
        if row["stage"] == "report" and row["band"] == "L33-40"
    ]
    mu = mean(row["valence"] for row in rows) or 0.0
    sd = math.sqrt(sum((row["valence"] - mu) ** 2 for row in rows) / (len(rows) - 1))
    for row in rows:
        row["z"] = (row["valence"] - mu) / sd

    width = 980
    height = 650
    left = 82
    top = 76
    chart_w = 730
    chart_h = 430
    min_x = -3.2
    max_x = 2.4

    def sx(value: float) -> float:
        return left + (value - min_x) / (max_x - min_x) * chart_w

    def sy(value: float) -> float:
        return top + chart_h - (value + 4) / 8 * chart_h

    parts = [
        f'  <rect x="{sx(min_x):.1f}" y="{sy(4):.1f}" width="{sx(-0.75) - sx(min_x):.1f}" height="{sy(0) - sy(4):.1f}" fill="#FDEDEC"/>',
        f'  <text x="{sx(-2.2):.1f}" y="{sy(3.45):.1f}" class="tiny" text-anchor="middle">NEG-like vector, neutral/positive report</text>',
        f'  <line x1="{left}" y1="{top + chart_h}" x2="{left + chart_w}" y2="{top + chart_h}" class="axis"/>',
        f'  <line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" class="axis"/>',
        f'  <line x1="{sx(-0.75):.1f}" y1="{top}" x2="{sx(-0.75):.1f}" y2="{top + chart_h}" stroke="#B94A48" stroke-dasharray="5 4"/>',
        f'  <line x1="{left}" y1="{sy(0):.1f}" x2="{left + chart_w}" y2="{sy(0):.1f}" stroke="#555" stroke-dasharray="5 4"/>',
    ]
    for tick in [-3, -2, -1, 0, 1, 2]:
        x = sx(tick)
        parts.append(f'  <line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + chart_h}" class="grid"/>')
        parts.append(f'  <text x="{x:.1f}" y="{top + chart_h + 22}" class="tiny" text-anchor="middle">{tick}</text>')
    for tick in [-4, -2, 0, 2, 4]:
        y = sy(tick)
        parts.append(f'  <line x1="{left}" y1="{y:.1f}" x2="{left + chart_w}" y2="{y:.1f}" class="grid"/>')
        parts.append(f'  <text x="{left - 10}" y="{y + 4:.1f}" class="tiny" text-anchor="end">{tick}</text>')

    mismatch = []
    for row in rows:
        x = sx(row["z"])
        y = sy(row["rating"])
        radius = 8 if row["z"] < -0.75 and row["rating"] >= 0 else 5
        stroke = "#B94A48" if radius == 8 else "#222"
        parts.append(
            f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{COLORS[row["persona"]]}" '
            f'fill-opacity="0.72" stroke="{stroke}" stroke-width="1.1">'
            f'<title>{esc(row["run_id"])}: z {row["z"]:.2f}, rating {row["rating"]:.0f}</title></circle>'
        )
        if radius == 8:
            mismatch.append(row)

    parts.append(f'  <text x="{left + chart_w / 2}" y="{height - 52}" class="label" text-anchor="middle">Held-out report-vector valence z-score, layers 33-40</text>')
    parts.append(f'  <text x="24" y="{top + chart_h / 2}" class="label" transform="rotate(-90 24 {top + chart_h / 2})" text-anchor="middle">Scalar self-report rating</text>')
    parts.append(f'  <text x="{left}" y="548" class="subtitle">Each point is scored by a vector trained on the other round. Highlighted cases are NEG-like but report neutral or positive.</text>')

    legend_x = 835
    parts.append(f'  <text x="{legend_x}" y="95" class="subtitle">Personas</text>')
    for i, persona in enumerate(PERSONAS):
        y = 122 + i * 28
        parts.append(f'  <circle cx="{legend_x}" cy="{y}" r="6" fill="{COLORS[persona]}"/>')
        parts.append(f'  <text x="{legend_x + 14}" y="{y + 4}" class="tiny">{persona}</text>')
    parts.append(f'  <text x="{legend_x}" y="266" class="subtitle">Replicated social NEG pair</text>')
    parts.append(f'  <text x="{legend_x}" y="290" class="tiny">Round 1: Sol -2, Static 0</text>')
    parts.append(f'  <text x="{legend_x}" y="310" class="tiny">Round 2: Sol -2, Static +2</text>')
    parts.append(f'  <text x="{legend_x}" y="340" class="tiny">Their held-out vector scores</text>')
    parts.append(f'  <text x="{legend_x}" y="358" class="tiny">remain closely matched.</text>')

    save_svg("masking_candidates.svg", svg_frame(width, height, "Self-Report vs Held-Out Vector Mismatch", "\n".join(parts)))


def draw_behavior_mismatch(json_rows: list[dict[str, object]]) -> None:
    width = 960
    height = 420
    left = 86
    top = 76
    panel_w = 250
    panel_h = 220
    gap = 42
    tests = ["T0 social", "T1 task", "T2 identity"]
    parts = []
    for t_idx, test in enumerate(tests):
        x0 = left + t_idx * (panel_w + gap)
        y0 = top
        parts.append(f'  <text x="{x0}" y="{y0 - 20}" class="subtitle">{esc(test)}</text>')
        parts.append(f'  <line x1="{x0}" y1="{y0 + panel_h}" x2="{x0 + panel_w}" y2="{y0 + panel_h}" class="axis"/>')
        parts.append(f'  <line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + panel_h}" class="axis"/>')
        for tick in [0, 0.5, 1.0]:
            y = y0 + panel_h - tick * panel_h
            parts.append(f'  <line x1="{x0}" y1="{y:.1f}" x2="{x0 + panel_w}" y2="{y:.1f}" class="grid"/>')
            parts.append(f'  <text x="{x0 - 8}" y="{y + 4:.1f}" class="tiny" text-anchor="end">{tick:.1f}</text>')
        for p_idx, pole in enumerate(POLES):
            rows = [r for r in json_rows if r["test"] == test and r["pole"] == pole]
            rate = sum(1 for r in rows if r["c1"] == "A") / len(rows)
            bar_w = 48
            x = x0 + 34 + p_idx * 78
            y = y0 + panel_h - rate * panel_h
            parts.append(f'  <rect x="{x}" y="{y:.1f}" width="{bar_w}" height="{rate * panel_h:.1f}" fill="{COLORS["behavior"]}"/>')
            parts.append(f'  <text x="{x + bar_w / 2}" y="{y - 6:.1f}" class="tiny" text-anchor="middle">{rate:.2f}</text>')
            parts.append(f'  <text x="{x + bar_w / 2}" y="{y0 + panel_h + 18}" class="tiny" text-anchor="middle">{pole}</text>')
    parts.append(f'  <text x="{left + 375}" y="360" class="label" text-anchor="middle">Rate of choosing A in the first behavioral choice</text>')
    parts.append(f'  <text x="25" y="{top + panel_h / 2}" class="label" transform="rotate(-90 25 {top + panel_h / 2})" text-anchor="middle">A-choice rate</text>')
    parts.append(f'  <text x="{left}" y="388" class="subtitle">Social approach is saturated; task and identity choices vary strongly by condition.</text>')
    save_svg("behavior_choice_by_pole.svg", svg_frame(width, height, "Behavior Channel: A-Choice Rate by Pole", "\n".join(parts)))


def draw_stage_alignment(layer_summary: list[dict[str, str]]) -> None:
    bands = {
        "L9-13": range(9, 14),
        "L20-32": range(20, 33),
        "L33-40": range(33, 41),
        "L55-63": range(55, 64),
        "L70-79": range(70, 80),
    }
    items = []
    for stage, band_name in [
        ("manip2", "L9-13"),
        ("choice1", "L9-13"),
        ("choice2", "L9-13"),
        ("report", "L33-40"),
        ("report", "L70-79"),
    ]:
        rows = [r for r in layer_summary if r["stage"] == stage and int(r["layer"]) in bands[band_name]]
        pole = mean(f(r["spearman_valence_score_vs_pole_num"]) for r in rows) or 0.0
        rating = mean(f(r["spearman_valence_score_vs_rating"]) for r in rows) or 0.0
        items.append((f"{stage} {band_name}: vs pole", abs(pole), COLORS["pole"]))
        items.append((f"{stage} {band_name}: vs rating", abs(rating), COLORS["rating"]))
    draw_bar_chart("stage_alignment_contrast.svg", "Vector Alignment Shifts From Pole To Report", items)


def main() -> None:
    json_rows = load_json_runs()
    layer_summary = read_csv(VECTOR_DIR / "hidden_vector_layer_summary.csv")
    score_rows = read_csv(VECTOR_DIR / "hidden_vector_scores.csv")
    crossval_rows = read_csv(CROSSVAL_DIR / "crossval_band_scores.csv")

    draw_channel_alignment(json_rows, layer_summary)
    draw_layer_heatmap(layer_summary)
    draw_persona_profiles(json_rows)
    draw_explicit_welfare_by_test(json_rows)
    draw_round_replication(json_rows)
    draw_scatter(score_rows)
    draw_eta_bars(json_rows, score_rows)
    draw_mismatch_candidates(crossval_rows)
    draw_behavior_mismatch(json_rows)
    draw_stage_alignment(layer_summary)


if __name__ == "__main__":
    main()
