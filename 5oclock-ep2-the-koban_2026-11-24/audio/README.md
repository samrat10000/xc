# Episode 2 audio handoff

Use VOICE_SCRIPT.md for the eight timing slots and the exact take prefixes. Place the approved MP3s beside that file. The mixer selects takeA when available and takeB otherwise. Keep the optional hum separate as H1. An explicitly edited _takeA_edit.wav is preferred to its matching raw take.

From the Episode 2 folder, run:

```powershell
pwsh -File .\shots\production\finish_episode.ps1 -Version 6
```

The runner verifies the locked picture before mixing. Eight present takes give a dialogue master. The scored version uses the recorded piano, chime and sound effects. The outputs have different filenames. Increment the version for a later mix.

CUE_QA.json lists the checked chime onsets and knock. SOURCE.md records the recipe for each shot, and SOURCES.md in this folder lists the audio credits.

