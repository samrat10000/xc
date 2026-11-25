# QA LOG — `ep02_nobody_leaves`

Initialized `c:\Users\cross\Downloads\xc\creepy\ep02_nobody_leaves` (`10x PSX 3D upgrade of Reference Reel 1 DeeVNnAu_C0`).

## G3 PSX Textures — PASS
- Generated and inspected 7 `Closest`-filtered low-res textures in `assets/`: `psx_wall_plaster.png` (`256×256`), `psx_door_grimy.png` (`256×512`, 4-panel recessed dirty wood, brass knob, deadbolt, smudged handprint, `04` plate), `psx_carpet_crimson.png` (`256×256`), `psx_ceiling_tile.png` (`256×256`), `psx_eye_seraph.png` (`256×256` bloodshot amber-crimson iris + pinpoint pupil), `psx_star_flesh.png` (`256×256`), `psx_note_wall.png` (`128×128` `"DO NOT OPEN"` slip).

## G4 Probe Pass (`probe_v1`, `270×480` native -> `1080×1920` 4× NN) — Iterated -> PASS
- **Pass 1 issues caught & fixed cleanly before full render:**
  1. `HallShadow_Eye` stayed bright (`emission=2.2`) when `Hall_Back_Light` was off, leaving tiny floating white dots in dark doorway void on non-flicker frames; fixed via `_set_tree_hide` synced strictly to `Hall_Back_Light` (`f091–f096`).
  2. `Seraph_Cloak` showed a rounded grey specular shoulder dome; reshaped into a continuous looming tapered gothic shroud with `Specular IOR Level = 0.02` (true crushing black silhouette).
  3. Widened left door swing `-16.5° -> -25.0°`, brought `DoorLurker_EyePivot` closer to crack gap (`emission=1.15`), enlarged 6 hidden calyx `MiniEyes` (`r=0.034`) + Beat 3 unfolding clawed shadow-arms (`bevel=0.036`), and removed circular ceiling stain rings in favor of organic damp blotches.
- **Pass 2 visual inspection — PASS:** Inspected `qa/probe_v1/contact.jpg`, `f_0001`, `f_0093`, `f_0175`, `f_0245`, `f_0286`, `crop_door_lurker_005`, `crop_seraph_head_007`: `avg mean=0.159, p95=0.467, sat=0.423, 0 black, 0 frozen`.

## G5/G6 Final Master (`ep02_nobody_leaves_v1.mp4`) — PASS
- Full 288-frame PSX render (`full_v1_raw`, `270×480`) & compositor (`full_v1_comp`, `1080×1920` Bayer 4×4 + RGB555 + fog glow + Garamond Bold pixelated typewriter overlay + CRT scanlines/CA) completed cleanly.
- Verified `qa/final_v1/stats.json`: `frames 288 | avg mean 0.155 p95 0.459 sat 0.433 | PASS no black frames | PASS 0 frozen consecutive frames`.
- Encoded archival CRF 14 master (`out/ep02_nobody_leaves_v1.mp4`, `14,706,723` bytes / `14.0 MB`) and IG-ready CRF 20 preview (`out/ep02_nobody_leaves_v1_share.mp4`, `6,976,029` bytes / `6.7 MB`).
- `ffprobe` verified: `h264 yuv420p`, `1080×1920`, `24 fps`, `duration=12.000000s`, `aac 44100 Hz stereo`.
- `ffmpeg ebur128` verified: **`I: -14.2 LUFS`**, **`LRA: 1.8 LU`**, **`True Peak: -3.8 dBFS`**.
- Directly inspected `qa/final_v1/contact.jpg`, full-size PNGs (`f_0001.png`, `f_0093.png`, `f_0175.png`, `f_0245.png`, `f_0286.png`), AND full video+audio playback of `ep02_nobody_leaves_v1_share.mp4` via `read_file`: verified 0s hook silhouette, `f093` distant corridor flicker, `f175` door-crack claws, `f204` door slam + Beat 3 blood-crimson flood, 6 snapping calyx eyes + unfolding shadow-arms, 68 sample-accurate retro dialogue blips, tape pitch-sag, and safe-zone typography.


## G4/G5/G6 v2 Upgrade & Dark-Edge Fix (`ep02_nobody_leaves_v2.mp4`) — PASS
- **v2 Enhancements:** Blowout-proof `make_crisp_eye_mat` shaders (`DoorLurker_EyeMat`, `Seraph_Eye_Mat`, `Seraph_MiniEye_Mat`), `-30°` door swing with glaring eye cleanly behind jamb at `(-0.885, 1.52, 1.52)`, enlarged 6 Beat 3 calyx mini-eyes (`r=0.042`), matte-charred anatomical wall-caging arms (`make_arm_rim_mat`) with asymmetric zero-clip reach, 3 distant Beat 3 corridor watcher pairs, Beat 3 crimson pulse text glow + 2-frame slam VHS tear (`f204–f205`), and `52 Hz` Beat 3 sub-heartbeat + creaking unfurl audio (`out/ep02_audio_master_v2.wav`).
- **Dark-Edge Fix (`probe_v2` -> PASS):** Eliminated EEVEE Next stochastic shadow blotches on ceiling and side walls by setting `visible_shadow=False` on `Seraph_Cloak`, `Seraph_ShadowCalyx`, `Seraph_Petal_0..5`, and Seraph eyes/lids (preserving crisp arm cast shadows), setting `use_shadow_jitter=False` + custom light cutoffs, bumping `taa_render_samples` to `48`, adding smooth shader-level `SmoothStep(3.1m -> 6.0m)` corridor Y-depth darkening (unlocked to `0.15` during `f091–f096` flicker), and attenuating near-black Bayer dithering (`levels=40`, `dither_w=np.clip(srgb * 4.0, 0.20, 1.0)`).
- **Final v2 Verification (`qa/final_v2/stats.json`):** `frames 288 | avg mean 0.173 p95 0.501 sat 0.435 | PASS no black frames | PASS 0 frozen consecutive frames`.
- **Outputs & Verification:**
  - `out/ep02_nobody_leaves_v2.mp4`: `14,672,109` bytes (`14.0 MB`), `1080×1920`, `24 fps`, `12.000 s`, `yuv420p`, `aac 44100 Hz stereo`.
  - `out/ep02_nobody_leaves_v2_share.mp4`: `6,616,527` bytes (`6.3 MB`).
  - `ffmpeg ebur128`: **`I: -14.1 LUFS`**, **`LRA: 1.9 LU`**, **`True Peak: -3.1 dBFS`**.
  - Inspected `qa/final_v2/contact.jpg`, `f_0001.png`, `f_0175.png`, `f_0245.png`, `f_0286.png`, and full video+audio playback of `ep02_nobody_leaves_v2_share.mp4` via `read_file`: silky smooth corridor dark edges across Beats 1–3, stark Seraph silhouette, crisp peering door-crack eye & claws, readable bloodshot calyx eyes, clean arm shadows, and intact `v1` files.
