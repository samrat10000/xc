"""Public preview photos for internal pose reference, never episode footage."""
import urllib.request,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'references';DEST.mkdir(exist_ok=True)
sources=[
 {'name':'driving-hands-reference.jpg','page':'https://unsplash.com/photos/person-driving-car-during-night-time-94SJZvsnEzY','author':'Edwin Harvey','url':'https://images.unsplash.com/photo-1594436261352-cd1d57393acb?w=900&q=80'},
 {'name':'forearm-grip-reference.jpg','page':'https://depositphotos.com/photos/helping-each-other.html','author':'Depositphotos public preview; underlying photographer unknown','url':'https://st4.depositphotos.com/1784615/21947/i/450/depositphotos_219471508-stock-photo-man-saving-rescuing-helping-woman.jpg'},
]
for source in sources:
 p=DEST/source['name']
 if not p.exists():
  with urllib.request.urlopen(urllib.request.Request(source['url'],headers={'User-Agent':'Mozilla/5.0'}),timeout=20) as r:p.write_bytes(r.read(5000000))
 source['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();source['use']='Internal reference only; not a licensed episode asset or cleared for public redistribution'
(DEST/'POSE_REFERENCE_SOURCES.json').write_text(json.dumps(sources,indent=2),encoding='utf8')
print('Saved',len(sources),'reference previews; not episode footage.')
