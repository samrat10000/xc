# MISTAKES · 5 O'CLOCK Episode 3

Inherited baseline from Ep1 (`ERROR_CATALOG.md` A-K) and Ep2 (`MOTION2D_QA_LEARNINGS.md`, `CLAUDE_REVIEW_EP2.md`). New Ep3 discoveries and fixes will be logged below.

| # | Shot / Probe | Symptom | Root cause | Fix -> Rule |
|---|---|---|---|---|
| 1 | 01 Probe 1 | Glass & fogged handprint rendered as stipple dither noise (`crop_crows_wire_004.png`) | Blender 5.0 EEVEE defaults transparent materials to `surface_render_method = 'DITHERED'` | Always set `mat.surface_render_method = 'BLENDED'` + `use_transparency_overlap = False` on glass/alpha planes (`R0` no dither) |
| 2 | 01 Probe 1 | Right-hand IK error 20-29 cm (`crop_hand_bolt_003.png`) | Character stood ~0.60 m from bolt knob and stayed stationary as door slid +0.145 m | Place actor within comfortable arm reach (`<= 0.45 m`), lean/step torso with sliding object, verify `IK_err <= 0.02 m` |
