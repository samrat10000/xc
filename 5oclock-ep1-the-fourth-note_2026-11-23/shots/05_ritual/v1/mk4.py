from PIL import Image
import os, sys
v = sys.argv[1]; sh = Image.new('RGB', (5 * 240, 2 * 427))
for r, cut in enumerate('ab'):
    for i, f in enumerate((1, 10, 17, 24, 28)):
        p = os.path.join(v, 'probe4_' + cut, 'c', '%03d.png' % f)
        if os.path.exists(p): sh.paste(Image.open(p).resize((240, 427)), (i * 240, r * 427))
sh.save(os.path.join(v, 'contact4.png'))


