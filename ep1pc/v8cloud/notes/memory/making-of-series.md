---
name: making-of-series
description: Sam's Instagram making-of series for Night Terror, narrated by a clone of Sam's own voice; doc, repo pick, status
metadata:
  type: project
  modified: 2026-11-20T08:11:12.988Z
---

2026-11-20: Sam wants every step of making [[zombie-series]] posted on Insta as behind-the-scenes reels, narrated in Sam's OWN cloned voice (Sam's consent, Sam's voice only).
Doc (plan, 10-post list, scripts in Sam's casual voice, repo comparison): https://claude.ai/artifact/G4rjoxGM7DQoFWzGwxRCdV
Voice repo pick: test VoxCPM (42.7k stars, Apache-2.0 weights) and Chatterbox (28k, MIT, multilingual incl. Hindi) on Sam's sample; GPT-SoVITS (64k, MIT) fallback. Skip F5-TTS (weights CC-BY-NC) and Fish Speech (non-commercial model licence).
Status: asked Sam for a 60-90 s clean voice sample + language (English/Hindi/Hinglish). Next: test narration of script 1 with both models.
Sam picked Chatterbox (MIT) 2026-11-20. Voice booth page for Sam's sample: https://claude.ai/artifact/3Jras4QFNYAsc7jQj36eU5 (assets capability; sample lands in its asset store, list with Artifact scope "assets"; mic API is blocked in artifacts so it uses the phone's file-capture recorder).
2026-11-20 2:50 PM IST: Sam's sample (100 s English, quiet + low rumble, ~10 dB SNR) -> ref.wav = first 18 s, highpass+afftdn+dynaudnorm. Chatterbox CPU venv (py3.11, needs setuptools<80 for perth watermarker), ~25 s per line. best.py = 3 takes/line, Whisper-small picks closest to text (spell times as words). Sent reels/making-of/post1-voice-test-chatterbox.mp3 + voice-compare-real-then-clone.mp3; awaiting Sam's verdict.
Sam on v1 clone (2:52 PM IST): not like him: too fluent, monotone/sing-song low-high pattern, no natural essence. v2: script rewritten with Sam's fillers/repeats (s1n.txt), generated as 4 long chunks (nat.py, exag .45 cfg .3 temp .9), two refs (A = 0-11 s, B = 49-60 s). Sent post1-voice-v2-A/B.mp3. VoxCPM1.5 is unusable on CPU (~9 s/step, ~40 min per line; also needs load_denoiser=False since modelscope.cn is blocked). Next if still off: GPT-SoVITS fine-tune on Sam's sample.
Sam rated v2 3/10 (3:30 PM IST). Now fine-tuning GPT-SoVITS v2 on CPU: scratch voice/gsv (venv gsvenv py3.10, torch 2.6, gradio 4.44.1; NLTK needs NLTK_ALLOW_PROXIED_URLOPEN=1), dataset ds/ = 13 clips from Sam's sample, train.sh (s2 8 epochs ~7 min each, then s1 15 epochs).
v3 (GPT-SoVITS fine-tune, GPT e15 + SoVITS e4, best_gsv.py best of 5/line, cut0, top_k 5, temp .6) sent 4:40 PM IST as post1-voice-v3-trained.mp3. Mumbles names (Night Terror, 3:12) because only 90 s of quiet audio; needs 3-5 min clean recording. Gotchas: env TEMP clashes (use GTEMP), need jieba_fast shim + resampy, logs/sam/logs_s2_v2 must exist, don't run inference while training (OOM kill).
Correction: v3 trained take failed (half speed, slurred, Whisper can't read it even at atempo 1.8). Told Sam; asked for 3-5 min clean audio to retrain. Chatterbox v2 remains best so far (Sam: 3/10).
2026-11-20 8:38 PM IST: Sam sent 2nd sample (215 s, ~17 dB SNR, much better). ds2/ = 38 clips (290 s, new+old). Retraining exp sam2 via gsv/pipe2.sh (prep -> s1 15 ep -> s2 8 ep; status in pipe2.status).
9:45 PM IST: GPT-SoVITS sam2 retrain (5 min data) still broken: GPT outputs empty/garbled takes, even base GPT drags 3-4x long; pipeline bug suspected, parked. Sent Chatterbox v4 with new cleaner ref2.wav (ds2 c018+c019, 14.5 s): post1-voice-v4.mp3 (best2.py, per-line, all words right), post1-voice-v4-flowing.mp3 (4 long chunks, some word errors), voice-compare-v4.mp3.
