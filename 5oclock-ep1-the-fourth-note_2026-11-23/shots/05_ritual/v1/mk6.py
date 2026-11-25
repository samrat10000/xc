from PIL import Image
import os, sys
v = sys.argv[1]; sh = Image.new('RGB', (7 * 162, 2 * 288), (90, 90, 100))
for r, cut in enumerate('ab'):
    for i, f in enumerate((1, 5, 9, 14, 19, 24, 28)):
        im = Image.open(os.path.join(v, 'probe6_' + cut, 'cel_%03d.png' % f)).convert('RGBA')
        bg = Image.new('RGBA', im.size, (90, 90, 100, 255)); bg.alpha_composite(im)
        sh.paste(bg.convert('RGB').resize((162, 288)), (i * 162, r * 288))
sh.save(os.path.join(v, 'contact6.png'))
