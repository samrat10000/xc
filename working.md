# working.md: Night Terror Ep1 (v8), live status

Last updated 2026-11-24 ~17:36 IST. Read this first if you are picking this up in VS Code with another account.
Background and Sam's taste rules: `PROJECT_HANDOFF.md`, `EPISODES/EP1_THE_CALL.md`, `CLAUDE_REVIEW_EP2.md`.

## EP1 v8 RENDER STATE (stopped 2026-11-24 23:50 IST by Sam, all rendering ended)
- Frames done per cut (out\v8\cNNN): 525: 62/144 (partial, no mp4); 530: 72 done; 535: 60 done; 540: 48 done; 550: 28/60 (partial, no mp4); 552, 565, 400, 404, 406, 441, 450, 455, 471, 490, 495, 160: 0.
- mp4s that exist (out\v8): 130_overpass_park, 135_dash_reveal, 140_crash_zoom (all *_v8_silent.mp4). Partial cuts were NOT encoded. All finished frames are kept.
- Resume: run queue_v8.ps1 again. It skips finished mp4s and finished frames; the c525 and c550 partial frames are kept and continue.
- Speed warning: render speed drops after a few hours (VRAM ~3.7 GB). If frames get slow, end blender.exe and the queue restarts it fresh on the next cut.

Full Ep1 v8 state, decisions and next steps: ep1pc\WORKING_EP1_V8.md. Everything built in the cloud (sound mix, voices, SFX, plan, probes, scripts, project memory notes) is in ep1pc\v8cloud\.
2026-11-24 18:16 IST: Ep1 v8 render (c525 blender) is SUSPENDED so the creepy render finishes first; a hidden watcher resumes it when the creepy blender exits (log: C:\Users\cross\AppData\Local\Temp\claude\2025787e23e4a901\9e68133b-fefc-4c85-a5b7-0d5c43ec2681\scratchpad\hold.log). If c525 comes back broken after the resume, delete out\v8\125_brute_jturn_v8_silent.mp4 and any 0-byte png in out\v8\c525 and re-run queue_v8.ps1: it skips finished frames.
2026-11-24 19:43 IST: c525 stopped at f0062 after the suspend made it slow; re-run queue_v8.ps1 after the queue finishes to complete c525 (it skips done frames and done mp4s).

## Where things live (all under `C:\Users\cross\Downloads\xc`)
- `ep1pc\ep1\`: the working Blender scripts for Ep1 on this PC. `shots2.py` is the renderer, `v7sets.py` holds the per-cut scene setups (cut400, cut160, ...), `anim.py`, `city.py`, `edit*.py` etc.
  (An older copy of the scripts is in `xc\ep1\`. Use `ep1pc\ep1`.)
- `blender501\blender.exe`: Blender 5.0.1 used for renders.
- `ep1pc\queue_v8.ps1`: the render queue (17 cuts, runs one Blender per cut, then ffmpeg to a silent mp4).
- `ep1pc\out\v8\`: queue output. `cNNN\fXXXX.png` frames, `rNNN.log` Blender log (UTF-16), `NNN_name_v8_silent.mp4` per finished cut.
- `ep1pc\out\q8.log`: queue status lines (CUT / MP4 / FAILED / QUEUE DONE).
- `ep1pc\out\v7final\`: earlier v7 renders (125, 140, 150).
- `ep1pc\out\bench\`: benchmark frames only, safe to delete.
- Voice/dialogue: `voice_ep1\`, `ep1pc\ep1\dialogue_mix.py`, `mix6.py`.

## Render queue state
- Started with `queue_v8.ps1` (hidden powershell) on this PC, GPU, all on the local machine as Sam wants.
- Cut order: 525, 530, 535, 540, 550, 552, 565, 400, 404, 406, 441 (frames 313-444 only), 450, 455, 471, 490, 495, 160.
- A cut is skipped if its `*_v8_silent.mp4` already exists, so the queue can be restarted safely.
  Frames are not resumed: a restart re-renders the current cut from its start.
- Speed now: about 41 s per frame at 1080x1920, 32 samples. Cut 525 was the first to run (frames 1.. in `c525`).
- At the time of writing cut 525 was around frame 9 and rendering. Check `q8.log` for finished cuts.
- If the queue is dead: check `tasklist | findstr blender`, then rerun
  `Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File C:\Users\cross\Downloads\xc\ep1pc\queue_v8.ps1' -RedirectStandardOutput C:\Users\cross\Downloads\xc\ep1pc\out\q8.log -WindowStyle Hidden`
  (only after making sure no blender.exe is running; delete any 0-byte pngs in `out\v8` first).

## Decisions and changes made today (2026-11-24)
1. First v8 run (SAMP=48, persistent data on) was far too slow: frame 2 of cut 525 ran over 9 minutes. Likely cause: persistent data pushing the 4 GB laptop GPU over its VRAM limit.
2. Fix applied:
   - `shots2.py`: `use_persistent_data` now reads env `PERSIST` (default 1); `volume_step_rate` reads env `VSTEP` (default 6).
   - `queue_v8.ps1`: `SAMP=32`, `PERSIST=0`, `VSTEP=10`. Removed the keep-awake (SetThreadExecutionState) lines, which also threw an error. Power settings were not touched.
3. Benchmark (CUT=525, frames 60-62, SAMP=32, PERSIST=0, VSTEP=10): about 40 s per frame. Queue restarted after that.
4. `v7sets.py` cut400 (the hook) retimed: `nf` 120 -> 168, watcher/fog keys shifted later (77/78 -> 127/128 etc.), camera keys, `hunt` window 36-60 -> 59-98, kicks 78/84 -> 128/134.
5. `v7sets.py` cut160 (empty seat): the Akash screen emit lowered (emit .001 on material, keyed values 2.2 -> 1.3).
6. The one frame from the old run (`c525\f0001.png`, 48 samples) may be overwritten by the new run.

## Open questions / next steps
- Estimate for all 17 cuts not yet worked out (need each cut's frame count; the queue prints frames, secs, spf per cut in `q8.log`).
- When cuts finish: review the mp4s, then audio mix (`dialogue_mix.py`, `mix6.py`) and final edit.
- Cuts 400 and 160 were retimed/re-lit without a test render. Look at them first when they come up.
- The earlier note said `blender.exe` should be the only GPU job. Do not run anything else heavy while the queue renders.

---

# Episode 2: two different projects share the name. Do not mix them up.

Neither is being rendered by me. State below is read from the folders at 2026-11-24 ~17:40 IST.

## A. "Night Terror: Dead Roads" Ep2, The 43rd Round (same series as Ep1 v8 above)
Cloud files for this episode: EPISODES\ep2_cloud\ (see README_EP2_CLOUD.md)
- Folder: `dead-roads-ep2\` (own git repo; last commits are look-test sheets s02, s08, s13 and drift fixes from PC look tests). Remote: `samrat10000/dead-roads-ep2`.
- Plan v2 (48 s, 17 shots, 4 acts), status in `EPISODES\EP2_THE_43RD_ROUND.md`: IVORY trike rider with 42 rounds vs a horde and the unkillable Stalker; the trike must really hit a zombie (ragdoll); Mixamo mocap zombies; Stalker shoves the truck with a crash zoom; ends on the Stalker's leap (Ep3 opens on it). Hook text on frame 0: "She brought 42 rounds."
- Run: set `EP2=C:\Users\cross\Downloads\xc\dead-roads-ep2` and `GPU=1`, then
  `..\blender501\blender.exe -b --python sc\shots.py` with env `SHOT=n RES=1 SAMP=64 OUT=out\sNN`. Shot script `sc\ep2.py` / `sc\shots.py`.
- Outputs so far: `out\ep2`, `ep2v2`..`ep2v4`, look tests `look_*`, previews `previews\ep2-preview-1..4.mp4`. Shot 2, 8 and 13 had look tests (RES .3, 12 spp) with fixes applied; no full final render noted.
- Assets: rider `rider-v3.2.glb`, trike `ivory-dead-roads-trike-v2.glb`, Stalker bull-skull `stalker_v3` (in `assets\`). Camera notes in `CAMERA-MOVES.md`.
- Next: finish the remaining shots at full res/samples, assemble, score (Flow "Action Horror Cue", 120 BPM, kills on beats).
- GPU rule: Ep1 v8 queue has priority on this PC. Do not start a second Blender while it runs.

## B. "5 O'CLOCK" Ep2, The Koban (a separate series, Claude/Codex shared workflow)
Cloud files for this episode: EPISODES\ep2_cloud\ (see README_EP2_CLOUD.md)
- Folder: `5oclock-ep2-the-koban_2026-11-24\`. Read `STATE.md`, `PRODUCTION_LOG.md`, `V7_HAND_REVIEW.md`, `ERROR_CATALOG.md`, `SHOT_RULES.md`, and `..\CODEX_CLAUDE_STATUS.md` (shared continuity and GPU coordination), `..\CLAUDE_REVIEW_EP2.md`.
- Sam rated v5 3/10. v6 built from the review: selected master `episode\5oclock_ep2_the_koban_v6.mp4` (57.4 s, 1378 frames, 1080x1920, 24 fps, -14.94 LUFS, -2.94 dBTP, 7.8 LU). Delivery index `episode\DELIVERY_V6.md`. Sam approved the v6 voices.
- Current work: v7 hand and gait pass (shots 05, 06, 07, 10, 13: gait, wrists, fingers, door grips). Plan and evidence in `V7_HAND_REVIEW.md`. Keep the v6 audio and frame layout as the baseline.
- Sam's rules that apply to both Ep1 and Ep2 (from `CODEX_CLAUDE_STATUS.md`): hands on moving objects stay gripped; headphones grabbed with four fingers and a neutral wrist; mirrors and glass fully reflective and stable (no flicker); swivels get a real pivot with ease and overshoot.
- Related: `5oclock-ep1-the-fourth-note_2026-11-23\` (5 O'CLOCK Ep1, scored cut done) and `5oclock-ep3-dont-answer_2026-11-24\` (Ep3, has its own WORKING.md).
- I (this PC session) did not work on B. Codex/Claude do, in those folders.
