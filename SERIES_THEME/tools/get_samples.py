"""Download the CC0 VSCO 2 CE samples the 5 O'CLOCK series theme uses (github.com/sgossner/VSCO-2-CE, CC0 1.0).
Saves to ../samples/<folder>/. Skips files already present. usage: python -I get_samples.py"""
import json, re, urllib.request, urllib.parse
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'samples'
H = {'User-Agent': 'anim-tool'}
tree = json.load(urllib.request.urlopen(urllib.request.Request(
    'https://api.github.com/repos/sgossner/VSCO-2-CE/git/trees/master?recursive=1', headers=H)))['tree']
paths = [t['path'] for t in tree if t['type'] == 'blob']
WANT = {  # folder -> regex on the repo path
    'cello_spic': r'^Strings/Cello Section/spic/spic_[A-G]\d_v2_RR1\.wav$',
    'cello_sus': r'^Strings/Cello Section/susvib/susvib_[A-G]\d_v3_1\.wav$',
    'cello_trem': r'^Strings/Cello Section/trem/trem_[A-G]\d_v2_1\.wav$',
    'vln_trem': r'^Strings/Violin Section/Trem/VlnEns_Trem_[A-G]#?\d_v2\.wav$|F#3_v1\.wav$',
    'vln_sus': r'^Strings/Violin Section/susVib/VlnEns_susVib_[A-G]#?\d_v2\.wav$',
    'vln_spic': r'^Strings/Violin Section/Spic/VlnEns_Spic_[A-G]#?\d_v2_rr1\.wav$',
    'bass_sus': r'^Strings/Solo Contrabass/SusNV/BKCtbss_SusNV_[A-G]#?\d_v3_rr1\.wav$',
    'timp': r'^Percussion/Timpani/Timpani\d_(Hit_v4_rr1|Hit_v3_rr1|Roll_v5_rr1)_Sum\.wav$',
    'perc': r'^Percussion/(BDrumNewhit_v7_rr[12]_Sum|gongHit_(fff|f)|susCymb1-cresc-(Long|Median)_v1|TB_hit_\w+|susCymb1-hit_fff_rr1|cymbal-crash1_ff_rr1|Anvil_Hit1_v3_Sum)\.wav$',
    'harp': r'^Strings/Harp/KSHarp_\w+\.wav$',
}
n = 0
for folder, rx in WANT.items():
    d = OUT / folder; d.mkdir(parents=True, exist_ok=True)
    for p in paths:
        if folder == 'vln_trem' and not p.startswith('Strings/Violin Section/Trem/'): continue
        if not re.search(rx, p): continue
        f = d / Path(p).name
        if f.is_file() and f.stat().st_size: continue
        url = 'https://raw.githubusercontent.com/sgossner/VSCO-2-CE/master/' + urllib.parse.quote(p)
        f.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=H)).read()); n += 1
    print(folder, len(list(d.glob('*.wav'))))
(OUT / 'LICENSE.txt').write_text('VSCO 2 Community Edition by Versilian Studios / Sam Gossner, CC0 1.0 (public domain).\n'
                                 'https://github.com/sgossner/VSCO-2-CE\n', encoding='utf-8')
print('downloaded', n)
