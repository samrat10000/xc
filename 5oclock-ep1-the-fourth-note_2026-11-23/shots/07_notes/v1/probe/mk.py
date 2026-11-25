from PIL import Image
import os, sys
o = sys.argv[1]; fr = (1, 12, 36, 60, 90); sh = Image.new('RGB', (5 * 240, 427))
for i, f in enumerate(fr):
    p = os.path.join(o, 'c', '%03d.png' % f)
    if os.path.exists(p): sh.paste(Image.open(p).resize((240, 427)), (i * 240, 0))
sh.save(os.path.join(o, 'contact.png'))
