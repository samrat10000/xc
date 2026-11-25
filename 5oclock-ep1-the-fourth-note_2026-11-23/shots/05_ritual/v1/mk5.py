from PIL import Image
import os, sys
v = sys.argv[1]; sh = Image.new('RGB', (3 * 300, 533))
for i, f in enumerate((1, 17, 28)):
    sh.paste(Image.open(os.path.join(v, 'probe5_b', 'c', '%03d.png' % f)).resize((300, 533)), (i * 300, 0))
sh.save(os.path.join(v, 'contact5.png'))
