---
name: sound-tools
description: earshot (listen to audio), Clipwing real-sfx, Openverse CC sound search - where they live, how to install/call them in any thread
metadata:
  type: reference
  modified: 2026-11-20T17:59:44.837Z
---

Sam (2026-11-20) asked that every thread use these sound tools, especially earshot, which lets Claude "listen".
How-to + sources: /mnt/project-files/tools/SOUND-TOOLS.md (earshot-src.tgz, clipwing-real-sfx-src.tgz, openverse_fetch.py).
- earshot: venv install about 10 min plus 1.1 GB of models. Commands: describe, match, rank, find, realness, timeline, sheet, critique (mp4 soundtrack review, sync to cuts). Rule: never claim how audio sounds without an earshot reading.
- Openverse API: api.openverse.org needs a browser User-Agent. Results are mostly Freesound CC0/CC-BY; keep credits.
- The cloud Default environment now allows api.openverse.org, freesound.org, cdn.freesound.org, upload.wikimedia.org, download.pytorch.org. Sam approved this on 2026-11-20.
- Prefer REAL recorded SFX (Sam hates synthetic sound). Flow Music is still the source for score and designed SFX.
Related: [[shootout-reel]], [[reel-pipeline]].
