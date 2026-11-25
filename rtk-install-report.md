# rtk install report (2026-11-21)

**Installed:** rtk 1.2.1 (rtk-ai/rtk, the Rust Token Killer), via `winget install rtk-ai.rtk`. The installer hash was verified by winget.
Binary: `C:\Users\cross\AppData\Local\Microsoft\WinGet\Packages\rtk-ai.rtk_Microsoft.Winget.Source_8wekyb3d8bbwe\rtk.exe`. winget added this folder to your user PATH.
Check: `rtk gain` prints the savings dashboard, so this is the right tool.

## What changed
- `C:\Users\cross\.claude\settings.json`: the only change is one new `PreToolUse` entry, `{"matcher":"Bash","hooks":[{"type":"command","command":"rtk hook claude"}]}`. Your claude-buddy hooks, permissions, model and other settings are untouched. The diff was checked against the backup.
- Backups: `settings.json.bak-rtk` (mine, made before anything changed) and `settings.json.bak` (rtk's own).
- I used hook-only mode (`rtk init -g --hook-only --auto-patch --no-trust-filters`), so no `RTK.md` was created and `~/.claude/CLAUDE.md` was not edited.
- Telemetry: it was off already ("never asked"). I ran `rtk telemetry disable` to record consent = no explicitly.

## Windows notes
- The hook runs natively as `rtk.exe`. It needs no bash and no jq. A test call to the hook rewrote `git status` to `rtk git status` correctly.
- It only rewrites **Bash** tool calls. It does nothing for Claude Code's **PowerShell** tool, which is the main shell on this PC. You only save tokens when Claude uses Bash, or when you call `rtk <cmd>` yourself.
- WSL bash on this PC is broken (`/bin/bash` not found). This doesn't matter: Claude's Bash tool uses Git Bash, and rtk runs natively.
- **Restart Claude Code** so new sessions pick up the PATH change and the hook.

## Before/after measurement
| Command | Raw bytes | rtk bytes | Saved |
|---|---|---|---|
| `git status` (dead-roads-ep2, clean tree) | 100 | 49 | 51% |
| `ls -laR` of `Downloads\xc` | 1,693,515 | 794 | ~99.9%* |

*Not a fair comparison: `rtk ls` printed only the top-level folders and dropped the recursive listing. That's fine for orienting, but if you need the full tree, use `rtk bypass ls -laR` or run it without rtk.

## Uninstall
```
rtk init -g --uninstall
winget uninstall rtk-ai.rtk
```
To restore settings by hand instead, copy `settings.json.bak-rtk` back over `settings.json`.
