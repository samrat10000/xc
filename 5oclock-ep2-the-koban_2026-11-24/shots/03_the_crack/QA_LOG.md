# 03 The crack · QA

| Pass | Finding and correction |
| --- | --- |
| 1 | A pose reset exposed the T-pose and Sam's arm cut across the window. The lintel hid the crown, and preview p95 was 0.630. Solved the arm directions, raised the header above the view, textured the curtain and replaced the substitute silhouette with the exact Episode 1 crown. |
| 2 | The crown was visible but the character filled too much of the screen. A retained animation channel moved the left ear cup after frame 39. Created a lower, weight-bearing silhouette, framed more sky, and cleared animation from the imported rig controls. |
| 3 | Ear cups stayed against the head and the window held. The curtain hid too many horn mouths and the halo was flat. Shifted the distant crown to clear the curtain. Broke up the masking cloud edge, darkened the foreground and lifted the dawn horizon. |
| 4 | The reveal reads through the actual window matte. The scene's p95 is 0.837 and mean is 0.396, both within 10% of Shot 02's comparable wide frame. The hair and curtain use different motion and the crown changes no pose. |

## References and targets

- Episode 1 Listener shot 15 frame 108 is the source of the exact horn silhouette. The paint grade gives it the softer and cooler contrast of a distant morning subject.
- Previously made Sam rig and bedroom geometry are reused. The window reads as the same right-side shoji from Wrong room, with a view through the slid panel.
- The real-world atmosphere reference is the JNTO mountain valley with mist between ridges. The TOA horn drawing verifies the fabricated flare concept. Episode 1 supplies the circular bells.
- Keep Sam and the curtain low and to the edges. The seam, sill lintel, curtain folds, headphones, layered cedar ridges, horn bells, mist, cracking glow and dawn band create clear foreground and background separation.
## Master

- 96 verified silent video frames at 1080 × 1920, 24 fps, exactly 4 seconds. H.264 yuv420p at CRF 14.
- Contact sheet: Sam's shoulders remain anchored low. Curtain reveals a narrow change in the edge over time. The crown holds while the cloud lifts, and the ridges gain distinct separation. Native crops confirm continuous headphone placement and a smooth fissure against the sky.
- Average mean .396 and p95 .839 pass against Wrong room at .365/.905. No black or frozen consecutive frames.
- Ten exterior planes have distinct start-to-end transforms. The screen aperture stays at or above 44.3%. The curtain edge moved 27 rendered pixels in the sampled rows. The cloud moved up 48.1 px relative to the fixed crown plane.
- Haze keeps a strip of horn mouths partially hidden. The large silhouette reads earlier and more clearly than the individual bells.

## Episode v6 · v2 · p64

Probe shows the torso recoil and a turn that brings Sam into three-quarter view while the morning crown and cloth remain visible. Exterior comp retains the original layered skies.

### Full-size master review

[Clip](03_the_crack_v2.mp4) · [Contact sheet](qa/v2_review/contact.jpg)

The body and head turn before the cut to the kitchen. The crown and curtain continue moving in the background. Wider coverage keeps the whole reveal, so Sam's reaction stays small. The reference mean-brightness guard reads 0.402 versus 0.365 for the prior composition. Review accepts the brighter morning sky and preserved face and curtain detail. The image has no neighboring identical frames or black frames.
