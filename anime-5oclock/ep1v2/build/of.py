import json,urllib.request,urllib.parse,os,sys
o=urllib.request.build_opener(); o.addheaders=[('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36')]; urllib.request.install_opener(o)
Q=dict(a.split('=',1) for a in sys.argv[1:])
out=json.load(open('index.json')) if os.path.exists('index.json') else {}
for k,q in Q.items():
    u='https://api.openverse.org/v1/audio/?'+urllib.parse.urlencode({'q':q,'page_size':8,'license':'cc0,by'})
    try: d=json.load(urllib.request.urlopen(u,timeout=30))
    except Exception as e: print(k,e); continue
    os.makedirs(k,exist_ok=True); out[k]=[]
    for i,r in enumerate(d['results']):
        ext=(r.get('filetype') or 'mp3')
        f=f"{k}/{i}_{r['id'][:8]}.{ext}"
        try: urllib.request.urlretrieve(r['url'],f)
        except Exception as e: continue
        out[k].append(dict(file=f,title=r['title'],license=r['license'],creator=r.get('creator'),url=r.get('foreign_landing_url'),dur=r.get('duration')))
    print(k,[(x['title'][:40],x['dur']) for x in out[k]])
json.dump(out,open('index.json','w'),indent=1)
