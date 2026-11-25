import os, sys
D = os.path.dirname(os.path.abspath(__file__)); t = open(os.path.join(sys.argv[1], 'comp_s02.py'), encoding='utf-8').read()
for x, y in (("import paint_night as PN", "import paint_day17 as PN"), ("lu = (fs - 24) / 36.0", "lu = None")):
    if x not in t: print('MISSING', x)
    t = t.replace(x, y)
open(os.path.join(D, 'comp_s17.py'), 'w', encoding='utf-8').write(t); print('ok')
