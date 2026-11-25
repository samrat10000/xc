from pathlib import Path
from urllib.request import Request,urlopen
import re,json
out=Path(r'C:/Users/cross/Downloads/xc/anime-5oclock/ep2_codex/production/audio/recordings')
clips={
 'buzz':'https://freesound.org/people/mobaudio/sounds/384485/',
 'broom':'https://freesound.org/people/randbsoundbites/sounds/792417/',
 'knock':'https://freesound.org/people/qubodup/sounds/442878/',
 'paper':'https://freesound.org/people/Mihacappy/sounds/814247/',
 'steps':'https://freesound.org/people/FOSSarts/sounds/740419/',
 'door':'https://freesound.org/people/RutgerMuller/sounds/50706/',
 'kettle':'https://freesound.org/people/sethlind/sounds/265017/',
 'hinge':'https://freesound.org/people/Mariayolanda511/sounds/850566/',
}
notes=json.loads((out/'freesound_sources.json').read_text()) if (out/'freesound_sources.json').exists() else {}
for name,url in clips.items():
 if name in notes and (out/(name+'.mp3')).exists(): continue
 try:
    payload=urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=18).read().decode('utf-8')
    candidates=re.findall(r'https?://cdn\.freesound\.org/previews/[^"\s<]+?\.mp3',payload)
    link=next((s for s in candidates if 'hq' in s),candidates[0] if candidates else None)
    if link is None:
        print(name,'no public preview',flush=True)
        continue
    sample=urlopen(Request(link,headers={'User-Agent':'Mozilla/5.0'}),timeout=18).read()
    (out/(name+'.mp3')).write_bytes(sample)
    notes[name]={'page':url,'preview':link}
    print(name,len(sample),flush=True)
 except Exception as e: print(name,type(e).__name__,str(e)[:170],flush=True)
(out/'freesound_sources.json').write_text(json.dumps(notes,indent=2))

