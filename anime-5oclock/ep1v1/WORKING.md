# 5 O'CLOCK Ep1 v1 "Three Notes": working log (Claude, 2026-11-22)

## What was made
- Storyboard: ep1_storyboard.png (5 panels).
- Shots (1080x1920, 24 fps, animated on twos): 001_mirror 3.0 s, 002_speaker 3.5 s, 003_sam 3.5 s, 004_street 3.0 s, 005_answer 3.0 s. Total 16.0 s.
- Each shot clip with sound: NNN_name_v1.mp4. Full cut: ep1_v1_full_cut.mp4 (only for after the shots pass).

## How (all in src/)
- Drawing: pycairo vector shapes in code (no AI images). Flat cel fill + one shadow tone + thin warm-dark line, tiny line boil on twos.
- Streets: a pinhole camera over a 3D layout (houses, block walls, poles, wires, vending machine, the 1964 radio tower), drawn flat. Depth blur = gaussian per depth band. Night copy = same world, night palette.
- Mirror: night street warped into the convex mirror with a real fisheye remap (lib.fisheye_into), flipped like a reflection.
- Sam: sam.py, one fixed design (black messy hair, red glasses, charcoal hoodie, black headphones). Pose params change the drawing: eye dart (2 drawings), head lift, brows, blink (3 drawings), fingertips over the cup, cup off the ear.
- Render: python3 render.py shotNNN <frames> <outdir> (4 processes), ffmpeg to mp4. ~1.2 s/frame on 4 cloud CPUs.
- Score (score.py): only real recorded samples from VSCO-2 CE (Ivy Audio pipe organ loud+quiet, organ blower noise, violin/viola/cello sections, marimba, glock, timpani, gong, claves ticks). A minor ostinato 0.3 s pulse -> F major on the 4th note. Original melody, not Zimmer's.
- Chime: marimba+glock F4 A4 C5 through a loudspeaker model (band-limit, saturation, mountain echoes 0.42/0.86/1.5 s). 4th note F5 comes dry and close from the mirror at 14.2 s.
- SFX (sfx.py): Freesound via Openverse. Crows: "210701 American Crows..." by TRP (CC0) pitched down 3 st, "Crows.wav" by ken788 (CC0). Wind in power lines: "Tuuli sähkölangoissa / Wind humming and howling in..." (CC-BY, credit the creator). Distant town: "ShinNakanoOmekaidoLateNight..." by markystar (CC0).
- Mix: amix + limiter, loudnorm I=-15 LUFS.
