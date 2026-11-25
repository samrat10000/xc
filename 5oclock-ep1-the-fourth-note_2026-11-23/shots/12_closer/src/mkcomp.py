import os, sys
D = os.path.dirname(os.path.abspath(__file__)); t = open(os.path.join(sys.argv[1], 'comp_s11.py'), encoding='utf-8').read()
reps = [("import paint_night11 as PN", "import paint_night11 as PN\nimport json as _j\nfrom scipy.ndimage import uniform_filter1d as _u1\nM12 = _j.load(open(os.path.join(sys.argv[1], 'meta.json')))"),
        ("night = PN.draw(", "PN.CLOSE = M12[str(f)].get('close', 0.0); night = PN.draw("),
        ("    Image.fromarray((np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)).save(os.path.join(OUT, '%03d.png' % f))",
         "    wv = M12[str(f)].get('whip', 0.0)\n    if wv > 0.02:                                                        # whip-pan smear frames\n        img = _u1(img, size=int(9 + wv * 260), axis=1, mode='nearest')\n    Image.fromarray((np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)).save(os.path.join(OUT, '%03d.png' % f))")]
for x, y in reps:
    if x not in t: print('MISSING', x[:50])
    t = t.replace(x, y)
open(os.path.join(D, 'comp_s12.py'), 'w', encoding='utf-8').write(t); print('ok')
