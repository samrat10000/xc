# Episode 3 build decisions

Sam authorized use of the supplied buggy and adaptation of the cabin/roof sequence on 2026-11-21. He subsequently said to make the needed modifications and build it.

- Preserve the supplied original at `SHARED_ASSETS/originals_from_sam/Night_Terror_Fastback_v2.glb`. It is an open, one-seat buggy despite its filename. Verified by Blender import and a CPU studio render in `audit/original-car-check.png`.
- The imported dimensions are approximately 4.87 × 2.30 × 2.42 metres. Front is -X in the imported scene. The README's seven-metre, -Y description does not describe this file.
- Make a versioned two-seat cockpit refit. Keep the vehicle's distinctive armor, tires, skull and equipment. Add passenger seating/handholds and reinforced roll-cage rails.
- Shots 4, 13, 16 use a camera mounted on the open cockpit's crossbar. Remove references to spidered windscreen, sealed headliner, windscreen shoulder framing and wind through newly opened roof holes.
- Shot 13: creature claws hook and buckle the upper cage; rider fires upward through the open gap. Shot 14: raised antlers meet the 3.81 m lip and snag the creature off the cage. Anatomical left antler breaks; source original remains intact.
- Shot 17: look over Sam's shoulder between cage rails. Quiet is relative: engine ticks, tunnel reverb and open-cockpit wind remain.
- `SHOTS.json` preserves the supplied storyboard. Adaptations live separately in `SHOTS_BUILD.json` so the original plan remains reviewable.
- A different car is present in `ep1/car/`; it is not substituted after Sam chose the buggy.
- Claude is rendering on the 4 GB GPU. Use CPU for limited scene checks and keep GPU jobs sequential. No claimed GPU lock is shared with Claude until a render actually starts.

Quality gate: a blocking render is not a final shot. Check hands/contact, proper scanned vehicle props, exact audio stems, damage continuity and motion before final encoding.
