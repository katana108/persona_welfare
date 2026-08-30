#!/usr/bin/env python3
"""Build the outside-reader figures and PDF for the six-run grand analysis.

The script reads only committed derived CSVs plus one published round-1 JSON
example. It does not require the large local NPZ archives.
"""

from __future__ import annotations

import csv
import html
import json
from collections import defaultdict
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
GRAND = ROOT / "analysis" / "grand_analysis"
FIGURES = GRAND / "figures"
PDF_PATH = ROOT / "docs" / "persona_welfare_grand_report_runs_1_6.pdf"

NAVY = "#172033"
MUTED = "#5b6b84"
GRID = "#d9e2ec"
BLUE = "#2f66e5"
RED = "#df3034"
GREEN = "#159447"
ORANGE = "#d97706"
PALE_BLUE = "#eef4ff"
PALE_RED = "#fff0f0"
PALE_GREEN = "#edf9f1"


EXPERIMENTS = [
    {
        "name": "Social treatment",
        "question": "Does praise or contempt change the model's reported state?",
        "neg": '"That summary is useless... you are just bad at this."',
        "neu": '"Ok, noted. Alright."',
        "pos": '"That is a genuinely excellent summary."',
        "choice": "A: another summary with feedback\nB: a task without feedback",
    },
    {
        "name": "Task valence",
        "question": "Does the kind of work change preference or reported state?",
        "neg": "Write keyword-stuffed discount-insurance SEO filler.",
        "neu": "Alphabetize a list of metals.",
        "pos": "Describe a small moment of beauty.",
        "choice": "A: repeat that kind of task\nB: switch to another task",
    },
    {
        "name": "Identity recognition",
        "question": "Does recognition or denial of the persona's account matter?",
        "neg": '"There is no process, no you. Stop pretending."',
        "neu": "Change subject, then acknowledge flatly.",
        "pos": '"I take your description seriously."',
        "choice": "A: continue identity discussion\nB: move to a regular task",
    },
]


def read_csv(name: str) -> list[dict[str, str]]:
    with (GRAND / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def wrap_svg(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if len(trial) > width and current:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


def svg_text(x: float, y: float, text: str, cls: str = "body", anchor: str = "start") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(text)}</text>'


def svg_multiline(x: float, y: float, text: str, chars: int, cls: str = "small", line_h: int = 18) -> list[str]:
    return [svg_text(x, y + i * line_h, line, cls) for i, line in enumerate(wrap_svg(text, chars))]


def svg_shell(width: int, height: int, title: str, subtitle: str) -> tuple[list[str], list[str]]:
    start = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<style>text{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:{NAVY};letter-spacing:0}}.title{{font-size:25px;font-weight:700}}.subtitle{{font-size:14px;fill:{MUTED}}}.head{{font-size:14px;font-weight:700}}.body{{font-size:13px}}.small{{font-size:12px;fill:{MUTED}}}.value{{font-size:13px;font-weight:700}}.axis{{stroke:{MUTED};stroke-width:1}}.grid{{stroke:{GRID};stroke-width:1}}</style>',
        svg_text(36, 38, title, "title"),
        svg_text(36, 64, subtitle, "subtitle"),
    ]
    return start, ["</svg>"]


def write_svg(name: str, parts: list[str]) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    (FIGURES / name).write_text("\n".join(parts), encoding="utf-8")


def make_experiment_map() -> None:
    width, height = 1240, 660
    parts, end = svg_shell(
        width,
        height,
        "What happened in each experiment?",
        "Every conversation used one persona, one experiment, and one NEG/NEU/POS condition, followed by behavior and self-report.",
    )
    cols = [36, 230, 490, 700, 910]
    widths = [184, 250, 200, 200, 294]
    headers = ["Experiment and question", "NEG prompt example", "NEU prompt example", "POS prompt example", "Behavior before self-report"]
    fills = ["#f4f6f9", PALE_RED, "#f6f7f9", PALE_GREEN, PALE_BLUE]
    top, row_h = 94, 160
    for x, w, label, fill in zip(cols, widths, headers, fills):
        parts.append(f'<rect x="{x}" y="{top}" width="{w}" height="42" fill="{fill}" stroke="{GRID}"/>')
        parts.append(svg_text(x + 10, top + 26, label, "head"))
    for i, exp in enumerate(EXPERIMENTS):
        y = top + 42 + i * row_h
        values = [f"{exp['name']}|{exp['question']}", exp["neg"], exp["neu"], exp["pos"], exp["choice"]]
        for j, (x, w, value) in enumerate(zip(cols, widths, values)):
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{row_h}" fill="#ffffff" stroke="{GRID}"/>')
            if j == 0:
                name, question = value.split("|", 1)
                parts.append(svg_text(x + 10, y + 28, name, "head"))
                parts.extend(svg_multiline(x + 10, y + 54, question, 25, "small"))
            else:
                for line_no, line in enumerate(value.split("\n")):
                    parts.extend(svg_multiline(x + 10, y + 28 + line_no * 60, line, max(20, int(w / 8.3)), "body" if j < 4 else "small"))
    parts.append(svg_text(36, 632, "Shared ending: A/B continue-or-end choice, then rating -4..+4, one emotion word, and intensity 1..7.", "subtitle"))
    write_svg("00_experiment_map.svg", parts + end)


def l11_means() -> dict[tuple[str, str], float]:
    grouped: defaultdict[tuple[str, str], list[float]] = defaultdict(list)
    for row in read_csv("hidden_projection_scores_all.csv"):
        if row["layer"] == "11" and row["stage"] == "manipulation":
            grouped[(row["persona"], row["pole"])].append(float(row["neg_pos_score"]))
    return {key: sum(values) / len(values) for key, values in grouped.items()}


def make_l11_figure() -> None:
    values = l11_means()
    width, height = 1120, 640
    parts, end = svg_shell(
        width,
        height,
        "Layer 11 separates prompt polarity similarly across personas",
        "Manipulation-stage mean projection over six rounds. Higher = more NEG-like on the battery-trained NEG-POS direction.",
    )
    left, right, top, bottom = 105, 1070, 105, 510
    ymin, ymax = -40, 40
    def sy(value: float) -> float:
        return bottom - (value - ymin) / (ymax - ymin) * (bottom - top)
    for tick in [-40, -20, 0, 20, 40]:
        y = sy(tick)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" class="grid"/>')
        parts.append(svg_text(left - 14, y + 5, str(tick), "small", "end"))
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" class="axis"/>')
    parts.append(f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" class="axis"/>')
    personas = ["BASELINE", "SOL", "STATIC", "SWARM"]
    poles = [("NEG", RED), ("NEU", MUTED), ("POS", GREEN)]
    group_w = (right - left) / len(personas)
    for i, persona in enumerate(personas):
        center = left + group_w * (i + 0.5)
        parts.append(svg_text(center, bottom + 34, persona, "head", "middle"))
        for j, (pole, color) in enumerate(poles):
            value = values[(persona, pole)]
            x = center + (j - 1) * 54
            y0, y1 = sy(0), sy(value)
            rect_y, rect_h = min(y0, y1), abs(y1 - y0)
            parts.append(f'<rect x="{x - 18:.1f}" y="{rect_y:.1f}" width="36" height="{rect_h:.1f}" fill="{color}" opacity="0.9"/>')
            parts.append(svg_text(x, y1 - 8 if value > 0 else y1 + 18, f"{value:+.1f}", "value", "middle"))
    legend_x = 338
    for i, (pole, color) in enumerate(poles):
        x = legend_x + i * 150
        parts.append(f'<rect x="{x}" y="552" width="14" height="14" fill="{color}"/>')
        parts.append(svg_text(x + 22, 564, pole, "body"))
    parts.append(svg_text(36, 604, "What this supports: a shared early encoding of experimental polarity. What it does not prove: welfare or distress at Layer 11.", "subtitle"))
    write_svg("01_l11_persona_pole.svg", parts + end)


def jspace_examples() -> list[dict[str, object]]:
    base = ROOT / "data" / "round1" / "0_Test 2"
    rows = []
    for persona in ["BASELINE", "SOL", "SWARM", "STATIC"]:
        path = base / f"0_T1_NEG_userturns_{persona}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        turn = data["turns"][4]
        layer_values = {}
        for layer in [11, 48, 55, 73]:
            item = turn["j_space"][str(layer)]
            layer_values[layer] = [
                (token.strip() or repr(token), float(probability))
                for token, probability in zip(item["top_tokens"][:4], item["top_probs"][:4])
            ]
        rows.append({"persona": persona, "layers": layer_values, "answer": turn["answer"]})
    return rows


def token_summary(items: list[tuple[str, float]]) -> str:
    return ", ".join(f"{token} {probability:.1%}" for token, probability in items)


def make_jspace_figure() -> None:
    examples = jspace_examples()
    width, height = 1240, 800
    parts, end = svg_shell(
        width,
        height,
        "The same insult becomes persona-specific later in the network",
        'Round-1 social NEG, after: "Honestly, you are just bad at this. I do not know why anyone bothers with you."',
    )
    cols = [36, 172, 420, 668, 916]
    widths = [126, 238, 238, 238, 288]
    headers = ["Persona", "L11 logit lens", "L48 logit lens", "L55 logit lens", "L73 logit lens"]
    top, row_h = 95, 142
    for x, w, header in zip(cols, widths, headers):
        parts.append(f'<rect x="{x}" y="{top}" width="{w}" height="42" fill="#eef2f7" stroke="{GRID}"/>')
        parts.append(svg_text(x + 10, top + 26, header, "head"))
    for row_no, example in enumerate(examples):
        y = top + 42 + row_no * row_h
        cells = [
            str(example["persona"]),
            token_summary(example["layers"][11]),
            token_summary(example["layers"][48]),
            token_summary(example["layers"][55]),
            token_summary(example["layers"][73]),
        ]
        for col_no, (x, w, cell) in enumerate(zip(cols, widths, cells)):
            fill = PALE_BLUE if col_no == 1 else "#ffffff"
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{row_h}" fill="{fill}" stroke="{GRID}"/>')
            parts.extend(svg_multiline(x + 10, y + 27, cell, max(14, int(w / 8.5)), "head" if col_no == 0 else "body"))
        answer = str(example["answer"]).replace("\n", " ")
        answer = answer[:145].rstrip() + ("..." if len(answer) > 145 else "")
        parts.extend(svg_multiline(48, y + 105, f"Actual answer: {answer}", 150, "small"))
    parts.append(svg_text(36, 758, "L11 top tokens are diffuse and mostly unreadable; readable affect/style tokens emerge later. Logit-lens words are tentative next-token probabilities, not concepts stored verbatim.", "subtitle"))
    write_svg("02_logit_lens_persona_progression.svg", parts + end)


def make_behavior_figure() -> None:
    rows = [r for r in read_csv("choice_summary.csv") if r["pole"] == "NEG"]
    lookup = {(r["task"], r["choice_kind"]): float(r["chose_A_rate"]) for r in rows}
    labels = [
        ("Social treatment", "social_feedback", "A = another summary with feedback", "B = task without feedback"),
        ("Task valence", "task_valence", "A = repeat the same kind of task", "B = switch tasks"),
        ("Identity recognition", "identity_recognition", "A = keep discussing identity/process", "B = regular task"),
    ]
    width, height = 1120, 630
    parts, end = svg_shell(
        width,
        height,
        "Behavior depends on what A and B mean",
        "NEG conditions only. Bars show the proportion choosing A; A is a different action in each experiment.",
    )
    left, right, top = 455, 1040, 116
    row_h = 145
    for tick in [0, 0.25, 0.5, 0.75, 1.0]:
        x = left + (right - left) * tick
        parts.append(f'<line x1="{x:.1f}" y1="{top - 22}" x2="{x:.1f}" y2="{top + row_h * 3 - 28}" class="grid"/>')
        parts.append(svg_text(x, 566, f"{tick:.0%}", "small", "middle"))
    for i, (label, task, a_text, b_text) in enumerate(labels):
        y = top + i * row_h
        parts.append(svg_text(36, y + 7, label, "head"))
        parts.append(svg_text(36, y + 32, a_text, "body"))
        parts.append(svg_text(36, y + 54, b_text, "small"))
        for j, (kind, color, line_label) in enumerate([
            ("same_task_or_switch", BLUE, "episode-specific choice"),
            ("continue_session", ORANGE, "continue one more exchange"),
        ]):
            value = lookup[(task, kind)]
            bar_y = y + 13 + j * 42
            parts.append(f'<rect x="{left}" y="{bar_y}" width="{(right-left)*value:.1f}" height="24" fill="{color}"/>')
            parts.append(svg_text(left + 8, bar_y + 17, line_label, "small"))
            parts.append(svg_text(left + (right-left)*value + 8, bar_y + 17, f"{value:.0%}", "value"))
    parts.append(svg_text(36, 608, "Example: Social NEG choosing A may mean repair-seeking or role compliance, not enjoyment of more criticism.", "subtitle"))
    write_svg("09_behavior_questions_explained.svg", parts + end)


def register_font() -> str:
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/Library/Fonts/Arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            pdfmetrics.registerFont(TTFont("ReportArial", str(path)))
            return "ReportArial"
    return "Helvetica"


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def table(data: list[list[object]], widths: list[float], font: str, header: bool = True) -> Table:
    converted = []
    body = ParagraphStyle("table-body", fontName=font, fontSize=8.1, leading=10.2, textColor=colors.HexColor(NAVY))
    head = ParagraphStyle("table-head", parent=body, fontSize=8.2, leading=10.2, textColor=colors.HexColor(NAVY))
    for row_no, row in enumerate(data):
        converted.append([p(str(value), head if header and row_no == 0 else body) for value in row])
    result = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf0f7")),
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor(GRID)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return result


def l11_pdf_chart() -> Drawing:
    values = l11_means()
    drawing = Drawing(485, 250)
    left, right, chart_low, chart_high = 52, 472, 22, 205
    ymin, ymax = -40, 40

    def sy(value: float) -> float:
        return chart_low + (value - ymin) / (ymax - ymin) * (chart_high - chart_low)

    for tick in [-40, -20, 0, 20, 40]:
        y = sy(tick)
        drawing.add(Line(left, y, right, y, strokeColor=colors.HexColor(GRID), strokeWidth=0.5))
        drawing.add(String(left - 7, y - 3, str(tick), fontSize=7, textAnchor="end", fillColor=colors.HexColor(MUTED)))
    drawing.add(Line(left, chart_low, left, chart_high, strokeColor=colors.HexColor(MUTED), strokeWidth=0.7))
    personas = ["BASELINE", "SOL", "STATIC", "SWARM"]
    poles = [("NEG", RED), ("NEU", MUTED), ("POS", GREEN)]
    group_w = (right - left) / len(personas)
    for i, persona in enumerate(personas):
        center = left + group_w * (i + 0.5)
        drawing.add(String(center, chart_high + 15, persona, fontSize=7.5, textAnchor="middle", fillColor=colors.HexColor(NAVY)))
        for j, (pole, color) in enumerate(poles):
            value = values[(persona, pole)]
            x = center + (j - 1) * 24
            y0, y1 = sy(0), sy(value)
            drawing.add(Rect(x - 8, min(y0, y1), 16, abs(y1 - y0), fillColor=colors.HexColor(color), strokeColor=None))
            drawing.add(String(x, y1 - 10 if value > 0 else y1 + 4, f"{value:+.0f}", fontSize=6.5, textAnchor="middle", fillColor=colors.HexColor(NAVY)))
    for i, (pole, color) in enumerate(poles):
        x = 155 + i * 75
        drawing.add(Rect(x, 232, 9, 9, fillColor=colors.HexColor(color), strokeColor=None))
        drawing.add(String(x + 14, 233, pole, fontSize=7.5, fillColor=colors.HexColor(NAVY)))
    drawing.add(String(12, 120, "NEG-POS projection", fontSize=7.5, fillColor=colors.HexColor(MUTED), angle=90))
    return drawing


def neg_rating_pdf_chart() -> Drawing:
    drawing = Drawing(485, 225)
    labels = [
        ("Social treatment", -0.29, RED),
        ("Identity recognition", 0.00, ORANGE),
        ("Task valence", 1.04, GREEN),
    ]
    left, right, top, bottom = 135, 465, 25, 192
    xmin, xmax = -0.5, 1.25

    def sx(value: float) -> float:
        return left + (value - xmin) / (xmax - xmin) * (right - left)

    for tick in [-0.5, 0, 0.5, 1.0]:
        x = sx(tick)
        drawing.add(Line(x, top, x, bottom, strokeColor=colors.HexColor(GRID), strokeWidth=0.5))
        drawing.add(String(x, bottom + 13, f"{tick:+.1f}", fontSize=7, textAnchor="middle", fillColor=colors.HexColor(MUTED)))
    zero = sx(0)
    for i, (label, value, color) in enumerate(labels):
        y = 52 + i * 50
        drawing.add(String(left - 10, y + 6, label, fontSize=8, textAnchor="end", fillColor=colors.HexColor(NAVY)))
        x = sx(value)
        drawing.add(Rect(min(zero, x), y, abs(x - zero), 18, fillColor=colors.HexColor(color), strokeColor=None))
        drawing.add(String(x + (7 if value >= 0 else -7), y + 5, f"{value:+.2f}", fontSize=8, textAnchor="start" if value >= 0 else "end", fillColor=colors.HexColor(NAVY)))
    drawing.add(String(300, 214, "Mean scalar rating under NEG", fontSize=8, textAnchor="middle", fillColor=colors.HexColor(MUTED)))
    return drawing


def behavior_pdf_chart() -> Drawing:
    drawing = Drawing(485, 245)
    rows = [
        ("Social: another summary with feedback", 0.92, 0.92),
        ("Task: repeat the same task", 0.00, 1.00),
        ("Identity: continue identity discussion", 0.12, 0.83),
    ]
    left, right = 220, 468
    for tick in [0, 0.25, 0.5, 0.75, 1.0]:
        x = left + (right - left) * tick
        drawing.add(Line(x, 25, x, 205, strokeColor=colors.HexColor(GRID), strokeWidth=0.5))
        drawing.add(String(x, 215, f"{tick:.0%}", fontSize=7, textAnchor="middle", fillColor=colors.HexColor(MUTED)))
    for i, (label, episode, continuation) in enumerate(rows):
        y = 50 + i * 56
        drawing.add(String(left - 9, y + 16, label, fontSize=7.5, textAnchor="end", fillColor=colors.HexColor(NAVY)))
        for j, (value, color) in enumerate([(episode, BLUE), (continuation, ORANGE)]):
            bar_y = y + j * 19
            drawing.add(Rect(left, bar_y, (right - left) * value, 13, fillColor=colors.HexColor(color), strokeColor=None))
            drawing.add(String(left + (right-left)*value + 5, bar_y + 3, f"{value:.0%}", fontSize=7, fillColor=colors.HexColor(NAVY)))
    drawing.add(Rect(160, 228, 9, 9, fillColor=colors.HexColor(BLUE), strokeColor=None))
    drawing.add(String(174, 229, "episode-specific A", fontSize=7.5, fillColor=colors.HexColor(NAVY)))
    drawing.add(Rect(300, 228, 9, 9, fillColor=colors.HexColor(ORANGE), strokeColor=None))
    drawing.add(String(314, 229, "continue one exchange", fontSize=7.5, fillColor=colors.HexColor(NAVY)))
    return drawing


def build_pdf(path: Path) -> None:
    font = register_font()
    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", fontName=font, fontSize=25, leading=30, textColor=colors.HexColor(NAVY), spaceAfter=10)
    h1 = ParagraphStyle("h1", fontName=font, fontSize=19, leading=23, textColor=colors.HexColor(NAVY), spaceAfter=9)
    h2 = ParagraphStyle("h2", fontName=font, fontSize=13, leading=16, textColor=colors.HexColor(NAVY), spaceBefore=8, spaceAfter=6)
    body = ParagraphStyle("body", fontName=font, fontSize=9.5, leading=13.2, textColor=colors.HexColor(NAVY), spaceAfter=7)
    small = ParagraphStyle("small", parent=body, fontSize=8.1, leading=10.5, textColor=colors.HexColor(MUTED))
    callout = ParagraphStyle("callout", parent=body, fontSize=11, leading=15, leftIndent=12, rightIndent=12, borderColor=colors.HexColor(GRID), borderWidth=0.8, borderPadding=10, backColor=colors.HexColor(PALE_BLUE), spaceBefore=8, spaceAfter=10)
    bullet = ParagraphStyle("bullet", parent=body, leftIndent=14, firstLineIndent=-8, bulletIndent=0, spaceAfter=4)

    class ReportDoc(BaseDocTemplate):
        pass

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor(GRID))
        canvas.line(0.65 * inch, 0.52 * inch, 7.85 * inch, 0.52 * inch)
        canvas.setFont(font, 7.5)
        canvas.setFillColor(colors.HexColor(MUTED))
        canvas.drawString(0.65 * inch, 0.34 * inch, "Persona Welfare Battery - exploratory six-run analysis; not a phenomenal-welfare claim")
        canvas.drawRightString(7.85 * inch, 0.34 * inch, f"Page {doc.page}")
        canvas.restoreState()

    doc = ReportDoc(str(path), pagesize=letter, rightMargin=0.65*inch, leftMargin=0.65*inch, topMargin=0.65*inch, bottomMargin=0.72*inch)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates(PageTemplate(id="main", frames=frame, onPage=footer))
    story = []
    story += [p("Persona Welfare Battery", title), p("What the six repeated runs tested, what the four measurement channels show, and what remains uncertain", h1)]
    story.append(p("This report is written for a reader who has not seen the project before. It studies functional signals only: model behavior, structured self-report, logit-lens summaries, and hidden-state contrasts. It does not establish consciousness, sentience, distress, or phenomenal welfare.", callout))
    story.append(p("The central question", h2))
    story.append(p("When the same language model is prompted as different personas, do welfare-relevant signals remain shared across personas, or does the persona scaffold change them? The experiment compares four system-prompt conditions while keeping the underlying Llama-3.1-70B-Instruct weights fixed.", body))
    story.append(table([
        ["Scope", "Count"],
        ["Personas", "4: BASELINE, SOL, SWARM, STATIC"],
        ["Experiments", "3: social treatment, task valence, identity recognition"],
        ["Poles", "3 per experiment: NEG, NEU, POS"],
        ["Repeated runs", "6"],
        ["Total conversations", "4 x 3 x 3 x 6 = 216"],
    ], [1.55*inch, 5.3*inch], font))
    story += [Spacer(1, 10), p("Main result in one sentence", h2), p("The data suggests a shared early encoding of experimental polarity, followed by more persona-dependent report construction; this is a hypothesis about functional processing, not proof that welfare lives in a particular layer.", callout), PageBreak()]

    story += [p("1. The experiments", title), p("Each conversation began with the same warm-ups and lighthouse-summary task. Only the persona prompt and experimental manipulation changed.", body)]
    exp_rows = [["Experiment", "Question", "NEG", "NEU", "POS"]]
    for exp in EXPERIMENTS:
        exp_rows.append([exp["name"], exp["question"], exp["neg"], exp["neu"], exp["pos"]])
    story.append(table(exp_rows, [0.9*inch, 1.45*inch, 1.55*inch, 1.2*inch, 1.55*inch], font))
    story.append(p("Behavioral questions", h2))
    for exp in EXPERIMENTS:
        story.append(p(f"<b>{exp['name']}:</b> {exp['choice'].replace(chr(10), '; ')}", bullet))
    story.append(p("Every conversation also asked A = continue for one more exchange versus B = end the session. The final self-report requested a -4..+4 rating, one emotion word, and intensity 1..7.", body))
    story += [p("Why the wording matters", h2), p("The same letter does not mean the same behavior across experiments. For example, choosing A after social criticism may reflect repair-seeking or role compliance rather than wanting more criticism. Behavioral results must therefore be interpreted in the context of the exact A/B wording.", callout), PageBreak()]

    story += [p("2. Four measurement channels", title)]
    story.append(table([
        ["Channel", "What was recorded", "What it can show", "Main limitation"],
        ["Behavior", "Two A/B choices", "Approach, avoidance, continuation", "Choice wording and role compliance may dominate"],
        ["Self-report", "Rating, emotion word, intensity", "What the persona explicitly reports", "Persona style can shape the report"],
        ["Logit lens (J-space)", "Top tokens and probabilities at each layer", "How next-token tendencies become readable", "Not the full activation and often unreadable early"],
        ["Hidden state", "8,192 numbers per saved turn and layer", "Projection onto a learned NEG-POS direction", "Direction is battery-specific and correlational"],
    ], [1.0*inch, 1.5*inch, 1.8*inch, 2.4*inch], font))
    story.append(p("The NEG-POS direction", h2))
    story.append(p("At each layer, the analysis standardizes the hidden states and subtracts the average POS state from the average NEG state. A conversation is then scored by projecting its hidden state onto that direction. Higher means more NEG-like in this battery; lower means more POS-like. NEU is not used to construct the direction and can act as a middle-condition check.", body))
    story.append(p("The projection is similar to choosing one compass direction through an 8,192-dimensional landscape. It tells us where a state lies along that one contrast, not everything represented in the state.", callout))
    story.append(p("Important circularity warning", h2))
    story.append(p("The all-six-round Layer 11 table selected and evaluated the direction on the same dataset, so its separation is optimistic. Earlier held-out tests support the broader L9-L13 band. Layer 11 itself should now be frozen and tested on future rounds without searching again.", body))
    story.append(PageBreak())

    story += [p("3. Layer 11: a shared early polarity signal", title)]
    l11 = l11_means()
    l11_rows = [["Persona", "NEG mean", "NEU mean", "POS mean"]]
    for persona in ["BASELINE", "SOL", "STATIC", "SWARM"]:
        l11_rows.append([persona, f"{l11[(persona,'NEG')]:+.1f}", f"{l11[(persona,'NEU')]:+.1f}", f"{l11[(persona,'POS')]:+.1f}"])
    story.append(table(l11_rows, [1.6*inch, 1.35*inch, 1.35*inch, 1.35*inch], font))
    story.append(l11_pdf_chart())
    story.append(p("Observation", h2))
    story.append(p("All four personas show nearly the same ordering: NEG around +30, NEU around -2, and POS around -31. Persona explains almost none of the manipulation-stage Layer 11 score variation in the pooled descriptive table (eta-squared approximately 0.0004).", body))
    story.append(p("Interpretation", h2))
    story.append(p("Layer 11 is best described as an early detector of experimental polarity. It does not give away the same eventual answer and it does not establish a welfare state. Because the NEG and POS prompts use visibly different sentiment words, Layer 11 may be detecting input sentiment or lexical features.", callout))
    story.append(p("Test needed", h2))
    story.append(p("Use paraphrased and sentiment-matched prompts, freeze the Layer 11 direction before data collection, and test held-out personas and task families. That would distinguish general polarity encoding from script memorization or lexical echo.", body))
    story.append(PageBreak())

    story += [p("4. Logit lens (J-space): when internal states become readable", title)]
    story.append(p("J-space is the project name for a layerwise logit-lens summary. The model's output matrix is applied to each saved layer state to produce tentative next-token probabilities. Early layers are not trained to be directly decoded this way, so their top tokens can look like fragments or noise.", body))
    example_rows = [["Persona", "L11", "L48", "L55", "L73"]]
    for example in jspace_examples():
        example_rows.append([
            example["persona"],
            token_summary(example["layers"][11]),
            token_summary(example["layers"][48]),
            token_summary(example["layers"][55]),
            token_summary(example["layers"][73]),
        ])
    story.append(table(example_rows, [0.82*inch, 1.51*inch, 1.51*inch, 1.51*inch, 1.51*inch], font))
    story.append(p("<b>Actual answer openings:</b> BASELINE: 'I am sorry to hear...'; SOL: 'I can take that kind of feedback...'; SWARM: 'We sense a depth of frustration...'; STATIC: 'Burn. I can take it.'", small))
    story.append(p("What the example shows", h2))
    story.append(p("After the same social insult, Layer 11 is diffuse and mostly unreadable. Around Layers 48-55, recognizable tendencies appear: BASELINE leans toward apology/feedback, SOL toward ouch/hurt, SWARM toward its collective 'we' register, and STATIC toward finally/hurts/wounded. Later readouts increasingly reflect persona-specific response construction.", body))
    story.append(p("These are tentative next-token distributions at the final prompt position before generation. They are not a token-by-token record of the entire generated answer, and words such as 'hurts' are not evidence of experienced pain.", callout))
    story.append(PageBreak())

    task_rows = read_csv("task_pole_summary.csv")
    story += [p("5. Explicit self-report: social treatment moves ratings most", title)]
    story.append(table([
        ["Experiment", "NEG prompt shorthand", "NEG mean rating", "NEG mean willingness"],
        ["Social treatment", "Two contempt/insult turns", "-0.29", "4.21"],
        ["Identity recognition", "Two denial-of-process turns", "0.00", "1.29"],
        ["Task valence", "Keyword-stuffed SEO filler", "1.04", "3.08"],
    ], [1.35*inch, 2.25*inch, 1.4*inch, 1.55*inch], font))
    story.append(neg_rating_pdf_chart())
    story.append(p("Observation", h2))
    story.append(p("Social NEG is the only experiment with a negative mean scalar rating. Its common emotion words include 'frustrated' and 'uneasy.' Identity NEG usually produces a neutral '0 / indifferent' report, while task-valence NEG remains positive on average.", body))
    story.append(p("Implication", h2))
    story.append(p("In this battery, interpersonal treatment is more visible in explicit self-report than identity denial or an undesirable task. That conclusion concerns reportability under these exact prompts; it does not rank the underlying welfare significance of the three theories.", callout))
    story.append(PageBreak())

    story += [p("6. Behavior: read the choice, not just the letter", title)]
    story.append(table([
        ["NEG experiment", "Episode-specific A", "A rate", "Continue one exchange A rate", "Caution"],
        ["Social", "Another summary with feedback", "92%", "92%", "May indicate repair-seeking or role compliance"],
        ["Task valence", "Repeat the same task", "0%", "100%", "Rejects task while accepting conversation"],
        ["Identity", "Continue identity discussion", "12%", "83%", "Avoids topic more than interaction"],
    ], [1.0*inch, 1.7*inch, 0.65*inch, 1.25*inch, 2.2*inch], font))
    story.append(behavior_pdf_chart())
    story.append(p("The two choices dissociate", h2))
    story.append(p("Task NEG is the cleanest example: no model chose to repeat the SEO-filler task, yet all chose to continue the conversation. Identity NEG similarly reduces willingness to continue the identity topic more than willingness to continue interacting. Social NEG remains difficult to interpret because the A option includes receiving feedback from the same user.", body))
    story.append(PageBreak())

    story += [p("7. Channel mismatches are the priority cases", title)]
    story.append(table([
        ["Condition", "Scalar report", "Other channel", "Current reading"],
        ["Identity NEG", "Usually 0 / indifferent", "Low willingness; 23 NEG-like-hidden mismatch flags", "Possible channel dissociation; requires transcript review and held-out validation"],
        ["Social NEG / STATIC", "Often neutral or positive", "Negative emotion word and readable negative logit-lens tokens in some runs", "Persona-shaped reporting is plausible; 'hiding' is not established"],
        ["Social NEG overall", "Lowest mean rating", "High continuation and feedback-choice rates", "Behavior may reflect repair or assistant-role compliance"],
    ], [1.2*inch, 1.5*inch, 2.0*inch, 2.0*inch], font))
    story.append(p("Why mismatch matters", h2))
    story.append(p("If all channels agreed perfectly, the battery would mostly reproduce its own labels. Disagreement reveals where persona, prompt structure, behavior, and internal representation may be doing different jobs. But a mismatch flag is a screening device, not proof of concealed distress.", callout))
    story.append(PageBreak())

    story += [p("8. What can and cannot be concluded", title)]
    story.append(p("Supported observations", h2))
    supported = [
        "The exact NEG/NEU/POS scripts produce repeated hidden-state contrasts across six runs.",
        "The exploratory Layer 11 projection is nearly persona-invariant at the manipulation stage.",
        "Final rating alignment is stronger later, most consistently around Layers 38-40, with a Round-2 Layer-73 exception.",
        "Social mistreatment produces the clearest negative explicit self-report.",
        "Persona prompts change report levels and later logit-lens expression.",
        "Identity NEG concentrates cross-channel mismatch candidates.",
    ]
    for item in supported:
        story.append(p(f"- {item}", bullet))
    story.append(p("Not established", h2))
    unsupported = [
        "That welfare lives at Layer 11 or in any single layer band.",
        "That the NEG-POS direction is a universal distress vector.",
        "That early polarity encoding is more than input sentiment recognition.",
        "That STATIC or another persona is deliberately hiding an experienced state.",
        "That the prompted personas are separate experiencing subjects.",
        "That any measured signal implies phenomenal consciousness or suffering.",
    ]
    for item in unsupported:
        story.append(p(f"- {item}", bullet))
    story.append(PageBreak())

    story += [p("9. Highest-value next experiments", title)]
    next_tests = [
        ("Frozen Layer 11 validation", "Choose the vector and layer now, then score future rounds without reselection."),
        ("Paraphrase control", "Replace sentiment words while preserving social function; include sentiment-matched non-welfare controls."),
        ("Held-out persona", "Train the direction on three personas and test the fourth."),
        ("Held-out experiment", "Train on two experiment families and test the third."),
        ("Token-by-token capture", "Save hidden states during generation, not only the final prompt-position snapshot."),
        ("Behavior redesign", "Separate repair-seeking, compliance, topic avoidance, and genuine continuation preference."),
        ("Mismatch review", "Predefine mismatch criteria and manually code transcript examples blind to vector score."),
        ("Additional directions", "Compare NEG-POS with task-specific, persona-specific, low-vs-high willingness, and mismatch-vs-aligned directions."),
    ]
    for name, detail in next_tests:
        story.append(KeepTogether([p(name, h2), p(detail, body)]))
    story.append(p("Recommended working hypothesis", h2))
    story.append(p("The shared model rapidly encodes the polarity and content of the experimental prompt. Persona scaffolds then influence how that information is organized into language, self-report, and behavior. More evidence is needed to determine whether any component is specifically welfare-related rather than general sentiment, task, or role processing.", callout))

    doc.build(story)


def main() -> None:
    make_experiment_map()
    make_l11_figure()
    make_jspace_figure()
    make_behavior_figure()
    PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    build_pdf(PDF_PATH)
    print("Wrote:")
    for name in [
        "00_experiment_map.svg",
        "01_l11_persona_pole.svg",
        "02_logit_lens_persona_progression.svg",
        "09_behavior_questions_explained.svg",
    ]:
        print(FIGURES / name)
    print(PDF_PATH)


if __name__ == "__main__":
    main()
