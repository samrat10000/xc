import json, struct, sys
sys.stdout.reconfigure(encoding="utf-8")
for p in sys.argv[1:]:
    b = open(p,'rb').read()
    n = struct.unpack('<I', b[12:16])[0]
    j = json.loads(b[20:20+n])
    ext = j.get('extensions', {})
    meta = ext.get('VRM', {}).get('meta') or ext.get('VRMC_vrm', {}).get('meta')
    print(p, list(ext.keys()))
    print(json.dumps({k:v for k,v in (meta or {}).items() if k!='texture'}, ensure_ascii=False, indent=1))
    print('materials:', [m['name'] for m in j['materials']])
