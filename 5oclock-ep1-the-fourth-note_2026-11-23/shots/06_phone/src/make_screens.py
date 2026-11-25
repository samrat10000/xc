"""draw the phone lock-screen states (system python with PIL). usage: python make_screens.py <outdir>"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)

def font(sz, jp=False):
    for p in (['C:/Windows/Fonts/YuGothB.ttc', 'C:/Windows/Fonts/msgothic.ttc'] if jp else ['C:/Windows/Fonts/segoeuib.ttf', 'C:/Windows/Fonts/arialbd.ttf']):
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def screen_png(clock, pressed, track):
    W_, H_ = 540, 1170
    im = Image.new('RGB', (W_, H_)); d = ImageDraw.Draw(im)
    for y in range(H_):                                   # dusk-purple player background
        t = y / H_; d.line([(0, y), (W_, y)], fill=(int(40 + 30 * (1 - t)), int(26 + 14 * (1 - t)), int(58 + 30 * (1 - t))))
    d.text((34, 22), clock, font=font(30), fill=(240, 236, 240))
    # battery 3% (red sliver) top right
    d.rounded_rectangle((420, 24, 490, 54), 6, outline=(235, 235, 240), width=3); d.rectangle((492, 33, 498, 45), fill=(235, 235, 240))
    d.rectangle((425, 29, 429, 49), fill=(232, 52, 44)); d.text((360, 22), '3%', font=font(28), fill=(232, 52, 44))
    d.text((W_ // 2, 250), clock, font=font(150), fill=(250, 246, 250), anchor='mm')
    d.text((W_ // 2, 360), '11月23日(日)', font=font(34, True), fill=(220, 214, 226), anchor='mm')
    d.rounded_rectangle((60, 560, 480, 900), 28, fill=(26, 18, 34))
    d.rounded_rectangle((84, 584, 196, 696), 14, fill=(198, 92, 70))                    # album art: a red sun
    d.ellipse((112, 612, 168, 668), fill=(250, 214, 150))
    d.text((216, 600), track[0], font=font(34, True), fill=(244, 240, 246))
    d.text((216, 650), track[1], font=font(26, True), fill=(176, 168, 190))
    d.rounded_rectangle((84, 740, 456, 748), 4, fill=(80, 70, 96)); d.rounded_rectangle((84, 740, 84 + int(372 * track[2]), 748), 4, fill=(236, 230, 240))
    for cx, sym in ((160, 'prev'), (270, 'play'), (380, 'next')):
        r_ = 44 if sym == 'play' else 34
        if sym == 'next' and pressed: d.ellipse((cx - 50, 830 - 50, cx + 50, 830 + 50), fill=(90, 80, 110))
        if sym == 'play':
            d.rectangle((cx - 16, 830 - 24, cx - 6, 830 + 24), fill=(246, 242, 248)); d.rectangle((cx + 6, 830 - 24, cx + 16, 830 + 24), fill=(246, 242, 248))
        else:
            s = 1 if sym == 'next' else -1
            d.polygon([(cx - 14 * s, 830 - 18), (cx + 8 * s, 830), (cx - 14 * s, 830 + 18)], fill=(246, 242, 248))
            d.rectangle((cx + 10 * s - 3, 830 - 18, cx + 10 * s + 3, 830 + 18), fill=(246, 242, 248))
    p = os.path.join(OUT, 'screen_%s_%d_%d.png' % (clock.replace(':', ''), int(pressed), int(track[2] * 100)))
    im.save(p); return p


TR1 = ('夕焼けのうた', 'Kiriyama FM', 0.82); TR2 = ('帰り道', 'Kiriyama FM', 0.03)
for args in (('16:59', False, TR1), ('16:59', True, TR1), ('16:59', False, TR2), ('17:00', False, TR2)):
    print(screen_png(*args))
