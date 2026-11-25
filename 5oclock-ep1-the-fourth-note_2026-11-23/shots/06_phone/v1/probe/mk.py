from PIL import Image
import os, sys
o = sys.argv[1]; sh = Image.new('RGB', (4 * 300, 533))
for i, f in enumerate((1, 20, 30, 40)):
    p = os.path.join(o, 'c', '%03d.png' % f)
    if os.path.exists(p): sh.paste(Image.open(p).resize((300, 533)), (i * 300, 0))
sh.save(os.path.join(o, 'contact.png'))
