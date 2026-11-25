---
name: teaser-v1-review
description: Sam's review of the full Night Terror teaser v1 (2026-11-23 00:08 IST): what to keep, what to fix
metadata:
  type: feedback
---
Loved: 901 opening, 907 lightning, 903 windshield + giant, 909 crash zoom ("so damn good"), 910 eye with saccades ("crazy"), 911 car skid ("perfect shot"), 912 VHS glitch stinger ("crazy, perfect").
Fix:
- Music must flow continuously across the whole teaser; no cut-outs between shots.
- ~6-7 s (905->906): the car seemed to stop, then the side shot starts. The car must keep moving through the cut, and the side camera must show it moving.
- Remove the black gap at ~11 s (between 910 and 911). Keep the dark beat before 912.
- 912 glitch stinger: hold it ~2 s longer so it's noticeable.
- Stalker arms/legs look "funny", like sticks that fold then drop. Sam wants a proper monster: refs are wendigo-style (hunched, spine spikes, long bony arms with clawed hands hanging forward, digitigrade hooved legs) and a long-limbed crawler with claws. Real hands/claws, scary reaching motion.
- Sam wants faster renders.
**How to apply:** keep everything Sam loved untouched; change only these. Related: [[stalker-motion]], [[poster-teaser]].
Sam 2026-11-23 00:25 IST (overrides the music lock for the teaser): NO background music. Use only real sounds: rain, thunder, police siren, car engine revs ("vroom" like a car-reveal teaser), a much better drift/tyre screech (Sam: drift sound is "the thing you always do wrong"), monster growls, deep booms/hits. Open like a trailer: near silence + a single ping, then the scene. "$1 billion sound effects." The teaser is the top priority. Sam is tired of trial-and-wait: send fewer, finished versions. Goal: millions of IG views; after Ep1 everything becomes a reusable skill.

Status 2026-11-23 01:30 IST: sound v2 built (teaser/edit/sound_v2.py, earshot-verified, -14 LUFS, no music). earshot runs from ~/earshot/earshot/.venv/bin/earshot (cloud). Waiting on the PC render of 911/906/912 with Stalker v5, then assemble night_terror_teaser_v2.mp4.
FINAL 2026-11-23 08:13 IST: teaser/night_terror_teaser_final_IG.mp4 (+ _master, CREDITS_teaser_sound.txt) sent to Sam for the morning post; awaiting verdict. PC->cloud file route that works: PC encodes crf8 mp4s and pushes to branch claude/project-thread-b8yfdd (Sam may need to approve the push on the PC); cloud clones and extracts frames.
