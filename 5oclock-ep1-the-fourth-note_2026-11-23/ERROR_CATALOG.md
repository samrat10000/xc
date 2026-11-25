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
| K3 | A copied run script silently skips a step (02: no sky paint -> comp failed after the night chain) | The PC port of run_full.sh dropped a line | Diff every copied run script against the skill's reference run_full.sh before chaining it overnight; the chain must log each step's exit |
| K4 | Blender build fails: No module named PIL | Blender's bundled python has no Pillow | Draw textures (screens, signs) with system python into PNGs first; Blender only loads them |
| J9 | Screen/sign text upside down or mirrored | UV corner order guessed | After the first probe, crop the screen at full size and READ the text; fix the UV order before anything else |
| K5 | Japanese text turns into mojibake (boxes, a-umlauts) after a small patch | Windows PowerShell 5.1 Get-Content reads UTF-8 without BOM as ANSI; the re-save destroys every non-ASCII character | Never patch files that contain non-ASCII text through PowerShell; patch with python (encoding='utf-8'), or Get-Content -Encoding UTF8. Grep for mojibake after any patch |
| E4 | Handwriting reads as a computer font | Glyphs placed straight with tiny jitter | Per glyph: size 0.84-1.12, tilt +-7 deg, baseline +-9%, pen wobble field 3-4 px, pressure noise, ink bleed; different slant per writer |
| J10 | A hand never returns to its rest target (clutches the chest) | IK target moved by setting matrix_world, which persists; the next frame reads the moved position as 'home' | Store each target's rest local location once; reset it at the top of every frame before computing new positions |
| E5 | A whip/pan lands on an empty plane | The reused set was only dressed for its original camera | Before any camera move, list every direction the camera will face and dress each (road paint, kerbs, walls, poles, houses) |
| J11 | Hand over the eyes when it should touch the lips | IK places the WRIST, the fingers extend ~10 cm further | Offset IK targets by the hand length toward the wrist; check the fingertip position, not the wrist |
| B6 | Over-the-shoulder camera ends up inside the head | Camera start computed too close to the foreground head | Keep >= 0.4 m from the head centre; probe the FIRST frame of every camera move |
| K6 | exec-reuse of a build fails with 'unterminated string' | The cut marker ('META = {}') also occurs inside the reused file's own code, so the cut lands mid-line | Cut at a LINE-START marker ('\nMETA = {}') and print the first lines of the transformed source when an exec fails |

| C9 | A window/mirror stutters between reflection and wall on every frame (Sam: 08 @24 s, 10 @32 s, 16) | Holdout glass modelled on the exact plane of the building's front face: EEVEE z-fights, so each frame picks one or the other at random | Never put two surfaces on one plane; offset glass/decals >= 1 cm. TEST: % of glass pixels transparent per frame must be steady (v1 jumped 2%-65%; fixed 64-70%) |
| D8 | Reflection switches off while the glass still fills the frame | Visibility tested on 4 projected corners with all(z>0): one corner behind the lens kills the pass | Clip the quad at the near plane before projecting (glass_proj in build_s04); visibility = clipped polygon overlaps the frame |
| D9 | Glass reads as shutters sliding across it | Sheen stripes computed in SCREEN space, so they slide when the camera moves | Any glass highlight lives in the glass's own coordinates or not at all; restraint rule: a clean mirror |
| J12 | Hands render flat-fingered although the curl was set (05a mirror, 05c shutter) | A per-frame reset() restored EVERY bone to the base pose, wiping the finger curl made once at setup | Store the finger curl as data and re-apply it inside reset(); TEST: crop a hand on a mid frame, never just frame 1 |
| J13 | Hands meet in a diamond overhead instead of gripping the bar (05c) | IK/aim/palm targets parented to an object animated by SCALE: their offsets shrank to 1/5 | Never parent targets to a scaled object; recompute them in world/street space from the prop each frame |
| J14 | Wrist curled when a riding hand grabs something else (09 headphones) | Only the IK wrist target moved; the hand's aim + palm-roll targets stayed on the handlebar | When a hand changes object, move ALL three targets (wrist, aim, palm) and change the finger curl (fist -> drape) |
| A3 | A turned prop looks unnatural (05a mirror spin 212 deg in 9 frames) | Rotation picked the long way round, linear, too fast, the hands sliding round the rim | Take the short way; a push (ease-in) by the hand, release, momentum, ~5 deg overshoot, settle; hands only where they can physically stay |
| B7 | Background ends 'after ~10 m', one side empty (08, 16) | The reused set was built for its original camera (04 looks downhill); the new shots look uphill, the set stops at x=-30 | List every camera direction; extend the set to the horizon in each (SET_EXT in build_s04); check the FOV edges, not the centre |
| H3 | Two background probes launched together on the shared GPU | Each waiting script polled 'no Blender' independently | Chain jobs in ONE queue script, never two waiters |
| K7 | A whole render chain ran against wrong paths in seconds and made stray folders | PowerShell variables are case-insensitive: the loop variable $s overwrote the shots path $S | Never name two variables that differ only in case; give paths long names ($SH, $shotsDir); TEST: print the first resolved path before launching a chain |

- K8: python -I drops the script folder from sys.path, so comps that import siblings (paint_night11, paint_day17) failed. Use -E -s.
- K9: take_in.ps1 called with the wrong letters overwrote 2 good takes. Check the target names before moving files.
- K10: squeezing lines to fit tight slots sped voices up to x1.82. Widen the slot to the take's native length; never speed above x1.00.

## v3 (Sam's v2 notes, 2026-11-24)
- K11: a character turned 180 deg (yaw 180) has HIS left at world -x. The 05c shutter targets used +x for L = crossed wrists. Test: for every IK target, assert dot(target - chest, character_left) has the sign of the side.
- K12: same bug in the 17 mother: elbow pole on the wrong side folded the arm behind her head ("only one hand"). Poles must sit on the arm's own side, a little forward and down.
- K13: bike grips aimed the hand ALONG the bar (fingers pointing inward) = "hands inwards". The hand's long axis crosses the grip; wrist behind the bar, knuckles on top.
- K14: palm target placed inside a prop (headphone cup). Measure the prop's half-thickness along the approach axis and keep the palm outside it.
- D10: the 08 glide looked down the road past the built world (X1=60) into the painted bay = "a dead end / a sea". Every forward view needs the world extended to the horizon or closed by terrain (SET_FWD: road to 340 m + village + headland).
- D11: leaves hung 0.35 m from the lens smear into brown streaks ("glitch"). Keep props >= 0.9 m from any camera path.
- A4: characters on twos read robotic in body-mechanics actions (push, pull, grab). Human actions on ones; only the monster stays on twos (the stutter is creepy there).
- A5: the town-chime notes as marimba were cute, not thrilling. Thriller sound = a designed siren voice (formants + horn + drive + hill echoes) layered over real CC0 sirens; verified with earshot (AudioSet: civil defense siren 0.54).

- D12: the 08 glide flew THROUGH the frozen kid (blue frames, then black inside his body at 25-26 s = Sam's 'glitch'). Test: flick.py frame-diff spikes + every prop/character >= 1.2 m from the camera path.

## v4 (Sam's v3 notes, 2026-11-25)
- D13: the comp placed the painted sky from a horizon point on a FIXED world axis (+y). A turning camera swung that point off-axis -> one-frame sky jumps (08, 26-27 s). Horizon = the camera's own flattened heading; sun behind the camera = no disk.
- D14: the glide's look-ahead was measured from the BLENDED camera position; when the camera overtook the path point it looked backwards for a frame (08, 28 s). Look-ahead path-to-path only.
- K15: a new IK constraint has influence 1 and its target at the origin. Zero ALL constraints before posing/planting, or the first rendered frame breaks (05b kid stretched across the set).
- K16: IK elbow poles behind the body hide the forearms (17 mom). Calling / reaching poses: poles in front and out.
- K17: the kids' IK list was EMPTY (constraints never created) -> pure FK lerp = wings. Assert len(constraints) > 0 after setup.
- A6: a planned 'true silence' after a hit reads as a broken edit on a phone. Let the hit decay into an echo/rumble; never a dead stop.
- T2: on-screen text must match the spoken line word for word (page said 'Never let the song end', narrator says 'Never finish the song').
- A7: finger curl 0.85 on a FREE hand = a claw. Free hands 0.2-0.3; only gripping hands 0.85-0.95.
- K18: selecting objects by name prefix ('drop') grabbed the verge meshes 'drop'/'drop_fwd' and moved them onto the water path -> a grey wall in front of the shot-10 lens. Select by exact pattern (drop\d+) or keep a list at creation. Diagnose blocked frames with a camera ray_cast, not guesses.
