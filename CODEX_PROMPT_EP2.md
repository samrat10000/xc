# Prompt for Codex: 5 O'CLOCK Episode 2 (paste everything below into Codex)

You are making 5 O'CLOCK Episode 2, a 2D anime / toon vertical reel (9:16, 1080x1920, 24 fps, 45-65 s), shot by shot, to final quality.
Sam (the director) is asleep. Do NOT ask him anything and do NOT wait for him. Work through the whole episode on your own.

## Start
1. Run the motion2d skill: read `motion2d/SKILL.md` and every file it lists (installed in ~/.codex/skills/motion2d, source:
   https://github.com/samrat10000/money-skills, folder make-motion2d). Use the highest reasoning effort.
2. Then read, in this order, from Episode 1's folder `C:\Users\cross\Downloads\xc\5oclock-ep1-the-fourth-note_2026-11-23\`:
   `ERROR_CATALOG.md` (every mistake already made, by category, with the check that prevents it; run its pre-flight checklist before EVERY shot),
   `AUTOMATION.md` (the per-shot loop and token rules), `SHOT_RULES.md` (the quality bar), `PRODUCTION_LOG.md`, `STATE.md`.
   Episode 1's story is in its `story\` folder: Episode 2 continues from its ending (rule seven torn out, new ink in Sam's handwriting).
3. Do NOT change anything inside the Episode 1 folder or `anime-5oclock\` (another session is still working there). Copy what you need.
4. Make your own folder: `C:\Users\cross\Downloads\xc\5oclock-ep2-<title>_<YYYY-MM-DD>\` with STATE.md, story\, shots\, audio\, ERROR_CATALOG.md (start from Ep1's, append your own),
   PRODUCTION_LOG.md, and a CHANGELOG_FOR_CLAUDE_DESKTOP.md that says what you created, where, and when.

## Reuse (do not rebuild what exists)
- Cast: `...ep1...\assets\cast_v2\` (grandma, shopkeeper, kid_girl, kid_boy; ages already fixed) and `assets\toon_sam\sam_toon.blend` (Sam, approved).
- Sets/code: Ep1 `shots\04_ride\src\` (the street, the Yamada shop, Sam on his bike), `shots\08_frozen\src\build_s08.py` (shows how to exec build_s04.py up to its render loop
  and add to the scene), `shots\05_ritual\src\` (IK grips on props), `shots\15_listener\src\` (the Listener kaiju, the sky crack, 3D dusk town, shared camera module).
- Blender: `C:\Users\cross\Downloads\xc\blender501\blender.exe` (GPU render box, one Blender render at a time, below-normal priority).

## The loop (never stop to ask "should I continue?")
Plan the episode first (story spine, 12-18 shots, dialogue table, as in the skill's PLAYBOOK_5OCLOCK.md). Then per shot:
pre-flight checklist -> build from the nearest proven code -> probe 4-6 key frames at 50% -> look at ONE contact sheet + crops (+ silhouette test for creatures/characters,
+ each pass alone when something looks wrong) -> fix ROOT causes, diagnosed with printed numbers -> full render in the background -> while it renders, write the lessons into
ERROR_CATALOG.md and PRODUCTION_LOG.md and start the next shot. Hardest shots first as 2 s tests. Never overwrite a version; new vN each time.
Known traps that already cost hours: emission colours are linear (true black <= 0.004); lathe() caps its first ring; VRM rigs are quaternion; non-uniform bone scales shear
(set inherit_scale FIX_SHEAR on kids); reset poses with the FULL matrix_basis, not only rotation; plant feet absolutely, never cumulatively; switch IK off before matrix posing;
camera clip_end for far giants; UTF-8 without BOM; put patches in .py files, not inline in PowerShell.

## Voices and music (decided by Sam)
- Voices: ElevenLabs (elevenlabs.io), in Sam's own signed-in browser. Music: Flow Music (flowmusic.app) or an original score on real sampled piano.
- You will probably have no browser control and Sam is asleep: do NOT block on this and do NOT wake him. Never type passwords, never change system settings.
- Write `audio\VOICE_SCRIPT.md` exactly like Ep1's (`...ep1...\audio\VOICE_SCRIPT.md`): every line with its time, shot, character, ElevenLabs text with [tags],
  file names (`N1_takeA.mp3`...). Same voices as Ep1 (Narrator: deep warm older man, close-mic; Sam: young low natural; Grandma: dry sharp elderly woman;
  Mirror-Sam: Sam's voice processed). Sam will generate them when he wakes; you mix them in when the files appear.
- Picture first, sound last (the skill's order). Finish every shot's picture before any mixing.

## Report
Keep STATE.md current after every step. When you finish a shot: clip path + contact sheet + one honest critique (what is great, what is weak) in PRODUCTION_LOG.md.
