"""Paint the room plate in world space and draw the custom mirrored display."""
from pathlib import Path
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scipy.ndimage import gaussian_filter, zoom

HERE = Path(__file__).resolve().parent
PLATE = (-.26, .26, -.23, .47)


def smooth(a, b, value):
    t = np.clip((value - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def floor_plate():
    width, height = 2300, 2800
    left, right, near, far = PLATE
    x = np.linspace(left, right, width, dtype=np.float32)[None, :]
    y = np.linspace(far, near, height, dtype=np.float32)[:, None]
    rng = np.random.default_rng(450)
    fine = zoom(rng.normal(0, 1, (201, 58)).astype(np.float32),
                (height / 201, width / 58), order=1)[:height, :width]
    broad = zoom(rng.normal(0, 1, (20, 13)).astype(np.float32),
                 (height / 20, width / 13), order=3)[:height, :width]

    # Rush weft curves over and under darker, perpendicular warp threads.
    warp = np.floor(x / .00445 + .1 * fine)
    weft = (y / .00163 + .12 * (warp % 2) + .085 * fine) % 1
    rib = np.sin(np.pi * weft) ** .8
    pin = np.exp(-((x / .00445 % 1 - .12) / .12) ** 2)
    grain = .079 * (rib - .6) - .028 * pin + .032 * fine + .021 * broad
    grain += .010 * np.sin(x * 14100 + y * 3900 + fine * 4)
    tatami = np.array([.51, .47, .319], dtype=np.float32) + grain[..., None]
    # Trace a T-joint at the far end of a single pair of long brocade edges.
    vertical = (y < .217) & (np.abs(x + .072) < .012)
    horizontal = (y >= .217) & (y < .236)
    cloth = vertical | horizontal
    stitch = np.where(vertical, np.abs(np.abs(x + .072) - .0101),
                      np.abs(y - .234))
    gap = np.where(vertical, np.abs(x + .072), np.abs(y - .220))
    cloth_rgb = np.array([.176, .178, .170], dtype=np.float32)
    cloth_rgb = cloth_rgb + (.023 * fine + .017 * np.sin(y * 4100) * np.sin(x * 5300))[..., None]
    cloth_rgb = cloth_rgb + (np.exp(-(stitch / .00037) ** 2) *
                             (.025 + .033 * (np.sin(y * 2500 + x * 1850) > 0)))[..., None]
    brocade = np.cos((y + x) * 600) * np.cos((y - x) * 600)
    cloth_rgb += (.021 * smooth(.35, .78, brocade))[..., None] * np.array([1., .72, .59])
    cloth_rgb = cloth_rgb * (1 - .62 * np.exp(-(gap / .00065) ** 2))[..., None]
    tatami = np.where(cloth[..., None], cloth_rgb, tatami)

    # The shoji is offscreen right. A slanting column of sun and narrow muntin
    # shadows reveal the floor material in the bright part of the room.
    across = x + .59 * y
    beam = smooth(.004, .014, across) * (1 - smooth(.225, .264, across))
    muntin = np.exp(-((x - .24 * y - .096) / .0054) ** 4)
    crossbar = np.exp(-((y + .24 * x - .123) / .0050) ** 4)
    light = beam * (1 - .77 * np.maximum(muntin, crossbar))
    falloff = .89 + .11 * smooth(-.15, .20, y)
    shadow = tatami * np.array([.70, .66, .94], dtype=np.float32) + [.020, .021, .064]
    bright = tatami * [1.00, .96, .83] + [.425, .362, .205]
    image = (shadow + (bright - shadow) * light[..., None]) * falloff[..., None]
    # Keep the cut to the waking shot grounded with a corner of quilted bedding.
    quilt_edge = x - .072 - .54 * (y + .087) - .0022 * np.sin(y * 84)
    quilt = smooth(-.0010, .0014, quilt_edge) * (1 - smooth(-.080, -.068, y))
    crease = .019 * np.cos((x + y * .24) * 203 + np.sin(y * 47))
    seam = np.exp(-((quilt_edge - .0057) / .0011) ** 2)
    cotton = np.array([.265, .270, .346]) + (crease + .026 * fine + .037 * seam)[..., None]
    image = image * (1 - quilt[..., None]) + cotton * quilt[..., None]
    image = gaussian_filter(image.astype(np.float32), (.55, .55, 0))
    Image.fromarray(np.uint8(np.clip(image * 255 + .5, 0, 255))).save(HERE / 'tatami.png')
    Image.fromarray(np.uint8(light * 255 + .5)).save(HERE / 'window.png')


def display():
    w, h = 640, 1320
    u, v = np.meshgrid(np.linspace(0, 1, w), np.linspace(0, 1, h))
    # A simple painted lock-screen mountain silhouette, almost lost in blue.
    ridge = np.interp(u, [0, .15, .19, .26, .31, .36, .40, .46, .48, .58, .62, .70, .77, .85, 1],
                      [.79, .74, .728, .754, .747, .733, .703, .74, .732, .76, .754, .733, .75, .777, .74])
    ridge += .0014 * np.sin(820 * u) + .0027 * np.sin(151 * u)
    rgb = np.zeros((h, w, 3)) + [15, 20, 30]
    rgb += (10 * np.exp(-((v - .71) / .24) ** 2))[..., None] * [1, .95, 1.4]
    rgb -= (9 * smooth(-.001, .002, v - ridge))[..., None]
    rgb += (4 * smooth(.73, .742, u + .22 * v) *
            (1 - smooth(.79, .82, u + .22 * v)))[..., None] * [1.12, 1, .84]
    img = Image.fromarray(np.uint8(np.clip(rgb, 0, 255)))
    ui = Image.new('RGBA', img.size)
    draw = ImageDraw.Draw(ui)
    font_dir = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
    clock = ImageFont.truetype(str(font_dir / 'bahnschrift.ttf'), 230)
    status = ImageFont.truetype(str(font_dir / 'segoeuib.ttf'), 68)
    draw.text((323, 416), '6:00', font=clock, anchor='mm', fill='#fff0e2')
    draw.text((477, 159), '3%', font=status, anchor='rm', fill='#e8dfe2')
    draw.rounded_rectangle((491, 137, 567, 181), 9, outline='#e5dbdc', width=5)
    draw.rounded_rectangle((568, 149, 575, 169), 2, fill='#c9b5b8')
    draw.rounded_rectangle((499, 145, 511, 173), 3, fill='#ef5b50')
    draw.rounded_rectangle((275, 1241, 365, 1247), 3, fill='#9c99ab')
    draw.ellipse((307, 581, 333, 607), outline='#868093', width=3)
    draw.line([(320, 585), (320, 594), (326, 597)], fill='#868093', width=3)
    draw.line([(307, 581), (312, 577)], fill='#868093', width=3)
    draw.line([(328, 577), (333, 581)], fill='#868093', width=3)
    img.paste(ImageOps.mirror(ui), (0, 0), ImageOps.mirror(ui).getchannel('A'))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((280, 57, 360, 78), 10, fill='#0c0d16')
    draw.ellipse((343, 63, 351, 71), fill='#25263f')
    img.save(HERE / 'display.png')


if __name__ == '__main__':
    floor_plate()
    display()
