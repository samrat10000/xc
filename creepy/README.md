# `creepy` — Short-Form Horror & Dark Surreal Reels Project

Workspace inside `c:\Users\cross\Downloads\xc\creepy` dedicated to analyzing and producing high-retention **8–12s creepy/uncanny short-form reels** (`1080×1920`, 9:16 vertical).

## Quick Links

- **[ANALYSIS.md](ANALYSIS.md)** — Deep deconstruction of both reference reels (`DeeVNnAu_C0` & `DZC5NnpIwXe`), viral mechanics, and production blueprint.
- **[Episode 2: "Nobody Ever Leaves" (`ep02_nobody_leaves`)](ep02_nobody_leaves/STATE.md)**: *(10x PSX 3D upgrade of Reel 1)*
  - **v2 Archival Master (CRF 14):** [ep02_nobody_leaves_v2.mp4](ep02_nobody_leaves/out/ep02_nobody_leaves_v2.mp4) (`14.0 MB`, `1080×1920`, `24 fps`, `12.000 s`)
  - **v2 Shareable / IG-Ready (CRF 20):** [ep02_nobody_leaves_v2_share.mp4](ep02_nobody_leaves/out/ep02_nobody_leaves_v2_share.mp4) (`6.3 MB`, `1080×1920`, `24 fps`, `12.000 s`)
  - **v2 QA Contact Sheet:** [contact.jpg](ep02_nobody_leaves/qa/final_v2/contact.jpg)
  - **v1 Archival Master (CRF 14):** [ep02_nobody_leaves_v1.mp4](ep02_nobody_leaves/out/ep02_nobody_leaves_v1.mp4) (`14.0 MB`, `1080×1920`, `24 fps`, `12.000 s`)
  - **v1 Shareable / IG-Ready (CRF 20):** [ep02_nobody_leaves_v1_share.mp4](ep02_nobody_leaves/out/ep02_nobody_leaves_v1_share.mp4) (`6.7 MB`, `1080×1920`, `24 fps`, `12.000 s`)
  - **v1 QA Contact Sheet:** [contact.jpg](ep02_nobody_leaves/qa/final_v1/contact.jpg)
- **[Episode 1: "Borrowed Time" (`ep01_borrowed_time`)](ep01_borrowed_time/STATE.md)**:
  - **v2 Archival Master (CRF 14):** [ep01_borrowed_time_v2.mp4](ep01_borrowed_time/out/ep01_borrowed_time_v2.mp4) (`61.5 MB`, `1080×1920`, `24 fps`, `9.000 s` seamless loop)
  - **v2 Shareable / IG-Ready (CRF 20):** [ep01_borrowed_time_v2_share.mp4](ep01_borrowed_time/out/ep01_borrowed_time_v2_share.mp4) (`4.3 MB`, `1080×1920`, `24 fps`, `9.000 s` seamless loop)
  - **v2 QA Contact Sheet:** [contact.jpg](ep01_borrowed_time/qa/final_v2/contact.jpg)
  - **v1 Archival Master (CRF 14):** [ep01_borrowed_time_v1.mp4](ep01_borrowed_time/out/ep01_borrowed_time_v1.mp4) (`88.9 MB`, `1080×1920`, `24 fps`, `9.000 s` seamless loop)
  - **v1 Shareable / IG-Ready (CRF 20):** [ep01_borrowed_time_v1_share.mp4](ep01_borrowed_time/out/ep01_borrowed_time_v1_share.mp4) (`10.6 MB`, `1080×1920`, `24 fps`, `9.000 s` seamless loop)
  - **v1 QA Contact Sheet:** [contact.jpg](ep01_borrowed_time/qa/final_v1/contact.jpg)

## Directory Structure

```text
creepy/
├── README.md
├── ANALYSIS.md
├── ep02_nobody_leaves/                    # Episode 2 ("Nobody Ever Leaves" — 10x PSX 3D upgrade of Reel 1)
│   ├── STATE.md, QA_LOG.md
│   ├── src/                               # paint_psx_textures.py, build_scene.py, comp_psx.py, make_audio.py
│   ├── assets/                            # 7 grungy Closest PSX textures + typewriter_events.json
│   ├── renders/                           # probe_v1/v2 (270x480 -> 1080x1920), full_v1/v2_raw, full_v1/v2_comp
│   ├── qa/                                # Contact sheets, pixel stats, crops
│   └── out/                               # ep02_nobody_leaves_v1/v2.mp4 + _share.mp4 + audio masters
├── ep01_borrowed_time/                    # Episode 1 ("Borrowed Time" — 10x upgrade of Reel 2)
│   ├── STATE.md, brief.md, SHOT_RULES.md, QA_LOG.md
│   ├── src/                               # paint_textures.py, build_scene.py, comp_reel.py, make_audio.py
│   ├── assets/                            # Charcoal wall, wood floor, crimson clock, 11 word-clock dials
│   ├── renders/                           # probe_v1, probe_v1b, probe_v2, full_v1_raw, full_v1_comp
│   ├── qa/                                # Contact sheets, pixel stats, full-size crops
│   └── out/                               # ep01_borrowed_time_v1.mp4 + _share.mp4 + audio master
├── scripts/                               # Reference IG scraper & processor
└── references/                            # Captured reference reels (DeeVNnAu_C0 & DZC5NnpIwXe)
```
