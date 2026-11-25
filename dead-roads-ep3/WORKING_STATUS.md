# Episode 3 working status

This is an unfinished build, not a final episode. Current working source is `sc/shot_builder_v008.py`, called by `sc/ep3.py` for versions other than v006/v007. Earlier builders and renders are retained for diagnosis. Use the actual working folder, not an archived shared source snapshot, to run commands.

## User decisions

- Sam authorized building Episode 3 from the brief and storyboard.
- The supposedly named fastback in SHARED_ASSETS is actually an open buggy. Sam explicitly chose the buggy and authorized adapting the cabin/roof sequence, then said to make needed modifications and build it.
- Use two seats and roll-cage damage. No enclosed windscreen/headliner story elements. Another actual car file exists in `ep1/car/` but must not silently replace Sam's chosen buggy.
- Sam confirmed Claude is rendering and gave discretion about GPU use. The 4 GB GPU remains heavily occupied by other Blender jobs, so current checks use CPU. Do not terminate their processes.
- Sam signed into Flow Music after being asked and replied done. Logged-in profile shown: sireportal43, free plan. A Google One access banner is present; do not grant expanded subscription access or buy an upgrade.
- Sam asked for a sample. Current rescue still shown; the genuine one-second, 24-frame silent rescue sample is complete at `out/ep3-rescue-motion-sample-v001.mp4` and was presented. Sam requested another sample; `sc/render_jturn_sample.py` is rendering the full three-second J-turn from v007 shot11, CPU only.

## Artifacts and validation

- RESEARCH.md covers the required tools with official sources and tested/untested status. Five-line findings were reported before building.
- SHOTS.json extracted from the literal storyboard array: exactly 19 shots, 1,152 frames, 48 seconds, 24 fps.
- SHOTS_BUILD.json and BUILD_NOTES.md record the buggy adaptation. Credits and sound cue sheet exist.
- Source snapshot `SHARED_ASSETS/ep3/build-v006/` is an old review snapshot, not the current source. Its early creature caches were incomplete. New snapshot and shared README/status update are still needed.
- Original car cache and optimized buggy preserve the supplied source. Optimization reduced 2,154 objects to 358. Actual axle pivots were corrected in newer builder (original assembly origins were wrong for spinning wheels).
- Trike `.blend` append caused native Blender crashes; a clean GLB-derived wreck cache fixes that. Trike roll axis was corrected to X in the current source.
- Creature v001 caches contained skeletons only and are invalid. v002 restored all geometry but inherited newer-Blender library issues. Use **v003** caches, round-tripped through skinned glTF in Blender 5.0.1. Counts: Husk 47 meshes, Runner 26, Screamer 29, each 163 bones.
- Current asset imports filter null objects; current cast v003 scenes have passed loading and rendering. Glass shadow transmission and skin/lighting changes for car jam are still being refined.
- Car jam contains 27 instances of two licensed Khronos car designs and 40 seated Husks. These are two designs, not six distinct car models. Latest code aims at an actual head-bone position and uses world-axis quaternion head turns with 0–2 frame offsets.
- Rescue finger curl was measured against opposing forearms. Correct hinge is negative local Z for this rig, not the initially used positive X. Latest still is under `frames/v012/shot06/f0030.png`; current source further adds close-up DOF.
- Assembler rejects incomplete frame sets. No `out/ep3.mp4` or final audio mix has been created. Do not label the stills as a finished episode or build a slideshow and call it animation.

## Current render review coverage

- v007: 1–6, 11, 12, 14, 17, 18.
- v006: 6–19 baseline, with defects found later (notably missing cached creature geometry and old pivots).
- v008: improved 1–3, 6, 8, 9, 18; shot 10 failed on inherited library null refs.
- v009: improved 6; 18 native-crashed during library/material loading.
- v010: 18 failed before render.
- v011: 18 passed with clean v003 character library; lighting/skin/aim still needed corrections afterward.
- v012: 10, 14, 7, 12, 17, 6, 5 passed, but current source has subsequent improvements not all rendered yet.
- A complete selected contact sheet with manifest of actual image versions is still needed; `out/ep3-v006-contact-sheet.jpg` has missing 1–5 and is not the requested complete sheet.

## Next work

1. Finish rescue motion sample; ffprobe verifies 24 frames, 24 fps, one second. Present as silent blocking sample.
2. Resume Flow Music UI after the user restores the minimized Chrome window (requested asynchronously). Native CUA window 656202, `scoreChrome` binding if REPL alive. Chrome extension browser 3 is a different tab inventory; earlier getTab calls timed out. Native controls work after restoring/raising the window. Do not automate authentication.
3. Submit the concrete score brief (`audio/SCORE_BRIEF.md`) as text; no need to upload private files. Verify credits/cost UI before any paid action. Generation and download are now complete: `audio/ep3-flow-score-source-v001.wav`, 61.226667 s stereo 48 kHz. Metadata is saved beside it and in shared audio; editorial conform and approval remain pending.
4. Render latest corrected 7, 10, 17, 18, 6 as needed. Improve readability without washing out the faces. Test key motion frames, not only midpoint stills.
5. Still missing/incomplete animation beats: driver climbing out in shot 5, genuine reload in 16, actual separated left-antler prop/snap and matching skid in 14–15, stronger leap/gallop articulation. Current antler skid prop is generic and must be replaced by actual source geometry.
6. Only after picture checks and GPU availability, render final sequences and mix isolated real SFX plus score. Approved isolated Screamer/Stalker source takes are not in this shared mirror; old shootout mix WAV is not a source stem. Locate/request precise source files rather than claiming new voices match.
7. Publish fresh versioned shared package, selected stills/contact sheet, and log lines. No social publishing without Sam's preview and go.

## UI and tool limits observed

- Opening local file: HTML in browser was security-blocked. Read/extracted storyboard locally; do not bypass that browser policy via alternate surface/server.
- Native Chrome reads work while minimized, but clicking/screenshot fails. User is asked to leave the Flow window restored; it can be occluded.
- Flow Music sign-in is confirmed; no password entered by Codex. Google One access remains ungranted.
- Network downloads require approved elevated shell. Only official CC0 Camera Shakify data, two reference photo previews (internal only), and licensed Khronos cars were downloaded. Data source hashes/licenses are stored.

## Latest checks

- v015 shot18 glass now has a 4 mm solidified shell; visible occupants replace infinite-refraction patches. Still low-resolution blocking.
- v013 shot7 camera is too high; belt insert needs reframing. Driver exit5/reload16 remain incomplete. Antler split/floor fixes exist in current builder, but latest14/15 need rerender.
- Sam does not know where the approved creature voice takes are. Current mirror contains only old mixed WAV; do not claim it is an isolated source.
