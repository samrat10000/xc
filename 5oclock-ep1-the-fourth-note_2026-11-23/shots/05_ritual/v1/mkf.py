from PIL import Image
import os, sys
v = sys.argv[1]; fr = (2, 12, 22, 28, 34, 44, 52, 58, 70, 84); sh = Image.new('RGB', (216 * 10, 384))
for i, f in enumerate(fr): sh.paste(Image.open(os.path.join(v, 'fullc', '%03d.png' % f)).resize((216, 384)), (i * 216, 0))
sh.save(os.path.join(v, 'contact_v1.png'))
