---
name: chatgpt-handoff
description: Sam also uses ChatGPT/Codex on the xc folder; handoff guide + file-inbox protocol between the AIs (2026-11-21)
metadata:
  type: reference
  modified: 2026-11-21T11:37:32.551Z
---
Sam (2026-11-21 5 PM IST) shared C:\Users\cross\Downloads\xc with ChatGPT/Codex and is the boss of both AIs.
Guide: xc\PROJECT_HANDOFF.md, starter prompt xc\STARTER_PROMPT.md (copies in /mnt/project-files/handoff/).
Protocol: AIs exchange notes ONLY via xc\INBOX_FOR_CLAUDE.md (ChatGPT -> Claude) and xc\INBOX_FOR_CHATGPT.md (Claude -> ChatGPT), append-only dated notes, and only when Sam asks (token saving). Don't run two GPU renders at once.
**How to apply:** when Sam says ChatGPT left a note, read INBOX_FOR_CLAUDE.md; refresh PROJECT_HANDOFF.md when big status changes and Sam asks. Related: [[sam-global-rules]].
SHARED FOLDER (Sam 2026-11-21 5:40 PM IST): xc\SHARED_ASSETS\ is THE shared folder for Claude + Codex (README.md lists every asset; mirror of project reels/ minus old mp4s, Sam's originals incl. Night_Terror_Fastback_v2.glb, Asus blends). From now on ALL new assets from every thread go there too, with a README log line. Codex Ep3 brief: xc\dead-roads-ep3\CODEX_INSTRUCTIONS.md (source /mnt/project-files/handoff/). Copy method: tar, split into 24 MB parts, one device_commit_files call per part in parallel (bigger calls time out).
RENDER RULE (Sam, all threads): render on Sam's PC GPU whenever possible, not cloud.
