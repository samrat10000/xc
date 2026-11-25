import json,urllib.request,urllib.parse,os,sys
o=urllib.request.build_opener(); o.addheaders=[('User-Agent','Mozilla/5.0 (sfx-fetch)')]; urllib.request.install_opener(o)
Q={'mg':'50 cal machine gun','gun':'gunshot rifle','bolt':'rifle bolt charging handle','dry':'dry fire click gun empty','brass':'shell casings falling','engine':'v8 engine idle rev','growl':'monster growl','roar':'creature roar','steps':'heavy footsteps running','boom':'cinematic impact boom','flesh':'flesh impact hit','wind':'night wind ambience city','zombie':'zombie groan','ricochet':'bullet ricochet metal','tyre':'tire skid','splat':'gore splat'}
out={}
for k,q in Q.items():
    u='https://api.openverse.org/v1/audio/?'+urllib.parse.urlencode({'q':q,'page_size':8,'license':'cc0,by'})
    try: d=json.load(urllib.request.urlopen(u,timeout=30))
    except Exception as e: print(k,e); continue
    os.makedirs(k,exist_ok=True); out[k]=[]
    for i,r in enumerate(d['results']):
        f=f"{k}/{i}_{r['id'][:8]}.mp3"
        try: urllib.request.urlretrieve(r['url'],f)
        except Exception as e: continue
        out[k].append(dict(file=f,title=r['title'],license=r['license'],creator=r.get('creator'),url=r.get('foreign_landing_url'),dur=r.get('duration')))
    print(k,len(out[k]))
json.dump(out,open('index.json','w'),indent=1)
