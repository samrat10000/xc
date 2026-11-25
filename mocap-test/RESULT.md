# Video → mocap test (Asus, RTX 3050 4 GB) — 2026-11-21

**Verdict: it works.** MediaPipe Pose (PosePipe's engine, run headless) turned a 12 s clip into BVH and FBX in about 50 s, all on the CPU. The GPU wasn't used. The gait timing reads as real walking, but there's jitter and the occluded side flips: the far-side wrist jumps and the ankles swap left/right about 5 times. The rig has no fingers, and the feet slide because the root translation is rough. So it's good for blocking and timing reference. It needs a smoothing and cleanup pass before it beats hand-keyed animation, and it isn't final quality as it stands.

## Deliverables (`out/`)
- `walk_mocap.bvh`: 18 bones, 355 frames at 29 fps, Y-up (standard BVH). Re-import checked: feet sit on the floor and the neck is at 1.43 m.
- `walk_mocap.fbx`: the same rig with baked animation (189 curves, re-import checked).
- `walk_mocap.blend`: the baked rig in Blender 4.5.
- `walk_pose.json`: the raw MediaPipe landmarks (world and image), per frame.
- `contact_sheet.png`: video frames next to the skeleton's side view.

## Numbers
| | |
|---|---|
| Clip | Mixkit #51708, "young man with red hair walks in the city". 1280×720, 29 fps, 12.2 s, full body in profile. Free under the Mixkit license. Wikimedia CC0 clips returned HTTP 429, so I used this one. |
| Detection | 355 of 355 frames |
| Extraction speed | 7.8 fps (heavy model, model_complexity=2, CPU). The Blender bake and export took a few seconds. |
| Ankles | Mean step 6.8 cm/frame. 9–10 single-frame jumps over 20 cm (max 58 cm). About 5 left/right swaps. |
| Wrists | Near wrist is clean (0 jumps). Far, occluded wrist has visibility 0.26 and 20 jumps. |
| Hands | Pose model only, so wrist plus one hand bone and no fingers. |
| Feet | Ankle and toe are tracked (visibility 0.9+). Root X comes from the 2D image track, and the camera pans with the walker, so the rig mostly walks in place. Z keeps the lowest foot on the floor. |

## How it was built
- **PosePipe** (github.com/SpectralVectors/PosePipe), read in full. Its installer pip-installs into Blender's own Python, and its capture loop needs the Blender UI and a cv2 window. So I didn't install it as an add-on. Instead I re-implemented its pipeline headless: `scripts/extract_pose.py` does the same `mp.solutions` pose step, and `scripts/bake_bvh.py` does what PosePipe does with keyed empties and track constraints, then bakes to a skeleton. I improved on it in two ways: it uses `pose_world_landmarks` (metric, in metres) instead of PosePipe's image-space hack, and a locked-track constraint recovers pelvis and chest twist.
- **venv**: `mpenv` uses system Python 3.12 with system site-packages. It has mediapipe 0.10.14 and opencv-python 4.10, installed from wheels whose SHA-256 I checked against PyPI. Telemetry isn't used. Blender's own Python was left untouched.
- Re-run:
  - `mpenv\Scripts\python -E -P scripts\extract_pose.py <video> out\x.json 2`
  - `blender -b --factory-startup -P scripts\bake_bvh.py -- out\x.json out\x`

## GVHMR: not attempted
It needs a sign-up on the SMPL/SMPL-X sites (Sam would have to make those accounts), several GB of checkpoints from Google Drive, and pytorch3d and CUDA builds. The network here was about 20 KB/s during this test. On 4 GB of VRAM it's borderline at best. Revisit only if MediaPipe's quality isn't enough.

## Next steps if we use this
1. Add a One-Euro or Savitzky–Golay filter on the landmarks, plus a left/right swap fix (keep the leg assignment that's continuous with the previous frame). That should remove most of the jitter.
2. Add foot-contact locking (pin the foot while its velocity is near zero).
3. Retarget to a Rigify or Mixamo rig (the bone names are already Mixamo-like).
4. For fingers, run MediaPipe Hands, or Holistic, on close-up clips.
