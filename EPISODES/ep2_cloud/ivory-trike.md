---
name: ivory-trike
description: Third vehicle "IVORY" reverse trike / dune buggy rebuild (2026-11-20) - files, coordinates, pipeline
metadata:
  type: project
  modified: 2026-11-20T11:00:17.524Z
---

Sam sent ivory-orange-trike.glb (17.9 MB, no Draco, flat 1024 textures, slick tyres). Front = -X; front wheel (-2.52,0,.94) R.94 hw.45 rim r.69; rear wheels (1.85,±2.084,1.0) R1.0 hw.59 rim r.733.
v1 (2026-11-20): /mnt/project-files/reels/series/models/trike/ivory-dead-roads-trike-v1.glb (6.4 MB Draco, 639k tris). Scripts in trike/src: build_a.py (removes slick tyres, builds mud-terrain knobby tyres with "DEAD ROADS M/T" sidewall text, front LED pods, roof light bar on the orange crown, tail lamps, jerry can rack + straps), build_b.py (welds, joint smart-UV atlas per material, Cycles EMIT bake of procedural weathering: chips, scratches, streaks, AO grime, mud from below; ivory+orange 4K, gunmetal 2K; ~23 min), build_c.py (crease ink tubes + inverted hulls), export.py, render.py (hull/ink ray-vis off).
Pipeline: build_a -> build_b -> build_c -> export (WEBP) -> npx gltf-transform draco (scratch gt/). v2 (2026-11-20 5:35 PM IST, Sam asked): body stretched (STRETCH=.8 m piecewise X between x-1.55..-.45, front wheel now x=-3.32) + twin heavy MGs on the front fork ends (src/guns.py, exec'd by build_a), gun + ammo-can materials baked too. ivory-dead-roads-trike-v2.glb 7.4 MB. Run src/chain.sh for b->c->export->draco->renders. Rider + shootout reel live in thread 'Write dune buggy zombie shootout reel'. Awaiting Sam's review. Related: [[bandit-buggy]], [[zombie-series]].
