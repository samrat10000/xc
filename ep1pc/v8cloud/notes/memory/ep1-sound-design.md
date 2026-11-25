---
name: ep1-sound-design
description: Night Terror Ep1 SFX pipeline (AudioLDM2 clips, CLAP judge, physical V8, focus-mix) and Sam's realism demands
metadata:
  type: project
---

Sam (2026-11-19 10:09 PM IST): old SFX (car, rain, steps, skid) were bad and unreal; engine sounded like an EV; wants a grumbling 3-4 L V8 and "crazy realism".
Pipeline (session scratch music/): sfx_gen.py = AudioLDM2 (HF cvssp/audioldm2, 16 kHz; needs GPT2Model GenerationMixin patch), jobs1.json prompts, ~20-50 s per clip on CPU. clapscore.py/clapq.py = LAION CLAP (HF laion/clap-htsat-unfused) as the "ears": ranks takes, checks each mix section reads as intended. v8.py = crossplane V8 physical model (great at high rpm, CLAP .91-.99; reads as noise at idle/start, so use the AI engine_start clip there). sfxmix.py = buses + per-section music/amb automation ("focus mixing") + own lookahead limiter (pedalboard Limiter adds makeup gain, avoid it). edit3.py = picture re-cut on the music clock with frame-blend slow-mo.
Delivered sound-sample-v1.mp4 (first 21 s) 2026-11-19 10:25 PM IST; awaiting feedback. See [[ep1-music-pipeline]].
Sam on sample v1 (10:35 PM IST): scream PERFECT (keep its level; sfxmix anchors SFX RMS = music-3 dB in the 8-10.6 s scream window); 0.5 s runner insert at 13 s felt misplaced (never use sub-1 s inserts; use whip-blur transitions, edit3.WHIPS); crawler entrance sound "pathetic"; engine good but must sync with picture. v2: crawler sounds on hand plants (crawl period 1.6 s -> plants every .8 s from +.4 s), synthesized claw foley (foley.py) layered on AI takes, nothing may overlap into the scream (vox compressor ducks it), exhaust pop on the upshift hurt realism (removed). Sent sound-sample-v2.mp4 10:55 PM IST.

- 2026-11-20: Full Ep1 v3 delivered (night-terror-ep1-v3.mp4, 45.5 s). CLAP with a "monster screaming" label swallows any screech: use neutral labels ("car tires screeching|animal|music") when checking skids. AI skid/click takes were weak; foley.skid() and foley.chitter() (synth) replace them. Scream window verified identical to approved sample v2.
