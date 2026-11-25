# 5 O'CLOCK series theme: "The Fourth Note"

One signature cue for every episode (Sam asked for a common, "damn crazy" theme). It uses recorded instruments only: VSCO 2 CE strings, percussion, harp and tubular bells (CC0), plus the same marimba and glock as the in-story chime. It is built by code, so any episode can re-cut it.

## The idea
- **The chime.** The town chime is three notes, F#–A#–C#: major, innocent, the town at 17:00. The chime is played on bell, marimba, glock and harp, exactly the timbre of the in-episode chime.
- **The missing fourth note.** Where the fourth note should come, nothing plays. A contrabass drone and a cymbal swell rise out of the gap.
- **The drive.** A 3+3+2 cello + violin spiccato ostinato at 92 BPM in F# minor, with bass drum, timpani and tremolo violins climbing C#, then D, then E.
- **The melody.** F#–A–C# | **G** (held: one semitone above home) F# | E–F#–A | G#–G–C#. It keeps landing on the wrong note.
- **The hit.** A G major chord over the F# bass with gong, bass drum, timpani, crash and anvil, then a **hard cut to true silence**.
- **The end.** A lone bell rings **G**, the fourth note, one semitone above the F# you expect. "The fourth note was never ours to play."

## Files (stems/, 48 kHz stereo)
| file | use |
|---|---|
| theme_full.wav | 34.7 s: the whole cue (titles, trailers, end of season) |
| theme_intro.wav | 0–6.4 s: the chime + the gap + the drone (cold opens) |
| theme_bed_loop.wav | 10.43 s loop, 4 bars of the ostinato (tension under action; it loops on the bar) |
| theme_sting.wav | the hit, the silence and the wrong bell (reveals, the last shot of an episode) |
| stem_bells / strings / ostinato / perc / low.wav | for re-mixing under dialogue |
| theme_cues.json | bar length and the times of the intro, bed, theme, hit, cut and fourth note |

## Rules for every episode
1. Every episode uses the intro (or the three chime notes) near the open, and the sting at its biggest reveal or its last image.
2. Keep the hard cut silent: no foley or room tone in the 0.6 s gap.
3. Under dialogue, use the bed or the low stems, ducked about 10 dB. The melody never sits under a spoken line.
4. Each episode may vary only the last bell. Ep1 rings G. Later episodes can go further from F# as the Listener gets closer.

Rebuild: `python -I tools/get_samples.py` (once), `python -I tools/theme.py`, `python -I tools/check_theme.py` (RMS, cut silence, chroma, spectrogram). Credits: VSCO 2 Community Edition (Versilian Studios, CC0 1.0).
