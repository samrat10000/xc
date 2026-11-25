"""Transcribe every ElevenLabs take (faster-whisper small.en, local, CPU) and score it against VOICE_SCRIPT.md (Codex's Ep2 check,
ERROR_CATALOG: a take can repeat or drop words). Writes takes_check.json. usage: <python with faster_whisper> check_takes.py"""
import json, re, glob, difflib
from pathlib import Path
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parent
snap = sorted(glob.glob(str(Path.home() / '.cache/huggingface/hub/models--Systran--faster-whisper-small.en/snapshots/*')))[-1]
model = WhisperModel(snap, device='cpu', compute_type='int8', cpu_threads=6, local_files_only=True)
rows = re.findall(r'^\| (N\d|G\d|S\d|M\d|T\d) \| [^|]+\| [^|]+\| [^|]+\| (.+?) \|$', (ROOT / 'VOICE_SCRIPT.md').read_text(encoding='utf-8'), re.M)
plain = lambda s: ' '.join(re.sub(r"[^a-z0-9' ]", ' ', re.sub(r'\[[^\]]*\]', '', s.lower()).replace('1964', 'nineteen sixty four')).split())
out = {}
for prefix, text in rows:
    want = plain(text)
    for p in sorted(ROOT.glob(f'{prefix}_take*.mp3')):
        segs, _ = model.transcribe(str(p), language='en', beam_size=5)
        got = plain(' '.join(s.text for s in segs).replace('1964', ' 1964 '))
        score = difflib.SequenceMatcher(None, want.split(), got.split()).ratio()
        out[p.name] = dict(want=want, got=got, score=round(score, 2))
        print('%-14s %.2f | %s' % (p.name, score, got), flush=True)
(ROOT / 'takes_check.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
