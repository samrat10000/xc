from PIL import Image
import os, sys
e = sys.argv[1]
rows = [('02_mirror/src/fullc', (1, 24, 48, 72)), ('03_kiriyama/src/fullc', (1, 28, 56, 84)), ('05_ritual/v2/fullc', (8, 22, 40, 70))]
sh = Image.new('RGB', (4 * 202, 3 * 360))
for r, (d, fr) in enumerate(rows):
    for i, f in enumerate(fr):
        p = os.path.join(e, d, '%03d.png' % f)
        if os.path.exists(p): sh.paste(Image.open(p).resize((202, 360)), (i * 202, r * 360))
sh.save(os.path.join(e, 'night_contact.png'))
