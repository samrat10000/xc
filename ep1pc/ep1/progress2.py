import os, glob, time, datetime as dt
B = os.path.dirname(os.path.abspath(__file__)) + '/out/'
CUTS = [(2, 36, "Crawler close-up"), (3, 48, 'Crawler at the lens'), (4, 24, 'Crawler eyes close-up'), (5, 36, 'Rooftop wide'),
        (6, 36, 'Scream close-up'), (7, 24, 'Whip pan, heads turn'), (8, 60, 'Horde long take'), (9, 36, 'Feet in puddles'),
        (11, 36, 'Garage reveal'), (12, 36, 'Tyre close-up'), (13, 60, 'Chase tracking'), (14, 24, 'Runner beside the lens'),
        (15, 36, "Car bursts out of the fog"), (16, 36, 'Skid stop'), (17, 60, 'Brute over the shoulder'), (18, 24, 'Brute roar'),
        (19, 24, 'Headlights rev'), (20, 72, 'Stalker overpass'), (21, 36, 'Stalker skull close-up')]
done = {c: len(glob.glob(f'{B}cuts/c{c:02d}/f*.png')) for c, _, _ in CUTS}
g5 = min(36, len(glob.glob(f'{B}cuts/c10/f*.png')))
tot = sum(min(done[c], n) for c, n, _ in CUTS) + g5 + 60; T = sum(n for _, n, _ in CUTS) + 36 + 60
now = time.time()
recent = [f for c, _, _ in CUTS for f in glob.glob(f'{B}cuts/c{c:02d}/f*.png') if now - os.path.getmtime(f) < 1800]
span = max(600, now - min(os.path.getmtime(f) for f in recent)) if recent else 1800
rate = len(recent) / span if len(recent) > 3 else 1 / 30.
left = (T - tot) / rate
utc = dt.datetime.now(dt.timezone.utc); ist = lambda d: (d + dt.timedelta(hours=5, minutes=30)).strftime('%-I:%M %p')
bar = lambda d, n, w=20: '█' * round(w * d / n) + '░' * (w - round(w * d / n))
print(f"**Episode 1 (animated) render: {tot} / {T} frames ({100 * tot // T}%)**\n\n`{bar(tot, T)}`\n")
print(f"Expected finish around **{ist(utc + dt.timedelta(seconds=left + 900))} IST**, including the edit and sound.\n")
lines = ['✓ 1 · Drone dive (done earlier)']
for c, n, nm in CUTS[:8]: lines.append(f"{'✓' if done[c] >= n else ('✱' if done[c] else '○')} {c} · {nm}: {min(done[c], n)}/{n}")
lines.append(f"{'✓' if g5 >= 36 else ('✱' if g5 else '○')} 10 · Headlights ignite: {g5}/36")
for c, n, nm in CUTS[8:]: lines.append(f"{'✓' if done[c] >= n else ('✱' if done[c] else '○')} {c} · {nm}: {min(done[c], n)}/{n}")
print('\n'.join(lines))
print(f"\n_Updated {ist(utc)} IST. I'll refresh this message about every 30 minutes._")
