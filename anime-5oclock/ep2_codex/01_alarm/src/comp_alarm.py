"""Composite the world-painted floor, contact shadow, cel, and dawn finishing."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent


def perspective_coefficients(projected, width, height, tex_size):
    rows, values = [], []
    for (x, y), (u, v) in zip(projected, ((0, 0), (tex_size[0]-1, 0),
                                        (tex_size[0]-1, tex_size[1]-1), (0, tex_size[1]-1))):
        x, y = x * width, y * height
        rows.extend([[x, y, 1, 0, 0, 0, -x*u, -y*u],
                     [0, 0, 0, x, y, 1, -x*v, -y*v]])
        values.extend((u, v))
    return np.linalg.solve(rows, values)


def raster(image, size, coefficients):
    return image.transform(size, Image.Transform.PERSPECTIVE,
                           coefficients, Image.Resampling.BICUBIC)


def pixels(image):
    return np.asarray(image, dtype=np.float32) / 255


def blur(image, sigma):
    return pixels(image.filter(ImageFilter.GaussianBlur(sigma)))


def as_image(array):
    return Image.fromarray(np.uint8(np.clip(array * 255 + .5, 0, 255)))


def mask(size, polygon, offset=(0, 0)):
    w, h = size
    img = Image.new('L', size)
    ImageDraw.Draw(img).polygon([(x*w+offset[0], y*h+offset[1]) for x, y in polygon], fill=255)
    return img


class Composite:
    def __init__(self, size, revision):
        self.w, self.h = size
        self.scale = self.w / 1080
        self.size, self.revision = size, revision
        self.plate = Image.open(HERE / 'tatami.png').convert('RGB')
        self.light = Image.open(HERE / 'window.png').convert('L')
        u = np.linspace(0, 1, self.w, dtype=np.float32)[None, :]
        v = np.linspace(0, 1, self.h, dtype=np.float32)[:, None]
        self.depth_blend = (np.clip((.39 - v) * 2.6, 0, .85) +
                            np.clip((v - .78) * 3.0, 0, .68))[..., None]
        self.vignette = (1 - .24 * np.clip(((u-.5)**2*1.28 + (v-.49)**2)*2.3, 0, 1))[..., None]
        rng = np.random.default_rng(187)
        self.motes = [(rng.uniform(.39, .99), rng.uniform(.13, .8), rng.uniform(1.1, 2.7),
                       rng.uniform(0, 6.28)) for _ in range(34)]
        self.grain = [rng.normal(0, 1, (self.h, self.w)).astype(np.float32) for _ in range(5)]

    def render(self, f, cel, data):
        w, h, s = self.w, self.h, self.scale
        coeff = perspective_coefficients(data['floor'], w, h, self.plate.size)
        plate = raster(self.plate, self.size, coeff)
        bg = pixels(plate)
        bg += (blur(plate, 3.8*s) - bg) * self.depth_blend
        beam = pixels(raster(self.light, self.size, coeff))
        contact = mask(self.size, data['footprint'], (-3*s, 5*s))
        cast = mask(self.size, data['footprint'], (-19*s, 16*s))
        bg *= (1 - .42 * blur(contact, 3.9*s) - .23 * blur(cast, 9*s))[..., None]

        c = pixels(cel)
        a = c[..., 3:4]
        inner = a * np.clip(1 - blur(cel.getchannel('A'), 5*s)[..., None], 0, 1)
        img = c[..., :3] * a + bg * (1 - a)
        wrap = ((.09 if self.revision == 1 else .19) * beam)[..., None]
        img += inner * wrap * np.array([1.0, .63, .38], dtype=np.float32)
        img += beam[..., None] * (1 - a) * np.array([.026, .012, .004], dtype=np.float32)

        f2 = f - (f - 1) % 2
        if self.revision >= 2:
            for u, v, size, phase in self.motes:
                x = int(w * (u + .009*np.sin(f2*.045 + phase) - f2*.00026))
                y = int(h * (v - f2*.00045))
                r = max(2, int(np.ceil(size*s*2)))
                if x-r < 0 or y-r < 0 or x+r >= w or y+r >= h:
                    continue
                weight = beam[y, x] * (1 - a[y, x, 0])
                p = np.arange(-r, r+1, dtype=np.float32)
                glow = np.exp(-(p[:, None]**2 + p[None, :]**2) / (2*(max(.45, size*s))**2))
                warmth = np.array([.30, .194, .086], dtype=np.float32)
                img[y-r:y+r+1, x-r:x+r+1] += glow[..., None] * warmth * weight * (.66 + .34*np.sin(phase + f2*.085))

        highlight = img * np.clip((img.max(axis=2, keepdims=True) - .83) / .17, 0, 1)
        img += .19 * blur(as_image(highlight), 22*s)
        img = (img * 1.025 + np.array([.018, .012, .032], dtype=np.float32)) * self.vignette
        img += .0078 * self.grain[f % len(self.grain)][..., None] * (1.14 - img.mean(axis=-1, keepdims=True))
        return as_image(img)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cel', type=Path)
    parser.add_argument('out', type=Path)
    parser.add_argument('revision', type=int)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    metadata = json.loads((args.cel / 'projection.json').read_text(encoding='utf-8'))
    composite = None
    for frame in sorted(map(int, metadata)):
        cel = Image.open(args.cel / f'cel_{frame:03d}.png').convert('RGBA')
        if composite is None:
            composite = Composite(cel.size, args.revision)
        composite.render(frame, cel, metadata[str(frame)]).save(args.out / f'{frame:03d}.png',
                                                               compress_level=3)
        print(f'composited {frame:03d}', flush=True)


if __name__ == '__main__':
    main()
