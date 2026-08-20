#!/usr/bin/env python3
"""
SignalDesk weekly health check.

Run:
    python3 health_check.py
"""
import csv
from pathlib import Path

HERE = Path(__file__).parent
DATA_PATH = HERE / "sample-data" / "product_usage_events.csv"
OUTPUT_DIR = HERE / "output"
PROMPT_START = "2026-08-04"
WORKFLOWS = ("Lead summary", "Reply draft", "Feedback clustering")


def load_rows(path):
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            team_raw = raw["team"].strip()
            conf_raw = (raw["median_confidence"] or "").strip()
            rating_raw = (raw["user_rating"] or "").strip()

            try:
                confidence = float(conf_raw)
            except ValueError:
                confidence = None

            rating = float(rating_raw) if rating_raw else None

            rows.append({
                "date": raw["date"],
                "team_raw": team_raw,
                "team": team_raw.title(),
                "workflow": raw["workflow"],
                "source": raw["source"],
                "sessions": int(raw["sessions"]),
                "completed": int(raw["completed"]),
                "accepted": int(raw["accepted_output"]),
                "flagged": int(raw["flagged_for_review"]),
                "minutes": float(raw["avg_minutes_saved"]),
                "confidence": confidence,
                "confidence_raw": conf_raw,
                "rating": rating,
                "notes": raw["notes"] or "",
            })
    return rows


def issues(row):
    labels = []
    note = row["notes"].lower()
    if row["rating"] is None:
        labels.append("missing user rating")
    if row["team_raw"] != row["team_raw"].title():
        labels.append("team label casing differs")
    if "demo account" in note:
        labels.append("demo-account traffic spike")
    if "duplicate export row" in note:
        labels.append("duplicate export row")
    if row["confidence"] is None and row["confidence_raw"]:
        labels.append(f"confidence stored as text {row['confidence_raw']}")
    if "review policy changed" in note:
        labels.append("review policy changed mid-day")
    return labels


def should_drop(row):
    note = row["notes"].lower()
    return "demo account" in note or "duplicate export row" in note


def summarize(rows):
    sessions = completed = accepted = flagged = 0
    minutes_sum = 0.0
    rating_sum = 0.0
    rating_weight = 0

    for row in rows:
        sessions += row["sessions"]
        completed += row["completed"]
        accepted += row["accepted"]
        flagged += row["flagged"]
        minutes_sum += row["minutes"] * row["completed"]
        if row["rating"] is not None:
            rating_sum += row["rating"] * row["completed"]
            rating_weight += row["completed"]

    return {
        "sessions": sessions,
        "completion": (completed / sessions) if sessions else None,
        "accept": (accepted / completed) if completed else None,
        "flag": (flagged / completed) if completed else None,
        "minutes": (minutes_sum / completed) if completed else None,
        "rating": (rating_sum / rating_weight) if rating_weight else None,
    }


def pct(value):
    return "n/a" if value is None else f"{value:.0%}"


def num(value, digits=2):
    return "n/a" if value is None else f"{value:.{digits}f}"


def build_brief(rows):
    clean = [row for row in rows if not should_drop(row)]
    start = min(row["date"] for row in rows)
    end = max(row["date"] for row in rows)

    by_workflow = {}
    for name in WORKFLOWS:
        by_workflow[name] = summarize(r for r in clean if r["workflow"] == name)

    lead_email = summarize(
        r for r in clean if r["workflow"] == "Lead summary" and r["source"] == "email"
    )
    lead_before = summarize(
        r for r in clean if r["workflow"] == "Lead summary" and r["date"] < PROMPT_START
    )
    lead_after = summarize(
        r for r in clean if r["workflow"] == "Lead summary" and r["date"] >= PROMPT_START
    )
    policy = next(r for r in rows if "review policy changed" in r["notes"].lower())
    feedback = by_workflow["Feedback clustering"]

    lines = [
        "SIGNALDESK WEEKLY HEALTH CHECK",
        f"{start} to {end}  |  {len(rows)} rows, {len(rows) - len(clean)} dropped from totals",
        "=" * 72,
        "",
        "RECOMMENDATION",
        "  Do not roll out more broadly yet.",
        "  Investigate the 7 Aug Support review-policy change first.",
        "  Lead summary (email) is the strongest clean signal so far.",
        "  Do not use the 5 Aug Sales email demo rows or median_confidence",
        "  as primary success metrics.",
        "",
        "WHAT IS WORKING",
        f"  Lead summary / email — accept {pct(lead_email['accept'])}, "
        f"flag {pct(lead_email['flag'])}, rating {num(lead_email['rating'])}.",
        "  After the 4 Aug prompt start (demo rows excluded): Lead summary accept "
        f"{pct(lead_before['accept'])} → {pct(lead_after['accept'])}. "
        "Descriptive only, not proof of impact.",
        "",
        "WHAT LOOKS SUSPICIOUS",
        "  • 5 Aug Lead summary email: demo spike (140 sessions) + duplicate row.",
        f"  • 7 Aug Reply draft queue: rating {num(policy['rating'], 1)}, "
        f"confidence {num(policy['confidence'])}, "
        f"flag {pct(policy['flagged'] / policy['completed'] if policy['completed'] else None)} "
        "— review policy changed mid-day.",
        f"  • Feedback clustering: highest estimated minutes ({num(feedback['minutes'], 1)}) "
        f"but weakest accept ({pct(feedback['accept'])}) on lower volume.",
        "",
        "METRIC TO TRUST LEAST",
        "  median_confidence — model self-report, not human quality.",
        "  On 7 Aug it was high while the user rating crashed.",
        "",
        "LOOK AT NEXT",
        "  1. What exactly changed in Support review policy on 7 Aug?",
        "  2. Filter demo/test accounts out of exports.",
        "  3. Weekly: accept rate + user rating by workflow + source (never blended).",
        "",
        "DATA QUALITY FLAGS",
    ]

    for row in rows:
        labels = issues(row)
        if not labels:
            continue
        marker = "  ← kept visible, not dropped" if "review policy changed mid-day" in labels else ""
        lines.append(
            f"  {row['date']}  {row['team']}/{row['workflow']}/{row['source']}  "
            f"[{', '.join(labels)}]{marker}"
        )

    lines.extend([
        "",
        "WORKFLOW HEALTH (demo + duplicate excluded)",
        "  Rates: completion = completed/sessions; accept and flag = count/completed.",
    ])
    for name in WORKFLOWS:
        s = by_workflow[name]
        lines.append(
            f"  {name:<22} sessions {s['sessions']:>3}  "
            f"complete {pct(s['completion']):>3}  "
            f"accept {pct(s['accept']):>3}  "
            f"flag {pct(s['flag']):>3}  "
            f"min {num(s['minutes'], 1):>4}  rating {num(s['rating'])}"
        )
    lines.append("")
    return "\n".join(lines), by_workflow


def write_chart(by_workflow, path):
    """
    Simple SVG grouped bar chart: accept rate vs flag rate by workflow.
    No extra packages.
    """
    width, height = 720, 380
    left, right, top, bottom = 70, 40, 50, 70
    plot_w = width - left - right
    plot_h = height - top - bottom
    group_w = plot_w / len(WORKFLOWS)
    bar_w = group_w * 0.28

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fffdf8"/>',
        '<text x="36" y="28" font-family="Helvetica, Arial, sans-serif" font-size="16" '
        'fill="#1f1c16">Workflow health after dropping demo + duplicate rows</text>',
        '<text x="36" y="46" font-family="Helvetica, Arial, sans-serif" font-size="11" '
        'fill="#5f584c">Accept rate and flag rate use completed sessions as the denominator</text>',
        # axes
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" '
        'stroke="#5f584c" stroke-width="1"/>',
        f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" '
        'stroke="#5f584c" stroke-width="1"/>',
    ]

    for frac, label in ((0, "0%"), (0.25, "25%"), (0.5, "50%"), (0.75, "75%"), (1, "100%")):
        y = top + plot_h - frac * plot_h
        parts.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" '
            'stroke="#ddd6c8" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{left - 8}" y="{y + 4:.1f}" text-anchor="end" '
            'font-family="Helvetica, Arial, sans-serif" font-size="11" '
            f'fill="#5f584c">{label}</text>'
        )

    for i, name in enumerate(WORKFLOWS):
        stats = by_workflow[name]
        accept = stats["accept"] or 0
        flag = stats["flag"] or 0
        cx = left + (i + 0.5) * group_w
        accept_h = accept * plot_h
        flag_h = flag * plot_h
        ax = cx - bar_w - 4
        fx = cx + 4
        ay = top + plot_h - accept_h
        fy = top + plot_h - flag_h

        parts.append(
            f'<rect x="{ax:.1f}" y="{ay:.1f}" width="{bar_w:.1f}" height="{accept_h:.1f}" '
            'fill="#215c3a"/>'
        )
        parts.append(
            f'<rect x="{fx:.1f}" y="{fy:.1f}" width="{bar_w:.1f}" height="{flag_h:.1f}" '
            'fill="#8a4b00"/>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{top + plot_h + 22}" text-anchor="middle" '
            'font-family="Helvetica, Arial, sans-serif" font-size="12" '
            f'fill="#1f1c16">{name}</text>'
        )
        parts.append(
            f'<text x="{ax + bar_w / 2:.1f}" y="{ay - 6:.1f}" text-anchor="middle" '
            'font-family="Helvetica, Arial, sans-serif" font-size="11" '
            f'fill="#215c3a">{accept:.0%}</text>'
        )
        parts.append(
            f'<text x="{fx + bar_w / 2:.1f}" y="{fy - 6:.1f}" text-anchor="middle" '
            'font-family="Helvetica, Arial, sans-serif" font-size="11" '
            f'fill="#8a4b00">{flag:.0%}</text>'
        )

    # legend
    parts.append('<rect x="520" y="18" width="12" height="12" fill="#215c3a"/>')
    parts.append(
        '<text x="538" y="28" font-family="Helvetica, Arial, sans-serif" font-size="12" '
        'fill="#1f1c16">Accept rate</text>'
    )
    parts.append('<rect x="620" y="18" width="12" height="12" fill="#8a4b00"/>')
    parts.append(
        '<text x="638" y="28" font-family="Helvetica, Arial, sans-serif" font-size="12" '
        'fill="#1f1c16">Flag rate</text>'
    )
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main():
    if not DATA_PATH.exists():
        raise SystemExit(f"Missing data file: {DATA_PATH}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    brief, by_workflow = build_brief(load_rows(DATA_PATH))
    print(brief)

    brief_path = OUTPUT_DIR / "health_check_output.txt"
    chart_path = OUTPUT_DIR / "workflow_rates.svg"
    brief_path.write_text(brief + "\n", encoding="utf-8")
    write_chart(by_workflow, chart_path)

    print(f"Wrote {brief_path}")
    print(f"Wrote {chart_path}")
    print(f"Optional: add your terminal screenshot as {OUTPUT_DIR / 'terminal_screenshot.png'}")


if __name__ == "__main__":
    main()
