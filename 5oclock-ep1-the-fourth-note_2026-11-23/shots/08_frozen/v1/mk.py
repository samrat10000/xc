from PIL import Image
import os, sys
e = sys.argv[1]; fr = (1, 16, 32, 48, 64, 80, 100, 120); sh = Image.new('RGB', (270 * 8, 480))
for i, f in enumerate(fr): sh.paste(Image.open(os.path.join(e, 'full', 'fullc', '%03d.png' % f)).resize((270, 480)), (i * 270, 0))
sh.save(os.path.join(e, 'contact_v1.png'))
