# CODEX BRIEF: make 5 O'CLOCK Episode 2 ("Day 2: The Koban")

You are Codex. Sam (the owner, the "director") is running a trial: you will make **Episode 2** of his vertical anime reel series **5 O'CLOCK**, from story to finished silent animation, on your own, to the same standard Claude is held to. Read this whole file before doing anything. It is long on purpose: every rule in it comes from something Sam asked for or rejected.

## 0. READ FIRST: corrections and extra references (added by Claude on Sam's PC, 2026-11-23)

These override anything below that disagrees.

**A. The quality bar is shot 01 v4, not v1.** Sam locked `01_speaker_v4` ("v4 was more better, keep v4").
- `reference/shot01_v4/` holds the v4 clip, 4 full-size frames and the exact v4 scripts: `build_s01_v4.py`, `paint_bg.py`, `comp_s01.py`, plus the CC0 crow model.
- `reference/shot01/` (v1) is history only. Don't copy it.
- `reference/SHOT_RULES.md` holds the binding rules taken from v4, plus every note Sam gave on later shots: real garment cut on clothes, real roof tiles, textured verges, depth cues on flat areas, organic leaf outlines, no primitive-built creatures. Where SHOT_RULES.md and section 5 differ, SHOT_RULES.md wins.

**B. Running it on this PC (proven; RTX 3050, Blender 5.0.1, EEVEE).**
- The build scripts expect `sys.argv[1:]`. Under blender.exe, pass the arguments after `--` (the v4 script here is already patched): `C:\Users\cross\Downloads\xc\blender501\blender.exe -b --python build_s01_v4.py -- <ABSOLUTE outdir> 1.0 all`.
- Always give an ABSOLUTE outdir. A relative one made Blender write to `C:\test\`.
- Shot 01 also needs `set CROW_GLB=<path>\crow_tehbucket_raven_cc0.glb`. Blender prints `SUN_SCREEN x y`.
- Then run `python paint_bg.py bg.png <x> <y>`, then `python comp_s01.py <celdir> bg.png <compdir>`, then the ffmpeg line in section 5.
- Measured on this PC: about 0.6 s per 1080x1920 cel frame, about 3 s per comp frame, so a 72-frame shot takes about 5 minutes. Full notes: `C:\Users\cross\Downloads\xc\anime-5oclock\ep1v3\pc_test\` (on GitHub: branch `claude/project-thread-31g858`, `anime-5oclock/ep1v3/pc_test/RENDER_NOTES.md`).
- Run every render at below-normal process priority, one at a time. The teaser has priority on this PC, so never stop its jobs.

**C. More material on this PC (read only, don't edit).**
- `C:\Users\cross\Downloads\xc\anime-5oclock\ep1v3\`: Ep1 v3 shot sources for 02_mirror and 03_kiriyama (`src_v2`), made to the same rules. Use them as working examples of mirrors, painted figures, roofs, fields and the tower.
- The toon Sam character is the VRoid sample "Sakurada Fumiriya" (CC0) with the VRM add-on v4.10.5, plus Sam's hoodie, glasses and headphones built by `build_sam.py`.
  - On this PC: `C:\Users\cross\Downloads\xc\anime-5oclock\toon3d\` (model in `dl\base\sakurada_fumiriya\`, add-on in `dl\vrmaddon\vrm_ext.zip`, licences in `SOURCES.md`).
  - On GitHub: `anime-5oclock/assets/toon_sam/`.
- Research:
  - `anime-5oclock\granite-waves-study.html`: the Granite Waves art-form study.
  - `anime-5oclock\REEL_RESEARCH.md`, `WORKING.md` sections 2-6: what works on Instagram, the voice analysis, and the night-road void reel.
  - `anime-5oclock\MUSIC_REFERENCE.md`, `LINKS.md`.
  - `anime-5oclock\frames\`: reference frames.
- Sam's own words: `anime-5oclock\story_thread\DECISIONS.md` (what he approved and rejected, quoted) and `story_thread\IDEAS.md` (all story versions, the rejected pitches and the open questions).

**D. What Sam already rejected (don't repeat it).**
- The Ep1 v2 2D reel was "not up to the mark". It had shapes drawn by code, a 3D character pasted on a flat 2D background so the styles didn't match, and too little real acting.
- Creatures made of ovals, spheres or cut-out cards. Feet that hover.
- Dotted or dithered looks.
- Walls of text. Lead with pictures and clips.
- The five early story pitches (SURGE, KONBINI 24, LAST TRAIN ZERO, LIGHTS OUT, FORECAST).

**E. Error-catching lessons Claude learned the hard way. Apply them.**
- Look at EVERY in-between at full size, not just the keys.
  - The Ep1 shot 003 reach went through two bad in-betweens (the elbow jutting sideways) before it was right.
  - When an IK elbow or knee looks wrong, solve the pole position numerically (search candidates and measure the joint position) instead of guessing and re-rendering.
- Check pixel values numerically, and check the real output file, not a viewer preview.
- Keep the minimum of 3 self-check passes per shot (section 6). If a shot still fails after 6, show Sam the best version with an honest list of what is still wrong. Never hide a flaw.
- Never overwrite a version Sam has seen. New version, new file name.

**F. Your files.** Keep your own log in `codex_ep2\WORKLOG.md` (section 9) and your outputs in `anime-5oclock\ep2_codex\`. Don't edit Claude's `WORKING.md`, `DECISIONS.md` or any Ep1 folder. This is a side-by-side trial.

---

Everything you need is in this folder:

```
codex_ep2/
  CODEX_EP2_BRIEF.md        <- this file (the only instructions)
  reference/
    ep1_story.html           <- Episode 1 story page (open in a browser): 18 shots, script, cast, world
    SHOT_RULES.md            <- the binding shot rules (from 01 v4 + Sam's later notes)
    shot01_v4/               <- Episode 1 shot 01 v4: the LOCKED QUALITY BAR (clip, 4 frames, src/)
    shot01/                  <- Episode 1 shot 01 v1: history only (superseded by v4)
      01_speaker_v1_f*.png   <- full-size frames of shot 01
      src/build_s01.py       <- Blender scene + toon shading + animation (the recipe)
      src/paint_bg.py        <- painted anime sky / mountains / town background
      src/comp_s01.py        <- composite + light wrap + bloom + dust + grain
      src/run_full.sh        <- how the full shot is rendered and encoded
  WORKLOG.md                 <- YOU create and keep this (see section 9)
```

---

## 1. Who Sam is and what he wants (read twice)

- Sam is the main character of the series. He watches every frame. He is a demanding director who wants **"100 times"** more detail and precision than average, a result that will make him **stand out** on Instagram and YouTube Shorts.
- **The animation is the product.** Sam's exact words: "the animation is the thing that will stand it out from others. So it shouldn't be degraded." Never show him compressed previews as the main deliverable.
- **Art form reference:** the hand-drawn 2D anime reel series **"Granite Waves" by Tezeze** (Instagram). Copy its *art form and level of animation*, never its characters, scenes or story. Its look: clean thin dark ink line, flat cel colour with one shadow tone, painted soft-focus backgrounds, one strong accent colour, held poses with small precise real animation, cinematic camera.
- **Sam's bar:** "The animation should be exactly like that reel... the movements exactly like that... the people, monster, props, everything needs to be 100 times better than the reel."
- **It must never look AI-made.** No AI images, no AI video, no morphing, no warping, no "puppet stretch" animation, no glossy symmetric over-graded look. If a frame looks like it came from an image generator, it is rejected.
- **Perfect human anatomy.** Hands, fingers, elbows, limbs must be right. Broken fingers or arms instantly read as AI. Relaxed hands hang with the palm toward the thigh. Sam (the character) is a **lean ectomorph**: narrow shoulders, slim arms, flat chest. Never bulky.
- **References first.** Never build a character, body, creature or pose without real reference images or video. Compare your render side by side with the reference before you show it.
- **One shot perfect first.** Sam's rule (2026-11-23): "We need to make one short perfect, and rest is easy." Make your first shot perfect, write down exactly how you made it, and make every other shot to that same recipe and standard.
- **Shot by shot.** Show Sam each finished shot as its own clip plus full-size PNG frames. Never show the whole episode first. Only cut the episode together from shots he passed.
- **Sound comes last.** Write the dialogue script now, but do NOT make music or voices until every shot's animation is approved. (When that time comes: real recorded instruments only, piano-led like Sam's music reference reel https://www.instagram.com/reel/DesekZbo2jK/ ; never AI music like ACE-Step; dialogue and music must blend, music thins under each line.)
- Sam does not want to read walls of text. Lead with pictures and clips. Keep messages short and plain.
- Sam watches token and time cost. No endless exploration. Work with a plan.

## 2. The series bible (keep it consistent)

- **Logline:** "The 5 PM chime was never meant for children. Kiriyama built it in 1964 to keep a door shut. This year, the other side learned the song."
- **Kiriyama:** a fictional mountain-valley town on the sea in Japan, ~6,000 people, one train line, rice fields. Orange curve mirrors on every corner, Showa-era loudspeaker horns on concrete poles (the real "bosai musen" 5 PM chime system), the 1964 radio tower with a blinking red light on the ridge, a lone vending machine, a railway crossing, a tobacco & sweets shop, a koban (police box).
- **The chime:** every Japanese town plays a song at 5 PM to send children home. Kiriyama's has **four notes**. It must have four.
- **The other side:** a mirror Kiriyama. Same town, turned around (all writing reversed, hair parted the other way). Ruled by **The Listener**: a colossal being beyond a crack in the sky, taller than the mountain, whose head is a crown of hundreds of rusted Showa loudspeaker horns that all turn together like sunflowers following a sound; long arms with too many joints. It learned the song.
- **Rules notebook** left in the koban by **Officer Tanaka** (survived 11 days, decades ago):
  1. Be indoors, with your ears covered, at 5:00.
  2. If the speaker says your name, do not answer.
  3. Never pick up a ringing phone that belongs to one of the gone.
  4. Don't count the people at the bus stop. There is always one more.
  5. Nothing red outside.
  6. If someone from the town waves at you, don't wave back.
  7. (torn out)
- **Cast:**
  - **Sam, 17:** lean, slightly-too-long dark hair, big over-ear headphones, oversized grey hoodie with uneven strings, phone always near 3% battery. Quiet, a little sarcastic.
  - **Mirror-Sam:** identical but hair parted the other way, hoodie strings swapped, pupils never catch the light, moves half a beat early.
  - **Mom:** on the REAL side now. Warm, tired, searching for Sam.
  - **Mirror-Mom:** looks exactly like Mom from behind. Never shows her face directly.
  - **Grandma Hoshino:** tiny, bent, bamboo broom, sharp eyes, runs the corner shop, knows the rules.
  - **Narrator:** deep, warm, older man (not too old), close to the mic, unhurried, like telling a secret.

## 3. Where Episode 1 ends (so Episode 2 follows on)

Open `reference/ep1_story.html`. Short version: at 5 PM the chime plays only three notes, the town freezes, Sam (headphones on) is the only one who notices. In the curve mirror the town at night turns to face him. His reflection hums the fourth note, every mirror cracks, The Listener pushes a hand through the sky. The town wakes up mirrored and says "Okaeri, Sam" (welcome home). Through the glass Sam sees his real mom calling for him: **he is on the wrong side now.** Stinger: the notebook's torn rule 7 rewrites itself in Sam's handwriting: "Never finish the song."

## 4. Episode 2 story: "Day 2: The Koban" (63 s, 15 shots, 9:16)

You may improve shots, camera and timing, but keep the spine and the ending. Every shot must have real animation (nothing frozen except on purpose), a camera idea, and one "wow" detail.

| # | Time | Shot | What happens / what moves | Wow detail |
|---|------|------|---------------------------|------------|
| 01 | 0.0-3.0 | Alarm | ECU of Sam's phone on the floor buzzing. The clock reads 6:00 but the digits are mirrored. Battery 3%. The phone vibrates across the tatami. | Hook in 1 second: mirrored digits. |
| 02 | 3.0-7.0 | Wrong room | Sam wakes on his bedroom floor in morning light. Slow push. Everything is mirrored: poster text backwards, the window on the wrong wall, his hair parted the wrong way when he catches himself in a dark phone screen. | Sunlight comes from the wrong side; dust in the beam. |
| 03 | 7.0-11.0 | The crack | Sam at the window. Over the mountains the crack in the sky from Ep 1 is still there; behind a cloud, the crown of horns of The Listener, motionless, huge. Curtains breathe in the wind. | Multi-plane parallax, 5+ layers; clouds drift toward the crack. |
| 04 | 11.0-15.0 | Mirror-Mom | Kitchen. A woman cooking with her back to him, humming three notes. "You're late, Sam." She never turns. Her reflection in the kettle has no face. | Steam animation; the faceless kettle reflection is held for 6 frames only. |
| 05 | 15.0-19.0 | The street | Sam runs out. Townsfolk do their morning routines in perfect unison (four people sweeping on the same beat). They all stop when he passes, then resume. | Synchronised secondary animation: brooms, aprons, shadows. |
| 06 | 19.0-24.0 | The koban | Sam reaches the police box. Inside: dust, a 1964 calendar, a desk, Officer Tanaka's notebook chained to the desk. The lamp flickers. | Light-and-shadow animation; dust motes; the chain sways. |
| 07 | 24.0-29.0 | The rules | Top-down ECU of the notebook, Sam's fingers turning pages (correct anatomy!). Rules 1-6 handwritten; rule 7 torn. | Paper bends with real weight; handwriting is drawn, not typed. |
| 08 | 29.0-33.0 | Mom calls | Phone buzzes: "MOM". Video call. Real Mom in the real kitchen, crying, hears only static. Sam: "Mom! I'm here!" | Phone-screen video look: compression blocks, lag, a frozen frame. |
| 09 | 33.0-37.0 | Behind him | On Mom's video, the real kitchen mirror shows Sam's side, and Mirror-Mom standing right behind Sam. | Tiny detail in the background of a small screen: rewards rewatching. |
| 10 | 37.0-41.0 | The window | Sam spins round: nobody. He turns back to the koban window: in its reflection, Mirror-Mom's hand rests on his shoulder. | Whip-pan with smear frames; hand anatomy perfect and still. |
| 11 | 41.0-45.0 | 16:59 | The phone clock jumps from 7:12 to 16:59. He lost the whole day. | Time-skip shown by shadows racing across the floor in 12 frames. |
| 12 | 45.0-50.0 | The horns turn | Every loudspeaker horn on every pole turns by itself toward the koban (servo creak). Every townsperson stops, turns, faces the koban. | Mechanical motion with overshoot and settle; dozens of horns staggered. |
| 13 | 50.0-55.0 | Rule one | Sam slams the door, crouches, covers his ears (rule 1). The chime plays **four** notes this time, from every direction. In the sky The Listener's horns turn too. | Shockwave rings in clouds per note; dust jumps off the floor on each note. |
| 14 | 55.0-60.0 | The knock | Silence. A knock. Outside, Sam's own voice: "Sam. Let me in. It's my turn now." Cut to black. | The door's frosted glass shows a silhouette with headphones. |
| 15 | 60.0-63.0 | Rule eight | The notebook: a new line writes itself under rule 7, in Sam's handwriting: "8. Don't let yourself in." | Ink bleeds into the paper fibres. |

Hidden detail for rewatchers (put it in): in shot 05 one of the sweepers is Grandma Hoshino, and she is the only one sweeping off the beat. She is looking straight at the camera.

### Dialogue script (record ONLY after all animation is approved)

| Time | Shot | Who | Line | Delivery |
|------|------|-----|------|----------|
| 3.4 | 02 | Narrator | "On the other side, everything is the same." | Deep, warm, close. |
| 5.2 | 02 | Narrator | "Just turned around." | A smile you can hear. |
| 12.6 | 04 | Mirror-Mom | "You're late, Sam." | Gentle, but slightly too even. |
| 25.0 | 07 | Narrator | "Officer Tanaka lasted eleven days. He wrote everything down." | Slower. |
| 30.6 | 08 | Sam | "Mom! I'm here! Mom!" | Breaking, too loud for the small room. |
| 42.5 | 11 | Narrator | "Time runs differently on this side." | Matter of fact. |
| 56.5 | 14 | Mirror-Sam | "Sam. Let me in. It's my turn now." | Sam's voice, drier, closer, a hair lower. |
| 60.5 | 15 | Narrator | "Rule eight." | Final, almost tender. |

## 5. The pipeline (proven on Ep 1 shot 01; read the src files)

Use the same pipeline so Ep 1 and Ep 2 match. You may use your own installed skills (ffmpeg, motion/film/animation skills, etc.) wherever they make the result better, but the look must match shot 01.

**Software:** Blender (Sam's PC: portable Blender 5.0.1 at `C:\Users\cross\Downloads\xc\blender501\blender.exe`, RTX 3050 4 GB, OptiX works). Python with numpy, scipy, Pillow. ffmpeg.

**Layers per shot:**
1. **Cel layer (Blender EEVEE, transparent film):** all characters, props and anything that moves in 3D.
   - Toon material = Diffuse BSDF -> Shader to RGB -> RGB to BW -> x0.5 -> ColorRamp (CONSTANT) with 2 tones (shadow, lit) and an optional 3rd highlight; the colour goes into an Emission shader.
   - **Gotcha (cost us an hour):** ColorRamp colours are LINEAR. Convert your sRGB design colours to linear first (see `lin()` in build_s01.py), or everything renders far too light.
   - **Gotcha:** the ramp thresholds are tiny (lit at ~0.035, highlight at ~0.075 after the x0.5) because the diffuse values are low. Measure the BW values with a debug render before choosing thresholds.
   - **Rim light:** backlit anime rim = (Layer Weight Facing > 0.40) AND (dot(normal, sun direction) > -0.15) -> mix to a warm rim colour. Do NOT put rim on flat cards (feathers, paper) or you get ugly bands.
   - **Ink line:** inverted hull (Solidify, flip normals, offset 1, ink material with backface culling), thickness 0.003-0.008 m by object size. Ink colour warm near-black (0.10, 0.06, 0.08).
   - Character and prop animation **on twos** (sample the pose at odd frames and hold), held on threes for weight; camera moves **on ones**. Fast moves get smear frames.
   - Render settings: 1080x1920, Standard view transform, EEVEE, 16 TAA samples, PNG RGBA.
2. **Background layer (painted in code, `paint_bg.py` style):** sky gradient, layered clouds with crisp anime edges and sun-lit undersides and gold rims, fbm mountain ridges with haze, silhouettes of town / tower. Paint 10% oversize so it can push and drift. Blur slightly for depth of field.
3. **Composite (`comp_s01.py` style):** BG push-in slower than the cel layer (parallax), light wrap of bright sky over cel edges, bloom on highlights, dust motes on twos in light beams, a gentle grade (lift shadows toward violet), vignette, fine film grain.
4. **Encode:** `ffmpeg -framerate 24 -i %03d.png -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p NN_name_vN.mp4`.

**Speed (Sam wants fast renders):** cel frames at 1080x1920 took ~10 s each in EEVEE on 4 CPU cores; on the RTX 3050 they are faster. Test at 40% resolution on 4-6 key frames; only render all frames at 100% when the key frames pass your checks.

## 6. How to catch your own errors (do this EVERY shot, before Sam sees anything)

Sam said about Claude: "I see you're picking your own errors and you need to keep on doing this frequently." Do the same.

**Iteration loop per shot (minimum 3 passes, maximum 6 before showing Sam):**
1. Block: camera + layout + key poses only. Render 5-6 key frames at 40%. Make a contact sheet (one image, frames side by side).
2. Look at the contact sheet and write a numbered critique in WORKLOG.md using the checklist below. Be harsh. Fix the worst 3 problems.
3. Re-render the key frames. Compare against the previous sheet AND against your reference images side by side.
4. Repeat until every checklist item passes. Then render all frames at 100%.
5. Check the final frames again (a 12-frame contact sheet across the shot + full-size crops of faces/hands). Then send.

**Checklist (each must pass):**
- [ ] Silhouette: is every character/prop instantly readable as what it is in a black silhouette? (Our v1 crow's wings looked like stacked balls in flight; that fails.)
- [ ] Anatomy: hands, fingers, elbows, necks correct; no broken or squeezed limbs; lean Sam.
- [ ] Motion: real animation in every shot, follow-through on hair/cloth/straps, weight on landings, no floaty or linear moves, no pops except deliberate snaps.
- [ ] Consistency: same character design, colours and line weight as previous shots and as Episode 1.
- [ ] Lighting: one clear light direction matching the painted BG; rim light on the correct side.
- [ ] Composition: subject in a strong place in the 9:16 frame; nothing important cut off; safe from IG UI at bottom 15%.
- [ ] Nothing looks AI-made, morphy, glossy or over-graded.
- [ ] Colour: correct values (check pixel values numerically; previews can lie about brightness).
- [ ] Technical: no flicker between frames, no missing objects, no transparency holes, no z-fighting, no frame-number gaps, correct duration.
- [ ] The shot's "wow detail" from section 4 is clearly there.

Also write your own honest critique in every message to Sam: what works, what you will fix next. Never hide a known flaw.

## 7. Deliverables and naming

- Number every shot and name every file `NN_shortname_vN` (for example `07_rules_v2.mp4`). New version = new file name. Never overwrite a version Sam has seen.
- Per shot send: the clip (crf 14, 1080x1920, 24 fps) + 4 full-size PNG frames (start, key moment, a hand/face close crop if any, end).
- Put outputs in `C:\Users\cross\Downloads\xc\anime-5oclock\ep2_codex\NN_shortname\` with a `src\` folder holding the exact scripts that made them.
- Order: make **shot 01 perfect first** and show it to Sam. After he approves it, write `SHOT_RULES.md` (exactly how you made it: models, materials, colours, thresholds, line weights, timing, camera, post settings), then make every other shot to those rules.
- Only after all 15 shots are approved: assemble the silent cut, then (when Sam says) voices and music.

## 8. Hard rules

- Never type passwords or sign in for Sam; if a site needs a login, ask Sam to do it.
- Never post anything online.
- Git: only push to branch `claude/project-thread-31g858` of `samrat10000/dead-roads-ep2` if asked; never to `main`.
- Don't run two GPU renders at once on Sam's PC; the Night Terror teaser renders have priority.
- Don't change Episode 1 files.

## 9. Your log (so Sam can switch tools without losing context)

Create `codex_ep2/WORKLOG.md` and append a dated entry after every step: what you did, the files made and where, your critique, what is next. Keep a short "Decisions" list at the top (what was decided and why). Before you run low on context or tokens, bring the log fully up to date.

## 10. First thing to do now

1. Read this file and open `reference/ep1_story.html` and the shot01 PNGs and scripts.
2. Reply to Sam in at most 8 short lines: your understanding of Episode 2, your plan for shot 01 "Alarm", the references you will gather, and how long you expect shot 01 to take.
3. Then start shot 01 without waiting.
