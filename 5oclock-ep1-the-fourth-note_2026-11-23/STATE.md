# STATE: 5 O'CLOCK Ep1 "The Fourth Note" (63 s, 18 shots, 1080x1920, 24 fps, toon-anime)

Read in this order: this file -> AUTOMATION.md (the loop + token rules) -> ERROR_CATALOG.md (pre-flight) -> SHOT_RULES.md -> PRODUCTION_LOG.md.
Story: story\5 O'CLOCK Episode 1.md/.html and the skill's PLAYBOOK_5OCLOCK.md (shot table). NOT the old anime-5oclock 21 s story.
Model: Opus 5.5 (Sam's choice, 2026-11-23). Render box: this PC, xc\blender501\blender.exe, below-normal priority.
Assets: assets\cast_v2\ (grandma, shopkeeper, kid_girl, kid_boy; G3 passed, lineup.png), assets\toon_sam\sam_toon.blend (approved hero), assets\vrm\.

## Shot queue (the loop takes the first row that is not 'sent' or 'locked')
| # | shot | s | status | latest | notes / next action |
|---|---|---|---|---|---|
| 15 | The Listener | 4.5 | sent v3 | shots\15_listener\v3\15_listener_v3_silent.mp4 | full length. Known: hand still reads a bit like pegs; no tiny Sam in foreground |
| 08 | The frozen town | 5.0 | sent v1 | shots\08_frozen\v1\08_frozen_v1_silent.mp4 | known: crow barely visible; boy's arms need FIX_SHEAR (J1) |
| 01 | The speaker | 3.0 | locked v4 (copied) | shots\01_speaker\v4\01_speaker_v4.mp4 | Sam: 'keep v4' |
| 02 | The mirror | 3.0 | rendered v1 | shots\02_mirror\v1\02_mirror_v1.mp4 | approved code re-rendered (PC run script lacked the paint step: added by hand) |
| 03 | Kiriyama | 3.5 | rendered v2 | shots\03_kiriyama\v2\03_kiriyama_v2.mp4 | approved code re-rendered |
| 04 | Sam rides home | 4.0 | sent v4 (copied) | shots\04_ride\v4\04_ride_v4.mp4 | handlebar grip fix; hidden late reflection |
| 05 | The ritual | 3.5 | sent v2 | shots\05_ritual\v2\05_ritual_v2_silent.mp4 | v1 rejected by self-check (J7/J8) |
| 06 | 4:59 | 2.0 | sent v1 | shots\06_phone\v1\06_phone_v1_silent.mp4 | screen states in src\screens; thumb not visible |
| 07 | Three notes | 4.5 | sent v1 | shots\07_notes\v1\07_notes_v1_silent.mp4 | 42 ravens, rings in the clouds |
| 09 | Silence | 3.0 | sent v1 | shots\09_silence\v1\09_silence_v1_silent.mp4 | headphones to neck, brake, foot planted |
| 10 | Grandma's eyes | 3.5 | sent v1 | shots\10_eyes\v1\10_eyes_v1_silent.mp4 | exec of 08 (exact continuity); Sam coasts past (plan: walks the bike) |
| 11 | In the mirror | 3.5 | sent v1 | shots\11_mirror\v1\11_mirror_v1_silent.mp4 | 02 set + paint_night11 (crowd, cracked sky); CLOSE env for 12 |
| 12 | Closer | 3.5 | sent v1 | shots\12_closer\v1\12_closer_v1_silent.mp4 | whip to a dressed street, frozen backs; crowd closer in the glass |
| 13 | Mirror-Sam | 3.0 | sent v1 | shots\13_mirrorsam\v1\13_mirrorsam_v1_silent.mp4 | separate night-lit reflection pass (msam), no catch-lights, unmirrored |
| 14 | The fourth note | 3.5 | sent v1 | shots\14_fourth\v1\14_fourth_v1_silent.mp4 | ECU hum (night pass) + hard cut wide + 4 hand-keyed crack drawings |
| 16 | Welcome home | 3.0 | sent v1 | shots\16_welcome\v1\16_welcome_v1_silent.mp4 | POV; unfreeze, signs mirror on f12, all turn + smile; girl out of frame |
| 17 | The wrong side | 3.0 | sent v1 | shots\17_wrongside\v1\17_wrongside_v1_silent.mp4 | painted day insert (paint_day17), palm flat on the glass |
| 18 | Rule seven | 4.0 | sent v1 | shots\18_rule7\v1\18_rule7_v1_silent.mp4 | 2D painted insert |
| - | Edit + score | 63.0 | delivered v1 | edit\5oclock_ep1_v1_scored.mp4 (+ _IG, _silent) | 1512 frames verified; recorded-instrument score; voices pending (audio\VOICE_SCRIPT.md) |

## Open questions for the director (non-blocking until sound)
1. Voices: ElevenLabs (AI, needs your browser) or a real voice?
2. Music: Flow piano is AI; real sampled piano score instead?

## v2 pass (Sam's notes on v1, 2026-11-24)
| item | status |
|---|---|
| glass flicker 08/10/16 (z-fight, corner test, sheen) | fixed in build_s04 + comps; 16 v2 verified (glass 56-70% every frame) |
| 16 set to horizon, natural stances, wider lens, POV 2.3 m closer | 16 v2 rendered (72 f) |
| 08 / 10 re-render with the glass fix + SET_EXT | queued after probes (edit/run_v2_queue.ps1) |
| 05a swivel (push, release, overshoot), 05c shutter grip, finger-curl reset bug | code done; probing (v3_probe_a/c) |
| 09 four-finger headphone grab | probe 1 good at f20; cup-centre fix; re-probe queued |
| 17 mother in 3D (build_s17_day.py + Codex's mom rig, DAY17_DIR) | probe queued |
| 11-14 night crowd as 3D sprites (build_crowd_sprites.py) | sprites queued; paint_night11 hookup next |
| series theme | xc/SERIES_THEME (stems + README); Ep1 mix integration next |
| voices | waiting for Codex (ElevenLabs) |
Env for every v2 render: GLASS_INTERIOR=0.22, SET_EXT=1 (04 locked renders without them).
### 2026-11-24 20:55 status
- Voices DONE (Claude via Sam's ElevenLabs in Chrome): George = narrator, Roger = Sam/Mirror-Sam, Chieko (Japanese elderly) = Grandma, town = Spuds Oxley + Jessica + Mark + Chieko (T1 A-H). Whisper-checked (audio/takes_check.json): S1 A repeated "hello" -> swapped; G1 re-done firm (whispered kept as G1_whisper*). mix_ep1.py: all lines at native speed (deadlines widened).
- Rendered: 05 v3, 08 v2, 09 v2, 10 v2, 16 v2 (QA good). Running: edit/recomp_v2.ps1 (11-14 3D crowd, 17 3D mother).
- Next: assemble.ps1 (v2 order set) -> mux premaster.wav with loudnorm -> QA sheet -> DELIVERY v2 -> tell Codex.
## 22:00 v2 master DONE
edit\5oclock_ep1_v2.mp4: 1512 frames, 63.0 s, -15.6 LUFS, true peak -1.3 dBFS. Voices = ElevenLabs (Claude, via Chrome), native speed. 11-14 3D crowd + 17 3D mother recomped. Waiting on Sam's notes.

## 23:20 v3 in progress (Sam's v2 notes)
- Code done: 08 forward world (SET_FWD), leaves off the lens; 05a push on ones + body mechanics; 05c shutter hands uncrossed (K11); 09 palm outside the cup, on ones; bike grip v3 (GRIP_V3); 17 both hands cupped, poles fixed (K12), on ones; 04 glass_proj + no sheen; NEW 10b_arrive (black mirror); 15 v4 scary Listener, no shards; 18 v2 English rules (rendered).
- Sound: audio/thriller.py (siren design + Openverse CC0 in audio/recordings/openverse, earshot-checked), mixed in premaster.wav.
- Queue (one waiter each, chained): chain_v3a (08, 05a, 05c) -> chain_v3b (09, 10b, 15, 17) -> chain_v3c (04). Blocked behind Codex shots2.py; GPU_QUEUE_EP1.txt flag set.
- Then: QA probes -> full renders (04 v5, 05 v4, 08 v3, 09 v3, 10b v1, 15 v4, 17 v3) -> edit\assemble_v3.ps1 -> earshot timeline on the mix.

## 01:40 v3 DONE
edit\5oclock_ep1_v3.mp4 (1512 f, 63.0 s, -16.1 LUFS, peak -2.4), _IG.mp4, _preview.webm (plays in VS Code). Weak spot: 05b kids' arms stiff mid-cover (reused cut). Waiting on Sam's notes.

## 2026-11-25 04:55 v4 DONE
edit\5oclock_ep1_v4.mp4 (1512 f, -16.2 LUFS, peak -2.4), _IG, _preview.webm. GitHub (private): https://github.com/samrat10000/5oclock-ep1/releases/tag/v4. Not done: new spoken lines (Sam 'everyone's frozen', lines in 16/17) need ElevenLabs (no key/browser overnight) - S1 'Hello?' reused at 39.7 s; chant built from M1.
