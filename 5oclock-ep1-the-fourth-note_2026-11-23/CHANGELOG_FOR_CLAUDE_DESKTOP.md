# CHANGELOG (read this first if you are Claude Desktop or any other Claude/AI picking this up)

## 2026-11-23: Sam started a NEW episode folder while experimenting with the motion2d skill
- Sam changed how this project is organised. The NEW Episode 1 ("The Fourth Note", 63 s, 18 shots) lives in:
  `C:\Users\cross\Downloads\xc\5oclock-ep1-the-fourth-note_2026-11-23\`
  - `story\5 O'CLOCK Episode 1.md` and `.html` = the script / storyboard Sam supplied (source of truth for this episode)
  - `STATE.md` = current status, shot table, next step (read it next)
  - `SHOT_RULES.md` = copied quality bar from the old shot 01 v4 (rules still apply)
  - `shots\NN_name\src|vN\` = build scripts and outputs per shot (never overwrite a version Sam has seen)
- The OLD project folder `C:\Users\cross\Downloads\xc\anime-5oclock\` (Ep1 v1-v3, a 21 s version) is NOT this story. Sam said do not refer to it for story. Leave it untouched.
- Skills: Sam installed `make-teaser` and `make-motion2d` from his repo https://github.com/samrat10000/money-skills (main) into ~/.claude/skills and ~/.codex/skills on 2026-11-23. Use `/motion2d` (or "use the motion2d skill").
- Experiment: Sam is testing whether Sonnet 5.5 (medium) can match the quality the Claude Desktop (Opus-class) run produced. First test shot = the hardest, shot 15 "The Listener" (2 s). Result and honest critique are in STATE.md.
- Lessons so far (add to SHOT_RULES.md as they are confirmed by Sam):
  - Camera at ground level makes the town a flat slab; a hillside viewpoint (camera ~28 m up, ground sloping down) gives depth and shows the road.
  - Painted layers (sky, crack, ridges, town, wires) are projected per frame from the same camera maths as Blender (`cam.py`), so they never drift apart.
  - Keep files UTF-8 WITHOUT BOM (PowerShell `Set-Content -Encoding utf8` adds one and Blender's exec then fails).
  - Blender default camera clip_end (100 m) clips distant giants: set clip_end 6000.
