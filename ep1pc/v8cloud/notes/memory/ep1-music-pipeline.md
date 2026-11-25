---
name: ep1-music-pipeline
description: How Night Terror music/SFX are made now (VSCO-2 orchestra sampler, ACE-Step, HF access) and Sam's source choice
metadata:
  type: project
---

Sam chose (2026-11-19) "Free AI models + real orchestra" for music/SFX. Network: huggingface.co (+cdn-lfs, xethub hosts) added to the Default environment allowlist; github.com git clone works (web/API don't), pypi works; freesound/pixabay/elevenlabs blocked.
Score = VSCO-2 CE (CC0) samples cloned via git (SFZ branch, sparse) + small SFZ sampler (music/sampler.py) + score.py (90 BPM D minor, hit map, pedalboard mix, master automation, loudest 3 s at -9 LUFS). Session scratch music/ (venv py3.12 with torch CPU, pedalboard, pyloudnorm). Animatic: music/animatic.py -> /mnt/project-files/reels/series/ep1/music-sketch-v1.mp4 (sent 2026-11-19 9:00 PM IST, awaiting feedback).
Plan: ACE-Step 1.5 turbo (HF ACE-Step/Ace-Step1.5, no GPU) for texture bed; AudioLDM2 or AudioGen for SFX; then re-cut picture to the music hits. Stable Audio Open is gated (needs HF token). See [[zombie-ep1-status]].

ACE-Step on CPU works: ace_run.py (music/), text mode ~3.5 min, cover mode (src_audio=score, strength .3-.5) ~5 min; must patch VAE decode chunk=48 and encode chunk=4 s or it OOMs (15 GB RAM). Cover does NOT keep the score's hit timing. Hosts also needed: us.aws.cdn.hf.co. Versions A (orchestral, hit-locked), B (AI text), C/D (AI cover 50/30%) sent 2026-11-19 9:40 PM IST as ep1/music-sketch-{v1,B,C,D}.mp4; awaiting Sam's pick.

Sam feedback 2026-11-19 9:41 PM IST: AI versions B/C/D were trash (don't match the story) - never deliver raw ACE-Step tracks again. Version A (hand-written orchestral score) was good but lacking. He wants electric guitar added/converted, and a Stranger Things-like vibe (pulsing 80s analog synth arps, crazy beats). Keep originals: same feel, never copy the ST theme melody.
v2 hybrid (score2.py = score.py + part2.py layer; synth.py = numba ladder synth, gated drums, Karplus-Strong guitar + amp) sent 2026-11-19 9:45 PM IST as ep1/music-sketch-v2-synth-guitar.mp4.
Sam 2026-11-19 9:46 PM IST: v2 Karplus-Strong guitar 'irritates the ears' -> v3 uses REAL guitar samples: Karoryfer Shinyguitar (CC0, git clone sfzinstruments/karoryfer.shinyguitar into music/shiny), 4x-oversampled tube-style clip + steep cab lowpass (synth.py guitar()). Never use synthesized guitar again. v3 sent as ep1/music-sketch-v3-real-guitar.mp4. Sam won't move on until the music is finalized.
Sam 9:51 PM: v3 'more promising'; start slightly off-tune, guitar needs more bass; ENDING (Stalker lunge -> theme over black) is perfect, keep it. v5: Splendid Grand Piano (sfzinstruments, PD) replaces honky VSCO upright, sampler autotune (cents_off), synth detune .04-.05, bass-guitar layer under power chords. Sent ep1/music-v5.mp4 9:55 PM IST.

2026-11-20: Sam switched music (and wants SFX) to Google Flow Music (flowmusic.app), driven in Sam's Chrome via the Claude extension (signed in with Google by Sam). Flow track "Punchier Horror-Action Score" (45.1 s) hit our timeline from a text prompt; Ep1 re-mixed on it: ep1/night-terror-ep1-v3-flow.mp4. Flow downloads land on Sam's PC (data: URL), so Sam must upload them to the chat. Can't upload audio into Flow via the extension (screenshots only). Prompt file: ep1/flow/flow-music-prompt.md.
