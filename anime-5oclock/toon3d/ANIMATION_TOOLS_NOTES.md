# Animation tools research (partial, 2026-11-22)

Constraint: this PC has an RTX 3050 Laptop with 4 GB VRAM. Most open AI video models need 12 GB+.

## Route A: 3D toon in Blender (what toon3d/ uses; runs on this PC)
- VRoid Studio + VRM Add-on + Blender EEVEE toon shading. Already installed and working.
- Granite Waves-style motion (long holds, small moves, animated on twos) can be keyed in Blender.
- Motion sources: hand keys and IK in Blender; FreeMoCap (open source, video to BVH); BlendArMocap (MediaPipe in Blender);
  Rokoko Video (free, needs a free account); Mixamo (needs an Adobe account); Cascadeur (AI auto-posing, but FBX export needs paid Indie, about $8/month).
- Reference: Dillon Goo Studios / Goo Engine (custom Blender build for anime), Blender Studio "Toon Character Workflow" and "Wing It!" NPR.
  https://studio.blender.org/training/toon-character-workflow/ , https://gamefromscratch.com/goo-engine-blender-for-anime/
- Lip sync: VRM face shape keys (A/I/U/E/O) can be keyed, and Rhubarb Lip Sync can generate the timing from audio (not yet verified here).

## Route B: 2D hand-drawn / puppet (needs a human artist)
- Clip Studio Paint EX (about $219 one-time), OpenToonz (free, descended from the Toonz software Ghibli used), Krita, Toon Boom Harmony (studio price).
- Puppet rigs: Live2D Cubism (free tier), Inochi2D / Inochi Creator (open source, BSD-2).

## Route C: AI anime video (needs a rented cloud GPU, or a paid hosted service)
- Wan 2.2 / 2.7 (Apache 2.0, open weights). Wan2.2-Animate-14B GGUF needs about 12 GB VRAM. https://huggingface.co/QuantStack/Wan2.2-Animate-14B-GGUF
- Bilibili Index-AniSora (anime-specific, has a 12 GB version of V3.1). https://github.com/bilibili/Index-anisora
- ToonComposer (TencentARC, ICLR 2026): in-betweening plus colour from keyframes and sketches, built on Wan2.1 14B. https://github.com/TencentARC/ToonComposer
- AniDoc (CVPR 2025): line-art colourisation. ToonCrafter: cartoon in-betweening (flicker reported).
- Hosted: Kling, Runway, Luma (accounts and payment).
- Risk: viewers on the reference reels reacted strongly to anything they suspected was AI, and Sam wants nothing AI-sounding.

## Claude plugin catalog
- "animation-studio" (code-drawn frames), "Anime Story Video Maker" (ManyMotions, remote AI, needs an account), "Sticklore" (stick figures, not useful).
  None replaces a proper character pipeline.
