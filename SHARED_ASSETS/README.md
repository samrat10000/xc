# SHARED_ASSETS: the one shared folder for Claude and Codex

**Path:** `C:\Users\cross\Downloads\xc\SHARED_ASSETS\`

This is THE shared folder for "Night Terror: Dead Roads". Claude and ChatGPT/Codex both read from it and write to it.
Sam's rule (2026-11-21): **from now on, every new asset either AI makes goes in here** (models, textures, renders, music, SFX, storyboards, scripts). Add one line to the "Log of additions" at the bottom when you add something. Never delete or overwrite another AI's file. Save a new version (`-v2`, `-v3`) instead.

Built by Claude on 2026-11-21 from Claude's project folder plus Sam's original uploads.

---

## Layout

| Folder | What is in it |
|---|---|
| `originals_from_sam\` | Files Sam gave us, untouched. The Night Terror car, the IVORY trike, reference photos, voice sample, screen recordings. |
| `project\reels\` | A mirror of Claude's project folder: every model, script, storyboard, music file and note. Old mp4 renders were left out (ask Claude). |
| `project\handoff\` | Handoff guide, starter prompt, inbox files (copies; the live inbox files are in `xc\`). |
| `project\tools\` | Sound tools: earshot (lets an AI "listen" to audio), Clipwing real-SFX finder, Openverse search script. |
| `project\skills\` | Claude skills Sam installed (Instagram, marketing, Remotion). Readable as plain instructions. |
| `blends\` | Blender scene files that were already on the Asus (rider, Stalker rig, trike, walker, Sam wake-up scene). Copied, the originals stay where they were. |

---

## Hero vehicles

| Asset | Path | Status |
|---|---|---|
| **Night Terror** (Sam's armoured fastback, the hero car) | `originals_from_sam\Night_Terror_Fastback_v2.glb` | Sam's original. Draco + WebP compressed. Blender 5.0.1 imports it. If an importer fails on Draco, decode with `project\reels\pipeline\undraco.py` (needs `pip install DracoPy`). About 7 m long, length along Y, front at -Y, Z up. Hide `* hull` meshes in Cycles (they are real-time outlines). Headlights at world nose y about -5.4 when the car root is at (.4,-2). |
| IVORY trike, Sam's original | `originals_from_sam\IVORY_trike_original.glb` | Sam's original (17.9 MB, no Draco). Front = -X. |
| IVORY trike v2 (Dead Roads refit, twin MGs) | `project\reels\series\models\trike\ivory-dead-roads-trike-v2.glb` | **Current.** Mud tyres, LED pods, weathering, twin heavy MGs. Front wheel (-3.32,0,.94) R.94, rear wheels (1.85,±2.084,1.0) R1.0, MG muzzles about (-4.6,±.76,1.36), seat about (0.4,0,1.3). Sources in `trike\src\`. |
| Bandit military buggy | `project\reels\series\models\bandit-military\bandit-military-v1.glb` | Camo army refit of Sam's Bandit buggy. Not used in an episode yet. Sources in `bandit-military\src\`. |

## Creatures (all in `project\reels\series\models\`)

| Creature | File | Status / notes |
|---|---|---|
| **Stalker** (deer skull, burnt antlers, Sam's favourite) | `stalker-v2.glb`; rigged scene `blends\stalker_rig.blend` | **Current, loved.** Sam rejected v1 as "earthworm"; avoid ringed or banded shapes. Sheet `progress\stalker-v2-sheet.png`. |
| Husk (grey rotting skeletal, open ribs, long hooked fingers) | `husk-v2.glb` | Current. Matches Sam's first reference. |
| Screamer | `screamer-v1.glb` | Current. Its scream is approved, keep that take. |
| Brute | `brute-v1.glb` | Sam said it looks like a "potato". Needs a scarier redesign before reuse. |
| Crawler | `crawler-v1.glb` | Sam disliked its sound and the "sinking into the ground" look. Use sparingly. |
| Runner | `runner-v2.glb` | Current. |
| Walker | `walker-wip.glb`; rigged `blends\walker.blend` | Usable. The Ep2 plan wants gaunt realistic zombies: grey-yellow mottled skin, black veins, milky eyes, torn dark wet clothes. |

## Humans

| Character | File | Status / notes |
|---|---|---|
| Rider (white bob, goggles, tan bomber jacket, bandolier) | `project\reels\series\models\rider\rider-v3.2.glb` if present, else latest `rider-v3*`; rigged `blends\rider.blend` | Current best. Sources `models\rider\`. |
| Sam (the creator, as the hero) | `blends\wakeup\sam.blend` (Ep1 v6 build); old `project\reels\series\models\sam.glb` | Sam's look: South Asian man, late 20s, 6 ft, LEAN ectomorph (not bodybuilder), long wavy black hair (not thick), centre part, red rectangular glasses always on, light stubble, always a loose black hoodie and baggy jeans. The MakeHuman slider build was rejected ("terrible"); keep his face in shadow or at a distance until a better build exists. |
| Friends 1–3 (placeholders) | `f1.glb`, `f2.glb`, `f3.glb` | Placeholders only. Names and looks unknown. |

## Sets, textures, plates

| Asset | Path | Notes |
|---|---|---|
| Ep2 street set (CC0 scanned) | `xc\dead-roads-ep2\assets\cc0\` (left in place, used by `sc\ep2.py`) | Poly Haven / ambientCG: asphalt, wet roads, brick, concrete barrier, covered car, hydrant, lamps, trash, night HDRI. Credits in `SOURCES.md`. |
| NYC night plate | `project\reels\series\ep1\v6\plates\nyc_esb_north.png` | Real Midtown photo, CC BY 3.0 (Wikimedia/panoramio). Credit it. |
| Ep1 city kit | `project\reels\series\ep1\city.py` | Procedural city. Reads CG in close-ups, so prefer scanned assets. |

## Music and sound

| Asset | Path | Notes |
|---|---|---|
| Locked score reference v5 | `project\reels\series\ep1\flow\night-terror-score-v5-reference.mp3`, `project\reels\series\ep1\music-v5.mp4` | Sam LOVED this sound: orchestra + original 80s synth (Stranger Things mood, never its melody) + real recorded electric guitar doubled by bass, tuned Steinway opening. |
| Flow Music prompt | `project\reels\series\ep1\flow\flow-music-prompt.md`, `project\reels\series\shootout\flow\` | Google Flow Music (flowmusic.app) is the source for score and designed SFX. Sam signs in himself. |
| Ep2 audio | `project\reels\series\shootout\audio\`, `the-43rd-round-v1-credits.md` | CC-BY SFX need their credits kept. |
| Rejected music (do NOT reuse) | `music-sketch-B/C/D.mp4`, `music-sketch-v2-synth-guitar.mp4` | AI-generated and synthetic guitar. Sam hated these. |
| Sound tools | `project\tools\SOUND-TOOLS.md` | earshot, Clipwing, Openverse. |

## Storyboards and plans

| Episode | Path | Live link |
|---|---|---|
| Ep1 v6 (wake-up in NYC) | `project\reels\series\ep1\v6\storyboard.html` | https://claude.ai/artifact/2moCfd5GjpBkaXh3mufQDp |
| Ep2 "The 43rd Round" | `project\reels\series\shootout\v2\episode2-storyboard.html` | https://claude.ai/artifact/B1Em86ZACWEYtq3JR7GGQZ |
| **Ep3 "Tunnel Vision"** | `project\reels\series\ep3\episode3-storyboard.html` (also `xc\dead-roads-ep3\EP3_STORYBOARD.html`) | https://claude.ai/artifact/JYAypPuniitLaG7EhGbGcY |
| Camera moves Sam loves | `project\reels\series\shootout\v2\camera-moves.md` | |
| Lessons log | `project\reels\LESSONS.md` | |
| Repos tested | `project\reels\REPOS.md` | |

## Finished and draft videos (for reference, not to reuse as footage)

- Ep1: `project\reels\series\ep1\night-terror-ep1-v5.mp4` (best before v6; Sam loved the garage and the Screamer), v3/v4 older.
- Ep2 v1: `project\reels\series\shootout\the-43rd-round-v1.mp4` (rejected except the final leap).
- Ep2 v2 previews: `project\reels\series\shootout\v2\ep2-preview-*.mp4`.
- Wake-up v1: `project\reels\series\ep1\v6\renders\wakeup_v1.mp4`.
- Posters: `project\reels\series\ep1\poster\` (Sam prefers the Stalker one).

---

## Log of additions
- 2026-11-21 Claude: folder created; full project mirror, Sam's originals, Asus blends.

- 2026-11-21 18:20 IST Codex: Episode 3 source snapshot `ep3\build-v006`; research, adapted shot plan, scripts, credits, cue sheet and audit.
- 2026-11-21 18:20 IST Codex: `ep3/v001/assets/` contains versioned original-buggy import, optimized assemblies, GLB-derived trike wreck, Husk/Runner/Screamer rigs, and licensed Khronos car sources/prepared props; source originals unchanged.
- 2026-11-21 18:20 IST Codex: `ep3/v001/references/camera-shakify/` contains official CC0 recorded shake data, license and download hashes. Internal pose photo references remain in the Ep3 working folder and are not publication assets.

- 2026-11-21 Codex: generated/downloaded Episode 3 first score source in `ep3/v001/audio/ep3-flow-score-source-v001.wav`; adjacent JSON records provenance, hash and measurements. Not approved or conformed final mix.

- 2026-11-22 17:07 IST Codex: [5 O'CLOCK shared research handoff](anime-5oclock/research-v1/REEL_RESEARCH.md) with Instagram comments and metrics, Japanese and cross-platform references, both original reel studies, and 14 reference stills.

- 2026-11-22 Codex added the [5 O'CLOCK chime reply concept frame](anime-5oclock/concepts/5oclock-chime-reply-v2.png), an ImageGen study for a hand-drawn reel. The alternate town appears in a convex traffic mirror.

- 2026-11-22 Codex: [5 O'CLOCK The Reply](anime-5oclock/reel-v1/5oclock-the-reply.mp4), 15-second vertical 2D reel with an original stereo chime, mirror composite, and editable render source.

- 2026-11-22 Codex: [5 O'CLOCK The Reply v2](anime-5oclock/reel-v2/5oclock-the-reply-v2.mp4), continuous 15-second 2D cel-rig shot with animated character acting and layered reflection. [Editable source notes](anime-5oclock/reel-v2/README.md).

- 2026-11-22 Codex shared [The Fourth Note approval site](anime-5oclock/episode-01-pitch/index.html). Includes the new Sam and bell creature designs, action beats, and an original 15-second stereo score. Awaiting creative approval. Earlier passes relied on a plate or a cel rig; for this shot, animate the heel slip, finger grip, wet cuff lag, and collar vibration as separate physical actions. The costume sheet has longer hair than the action frame; use the sheet as the model for final animation. No new audience or retention metrics were verified in this pass.
2026-11-22 — [The Fourth Note, finished reel](anime-5oclock/the-fourth-note/5oclock-the-fourth-note.mp4). Approved pitch rendered with three sets of AI-generated character and creature poses, motion interpolation, rain, and original stereo score. Source art and renderer are beside the export under source/.
