# Episode 3 production research

Checked 2026-11-21. Sources below are official projects, vendor pages, or Blender documentation. "Tested" means executed here for Episode 3, unless explicitly marked as an earlier project test. A source review is not a runtime test. No downloads, installations, paid purchases, or account sign-ins are implied by this report.

## Direction

Keep Blender 5.0.1, the original Night Terror vehicle, the approved Stalker rig, and the existing scanned PBR library. Build and review all 19 shots at quarter resolution before final rendering. Character contact, vehicle damage, the tunnel clearance collision, and the synchronized head turn need dedicated tests. A finished-looking still does not establish animation quality.

## Motion and retargeting

| Project | Purpose and source | License / access | Tested | Verdict |
|---|---|---|---|---|
| MediaPipe | [Official repo](https://github.com/google-ai-edge/mediapipe), CPU landmark extraction | Apache-2.0 code; check individual model terms | Earlier project test documented in `mocap-test/RESULT.md`; no new Ep3 test yet | Keep local pipeline; confidence-aware smoothing, identity continuity and foot contacts must be corrected before hero use. |
| PosePipe | [Official repo](https://github.com/SpectralVectors/PosePipe), Blender/OpenCV capture | Apache-2.0 | Source reviewed; existing local reimplementation previously tested | No need to pip-install into Blender. Reuse isolated environment. |
| GVHMR | [Repo](https://github.com/zju3dv/GVHMR), world-grounded reconstruction | [License](https://raw.githubusercontent.com/zju3dv/GVHMR/main/LICENSE) permits educational/research/nonprofit use; commercial use requires separate permission | No | Exclude from monetized production pending permission. Hardware suitability on 4 GB is also untested. |
| WHAM | [Repo](https://github.com/yohanshin/WHAM) | [MIT code](https://raw.githubusercontent.com/yohanshin/WHAM/main/LICENSE); SMPL, checkpoints and dependencies have separate terms | No | Possible research branch; not a production shortcut until model rights, setup and memory are checked. |
| 4DHumans | [Repo](https://github.com/shubham-goel/4D-Humans) | [MIT code](https://raw.githubusercontent.com/shubham-goel/4D-Humans/main/LICENSE.md); separate body-model/checkpoint dependencies | No | Reconstruction/tracking is not a ready-to-use contact animation. Defer heavyweight installation. |
| Mixamo | [Adobe FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html) | Free Adobe ID; FAQ permits royalty-free films including commercial use. Save local assets; do not redistribute raw library as a product. | No; Sam signs in | Best initial source for humanoid locomotion and reactions. Its biped auto-rigger does not solve a quadrupedal Stalker gallop. |
| Rokoko | [Official plans](https://www.rokoko.com/pricing), [free-mocap overview](https://www.youtube.com/watch?v=uDxZC5SEp0A) | Account; free/paid availability varies by clip and feature; confirm each downloaded pack's terms | No | Useful alternate mocap source. Do not assume all motion-library entries or export formats are free. |
| CMU mocap | [Official database](https://mocap.cs.cmu.edu/) | Official page timed out in this session; exact current usage conditions unverified | No | Candidate, not cleared or downloaded. Avoid replacing the source with an unverified repack. |
| Rigify | [Blender manual](https://docs.blender.org/manual/en/5.0/addons/rigging/rigify/index.html) | Blender GPL tools | No new Ep3 retarget test | Rig controls and IK are useful; Rigify alone is not a universal automatic retargeter. Map actual source/target rest poses. |
| Auto-Rig Pro | [Author's product page](https://superhivemarket.com/products/auto-rig-pro) | Paid software; confirm purchase/license/version before use | No | Remap supports retargeting. Do not purchase or rebuild established rigs without a demonstrated benefit. |

## Crowds, physics and effects

| Technique | Source | License / access | Tested | Verdict |
|---|---|---|---|---|
| Geometry Nodes / linked instances | [Blender instances](https://docs.blender.org/manual/en/5.0/modeling/geometry_nodes/instances.html) | Built into Blender | No new Ep3 render | Share geometry/materials; use several baked pose variants or time-sampled caches for crowd offsets. A random field does not automatically give each collection instance an independent armature evaluation time. Keep foreground actors as real rigs. |
| Crowd add-ons | [Blender Extensions](https://extensions.blender.org/) | Per extension; none selected or installed | No | Existing Blender instancing is sufficient for initial 30–60 background figures. An add-on must demonstrate Blender 5 compatibility before adoption. |
| Rigid-body constraints | [Manual](https://docs.blender.org/manual/en/5.0/physics/rigid_body/constraints/introduction.html) | Built in | No | Use simplified collision proxies and bake. Constrain the hero impact's timing; a random simulation must not miss the truck or tunnel lip. |
| Shape-key vehicle deformation | [Manual](https://docs.blender.org/manual/en/5.0/animation/shape_keys/introduction.html) | Built in; original mesh remains Sam's asset | No | Reversible nose/roof damage states; split moving panels deliberately. Keep front damage after the hit and roof holes after shot 13. |
| Cell Fracture | [Official extensions catalog](https://extensions.blender.org/add-ons/cell-fracture/) | See current extension license/version before installation | No | Suitable for concrete/glass shards using bounded proxies. Fractured rigid pieces are not elastic sheet metal. No installation yet. |
| Soft body | [Blender manual](https://docs.blender.org/manual/en/5.0/physics/soft_body/index.html) | Built in | No | Defer for the hero car; difficult to control and expensive relative to authored dents. |
| Mantaflow | [Fluid manual](https://docs.blender.org/manual/en/5.0/physics/fluid/index.html) | Built in | No | Physically interactive smoke is possible but baking and volume rendering need measured budgets. No full-street volume by default. |
| EmberGen stock VDBs | [Official free VDBs](https://jangafx.com/software/embergen/download/free-vdb-animations) | Page explicitly labels its free VDB simulations CC0 | Source reviewed, not downloaded/rendered | Good optional smoke source. Some archives are multiple GB; a baked VDB still costs volume render time. Test a tightly cropped small element only. |
| Real footage elements | [Freesound](https://freesound.org/), [Openverse](https://openverse.org/) for recorded sound; footage requires a separate source | CC0/CC-BY only after item-level verification; footage is not licensed merely because its sound is | No new pulls | Composite licensed steam/rain where depth and camera movement permit. Preserve occlusion, alpha and perspective; no unlicensed movie clips. |
| Rain / sparks | Existing Ep2 geometric streaks, ballistic sparks, real recorded rain | Project code plus item-level sound licenses | Existing Ep2 code inspected | Reuse bounded rain geometry and collision-timed sparks. Avoid unnecessary smoke volumes and glowing-line bullets. |

## Camera, assets and finishing

| Tool / source | What it does | License / access | Tested | Verdict |
|---|---|---|---|---|
| Camera Shakify | [Official repo](https://github.com/EatTheFuture/camera_shakify), [extension](https://extensions.blender.org/add-ons/camera-shakify/) | GPL-3 code; recorded shake data CC0. Release 0.5.1 includes a Blender 5.0 driver fix. | Not yet installed or baked | Use recorded handheld data after a short compatibility check. Bake cameras for reproducibility; keep intentional tracking separate from shake. |
| Lens / focus | [Blender camera](https://docs.blender.org/manual/en/5.0/render/cameras.html) | Built in | No new test | Small focus shifts and calibrated distortion; subtle breathing. Do not hide bad anatomy with blur. |
| VHS / camcorder | [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html) | FFmpeg build license varies with enabled components | Existing ffmpeg command available; no Ep3 filter test | Chroma softness/delay, slight distortion and bottom-edge switching noise. Restrict to shots 4, 13, 16. 4:3 picture inside 9:16; tiny REC overlay only. No authentic hardware LUT has been sourced; do not label a fabricated LUT as authentic. |
| Poly Haven | [Asset license](https://polyhaven.com/license) | CC0 assets | Existing local source manifest inspected | Reuse scanned asphalt, concrete, brick, props and HDRI. Existing local vehicle is covered and cannot show seated figures. Do not assume an uncovered car collection exists here. |
| ambientCG | [License](https://docs.ambientcg.com/license/) | CC0 assets | Existing puddle material documented | Reuse; source dirty tunnel tile/concrete as needed. |
| BlenderKit | [License documentation](https://www.blenderkit.com/docs/licenses/) | Per-asset CC0 or royalty-free terms; account/download tier varies | No sign-in/download | Candidate for proper car cabins. Record the exact asset ID, author, license and allowed sharing before adding to shared assets. |
| Sketchfab | [Creative Commons guide](https://sketchfab.com/licenses) | Model-specific CC license; download/account availability varies | No downloads | Only use models with confirmed commercial/adaptation permission. CC-BY needs credits; reject NC for monetized releases and ND where modifications are needed. |
| AgX / motion blur | [Color management](https://docs.blender.org/manual/en/5.0/render/color_management.html), [Cycles sampling](https://docs.blender.org/manual/en/5.0/render/cycles/render_settings/sampling.html) | Built in | Existing code inspected | AgX, restrained highlights, shutter blur; inspect dark skin and rubber at exposure. Fine sensor texture is separate from the rejected stylized dithering. |
| OptiX | [Blender 5.0 GPU manual](https://docs.blender.org/manual/en/5.0/render/cycles/gpu_rendering.html) | Local NVIDIA hardware/driver | GPU observed: RTX 3050 Laptop 4096 MiB, driver 566.07; Claude currently rendering | No simultaneous GPU jobs. Enable only OptiX device, adaptive samples, OptiX denoising, persistent data; benchmark this scene. The brief's 77-minute total is an estimate, not a measurement. |
| FFmpeg finish | [Official filter documentation](https://ffmpeg.org/ffmpeg-filters.html) | Local build's license | ffprobe used previously; no final Ep3 encode | Exact 24 fps, 1,152 frames; mix and encode once after picture approval. Measure loudness and peaks; never claim audio quality without listening/measurement. |

## Continuity and editorial issues to resolve in the build

- Source code available locally uses a different shot numbering scheme from the Ep2 storyboard. The final-leap framing reference must be verified from an actual final frame, not inferred from a function number.
- A 120 BPM two-bar tail in 4/4 takes 4 seconds. The specified 33.5–36.0 window is 2.5 seconds. Preserve picture timing; start the musical release earlier or use a 2.5-second tail, documenting which the actual score supports.
- The crash repeats from inside in shot 4: preserve damage progression, screen direction and the rider's location in the replay.
- The broken antler is the creature's anatomical LEFT. Do not pick it by screen-left.
- The sign's 12 ft 6 in clearance is 3.81 m; roof + raised Stalker must actually exceed it while the car clears.
- Sam's character is unapproved. Keep facial identity obscured as requested; this does not make it an approved likeness.
- Pull-up and reload hero hands require real reference and close visual checks. Existing walking mocap has no articulated fingers and is not a solution for these shots.
- Flow score, approved creature voices and isolated licensed SFX must be identified. An old mixed WAV is not a clean source stem.
- Browser policy blocked opening local `file:` HTML. The storyboard source can be read and its literal shot data extracted locally without browser execution; no browser bypass is attempted.
