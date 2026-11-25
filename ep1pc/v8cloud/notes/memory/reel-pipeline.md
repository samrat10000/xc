---
name: reel-pipeline
description: Sam's procedural 9:16 explainer-reel pipeline (Blender passes -> sketch/pixel stylise -> pixel HUD -> synced synth audio) and its status
metadata:
  type: project
  modified: 2026-11-18T14:30:49.767Z
---

Scripts: /mnt/project-files/reels/pipeline/ (render.py, stylize.py, compose.py, timeline.py, font.py, audio.py, undraco.py, pal.npy). Lessons and Sam's feedback: /mnt/project-files/reels/LESSONS.md. Read it first, because it gets folded into one skill once Sam calls the reel final.
Car: Sam's "Night Terror Fastback" GLB (Draco). It arrived as optimized-models.zip under /root/.claude/uploads in the session that received it. Decode it with undraco.py (needs DracoPy).
Status 2026-11-18: v1 reel delivered at /mnt/project-files/reels/night-terror-v6-reel-v1.mp4. It shows a V6 cutaway with a section cut, a night street, and the sketch inking in and then turning to pixel art. Waiting on Sam's feedback.
Sam's standards: a professional look that doesn't read as AI-made; keep the whole car visible and cut away only a section; the scene matters; they want to watch the build live through progress stills.
Full render is about 60 min (3–4 parallel jobs). Preview cameras with PREVIEW=cams.json first.
