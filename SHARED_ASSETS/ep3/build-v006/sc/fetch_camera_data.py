"""Fetch only public recorded-camera data, not install or execute an add-on."""
import ast,hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT.parent/'SHARED_ASSETS/ep3/v001/references/camera-shakify'
DEST.mkdir(parents=True,exist_ok=True)
sources={n:'https://raw.githubusercontent.com/EatTheFuture/camera_shakify/master/'+n for n in ['shake_data.py','LICENSE_DATA.md']}
report=[]
for name,url in sources.items():
 p=DEST/name
 if not p.exists():
  request=urllib.request.Request(url,headers={'User-Agent':'NightTerror-production-reference/1.0'})
  with urllib.request.urlopen(request,timeout=20) as response: content=response.read(4000000)
  p.write_bytes(content)
 report.append({'file':str(p),'source':url,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
module=ast.parse((DEST/'shake_data.py').read_text(encoding='utf8'))
values={}
for node in module.body:
 if isinstance(node,ast.Assign):
  for target in node.targets:
   if isinstance(target,ast.Name):
    try: values[target.id]=ast.literal_eval(node.value)
    except (ValueError,TypeError): pass
(DEST/'sources.json').write_text(json.dumps(report,indent=2),encoding='utf8')
for k,v in values.items():
 if k=='SHAKE_LIST':
  normalized={name:{'name':entry[0],'fps':entry[1],'channels':[{'path':key[0],'axis':key[1],'keys':points} for key,points in entry[2].items()]} for name,entry in v.items()}
  (DEST/'shake_data.json').write_text(json.dumps(normalized),encoding='utf8')
  print('SHAKES',[(x,type(y).__name__,len(y)) for x,y in v.items()])
print('Saved public data and license. No add-on code executed.')
