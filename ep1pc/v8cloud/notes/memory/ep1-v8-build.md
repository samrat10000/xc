---
name: ep1-v8-build
description: Ep1 v8 build state (2026-11-24) - new cut functions, voice lines, blockers, delivery limits
metadata:
  type: project
  modified: 2026-11-24T09:35:41.032Z
---
v8 plan: https://claude.ai/artifact/UVoWQ7tyVwtVc8Q5cd3Qxj (rules in /terror-night PR #5, merged). Sam said "go" 2026-11-24.
Code (scratch ep1/v7sets.py, exec'd by shots2.py, CUT=<n>): cut406 (006 still Screamer + long-lens push), cut441 (041 stair take continued to LOBBY door, render f313-444 only), cut450 (050 with stair-door push prelude, ends at B1 PARKING door), cut455 (055 service stair -> dark garage = 060 f1), cut470/cut471 (070: 471 = Sam seated in driver seat via sam_in_driver_seat(), over-shoulder from passenger headrest, hand to key, crank), cut490 (090 gate burst, low road cam). pent7.py fixed for 007 (empty chair, CURVES hidden).
Gotchas: renders SKIP existing frames ("No frames rendered, skipped") - delete old probe PNGs first. wall_decal text: scale x -.6 reads correctly on the LOBBY sign (positive was mirrored).
Sound: snd7/s030_v8.py drops the female sob (the "female voice" Sam heard). Screamer v5 scream at S/v8/snd/scream_v5_*.wav.
Voices: 11 new lines generated in ElevenLabs (Browser 1, Asus): Sam = Jack John, Akash = Adam, 2 takes each. Chrome blocked multiple downloads; asked Sam to "Always allow" elevenlabs.io (14:16 IST). Only hook line 1 (2 takes) + hook line 2 take 1 pulled so far.
Delivery: the Ep1 thread hit its 96 attached-outputs limit; deliver by path/GitHub raw link instead.
Related: [[ep1-v7-final-review]] [[terror-night-skill]]
