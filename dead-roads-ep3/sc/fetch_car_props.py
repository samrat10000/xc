"""Download two vetted model assets and their metadata from Khronos' official repo."""
import urllib.request,json,hashlib,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT.parent/'SHARED_ASSETS/ep3/v001/assets/khronos';DEST.mkdir(parents=True,exist_ok=True)
manifest=[]
for name in ('ToyCar','CarConcept'):
 base=f'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/{name}/'
 for suffix in ('glTF-Binary/'+name+'.glb','LICENSE.md','README.md','metadata.json'):
  p=DEST/name/suffix;p.parent.mkdir(parents=True,exist_ok=True);url=base+suffix
  if not p.exists():
   request=urllib.request.Request(url,headers={'User-Agent':'NightTerror-production-assets/1.0'})
   with urllib.request.urlopen(request,timeout=60) as r:content=r.read(100000000)
   if p.suffix=='.glb' and content[:4]!=b'glTF':raise ValueError('Invalid GLB response')
   p.write_bytes(content)
  manifest.append({'file':str(p),'source':url,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
 print('Downloaded',name,flush=True)
(DEST/'sources.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
