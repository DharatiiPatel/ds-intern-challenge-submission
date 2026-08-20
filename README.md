# Submission README

## Track Chosen

Track A: Fictional Domain Packet (SignalDesk).

## What I Built

A simple Python script called health_check.py.

How to run:

1. Open the folder that contains health_check.py and the sample-data folder.
2. Run: python3 health_check.py

Needs Python 3 only. No extra packages. It prints a short weekly health brief. It cleans the messy export, drops bad rows from the totals, and tells a teammate what is working, what looks odd, and what to check next.

## Who It Is For

A SignalDesk product teammate who wants to know if these AI workflows are ready to expand. They need a clear next step, not a big dashboard.

## Data Or Source Used

The fictional CSV in sample-data/product_usage_events.csv (Aug 1-7, 2026), plus the notes in domain-packet.md.

## Assumptions I Made

- accepted/completed is the best "was this useful?" signal in this file.
- Demo traffic and the duplicate row should not be in the health totals.
- The Aug 7 Support policy-change row should stay visible, not get hidden.
- Do not average all workflows together.
- Model confidence is not the same as quality.



## Data Issues Or Caveats I Noticed

- Aug 5 Lead summary email looks like a demo spike, then a duplicate.
- Team name casing differs (product vs Product).
- Confidence shows up as n/a text in one row.
- One missing user rating.
- Aug 7 is missing two source slices.
- Feedback clustering has a small sample.
- Aug 7 Support review policy change makes that day hard to compare with other days.



## What I Would Do Next With More Time

- Match prompt and policy changes to exact timestamps.
- Keep demo/test accounts out of the main export.
- Do a small human review sample on Reply draft before rolling it out more.

