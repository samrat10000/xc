import os, sys, re
D = os.path.dirname(os.path.abspath(__file__)); t = open(os.path.join(sys.argv[1], 'comp_s11.py'), encoding='utf-8').read()
m = re.search(r"\n(\s*)night = PN\.draw\(.*\n", t)
if not m: print('MISSING draw line')
ind = m.group(1)
add = (ind + "_ms = np.asarray(Image.open(os.path.join(CEL, 'msam_%03d.png' % f)).convert('RGBA').resize((night.shape[1], night.shape[0]), Image.LANCZOS)).astype(np.float32) / 255\n" +
       ind + "night = night * (1 - _ms[..., 3:4]) + _ms[..., :3] * _ms[..., 3:4]      # the reflection that does not turn\n")
t = t[:m.end()] + add + t[m.end():]
t = t.replace("import paint_night11 as PN", "import paint_night11 as PN\nPN.CLOSE = 0.55")
open(os.path.join(D, 'comp_s13.py'), 'w', encoding='utf-8').write(t); print('ok')
