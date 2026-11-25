# 5 O’CLOCK · Episode 2 worklog

## Decisions

- Use the 15-shot, 63-second spine and dialogue timing from the brief. The director's approval of Alarm gates shots 02–15.
- Use the locked Episode 1 speaker v4 as the visual bar. Read the supplied v1 sources as pipeline documentation and use motion2d's shared v4 material helpers.
- Alarm takes a floor-level insert approach: warm early sun on woven igusa, cool cel shadows, one low-battery red accent. A generic phone has measured handset proportions and a custom mirrored screen.
- Keep all picture work silent and preserve Episode 1 source files.

## 2026-11-23

1. Intake. Read section 10 first, then the rest of the brief and Episode 1 story from source. The browser blocked local-file navigation. Inspected the supplied Episode 1 speaker v1 and locked v4 hero frames and source recipe. The v4 reference keeps strong silhouettes and pushes the warm rim harder than the internal detail.
2. Planning and references. Set up the episode state and Alarm card. Collected handset, igusa and shoji references in the shot's refs folder. The 3-second hold will succeed or fail on the first-frame mirrored 6:00 and a visibly physical buzz. Next is the six-frame block probe.
3. Verified motion2d. All 67 tracked files in the installed skill match GitHub HEAD `17728f927edb7833db34ef84d6b0ff7d224b4f89`, allowing for Windows line endings. The existing installation is current.
4. Built Alarm in Blender with the shared v4 toon setup. Painted the igusa, shoji light and custom screen separately and used Blender projection to register the floor/contact shadow in the composite. The first Blender call treated the relative render path as drive-rooted. Fixed the source to resolve an absolute path.
5. Block probe: the clock read clearly. The full handset clipped the left edge, the 3% status was tiny, and the window pattern was too soft. Mean 0.335 and p95 0.678. Enlarged the status, shifted aim, sharpened the shoji, and moved warm edge detail to the light-facing side.
6. Second probe: improved glass restraint, contact and direction of light. The first phone pose still clipped on the left and p95 was 0.795. Widened to 46 mm, offset and tracked the camera, and refined the wallpaper and the lit straw. 
7. Third probe: the complete silhouette fits and the display holds through the three kicks. Mean 0.321 and p95 0.856, both inside the locked opener's 10% bounds. The last key still sat close to the right edge. Nudged aim 5 mm right and brought the underside within 0.25 mm of the floor. Spot-check the corrected bookends before rendering the master.
8. Fourth probe and references. The corrected side margins held. Compared the shot with Apple product photography and Motoyama's woven-rush photos. The dark indigo heri, phone rail and single warm edge carried through. Started one full render with the validated framing.
9. Master. Rendered all 72 frames at 1080 × 1920 and encoded `01_alarm_v1.mp4` at 24 fps, CRF 14, with no audio. Inspected the final contact sheet plus three full-resolution crops. Exported four full-size PNGs and kept the exact Blender, paint, composite and encode scripts. The reversed 3% is less immediate than the clock. The bright battery sliver reads first. Next gate is Sam's review of Alarm.
10. Sam approved moving to Shot 02 and reiterated iterative error-finding. Locked Alarm's recipe in SHOT_RULES.md. Confirmed that the reversed clock digits are the story's visual clue. Mapped Shot 02 using the existing VRoid-based Sam rig and a phone-glass reflection camera.
11. Built Wrong room with the existing hero rig, procedural washitsu, Alarm handset, and a mirror camera. P1 revealed duvet intersection, wrist reach error and glass occlusion. P2 removed them but exposed palm roll and tight framing. P3 pinned the support wrist and exposed a free-hand intersection. P4 recovered the reflected hair silhouette and reached targets, then showed a high free-hand hold. P5 tests a lower settle and a closer dawn grade.
12. Checked six keyframes in P6. Recovered thigh contact and locked the supporting wrist. Room p95 0.908–0.914, dim reflection insert p95 0.501. Started the full-res render after visual review.
13. Stopped the first master render after a native crop exposed the support-hand pinky intersecting the cushion. Adjusted wrist height and pitch, inspected frames 1, 39 and 69 at native scale, then restarted the unshown master.
14. Wrong room v1 final: verified H.264, silent, 96 frames, 24 fps, full-resolution contact sheet and native crops. Mean .365 and p95 .808 passed against Alarm. The physical reflection keeps Sam's fringe visible while his lower face falls behind his shoulder. Source scripts and the four review frames are in ep2_codex/02_wrong_room.
15. Sam asked for reusable weaknesses and a refinement before Shot 03. Created MOTION2D_QA_LEARNINGS.md. Wrong room v2 refines only the phone glass, with the opening 72 source frames verified unchanged. Started The crack with the existing bedroom and an exact crown cel from Episode 1.
16. The crack passed four layout and lighting probes. Fixed scene-import rig pose, cleared inherited ear-cup motion, opened the window view, lowered the foreground silhouette and matched the canon Listener crown. Added the causes and prevention checks to the skill research MD.
17. The crack v1 encoded and passed native crop, contact sheet and parallax verification. Sam asked to automate the rest of the reel and add picture-locked audio. Continue without approval waits while retaining the per-shot QA and reproducible records.

## 2026-11-24 — Shared-set probes and revision

- **04:** Reduced the kitchen light gain on the background to retain the tile, window and character separation. The actual Episode 1 character rig stays back-facing. The faceless reflection appears on the curved kettle only in frames 77–82. Steam continues after it disappears.
- **05/12:** P2 camera and timing make Sam read against four moving sweepers. Grandma looks across the frame and moves off-beat. Staggered horns finish rotating as the sweepers stop and turn. Batched static street meshes share their surfaces across both scenes.
- **06:** The first interior framing left the door across the book. P3 keeps the chained notebook unobstructed after the cut. The calendar and sign are reversed as specified for the mirror town.
- **07:** P3 resolves the reverse-page lettering. Extending the retained sleeve and reaiming the upper arm addresses a cut end visible during the turn in P3.
- **08/09:** The live feed has a delayed freeze and tear; the next shot contains the two figures independently posed inside the kitchen mirror, rather than as part of the phone artwork.
- **10:** P3 revealed too much of Mirror-Mom's face and drew the viewer toward her arm. Revised her shoulder contact and turned the rig away for another probe.
- **11:** The clock jumps from reversed 7:12 to reversed 16:59 as the light sweeps the floor over twelve frames.
- **13/14:** Removed the concealed arm polygons that emerged through the sleeve in the crouch. The knock silhouette now raises a hand before settling. P3 retains the four wave pulses and the headphone shape.
- **15:** The letters draw progressively in the same single-stroke handwriting as the rule insert. Frayed paper fibres retain the torn Rule Seven edge.

## 2026-11-24 — First master checks

- **08 v1:** The ring and video-call cues read, but the leftmost corner of the handset exceeds the frame during motion. Widened and shifted the camera for v2, leaving the call performance and timing intact.
- **09 v1:** Reviewed the native phone insert and contact sheet. The push-in may crop the phone's outer edge because the clue is inside the video. Sam and the second figure remain in the usable vertical area.
- **Finishing:** Compared the baseline compositor with three workers on the same 20 cels. Both produced identical PNGs by hash, at 15.75 and 7.02 seconds respectively. Retained three workers for subsequent masters.
- **Assembly:** Corrected the shot list to sort numerically. Added start-frame assertions and independent checks for cut boundaries and the authored black transition.
