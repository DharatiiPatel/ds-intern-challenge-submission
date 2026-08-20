# AI Collaboration Note

## Did You Use AI?

Yes. I used Cursor with Claude and Codex to help write the script and the short write-up. I read the challenge files and looked at the CSV myself first.

## How You Used It

I used AI to help turn my notes into a working script and clearer wording. I did not let AI pick the final recommendation alone.

I compared drafts from Claude and Codex. Claude’s version ranked the workflows and kept some noisy rows in the totals, so Lead summary looked better than it should. Codex’s version stayed closer to a weekly health brief: what is working, what looks suspicious, and what to look at next. That matched the teammate ask better so I used the Codex direction and then simplified the code myself.

## One Prompt, Workflow, Or Moment That Helped

Asking for one small use case i.e a weekly health brief instead of a dashboard or a model. Comparing Claude and Codex side by side also helped me see which output was more useful and which one overbuilt or trusted the data too much.

## One Thing You Verified Or Decided Yourself

I checked the main numbers myself from the CSV:

- 41 rows total
- drop both Aug 5 Lead summary email demo/duplicate rows from the totals
- Lead summary / email accept rate is about 81%
- Aug 7 Reply draft queue: rating 2.1, confidence 0.91, flag rate about 71%

I decided myself to:

1. drop demo and duplicate rows from health totals
2. keep the Aug 7 policy-change row visible
3. treat `median_confidence` as the least trustworthy metric

AI helped me write faster. Those judgment calls were mine. The final script I am submitting is the Codex-based version, cleaned up.