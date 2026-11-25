# AUTOMATION: how this episode is produced without the director babysitting it

Any AI (Claude Desktop, Claude Code, Codex) resumes from: STATE.md (queue + status) -> this file -> ERROR_CATALOG.md -> SHOT_RULES.md.

## The loop (one shot at a time, never stop to ask "should I continue?")
1. Take the next shot from the queue in STATE.md. Read its row in `story/` and in the skill's PLAYBOOK_5OCLOCK.md.
2. Run the ERROR_CATALOG pre-flight checklist (silhouette, scale table, projection, clip/sun/axes/encoding, light levels, occlusion, haze, ground/density).
3. Build from the nearest proven code (copy the shot folder of the most similar shot; never start from zero). Shared camera module per shot.
4. Probe at 50% on 4-6 key frames. Look at: contact sheet, full-size crops of hands/faces/the wow detail, each pass alone on magenta when something is wrong, the silhouette test for every creature/character.
5. Fix root causes (one-sentence cause backed by a number or a pass image). Max 4 probe rounds; if still failing, log it as a known weakness and move on (the director decides).
6. Full render in the background (`run_full_vN.ps1`, below-normal priority, refuses to overwrite).
7. While it renders: write the shot's lessons into ERROR_CATALOG.md (general category) and PRODUCTION_LOG.md (what happened), and start the next shot's plan.
8. Deliver: clip path + contact sheet + 1 crop + honest critique. Do not wait for a reply; continue with step 1. If notes arrive later: finish the current shot, then fix the noted one, and add the note to SHOT_RULES.md for all later shots.
9. After the last picture shot: assemble the silent cut (from PNGs, one grade), then sound (blocked items below), then master.

## Blocked on the director (do everything else around these)
- Voices: ElevenLabs needs Sam's browser session (never type passwords). Decide real voice vs ElevenLabs.
- Music: Flow piano is AI-generated; the brief says no AI. Decide.
- Approval of each shot (non-blocking: keep going).

## Token rules (measured in this session)
- One contact sheet per probe (6 frames at 360x640 in ONE image) + ONE crop sheet. Never open single full frames one by one.
- Composite review images in Python (contact + crops + silhouette in one PNG) and open that one file.
- Probe at 50% resolution and only the key frames (1, impact, mid, last). Full render only after the probe passes.
- Edit scripts with exact find/replace (a checked replace helper that prints MISSING), never rewrite a whole file to change a line.
- Copy the previous version's scripts to vN+1 and patch them; never re-read files already understood.
- Diagnose with numbers (pixel counts, means) before looking at images; images cost the most tokens.
- Background renders: never poll; wait for the completion notice.
- Don't re-read the skill docs after the first read; re-read only RULEBOOK/QA/STATE after a context compaction.
- Keep chat updates to a few lines; findings go into the MD files, not the chat.
- Use the strongest model for new hard shots and QA verdicts; repeats of a locked recipe can run on a cheaper model.
