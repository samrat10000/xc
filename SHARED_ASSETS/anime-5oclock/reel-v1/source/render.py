"""Composite the mirror scene and render its stereo mix to Instagram MP4."""

import math
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
from scipy import ndimage, signal


HERE = Path(__file__).resolve().parent
FPS = 24
DURATION = 15
SIZE = (1080, 1920)
RATE = 48000


def ease(start, stop, time):
    fraction = min(1, max(0, (time - start) / (stop - start)))
    return fraction * fraction * (3 - 2 * fraction)


def bands(samples, low, high):
    return signal.sosfilt(signal.butter(2, (low, high), fs=RATE, btype="bandpass", output="sos"), samples)


def render_sound(path):
    rng = np.random.default_rng(502)
    count = DURATION * RATE
    time = np.arange(count) / RATE
    wind = bands(rng.standard_normal(count), 45, 385)
    air = bands(rng.standard_normal(count), 450, 2400)
    drift = 0.78 + 0.13 * np.sin(2 * np.pi * 0.21 * time) + 0.09 * np.sin(2 * np.pi * 0.09 * time)
    quiet = 1 - 0.43 * np.exp(-((time - 8.3) / 1.9) ** 2)
    stereo = np.column_stack((wind * 0.047 + air * 0.009, wind * 0.039 + np.roll(air, 39) * 0.011))
    stereo *= (drift * quiet)[:, None]

    def place(sound, when, left, right):
        start = int(when * RATE)
        length = min(len(sound), count - start)
        stereo[start:start + length, 0] += sound[:length] * left
        stereo[start:start + length, 1] += sound[:length] * right

    # Texture first, then the lower heel impact. The second sound is a small weight shift.
    for when, gain, side in [(0.63, 0.44, 0.69), (12.19, 0.14, 0.62)]:
        t = np.arange(int(RATE * 0.36)) / RATE
        grit = bands(rng.standard_normal(len(t)), 900, 3300) * np.exp(-t * 34)
        sole = bands(rng.standard_normal(len(t)), 55, 320) * np.exp(-t * 22)
        foot = (grit * 0.21 + sole * 0.43 + np.sin(2 * np.pi * 68 * t) * np.exp(-t * 54) * 0.08)
        foot *= np.minimum(1, t * 185)
        place(foot, when, gain, gain * side)

    # A small, unrelated bird call gives the opening a physical space.
    for when, frequency in [(0.54, 1880), (0.68, 2200), (1.39, 1720)]:
        t = np.arange(int(RATE * 0.11)) / RATE
        phase = 2 * np.pi * (frequency * t + 1250 * t * t)
        bird = np.sin(phase) * np.sin(np.pi * t / 0.11).clip(0) ** 2
        place(bird, when, 0.018, 0.029)

    def chime(when, notes, reply=False):
        t = np.arange(int(RATE * 1.65)) / RATE
        for delay, frequency in notes:
            phase = 2 * np.pi * frequency * t
            bell = (np.sin(phase) * np.exp(-t * 3.8)
                    + 0.19 * np.sin(phase * 2.01 + 0.5) * np.exp(-t * 8.8)
                    + 0.075 * np.sin(phase * 3.11) * np.exp(-t * 14))
            bell *= (1 - np.exp(-t * (55 if reply else 111)))
            bell += bands(rng.standard_normal(len(t)), 460, 2100) * np.exp(-t * 14) * 0.014
            bell = bands(bell, 360, 1550 if reply else 2490)
            bell = np.tanh(1.25 * bell) / 1.25
            left, right = (0.034, 0.105) if reply else (0.135, 0.109)
            place(bell, when + delay, left, right)
            place(bell, when + delay + 0.091, right * 0.25, left * 0.31)
            place(bell, when + delay + 0.217, left * 0.13, right * 0.17)

    chime(2.01, [(0, 784), (0.36, 659.25), (0.78, 587.33), (1.31, 659.25)])
    chime(8.36, [(0, 779.8), (0.39, 651), (0.84, 581.1), (1.42, 652.2), (2.04, 523.2)], reply=True)
    chime(12.74, [(0, 522.1)], reply=True)

    fade = np.minimum(1, time / 0.1) * np.minimum(1, (DURATION - time) / 0.2)
    stereo *= fade[:, None] * 4.25
    pcm = (32767 * np.tanh(stereo)).astype("<i2")
    with wave.open(str(path), "wb") as wav:
        wav.setparams((2, 2, RATE, 0, "NONE", "not compressed"))
        wav.writeframes(pcm.tobytes())


class Street:
    def __init__(self):
        self.wide = Image.open(HERE / "street.png").convert("RGB")
        self.reverse = Image.open(HERE / "reaction.png").convert("RGB")
        self.closed_eyes = self.blink_plate()
        self.mirror_bounds = (663, 410, 869, 684)
        night = np.asarray(self.wide.crop(self.mirror_bounds), dtype=np.float32)
        red, green, blue = night.transpose(2, 0, 1)
        glass = (blue - red > 9) & (blue - green > 3)
        regions, _ = ndimage.label(glass)
        target_region = regions[50, 105]
        if target_region == 0:
            sizes = np.bincount(regions.ravel())
            sizes[0] = 0
            target_region = sizes.argmax()
        glass = ndimage.binary_fill_holes(regions == target_region)
        glass = ndimage.binary_erosion(glass, iterations=1)
        self.matte = Image.fromarray(np.uint8(ndimage.gaussian_filter(glass.astype(float), 0.9) * 255))
        self.night = Image.fromarray(night.astype(np.uint8))
        # Approximate the daytime mirror using the same layout so the glass and the reflected edges register.
        luminance = night @ np.array([.22, .66, .12])
        day_value = np.clip(19 + 1.48 * luminance, 0, 155)
        # Dark hills, gray light and a cooler foreground. The one lit window comes on at the reply.
        sky = np.clip((blue - green - 13) / 23, 0, 1)
        day_value = np.clip(day_value + sky * 46, 0, 161)
        day = np.stack((day_value * .97, day_value * 1.00, day_value * 1.04), axis=2)
        y, x = np.indices(glass.shape)
        lamp = np.clip((red - blue - 22) / 38, 0, 1) * ((x - 175) ** 2 + (y - 165) ** 2 < 30 ** 2)
        day = day * (1 - lamp[..., None]) + np.array([64, 64, 65]) * lamp[..., None]
        self.day = Image.fromarray(day.astype(np.uint8))
        self.daywide = self.paint_mirror(0)

    def blink_plate(self):
        """Draw one closed-eyelid cel inside the existing spectacle rims."""
        closed = self.reverse.copy()
        draw = ImageDraw.Draw(closed)
        draw.polygon([(379, 680), (390, 668), (411, 659), (426, 656), (438, 658), (447, 665),
                      (441, 680), (424, 690), (409, 694), (394, 691)], fill=(121, 91, 65))
        draw.line([(379, 680), (390, 682), (402, 684), (413, 683), (425, 679), (435, 673), (442, 666)],
                  fill=(52, 40, 33), width=3)
        draw.polygon([(505, 653), (516, 643), (527, 642), (532, 651), (532, 660), (526, 668), (506, 670)],
                     fill=(112, 83, 61))
        draw.line([(506, 655), (511, 658), (517, 658), (523, 656), (529, 652)], fill=(49, 37, 32), width=2)
        return closed

    @staticmethod
    def shift_patch(picture, bounds, dx, dy):
        """Move a small part of the drawing with a feather to carry adjacent outlines."""
        if abs(dx) + abs(dy) < 0.18:
            return picture
        patch = picture.crop(bounds)
        moved = patch.transform(patch.size, Image.Transform.AFFINE, (1, 0, -dx, 0, 1, -dy), Image.Resampling.BICUBIC)
        alpha = Image.new("L", patch.size)
        draw = ImageDraw.Draw(alpha)
        draw.rounded_rectangle((29, 29, patch.width - 29, patch.height - 29), radius=36, fill=255)
        alpha = alpha.filter(ImageFilter.GaussianBlur(15))
        picture = picture.copy()
        picture.paste(moved, bounds[:2], alpha)
        return picture

    def reaction(self, time, first):
        blink_at = 5.37 if first else 12.11
        blink = ease(blink_at - 0.095, blink_at - 0.015, time) * (1 - ease(blink_at + 0.025, blink_at + 0.14, time))
        picture = Image.blend(self.reverse, self.closed_eyes, blink) if blink else self.reverse
        if first:
            turn = ease(4.6, 5.04, time)
            return self.shift_patch(picture, (20, 360, 673, 1020), 3.7 * turn, -3.4 * turn)
        recoil = ease(11.49, 11.82, time) * (1 - ease(12.4, 13.35, time))
        return self.shift_patch(picture, (20, 360, 673, 1020), -5.4 * recoil, 4.3 * recoil)

    def paint_mirror(self, night_fraction):
        reflected = Image.blend(self.day, self.night, night_fraction)
        picture = self.wide.copy()
        picture.paste(reflected, self.mirror_bounds[:2], self.matte)
        return picture

    @staticmethod
    def reframe(picture, cx, cy, width):
        height = width * SIZE[1] / SIZE[0]
        left = min(max(0, cx - width / 2), picture.width - width)
        top = min(max(0, cy - height / 2), picture.height - height)
        return picture.resize(SIZE, Image.Resampling.BICUBIC, box=(left, top, left + width, top + height))

    def frame(self, time):
        if time < 4.55:
            push = ease(0, 4.55, time)
            settle = ease(0.15, 0.70, time)
            picture = self.shift_patch(self.daywide, (117, 1358, 283, 1591), 11 * settle, 10 * settle)
            return self.reframe(picture, 468 + 9 * push, 835 - 14 * push, 907 - 37 * push)
        if time < 7.48 or 11.49 <= time < 13.43:
            first_reaction = time < 7.48
            progress = ease(4.55, 7.48, time) if first_reaction else ease(11.49, 13.43, time)
            width = self.reverse.width * (0.94 if first_reaction else 0.84)
            picture = self.reaction(time, first_reaction)
            return self.reframe(picture, self.reverse.width * (.48 + .007 * progress),
                                self.reverse.height * (.49 - .007 * progress), width * (1 - .019 * progress))
        if time < 11.49:
            night_fraction = ease(8.28, 8.79, time)
            picture = self.paint_mirror(night_fraction)
            progress = ease(7.48, 11.49, time)
            return self.reframe(picture, 689 + 12 * progress, 498 - 8 * progress, 483 - 15 * progress)
        picture = self.paint_mirror(1)
        # Return to the photographed geography. The daylight outside the mirror still matches the opening shot.
        progress = ease(13.43, 15, time)
        result = self.reframe(picture, 488, 807 - 5 * progress, 861 - 9 * progress)
        return ImageEnhance.Brightness(result).enhance(1 - .018 * progress)


def render(output):
    with tempfile.TemporaryDirectory(prefix="5oclock-reel-") as tmp:
        local = Path(tmp)
        sound = local / "sound.wav"
        render_sound(sound)
        shot = Street()
        command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-n",
                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", str(FPS), "-i", "pipe:0",
                   "-i", str(sound), "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p",
                   "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                   "-vf", "scale=out_color_matrix=bt709", "-c:a", "aac", "-b:a", "256k", "-t", str(DURATION),
                   "-movflags", "+faststart", str(output)]
        with subprocess.Popen(command, stdin=subprocess.PIPE) as ffmpeg:
            for frame in range(DURATION * FPS):
                picture = shot.frame(frame / FPS)
                ffmpeg.stdin.write(picture.tobytes())
            ffmpeg.stdin.close()
            if ffmpeg.wait():
                raise RuntimeError("FFmpeg render failed")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        folder = Path(sys.argv[2])
        folder.mkdir(exist_ok=True)
        shot = Street()
        for timestamp in [1, 5, 7.75, 8.5, 9.6, 12, 14.0]:
            shot.frame(timestamp).resize((270, 480), Image.Resampling.LANCZOS).save(folder / f"{timestamp}.jpg", quality=93)
    else:
        render(Path(sys.argv[1]).resolve())
