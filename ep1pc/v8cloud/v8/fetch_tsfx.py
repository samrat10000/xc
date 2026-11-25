import json,urllib.request,urllib.parse,re,os,sys
o=urllib.request.build_opener(); o.addheaders=[('User-Agent','Mozilla/5.0 (sfx-fetch)')]; urllib.request.install_opener(o)
lines=[l for l in open('/mnt/project-files/reels/series/teaser/CREDITS_teaser_sound.txt') if re.match(r'^\w+_\d+:',l)]
got={}
for l in lines:
    m=re.match(r'^(\w+_\d+): "(.*)" by (\S+) \((CC[^)]*)\) (https://freesound.org/people/[^/]+/sounds/(\d+))',l.strip())
    if not m: print('skip',l[:40]); continue
    key,title,by,lic,url,sid=m.groups()
    q=re.sub(r'\.(wav|mp3|flac|aiff)$','',title)[:60]
    found=None
    for qq in (q, q.split('(')[0], ' '.join(q.split()[:4])):
        u='https://api.openverse.org/v1/audio/?'+urllib.parse.urlencode({'q':qq,'page_size':20})
        try: d=json.load(urllib.request.urlopen(u,timeout=30))
        except Exception as e: print(key,'api',e); continue
        for r in d.get('results',[]):
            if sid in (r.get('foreign_landing_url') or '') or r.get('foreign_identifier')==sid: found=r; break
        if found: break
    if not found: print('MISS',key,title); continue
    f=f"{key}.mp3"
    try: urllib.request.urlretrieve(found['url'],f); got[key]=dict(file=f,title=title,by=by,license=lic,url=url); print('ok',key)
    except Exception as e: print('dl fail',key,e)
json.dump(got,open('index.json','w'),indent=1)
