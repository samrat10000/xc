"""Generate Shot 01 RGBA textures (system Python PIL/numpy) before Blender build (ERROR_CATALOG K4)."""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TEXD = os.path.join(HERE, "textures")
os.makedirs(TEXD, exist_ok=True)


def make_glass_handprint():
    """Create 512x1126 RGBA condensation + pressed handprint matching 0.50m x 1.10m glass aspect."""
    W, H = 512, 1126
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u, v = xx / W, yy / H
    cx, cy = 0.52, 0.54
    dx = (u - cx) / 0.36
    dy = (v - cy) / 0.18
    dist = np.sqrt(dx * dx + dy * dy)
    fog = np.clip(1.0 - dist, 0.0, 1.0) ** 1.35

    rng = np.random.default_rng(301)
    n_lo = rng.normal(0.0, 1.0, (32, 32)).astype(np.float32)
    n_lo_img = Image.fromarray(((n_lo * 0.25 + 0.5).clip(0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    noise = (np.asarray(n_lo_img, dtype=np.float32) / 255.0 - 0.5) * 0.45
    fog = np.clip(fog * (0.88 + noise), 0.0, 1.0)

    hand_im = Image.new("L", (W, H), 0)
    hd = ImageDraw.Draw(hand_im)
    S = 0.56  # isotropic pixel scale so hand proportions are realistic human anatomy

    def rot(px, py, ang=-8):
        rad = math.radians(ang)
        rx = cx * W + (px - cx * W) * math.cos(rad) - (py - cy * H) * math.sin(rad)
        ry = cy * H + (px - cx * W) * math.sin(rad) + (py - cy * H) * math.cos(rad)
        return rx, ry

    def draw_capsule(draw, p0, p1, r0, r1, fill=255):
        steps = 28
        for i in range(steps + 1):
            t = i / steps
            x = p0[0] * (1 - t) + p1[0] * t
            y = p0[1] * (1 - t) + p1[1] * t
            r = r0 * (1 - t) + r1 * t
            draw.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    px0, py0 = cx * W, cy * H + 40 * S
    draw_capsule(hd, rot(px0 - 22 * S, py0 + 60 * S), rot(px0 - 10 * S, py0 - 70 * S), 58 * S, 72 * S, 255)
    draw_capsule(hd, rot(px0 + 26 * S, py0 + 55 * S), rot(px0 + 38 * S, py0 - 65 * S), 54 * S, 68 * S, 255)
    hd.ellipse([px0 - 68 * S, py0 + 18 * S, px0 + 78 * S, py0 + 145 * S], fill=255)

    fingers = [
        ((-78, -58), (-118, -182), 18, 15),
        ((-36, -74), (-52, -238), 21, 17),
        ((8, -80), (6, -264), 22, 18),
        ((52, -70), (74, -232), 21, 17),
        ((72, 24), (168, -68), 26, 20),
    ]
    for (ox0, oy0), (ox1, oy1), r0, r1 in fingers:
        p0 = rot(px0 + ox0 * S, py0 + oy0 * S)
        p1 = rot(px0 + ox1 * S, py0 + oy1 * S)
        draw_capsule(hd, p0, p1, r0 * S, r1 * S, 255)

    hand_soft = np.asarray(hand_im.filter(ImageFilter.GaussianBlur(radius=3.0)), dtype=np.float32) / 255.0
    hand_halo = np.asarray(hand_im.filter(ImageFilter.GaussianBlur(radius=14.0)), dtype=np.float32) / 255.0

    edge_ridge = np.clip(hand_halo - hand_soft * 0.65, 0.0, 1.0) * 1.65
    alpha = np.clip(0.02 + fog * 0.25 + edge_ridge * 0.45 + hand_soft * 0.34, 0.0, 0.85)
    bottom_dust = np.clip((v - 0.90) / 0.10, 0.0, 1.0) * 0.12
    alpha = np.clip(alpha + bottom_dust, 0.0, 0.88)

    r_ch = 0.88 - hand_soft * 0.36
    g_ch = 0.92 - hand_soft * 0.32
    b_ch = 0.98 - hand_soft * 0.24
    rgba = np.stack([
        np.clip(r_ch * 255, 0, 255),
        np.clip(g_ch * 255, 0, 255),
        np.clip(b_ch * 255, 0, 255),
        np.clip(alpha * 255, 0, 255),
    ], axis=-1).astype(np.uint8)
    out = os.path.join(TEXD, "glass_handprint.png")
    Image.fromarray(rgba, "RGBA").save(out)
    print("WROTE", out)


def make_koban_sign_rev():
    """Create mirrored Japanese koban placard texture (霧山交番 reversed horizontally)."""
    W, H = 512, 1024
    im = Image.new("RGBA", (W, H), (226, 222, 210, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([16, 16, W - 16, H - 16], outline=(35, 32, 38, 255), width=12)
    d.ellipse([156, 56, 356, 256], fill=(182, 38, 34, 255), outline=(28, 24, 28, 255), width=6)
    d.ellipse([204, 104, 308, 208], fill=(226, 222, 210, 255))
    font_path = next((p for p in ("C:/Windows/Fonts/YuGothB.ttc", "C:/Windows/Fonts/msgothic.ttc") if os.path.exists(p)), None)
    fnt = ImageFont.truetype(font_path, 130) if font_path else ImageFont.load_default()
    for idx, ch in enumerate("霧山交番"):
        d.text((190, 310 + idx * 155), ch, fill=(28, 26, 32, 255), font=fnt)
    im = im.transpose(Image.FLIP_LEFT_RIGHT)
    out = os.path.join(TEXD, "koban_sign_rev.png")
    im.save(out)
    print("WROTE", out)


if __name__ == "__main__":
    make_glass_handprint()
    make_koban_sign_rev()
