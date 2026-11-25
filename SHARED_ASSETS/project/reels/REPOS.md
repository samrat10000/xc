# Useful repos/tools (scrape internet, 2026-11-21)

Sources: Sam's Instagram saved + liked pages were EMPTY (nothing to read there), so this list comes from web search and articles (DeployHQ "7 free repos that cut Claude Code token usage", Blender Artists, GitHub). Pinterest not checked (not a source for repos). If Sam forwards names, add them.

## Tested for real
| Rank | Repo | What it does | Result |
|---|---|---|---|
| 1 | rtk-ai/rtk (https://github.com/rtk-ai/rtk) | Rust CLI proxy that shrinks shell output before Claude reads it (hook) | Built from source (v0.49.0, 4m38s). `ls -laR` output 3744 -> 1527 bytes (-59%), `git status` -51%, but `git log --stat` was NOT reduced (114930 -> 115008). Only helps shell output, not Read/Grep. Safe: source-built, no installer run. Worth using for log-heavy Blender/ffmpeg runs; savings are real but modest overall. |
| 2 | ahujasid/blender-mcp (https://github.com/ahujasid/blender-mcp) | Claude drives a live Blender: scene info, scripts, asset search (Poly Haven), 3D generation | Cloned and read (updated 2026-11-18). Has built-in telemetry + consent prompt, so keep telemetry OFF before installing into Blender on the Asus. Not installed there yet (needs Sam's Blender session). Useful for fast scene/camera tweaks; our pipeline already scripts bpy directly, so gain is moderate. |

## Read but not installed (claims only)
- JuliusBrussee/caveman: terse output voice. Claimed 3% (/caveman) to 35% (/ultracave) fewer output tokens; v4 CLI sends telemetry by default. Risk: terse replies can hurt quality, test before adopting. Low priority.
- tirth8205/code-review-graph: tree-sitter graph over MCP so Claude reads fewer files. Claim "63x" is vs whole-repo baseline, so inflated. Only useful for big code repos, not for our scripts.
- vercel-labs/agent-browser: browser CLI with reusable logins. Not needed (we have Chrome).
- phuryn/claude-usage, Maciek-roboblog/Claude-Code-Usage-Monitor: usage dashboards, monitoring only, no savings.
- Alishahryar1/free-claude-code: swaps in non-Claude models. Not Claude, quality drop, skip.
- CommonSenseMachines/blender-mcp: text-to-animation from a fixed library; generic motions, would read as AI. Skip.
- Blender mocap candidates (GVHMR, PosePipe/MediaPipe addon, text2motion, Rigify which is built into Blender): video-to-motion from real footage of Sam would give the most real-looking movement. GVHMR needs a GPU with more headroom than 4 GB likely; PosePipe (MediaPipe) is lighter. Not tested yet.
- agmmnn/awesome-blender: curated add-on list, good for browsing.

## Honest verdict
Token-saving repos give small real gains (rtk ~50% on directory listings/status only). No repo gives "same output at far fewer tokens" for free; the biggest saver remains the project rules (Sonnet for routine, few image checks). Biggest realism gain would come from real-footage mocap, next test.
