# STATE: 5 O'CLOCK ep1 (update after every step; any agent resumes from this file)
- Phase: P0 intake done 2026-11-23 (motion2d skill first run). Path A+ (previous episode in skill format exists).
- Style: toon-anime | Length: NOT DECIDED (see open questions) | 24 fps | 1080x1920
- Locked look: ep1v3\SHOT_RULES.md (from 01_speaker_v4, Sam: "keep v4")
- Render box: this PC (RTX 3050 4 GB), `xc\blender501\blender.exe` (also `blender5\`), ffmpeg on PATH, below-normal priority
- Skill: ~/.claude/skills/motion2d (installed from samrat10000/money-skills main). Read the reference code in its `reference/5oclock_ep1v3/`.
- Read also: WORKING.md (log), DECISIONS.md (decisions + to-do).

| shot | status | latest version | file | director's note | next action |
|---|---|---|---|---|---|
| 01_speaker (crow on loudspeaker) | locked | v4 / v4b glint fix | ep1v3\01_speaker\src\01_speaker_v4b.mp4 | "keep v4" | none |
| 02_mirror (curve mirror) | passed | v1 | ep1v3\02_mirror\ (scripts only locally, no clip found) | "good, go with this" | re-render on PC if a clip is needed |
| 03_kiriyama (town wide) | passed (v1) | v1 | ep1v3\03_kiriyama\src_v2 | "perfect, but..." notes now in SHOT_RULES s10 | re-render with the s10 rules |
| 04_ride (Sam rides home) | probe | v3 | only in _wt_ep1v2\...\04_ride\src\04_ride_v4.mp4 (24 MB, newest, 21:50 today) | "nobody grabs a handle like that" | review v4 vs hand-grip rule R3, then deliver |
| 003_sam (code-drawn 2D Sam, close-up) | sent, no verdict | v3 | ep1v3\003_sam_v3_silent.mp4 | none yet | Sam's verdict (see question 1) |
| storyboard | v3 rejected as style ref | v3 | ep1v3\storyboard_v3.png | dropped lines, invented shots | storyboard v4 |
| cast (VRoid CC0) | built, none read right | | assets\vroid_cc0\ (11 VRMs) | grandma/kids read as teens | fix proportions per R2 |
| sound | blocked | | ep1v2\audio\ (ElevenLabs takes N1,N2,S1,P1,S2, A/B) | no-AI music/voice rule unresolved | after picture approved |

## Next step
Get Sam's answers to the open questions, then re-plan the episode per STORY.md (45-65 s), keep 01 as the bar.

## Open questions for the director (one batched)
1. Look for Sam: the locked bar is the toon-3D VRM look (01-04). 003_sam_v3 is code-drawn 2D, which this skill rates as the "stick figure" risk. Keep 003 v3's drawn Sam, or rebuild Sam from a VRM toon model?
2. Length: skill/STORY.md says episodes are 45-65 s; the current v3 plan is 21 s. Which?
3. Voice and music: ElevenLabs takes exist; the Flow piano is AI. Decide, since sound is last anyway.
