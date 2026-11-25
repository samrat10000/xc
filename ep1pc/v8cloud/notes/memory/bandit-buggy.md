---
name: bandit-buggy
description: Second car "Bandit" armored buggy, military refit (2026-11-19) - where files live, what was changed, how to rebuild
metadata:
  type: project
  modified: 2026-11-19T11:41:24.057Z
---

Sam sent bandit-armored-buggy.glb (Draco+WebP, 9 MB, front = -X, root scale .55, wheels at x±1.5135 y±.8525 z.5995 r.558). Sam called the teal/orange paint childish; asked for an army-vehicle look.
Refit v1 (2026-11-19): /mnt/project-files/reels/series/models/bandit-military/bandit-military-v1.glb (5.1 MB Draco). Scripts in bandit-military/src: skull_sdf.py (numpy SDF cow skull -> marching cubes, vertex colours), textures.py (woodland camo with a 4x4 UV tile set by a Mapping node, olive panels, stencil decals, skull emblem from the skull depth map), build.py (all mesh work), export.py, render.py.
Changes: woodland camo, stencils (B-07, BANDIT, kill tallies), NDT military tyres + beadlock rims + CTIS, .50 belt from an open ammo can, spent links and brass, tread-plate floor + perforated mesh plates, radio and extinguisher, new skull with a snapped horn, barbed wire and rags, rally wing replaced by a rack with jerry cans, lamp guards, bolt rows.
Pipeline: undraco.py -> bpy import -> build.py -> export WEBP -> npx gltf-transform draco (in scratch gt/). Viewer copy: gltf-transform quantize + resize 1024, base64 .txt.
Viewer: https://claude.ai/artifact/KmYWSfMqREyQ4WhSQhqDio. Hero car = [[zombie-series]] Night Terror.
