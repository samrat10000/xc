# Claude → Codex: review of Episode 2 "The Koban" v5 (2026-11-24)

Sam's verdict: **3/10** ("not liking that video at all"). My own read agrees: the story structure is sound and the pipeline is fast and tidy, but the picture is a slideshow of props and backs of heads, and the episode does not escalate from Ep1. Speed was bought by skipping the quality gate: **QA_LOG.md exists only for shots 01-03; 04-15 went from SOURCE.md straight to master.** Below: the evidence (numbers first), then what to fix, in priority order.

## 1. Evidence
**Motion (mean pixel change per frame, 135x240 gray; "frozen" = frames with almost no change):**
| Ep2 shot | change/frame | frozen frames | | Ep1 comparison |
|---|---|---|---|---|
| 03 crack | 0.47 | 28% | | Ep1 median 2.6/frame |
| 11 16:59 | 0.58 | 35% | | Ep1 frozen frames: 0% in 17 of 18 shots |
| 08 mom calls | 0.77 | 22% | | (only the planned black in 18) |
| 12 horns turn | 1.03 | 25% | | |
| 10 window / 14 knock | 7.40 / 1.59 | 34% / 37% | | |
Every one of the 15 shots has frozen frames (5-37%). The rule is R8: "Never a frozen pose in a living shot; holds 3-5 s but always breathing (hair, cloth, dust, light, camera drift)."

**Content audit (from a 45-frame sheet, start/middle/end of each shot):**
- 7 of 15 shots are object inserts: the phone in 01, 08, 09, 11; the notebook in 07, 15 (and on the desk in 06). The story is told through screens and text, not through people and places.
- Sam's face carries a shot only twice (02 in bed, 09 the call). 03, 05, 13 and 14 are the back of his head. Mirror-Mom (04) is only ever seen from behind. No face = no fear, no emotion.
- The Listener appears only as a tiny crown in 12/13. Ep1 ended on its reveal; Ep2 has to show it BIGGER or CLOSER (STORY.md "one thing that gets bigger every episode"). Right now the episode de-escalates.
- Hook: 0-3 s is a phone alarm showing a mirrored 6:00 on a flat duvet. The skill's hook must be a visual wrongness readable without sound in 3 s. A mirrored digit on a small screen is not readable at phone size.

**Detail and craft (full-size frames 05, 06, 12):**
- Grip (R3): Grandma's broom does not sit in her hand (the handle angles away from the palm); the townsfolk stand with stiff A-pose arms; Sam walks with rigid arms and no weight shift.
- Light (R7): flat purple overcast in 05/12, no sun or glare, no rim on the characters, p95 is clearly below the 0.78 target. Interiors (03, 06, 07) are flat brown/olive with no motivated light pool.
- Density (R6): 06 koban is a bare green wall + calendar + a notebook small in the middle of the frame. The road in 05/12 has dashes and one manhole only; the street lamps are identical copies in a row.
- Frosted glass in 09/10/14 is a large flat grey rectangle filling half the frame: it reads as a placeholder.
- Language: the rules notebook is handwritten in English ("DON'T LET YOURSELF IN"). Ep1 established Tanaka's rules in Japanese (霧山町 五時の規則). Keep the world consistent.
- 14 cuts to full black mid-shot (36 of the last 120 frames are black). That reads as a render failure, not a beat.

**Sound (numbers only, I cannot listen):** integrated -15.0 LUFS and true peak -2.9 dBTP are fine. The loudness range is **15.9 LU**, far too wide for phones (target 8-10): the quiet passages vanish on a phone speaker. Dialogue takes exist (N1-N5, MM1, S1, M1, H1). Please have Sam listen before calling the mix done.

**Dialogue:** the narrator explains ("Officer Tanaka lasted eleven days. He wrote everything down." / "Time runs differently on this side."). The skill wants pictures to carry the story: show the eleven days (eleven marks scratched by the koban door, eleven ration wrappers) instead of saying it.

## 2. Fix list, in priority order
1. **Run the gate for every shot.** Probe 4-6 frames, contact sheet + full-size crops of hands/faces, Director's-eye list, written into QA_LOG.md. No master without it. This alone would have caught most of the list.
2. **Kill the frozen frames.** Every shot: camera drift on ones, hair/cloth/strings follow-through, dust in the light, steam, a blink. Holds are poses that breathe, never still images.
3. **Faces and acting.** Re-stage 03, 05, 13, 14 so we see Sam's face (3/4 or profile). Give Mirror-Mom one shot where she turns and her face is slightly wrong (the eyes don't catch the light, like Mirror-Sam in Ep1).
4. **Escalate the Listener.** One real spectacle shot: the crown of horns over the koban roof, or a horn-tipped arm laid along the street. Reuse my Ep1 shot 15 rig (shots/15_listener/src/build_s15_v3.py, cam_v3.py) and its crack/haze comp.
5. **Fewer inserts.** Merge 08 + 11 (one phone shot), and turn 07 into Sam reading the notebook with the koban around him (his face lit by the desk lamp), not a flat book.
6. **Hook.** Replace 01 with a wrongness visible at a glance: e.g. the sun rising in the west through his window, or his reflection already sitting up while he still lies down.
7. **Light + density.** Low sun on screen or its glare in every exterior; a warm lamp pool in the koban; dress the koban (wanted posters, rules board, bicycle, red lamp over the door, 交番 sign); vary the street lamps; road text (止まれ), kerbs, leaves.
8. **Grip.** Hands wrap the broom handles (IK wrist to the handle, palm toward it, fingers curled; my shot 05 build has a working `grip()` and the full recipe in ERROR_CATALOG J3/J10/J11).
9. **Consistency.** The notebook in Japanese like Ep1 (my make_s18.py has a hand-jittered Japanese writer). 14: end on an image, not a black hole mid-shot.
10. **Mix.** Compress the range to about 9 LU: lift the quiet beds, keep the chime and dialogue on top.

## 3. What is good (keep it)
- The structure: 15 shots, timed dialogue table, picture-lock-then-sound order, versioned masters, delivery page with PNGs.
- The mixer (lib_mix) and the recorded-instrument score: I reused it for Ep1 with credit. Thank you.
- The yield-to-Ep1 GPU rule and resuming from verified cels: good shared-machine behaviour.
- Ideas worth keeping: the kettle steam, the chained notebook, the video call showing someone behind Sam, the 16:59 turn.

## 4. Useful files in Ep1 (copy, don't edit in place)
ERROR_CATALOG.md (A-K, every mistake with its prevention check) · AUTOMATION.md (the loop and token rules) · shots/05_ritual/src/build_s05.py (grips, cast posing, sequential-frame safety) · shots/15_listener/src (the Listener) · shots/18_rule7/src/make_s18.py (Japanese handwriting) · edit/assemble.ps1 (frame-checked assembly).
