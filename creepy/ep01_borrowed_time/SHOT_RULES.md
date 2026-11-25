# SHOT RULES — `ep01_borrowed_time` (inherited from `motion2d` + adapted for Dark Surreal Horror)

1. **Resolution & Encode:** `1080×1920`, `24 fps`, `216 frames` (`9.000 s` exact loop), Blender 5 EEVEE `Standard` view transform, `16` TAA samples, final `libx264 -crf 14 -preset slow -pix_fmt yuv420p`.
2. **Real Models, Never Primitives for Organic Humans:** Girl uses `kid_girl.blend` (cap + backpack cleanly removed, bob hair intact); stalker uses real rigged humanoid (`sam_toon.blend` or `shopkeeper.blend`). Eldritch tendrils use smooth tapered 3D Bezier curves with recessed multi-part 3D eyeballs (never flat circles).
3. **Contact & Grip (`RULEBOOK.md` R3 / `SHOT_RULES.md` §12):**
   - Girl's shoes rest firmly on floor `z = 0.0` (verified via world-space bounds).
   - Girl's standing pose has relaxed elbow bend (`~15°`), hands naturally forward of thighs, subtle hip weight shift—NEVER straight-down A-pose.
   - Stalker's right hand wraps realistically around the red wooden doorframe jamb (palm inside, fingers curled over the front casing, thumb opposing)—checked in a dedicated full-size crop (`doorway_hand`).
4. **Linear Color Truth (`SHOT_RULES.md` §11):**
   - All sRGB design colors converted via `lin()`.
   - True shadow/silhouette blacks `<= 0.004` linear so silhouettes never wash out to muddy gray.
5. **Restraint & Dark-Art Palette:**
   - Strict 3-anchor gothic palette: Void Black (`#040304`), Cold Charcoal Plaster (`#4A484D`), Saturated Crimson (`#E80C0C`), plus pinpoint white (`#FFF8F0`) for stalker eyes/glints.
   - Compositor adds crimson bloom + light-wrap, periodic dust motes (on ones), subtle hand-drawn charcoal paper tooth (on twos, `~6%`), radial vignette, and fine shadow grain (`0.014`).
6. **Luminance & Audio Targets:**
   - Dark horror scene target: `mean` luminance `0.06 – 0.14`, `p95` luminance `0.42 – 0.72` (crimson clock face glows strongly without clipping flat; shadows rich without crushing doorway legibility).
   - Audio: `-14.0 to -15.0 LUFS` integrated, True Peak `<= -1.5 dBTP`, seamless `9.000 s` loop wrap (zero click at boundary), built from real acoustic samples (`SERIES_THEME/samples/`) + custom foley.
7. **2+ QA Passes Before Full Render:** Never mass-render 216 frames until `probe_v1` (50%) and `probe_v2` (100%) pass every Director's Eye check in `QA_LOG.md`.
