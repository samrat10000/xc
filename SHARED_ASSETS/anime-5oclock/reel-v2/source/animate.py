"""Animate a continuous 2D cel shot with independently posed body regions."""

import importlib.util
import math
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.interpolate import PchipInterpolator


ROOT = Path(__file__).resolve().parent
FPS = 24
DURATION = 15
OUTPUT_SIZE = (1080, 1920)


def ease(value):
    value = np.clip(value, 0, 1)
    return value * value * (3 - 2 * value)


# Seconds, weight shift, vertical shift, head rotation, elbow rotation, wrist rotation.
# Frame 0.9 is the contact pose. The reply at 8.36 s breaks the held pose.
KEYS = np.array([
    (0.00, -29, -1,   2, -17,  5),
    (0.42, -19, -3,   1, -10,  4),
    (0.92,   0,  0,   0,   0,  0),
    (1.34,   3,  3,   1,   0, -1),
    (1.95,   4,  0,   0,   0, -1),
    (2.16,   2, -4,  -2,   0, -1),
    (2.78,  -5, -7,  -7,  -1,  1),
    (3.72,  -1, -4,  -4,  -1,  0),
    (5.10,   3,  3,  -1,   0,  0),
    (6.66,   2,  1,  -2,   0,  0),
    (8.24,   2,  1,  -2,   0,  0),
    (8.47, -15, -8, -10,  -3, -7),
    (8.91, -39, -8, -14,  18, -7),
    (9.54, -46, -4,  -8,  30,  4),
    (10.25,-41,  1,  -4,  37,  7),
    (11.20,-36,  2,  -4,  33,  1),
    (12.86,-39, -4,  -7,  36,  3),
    (15.00,-37,  2,  -4,  35,  4),
], dtype=float)


class Cel:
    def __init__(self):
        art = Image.open(ROOT / 'sam-cel.png').convert('RGBA')
        # RGB values outside the alpha channel are only a fringe. Premultiply before resampling.
        rgba = np.array(art)
        rgba[:, :, 3] = np.uint8(np.clip((rgba[:, :, 3].astype(float) - 5) * 255 / 245, 0, 255))
        self.open = Image.fromarray(rgba)
        self.blink = self.draw_blink()
        self.pose = PchipInterpolator(KEYS[:, 0], KEYS[:, 1:], axis=0)
        self.xs = np.r_[np.arange(0, art.width, 24), art.width]
        self.ys = np.r_[np.arange(0, art.height, 24), art.height]
        self.x, self.y = np.meshgrid(self.xs, self.ys)
        self.body_weight = ease((1190 - self.y) / 825)
        self.head_weight = ease((443 - self.y) / 134)
        self.arm_weight = (ease((self.x - 474) / 115) * ease((self.y - 509) / 156)
                           * ease((1170 - self.y) / 106))
        self.wrist_weight = ease((self.x - 688) / 88) * self.arm_weight
        self.hair_weight = (ease((345 - self.x) / 118) * ease((359 - self.y) / 97)
                            * ease((self.y - 104) / 95))
        self.boxes = [(left, top, right, bottom) for top, bottom in zip(self.ys[:-1], self.ys[1:])
                      for left, right in zip(self.xs[:-1], self.xs[1:])]

    def draw_blink(self):
        drawing = self.open.copy()
        draw = ImageDraw.Draw(drawing)
        draw.polygon([(454, 225), (461, 220), (477, 215), (485, 215), (484, 229), (476, 232), (461, 233)],
                     fill=(163, 121, 85, 255))
        draw.line([(454, 225), (462, 227), (473, 226), (482, 221)], fill=(67, 47, 39, 255), width=3)
        draw.polygon([(518, 204), (524, 199), (529, 198), (531, 209), (518, 217)], fill=(137, 98, 69, 255))
        draw.line([(518, 209), (523, 210), (530, 205)], fill=(62, 44, 36, 255), width=2)
        return drawing

    @staticmethod
    def rotate_back(x, y, pivot, angle):
        angle = math.radians(angle)
        ox, oy = pivot
        cx, cy = x - ox, y - oy
        return ox + cx * math.cos(angle) + cy * math.sin(angle), oy - cx * math.sin(angle) + cy * math.cos(angle)

    def render(self, frame):
        # Animate on twos at 24 fps, with anchored hips and distinct follow-through for the wrist and hair.
        t = (frame // 2) * 2 / FPS
        lean_x, lean_y, head, elbow, wrist = self.pose(t)
        x = self.x - lean_x * self.body_weight
        y = self.y - lean_y * self.body_weight
        hx, hy = self.rotate_back(x, y, (399, 367), head)
        x += (hx - x) * self.head_weight
        y += (hy - y) * self.head_weight
        ex, ey = self.rotate_back(x, y, (548, 745), elbow)
        x += (ex - x) * self.arm_weight
        y += (ey - y) * self.arm_weight
        wx, wy = self.rotate_back(x, y, (740, 823), wrist)
        x += (wx - x) * self.wrist_weight
        y += (wy - y) * self.wrist_weight
        breeze = (2.5 * math.sin(t * 5.1) + 1.9 * math.sin(t * 3.3))
        x += self.hair_weight * breeze
        y += self.hair_weight * breeze * 0.5
        points = np.stack((x, y), axis=-1)
        quads = np.concatenate((points[:-1, :-1], points[1:, :-1], points[1:, 1:], points[:-1, 1:]), axis=-1)
        mesh = list(zip(self.boxes, map(tuple, quads.reshape(-1, 8))))
        blink = max(float(ease(1 - abs(t - cue) / .15)) for cue in (1.67, 5.5, 9.08, 13.25))
        paint = Image.blend(self.open, self.blink, blink) if blink else self.open
        return paint.transform(paint.size, Image.Transform.MESH, mesh, Image.Resampling.BILINEAR)


class Overlook:
    def __init__(self):
        self.backdrop = Image.open(ROOT / 'overlook.png').convert('RGBA')
        self.cel = Cel()
        # A fixed mirror rim, with a separate layer for the glass interior.
        self.glass_box = (658, 417, 889, 701)
        glass = self.backdrop.crop(self.glass_box)
        matte = Image.new('L', glass.size)
        draw = ImageDraw.Draw(matte)
        draw.polygon([(110, 6), (145, 8), (179, 26), (206, 55), (222, 94), (226, 137),
                      (218, 184), (201, 223), (175, 252), (143, 271), (113, 278), (78, 271),
                      (52, 253), (30, 228), (12, 191), (4, 153), (5, 113), (16, 77),
                      (32, 50), (56, 27), (81, 13)], fill=255)
        self.glass_matte = np.asarray(matte.filter(ImageFilter.GaussianBlur(1.8)), dtype=np.float32) / 255
        self.day = np.asarray(glass.convert('RGB'), dtype=np.float32)
        self.night = self.day * np.array([.23, .30, .50], dtype=np.float32) + (1, 5, 15)
        self.gy, self.gx = np.indices(matte.size[::-1], dtype=np.float32)
        lamp = Image.new('L', matte.size)
        draw = ImageDraw.Draw(lamp)
        draw.polygon([(199, 137), (207, 135), (206, 149), (199, 151)], fill=255)
        draw.polygon([(183, 140), (189, 139), (189, 148), (182, 150)], fill=215)
        self.lamp = np.asarray(lamp.filter(ImageFilter.GaussianBlur(.55)), dtype=np.float32) / 255

    def backdrop_at(self, t):
        if t <= 8.13:
            return self.backdrop.copy()
        progress = float(ease((t - 8.13) / 1.02))
        # Night crosses from one edge of the reflected street to the other with a soft uneven boundary.
        boundary = self.gx + 10 * np.sin(self.gy / 41 + t * 2.5)
        mix = ease((-22 + progress * 279 - boundary) / 32 + .5) * self.glass_matte
        light = self.lamp * float(ease((t - 9.30) / .31))
        fade = self.night * (1 - light[..., None]) + np.array([169, 129, 67]) * light[..., None]
        pixels = self.day * (1 - mix[..., None]) + fade * mix[..., None]
        plate = self.backdrop.copy()
        plate.paste(Image.fromarray(np.uint8(pixels)), self.glass_box[:2])
        return plate

    def frame(self, index):
        t = index / FPS
        plate = self.backdrop_at(t)
        sam = self.cel.render(index)
        plate.alpha_composite(sam, dest=(-217, 87))
        return plate.convert('RGB').resize(OUTPUT_SIZE, Image.Resampling.LANCZOS, box=(3, 0, 912, 1616))


def make_mix(path):
    audio_source = ROOT.parents[1] / 'reel-v1' / 'source' / 'render.py'
    spec = importlib.util.spec_from_file_location('original_sound', audio_source)
    original = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(original)
    original.render_sound(path)
    with wave.open(str(path), 'rb') as wav:
        params = wav.getparams()
        recording = np.frombuffer(wav.readframes(params.nframes), dtype='<i2').astype(float).reshape(-1, 2)
    t = np.arange(int(params.framerate * .27)) / params.framerate
    click = (np.sin(2 * np.pi * 519 * t) * np.exp(-t * 24) +
             .21 * np.sin(2 * np.pi * 1133 * t) * np.exp(-t * 65)) * np.minimum(1, t * 420)
    start = round(.91 * params.framerate)
    recording[start:start + len(t)] += click[:, None] * np.array([2260, 1900])
    with wave.open(str(path), 'wb') as wav:
        wav.setparams(params)
        wav.writeframes(np.clip(recording, -32768, 32767).astype('<i2').tobytes())


def render(output):
    scene = Overlook()
    if output.suffix.lower() == '.jpg':
        frames = [0, 22, 67, 144, 204, 217, 230, 255, 334]
        sheet = Image.new('RGB', (190 * len(frames), 338))
        for pos, frame in enumerate(frames):
            sheet.paste(scene.frame(frame).resize((190, 338)), (pos * 190, 0))
        sheet.save(output, quality=94)
        return
    with tempfile.TemporaryDirectory(prefix='5oclock-motion-') as scratch:
        sound = Path(scratch) / 'chime.wav'
        make_mix(sound)
        command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-f', 'rawvideo',
                   '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(FPS), '-i', 'pipe:0', '-i', str(sound),
                   '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p',
                   '-vf', 'scale=out_color_matrix=bt709', '-colorspace', 'bt709', '-color_primaries', 'bt709',
                   '-color_trc', 'bt709', '-c:a', 'aac', '-b:a', '256k', '-t', str(DURATION), '-movflags', '+faststart',
                   str(output)]
        with subprocess.Popen(command, stdin=subprocess.PIPE) as ffmpeg:
            for frame in range(DURATION * FPS):
                ffmpeg.stdin.write(scene.frame(frame).tobytes())
            ffmpeg.stdin.close()
            if ffmpeg.wait():
                raise RuntimeError('FFmpeg render failed')


if __name__ == '__main__':
    render(Path(sys.argv[1]).resolve())
