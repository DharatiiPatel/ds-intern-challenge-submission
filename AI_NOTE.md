# AI Collaboration Note

## Did You Use AI?

Yes. I used Cursor with Claude and Codex.

## How You Used It

I read the challenge files and the domain packet, then opened the CSV and just scrolled through it. The notes column made the big issues obvious, so I already knew what looked trustworthy and what did not. 

After that, I used AI to help me turn those notes into a small script and cleaner wording. 

I also compared Claude and Codex while drafting. Claude pushed more toward ranking workflows and left some noisy rows in the totals, which made Lead summary look too good. Codex stayed closer to a short weekly brief for a teammate. That comparison was useful  but I still made some changes so it matched the assumptions I cared about like dropping the demo rows and keeping Aug 7.

## **One Prompt, Workflow, Or Moment That Helped**

The most useful moment was asking AI to code around the rules I already wrote in my README: use accepted/completed, drop the Aug 5 demo/duplicate rows, and keep Aug 7 visible. When a draft tried to “clean away” the policy-change day, I stopped it. That row is the main warning, so it had to stay in the brief.

## One Thing You Verified Or Decided Yourself

I checked the main numbers myself from the CSV instead of trusting the scripts:

- 41 rows total
- drop both Aug 5 Lead summary email demo/duplicate rows from the totals
- Lead summary / email accept rate is about 81%
- Aug 7 Reply draft queue: rating 2.1, confidence 0.91, flag rate about 71%

I also made a few calls myself:

1. Drop demo and duplicate rows from the health totals
2. Keep the Aug 7 policy-change row visible
3. Treat median_confidence as the least trustworthy metric

AI made writing faster. The final judgment was mine. The script I am submitting is the Codex-based version after I simplified it.