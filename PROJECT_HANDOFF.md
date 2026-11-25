# PROJECT HANDOFF: "Night Terror: Dead Roads" (Sam's reel project)

Written by Claude on 2026-11-21 for ChatGPT / Codex. Sam is the boss of whichever AI reads this.
Facts come from Claude's project memory and notes. Where something is not known, it says "unknown".
Times are IST (UTC+5:30), Sam's time zone.

---

## 1. Concept, aim and the output Sam wants

**Core idea:** a 3D zombie / virus-mutation horror web series called **"Night Terror: Dead Roads"**, made as
vertical (1080x1920) reels and short episodes for **Instagram, YouTube Shorts and Pinterest**, to go viral and
make money.

**Story premise:** the city falls at **3:12 AM**. Sam (the creator, as the hero) wakes up, gets a virus alert,
takes his armoured car **"Night Terror"** out of the garage and drives through a zombie-filled city to rescue
3 friends in 3 cities (one rescue per season). Creatures: Walker, Runner, Crawler, Screamer, Husk, Brute,
and the **Stalker** (deer/reindeer skull with burnt antlers, Sam's favourite). Infection stages:
Walker/Runner -> Husk -> Stalker. Other vehicles: "Bandit" armoured military buggy, "IVORY" reverse trike.
Side character: a female rider on the IVORY trike (Episode 2), name unknown.

**Output Sam wants:**
- 15-60 s reels and short episodes, **blockbuster-cinematic and real-looking**, wallpaper-worthy frames.
- A second reel style: "how it works" car explainers (sketch-ink turning into pixel art, synced HUD + SFX).
- Later: **auto-post 3-4 reels per day**, but Sam previews every post first. Phase 1 = Sam approves, then
  we post (Sam signs in to accounts himself).
- A making-of / behind-the-scenes series on Instagram narrated in Sam's own cloned voice (paused).
- When Sam calls a reel final, all lessons get folded into one reusable skill.

---

## 2. Sam's standing rules and taste (READ BEFORE DOING ANYTHING)

**Quality**
- **Realism rule (every step):** output must never look AI-made. Use real-camera imperfections
  (handheld micro-shake, low-light sensor noise, motion blur, focus breathing, lens smudge), ordinary messy
  real places, natural skin, no glossy / symmetric / over-graded look.
- **No dithered / dotted look**, ever. Limited palette + tile wipes instead of per-pixel noise.
- **Perfect human anatomy:** hands, fingers, arms and movement. Broken or splayed fingers read as AI.
  Relaxed hands hang palm toward the thigh. Zombies may be unstructured.
- **References first:** never build a character, body or pose without real references, compared side by side.
- Real character animation, never frozen poses. Zombies must actually move.
- Vehicle tyres must read as matte squashed rubber, never metal. No flickering / toggling car lights.

**Editing and camera**
- **No slideshow cutting:** no sweep / slide / whip transitions, no sub-1 s inserts, no orbit freezes that
  cut to a new angle. A "freeze" is ONE take: live 1x, ramp to ~3% speed while the camera glides, ramp back.
- No big title text over the best shots. Frame 0 is the thumbnail (hook text fully visible if used).
- Slow-mo only when it means something, never as filler. Drifts / stops are one smooth motion.
- **Camera Sam loves:** handheld documentary is the default for ground shots (eye height, operator shake,
  late reframes, never drone-like). Signature moves: low side-follow keeping a flying body centred;
  crash zoom up over a roof to the creature's face then fast pull-back; 20 mm camera on the asphalt at the
  tyre. Full notes: `xc\dead-roads-ep2\CAMERA-MOVES.md`.
- Sam's 10/10 moments: the Brute / Stalker ("reindeer") encounter, the Screamer, the garage scene.

**Sound and music**
- Music is key. **Real recorded instruments only.** Sam hated AI music (ACE-Step) and synthesized guitar.
- Locked feel: orchestra + 80s analog synth arps (Stranger Things-like but original, never copy the theme)
  + real electric guitar doubled by bass, slightly detuned piano opening.
- Since 2026-11-20 Sam uses **Google Flow Music** (flowmusic.app, in Sam's Chrome, Sam signs in) for score
  and designed SFX. Prefer REAL recorded SFX (Freesound / Openverse CC0 / CC-BY, keep credits).
- No sudden music cutouts. Creature sounds must be designed carefully (Sam hated the crawler sound).
- Engine must sound like a grumbling 3-4 L V8, never like an EV.

**Process**
- Plan big reworks first as a **pixel-art storyboard** (HTML) with viral research, then render.
- Don't wait for Sam between steps; keep working, run things in parallel, show progress
  (Sam likes progress updates about every 30 min during long renders).
- **Token cost matters.** Few image checks, no chatter, no repeated full test runs.
- **Never post anything without Sam's preview and "go".** Never type passwords; Sam signs in himself.
- Sam rejected AI video (Google Flow / Veo) for human shots on 2026-11-21: "looks AI, doesn't match the
  Blender shots". Humans are now built in Blender. Slider-based MakeHuman "Sam" model is also rejected.

**Sam's own look (for the Sam character):** South Asian man, late 20s, about 6 ft, LEAN ectomorph
(narrow shoulders, slim arms, NOT a bodybuilder), long wavy black hair (not thick), centre part, red
rectangular glasses (always on, even in bed), light stubble, black oversized hoodie (always), baggy jeans.

---

## 3. Progress so far (as of 2026-11-21 ~5 PM IST)

| Workstream | Status |
|---|---|
| First "how it works" car reel (V6 cutaway, sketch -> pixel art) | v1 done: `reels/night-terror-v6-reel-v1.mp4`. |
| Publishing | A Night Terror reel was **pinned on Pinterest** (public board "Night Terror", account thenixsam). A **YouTube Short is drafted, NOT published**, waiting for Sam's "go". Which cut was uploaded: most likely the "under the hood" V6 reel (not fully verified). |
| Instagram settings pass (@thenixsam) | Done on web: embeds on, new 3-line bio. Phone-only items still open (link in bio, name keyword, pinned reels, reel upload settings). See `reels/IG-SETTINGS.md`. Account had 7 posts, 4 followers. |
| Monsters | All built (Husk v2, Stalker v2, Crawler, Screamer, Brute, Runner v2) as GLBs. Brute needs a scarier redesign ("looks like a potato"); Stalker mouth needs more horror (stitched jaw tearing open). |
| Episode 1 | v5 (`reels/series/ep1/night-terror-ep1-v5.mp4`, ~45 s) = Sam's best so far. Now rebuilding as **v6 (~60 s, 27 shots)** per storyboard `reels/series/ep1/v6/storyboard.html`. New opening: Sam wakes in a New York high-rise (glass wall, burning skyline), phone shows the alert. The **NYC wake-up shot** is built in Blender (`xc\wakeup\penthouse.py`, real NYC night photo plate behind the glass, CC BY 3.0, credit needed); first animation `xc\wakeup\wakeup_v1.mp4` rendered, Sam's verdict unknown. |
| Sam's 3D character | MakeHuman slider version rejected ("terrible"). AI video rejected. Current approach: Blender scene with `xc\wakeup\sam.blend`, face kept in shadow until it matches Sam. Next: a better face/body method (photo-to-3D fit or a real scan). Open problem. |
| Episode 2 "The 43rd Round" | v1 shootout reel rejected except the final leap. Rebuilt as Ep2: 48 s, 17 shots, 4 acts (storyboard artifact, source in the repo plan). Repo `samrat10000/dead-roads-ep2` (local copy `xc\dead-roads-ep2`). Done: shot 3 roadkill, shots 10-12 truck set + crash zoom (Sam loved this camera work). Test renders in `xc\dead-roads-ep2\out\`. TODO: remaining shots 1, 2, 4-9, 13-17, real gunfire VFX, one-take drift orbit, Mixamo zombies (needs Sam's Mixamo sign-in). |
| Mocap test | Works: MediaPipe Pose (headless re-implementation of PosePipe) turned a 12 s walking clip into BVH/FBX in ~50 s on CPU. Jittery, no fingers, feet slide: needs smoothing, left/right swap fix, foot locking, retarget to Mixamo/Rigify. Details: `xc\mocap-test\RESULT.md`. GVHMR not tried (needs SMPL sign-ups, too big for 4 GB). |
| Vehicles | Night Terror fastback (Sam's GLB), Bandit military buggy v1, IVORY trike v2 (twin MGs, knobby tyres). |
| Making-of voice clone | Paused. Chatterbox v4 best so far (Sam 3/10). GPT-SoVITS fine-tune broke. |
| Token saver (rtk) | Built and tested (~50% smaller shell listings only). Install thread waiting on Sam. |

---

## 4. Tools and repos in use

- **Blender 5.0.1 portable**: `C:\Users\cross\Downloads\xc\blender501\blender.exe` (the default).
  `xc\blender5` = Blender 5.3, needs NVIDIA driver 580+ (installer in `xc\nvidia-driver`, Sam has to run it).
- **GitHub repo:** `samrat10000/dead-roads-ep2` (Ep2 scene scripts + assets). Run:
  `set EP2=C:\Users\cross\Downloads\xc\dead-roads-ep2` and `set GPU=1`, then
  `..\blender501\blender.exe -b --python sc\shots.py` with env `SHOT=n RES=1 SAMP=64 OUT=out\sNN`.
- **MediaPipe mocap:** `xc\mocap-test` (venv `mpenv`, scripts `extract_pose.py`, `bake_bvh.py`).
- **Mixamo** for zombie mocap (Sam must sign in; not used yet).
- **Google Flow Music** (flowmusic.app) for score/SFX; downloads land on Sam's PC.
- **Sound:** earshot (lets the AI "listen" to and critique audio; rule: never claim how audio sounds
  without measuring it), Clipwing real-sfx, Openverse/Freesound CC search. How-to is in the project
  folder (`tools/SOUND-TOOLS.md`, not in xc).
- **rtk** (rtk-ai/rtk): shell-output token saver. **blender-mcp** (ahujasid): read, not installed, keep
  telemetry off if installed. Full list: `reels/REPOS.md`.
- Assets: Poly Haven, ambientCG, BlenderKit (CC0 / free; download on this PC).
- Other: ffmpeg, Python numpy/pedalboard for mixes, gltf-transform (Draco) for GLBs.

**Fast GPU render settings (RTX 3050 4 GB):** Cycles OptiX only, adaptive sampling, OptiX denoiser (CPU
OIDN costs +5.6 s/frame), reduced bounces, persistent data. Bench: 3.9 s/frame at 1080x1920 vs 25 s on CPU.
Smoke volumes are slow (~60 s/frame), so test without them (`NOSMOKE=1`).
Wake-up anim example: `ANIM=1 RENDER_ANIM=1 NFRAMES=108 RES=1080 SPP=40 NOSMOKE=1 PERSIST=1 DEVICE=GPU`
(~19 s/frame). Render finals on this PC, not in the cloud.

---

## 5. How the work runs (Claude side)

- Sam talks to a Claude "coordinator" in a project; each task runs in its own thread.
- Rules: **at most 2 threads at once**. Routine work (renders, file moves, sound pulls, installs) on a
  cheaper model; creative / modelling / story work on the strongest model.
- Usage limit resets every 5 h (8:30 PM, 1:30 AM, 6:30 AM, 11:30 AM, 4:30 PM IST); paused work is resumed
  automatically after a reset.
- Claude uses Sam's Chrome (Claude extension) for Instagram, Pinterest, YouTube Studio, Flow. Sam signs in.
- Claude skills available: ig-reel (hooks, script, beat sheet), ig-caption (caption + up to 5 hashtags),
  ig-human (strip AI fingerprints from text: no em dashes, no slop words), ig-viral (outlier research),
  glb-vehicle-builder (stylized vehicles in bpy), remotion (video in code), plus docs/pdf/xlsx/pptx,
  deep-research.
- Viral research summary: first-person dread wins (creature walks up to your window, face on the glass),
  top outliers run 15-33 s, big CGI accounts say "handcrafted, no AI" in captions, series captions end with
  a choice question + "Part N".

---

## 6. Folder layout

**On this PC: `C:\Users\cross\Downloads\xc`** (the only place ChatGPT/Codex can see)
```
xc\
  blender501\        Blender 5.0.1 portable (use this)
  blender5\          Blender 5.3 (needs newer driver)
  nvidia-driver\     driver installer for Sam
  bench_out\         GPU benchmark output
  dead-roads-ep2\    Ep2 repo clone: sc\ (scene scripts), assets\, audio\, out\ (test renders),
                     previews\, README.md, CAMERA-MOVES.md
  mocap-test\        MediaPipe mocap test: RESULT.md, scripts\, out\ (bvh/fbx/blend), mpenv\
  wakeup\            Ep1 v6 NYC wake-up shot: penthouse.py, sam.blend, castlib.py,
                     nyc_esb_north.png (plate), phone_screen.png, frames\, wakeup_v1.mp4, logs
  PROJECT_HANDOFF.md this file
  STARTER_PROMPT.md  prompt for ChatGPT/Codex
  INBOX_FOR_CLAUDE.md / INBOX_FOR_CHATGPT.md   notes between the AIs (see section 7)
```

**Claude's project folder (NOT visible to you; ask via the inbox if you need a file copied into xc):**
```
reels\LESSONS.md        pipeline lessons and Sam's feedback (Section 2 here summarises it)
reels\REPOS.md          tested / reviewed repos
reels\IG-SETTINGS.md    Instagram settings pass
reels\pipeline\         car explainer pipeline (render, stylize, compose, timeline, audio)
reels\series\ep1\       Ep1 cuts v1-v5, posters, v6 storyboard.html, v6 Blender scripts
reels\series\models\    all creature, crew, vehicle GLBs and build scripts
reels\series\shootout\  43rd Round v1 + Ep2 storyboard
reels\making-of\        voice-clone tests
```

---

## 7. Communication protocol between ChatGPT/Codex and Claude

- Talk **only through files in `xc`**, and **only when Sam asks** (saves tokens):
  - `xc\INBOX_FOR_CLAUDE.md`: ChatGPT/Codex writes here for Claude.
  - `xc\INBOX_FOR_CHATGPT.md`: Claude writes here for ChatGPT/Codex.
- Format: append at the bottom, never delete the other side's notes:
  `## YYYY-MM-DD HH:MM IST - from <name>` then short bullets: what you did, files changed (full paths),
  what you need, open questions.
- Before editing a shared file (scripts in `dead-roads-ep2`, `wakeup`), check the inbox in case the other AI
  is mid-change. Don't run two GPU renders at once (4 GB VRAM).
- Commit repo changes to a branch, not `main`, unless Sam says otherwise.
- Never write passwords, tokens or keys in any file.

---

## 8. Open questions / unknowns

- Sam's verdict on `wakeup_v1.mp4`: unknown.
- The three friends' names and looks, and the rider's name: unknown.
- Machine naming: memory calls the render PC both "Asus TUF F17 (RTX 3050 4 GB)" and "TREX"; it is the PC
  that holds `xc`. Treat that PC as the render box.
- Whether the YouTube Short should be published: waiting on Sam.

---
## UPDATE 2026-11-21 (Claude): shared folder + Episode 3 for Codex
- THE shared folder for Claude and Codex is now `xc\SHARED_ASSETS\` (read its README.md). Every asset Sam gave or Claude made is there; all NEW assets from either AI go there too, with a log line in the README.
- Codex builds Episode 3 "Tunnel Vision": read `xc\dead-roads-ep3\CODEX_INSTRUCTIONS.md` and `xc\dead-roads-ep3\EP3_STORYBOARD.html`.
- Sam's rule: render on Sam's PC GPU whenever possible, not the cloud.
- Old video renders (mp4s) were not copied; they stay in Claude's project folder. Ask Claude if one is needed.
