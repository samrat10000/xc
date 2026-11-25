# QA LOG — `ep01_borrowed_time`

## G0 Intake & Asset Inspection — PASS
- Inspected `kid_girl.blend`, `sam_toon.blend`, and `shopkeeper.blend` via Blender 5.0.1 (`assets/asset_inspection.json`).
- `kid_girl.blend`: `Kid_girl_Rig` (`139` bones, VRM `QUATERNION` rest). Cap (`Kid_girl_yellow_cap`) and backpack (`Kid_girl_randoseru`) are separate objects and can be cleanly deleted, leaving `Kid_girl_Hair001` (bob haircut), `Kid_girl_Body`, `Kid_girl_Face`, `Kid_girl_Face_Outline` intact. Note: rest feet bottom is `z = 0.319 m` -> must ground lowest world vertex to `z = 0.0`.
- `sam_toon.blend`: `Sam_Rig` (`117` bones, relaxed A-pose, full finger chains `J_Bip_R_Index1..3`, `Middle1..3`, `Ring1..3`, `Little1..3`, `Thumb1..3`). Headphones (`Headphone_*`), glasses (`Glasses_Lens_*`), and hood roll/aglets are separate meshes and can be cleanly stripped for a gaunt stalker silhouette.

## G3 Textures & Dials — PASS
- Generated and visually inspected `assets/wall_charcoal.png` (`2048×2048`), `assets/floor_wood.png` (`1024×1024`), `assets/clock_main_dial.png` (`1024×1024`), and 11 vintage word-clock dials in `assets/clocks/` (`LOST`, `FADE`, `WAIT`, `EMPTY`, `STILL`, `ALONE`, `LATE`, `OFF`, `HUSH`, `STAY`, `DON'T TURN`).
- Visual check: Baskerville Roman numerals (`I–XII`), minute track, and spiderweb glass crack on `clock_main_dial.png` are crisp; `wall_charcoal.png` has authentic gothic plaster blotches and organic vertical charcoal hatching; `clock_EMPTY.png` vertical stack and `clock_DONT_TURN.png` blood-red flip read cleanly.

## G4 Probe Pass 1 (`probe_v1`, 50% @ `540×960`) — FAIL -> Fixed
- Inspected `qa/probe_v1/contact.jpg`, `f_0001`, `f_0086`, `f_0154`, and all 7 crops.
- Issues caught:
  1. `MainClock_Glass` rendered as opaque frosted sheet over `MainClock_Dial`, hiding Roman numerals & hands.
  2. Square word-clock frame cubes (`y=-0.006, depth=0.014`) extended in front of dial planes (`y=-0.012`), hiding `ALONE` & `OFF` text; disk UVs were vertically flipped (`HUSH` upside-down).
  3. Camera `sensor_fit='VERTICAL'` used default `sensor_height=24mm` with `36mm` lens, cropping doorway and right clocks.
  4. `kid_girl` arms angled ~24° out (A-pose); stalker used right arm instead of left arm nearest jamb, and eye bone offset was wrong.
  5. `Hall_Interior_Glow` too dark to silhouette black tendrils cleanly.
- Fixes applied: Removed opaque frosted glass & switched main dial to pure emission; placed square frames strictly behind dial planes and fixed upright disk UVs; set `lens=24.5mm`; dropped `kid_girl` arms 79°; switched stalker grip to left arm; lightened hallway fog (`#36373E`, `0.20`).

## G4 Probe Pass 1b (`probe_v1b`, 50% @ `540×960`) — PARTIAL -> Fixed for Pass 2
- Inspected `qa/probe_v1b/contact.jpg`, `f_0001`, `f_0086`, `f_0154`, and all 7 crops (`avg mean=0.133, p95=0.345`).
- Huge jump in quality: Roman numerals (`I–XII`), all word-clocks, crimson light, `kid_girl` bob silhouette + relaxed arms, `DON'T TURN` flip, stalker doorway hand grip, and multi-eyed tendrils all read cleanly.
- Remaining issues caught in `probe_v1b` crops:
  1. `crop_stalker_eyes_003.png`: Sam's glasses frames, headphone band, and white hoodie drawstrings are `CURVE` objects in `sam_toon.blend` and were not removed by mesh-only filter! Fixed by keeping ONLY `{"Sam_Rig", "Body", "Face", "Hoodie_Sleeves"}`.
  2. `f_0001.png`: `Hall_Ceil` (`y=1.20, size_y=2.45`) poked out to `y=-0.025`, casting a black horizontal rectangle across upper-left of `MainClock_Dial`. Fixed by keeping all hallway geometry behind `y=+0.08`.
  3. `crop_clock_flip_001.png`: Girl's head slightly touched left corner of `ALONE`/`DON'T TURN` diamond. Shifted `ALONE` to `(0.56, 1.54)` & `LATE` to `(0.80, 1.54)`, thinned word-clock hands (`0.0038`) for crisp readability.
  4. `crop_doorway_hand_002.png`: Hand had not yet reached jamb at `f058`; started reach at `f038 -> f056`.
  5. `crop_tendril_eyes_005.png`: Tendril tips ended blunt; enabled `use_fill_caps=True` and tapered tip radius to `0.06` with deeper S-curves.

## G4 Probe Pass 2 (`probe_v2`, 100% @ `1080×1920`) — PASS
- Re-rendered all 6 key frames (`1, 58, 86, 122, 154, 216`) at full `1080×1920` and widened `Hall_Interior_Glow` (`2.20×2.80`) to eliminate the sharp vertical box edge inside the doorway.
- Inspected `qa/probe_v2/contact.jpg`, full `1080×1920` PNGs (`f_0001`, `f_0086`, `f_0154`, `f_0216`), and all 7 crops:
  - `MainClock_Dial`: Crisp Baskerville Roman numerals (`I–XII`), minute track, spiderweb glass crack, 3D bezel, and clean 3D wrought-iron hands (`0` artifacts).
  - All 10 word-clocks (`LOST`, `STAY`, `STILL`, `WAIT`, `EMPTY`, `FADE`, `HUSH`, `ALONE`, `LATE`, `OFF`) legible & clear of obstructions; `ALONE -> DON'T TURN` hidden flip verified cleanly in `crop_clock_flip_005.png`.
  - Girl (`kid_girl.blend`): Cap/backpack 100% removed, relaxed arms/hands, crisp crimson rim on bob hair & shoulders, grounded at `z = 0.0`.
  - Doorway Intrusion 1: Stalker stripped of all `CURVE` accessories (no glasses/headphones/strings), left hand & curled fingers cleanly wrap crimson front edge of doorframe jamb (`crop_doorway_hand_003.png`), sharp white pinhole eyes (`crop_stalker_eyes_003.png`).
  - Doorway Intrusion 2: 5 tapered S-curved black tendrils with crimson rim and 8 recessed darting eyeballs (`crop_tendril_eyes_005.png`).
  - Loop symmetry: `f_0001` and `f_0216` align seamlessly.
  - Luminance note: `avg mean=0.134`, `p95=0.346`, `sat=0.745`, `0` black/frozen frames. (Rec.709 `Y = 0.2126*R` naturally reads ~0.35 on saturated pure crimson `#FF1010` peak pixels even when visually bright.)

## G5/G6 Final Master (`ep01_borrowed_time_v1.mp4`) — PASS
- Full 216-frame render & 2.5D compositor complete (`avg mean=0.128, p95=0.339, sat=0.776`, `0` black frames, `0` frozen frames via `qa_frames.py`).
- Encoded archival CRF 14 master (`out/ep01_borrowed_time_v1.mp4`, `88,919,647` bytes) and compact CRF 20 shareable MP4 (`out/ep01_borrowed_time_v1_share.mp4`, `10,569,895` bytes).
- Verified audio loudness on final MP4 via `ffmpeg ebur128`: `I: -14.8 LUFS`, `LRA: 3.0 LU`, `True Peak: -2.1 dBFS` (passes `-14 to -15 LUFS` and `<= -1.0 dBTP`).
- Directly inspected `qa/final_v1/contact.jpg`, full-size PNGs (`f_0001.png`, `f_0086.png`, `f_0154.png`, `f_0216.png`), and full video+audio playback of `ep01_borrowed_time_v1_share.mp4` via `read_file`: smooth timing, crisp doorframe hand grip, stalker blink, `III:00` slam, `ALONE -> DON'T TURN` hidden flip, tapered multi-eyed tendrils, and seamless loop verified.

## `v2` Probe Passes (`probe_v2_rev`, 100% @ `1080×1920`) — Iterated -> PASS
- **Pass A/B (caught & fixed before full render):**
  1. Replaced `sam_toon.blend` and bright googly eyeballs with bespoke hunched figure + painted `assets/horror_eye.png` (bruised-ivory bloodshot sclera, small oxblood iris, pinpoint pupil) + sculpted 3D almond eyelids on 4 bulbous creeping shadow-entities.
  2. Probe Pass A/B crops caught three visual issues: (a) flat Bezier arm-cap cutout on stalker's shoulder, (b) flat-shaded polygon specular squares on eldritch entity heads + straight wisp spikes, and (c) pear/bowling-pin upper-torso taper + flat horizontal toothpick fingers on the first stalker silhouette.
- **Pass C (`probe_v2_rev` final check) — PASS:**
  - Rebuilt `_make_stalker_torso` with emaciated waist, inverted-V ribcage expanding to broad hunched `24cm` shoulder shelf, hanging passive right shadow-arm, razor-narrow sunken eyes, and 4 curved Bezier talons hooking around the crimson woodgrain doorframe corner onto its front face.
  - Added smooth shading (`f.smooth = True`), rounded snout domes, `0.62` wet-shadow roughness, and organic S-curved wispy tendrils on the 4 eldritch entities.
  - Upgraded room/compositor: procedural gradient `Hall_Interior_Glow` (eliminated doorway horizon line), crimson woodgrain doorframe bump shader, gothic lance/spade hands on giant clock, reduced eye bloom threshold (`0.86`) and dust motes kept clear of girl's torso, velvety grain `0.0075`.
  - Verified both mid-retreat probe frames (`f_0108` and `f_0182`) and 100% crops: zero detached/lingering eyes on either entity type.

## `v2` Final Master (`ep01_borrowed_time_v2.mp4`) — PASS
- Full 216-frame render (`full_v2_raw`) & 2.5D compositor (`full_v2_comp`, `avg mean=0.1296, p95=0.3427`) completed cleanly; all `v1` files preserved untouched.
- Verified `qa/final_v2/stats.json`: `frames 216 | avg mean 0.130 p95 0.344 sat 0.730 | PASS no black frames | PASS 0 frozen consecutive frames`.
- Encoded archival CRF 14 master (`out/ep01_borrowed_time_v2.mp4`, `64,453,005` bytes / `61.5 MB`) and shareable CRF 20 preview (`out/ep01_borrowed_time_v2_share.mp4`, `4,477,325` bytes / `4.3 MB`) using `out/ep01_audio_master_v2.wav` (wooden doorframe creak + `III:00` cold-draft gust).
- `ffprobe` verified: `h264 yuv420p`, `1080×1920`, `24 fps`, `duration=9.000000s`, `aac 44100 Hz stereo`.
- `ffmpeg ebur128` on final MP4 verified: **`I: -14.8 LUFS`**, **`LRA: 3.0 LU`**, **`True Peak: -2.4 dBFS`**.
- Directly inspected `qa/final_v2/contact.jpg`, full-res PNGs (`f_0086.png`, `f_0108.png`, `f_0154.png`, `f_0182.png`), and full video+audio playback of `ep01_borrowed_time_v2_share.mp4` via `read_file`: verified looming humanoid silhouette + gripping claws, unified stalker retreat with zero lingering eyes, `III:00` shockwave & girl flinch/hair gust, creepy heavy-lidded bloodshot horror eyes locked inside retreating shadow bodies, and crisp loop sync.
