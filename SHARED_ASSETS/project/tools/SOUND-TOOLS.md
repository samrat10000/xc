# Sound tools (installed 2026-11-20 for Sam)

## 1. earshot (Leonxlnx/earshot, MIT): "ears" for Claude
Turns audio into evidence: describe, match a text description, rank a folder, find the best trim, realness
(real recording vs code-synthesized), timeline/sheet/critique of a whole mp4's soundtrack incl. sync to cuts.
Install in a fresh cloud container (~10 min, ~3 GB with torch + 1.1 GB models):
  git clone --depth 1 https://github.com/Leonxlnx/earshot ~/earshot   (or untar earshot-src.tgz here)
  cd ~/earshot && python3 -m venv .venv
  .venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu   # host now allowed; smaller
  .venv/bin/pip install -e ".[mcp]" && .venv/bin/python -m earshot doctor --fetch
Use: .venv/bin/python -m earshot describe|match|rank|find|realness|timeline|sheet|critique ...
For many calls use one script: `from earshot import api` (models load once, ~30 s). Read skills/earshot/SKILL.md.
Run with `nice` and EARSHOT_THREADS=2 while Blender renders.

## 2. Clipwing real-sfx (Clipwing/skills): places REAL recorded SFX on picture beats from a cue list
Needs a local sound library (config.json). Useful scripts: look.py (frames+audio), find_moments.py, mix.py, critique.py.
Source in clipwing-real-sfx-src.tgz; read skills/real-sfx/SKILL.md.

## 3. Openverse (WordPress/openverse): free CC sound search API (mostly Freesound)
No install needed: api.openverse.org (needs a browser-like User-Agent, else 403). openverse_fetch.py here
downloads top CC0/CC-BY hits per query. Keep licence + creator for credits (CC-BY needs attribution).
Cloud hosts allowed in the Default environment: api.openverse.org, freesound.org, cdn.freesound.org,
upload.wikimedia.org, download.pytorch.org.

Rule: never say how audio sounds without an earshot reading behind it.
