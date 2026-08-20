# Submission README

## Track Chosen

Track A: Fictional Domain Packet (SignalDesk).

## What I Built

A Python script called health_check.py. It prints a short weekly health brief. It cleans the messy export, drops bad rows from the totals, and tells a teammate what is working, what looks odd and what to check next. 

How to run:

1. Open the folder that contains health_check.py and the sample-data folder.
2. Run: python3 health_check.py
3. Check the output folder for health_check_output.txt and workflow_rates.svg

## **Who It Is For**

A SignalDesk product teammate who wants to know if these AI workflows are ready to expand. This document will help them to get a clear picture on what should be the next step like.

## **Data Or Source Used**

The fictional CSV in sample-data/product_usage_events.csv (Aug 1-7, 2026).

## Assumptions I Made

The export is small and messy, so I could not trust every column the same way. Before writing the script I chose a few rules for what to trust and what to treat carefully:

- I used accepted/completed as my main useful signal because finished just means the run ended and accepted means someone actually took the output with little rework.
- I left the demo traffic and the duplicate row out of the totals. If I kept the Aug 5 Lead summary email spike, that workflow would look way better than it really did on normal days.
- I kept the Aug 7 Support policy-change row in the brief. That is the day ratings fall and flags spike, so hiding it was wrong.
- I did not average all workflows into one score because Sales, Support, and Product are doing different jobs and blending them would hide what is actually working.
- I did not treat model confidence as quality because it is just the model scoring itself and on Aug 7 confidence was high while the user rating was low.



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

