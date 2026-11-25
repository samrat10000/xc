---
name: ig-research
description: Live Instagram outlier research for horror/zombie CGI reels (2026-11-20): what over-performs and how to read IG in Sam's Chrome
metadata:
  type: reference
---

Method that works in Sam's Chrome (signed in): open instagram.com/<user>/reels/, read the grid views via JS (the anchors a[href*="/reel/"] have the view count as innerText), and get captions by fetching /reel/<code>/ and reading og:description. The web_profile_info API returns HTML (blocked). The keyword search page is explore/search/keyword/?q=... (some queries return nothing).
Findings (8 accounts, ~110 reels):
- First-person dread is the top outlier: lights.are.off "He wants to come in!" (15 s, a creature walks up to your window, face on the glass) 99M at 55x median; shatoot3d (1.2M followers, Cinema 4D) "Underwater Nightmare II" 253M at 23x (33 s, calm realistic beauty, then a POV look down, then something beneath) and "Last Gear" 235M; shortestblockbusters POV series 78M at 39x; bramhastra.rt surreal single image 535x.
- Top outliers run 15-33 s. Big CGI accounts state "handcrafted, no AI" in captions.
- Zombie survival series (beaniesurvives 256K, drawn.tosurvive) use story captions that end with a choice question plus "Part N".
Applied to the Ep1 v6 storyboard: POV apartment act, Screamer face at his window, a 15 s teaser cut, captions with stakes plus a question. Related: [[zombie-ep1-status]], [[sam-global-rules]].
