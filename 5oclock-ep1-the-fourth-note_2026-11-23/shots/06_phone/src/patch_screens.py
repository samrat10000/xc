"""split the PIL screen drawing out of the Blender build (Blender's python has no PIL): writes make_screens.py and patches build_s06.py"""
import ast, os
D = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(D, 'build_s06.py'); t = open(p, encoding='utf-8').read()
a = t.index('def font(sz, jp=False):'); b = t.index('IMGS = {}')
draw = t[a:b]
ms = ('"""draw the phone lock-screen states (system python with PIL). usage: python make_screens.py <outdir>"""\n'
      'import os, sys\nfrom PIL import Image, ImageDraw, ImageFont\nOUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)\n\n' + draw +
      "for args in (('16:59', False, TR1), ('16:59', True, TR1), ('16:59', False, TR2), ('17:00', False, TR2)):\n    print(screen_png(*args))\n")
open(os.path.join(D, 'make_screens.py'), 'w', encoding='utf-8').write(ms)
t = t[:a] + t[b:]
t = t.replace('from PIL import Image, ImageDraw, ImageFont\n', '')
t = t.replace("    IMGS[key] = bpy.data.images.load(screen_png(*args))",
              "    c_, pr_, tr_ = args\n    IMGS[key] = bpy.data.images.load(os.path.join(HERE6, 'screens', 'screen_%s_%d_%d.png' % (c_.replace(':', ''), int(pr_), int(tr_[2] * 100))))")
t = t.replace("IMGS = {}", "TR1 = ('夕焼けのうた', 'Kiriyama FM', 0.82); TR2 = ('帰り道', 'Kiriyama FM', 0.03)\nIMGS = {}", 1)
ast.parse(t); ast.parse(ms)
open(p, 'w', encoding='utf-8').write(t); print('ok')
