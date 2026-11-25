# ERROR CATALOG: what goes wrong when an AI builds a 2D/toon shot, and how to prevent it

Source: 5 O'CLOCK Ep1 "The Fourth Note", shot 15 "The Listener" (2026-11-23). v1 by Sonnet 5.5 (4 probes, below the bar), v2 by Opus 5.5 (4 probes, clearly better, not final).
Purpose: read this BEFORE building any shot. Each category has the symptom (what the director sees), the root cause, and the
prevention check to run before a full render. Add new entries every time a probe or the director finds a new failure.

---

## A. Readability: the thing does not read as what it is
| # | Symptom | Root cause | Prevention check |
|---|---|---|---|
| A1 | A creature reads as an object (horn head = "raspberry", "mushroom", "tree", "dandelion") | Silhouette designed in 3D close-up, never judged at phone size; radial/symmetric layout; tall thin trunk under a round mass = tree | Render the silhouette ALONE (black on white) at 270x480. Ask: "what would a stranger call this in one word?" If the answer is not the intended thing, redesign the silhouette before any detail |
| A2 | A giant does not read as a being | No body mass, no shoulders/posture; head on a pole | Giants need a posture: hunched shoulders, a lean toward the target, a mass that is partly hidden (peering over a ridge) |
| A2b | Creature body reads as an object (goblet/bowl with a stick through it; "plant in a pot") | Torso and shoulders above the horizon line as round blobs, neck continuing below them, straight vertical neck | Hide the body behind the horizon; show only shoulder tops sloping into it; give the neck a CURVE and the head a LEAN toward its target (posture = alive). Re-run the silhouette test after every body change |
| A3 | Parts read as other objects (fingers = barrels/pegs, palm = saucer/UFO) | Texture bands across cylinders; rim light outlining a flat disc; parts too uniform | Check each part at full size in a crop; remove banding textures on sideways links; give flat parts no rim |
| A4 | Openings read as discs/eyeballs instead of holes (horn mouths) | Interior not dark enough; no contrast between lip and inside | Mouth/hole = lit lip + true-black interior (see C2). Keep a 3/4 view, not full-frontal |
| A5 | An effect reads as a different effect (glass cracks = lightning) | Random large turns + glow | Physical reference first: glass cracks are long straight runs with small sharp kinks, thin, little glow |
| A6 | A sky event reads as a "blue ribbon"/band | Flat colour fill without depth or edge | Give it a different world inside (night sky + stars), bright glass edges, and fractures spreading out |

## B. Scale and staging
| # | Symptom | Root cause | Prevention check |
|---|---|---|---|
| B1 | Colossal thing looks small/toy | No size references; no aerial haze; moves fast | Put known-size objects in frame (houses, poles, a person); haze that thickens toward the horizon; slow movement with mass (ease-out over seconds, not frames) |
| B2 | Two parts of the same giant at inconsistent scale (tiny hand, huge head) | Parts built separately, never compared in frame | Measure parts in world units against each other; a hand is ~0.8-1.0 x head height |
| B3 | Ground-level camera makes everything a flat slab | Camera at 1.6 m looking at distant layers | Lift the camera (hillside, rooftop, bridge) so ground, roads and roofs are visible and give depth |
| B4 | Important things cut off at the frame edge / empty top or bottom of frame | Positions set in world units without checking projection | Project key points with the shared camera before rendering; keep subjects inside 8-92% of width; fill large empty areas (clouds, structure) |
| B5 | The rise/reveal is over too fast | Timing chosen per-frame without thinking of mass | Big reveals take most of the shot; hold the final pose >= 1 s |

## C. Rendering pitfalls (Blender / EEVEE toon)
| # | Symptom | Root cause | Prevention check |
|---|---|---|---|
| C1 | Distant object missing entirely | Camera clip_end default (100 m) | Set clip_start 0.5, clip_end > the farthest object (e.g. 8000) |
| C2 | "Black" renders grey | Emission colours are LINEAR (0.025 -> sRGB ~0.17) | True black <= 0.004 linear. Measure pixel values in the pass, not by eye |
| C3 | Pole/prop upside down or pointing the wrong way | Rotation sign guessed (lathe axis +Y rotated -90 about X points DOWN) | Write the axis maths in a comment; probe one frame of the prop alone |
| C4 | Cream/odd bright triangles on walls | Rim light (facing + sun dot) misfires on flat or flipped faces | No rim on flat architecture; rim only on rounded characters/creatures |
| C5 | Rust/streak texture becomes rings | Texture runs along local Z, links point along Y | Use plain toon on sideways links, or map texture along the link axis |
| C6 | Everything too bright/flat at dusk | Fill light pushes camera-facing faces over the lit threshold | Fill <= 0.12 for dusk/backlit shots; check what tone camera-facing faces land in |
| C7 | Script fails in Blender with U+FEFF | File saved with a BOM (PowerShell Set-Content -Encoding utf8) | Write files as UTF-8 without BOM |
| C8 | Sun direction rim on the wrong side | Library's fixed sun vector (SUNV) not updated for the shot | Replace SUNV in the library source before exec when the sun moves |

## D. Compositing and depth
| # | Symptom | Root cause | Prevention check |
|---|---|---|---|
| D1 | Parts that should be hidden show (arm visible below the crack lip) | 2D mask has no depth information | Occlude in 3D: a holdout wall with the opening as a hole, rebuilt per frame |
| D2 | Object looks semi-transparent / background detail shows through | Haze/tint mixed with the SHARP background image | Haze colour = heavily blurred background + air colour, never the sharp plate |
| D3 | Painted layers slide against the 3D layer | Separate camera maths in painter and Blender | ONE shared camera module (pitch, lens, shake, positions) imported by both |
| D4 | Giant white glare washes out the subject | Sun glow + horizon colour + bloom all stacked behind the subject | Put the sun off the subject; bloom threshold >= 0.86; measure p95 and check the subject's silhouette contrast |
| D4b | A hard bright line across the sky | A procedural cloud band starts abruptly and its rim/underside highlight fires along the band edge | Fade bands in over >= 8 degrees; no rim highlight on bands far from the sun |
| D5 | Ground missing at frame bottom (sky shows through) | No ground plane under the painted town | Always lay a ground plane first; check the bottom 15% of every probe |

## E. Real-world density and truth
| # | Symptom | Root cause | Prevention check |
|---|---|---|---|
| E1 | Town = flat boxes/slabs | Painted silhouettes instead of 3D; no roof/window detail | Build towns in 3D (joined meshes per material): tiled roofs, lit windows, antennas, water heaters, poles and wires |
| E2 | Mountain = plain slab; treeline = saw blade | Single fill colour; alternating spikes | Texture + base haze + sun-side rim; trees in random clumps with gaps |
| E3 | Prop reads wrong from the camera angle (horn seen from behind = paddle) | Orientation chosen in world space without checking the view | Turn props so their identifying profile faces the camera |

## F. Process failures (agent behaviour)
| # | Symptom | Root cause | Prevention check |
|---|---|---|---|
| F1 | Many probe rounds wasted on avoidable bugs | Building without thinking through axes, clipping, encodings | Before the first probe, list the 5 most likely technical failures and guard each one |
| F2 | Fixes guessed, not diagnosed | Re-rendering hoping for a change | Every failing check: one-sentence cause, backed by a number or a pass-level image (e.g. count near-black pixels in the cel pass) |
| F3 | Reviewing only the composite | Errors hidden by later layers | Look at each pass alone (cel on magenta) when a part looks wrong |
| F4 | Motion never judged | Only stills sampled | Watch the clip or a 12-frame strip at even spacing; state clearly when motion was not watched |
| F5 | Background job reported "failed" when it succeeded | ffmpeg writes its banner to stderr, PowerShell treats it as an error | Use `-loglevel error` and verify the output file (frame count, size) instead of the exit status |
| F6 | Weaker model needed more passes for the same shot | Spatial reasoning and art judgement are where small models slip | Use the strongest model for new hard shots, character/creature design and QA verdicts; smaller models for renders, encodes, repeats of a locked recipe |

## Pre-flight checklist (run before the first probe of every shot)
1. Silhouette test at phone size (A1, A2).
2. Scale table of every big part in metres, and against a known-size object (B1, B2).
3. Project key points with the shared camera: nothing important clipped, no empty thirds (B4).
4. Camera clip range, sun vector, lathe axes, encodings (C1, C3, C7, C8).
5. Dusk/backlit light levels: fill <= 0.12, no rim on flat walls (C4, C6).
6. Anything behind an opening is occluded in 3D (D1).
7. Haze uses blurred colour only (D2).
8. Ground plane present; road/roof/window density present (D5, E1).

## G. Characters and garments (cast v2, 2026-11-23)
| # | Symptom | Root cause | Prevention check |
|---|---|---|---|
| G1 | Kids read as teens | Mild bone scales; teen clothes (uniform, knee socks) | Legs x0.68, lower legs x0.84, spine x0.80, arms x0.80, head x1.28-1.30; child clothes (T-shirt, shorts/skirt), yellow cap, randoseru |
| G2 | Grandma reads as a young woman in grey hair | No posture; open young eyes | Age posture saved in the pose (spine/chest/neck forward 10-12 deg each, knees bent); heavy lids (Fcl_EYE_Close 0.3) |
| G3 | Apron swings backward into the skirt when the body bends | Garment rigidly parented below the bending bone's pivot | Hang garments from the top bone and counter-rotate them plumb after posing (gravity), or rebuild them on the posed body |
| G4 | Side view not rendered / turned rigs ignore rotation | Rig objects in quaternion mode | Set rotation_mode before rotation_euler for every rig object and bone |
| G5 | Lineup misleads about size | Each preview normalised to the same height | Always check the cast in ONE render at true relative scale, front and side |

## H. Tooling
| # | Symptom | Root cause | Prevention check |
|---|---|---|---|
| H1 | Patched script starts with "MISSING:" and fails | A PowerShell function's printed output becomes its return value | Print warnings with Write-Host inside helpers; check the first line after patching |
| H2 | A find/replace silently does not apply | CRLF vs LF line endings in the search text | Normalise line endings before matching; the helper must report every miss |

## I. Staging moving shots (shot 08)
| # | Symptom | Root cause | Prevention check |
|---|---|---|---|
| I1 | The "reveal" subject is in frame from the first frame | Start positions set without timing the camera against the subject | Plot camera x and subject x per frame; the subject enters or is caught when the story says |
| I2 | Wow details (frozen water, hanging leaves) are invisible | Placed in the set, not along the camera path | Place hero details relative to the camera path (0.3-2 m from the lens) and aim the camera at them |
| I3 | A character's action is hidden by their own body | Facing chosen for the set, not for the camera | Face characters 3/4 toward the camera's passing side; the prop hand on the camera side |

## J. Rigs, IK and props (shot 05)
| # | Symptom | Root cause | Prevention check |
|---|---|---|---|
| J1 | Kids' limbs collapse into thin lines / "strings" when posed | Non-uniform bone scales (child proportions) shear the children when they rotate (IK or FK) | Set bone.inherit_scale = 'FIX_SHEAR' on arm/hand/finger/leg bones of any rig with non-uniform bone scales |
| J2 | A character floats metres above the road or vanishes | Foot planting was relative (accumulated) and one exploded first-frame vertex at -813 m was the "lowest point" | Plant ABSOLUTELY (reset z, measure, set) and only count vertices within ~0.9 m of the rig |
| J3 | An arm reaches although its IK is switched off | _rot_arm writes pb.matrix, which INCLUDES constraint results: the last IK pose gets baked in | Set IK influence 0 and update the view layer before any matrix-based posing each frame |
| J4 | A round prop shows as a solid disc covering its own face | lathe() caps the first profile ring by default | cap_back=False for any lathe part whose first ring is on the visible side (rims, back plates) |
| J5 | A disc prop shows edge-on as a "brick" | Rotated as if the lathe axis were Z (it is Y) | Write the axis in a comment and check one frame of the prop alone |
| J6 | A ritual action is unreadable | Staged from behind / hands do not reach the object | Stage actions in profile or 3/4 with the object between the hands and the camera; hands ride on the object (targets parented to it) |

## K. Tooling (more)
| # | Symptom | Root cause | Prevention check |
|---|---|---|---|
| K1 | Inline Python inside PowerShell fails to parse | Quotes and brackets collide across the two languages | Put every patch in a .py file (patch_vN.py) with MISSING reporting + ast.parse before writing |
| K2 | A script variable silently overwritten | A new local name (FR) equals a global one (frame list) | Prefix shot-local names; grep for collisions with globals of the exec'd base script |
| J7 | Limbs stretch into ribbons only in the FULL render (probes looked fine) | The per-frame reset restored rotation only; matrix-based posing also writes bone location/scale, so error accumulates over sequential frames | Reset with the full pb.matrix_basis; probe at least one run of ALL frames in sequence at low resolution before the full render |
| J8 | FIX_SHEAR stretched an adult's IK arms | Applied to every rig | Only on rigs with non-uniform bone scales (kids) |

## L. Episode 2 additions

| # | Symptom | Root cause | Prevention check |
|---|---|---|---|
| L1 | A deliberate mirror clock resembles a reversed export | The shot carried no distinction between the world and the viewing surface | Label the world and each reflection in the shot card. Compare a clock or sign with its original and check the parity of nested views. |
| L2 | A window holds neither a readable clue nor the desired character | The prop or actor is positioned before the foreground matte and camera move are considered | Check first recognition, full reveal and final hold through the actual foreground. Check the inset at full output size. |
| L3 | A moving sheet shows the lettering from its concealed side | A double-sided surface shares one texture or shader | Give front and reverse distinct artwork. Check the rendered surface on both sides of the turnover and at the end of travel. |
| L4 | A page-turn forearm ends visibly as a hollow sleeve | The isolation mask follows the close-up frame at rest rather than the arm's motion envelope | Retain the upper-arm garment and aim it off camera. Check first grip, page apex and the retreat. |
| L5 | Contact is lost after a pose correction hides a face | The change moves the reaching shoulder to the far side of the body | Bind the hand target to the visible shoulder in world space. Check hand and face visibility together from the final camera. |
| L6 | A known-good cast looks younger and its apron flares after loading | Resetting matrix_basis to identity discarded the authored aged pose and changed the apron bone angle | Copy the original full matrix basis before posing. Restore it each frame, preserve eyelid and posture defaults, and use FIX_SHEAR on the non-uniform child rigs. |
| L7 | Street asset setup takes minutes before the first image | Hundreds of static building and sidewalk pieces carry separate depsgraph objects | Join static geometry per material and bevel width. Keep moving doors, horns and rigs separate. Measure the first probe before and after batching. |
| L8 | A frame count is correct but shots are out of story order | The manifest was traversed in file insertion order | Sort by shot number and assert every planned cut frame. Compare the first and last decoded frame at each joined boundary. |
| L9 | A known sound or cast dependency still writes into a shared workspace after handoff | The copied scripts use an absolute root or a parent-relative fallback to the original project | Scan for protected roots, copy the approved inputs and repoint the active runner to the new folder. Confirm each live Blender output path before considering the migration complete. |
| L10 | Whole-reel review spends tokens on repeated render chatter and full-size frames | Logs and raw stills were used as the default context | Keep one compact state table, 4–6 half-size keys, named native crops, per-pass diagnostics, and terse status logs. Show the shot sheet and read individual frames only for the relevant defect. |

Full corrections, production examples and measured render savings are in MOTION2D_QA_LEARNINGS.md.

## L11. Codec peaks

A PCM mix can pass while the rendered AAC exceeds the true-peak ceiling. The v2 scored master measured −15.02 LUFS and −0.71 dBTP. The highest decoded peak occurred during the first phone buzz. Locate the worst peak in the decoded delivery file, attenuate that cue at its source, leave enough limiter headroom for encoding, and remeasure the delivered file. Keep the picture stream unchanged.

## L12. Repeated words in generated dialogue

An ElevenLabs take can repeat a phrase even though the prompt and time slot are correct. Transcribe all voiced cues from the actual export and compare against the script. Locate repeated speech using word timestamps and the waveform. Preserve raw takes and record the edited filename in the final timeline.

## L13. Motion problems between probe frames

A moving camera may intersect a foreground actor or see past the side of a set between key frames. Inspect the path with cheap sequential cels and compare the actor's camera-space depth and margins. Inspect the native silhouette in high-risk spans. Use cut handles when that removes a blocked span cleanly.

## L14. Readable action, hold lengths, and dialogue cadence

Measure the first frame where a clue is readable at reel size and count its remaining hold. Match dialogue slots to the natural take durations before lock. Record the expected and actual durations and transcribe the encoded mix. Use motivated gestures or a change of gaze so the audience sees a reaction during the beat.

## L15. Score accents, story cues, and authored silence

Write separate time cues for nondiegetic score and audible story events. Verify the score accent against the actual cut and the story chime against each intended reaction. Keep dialogue clear of any authored sound gap and check the decoded signal within that gap, including the effects and room buses.
