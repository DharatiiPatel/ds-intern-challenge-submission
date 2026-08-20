#!/usr/bin/env python3
"""
SignalDesk weekly health check.

Run:
    python3 health_check.py
"""

import csv
from pathlib import Path

DATA_PATH = Path(__file__).parent / "sample-data" / "product_usage_events.csv"
PROMPT_START = "2026-08-04"

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
    # Demo traffic and the known duplicate should not drive health totals.
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
        # No rater count in the export; weight daily ratings by completed.
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

def print_brief(rows):
    clean = [row for row in rows if not should_drop(row)]
    start = min(row["date"] for row in rows)
    end = max(row["date"] for row in rows)

    by_workflow = {}
    for name in ("Lead summary", "Reply draft", "Feedback clustering"):
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

    print()
    print("SIGNALDESK WEEKLY HEALTH CHECK")
    print(f"{start} to {end}  |  {len(rows)} rows, {len(rows) - len(clean)} dropped from totals")
    print("=" * 72)

    print()
    print("RECOMMENDATION")
    print("  Do not roll out more broadly yet.")
    print("  Investigate the 7 Aug Support review-policy change first.")
    print("  Lead summary (email) is the strongest clean signal so far.")
    print("  Do not use the 5 Aug Sales email demo rows or median_confidence")
    print("  as primary success metrics.")

    print()
    print("WHAT IS WORKING")
    print(
        f"  Lead summary / email — accept {pct(lead_email['accept'])}, "
        f"flag {pct(lead_email['flag'])}, rating {num(lead_email['rating'])}."
    )
    print(
        "  After the 4 Aug prompt start (demo rows excluded): Lead summary accept "
        f"{pct(lead_before['accept'])} → {pct(lead_after['accept'])}. "
        "Descriptive only, not proof of impact."
    )

    print()
    print("WHAT LOOKS SUSPICIOUS")
    print("  • 5 Aug Lead summary email: demo spike (140 sessions) + duplicate row.")
    print(
        f"  • 7 Aug Reply draft queue: rating {num(policy['rating'], 1)}, "
        f"confidence {num(policy['confidence'])}, "
        f"flag {pct(policy['flagged'] / policy['completed'] if policy['completed'] else None)} "
        "— review policy changed mid-day."
    )
    print(
        f"  • Feedback clustering: highest estimated minutes ({num(feedback['minutes'], 1)}) "
        f"but weakest accept ({pct(feedback['accept'])}) on lower volume."
    )

    print()
    print("METRIC TO TRUST LEAST")
    print("  median_confidence — model self-report, not human quality.")
    print("  On 7 Aug it was high while the user rating crashed.")

    print()
    print("LOOK AT NEXT")
    print("  1. What exactly changed in Support review policy on 7 Aug?")
    print("  2. Filter demo/test accounts out of exports.")
    print("  3. Weekly: accept rate + user rating by workflow + source (never blended).")

    print()
    print("DATA QUALITY FLAGS")
    for row in rows:
        labels = issues(row)
        if not labels:
            continue
        marker = "  ← kept visible, not dropped" if "review policy changed mid-day" in labels else ""
        print(
            f"  {row['date']}  {row['team']}/{row['workflow']}/{row['source']}  "
            f"[{', '.join(labels)}]{marker}"
        )

    print()
    print("WORKFLOW HEALTH (demo + duplicate excluded)")
    print("  Rates: completion = completed/sessions; accept and flag = count/completed.")
    for name in ("Lead summary", "Reply draft", "Feedback clustering"):
        s = by_workflow[name]
        print(
            f"  {name:<22} sessions {s['sessions']:>3}  "
            f"complete {pct(s['completion']):>3}  "
            f"accept {pct(s['accept']):>3}  "
            f"flag {pct(s['flag']):>3}  "
            f"min {num(s['minutes'], 1):>4}  rating {num(s['rating'])}"
        )
    print()

def main():
    if not DATA_PATH.exists():
        raise SystemExit(f"Missing data file: {DATA_PATH}")
    print_brief(load_rows(DATA_PATH))

if __name__ == "__main__":
    main()
