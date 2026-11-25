---
name: shot-review-flow
description: Sam's rule (2026-11-23) for 5 O'CLOCK shots: notify on each finished shot, move on after 1 min, fix old shots after the current one
metadata:
  type: feedback
---
When a shot is finished, message Sam right away with the clip + frames (a post_message notifies him). If he hasn't approved or commented within 1 minute, start the next shot. If he later asks for improvements on an earlier shot, finish the shot in progress first, then go back and fix the earlier one. His note also becomes a dated rule in SHOT_RULES.md.
**Why:** Sam reviews from his phone/office and doesn't want the pipeline stalling on him.
**How to apply:** Never wait for approval between shots; see [[perfect-shot-rule]].
