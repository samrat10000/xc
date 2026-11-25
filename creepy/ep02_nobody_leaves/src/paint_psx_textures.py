import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(r"c:\Users\cross\Downloads\xc\creepy\ep02_nobody_leaves")
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)


def get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\GARABD.TTF" if bold else r"C:\Windows\Fonts\GARA.TTF",
        r"C:\Windows\Fonts\georgiab.ttf",
        r"C:\Windows\Fonts\timesbd.ttf",
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
        gh = max(4, h // (2 ** (octaves + 1 - i)))
        gw = max(4, w // (2 ** (octaves + 1 - i)))
        grid = rng.random((gh, gw), dtype=np.float32)
        im = Image.fromarray((grid * 255).astype(np.uint8)).resize((w, h), Image.Resampling.BICUBIC)
        acc += (np.asarray(im, dtype=np.float32) / 255.0) * amp
        total += amp
        amp *= 0.5
    return np.clip(acc / total, 0.0, 1.0)


def paint_wall_plaster():
    """256x256 damp olive-beige/cold-grey apartment plaster with water leaks & baseboard grime."""
    S = 256
    n1 = fbm_noise(S, S, octaves=5, seed=101)
    n2 = fbm_noise(S, S, octaves=4, seed=102)
    streak_n = fbm_noise(64, S, octaves=4, seed=103)
    streak = np.asarray(
        Image.fromarray((streak_n * 255).astype(np.uint8)).resize((S, S), Image.Resampling.BILINEAR),
        dtype=np.float32,
    ) / 255.0

    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    yn = yy / float(S)

    # Sickly olive-beige/grey palette (#6C6E66 -> #262824)
    plaster = 0.25 + 0.16 * n1 + 0.07 * (n2 - 0.5)
    # Damp water-leak streaks from top
    top_damp = np.clip(1.0 - yn / 0.45, 0.0, 1.0) ** 1.4
    leak = np.clip((streak - 0.45) * 2.2, 0.0, 1.0) * top_damp * 0.14
    # Heavy baseboard grime at bottom
    bot_grime = (np.clip((yn - 0.72) / 0.28, 0.0, 1.0) ** 1.6) * 0.15
    lum = np.clip(plaster - leak - bot_grime, 0.08, 0.48)

    rgb = np.zeros((S, S, 3), dtype=np.float32)
    rgb[:, :, 0] = lum * 0.99
    rgb[:, :, 1] = lum * 1.01
    rgb[:, :, 2] = lum * 0.93

    # Subtle vertical wallpaper seam
    rgb[:, 126:129, :] *= 0.78
    rgb[:, 129:130, :] *= 1.08

    rng = np.random.default_rng(104)
    rgb = np.clip(rgb + rng.normal(0.0, 0.018, (S, S, 1)), 0.0, 1.0)
    im = Image.fromarray((rgb * 255).astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(im, "RGBA")
    for _ in range(45):
        x0 = float(rng.uniform(4, S - 4))
        y0 = float(rng.uniform(10, S - 20))
        dx = float(rng.uniform(-12, 12))
        dy = float(rng.uniform(15, 55))
        draw.line([(x0, y0), (x0 + dx, y0 + dy)], fill=(28, 30, 26, int(rng.integers(35, 95))), width=1)
    im.save(ASSETS / "psx_wall_plaster.png")


def paint_door_grimy():
    """256x512 filthy scratched 4-panel apartment door with brass knob, deadbolt, smudges & plate 04."""
    W, H = 256, 512
    n1 = fbm_noise(H, W, octaves=5, seed=201)
    grain_x = fbm_noise(H, 64, octaves=4, seed=202)
    grain = np.asarray(
        Image.fromarray((grain_x * 255).astype(np.uint8)).resize((W, H), Image.Resampling.BILINEAR),
        dtype=np.float32,
    ) / 255.0

    # Dirty peeling beige/grey paint (#59554B base)
    lum = np.clip(0.27 + 0.10 * n1 + 0.06 * (grain - 0.5), 0.10, 0.44)
    rgb = np.zeros((H, W, 3), dtype=np.float32)
    rgb[:, :, 0] = lum * 1.04
    rgb[:, :, 1] = lum * 0.99
    rgb[:, :, 2] = lum * 0.88

    # Edge wear & oil grime
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    edge_grime = np.clip((np.abs(xx - W / 2.0) / (W / 2.0) - 0.72) / 0.28, 0.0, 1.0)
    rgb *= (1.0 - 0.35 * edge_grime)[:, :, None]

    im = Image.fromarray((np.clip(rgb, 0.0, 1.0) * 255).astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(im, "RGBA")

    # 4 recessed door panels
    panels = [
        (32, 42, 114, 210),
        (142, 42, 224, 210),
        (32, 248, 114, 466),
        (142, 248, 224, 466),
    ]
    for x0, y0, x1, y1 in panels:
        draw.rectangle([x0, y0, x1, y1], fill=(56, 52, 45, 95), outline=(24, 22, 19, 215), width=4)
        draw.rectangle([x0 + 5, y0 + 5, x1 - 5, y1 - 5], outline=(98, 92, 82, 130), width=2)
        # Water/oil drip grime inside panel bottom
        for gx in range(x0 + 6, x1 - 6, 3):
            gh = int(10 + 18 * n1[y1 - 8, gx])
            draw.line([(gx, y1 - gh), (gx, y1 - 4)], fill=(25, 22, 18, 95), width=2)

    # Scratches & gouges across wood
    rng = np.random.default_rng(203)
    for _ in range(95):
        sx0 = float(rng.uniform(10, W - 10))
        sy0 = float(rng.uniform(15, H - 15))
        sx1 = sx0 + float(rng.uniform(-28, 28))
        sy1 = sy0 + float(rng.uniform(-14, 34))
        col = (20, 18, 15, int(rng.integers(55, 140))) if rng.random() < 0.7 else (115, 108, 96, 85)
        draw.line([(sx0, sy0), (sx1, sy1)], fill=col, width=int(rng.choice([1, 1, 2])))

    # Smudged dark handprint/streak near mid-right panel & knob
    smudge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(smudge, "RGBA")
    sd.ellipse([172, 215, 214, 268], fill=(18, 15, 12, 110))
    for fx, fy, fh in ((176, 196, 22), (186, 190, 26), (196, 193, 25), (206, 200, 20)):
        sd.line([(fx, fy + fh), (fx - 2, fy)], fill=(16, 14, 11, 125), width=4)
    smudge = smudge.filter(ImageFilter.GaussianBlur(radius=2.2))
    im = Image.alpha_composite(im.convert("RGBA"), smudge).convert("RGB")
    draw = ImageDraw.Draw(im, "RGBA")

    # Small tarnished brass room plate '04' near top center
    draw.rectangle([104, 16, 152, 36], fill=(92, 74, 42, 235), outline=(34, 26, 14, 250), width=2)
    font = get_font(16, bold=True)
    draw.text((117, 17), "04", font=font, fill=(22, 16, 10, 240))

    # Rusted deadbolt & weathered brass doorknob on right edge (front edge nearest camera!)
    draw.ellipse([220, 218, 238, 236], fill=(64, 36, 24, 240), outline=(22, 14, 10, 255), width=2)
    draw.ellipse([215, 246, 241, 272], fill=(122, 98, 54, 245), outline=(36, 26, 14, 255), width=2)
    draw.ellipse([221, 252, 235, 266], fill=(158, 130, 74, 240))

    im.save(ASSETS / "psx_door_grimy.png")


def paint_carpet_crimson():
    """256x256 deep rotting blood-burgundy carpet (#2E0505 -> #140202) with worn diamond weave."""
    S = 256
    n1 = fbm_noise(S, S, octaves=5, seed=301)
    n2 = fbm_noise(S, S, octaves=6, seed=302)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)

    # Worn vintage diamond runner weave
    diag_a = np.abs(np.sin((xx + yy) * 0.24))
    diag_b = np.abs(np.sin((xx - yy) * 0.24))
    weave = 0.025 * (diag_a * diag_b)

    stain = np.clip((n1 - 0.52) * 2.4, 0.0, 1.0) * 0.075
    r_ch = np.clip(0.16 + 0.07 * n2 + weave - stain, 0.04, 0.28)
    g_ch = np.clip(0.016 + 0.012 * n2 + weave * 0.2 - stain * 0.5, 0.004, 0.045)
    b_ch = np.clip(0.018 + 0.012 * n2 + weave * 0.2 - stain * 0.5, 0.004, 0.048)

    rng = np.random.default_rng(303)
    rgb = np.stack([r_ch, g_ch, b_ch], axis=-1)
    rgb = np.clip(rgb + rng.normal(0.0, 0.010, (S, S, 1)), 0.0, 1.0)
    Image.fromarray((rgb * 255).astype(np.uint8), "RGB").save(ASSETS / "psx_carpet_crimson.png")


def paint_ceiling_tile():
    """256x256 damp stained plaster ceiling (#52544E -> #1E201D) with irregular moisture blotches."""
    S = 256
    n1 = fbm_noise(S, S, octaves=5, seed=401)
    n2 = fbm_noise(S, S, octaves=5, seed=402)
    blotch = np.clip((n2 - 0.56) * 2.8, 0.0, 1.0) * 0.11
    lum = np.clip(0.24 + 0.11 * n1 - blotch, 0.08, 0.38)
    rgb = np.stack([lum * 0.99, lum * 1.01, lum * 0.95], axis=-1)
    im = Image.fromarray((rgb * 255).astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(im, "RGBA")
    draw.line([(45, 22), (82, 90), (118, 128), (154, 185)], fill=(20, 22, 18, 130), width=1)
    draw.line([(118, 128), (94, 178)], fill=(20, 22, 18, 95), width=1)
    im.save(ASSETS / "psx_ceiling_tile.png")


def paint_eye_seraph():
    """256x256 uncanny realistic-yet-pixelated human bloodshot eyeball -> assets/psx_eye_seraph.png."""
    S = 256
    cx, cy = S / 2.0, S / 2.0
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    dx, dy = xx - cx, yy - cy
    rr = np.sqrt(dx * dx + dy * dy) / (S * 0.5)
    theta = np.arctan2(dy, dx)

    n1 = fbm_noise(S, S, octaves=4, seed=501)
    n2 = fbm_noise(S, S, octaves=5, seed=502)

    ao = 1.0 - 0.80 * (np.clip((rr - 0.16) / 0.84, 0.0, 1.0) ** 1.3)
    mottle = (n1 - 0.5) * 0.11 + (n2 - 0.5) * 0.06
    # Muted bone-grey/ivory sclera #BDB5AC -> deep bruised edge
    sr = np.clip(0.74 * ao + mottle, 0.05, 0.82)
    sg = np.clip(0.71 * ao + mottle * 0.9, 0.04, 0.78)
    sb = np.clip(0.67 * ao + mottle * 0.8, 0.04, 0.74)

    img = Image.fromarray((np.stack([sr, sg, sb], axis=-1) * 255).astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    rng = np.random.default_rng(503)
    for vi in range(15):
        ang = (vi / 15.0) * 2.0 * math.pi + float(rng.uniform(-0.18, 0.18))
        r0 = float(rng.uniform(0.90, 1.0)) * (S * 0.5)
        r1 = float(rng.uniform(0.30, 0.46)) * (S * 0.5)
        pts = []
        ca = ang
        for st in range(10):
            f = st / 9.0
            rad_c = r0 * (1.0 - f) + r1 * f
            ca += float(rng.normal(0.0, 0.08))
            pts.append((cx + rad_c * math.cos(ca), cy + rad_c * math.sin(ca)))
        for st in range(9):
            draw.line([pts[st], pts[st + 1]], fill=(122, 18, 16, 155 if st < 5 else 95), width=2 if st < 3 else 1)

    arr = np.asarray(img, dtype=np.float32) / 255.0
    r_iris, r_pupil = 0.24, 0.085
    fiber = 0.5 + 0.30 * np.sin(theta * 34.0 + n1 * 4.0) + 0.20 * np.cos(theta * 64.0 - n2 * 4.5)
    iris_t = np.clip((rr - r_pupil) / (r_iris - r_pupil), 0.0, 1.0)
    # Smoky amber-crimson ringed iris
    ir_r = np.clip((0.44 + 0.22 * fiber) * (1.0 - 0.48 * iris_t ** 2), 0.08, 0.72)
    ir_g = np.clip((0.16 + 0.10 * fiber) * (1.0 - 0.55 * iris_t ** 1.8), 0.02, 0.30)
    ir_b = np.clip((0.06 + 0.04 * fiber) * (1.0 - 0.55 * iris_t ** 1.8), 0.01, 0.14)

    imask = np.clip(1.0 - (rr - r_iris) / 0.016, 0.0, 1.0) * np.clip((rr - (r_pupil - 0.008)) / 0.014, 0.0, 1.0)
    arr[:, :, 0] = arr[:, :, 0] * (1.0 - imask) + ir_r * imask
    arr[:, :, 1] = arr[:, :, 1] * (1.0 - imask) + ir_g * imask
    arr[:, :, 2] = arr[:, :, 2] * (1.0 - imask) + ir_b * imask

    lring = np.exp(-((rr - r_iris) / 0.014) ** 2)
    arr *= (1.0 - 0.72 * lring)[:, :, None]

    pmask = np.clip(1.0 - (rr - r_pupil) / 0.010, 0.0, 1.0)
    arr = arr * (1.0 - pmask)[:, :, None] + np.array([0.01, 0.008, 0.008])[None, None, :] * pmask[:, :, None]

    out = Image.fromarray((np.clip(arr, 0.0, 1.0) * 255).astype(np.uint8), "RGB")
    od = ImageDraw.Draw(out, "RGBA")
    od.ellipse([cx - 10, cy - 11, cx - 5, cy - 6], fill=(235, 240, 245, 200))
    out.save(ASSETS / "psx_eye_seraph.png")


def paint_star_flesh():
    """256x256 luminous pale ivory-bone veined petal texture (#FFF8E6 with golden-ochre striations)."""
    S = 256
    n1 = fbm_noise(S, S, octaves=5, seed=601)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    xn = (xx - S / 2.0) / (S * 0.5)
    yn = yy / float(S)

    # Vertical organic vein striations running along petal length (yn)
    vein = 0.5 + 0.5 * np.sin(xn * 22.0 + n1 * 5.5)
    edge_warm = np.clip(np.abs(xn), 0.0, 1.0) ** 1.4
    r_ch = np.clip(0.99 - 0.06 * edge_warm + 0.02 * (n1 - 0.5), 0.85, 1.0)
    g_ch = np.clip(0.95 - 0.16 * edge_warm - 0.05 * vein, 0.68, 0.99)
    b_ch = np.clip(0.86 - 0.24 * edge_warm - 0.08 * vein, 0.52, 0.94)

    rgb = np.stack([r_ch, g_ch, b_ch], axis=-1)
    Image.fromarray((rgb * 255).astype(np.uint8), "RGB").save(ASSETS / "psx_star_flesh.png")


def paint_note_wall():
    """128x128 peeling grimy yellow taped warning slip reading DO NOT / OPEN."""
    S = 128
    n1 = fbm_noise(S, S, octaves=4, seed=701)
    base = np.zeros((S, S, 3), dtype=np.float32)
    lum = 0.68 + 0.14 * (n1 - 0.5)
    base[:, :, 0] = np.clip(lum * 1.02, 0.0, 1.0)
    base[:, :, 1] = np.clip(lum * 0.94, 0.0, 1.0)
    base[:, :, 2] = np.clip(lum * 0.64, 0.0, 1.0)
    im = Image.fromarray((base * 255).astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(im, "RGBA")
    # Dark grimy edges + masking tape piece at top
    draw.rectangle([2, 2, S - 3, S - 3], outline=(42, 34, 24, 220), width=3)
    draw.polygon([(42, 0), (88, 0), (92, 18), (38, 18)], fill=(158, 145, 108, 215))
    font = get_font(23, bold=True)
    for li, word in enumerate(("DO NOT", "OPEN")):
        bbox = draw.textbbox((0, 0), word, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((S - tw) / 2 - bbox[0], 34 + li * 34 - bbox[1]), word, font=font, fill=(32, 12, 10, 235))
    im.save(ASSETS / "psx_note_wall.png")


def main():
    paint_wall_plaster()
    paint_door_grimy()
    paint_carpet_crimson()
    paint_ceiling_tile()
    paint_eye_seraph()
    paint_star_flesh()
    paint_note_wall()
    print(f"Painted 7 PSX textures in {ASSETS}")


if __name__ == "__main__":
    main()
