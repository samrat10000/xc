# Changelog for Claude Desktop

## 2026-11-24 · Established the independent Episode 2 production

- Copied the earlier Episode 2 shot sources, finished renders, and probe evidence into shots/. An earlier render queue targeting the shared workspace was stopped before the new queue began.
- Copied Episode 1’s error catalog and reference story. The new street passes load the approved Sam and cast_v2 Blender files from the Episode 2 copy.
- Put the episode story, timing and dialogue in story/. The active render runner and shared scene files are under shots/production/.
- Put the ElevenLabs script, named takes, sample credits and recorded audio inputs in audio/. The mixer uses the named takes when present.
- STATE.md lists the current shot versions. PRODUCTION_LOG.md records the review decisions, and ERROR_CATALOG.md carries the generalized checks.

A shared one-screen project status file now sits beside the two episode folders. Use it for one-line milestones, GPU priority and genuine blockers. Keep shot-level evidence in each episode’s own log.

The silent cut, scored MP4, stereo WAV and delivery index are ready in episode/. All 15 cue boundaries survived the audio remux. Audio and project state are also summarized in the shared status file in the xc parent.

Episode 2 dialogue master v5 is ready in episode/. The audio folder holds the eight ElevenLabs cues and hum, the two edited takes, and an exact export transcript comparison.

## 2026-11-24 · Episode 2 v6 revision

- Revised acting, framing and continuity in 11 shot masters. The retained versions, probe frames and critiques are under shots/ by name.
- Added frame-checked editing and final-mix scripts under audio/. The corrected shared theme assets live in audio/series_theme_v6/. The edit reuses the canonical Listener plate in the cold open and at the third chime.
- The precise v6 cut, cue times and master verifications live in episode/v6/. V6_REVISION.md describes the cut and mix decisions. MOTION2D_QA_LEARNINGS.md records the reusable checks and token-saving review workflow.
