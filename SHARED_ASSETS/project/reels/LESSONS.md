# Reel pipeline: lessons log (gets folded into the final skill)

## Input / GLB
- Sam's GLBs can be bigger than the upload limit, so ask for a zip. The car arrived as `optimized-models.zip` holding `Night_Terror_Fastback_v2.glb` (Draco + WebP).
- The pip `bpy` 5.3 wheel can't import Draco: `libbf_intern_draco_bridge.so` is missing. Fix: `pip install DracoPy`, then `python3 -I pipeline/undraco.py in.glb out.glb` to decode every primitive into plain accessors. Blender then imports it in about 14 s.
- The Night Terror file uses native units: length runs along Y with the front at -Y, the car is about 7 m long and Z is up. Groups are named `NT 01..14`. The engine (`NT 10`) is a V6 with heads at x=±0.31, z=0.836 and stations y=-2.125/-1.74/-1.338. The roof LED matrix (`NT 07`) is 15 columns × 3 rows.
- Hide the `* hull` meshes in Cycles (they're inverted-hull outlines for real-time viewers). Keep the `* ink` crease tubes.

## Look
- No dithering (Sam dislikes it). Use a limited palette, a mode filter after quantising, and tile wipes (5×5 px tiles) for the transitions, never per-pixel noise.
- The sketch phase redraws its lines every 2 frames (12 fps "boil") and has a ragged diagonal reveal, which makes it read as hand-drawn.
- With a 6 px pixel grid, hook text at scale 2 fits about 14 characters per line, so wrap hooks to 2–3 short lines.

## Timing / sound
- Everything hangs off one clock (`timeline.py`), with the crank angle integrated through the speed ramps. The HUD RPM, the captions, the bangs and the shake are all derived from that clock, which keeps them in sync automatically.
- Bangs are synthesised one per power stroke. At real speed they fuse into a growl, and in slow-mo each one is a pitched-down boom. The music tape-stops into slow-mo and tape-starts out of it.

## Process
- A full render takes 30+ min, so run it in the background with a long timeout (the default 30 min timeout killed the first run).
- Before polishing, ask what "professional" means to Sam. Feedback so far: the stand-in test felt "basic"; they want pro quality on their own GLB.

## Sam feedback round 2 (2026-11-18)
- "I can only see the piston and nothing about the engine. It looks bad." Don't hide the car or the engine for the x-ray. Keep the whole car visible and cut away only a section: the bonnet plus the near half of the block. Implementation: a shared `CutMask` shader node group added to every car material (world-position mask -> Transparent, backfaces -> dark section colour), toggled per shot. Moving parts and wheels get the object property `nocut=1`.
- Pick the cut mode to suit each shot: `front` slice (x > XF) for the V cross-section seen from the front, `top` slice (z > ZT) for the firing order from above, `half` (y < 0) for 3/4 views.
- Material override (the normal pass) bypasses material masks, so put the CutMask in the override material too. Otherwise ink lines get drawn over the cut area.
- "The scene also needs to improve": a bare floor plane reads as basic. Use wet asphalt (noise-driven roughness), moving street lamps with real spot lights, a scrolling skyline with lit windows and a gradient sky.
- Frame-check every shot with `PREVIEW=cams.json` (one import, several cameras, half res, 8 samples) BEFORE the full render. The first full render was wasted on bad framing.
- Speed: render col/xcol at 50% (270x480) for any frame that ends up pixel art. Full res only for sketch frames; nrm stays at full res for edges. Run 3 processes × 2 threads, because scene sync of 3.5k objects is single-threaded. Points JSON: run once with POINTS_ONLY=1.
- Sam wants to watch the build live: post stills of each stage as it happens.
- The normal pass is sRGB-encoded under the Standard view transform: +Z comes out as (188,188,255), not (128,128,255). The ground mask that tames wet-road glare uses that value.
- Frame 0 is the thumbnail, so the hook text has to be fully visible on it. Never type it on from empty.
- v2 edits (rings, valves, flame, launch, streaks) are saved in pipeline/. Sam stopped the v2 render on 2026-11-18 at about 34/384 frames.
