# Spec for the 5 O'CLOCK anime-reel skill (from Sam, 2026-11-23)

Sam's template is the prompt he gave the teaser thread for its teaser skill (Sam shared it here on 2026-11-23; its key asks are summarised below). The anime-reel skill follows the same brief.

## What it must be
- **One general skill.** Give it an idea, story or episode (with or without assets) and it produces the vertical 2D/toon anime reel at the quality we reached here, ideally in ONE iteration.
- **Works with any AI:** Claude (Windows/desktop app, VS Code extension, phone, any account), Codex, any model from a small Sonnet up to Opus/Fable. Bigger models should do better, but even a small one must give a top result.
- **Invoked like** `/anime-reel <idea>`, optionally with attached PNGs, videos, posters or episode files.
- **Style is set at the start** (default: this toon-anime look; others like 3D + black outline, comic, 2D, ...). What never changes is the quality bar and the deliverables.
- **With assets** (normal case: the episode is done): use the characters and models provided. **Without assets** (just a poster or idea): build the assets first (CC0 rigged models, VRoid, painted BGs), then the reel.
- **Repo:** a separate GitHub repo for Sam's skills, named "money ___ skills". Ask Sam for the exact name before creating it. Plain to read.

## What goes in it (from this thread)
- `SHOT_RULES.md` in full: v4 recipe, toon shading, painted sky, comp, camera, contact, motion, and every dated Sam note (crow made of ovals, cut-out wings, hovering feet; clothes, roofs, verges, field depth; organic leaves; mirror inserts; outline width; rim side; sun glare; road detail; keep left; handlebar and grips).
- The proven scripts: toonlib, build/paint/comp per shot, run_full.ps1 (below-normal priority, absolute outdir, args after `--`), the VRM/VRoid cast setup and licences.
- The workflow:
  - Story first, and get it approved.
  - Make one shot perfect, then turn it into rules.
  - Work shot by shot: notify Sam, and if he doesn't answer in 1 minute, move on. Fixes come after the current task.
  - Sound comes last.
  - Log everything (WORKING / DECISIONS / WORKLOG).
- **Self-analysis that is mandatory, not optional.** Before showing anything:
  - key frames at low res, a contact sheet, full-size crops (faces, hands, feet, contact points);
  - pixel stats (p5/p95/p99 against the reference shot);
  - a numbered critique, then fixes; minimum 3 passes, maximum 6;
  - an honest list of the flaws that remain.
  - Every small part gets checked against the plan and a photo reference.
- **Mistakes and their fixes**, so they aren't repeated:
  - relative outdir writing to `C:\test`
  - the bone-parent glint offset
  - IK elbow jut (solve the pole numerically)
  - the slerp in-between swinging the arm out
  - linear ColorRamp colours
  - tiny toon thresholds
  - `git add` of render folders (commit only explicit paths)
  - pushes rejected while another session pushes (pull --rebase)
- **Extra constraints for weaker setups** (VS Code extension, Codex):
  - explicit checklists, exact commands and numeric targets;
  - "analyse your own output before reporting";
  - never claim done without having looked at the real output files.

## When
At the end of Ep1, when the reel is complete, unless Sam asks for a first version sooner.
