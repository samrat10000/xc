# STATE · `creepy` Episode 2 — "Nobody Ever Leaves" (`ep02_nobody_leaves`)

- **Status:** COMPLETE (`v2` mastered and verified; `v1` preserved untouched)
- **v2 Master Output (CRF 14):** `c:\Users\cross\Downloads\xc\creepy\ep02_nobody_leaves\out\ep02_nobody_leaves_v2.mp4` (`14.0 MB` / `14,672,109` bytes, `1080×1920`, `24 fps`, `288 frames`, `12.000 s`)
- **v2 Shareable Preview (CRF 20):** `c:\Users\cross\Downloads\xc\creepy\ep02_nobody_leaves\out\ep02_nobody_leaves_v2_share.mp4` (`6.3 MB` / `6,616,527` bytes)
- **v2 Audio Master:** `c:\Users\cross\Downloads\xc\creepy\ep02_nobody_leaves\out\ep02_audio_master_v2.wav` (`12.000 s`, 68 synced PS1 dialogue blips + detuned Rhodes + `52 Hz` Beat 3 sub-heartbeat + creaking arm unfurl + SFX)
- **v2 QA Contact Sheet:** `c:\Users\cross\Downloads\xc\creepy\ep02_nobody_leaves\qa\final_v2\contact.jpg`
- **v1 Master Output (CRF 14, preserved):** `c:\Users\cross\Downloads\xc\creepy\ep02_nobody_leaves\out\ep02_nobody_leaves_v1.mp4` (`14.0 MB` / `14,706,723` bytes)

## Gates Status
- [x] **G0/G3:** Scaffold & 7 low-res PSX textures (`psx_wall_plaster`, `psx_door_grimy`, `psx_carpet_crimson`, `psx_ceiling_tile`, `psx_eye_seraph`, `psx_star_flesh`, `psx_note_wall`)
- [x] **G4 Probe Passes (`v1` & `v2`, `270×480 -> 1080×1920`):**
  - `v2` upgrades: blowout-proof eye shaders (`make_crisp_eye_mat`), `-30°` door crack with unclipped peering bloodshot eye above the 4 claws, enlarged 6 Beat 3 calyx mini-eyes (`r=0.042`), anatomical matte-charred wall-caging arms with zero wall clipping, 3 distant corridor watcher eye pairs, closer Beat 3 Seraph loom (`y=3.00->2.20`), and 2-frame door-slam VHS tear (`f204–f205`).
  - Dark-edge fix: disabled stochastic EEVEE shadow jitter (`use_shadow_jitter=False`), disabled Seraph cloak/petal/eye self-shadows (`visible_shadow=False`) while keeping arm cast shadows, added shader-level smooth corridor Y-depth darkening (`SmoothStep 3.1m->6.0m`, unlocked to `0.15` during `f091–f096` flicker), bumped TAA samples `16 -> 48`, and attenuated near-black Bayer dithering.
- [x] **G4 Full Render & PSX Compositor (`full_v2`):** All 288 frames @ `270×480` rendered -> Bayer 4×4 (`levels=40`, dark-attenuated) + fog bloom + `4×` Nearest-Neighbor (`1080×1920`) + pixelated Garamond Bold serif typewriter overlay + CRT scanlines/CA (`avg mean=0.173, p95=0.501, sat=0.435, 0 black, 0 frozen`)
- [x] **G5/G6 Audio & Master (`v2`):** Encoded CRF 14 + CRF 20 MP4s, verified `ffprobe` (`1080×1920`, `24 fps`, `12.000 s`, `yuv420p`), `ebur128` (`I=-14.1 LUFS`, `LRA=1.9 LU`, `True Peak=-3.1 dBFS`), and directly watched/listened to `ep02_nobody_leaves_v2_share.mp4` via `read_file`.
