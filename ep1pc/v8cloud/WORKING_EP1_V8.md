# Night Terror: Dead Roads, Episode 1, v8: WORKING notes (state on 2026-11-24, 6 PM IST)

Read this first if you continue Ep1 from another account or VS Code. Everything you need is in this folder:
`C:\Users\cross\Downloads\xc\ep1pc\` (render kit + v8 code) and `C:\Users\cross\Downloads\xc\ep1pc\v8cloud\` (everything
that was built in the cloud: sound, voices, SFX, plan, probes, memory notes).

## 1. Why v8 exists (Sam's review of the v7 "final", 2026-11-24 13:26 IST)
Full review: `v8cloud\notes\memory\ep1-v7-final-review.md`. Short version:
- KEEP: phone + answer, stand + blast, stairwell (best scene), garage + car, rolling onto the street, empty-seat ending.
- FIX: the v5 Screamer scream (the v7 swap was "trash") with the Screamer standing STILL (no floating turn) and the camera zooming
  in; no Sam left on the sofa while grabbing keys; corridor voice must be male; NO jump cuts stairs -> lobby -> garage;
  no invisible hand in the car (show Sam from behind or use a dashcam); real car sounds; the Brute must not be driven
  through (kill it or U-turn); bridge Stalker = the NEW teaser model + its skull motion, car parked; narration clearly audible.
- ADD: an IG hook narrated by Sam ("This was New York City... then boom"), narration + calls with Akash, NO background
  music (real sounds only) except ONE music piece at the Stalker, a hidden "someone is filming him" long-lens camera.
- Plan artifact (storyboard Sam approved with "go"): https://claude.ai/artifact/UVoWQ7tyVwtVc8Q5cd3Qxj
  (copy: `v8cloud\plan\ep1_v8_plan.html`, text dump `v8cloud\v8\plan.txt`). Rules went into /terror-night (PR #5, merged).

## 2. Shot list v8 (30 shots, 116.8 s at 24 fps). Frame counts are what the mixer assumes.
| # | shot | frames | picture source | status |
|---|---|---|---|---|
| 000 | hook (watcher long lens, blast on "boom" at f128) | 168 | CUT=400 | Asus queue (retimed today) |
| 001 | ring | 95 | v7 final `01_001_ring_v2` | keep |
| 002 | phone insert | 47 | v7 `02_002_phone` | keep |
| 003 | answer | 83 | v7 `03_003_answer_v2` | keep (new lines in the mix) |
| 004 | look outside, blast at 4.8 s | 174 | v7 `04_004_look_outside` | keep |
| 004w | watcher: Sam at the glass | 60 | CUT=404 | Asus queue |
| 005 | bridge call drop | 92 | v7 `05_005_bridge_v2` | keep |
| 006 | Screamer still + 135 mm push, scream | 96 | CUT=406 | Asus queue |
| 007 | grab: empty chair, keys | 48 | pent7.py (r007v8.sh) | cloud 1080 render, frames in `v8cloud\pent7\out007v8` |
| 030 | corridor | 72 | v7 `08_030_corridor_v1` | keep (re-voiced) |
| 040 | stairwell + continued take to LOBBY door | 311 + 132 | v7 `09_040_stairwell` (311 f) + CUT=441 FR=313,444 | Asus queue |
| 050 | lobby, door push prelude -> B1 PARKING | 120 | CUT=450 | Asus queue |
| 055 | B1 service stair -> dark garage (= 060 f1) | 70 | CUT=455 | Asus queue |
| 060 | garage | 96 | v7 `11_060_garage_v1` | keep |
| 070 | Sam in the driver seat, over the shoulder, key, crank | 84 | CUT=471 | Asus queue |
| 080 | ignition | 36 | v7 `13_080_ignition_v1` | keep (re-sounded) |
| 090 | gate burst, low road cam | 84 | CUT=490 | Asus queue |
| 095 | watcher from a window, car fishtails past | 60 | CUT=495 | Asus queue |
| 100 / 110 / 120 | tyre cam / chase / drift | 36 / 60 / 36 | v7 finals 14-16 | keep (re-sounded) |
| 125 | Brute J-turn, shoulder hit, second roar | 144 | CUT=525 | Asus queue (first in line) |
| 130 | car rolls up, PARKS, 23 m short of the overpass | 72 | CUT=530 | Asus queue |
| 135 | dashcam reveal (windscreen hidden + rain beads) | 60 | CUT=535 | Asus queue |
| 140 | crash zoom from the car roof to the skull | 48 | CUT=540 | Asus queue |
| 150 | scream (slam f52) | 60 | CUT=550 | Asus queue |
| 152 | far watcher: the Stalker drops toward the car | 36 | CUT=552 | Asus queue |
| 155 | black | 36 | - | |
| 160 | empty seat, phone "Akash calling" | 252 | CUT=160 (phone screen fixed today) | Asus queue |
| 165 | far watcher, door open, REC, tape stop | 36 | CUT=565 | Asus queue |
v7 final shot files: `xc\ep1pc\out\v7final` (Asus) and on the assets branch `ep1_final/`; the v7 IG cut is
`/mnt/project-files/reels/series/ep1/v7/final/` in the Claude project.

## 3. Rendering (Asus RTX 3050, Blender 5.0.1 portable)
- Queue: `xc\ep1pc\queue_v8.ps1` (log `out\q8.log`, frames `out\v8\c<CUT>\fNNNN.png`, mp4 `out\v8\<shot>_v8_silent.mp4`).
  Re-running it skips cuts whose mp4 exists, and Blender skips frames that already exist (delete 0-byte PNGs first).
- Settings: RES=1 SAMP=32 DEVICE=GPU MB=.2 PERSIST=0 VSTEP=10 -> ~41 s/frame. PERSIST=1 (old default) overflowed the 4 GB
  VRAM and went to 9+ min/frame. ~2,100 frames in the queue = ~24 h of GPU time.
- out\v8\c525\f0001.png was rendered with the OLD 48-sample settings: delete it and re-render frame 1 so 125 matches.
- Run one cut by hand: `cd xc\ep1pc\ep1` then set env CUT=525 RES=1 SAMP=32 DEVICE=GPU MB=.2 PERSIST=0 VSTEP=10 OUTROOT=<dir>
  [FR=a,b] and run `..\..\blender501\blender.exe -b --python shots2.py`.
- Debug without rendering: add `DRY=x,y,z` (or `auto`) and `DRYF=<frame>`: prints what the camera ray hits first
  (that is how the 552/565 "camera inside a building" and the 535 "grey windscreen slab" bugs were found).
- Code: `ep1\shots2.py` (render + helpers) execs `ep1\v7sets.py` (all v7/v8 cuts) which execs `ep1\v8bridge.py`
  (teaser Stalker port + bridge cuts 530-565, 495). The cloud copies are in `v8cloud\ep1\` (same as the Asus copies after
  today's edits).

## 4. Sound (built in the cloud; no background music)
- Mixer: `v8cloud\v8\mix_v8.py` builds the WHOLE 116.8 s timeline from real recordings, then `master.sh mix_pre.wav out.wav`
  brings it to -14 LUFS (last run: -14.5 LUFS, -1.0 dBTP; still aim for -1.5 dBTP). Output `v8cloud\v8\ep1_v8_mix.wav`.
  Run: `cd v8cloud\v8; OUT=mix_pre.wav python mix_v8.py; bash master.sh mix_pre.wav ep1_v8_mix.wav` (needs numpy + ffmpeg).
- Buses: amb, fx, car, keep (approved v7 per-shot mixes: 001, 002, 005, 030 v8, 040 first 311 f, 060, 160), vo (on-screen Sam),
  ph (Akash phone band), narr (Sam to the audience: dry, upfront, everything else ducks 10 dB under it), mus.
- Scene dynamics: per-shot targets (TGT dict) on the median level, so the apartment is quiet, the chase/Brute loud, and
  the bridge drops before the music. Approved v7 mixes only get fixed trims (KEEPG).
- The ONE music piece: the v5 score (`v8cloud\music\music-v5.mp4`), 22.9 s -> 32.9 s, its hit at 30.7 s lands on the
  Stalker's drop (152 f19); fades in at 135, out over the black 155.
- Real SFX: `v8cloud\v8\tsfx\` (the teaser's credited CC0/CC-BY set, index.json has the credits),
  `v8cloud\v8\xsfx\` (new today: starter crank + catch, V8 idle, car door, stairs, keys, chain, deadbolt, push bar,
  phone buzz, car alarms, heartbeat, bone cracks; index.json credits; two are CC BY: idle2 lonemonk, chain MattRuthSound),
  `v8cloud\sfx7\` (v7 set), Screamer v5 scream stems `v8cloud\v8\snd\scream_v5_{vox,hit,amb}.wav`.
- CREDITS still to write into the episode caption/description from the three index.json files.
- Not yet done in sound: listen-check every line over its bed after the picture is final; the watcher's breathing and a
  lens zoom motor (no good recording found yet); the "oh my God" whisper in 004 (no v8 take).

## 5. Voices (ElevenLabs, generated in Sam's browser)
- Sam = "Jack John", Akash = "Adam". Raw takes `v8cloud\v8\vo\*.mp3`, silence-trimmed `v8cloud\v8\vot\*.wav`.
- Chosen: h1_nyc_t1, h2_boom_t1 ("Then..." 0.04-0.82 s, "boom" 1.88-2.42 s), h3_slept_t1, 003_groggy_t1,
  003_akash_look_t1, 007_keys_t1, 030_comeon_r1 (124 Hz, the male re-voice), 070_please_t1, 095_akashsaid_t1,
  125_nope_t1, 125_bridge_t1. Male check = median F0 ~100-140 Hz; reject takes near 200-290 Hz (the v7 "female" problem).

## 6. Decisions made today (and why)
- Hook lengthened 120 -> 168 frames: the narration "This was New York City. Three forty-seven a.m. ... Then... boom." is
  6.4 s, so the blast moved to f128 to land on the word "boom". "And I slept through it." ends on the cut to 001.
- Bridge: PARK moved from y -20 to y -7 (23 m short of the overpass); from under the bridge the deck hid the Stalker.
- 535 dashcam: the tinted windscreen renders as an opaque grey slab, so it is hidden and replaced with rain beads.
- 552/565: the far watcher camera was inside a building (black frames); moved to (5.2, 34, 8.5) on the street side.
- 125: second roar now framed (camera pans to the Brute at f106), street lamp moved over the hit and raised to 6500 W.
- Hook: Sam is framed head-and-shoulders over the chair through wet glass (560 mm), rim-lit by a 90 W reading lamp. The
  fireball is a volumetric with a spherical falloff (billows, dark smoke shell, hot core): check it in the 1080 render.
- 160: the phone screen was a white bar because the emission was not linked to the screen image; fixed (emit 1.3).

## 7. Next steps, in order
1. Let the Asus queue finish; then look at one contact sheet per shot (QA.md director's-eye list). Fix and re-render
   only what fails.
2. Grade (`terror-night\scripts\grade.py`; VHS/REC overlay + tape stop only on the watcher shots 000, 004w, 095, 152, 165).
3. Assemble: concat the 30 shots in the order above (v7 finals for the keep shots), lay `ep1_v8_mix.wav` under it.
   If any final shot length differs from the frame counts above, change SHOTS in mix_v8.py and re-mix.
4. Send Sam every finished shot as its own clip (number_shortname), then the full cut. Deliver with a GitHub raw link
   (the Claude thread hit its attachment limit).
5. Two full-cut review passes before calling it final (gate G6.5 in the skill).

## 8. Where the rest lives
- Skill (the rules): github.com/samrat10000/money-skills `make-terror-night/` (start at its CLAUDE.md / SKILL.md).
- Project memory notes copied to `v8cloud\notes\memory\` (Sam's rules, past reviews, camera grammar, sound tools...).
- Asset rigs: `ep1pc\cast\out\rig\*` (Brute v2, Stalker = teaser model, Screamer, Crawler...), Sam: `ep1pc\cast\sam\sam.blend`,
  car: `ep1pc\ep1\car\nt.glb`.
