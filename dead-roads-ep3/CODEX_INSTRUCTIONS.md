# CODEX INSTRUCTIONS: build Episode 3 "Tunnel Vision"

Written by Claude on 2026-11-21 for ChatGPT / Codex, at Sam's request. **Sam is the boss.** Sam's words win over this file.

Sam's goal, in his words: Codex does Episode 3, and the result must be **"10x best"**, at a **"$10 billion movie" standard**. Everything you need is in this file and the shared folder. Read all of it before you touch Blender.

---

## 0. Read these first, in order

1. This file.
2. `xc\PROJECT_HANDOFF.md` (whole project, history, tools).
3. `xc\SHARED_ASSETS\README.md` (every model, sound and file, with status).
4. The Episode 3 storyboard: `xc\dead-roads-ep3\EP3_STORYBOARD.html` (open it in a browser). Live version: https://claude.ai/artifact/JYAypPuniitLaG7EhGbGcY. It has 19 pixel frames, the camera, action, sound and models per shot, and a **"Copy shot list JSON"** button. Save that JSON as `xc\dead-roads-ep3\SHOTS.json`.
5. `xc\SHARED_ASSETS\project\reels\shootout\v2\camera-moves.md` and `xc\SHARED_ASSETS\project\reels\LESSONS.md`. (Exact path: `xc\SHARED_ASSETS\project\reels\series\shootout\v2\camera-moves.md`.)
6. The Episode 2 code you build on: `xc\dead-roads-ep2\` (GitHub repo `samrat10000/dead-roads-ep2`). `sc\ep2.py` builds the street, truck, zombies and cameras; `sc\lib.py` has `zombify()`, `pbr()`, `use_scanned_city()`, `prop()` and the `GPU=1` OptiX switch.

## 1. The shared folder (very important)

- **`C:\Users\cross\Downloads\xc\SHARED_ASSETS\` is THE shared folder between Claude and Codex.** Every asset Sam gave and everything Claude made is in there.
- **From now on, every new asset you make goes in there too** (new models, textures, rigs, mocap, renders you want to keep, music, SFX), and you add one line to the log at the bottom of `SHARED_ASSETS\README.md`. Claude does the same.
- Never delete or overwrite the other AI's files. Save new versions (`-v2`).
- Episode 3 work lives in `xc\dead-roads-ep3\`:
  - `sc\` your scripts (one script per shot is fine, or one script with `SHOT=n`)
  - `assets\` Ep3-only assets (also copy finished reusable ones into SHARED_ASSETS)
  - `frames\shotNN\` rendered frames (PNG or EXR)
  - `audio\` score, SFX, mix
  - `out\ep3.mp4` the finished episode, plus `out\ep3-phone.mp4` (smaller file)

## 2. Talking to Claude

- Write to Claude only by appending a dated note to `xc\INBOX_FOR_CLAUDE.md`. Claude answers in `xc\INBOX_FOR_CHATGPT.md`. Append only, never rewrite.
- Do it only when Sam asks, or when you are truly blocked (token saving).
- **Only one GPU render at a time across both AIs.** Before a long render, append a line `RENDERING ep3 shot N, started HH:MM IST` to `INBOX_FOR_CLAUDE.md`, and `DONE` when it finishes.

## 3. Step one: research before building (Sam asked for this)

Before you build, **search the web for the best current repos, add-ons and techniques** for this kind of realistic Blender animation. Evaluate them, use the ones that help, and write what you found in `xc\dead-roads-ep3\RESEARCH.md` (name, link, what it does, licence, tested yes/no, verdict). Cover at least:

- **Mocap / realistic motion:** video-to-motion (GVHMR, WHAM, 4DHumans, MediaPipe/PosePipe; MediaPipe already works on this PC, see `xc\mocap-test\RESULT.md`: it needs smoothing and foot-lock cleanup), Mixamo (free Adobe sign-in, Sam signs in), Rokoko free mocap library, CMU mocap, Auto-Rig Pro / Rigify retargeting.
- **Crowds:** Geometry Nodes instancing with random animation offsets, crowd add-ons.
- **Physics:** rigid body ragdolls, car crash deformation (shape keys, Cell Fracture, soft-body denting), destruction.
- **Fire, smoke, steam, sparks, rain:** Mantaflow vs. VDB stock elements (JangaFX EmberGen free VDBs, Poly Haven), 2D real-footage elements composited in.
- **Camera realism:** Camera Shakify (real recorded handheld shake), lens distortion, focus breathing, VHS / camcorder emulation (real VHS LUTs, chroma bleed, head-switch noise).
- **Assets:** Poly Haven, ambientCG (CC0), BlenderKit (free tier, Sam signs in), Sketchfab CC models (check licences, credit CC-BY).
- **Grade / finish:** AgX, film grain, sensor noise, motion blur, ffmpeg finishing.

Report the top findings to Sam in 5 lines before you commit to a direction.

## 4. Episode 3 in one paragraph

Episode 2 ended with the Stalker leaping at the rider and a smash to black. **Episode 3 reveals what hit in that black: Sam's Night Terror car T-bones the Stalker mid-air.** Sam and the rider meet (forearm grip, no words). The Stalker lifts the truck off itself. A Screamer calls the horde. The car does a J-turn and flees, the Stalker gallops after it and gets onto the roof, and its claws punch through the headliner while the rider fires up through the roof. At a tunnel mouth (CLEARANCE 12'6") the concrete lip rips the Stalker off and snaps its LEFT antler. Inside, quiet. The single headlight crawls over a jam of abandoned cars. Someone is sitting upright in every one. All heads turn into the light. Black. Far behind, the Stalker's click.

**Specs:** 48.0 s, 19 shots, 24 fps (1,152 frames), 1080×1920 vertical. Hook text **"IT NEVER LANDED."** on frame 0 only (it is the thumbnail, so it must be fully visible on frame 0). No other on-screen text except the tiny camcorder REC overlay.

## 5. Shot list (same as the storyboard JSON)

| # | Time (s) | Name | Camera | Action | Sound |
|---|---|---|---|---|---|
| 1 | 0.0–2.0 | It never landed | Low road cam 18 mm, exactly the Ep2 leap angle | Stalker mid-leap over lens, rain around it. Hook text frame 0. | Rain, its Ep2 scream picking up mid-breath |
| 2 | 2.0–3.5 | High beams | Handheld, rider's eye line, 24 mm, looking up | Body fills the sky; a white high beam blows out the left of frame | V8 roars in from left, long horn |
| 3 | 3.5–6.0 | T-bone | Low side-follow 28 mm, Stalker kept centred | Car hits Stalker mid-air ~70 km/h, carries it 10 m into the box truck. Glass, sparks, truck rocks. | Impact = downbeat, score slams in |
| 4 | 6.0–8.0 | Dashcam | Dash camcorder (VHS), 4:3 inside 9:16 | Same hit from inside: windscreen spiders, Sam's hands jolt, antlers scrape past glass | Mic clipping, thump, grunt |
| 5 | 8.0–10.5 | Steam | Handheld doc, eye height, walking in | Crumpled bonnet steaming, LEFT headlight dead, trike on its side, driver door opens | Radiator hiss, ticking metal, far alarm |
| 6 | 10.5–13.0 | Take my arm | MCU handheld 50 mm, low | Sam reaches down, she locks his forearm, he hauls her up in one motion | Leather creak, breaths, rain |
| 7 | 13.0–15.0 | Last belt | Insert 85 mm handheld | She takes the one live belt from the trike tray and slings it | Brass rattle, buckle snap |
| 8 | 15.0–17.5 | It moves | 20 mm on the asphalt under the truck | Antler tip twitches in the puddle, a clawed hand slaps into water | Click-growl; score falls to pulse |
| 9 | 17.5–20.0 | Lift | Crash zoom up over the truck roof, then fast pull-back | Truck tips up; camera rushes to its face pushing up from beneath, rips back as they dive into the car | Metal groan, sub swell, doors |
| 10 | 20.0–22.0 | Screamer | Handheld wide 35 mm, street level | Rooftop silhouette screams; windows down the street fill with runners | Approved Screamer take; full drive |
| 11 | 22.0–25.0 | J-turn | Camera-car orbit, one continuous move | Reverse + 180° spin in ONE smooth arc, single headlight sweeps the horde | Gearbox whine, tyres, engine on beat |
| 12 | 25.0–28.0 | Gallop | Handheld from back seat through rear window | Stalker on all fours gaining, horde behind under street lamps | Gallop on asphalt, engine strain |
| 13 | 28.0–30.5 | On the roof | Dash camcorder (VHS) | Roof dents, claws punch through headliner, she fires pistol up 3×, flashes light cabin | Roof hits on beats, 3 shots |
| 14 | 30.5–33.5 | Clearance 12'6" | Low side-follow 24 mm, real speed | Tunnel mouth rushes in, Stalker rises on roof, hits the lip, ripped off, LEFT antler snaps | Bone on concrete, scrape |
| 15 | 33.5–36.0 | Antler | 20 mm on tunnel floor looking back | Stalker tumbles at the mouth, shrinking; broken antler skids past lens | Skitter, score rings out under low-pass |
| 16 | 36.0–40.0 | Breathe | Dash camcorder (VHS) two-shot | Quiet. She reloads, steady hands. Sam's hands shake on wheel. Wind through claw holes | No music. Ticks, wind, drip |
| 17 | 40.0–44.0 | Traffic | Handheld over Sam's shoulder through cracked glass | Headlight crawls over a jam of abandoned cars; stop; a figure upright in every car | Tyres on grit, brake squeak, silence |
| 18 | 44.0–46.5 | Heads turn | Slow handheld push to one windscreen 50 mm | Every head turns into the light at once (0–2 frame offsets), milky eyes catch the beam | Necks cracking, held breath |
| 19 | 46.5–48.0 | Click | Hard cut to black | Black, then the Stalker's click from the tunnel mouth | Sub hit, click echo |

Render budget: 1,152 frames × ~4 s = ~77 min per full pass on this PC. Do blocking at low res first (below).

## 6. Assets for each part (all in SHARED_ASSETS, see its README)

- **Night Terror car:** `SHARED_ASSETS\originals_from_sam\Night_Terror_Fastback_v2.glb`. Add: nose crumple shape key (after shot 3), LEFT headlight dead from shot 5 on (steady, never flicker), spidered windscreen, roof dent + claw-hole shape key (shot 13 on). Tyres must read as RUBBER (matte, squash where they meet the road), never metal.
- **Rider:** `SHARED_ASSETS\blends\rider.blend` (rigged v3.2). Poses: being pulled up, walking, seated passenger, firing a pistol upward.
- **Sam:** `SHARED_ASSETS\blends\wakeup\sam.blend`. Driver seated, climbing out, reaching down. Face mostly in shadow (his face build is not approved yet).
- **Stalker:** `SHARED_ASSETS\blends\stalker_rig.blend` (+ `stalker-v2.glb`). Separate the LEFT antler for the snap. Needs gallop, roof crawl, ragdoll tumble.
- **Trike (wrecked):** `SHARED_ASSETS\blends\trike.blend` / `trike-v2.glb`. On its side, bent front cage.
- **Street + rusted box truck:** rebuild with `xc\dead-roads-ep2\sc\ep2.py` (same set and truck as Ep2 shots 10–12, with CC0 assets in `xc\dead-roads-ep2\assets\cc0`). Ep3 shot 1 must match Ep2 shot 16's framing.
- **Screamer:** `screamer-v1.glb`. **Runners/walkers:** `runner-v2.glb`, `blends\walker.blend`, instanced 30–60, mostly backlit. **Husks:** `husk-v2.glb`, seated pose, 40+ instances in the car jam.
- **NEW to build:** tunnel set (dirty tiled walls, concrete ceiling, dead strip lights, lane divider, mouth with "CLEARANCE 12'6"" sign, ~200 m in repeated sections); abandoned car jam (6–8 real car models from Poly Haven / BlenderKit / Sketchfab CC, instanced 25+, some doors open, dust on glass); small 90s camcorder taped to the dashboard (the in-story camera).

## 7. Render recipe (this PC, RTX 3050 4 GB)

- **Sam's rule (2026-11-21, for all threads): render on Sam's PC GPU whenever possible, not in the cloud.**
- Blender **5.0.1 portable: `xc\blender501\blender.exe`**. (Blender 5.3 in `xc\blender5` needs NVIDIA driver 580+; this PC has 566.07.)
- Cycles, device **OptiX only**, adaptive sampling, **OptiX denoiser** (CPU OIDN costs +5.6 s/frame), reduced bounces, **persistent data on**. Benchmark: ~3.9 s/frame at 1080×1920 vs 25 s on CPU. Smoke volumes are slow (~60 s/frame), so use them only where they matter, or composite real smoke elements instead.
- VRAM is 4 GB: keep textures at 2K except hero close-ups, instance crowds, hide off-screen objects per shot.
- Workflow: block every shot at `RES .25`, few samples, check framing with a contact sheet, then final. Frames skip-if-exist so renders can resume. Use `render.use_placeholder=True` with `use_overwrite=False` if running two queues.
- Motion blur on (Sam wants real-camera blur). `motion_steps` 6 for spinning wheels. Wheels must spin the right way and stay on the road.
- Colour: AgX, low-key night grade, no oversaturation.

## 8. Camera grammar (Sam loves these)

- **Default = handheld documentary**: someone filming from the street at eye height with natural operator shake and late reframes. "As if someone is always recording." Never drone-smooth, never floating CG camera.
- **Dash camcorder (VHS)** for shots 4, 13 and 16: real VHS softness, chroma bleed, head-switch noise on the bottom few pixels, a small `REC ● 3:47 AM` in the corner. Nothing else on screen.
- **Signature moves to reuse** (Sam called them "crazy", the best part so far): the **low side-follow** that keeps the flying body centred (shots 3, 14); the **crash zoom up and over the roof to the creature's face, then a fast pull-back** (shot 9; keep the camera above any occluder); the **20 mm camera on the asphalt at the tyre** (shots 8, 15).
- Fury Road centre framing in fast cuts, so the eye never hunts.
- Use many real angles and close-ups. Web-series cutting. **Never a slideshow**: no sweep, slide or whip transitions, no sub-1-second inserts, no pans across still frames.

## 9. Sam's rules and taste: every one applies

**Realism (the biggest rule, every step):**
- It must look like real footage and **never AI-made**. Real-camera imperfections: handheld micro-shake, low-light sensor noise, motion blur, slight focus breathing, lens smudge/rain on lens. Ordinary messy real locations. Natural skin. No glossy, symmetric or over-graded look.
- **No dithered / dotted pixel look**, ever.
- Use real scanned assets (Poly Haven, ambientCG, BlenderKit) instead of procedural boxes. A white-box truck or flat box buildings read as fake.
- **No fake UI** in frames (Sam said fake Blender UI looked AI-made).

**Characters:**
- **Perfect human anatomy**: hands, fingers, arms, movement. Broken, bent-back or splayed fingers instantly read as AI. Relaxed hands hang palm toward the thigh. Arms must never look squeezed inward or broken. Zombies may be unstructured.
- **References first**: never build or pose a body without real reference photos, and compare renders side by side before sending.
- Creatures must MOVE (no frozen poses). The Stalker should act: head turns, eyes catch light, jaw opens.
- Sam's own look: see SHARED_ASSETS README (lean 6 ft, black hoodie, baggy jeans, red glasses always on).

**Motion and editing:**
- No slow-mo in Episode 3 (Ep2 used it). Never use slow-mo as filler or repeat it. If a freeze is ever used, it is ONE take (live → ramp down → camera glides → ramp back), never cut to a new angle.
- Drifts, turns and stops are one smooth motion, never stop-start.
- **No flickering or toggling car lights.** The dead headlight stays dead.
- No big title text over the best shots. Only the frame-0 hook.

**Music and sound:**
- Music is what makes the series famous. It must never cut out suddenly.
- Use **Google Flow Music (flowmusic.app)** for score and designed SFX. Sam signs in himself in his Chrome. Give it a prompt and/or upload existing sounds, then download results.
- Score style = the LOCKED v5 sound Sam loved: orchestra + original 80s analog synth (Stranger Things mood, never its melody) + **real recorded electric guitar doubled by bass**. Reference: `SHARED_ASSETS\project\reels\series\ep1\flow\night-terror-score-v5-reference.mp3`.
- **Never** raw AI music (Sam hated the ACE-Step versions) and **never synthetic guitar** (it "irritates the ears").
- SFX must be REAL recordings where possible (Freesound / Openverse CC0, keep CC-BY credits). Sam hates synthetic SFX. The engine must be a grumbling V8, never EV-sounding. Creature sounds are designed carefully (Sam hated the crawler sound). Keep the approved Screamer scream and the Ep2 Stalker voice.
- Sync every hit to picture. Loudness: avoid huge level swings and mud below 150 Hz.
- Episode 3 score map: 0–3.5 s no music; 3.5 s impact = downbeat; 8–20 s low pulse; 20–33.5 s full drive at 120 BPM; 33.5–36 s rings out under a low-pass sweep over 2 bars; 36–46.5 s silence + ambience; 46.5 s sub hit, then the click.

**What Sam loved (copy the spirit):** the Brute/"reindeer" Stalker encounter (10/10), the Ep1 garage scene ("best scene ever"), the Screamer, the Stalker scream, the Ep2 roadkill side-follow, the crash zoom over the truck roof, the low tyre cam, the final leap of Ep2, the v5 music ending.
**What Sam hated (never repeat):** slideshow/sweep/whip transitions, big title text over shots, frozen poses, toy-like green zombies in plaid, glowing-line bullets, the white-box truck, flickering headlights, stop-start drifts, AI music, synthetic guitar, the crawler sound, broken-looking arms and splayed fingers, anything that "looks AI".

## 10. Working rules

- Work only inside `C:\Users\cross\Downloads\xc`.
- **Token care:** short replies, no long progress chatter, no re-running things without a reason, few image checks. Routine work (renders, file moves, installs) should be cheap.
- Show Sam progress: a still from each finished shot as you go, and a progress line about every 30 minutes during long renders.
- Don't wait for Sam between steps. Keep going and run things in parallel where it doesn't break the one-GPU-render rule.
- Never type passwords; Sam signs in to Mixamo, BlenderKit, Flow, etc. himself.
- **Never post anything** to Instagram/YouTube without Sam's preview and "go".
- If something is unknown, say "unknown" and ask Sam. Don't guess.
- When Sam calls the episode final, write down what you learned in `xc\dead-roads-ep3\LESSONS.md`.

## 11. Tools and repos already in use

| Tool | Use |
|---|---|
| Blender 5.0.1 + Cycles OptiX | everything 3D |
| GitHub `samrat10000/dead-roads-ep2` (= `xc\dead-roads-ep2`) | Ep2 scene code to build on |
| MediaPipe / PosePipe | video-to-mocap, works here (`xc\mocap-test`) |
| Mixamo | mocap clips + auto-rig (Sam signs in) |
| Poly Haven, ambientCG, BlenderKit | real scanned assets |
| Google Flow Music | score + designed SFX |
| earshot | lets an AI "listen" to audio and check sync (`SHARED_ASSETS\project\tools\`) |
| Clipwing real-SFX, Openverse/Freesound | real recorded SFX search |
| rtk (github.com/rtk-ai/rtk) | shrinks shell output to save tokens; never at the cost of quality |
| blender-mcp (ahujasid) | optional live Blender control; turn telemetry OFF |
| ffmpeg | grade, grain, VHS finishing, mux |

More notes: `SHARED_ASSETS\project\reels\REPOS.md`.

## 12. Deliverables

1. `RESEARCH.md` + 5-line summary to Sam.
2. Blocking contact sheet of all 19 shots at low res, for Sam.
3. Final frames, score + SFX mix, `out\ep3.mp4` (1080×1920, 24 fps) and `out\ep3-phone.mp4`.
4. Credits file for any CC-BY assets or sounds.
5. New reusable assets copied into `SHARED_ASSETS` with a README log line each.
