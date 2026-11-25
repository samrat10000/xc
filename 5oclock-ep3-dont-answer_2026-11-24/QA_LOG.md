# QA_LOG · 5 O'CLOCK Episode 3

Every gate and probe pass must be recorded below with exact file paths, numerical stats from `qa_frames.py`, and full 13-point Director's Eye PASS/FAIL verdicts.

## Gate Log
- **G0 Intake:** PASS — `STATE.md`, `brief.md`, `SHOT_RULES.md`, `ERROR_CATALOG.md`, `assets/ref_s01_v4.png` created and verified.
- **G1 Story & G2 Plan:** PASS — `story/STORY.md`, `story/DIALOGUE.md`, `story/SHOT_TIMING.json`, `story/storyboard_strip.png`, `story/storyboard.html` generated and visually inspected.

## Shot 01 ("The Handprint") Probes

### Probe Pass 1 (`shots/01_handprint/src/probe1/`) — FAIL (7 root causes found)
- **Stats (`probe1/qa/stats.json`):** `mean=0.328` (-5% vs ref `0.347`, PASS), `p95=0.671` (-28% vs ref `0.929`, FAIL; `< 0.78` FAIL), `0` black frames, `0` frozen consecutive frames.
- **IK & Sun (`task-149.log`):** `IK_R_err=0.205m..0.295m` (FAIL `> 0.02 m`); `SUN_SCREEN=(0.934, 0.297)` (behind right wall/lintel).
- **Visual inspection (`contact.jpg`, `crop_face_sam_001.png`, `crop_hand_bolt_003.png`, `crop_crows_wire_004.png`, `crop_handprint_glass_001.png`):**
  1. `crop_crows_wire_004.png` + `crop_handprint_glass_001.png`: EEVEE default `surface_render_method='DITHERED'` turns the door glass and fogged handprint into noisy stipple dither.
  2. `contact.jpg`: Door glass (`X=0.02..0.66`) overflows right edge, cropping the fogged handprint in half.
  3. `crop_hand_bolt_003.png`: Sam stands too far from the brass bolt (`IK_R_err 0.20..0.29m`), so his hand stops behind the brass plate instead of wrapping the knob.
  4. `crop_crows_wire_004.png`: Vertical door stile splits right across the middle crow.
  5. `contact.jpg`: Sam's left hand sits oversized in bottom-left foreground corner with splayed thumb.
  6. `contact.jpg`: `SUN_SCREEN=(0.934, 0.297)` clipped outside right edge, making `p95=0.671` too dark.
  7. `contact.jpg`: First right-side exterior house wall (`X=6.2`) crowds the right half of the glass, blocking sunset mountains/tower.

### Probe Pass 2 (`shots/01_handprint/src/probe2/`) — FAIL (5 fixes left, stipple resolved)
- **Stats (`probe2/qa/stats.json`):** `mean=0.300` (-13% vs ref `0.347`, FAIL), `p95=0.650` (-30% vs ref `0.929`, FAIL; `< 0.78` FAIL), `0` black, `0` frozen.
- **IK & Sun (`task-170.log`):** `IK_R_err=0.0325m..0.0516m` (improved from 29cm, still `> 0.02 m`); `SUN_SCREEN=(0.519, 0.432)`.
- **Visual inspection (`contact.jpg`, `crop_face_sam_001.png`, `crop_hand_bolt_003.png`, `crop_crows_wire_005.png`, `crop_handprint_glass_001.png`):**
  - **Fixed:** `BLENDED` glass completely eliminated stipple dither! Crows & wire look clean through glass.
  - **Remaining:** (1) `crop_handprint_glass_001.png`: 1:1 texture mapped to 0.50x1.10m glass stretched fingers 2.2x tall. (2) `crop_hand_bolt_003.png`: Left arm swung forward over the bolt/right hand. (3) `crop_face_sam_001.png`: Sam angled too far away (only side of cheek/glasses sliver visible). (4) `SUN_SCREEN=(0.519, 0.432)` landed behind the vertical door stile and right-side house wall blocked horizon glow (`p95=0.650`). (5) `IK_R_err` needs `<= 0.02 m`.

### Probe Pass 3 (`shots/01_handprint/src/probe3/`) — NEAR PASS (2 numeric thresholds left)
- **Stats (`probe3/qa/stats.json`):** `mean=0.315` (-9% vs ref `0.347`, PASS), `p95=0.770` (-17% vs ref `0.929`, FAIL by 0.01 under `0.78`), `0` black, `0` frozen.
- **IK & Sun (`task-201.log`):** `IK_R_err=0.0836m..0.1045m` (FAIL `> 0.02 m`); `SUN_SCREEN=(0.790, 0.438)`.
- **Visual inspection (`contact.jpg`, `crop_face_sam_001.png`, `crop_hand_bolt_003.png`, `crop_crows_wire_005.png`, `crop_handprint_glass_001.png`):**
  - **Fixed:** Handprint proportions are now realistic human anatomy; left arm rests naturally by side; all 5 CC0 ravens sit cleanly on the wire inside the glass opening with crisp warm rims and eye glints; Sam's 3/4 face & red glasses read cleanly in f48-72.
  - **Remaining:** (1) `IK_R_err` 8.3-10.4 cm (`crop_hand_bolt_003.png` shows hand touching brass plate slightly left of knob). (2) `p95=0.770` just below `0.78` / ref `0.929` (pole cuts vertically down handprint & partial right-edge sun). (3) Start `head_yaw` at `-16 deg` so red glasses read from f01. (4) Vary exterior house silhouettes/colours along road.

### Probe Pass 4 (`shots/01_handprint/src/probe4/`) — NEAR PASS (1 mm/percent tweaks)
- **Stats (`probe4/qa/stats.json`):** `mean=0.332` (-4% vs ref `0.347`, PASS), `p95=0.812` (PASS `>= 0.78`, -13% vs ref `0.929`), `0` black, `0` frozen.
- **IK & Sun (`task-224.log`):** `IK_R_err=0.0122m..0.0244m` (only f34 was 4.4 mm over 0.020 m); `SUN_SCREEN=(0.707, 0.410)`.
- **Visual inspection (`contact.jpg`, `crop_face_sam_001.png`, `crop_hand_bolt_003.png`, `crop_crows_wire_005.png`, `crop_handprint_glass_001.png`):**
  - Sam's 3/4 face, eye & red glasses read crisply from f01 (`crop_face_sam_001.png`).
  - Hand wraps brass bolt knob cleanly (`crop_hand_bolt_003.png`); pole moved clear of fogged handprint (`crop_handprint_glass_001.png`).
  - Minor tweaks queued for Probe 5: step Sam 2 cm closer (`IK_R_err <= 0.015 m` all frames), turn crow snap `+78 deg` left toward Sam, boost outer sun glow + bloom so `p95` sits within `±10%` of ref `0.929`.

### Probe Pass 5 (`shots/01_handprint/src/probe5/`) — ALL PASS
- **Stats (`probe5/qa/stats.json`):** `mean=0.354` (+2% vs ref `0.347`, PASS), `p95=0.869` (-6% vs ref `0.929`, PASS; `>= 0.78`, PASS), `sat=0.263`, `0` black frames, `0` frozen consecutive frames.
- **IK & Sun (`task-255.log`):** `IK_R_err=0.0131m..0.0173m` across all 6 frames (`<= 0.020 m` PASS); `SUN_SCREEN=(0.707, 0.410)`.

### Director's Eye 13-Point Check (Shot 01 Probe 5)
1. **Organic things from primitives?** PASS — Hero uses `sam_toon.blend` (VRoid CC0); all 5 ravens use `crow_tehbucket_raven_cc0.glb` (Subsurf 2 + clips); maple leaves use 14-point lobed outlines.
2. **Feet/hands/limbs right?** PASS — Sam's feet planted on floor (`Z=0`); 5 ravens' toes locked to wire every frame; right hand wraps brass bolt knob (`crop_hand_bolt_003.png`, `IK_R_err <= 0.0173 m`), neutral wrist, opposing thumb; left hand relaxed by hip.
3. **Real objects match reference?** PASS — Wooden koban sliding door with brass slide-bolt, 11+1 tally scratches on jamb, mirrored `霧山交番` placard, Showa horn lathe, power lines, Japanese houses/fences.
4. **Stick figures / plain shapes?** PASS — Full 3D toon-shaded VRoid hero + real garments + hoodie strings/headphones/red glasses.
5. **Flat empty areas?** PASS — Exterior road has asphalt noise, centre dashes, kerbs, manhole, maple leaves, fences, varied houses with lit windows extending to horizon.
6. **Flat light?** PASS — `p95=0.869`, warm sun disk & dual glow shining through glass, rim on sun-facing edges (`N.sun > -0.15`), zero wall rim (`C4`).
7. **Frozen poses / missing follow-through?** PASS — `0` frozen consecutive frames; camera drift/push on ones; Sam breathing, head turn, hair/string sway, bolt slide, door settle, raven idle & 2-frame head-snap (`+78 deg` left toward Sam between f34 and f56).
8. **Outline thickness >= 0.00075 x D?** PASS — Sam hull `0.0016 m` at `~1.3 m` (`> 0.001 m`), crows `0.0042 m` at `~5.5 m` (`~0.00076 * D`).
9. **AI-made / dither look?** PASS — `BLENDED` glass eliminated all stipple dither; crisp cel edges + organic grain.
10. **Over-design / restraint?** PASS — Follows locked `01_speaker_v4` palette & restraint.
11. **Big title text over best shot?** PASS — Zero on-screen title text.
12. **Continuity?** PASS — Continues directly from Ep2 ending inside Tanaka's koban (`16:59`, 11+1 tally marks, mirrored Japanese text).
13. **Planned wow detail & dialogue space?** PASS — Fogged mirrored handprint + brass bolt + 5 ravens snapping heads left in unison (`f46-54`), leaving clean opening gap (`0.5 s`) for Narrator line 1.

### Final Full Render Verification (`shots/01_handprint/v1/01_handprint_v1.mp4`) — PASS
- **Stream (`ffprobe`):** `1080x1920`, `24 fps`, `72 frames` (`nb_read_packets=72`), `crf 14, slow, yuv420p`.
- **Stats (`v1/qa/stats.json`):** `mean=0.339` (-2% vs ref `0.347`, PASS), `p95=0.866` (-7% vs ref `0.929`, PASS; `>= 0.78`, PASS), `sat=0.270`, `0` black frames, `0` frozen consecutive frames.
- **IK (`full/meta.json`, all 72 frames):** `min=0.0122 m`, `max=0.0174 m` (strictly `<= 0.020 m`, zero sequential drift).
- **Visual inspection:** `v1/qa/contact.jpg`, `01_handprint_v1_crop_hand_f034.png`, `01_handprint_v1_crop_crows_f056.png` inspected at native resolution — crisp cel edges, wrapped 4-finger+thumb bolt grip, 5 crows toe-locked and snapping heads left toward Sam cleanly.
- **Deliverables:** `01_handprint_v1.mp4` + `f001/f034/f048/f066.png` + `crop_hand_f034.png` + `crop_crows_f056.png` + `ep3_shot01_side_by_side.png` + `ep3_shot01_crops_side_by_side.png`.
