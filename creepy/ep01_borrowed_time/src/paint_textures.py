import argparse
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ASSETS_DIR = Path(r"c:\Users\cross\Downloads\xc\creepy\ep01_borrowed_time\assets")
CLOCKS_DIR = ASSETS_DIR / "clocks"
CLOCKS_DIR.mkdir(parents=True, exist_ok=True)


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\BASKVILL.TTF",
        r"C:\Windows\Fonts\georgiab.ttf" if bold else r"C:\Windows\Fonts\georgia.ttf",
        r"C:\Windows\Fonts\cambriab.ttf" if bold else r"C:\Windows\Fonts\cambria.ttc",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()


def fbm_noise(h: int, w: int, octaves: int = 5, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    acc = np.zeros((h, w), dtype=np.float32)
    amp = 1.0
    total = 0.0
    for i in range(octaves):
        gh = max(4, h // (2 ** (octaves + 2 - i)))
        gw = max(4, w // (2 ** (octaves + 2 - i)))
        grid = rng.random((gh, gw), dtype=np.float32)
        im = Image.fromarray((grid * 255).astype(np.uint8)).resize((w, h), Image.Resampling.BICUBIC)
        acc += (np.asarray(im, dtype=np.float32) / 255.0) * amp
        total += amp
        amp *= 0.5
    return np.clip(acc / total, 0.0, 1.0)


def paint_wall_charcoal():
    W, H = 2048, 2048
    n1 = fbm_noise(H, W, octaves=5, seed=101)
    n2 = fbm_noise(H, W, octaves=6, seed=202)
    rng = np.random.default_rng(303)

    # Cold slate plaster base (#4A484D approx)
    base = np.zeros((H, W, 3), dtype=np.float32)
    plaster = 0.24 + 0.11 * n1 + 0.06 * (n2 - 0.5)
    # Subtle damp stain patches
    stain = np.clip((n1 - 0.56) * 2.5, 0.0, 1.0)
    plaster -= 0.07 * stain
    base[:, :, 0] = plaster * 0.98
    base[:, :, 1] = plaster * 0.95
    base[:, :, 2] = plaster * 1.03

    # Subtle vertical wallpaper strip seams
    for sx in (340, 680, 1024, 1368, 1710):
        x0 = max(0, sx - 2)
        x1 = min(W, sx + 3)
        base[:, x0:x1, :] *= 0.86

    # Paper tooth grain
    grain = rng.normal(0.0, 0.018, (H, W, 1)).astype(np.float32)
    base = np.clip(base + grain, 0.0, 1.0)
    img = Image.fromarray((base * 255).astype(np.uint8), "RGB")

    # Hand-drawn uneven vertical charcoal scratch lines (like @puss_art_ but richer)
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(950):
        x = float(rng.uniform(20, W - 20))
        y0 = float(rng.uniform(0, H - 120))
        length = float(rng.uniform(60, 520))
        y1 = min(H - 1, y0 + length)
        segs = rng.integers(4, 9)
        pts = []
        cx = x
        for s in range(segs + 1):
            t = s / segs
            cx += float(rng.normal(0.0, 1.4))
            pts.append((cx, y0 + t * (y1 - y0)))
        darkness = int(rng.integers(10, 42))
        alpha = int(rng.integers(25, 95))
        width = int(rng.choice([1, 1, 2]))
        draw.line(pts, fill=(darkness, darkness - 2, darkness + 2, alpha), width=width)

    # Diagonal subtle cross-scratches near eye level / center
    for _ in range(180):
        x0 = float(rng.uniform(200, W - 200))
        y0 = float(rng.uniform(200, H - 200))
        dx = float(rng.uniform(-90, 90))
        dy = float(rng.uniform(40, 180))
        alpha = int(rng.integers(18, 55))
        draw.line([(x0, y0), (x0 + dx, y0 + dy)], fill=(18, 15, 20, alpha), width=1)

    img.save(ASSETS_DIR / "wall_charcoal.png")


def paint_floor_wood():
    W, H = 1024, 1024
    n1 = fbm_noise(H, W, octaves=5, seed=404)
    # Stretch horizontally for wood grain
    grain_x = fbm_noise(256, 1024, octaves=4, seed=505)
    grain_img = Image.fromarray((grain_x * 255).astype(np.uint8)).resize((W, H), Image.Resampling.BILINEAR)
    g = np.asarray(grain_img, dtype=np.float32) / 255.0

    base = np.zeros((H, W, 3), dtype=np.float32)
    lum = 0.08 + 0.05 * n1 + 0.04 * g
    base[:, :, 0] = lum * 1.15
    base[:, :, 1] = lum * 0.92
    base[:, :, 2] = lum * 0.95

    # Plank seams every 128 px
    for y in range(0, H, 128):
        base[y:y + 3, :, :] *= 0.35
        base[y + 3:y + 5, :, :] *= 1.15

    rng = np.random.default_rng(606)
    img = Image.fromarray((np.clip(base, 0.0, 1.0) * 255).astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    for p_idx in range(8):
        y0 = p_idx * 128
        jx = int(rng.integers(100, W - 100))
        draw.line([(jx, y0), (jx, min(H, y0 + 128))], fill=(8, 6, 7, 190), width=3)
    img.save(ASSETS_DIR / "floor_wood.png")


def paint_main_clock():
    S = 1024
    cx, cy = S / 2.0, S / 2.0
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (S * 0.5)

    n = fbm_noise(S, S, octaves=5, seed=707)
    # Rich radial crimson glow: bright vivid crimson inside, deep blood rim outside
    rad_falloff = np.clip(1.0 - 0.52 * (rr ** 1.7), 0.18, 1.0)
    # Subtle mottled parchment soot
    soot = 0.86 + 0.22 * (n - 0.5)
    r_ch = np.clip(0.96 * rad_falloff * soot, 0.0, 1.0)
    g_ch = np.clip(0.045 * (rad_falloff ** 2) * soot, 0.0, 1.0)
    b_ch = np.clip(0.04 * (rad_falloff ** 2) * soot, 0.0, 1.0)

    rgb = np.stack([r_ch, g_ch, b_ch], axis=-1)
    img = Image.fromarray((rgb * 255).astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    # Outer border ring & antique inner minute track
    draw.ellipse([24, 24, S - 24, S - 24], outline=(16, 2, 2, 240), width=18)
    draw.ellipse([78, 78, S - 78, S - 78], outline=(18, 3, 3, 210), width=5)
    draw.ellipse([110, 110, S - 110, S - 110], outline=(18, 3, 3, 180), width=3)

    # 60 minute ticks
    for m in range(60):
        ang = math.radians(m * 6.0 - 90.0)
        r0 = 402 if m % 5 == 0 else 414
        r1 = 432
        w = 6 if m % 5 == 0 else 2
        x0, y0 = cx + r0 * math.cos(ang), cy + r0 * math.sin(ang)
        x1, y1 = cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)
        draw.line([(x0, y0), (x1, y1)], fill=(14, 2, 2, 225), width=w)

    # Roman numerals
    numerals = ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
    font = get_font(86, bold=True)
    for i, num in enumerate(numerals):
        ang_deg = i * 30.0
        ang = math.radians(ang_deg - 90.0)
        rad = 326.0
        px = cx + rad * math.cos(ang)
        py = cy + rad * math.sin(ang)

        # Render numeral to temp image so we can rotate radially around the dial
        txt_im = Image.new("RGBA", (220, 140), (0, 0, 0, 0))
        td = ImageDraw.Draw(txt_im)
        bbox = td.textbbox((0, 0), num, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        td.text((110 - tw / 2 - bbox[0], 70 - th / 2 - bbox[1]), num, font=font, fill=(10, 2, 2, 240))
        # Rotate top-half numerals upright-radial, bottom-half flip readable
        rot_angle = -ang_deg
        rot_im = txt_im.rotate(rot_angle, resample=Image.Resampling.BICUBIC, expand=True)
        img.paste(rot_im, (int(px - rot_im.width / 2), int(py - rot_im.height / 2)), rot_im)

    # Subtle center rosette & faint hairline glass crack
    draw.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=(12, 2, 2, 245))
    crack_origin = (cx + 155, cy - 190)
    crack_rays = [
        [(0, 0), (-45, 55), (-115, 95), (-170, 170)],
        [(0, 0), (50, 35), (130, 50), (210, 95)],
        [(0, 0), (-15, -70), (-40, -155)],
        [(0, 0), (85, -45), (165, -80)],
    ]
    for ray in crack_rays:
        pts = [(crack_origin[0] + dx, crack_origin[1] + dy) for dx, dy in ray]
        draw.line(pts, fill=(10, 2, 2, 130), width=2)

    img.save(ASSETS_DIR / "clock_main_dial.png")


def paint_word_clock(filename: str, word: str, shape: str = "round", inverted_red: bool = False):
    S = 512
    cx, cy = S / 2.0, S / 2.0
    n = fbm_noise(S, S, octaves=4, seed=sum(ord(c) for c in word) + (99 if inverted_red else 1))
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (S * 0.5)

    base = np.zeros((S, S, 3), dtype=np.float32)
    if inverted_red:
        # Dark blood-charcoal dial for the hidden "DON'T TURN" flip
        lum = np.clip(0.14 - 0.06 * rr + 0.04 * (n - 0.5), 0.03, 0.22)
        base[:, :, 0] = lum * 1.65
        base[:, :, 1] = lum * 0.25
        base[:, :, 2] = lum * 0.25
        ink = (235, 22, 22, 245)
        border = (175, 14, 14, 240)
    else:
        # Aged cool bone/ash parchment dial
        lum = np.clip(0.62 - 0.16 * (rr ** 1.4) + 0.09 * (n - 0.5), 0.28, 0.78)
        base[:, :, 0] = lum * 0.99
        base[:, :, 1] = lum * 0.96
        base[:, :, 2] = lum * 1.00
        ink = (18, 14, 16, 235)
        border = (145, 16, 16, 235)

    img = Image.fromarray((np.clip(base, 0.0, 1.0) * 255).astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    if shape in ("round", "oval"):
        draw.ellipse([18, 18, S - 18, S - 18], outline=border, width=16)
        draw.ellipse([42, 42, S - 42, S - 42], outline=ink, width=3)
        for m in range(12):
            ang = math.radians(m * 30.0)
            x0, y0 = cx + 196 * math.cos(ang), cy + 196 * math.sin(ang)
            x1, y1 = cx + 210 * math.cos(ang), cy + 210 * math.sin(ang)
            draw.line([(x0, y0), (x1, y1)], fill=ink, width=3)
    else:
        draw.rectangle([18, 18, S - 18, S - 18], outline=border, width=16)
        draw.rectangle([42, 42, S - 42, S - 42], outline=ink, width=3)

    lines = word.split("\n")
    if len(lines) == 1 and len(word) >= 5 and word == "EMPTY":
        # Vertical stack like Reel 2's oval EMPTY clock
        font = get_font(64, bold=True)
        total_h = len(word) * 58
        sy = cy - total_h / 2
        for idx, ch in enumerate(word):
            bbox = draw.textbbox((0, 0), ch, font=font)
            cw, chh = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((cx - cw / 2 - bbox[0], sy + idx * 58), ch, font=font, fill=ink)
    elif len(lines) == 2:
        font = get_font(78, bold=True)
        for li, ln in enumerate(lines):
            bbox = draw.textbbox((0, 0), ln, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            yy_pos = cy - 75 + li * 88
            draw.text((cx - tw / 2 - bbox[0], yy_pos - bbox[1]), ln, font=font, fill=ink)
    else:
        fsize = 104 if len(word) <= 4 else 88
        font = get_font(fsize, bold=True)
        bbox = draw.textbbox((0, 0), word, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1]), word, font=font, fill=ink)

    # Subtle grime/scratch over text so it reads as painted on old dial
    rng = np.random.default_rng(sum(ord(c) for c in word) * 17)
    for _ in range(18):
        x0, y0 = float(rng.uniform(40, S - 40)), float(rng.uniform(40, S - 40))
        dx, dy = float(rng.uniform(-45, 45)), float(rng.uniform(-45, 45))
        draw.line([(x0, y0), (x0 + dx, y0 + dy)], fill=(25, 20, 22, 48), width=1)

    img.save(CLOCKS_DIR / filename)


def paint_horror_eye():
    """Paint a realistic, muted, bloodshot horror eyeball texture (512x512) -> assets/horror_eye.png."""
    S = 512
    cx, cy = S / 2.0, S / 2.0
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    dx = xx - cx
    dy = yy - cy
    rr = np.sqrt(dx * dx + dy * dy) / (S * 0.5)
    theta = np.arctan2(dy, dx)

    n1 = fbm_noise(S, S, octaves=5, seed=808)
    n2 = fbm_noise(S, S, octaves=6, seed=909)

    # 1. Muted dead-ivory / bruised-grey sclera with strong outer socket AO darkening
    ao = 1.0 - 0.78 * (np.clip((rr - 0.18) / 0.82, 0.0, 1.0) ** 1.35)
    # Center ~ #ABA09A (0.67, 0.63, 0.60) darkening to #251C1E (0.145, 0.11, 0.118)
    mottle = (n1 - 0.5) * 0.14 + (n2 - 0.5) * 0.08
    bruise = np.clip((n1 - 0.54) * 2.0, 0.0, 1.0) * 0.09
    sclera_r = np.clip((0.67 * ao + mottle - bruise * 0.3), 0.06, 0.76)
    sclera_g = np.clip((0.62 * ao + mottle - bruise * 0.9), 0.04, 0.70)
    sclera_b = np.clip((0.59 * ao + mottle - bruise * 0.6), 0.04, 0.68)

    # Faint pinkish-red irritation halo around outer sclera and near iris margin
    conjunctiva = np.clip((rr - 0.52) / 0.48, 0.0, 1.0) ** 1.4
    sclera_r = np.clip(sclera_r + conjunctiva * 0.10, 0.0, 1.0)
    sclera_g = np.clip(sclera_g - conjunctiva * 0.06, 0.0, 1.0)
    sclera_b = np.clip(sclera_b - conjunctiva * 0.07, 0.0, 1.0)

    rgb = np.stack([sclera_r, sclera_g, sclera_b], axis=-1)
    img = Image.fromarray((rgb * 255).astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    # 2. Realistic asymmetrical crimson-brown bloodshot capillary veins creeping inward (rr 0.96 -> 0.32)
    rng = np.random.default_rng(1337)
    for v_idx in range(17):
        ang = (v_idx / 17.0) * 2.0 * math.pi + float(rng.uniform(-0.16, 0.16))
        r_start = float(rng.uniform(0.92, 1.02)) * (S * 0.5)
        r_end = float(rng.uniform(0.32, 0.48)) * (S * 0.5)
        steps = 12
        pts = []
        cur_a = ang
        for st in range(steps + 1):
            frac = st / float(steps)
            rad_cur = r_start * (1.0 - frac) + r_end * frac
            cur_a += float(rng.normal(0.0, 0.075))
            pts.append((cx + rad_cur * math.cos(cur_a), cy + rad_cur * math.sin(cur_a)))

        for st in range(steps):
            w_line = 2 if st < 4 else 1
            col = (125, 18, 18, 165) if st < 7 else (155, 28, 28, 100)
            draw.line([pts[st], pts[st + 1]], fill=col, width=w_line)

            # Secondary fork capillaries
            if st in (3, 6, 8) and rng.random() < 0.72:
                fork_pts = [pts[st]]
                fa = cur_a + float(rng.choice([-1, 1])) * float(rng.uniform(0.28, 0.58))
                fr0 = math.hypot(pts[st][0] - cx, pts[st][1] - cy)
                for fst in range(1, 5):
                    ffrac = fst / 4.0
                    fr = fr0 * (1.0 - 0.30 * ffrac)
                    fa += float(rng.normal(0.0, 0.11))
                    fork_pts.append((cx + fr * math.cos(fa), cy + fr * math.sin(fa)))
                draw.line(fork_pts, fill=(148, 24, 24, 95), width=1)

    # Slight soft blur pass on veins blended back so capillaries look beneath moist sclera
    arr_veins = np.asarray(img, dtype=np.float32) / 255.0
    blurred_veins = np.asarray(img.filter(ImageFilter.GaussianBlur(radius=0.8)), dtype=np.float32) / 255.0
    arr = np.clip(arr_veins * 0.65 + blurred_veins * 0.35, 0.0, 1.0)

    # 3. Small, hyper-focused uncanny iris & pinpoint pupil (radius ~0.25 of half-size = ~64px)
    r_limbal = 0.255
    r_iris_outer = 0.240
    r_pupil = 0.085

    # Radial iris fibers: smoky desiccated oxblood / dark crimson-brown
    ang_norm = (theta + math.pi) / (2.0 * math.pi)
    fiber = (
        0.5
        + 0.32 * np.sin(theta * 37.0 + n1 * 4.5)
        + 0.18 * np.cos(theta * 73.0 - n2 * 5.0)
    )
    iris_t = np.clip((rr - r_pupil) / max(1e-5, (r_iris_outer - r_pupil)), 0.0, 1.0)
    # Dark inner collarette & dark outer limbal ring
    collarette = np.exp(-((iris_t - 0.28) / 0.14) ** 2) * 0.25
    iris_r = np.clip((0.36 + 0.23 * fiber + collarette) * (1.0 - 0.55 * (iris_t ** 2.2)), 0.05, 0.64)
    iris_g = np.clip((0.055 + 0.050 * fiber) * (1.0 - 0.50 * (iris_t ** 2.0)), 0.01, 0.16)
    iris_b = np.clip((0.050 + 0.042 * fiber) * (1.0 - 0.50 * (iris_t ** 2.0)), 0.01, 0.14)

    # Subtle shadow feathering just outside limbal ring
    limbal_shadow = np.exp(-((rr - r_limbal) / 0.024) ** 2) * 0.52
    arr[:, :, 0] *= (1.0 - limbal_shadow)
    arr[:, :, 1] *= (1.0 - limbal_shadow)
    arr[:, :, 2] *= (1.0 - limbal_shadow)

    # Smooth mask for iris & limbal edge
    iris_mask = np.clip(1.0 - (rr - r_iris_outer) / 0.014, 0.0, 1.0) * np.clip((rr - (r_pupil - 0.008)) / 0.012, 0.0, 1.0)
    arr[:, :, 0] = arr[:, :, 0] * (1.0 - iris_mask) + iris_r * iris_mask
    arr[:, :, 1] = arr[:, :, 1] * (1.0 - iris_mask) + iris_g * iris_mask
    arr[:, :, 2] = arr[:, :, 2] * (1.0 - iris_mask) + iris_b * iris_mask

    # Crisp dark limbal ring
    limbal_ring = np.exp(-((rr - r_iris_outer) / 0.011) ** 2)
    arr *= (1.0 - 0.68 * limbal_ring)[:, :, None]

    # Tiny sharp pitch-black pinpoint pupil
    pupil_mask = np.clip(1.0 - (rr - r_pupil) / 0.008, 0.0, 1.0)
    arr[:, :, 0] = arr[:, :, 0] * (1.0 - pupil_mask) + 0.008 * pupil_mask
    arr[:, :, 1] = arr[:, :, 1] * (1.0 - pupil_mask) + 0.006 * pupil_mask
    arr[:, :, 2] = arr[:, :, 2] * (1.0 - pupil_mask) + 0.007 * pupil_mask

    out_img = Image.fromarray((np.clip(arr, 0.0, 1.0) * 255).astype(np.uint8), "RGB")
    out_draw = ImageDraw.Draw(out_img, "RGBA")
    # Tiny restrained cold-white wet corneal specular dot upper-left (zero bloom)
    sx, sy, sr_dot = cx - 14.0, cy - 16.0, 5.0
    out_draw.ellipse([sx - sr_dot, sy - sr_dot, sx + sr_dot, sy + sr_dot], fill=(225, 232, 240, 190))

    out_img.save(ASSETS_DIR / "horror_eye.png")
    print(f"Painted horror eye texture -> {ASSETS_DIR / 'horror_eye.png'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eye-only", action="store_true", help="Only generate horror_eye.png")
    args = ap.parse_args()
    if args.eye_only:
        paint_horror_eye()
        return

    paint_wall_charcoal()
    paint_floor_wood()
    paint_main_clock()
    word_specs = [
        ("clock_LOST.png", "LOST", "round", False),
        ("clock_FADE.png", "FADE", "round", False),
        ("clock_WAIT.png", "WAIT", "square", False),
        ("clock_EMPTY.png", "EMPTY", "oval", False),
        ("clock_STILL.png", "STILL", "square", False),
        ("clock_ALONE.png", "ALONE", "square", False),
        ("clock_LATE.png", "LATE", "round", False),
        ("clock_OFF.png", "OFF", "square", False),
        ("clock_HUSH.png", "HUSH", "round", False),
        ("clock_STAY.png", "STAY", "square", False),
        ("clock_DONT_TURN.png", "DON'T\nTURN", "square", True),
    ]
    for fname, word, shape, inv in word_specs:
        paint_word_clock(fname, word, shape, inv)
    paint_horror_eye()
    print(f"Painted wall, floor, main clock, horror eye, and {len(word_specs)} word-clock dials in {ASSETS_DIR}")


if __name__ == "__main__":
    main()
