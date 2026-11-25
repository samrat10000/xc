import os, glob, time, datetime as dt
N = {1:96,2:96,3:96,4:96,5:72,6:120,7:120,8:96}; names={1:'Aerial city',2:'Crawler',3:'Screamer rooftop',4:'Horde',5:'Garage ignition',6:'Chase',7:'Brute',8:'Stalker cliffhanger'}
base = os.path.dirname(os.path.abspath(__file__)) + '/out/shots'
done = {s: len(glob.glob(f'{base}/s{s}/f*.png')) for s in N}
tot = sum(done.values()); T = sum(N.values())
# rate from files written in the last 20 min
now = time.time(); recent = [f for s in N for f in glob.glob(f'{base}/s{s}/f*.png') if now - os.path.getmtime(f) < 1200]
rate = len(recent) / 1200 if recent else 1 / 24
eta = dt.datetime.utcnow() + dt.timedelta(seconds=(T - tot) / rate + 240)
ist = eta + dt.timedelta(hours=5, minutes=30)
nowist = dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)
bar = lambda d, n, w=20: '█' * round(w * d / n) + '░' * (w - round(w * d / n))
print(f"**Episode 1 render: {tot} / {T} frames ({100*tot//T}%)**\n\n`{bar(tot,T)}`\n\nFinished video expected around **{ist.strftime('%-I:%M %p')} IST** (about {(T-tot)/rate/3600:.1f} h of rendering left, then a few minutes for the edit and sound).\n")
for s in N:
    st = '✓' if done[s] >= N[s] else ('✱' if done[s] else '○')
    print(f"{st} Shot {s} · {names[s]}: {done[s]}/{N[s]}")
print(f"\n_Updated {nowist.strftime('%-I:%M %p')} IST. This card refreshes about every 30 minutes._")
