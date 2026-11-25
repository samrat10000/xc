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

## 2026-11-24 · Independent project and pre-flight

- Stopped the in-progress Episode 2 queue targeting the shared folders. Copied completed media and review artifacts into this project. New renders use below-normal priority and wait while Blender is occupied.
- Reviewed Episode 1's catalog against the outstanding close shots and street. The 50% probes verified the page's blank verso, a continuous sleeve, paired mirror characters, a fully framed incoming call, the town turn and the four wave rings.
- The window probe still hid the contact hand when the whole Mom rig turned away. Changed the chest and reaching arm back to the visible side and turned only the head away. The selected master will be checked for contact.
- Street probe with cast_v2 kept the children's distinct heights, backpacks and caps. The first pass straightened Grandma and changed her apron angle. The street build now restores the original full pose and uses world-space planted shoe targets. Native checks will use the shorter camera-middle distance.
- Shot 05 v1 was interrupted during the move. The new render uses v2 with the approved cast. The old files are kept as migration evidence.
- Audio follows verified picture. VOICE_SCRIPT.md matches Episode 1's take conventions. The project uses recorded piano and foley while the named dialogue takes are absent.

## 2026-11-24 · Master review

| Shot | Clip | Contact sheet | Critique |
|---|---|---|---|
| 01 Alarm | [v1](shots/01_alarm/01_alarm_v1.mp4) | [sheet](shots/01_alarm/qa/v1_review/contact.jpg) | Reversed clock and 3% read. The battery mark is intentionally small and needed the native crop. |
| 02 Wrong room | [v2](shots/02_wrong_room/02_wrong_room_v2.mp4) | [sheet](shots/02_wrong_room/qa/v2_review/contact.jpg) | The glass and reversed fringe read. The reflected lower face remains subtle at the steeper viewing angle. |
| 03 The crack | [v1](shots/03_the_crack/03_the_crack_v1.mp4) | [sheet](shots/03_the_crack/qa/v1_review/contact.jpg) | The stationary crown and drifting foreground work together. The outer horns stay in the haze until late. |
| 04 Mirror-Mom | [v2](shots/04_mirror_mom/04_mirror_mom_v2.mp4) | [sheet](shots/04_mirror_mom/qa/v2_review/contact.jpg) | The kettle reveal holds for six frames. The face is a very quick cue against the softened metal. |
| 05 The street | [v2](shots/05_the_street/05_the_street_v2.mp4) | [sheet](shots/05_the_street/qa/v2_review/contact.jpg) | Grandma's offset broom rhythm survives the cast update. Sam's run cycle is more readable at mid-distance than at the start, where he enters partly clipped. |
| 06 The koban | [v1](shots/06_the_koban/06_the_koban_v1.mp4) | [sheet](shots/06_the_koban/qa/v1_review/contact.jpg) | The reverse sign and chained book anchor the location. The calendar year is high in the interior framing and the light cue does most of the work for the lamp. |
| 07 The rules | [v1](shots/07_the_rules/07_the_rules_v1.mp4) | [sheet](shots/07_the_rules/qa/v1_review/contact.jpg) | The curling page, fingertip pinch and torn rule read. The small script needs a pause to read all six rules. The 11-day clue has its own large text and dialogue slot. |
| 08 Mom calls | [v2](shots/08_mom_calls/08_mom_calls_v2.mp4) | [sheet](shots/08_mom_calls/qa/v2_review/contact.jpg) | The revised framing fits the handset and the reconnect hold. Mom's reaction is intentionally subdued inside the inset. |
| 09 Behind him | [v1](shots/09_behind_him/09_behind_him_v1.mp4) | [sheet](shots/09_behind_him/qa/v1_review/contact.jpg) | The push grows the nested clue. Mirror-Mom's visual separation depends on the final phase of the push. |
| 11 16:59 | [v1](shots/11_1659/11_1659_v1.mp4) | [sheet](shots/11_1659/qa/v1_review/contact.jpg) | Colour and shadows carry the 12-frame time jump. Reversed digits take a little longer to read. |
| 12 The horns turn | [v1](shots/12_the_horns_turn/12_the_horns_turn_v1.mp4) | [sheet](shots/12_the_horns_turn/qa/v1_review/contact.jpg) | The foreground horn leads, then the town turns. The distant poles read as groups rather than individual horns. |
| 13 Rule one | [v1](shots/13_rule_one/13_rule_one_v1.mp4) | [sheet](shots/13_rule_one/qa/v1_review/contact.jpg) | Four rings time the chime and the headphones read. A small elbow crease remains during the transition to the crouch. |
| 14 The knock | [v1](shots/14_the_knock/14_the_knock_v1.mp4) | [sheet](shots/14_the_knock/qa/v1_review/contact.jpg) | The headphones identify the silhouette. The frosted figure is designed as a nearly still hold after the knock. Frames 114–120 are true black. |
| 15 Rule eight | [v1](shots/15_rule_eight/15_rule_eight_v1.mp4) | [sheet](shots/15_rule_eight/qa/v1_review/contact.jpg) | Stroke order is visible and the torn line remains above it. The last word gets a short hold before the end. |

**10 · The window.** [v2 clip](shots/10_the_window/10_the_window_v2.mp4) · [contact sheet](shots/10_the_window/qa/v2_review/contact.jpg) · [native contact crop](shots/10_the_window/qa/v2_review/crop_reflection_073.png). The prior pose missed the shoulder target by 22.8 cm in the three diagnostic frames. Moving Mirror-Mom's root toward the contact plane reduced the wrist-target error to the precision of the printed measurement. The fingers reach the shoulder edge and the head turns away. The elbow still has a pronounced bend in the reflection. Preserved source cels 1–56 by hash and rendered only 57–96 for v2.

## 2026-11-24 · Picture and score delivery

The independently assembled picture and scored v3 both decode to 1,512 frames. Their 15 start and end boundaries match the approved shot files. Only the seven planned black frames appear before the notebook stinger. No two neighboring nonblack frames have identical decoded pixels.

The scored export uses a recorded piano, real foley and the four-note recorded chime. The four note attacks and the knock slot were measured against the authored cues. AAC v2 exceeded the peak ceiling in the opening phone buzz, so v3 rebalanced the buzz and reserved encoder headroom. Scored v3 measures −15.02 LUFS and −2.80 dBTP. The voice recording pass remains pending with the named ElevenLabs takes. The mix has timing and level checks and still needs a listening pass.

[Scored cut](episode/5oclock_ep2_the_koban_score_only_v3.mp4) · [Shot index](episode/DELIVERY.md) · [Voice handoff](audio/VOICE_SCRIPT.md)

## 2026-11-24 · Dialogue master

The signed-in ElevenLabs history confirmed George for narration and Roger for Sam and Mirror-Sam. Sarah supplied Mirror-Mom and the hum. Downloaded the eight lines and the hum into audio/. The v4 transcript revealed repeated words in M1 and N5. Kept both source MP3s and created trimmed takes from the intended reading. The encoded v5 export transcribes to all eight scripted lines and lands in their shot windows. It measures −15.04 LUFS and −2.85 dBTP. The 1,512-frame timeline and all 15 cut boundaries matched after muxing. No human listening pass was performed.

[Full reel](episode/5oclock_ep2_the_koban_v5.mp4) · [Dialogue comparison](audio/qa/dialogue_whisper_v5.json) · [Voice assets](audio/VOICE_SCRIPT.md)

## 2026-11-24 · v6 picture review

| Shot | Clip | Contact sheet | Critique |
| --- | --- | --- | --- |
| 03 The crack | [v2](shots/03_the_crack/03_the_crack_v2.mp4) | [sheet](shots/03_the_crack/qa/v2_review/contact.jpg) | Sam turns into three-quarter view as the crown stays in frame. His expression is small in the wider shot. The brighter grade passes visual review. |
| 04 Mirror-Mom | [v3](shots/04_mirror_mom/04_mirror_mom_v3.mp4) | [sheet](shots/04_mirror_mom/qa/v3_review/contact.jpg) | The spoon stops on the line. The faceless kettle clue remains six frames and easy to miss. |
| 05 The street | [v3](shots/05_the_street/05_the_street_v3.mp4) | [sheet](shots/05_the_street/qa/v3_review/contact.jpg) | The running profile and foot push-off read. The edit omits ten frames where the tracking camera passes a townsperson. |
| 06 The koban | [v2](shots/06_the_koban/06_the_koban_v2.mp4) | [sheet](shots/06_the_koban/qa/v2_review/contact.jpg) | Sam's gaze links the calendar and notebook. The upper crop catches some of his hair late. |
| 07 The rules | [v2](shots/07_the_rules/07_the_rules_v2.mp4) | [sheet](shots/07_the_rules/qa/v2_review/contact.jpg) | Lamplight gives Sam's reading beat a clear face. The Japanese handwriting is dense at reel size. |
| 10 The window | [v3](shots/10_the_window/10_the_window_v3.mp4) | [sheet](shots/10_the_window/qa/v3_review/contact.jpg) | The glance anticipates the hand. A pronounced elbow bend still shows in the reflection. |
| 11 16:59 | [v2](shots/11_1659/11_1659_v2.mp4) | [sheet](shots/11_1659/qa/v2_review/contact.jpg) | Sam's eyes follow the clock shift. The intentionally reversed numerals still require context. |
| 12 The horns turn | [v2](shots/12_the_horns_turn/12_the_horns_turn_v2.mp4) | [sheet](shots/12_the_horns_turn/qa/v2_review/contact.jpg) | The turn has a clear start and settle, and the horn circle reads in dusk. The distant bells still read as groups. |
| 13 Rule one | [v2](shots/13_rule_one/13_rule_one_v2.mp4) | [sheet](shots/13_rule_one/qa/v2_review/contact.jpg) | Sam's body reacts to each note and the canonical Listener has a close insert in the edit. A small sleeve crease remains at the elbow. |
| 14 The knock | [v2](shots/14_the_knock/14_the_knock_v2.mp4) | [sheet](shots/14_the_knock/qa/v2_review/contact.jpg) | The silhouette leans in. Frosted glass limits the gesture to outline and weight shift. |
| 15 Rule eight | [v2](shots/15_rule_eight/15_rule_eight_v2.mp4) | [sheet](shots/15_rule_eight/qa/v2_review/contact.jpg) | The full warning has more than two seconds of reading time. The small older writing stays secondary. |

[Source and timing decisions](V6_REVISION.md) · [Reusable production checks](MOTION2D_QA_LEARNINGS.md)

## 2026-11-24 · v6 delivery and audio review

The encoded 57.417-second master matches the decoded first and last frame of all 19 segments. Only frames 1275–1281 are black, as designed. The center of the 0.62-second score gap decodes to zero. All seven selected ElevenLabs cues matched their scripted words in the encoded mix. Their trimmed source and placement durations agree within 1 ms.

The final AAC measures −14.94 LUFS, −2.94 dBTP and 7.80 LU range against v5’s 15.9 LU. The recorded theme has its opening motif and street ostinato, a hit on the close Listener edit and a brief silence after the fourth story chime. Human listening is pending.

At the fixed low-motion threshold of 0.25/255, the window beat went from 9.5% low-motion frame pairs to zero. Shot 06 and the notebook still contain deliberate quiet holds. This diagnostic is a proxy for motion and the visual performance was assessed from the rendered sheets.

[Full reel](episode/5oclock_ep2_the_koban_v6.mp4) · [Delivery index](episode/DELIVERY_V6.md) · [Decoded checks](episode/v6/RELEASE_QA_V6.json) · [Speech comparison](episode/v6/DIALOGUE_QA_V6.json) · [Motion comparison](episode/v6/MOTION_QA_V6.json)
