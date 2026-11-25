# 02 Wrong room · QA

| Review | Finding and fix |
| --- | --- |
| Probe 1 | Duvet penetrated both knees. Support arm missed by up to 11.5 cm at the rise and the cloth occluded the phone. Moved bedding aside, set a reachable wrist target at a separate cushion and flattened the handset on the floor. |
| Probe 2 | Window now reads on screen right and no cloth blocks the glass. Main palm turned sideways at some frames and reflected face was too low in a cropped phone. Solved palm roll from actual knuckle bones and widened the optically reflected insert. |
| Probe 3 | Support wrist tracked to numerical precision, but Sam's free hand intersected his jeans and the rack read as a block. Reposed the wrist, beveled and detailed the rack, and added textured shoji and a soft warm tatami light patch. |
| Probe 4 | The reflected fringe and eyes now read and the full phone stays in frame. The free hand rose too far and stayed up near the waist. Gave it a brief lift and a lower resting target, tuned the head tuck and graded the shadow values closer to Alarm. |
| Probe 5 | Both wrists reached the intended positions, but the free hand still stopped just above the thigh. Lowered it slightly more and let it travel forward before the final eyeline. |
| Probe 6 | The free hand now settles onto the thigh and the left wrist stays put on the cushion. Reflected fringe remains visible in the dark glass. Sampled wrist errors are below 0.001 mm. Room p95 is 0.908–0.914 with the shoji in frame. Phone insert p95 is 0.501 with the bright window outside the view. Checked the 6 renders before starting the master. |

## Comparisons

- Existing Sam turnaround: the same head, glasses, fringe, skin tones, headphones, long dark legs and narrow-shouldered charcoal hoodie carry through. The sleeping posture begins with eyelids closed. The shoulders and head lead the rise.
- Japan Tourism Agency room photos: shoji paper grid, sill, floor-level bedding, stitched tatami and wood skirting are visible in the frame. The original Kiriyama poster is reversed horizontally at texture creation.
- Episode 2 Alarm: warm frame-right daylight on the same handset geometry. The reflection uses the dark glass of the same phone; the main portrait and the dim phone insert have separate luma targets because the insert excludes the bright window.
- Shot is scripted 0:03–0:07. A silent cut to the phone insert lands at 0:06.0 (frame 73). Narrator timing from the supplied dialogue remains 0:03.4 and 0:05.2.


## Native-resolution hand repair

The 40% checks hid an intersection at the support-hand little finger. The 1080 × 1920 render exposed a separated-looking fingertip at frame 69. Stopped that render before export. Raised the fixed wrist anchor by 8 mm and reduced the press angle. All four long fingers form continuous silhouettes in the native crops of frames 1, 39 and 69. The hand remains on the padded surface during the rise. Restarted the master after the comparison.
## Master review

- Opened the twelve-frame contact sheet and native crops. Sam's hands follow separate arcs. The support fingers are continuous on the cushion and the free fingers follow the thigh. The face crop shows an eyelight and stable glasses. The mirror crop shows the reversed fringe, eyes and dark glass lip without screen graphics. The low angle leaves the lower face partly behind the shoulder.
- The sequence contains 96 intact RGB frames. The support wrist drift was below 0.001 mm and maximum measured target error across both wrists was below 0.001 mm. The reflected screen mask remains in frame, its left and right limits are .131 and .964. Sam's head stays safely inside the main framing throughout.
- Motion2d comparison passed against Alarm. Mean luminance .365 vs .334 (+9%), p95 .808 vs .864 (-7%), zero black frames, zero frozen consecutive frames. The room is brighter than the glass insert by design.
- The H.264 master decodes to 96 frames at 1080 × 1920, 24 fps, yuv420p and 4.000 seconds. The slow export uses CRF 14. Only a video stream is present.
## Revision 2

The original reflected face could read as an illuminated display. Added a faint, screen-anchored shoji reflection and a small lift confined to the deepest reflected colours. The first 72 composite frames are byte-identical to v1. All 24 phone frames change. Compared frame 94 at native scale and verified 96 silent frames at 1080 × 1920 and 24 fps. The lower face is still partly hidden by the optical angle. That framing preserves the physical camera geometry.

## Episode v6 · Re-edited sequence

Existing support-hand animation and phone reflection are used. The narration now starts at 2.25 and the second sentence can bridge the outside cut.
