"""Phone lock screen for the wake-up shot: emergency alert banner over an incoming call.
python3 phone_screen.py OUT.png"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 590, 1280
F = '/usr/share/fonts/truetype/noto/NotoSans-%s.ttf'
def font(w, s):
    try: return ImageFont.truetype(F % w, s)
    except OSError: return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', s)
im = Image.new('RGB', (W, H))
d = ImageDraw.Draw(im)
for y in range(H):                      # dim blurred wallpaper gradient
    t = y / H
    d.line([(0, y), (W, y)], fill=(int(18 + 20 * t), int(20 + 8 * t), int(34 - 10 * t)))
d.text((W / 2, 150), '3:47', font=font('Light', 150), fill=(235, 235, 240), anchor='mm')
d.text((W / 2, 250), 'Saturday, November 21', font=font('Regular', 30), fill=(210, 210, 215), anchor='mm')
# emergency alert card
d.rounded_rectangle((26, 320, W - 26, 560), 34, fill=(58, 58, 62))
d.text((60, 352), 'Emergency Alert', font=font('Bold', 28), fill=(255, 255, 255))
d.text((W - 60, 352), 'now', font=font('Regular', 24), fill=(190, 190, 195), anchor='ra')
for i, s in enumerate(['NYC Emergency Mgmt: Civil emergency in', 'Manhattan. Shelter in place. Avoid all', 'bridges and tunnels. More info to follow.']):
    d.text((60, 400 + i * 40), s, font=font('Regular', 25), fill=(235, 235, 238))
# incoming call
d.text((W / 2, 760), 'incoming call', font=font('Regular', 28), fill=(200, 200, 205), anchor='mm')
d.text((W / 2, 820), 'Danny', font=font('Regular', 64), fill=(255, 255, 255), anchor='mm')
for cx, col in ((150, (235, 64, 52)), (W - 150, (52, 199, 89))):
    d.ellipse((cx - 64, 1040 - 64, cx + 64, 1040 + 64), fill=col)
d.text((150, 1135), 'Decline', font=font('Regular', 24), fill=(220, 220, 225), anchor='mm')
d.text((W - 150, 1135), 'Accept', font=font('Regular', 24), fill=(220, 220, 225), anchor='mm')
im.filter(ImageFilter.GaussianBlur(.6)).save(sys.argv[1])
