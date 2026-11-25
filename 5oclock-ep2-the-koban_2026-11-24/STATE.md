# Episode 2 · The Koban

Production date 2026-11-24. This folder is the active, independent project. The Episode 1 folder and anime-5oclock are protected. Use the copies in this folder.

| # | Shot | Current status |
|---|---|---|
| 01 | Alarm | Locked v1 |
| 02 | Wrong room | Locked v2 |
| 03 | The crack | Reviewed v1 |
| 04 | Mirror-Mom | Reviewed v2 |
| 05 | The street | Reviewed v2 |
| 06 | The koban | Reviewed v1 |
| 07 | The rules | Reviewed v1 |
| 08 | Mom calls | Reviewed v2 |
| 09 | Behind him | Reviewed v1 |
| 10 | The window | Reviewed v2 |
| 11 | 16:59 | Reviewed v1 |
| 12 | The horns turn | Reviewed v1 |
| 13 | Rule one | Reviewed v1 |
| 14 | The knock | Reviewed v1 |
| 15 | Rule eight | Reviewed v1 |
| Audio | ElevenLabs and recorded score | Eight named dialogue takes, hum, piano, four-note chime and foley mastered in v5. |

See PRODUCTION_LOG.md for critiques, ERROR_CATALOG.md for pre-flight, and audio/VOICE_SCRIPT.md for the voice filenames.

## Deliverables

[Scored cut and shot index](episode/DELIVERY.md). Picture locked at 63 seconds, 1,512 frames, 1080 × 1920 at 24 fps. The mux matches all 15 cut boundaries. The first scored version below the loudness target and the second version over the peak ceiling remain earlier iterations. The selected v3 AAC measures −15.02 LUFS and −2.80 dBTP. Check the edited mix by ear when the dialogue takes arrive.

The selected full reel is v5. All eight lines matched the script on the encoded export. The named raw and edited takes are in audio/.


## v6 revision in progress

Sam authorized the shot, edit, and sound fixes from V5_SELF_REVIEW.md and ../CLAUDE_REVIEW_EP2.md on 2026-11-24. Claude is revising Episode 1 separately. Use ../CODEX_CLAUDE_STATUS.md for shared continuity decisions and GPU coordination. Earlier v5 outputs are preserved.

- Render inputs in shots/production use KOBAN_PICTURE_REVISION=6. The original recipe still builds the earlier versions with that variable unset.
- Core queue: Shot 10 v3, Shot 13 v2, Shot 12 v2, Shot 15 v2, Shot 14 v2, Shot 05 v3, Shot 07 v2. The p60, p62 and p63 probes capture the movement revisions and preflight.
- Additional acting probes p64 for 04, 06 and 11 start after the core queue. Review those sheets before queuing the extra masters.
- Once selected shot masters pass, use audio/revision_cut_v6.py to lock the revised picture and audio/revision_mix_v6.py for the natural-cadence score and dialogue master. The v6 product has its own timeline and stems.
- No launch of a new Blender process while another project owns it. Resume a preempted master with -Resume only if the scene source and version are unchanged.

The core seven rebuilt shots passed native frame-count checks and contact-sheet review. The v6 cut removes the tracking-camera obstruction at source frames 43–52 of Shot 05. The reaction re-probes passed for 03, 04, 06 and 11. The final queue is building those masters and then runs audio/finish_v6.ps1 and the local dialogue transcription.

The 04, 06 and 11 masters are built and visually reviewed. Shot 03 v2 is the sole remaining render. After it completes, the finish script locks the 1,378-frame v6 cut and runs the mix and release checks. The corrected shared theme stems and cue sheet are local under audio/series_theme_v6.

Shot 03 v2 finished and passed visual review. The v6 silent cut and AAC master were encoded at 57.417 seconds, 1,378 frames. The AAC loudness precheck is −14.94 LUFS, −2.94 dBTP, 7.80 LU. The decoded boundary, blackout, score gap and speech checks are running.

## Selected master · Episode 2 v6

[Full reel](episode/5oclock_ep2_the_koban_v6.mp4) · [Delivery and source index](episode/DELIVERY_V6.md) · [Final contact sheet](episode/v6/contact_v6.jpg)

- Revised masters are 03 v2, 04 v3, 05 v3, 06 v2, 07 v2, 10 v3, 11 v2, 12 v2, 13 v2, 14 v2, and 15 v2. Edits to retained masters are in the timeline.
- Confirmed all 19 segment boundaries, exactly seven authored black frames, the 0.62-second score gap, and seven spoken lines by local transcription. The source-duration comparison found no dialogue speed-ups. Human listening is pending.
- The final AAC measures −14.94 LUFS, −2.94 dBTP and 7.80 LU range. The v5 master still has the same SHA-256.
- Future handoffs start from this section, the delivery index and ../CODEX_CLAUDE_STATUS.md.

## v7 director hand and gait pass

Sam approved the v6 voices and flagged 05, 06, 07, 10 and 13 for targeted gait, wrist, finger and door-contact work. Plan and review evidence are in [V7_HAND_REVIEW.md](V7_HAND_REVIEW.md). The v6 AAC stream and frame layout are the edit baseline.

**Paused by Sam.** The queued Shot 05 probe was stopped before it rendered. The v7 source draft is unverified and v6 is still the selected master. Resume only when Sam explicitly says to start after Episode 1.
