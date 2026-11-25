---
name: ep1-v7-plan
description: Sam rejected Ep1 v6 (2026-11-22); the teardown, the v7 camcorder concept, beat timings and the rules that came out of it
metadata:
  type: project
  modified: 2026-11-22T07:05:32.876Z
---
Sam 2026-11-22 12:24 PM IST rejected Ep1 v6 (/mnt/project-files/reels/series/ep1/night-terror-ep1-v6.mp4).
- Problems: voices overlapping, a strange sound at the start, the reindeer/Stalker in the first second, a cheap-looking stairwell with no horror, bad walking/stair animation, music not complementing the dialogue, the Stalker's mouth hollow, and the phone-in-the-car ending feeling random.
- He wants the BEST "3D pencil sketch" animation (our ink-line 3D house style). He wants more scenes, and web references are allowed.

Teardown + v7 plan artifact: https://claude.ai/artifact/L2VrwBbCJ8Y4bcgCiPbwjV (src /mnt/project-files/reels/series/ep1/v7/storyboard_v7.html, template scratch ep1/v7_page.html.tpl).

Root causes I found:
1. I reused v5 shots Sam had asked to fix: c04 crawler blur, c162 freeze skid, c18/c19 potato Brute, c22 hollow mouth, c10 headlight flicker. I also replaced his favourite v5 garage reveal (c11) with a dark POV.
2. Three looks mixed: the real NYC photo plate, the photoreal phone, and the ink 3D world. The VHS blur killed the ink lines.
3. Story gaps: no keys or exit, no reason for the stairs, no lobby, never gets in the car, phone never placed on the seat.
4. Dialogue was fitted to the v5 music clock: 4 overlaps, 5 lines buried. Akash and the radio share the Adam voice. The opening buzz was a synthetic sine.

v7 concept: the camcorder on a tripod was filming a skyline timelapse when the phone rang. Sam carries it as handheld POV, then props it as the dashcam. The ending is the dashcam view of the empty seat with the door open and Akash calling, then the voicemail.
Timings (about 95 s; decision card posted, 95 s recommended):
- Act 1 call, 0-27.
- Act 2 corridor, dead elevator, pre-war stairwell, lobby horde, garage, phone tossed on the seat: 27-53.5.
- Score drops on the ignition at 53.5.
- Chase to 76. Overpass call, Stalker mouth tear, lunge, black at 84. Empty seat 85.5-96.

Rules:
- No cold open.
- No score before the ignition; real sound only before it.
- One line at a time with a breath after it.
- The radio gets a robotic EAS voice.
- Render 1080 on the Asus only. Keep Sam's face out of frame.
- Before reusing ANY old shot, re-check Sam's past review notes for it.

Related: [[zombie-ep1-status]], [[ep1-dialogue]], [[camera-grammar]].

Sam 2026-11-22 1:20 PM IST (via the coordinator, applies to all threads): number every shot and name each clip `<number>_<short-name>`, e.g. `040_stairwell.mp4`. Ep1 v7 shot numbers follow the cut numbers (c40 is 040_stairwell).
The Stalker skull must be redone for Ep1 v7 too:
- A real dead bull or cow skull shape, not round, popcorn-like or squarish-toothed.
- A genuinely scary mouth.
- A scarier red eye glow: not a flat dot and not snake-eyed.
- Use references from Pinterest and stag or reindeer demon horror films.
Reuse the teaser thread's new skull once it exists.

APPROVED LOOK (Sam 2026-11-22 2:03 PM IST, on 040_stairwell preview "damn cool, I want this realism in all the other clips"):
- Dark, lit only by practical lights (camcorder lamp, flickering emergency lamps, fire glow).
- Pre-war NYC detail: hex tile, marble treads, iron balusters with oak rail and ink, brass elevator.
- Real recorded footsteps and room tone, no score.
Source: scratch ep1/v7sets.py (cut40), sound ep1/snd7/stair_snd.py. Use this as the bar for every v7 shot.

Sam on 001_ring (2026-11-22 2:39 PM IST):
- The distant fire jitters too fast. It needs slow, real fire motion, a lot more realistic, and in several places across the city.
- The sky must not be pitch black: add stars or clouds lit by the fires, falling ash, and rain visible outside.
- The hand must not hover in an L shape. It rests naturally and only reaches for the phone when it picks it up.
- Everything else was good.

Skill logs (Sam 2026-11-22 3:23 PM IST, via the coordinator): append-only WORKING.md, DECISIONS.md and MISTAKES.md.
- Location: /mnt/project-files/reels/series/logs/ep1/, mirrored to xc\logs\ep1 on the Asus.
- Add an entry after each shot review.
- Sam turns them into one reusable skill once Ep1 and the teaser are approved.

Call drops (Sam 2026-11-22, on 005_bridge): never use beep/interference tones. Break the caller's words (gaps, stutter, crunch), cut mid-word, small click, dead line. Script: scratch ep1/snd7/calldrop.py.

PAUSED 2026-11-22 11:31 PM IST: Sam wants one thread at a time, with the teaser first. Ep1 v7 resumes only when Sam says so. The resume point is at the end of logs/ep1/WORKING.md (050_lobby test done; previews from 006 on go through the coordinator).
GRAIN (Sam 2026-11-23, on 050_lobby): no heavy grain or black dots; only a light film grain. Previews SAMP>=20, sparse rain-glass drops, mild hqdn3d on encode.
Sam 2026-11-23 2:16 AM IST: render in the cloud whenever the PC isn't reachable. If tokens run out, resume both active threads (teaser + Ep1) when limits refill. Lobby dots came from speckled marble/paint textures too: cut50 scales texture patterns 4x larger; keep surfaces smooth in later shots.
