"""Generate Ep1's 11 voice lines through the ElevenLabs API (same series voices as Codex's Ep2: George = Narrator, Roger = Sam and
Mirror-Sam, an old female voice for Grandma; 8 different voices layered for the town's "Okaeri, Sam.").
Needs the env var ELEVENLABS_API_KEY (set by Sam; never written to disk by this script). Writes <PREFIX>_takeA.mp3 / _takeB.mp3
next to this file, skips files that already exist, logs voice ids + model to voices_generated.json.
usage: python -I gen_voices.py            (then: python -I mix_ep1.py)"""
import json, os, re, sys, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KEY = os.environ.get('ELEVENLABS_API_KEY', '').strip()
if not KEY and (ROOT / '.elevenlabs_key').is_file(): KEY = (ROOT / '.elevenlabs_key').read_text(encoding='utf-8').strip()   # Sam's local key file
if not KEY: sys.exit('no ElevenLabs key: set ELEVENLABS_API_KEY or put the key in audio/.elevenlabs_key')
API = 'https://api.elevenlabs.io/v1'
SERIES = {'Narrator': 'JBFqnCBsd6RMkjVDRZzb', 'Sam': 'CwhRBWXzGAHq8TQ4Fs17'}          # George, Roger (as in Ep2)
SET = {'Narrator': dict(stability=0.4, similarity_boost=0.8, style=0.3, speed=0.9), 'Sam': dict(stability=0.45, similarity_boost=0.8, style=0.2),
       'Grandma': dict(stability=0.5, similarity_boost=0.8, style=0.25, speed=0.95), 'Town': dict(stability=0.5, similarity_boost=0.75)}


def call(path, body=None, raw=False):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body else None,
                                 headers={'xi-api-key': KEY, 'Content-Type': 'application/json', 'Accept': 'audio/mpeg' if raw else 'application/json'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r: return r.read() if raw else json.load(r)
        except urllib.error.HTTPError as e:
            msg = e.read()[:300]
            if e.code == 429 and attempt < 3: time.sleep(8 * (attempt + 1)); continue
            raise SystemExit(f'HTTP {e.code} on {path}: {msg}')


voices = call('/voices')['voices']
lab = lambda v, k: (v.get('labels') or {}).get(k, '').lower()
old_f = [v for v in voices if lab(v, 'gender') == 'female' and lab(v, 'age') in ('old', 'elderly')]
SERIES['Grandma'] = (old_f or [v for v in voices if lab(v, 'gender') == 'female' and lab(v, 'age') == 'middle aged'] or
                     [v for v in voices if lab(v, 'gender') == 'female'])[0]['voice_id']
town = [v['voice_id'] for v in voices if v['voice_id'] not in SERIES.values()][:8]
rows = re.findall(r'^\| (N\d|G\d|S\d|M\d|T\d) \| [^|]+\| [^|]+\| ([^|]+)\| (.+?) \|$', (ROOT / 'VOICE_SCRIPT.md').read_text(encoding='utf-8'), re.M)
log = dict(model=None, voices=dict(SERIES, town=town), files=[])


def tts(voice, text, settings, out):
    if out.exists() and out.stat().st_size: return
    for model in ('eleven_v3', 'eleven_multilingual_v2'):                     # v3 understands the [audio tags]
        try:
            body = dict(text=text if model == 'eleven_v3' else re.sub(r'\[[^\]]*\]\s*', '', text), model_id=model,
                        voice_settings={k: v for k, v in settings.items() if k != 'speed'})
            if 'speed' in settings and model != 'eleven_v3': body['voice_settings']['speed'] = settings['speed']
            out.write_bytes(call(f'/text-to-speech/{voice}', body, raw=True)); log['model'] = model; log['files'].append(out.name); return
        except SystemExit as e:
            if model == 'eleven_v3': print('v3 failed, falling back:', e); continue
            raise


for prefix, who, text in rows:
    who = who.strip(); text = text.strip()
    if prefix == 'T1':
        for i, v in enumerate(town): tts(v, text, SET['Town'], ROOT / f'T1_take{"ABCDEFGH"[i]}.mp3')
        continue
    role = 'Narrator' if who == 'Narrator' else 'Grandma' if who.startswith('Grandma') else 'Sam'
    for t in 'AB': tts(SERIES[role], text, SET[role], ROOT / f'{prefix}_take{t}.mp3')
    print('ok', prefix, role, flush=True)
(ROOT / 'voices_generated.json').write_text(json.dumps(log, indent=2), encoding='utf-8')
print('done', len(log['files']), 'files')
