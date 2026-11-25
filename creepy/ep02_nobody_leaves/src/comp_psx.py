import argparse
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter

ROOT = Path(r"c:\Users\cross\Downloads\xc\creepy\ep02_nobody_leaves")
ASSETS = ROOT / "assets"

FPS = 24
TOTAL_FRAMES = 288

# Exact dialogue beats matching Reel 1 rhythm with clean visual breathing space
DIALOGUE_LINES = [
    {"id": 1, "start_f": 21, "end_f": 110, "cps": 0.74, "text": "What are you looking for?", "is_red": False},
    {"id": 2, "start_f": 117, "end_f": 198, "cps": 0.84, "text": "Very brave of you\nto come here...", "is_red": False},
    {"id": 3, "start_f": 202, "end_f": 288, "cps": 0.75, "text": "But nobody ever leaves.", "is_red": True},
]

BAYER_4X4 = (
    np.array([
        [0, 8, 2, 10],
        [12, 4, 14, 6],
        [3, 11, 1, 9],
        [15, 7, 13, 5],
    ], dtype=np.float32) / 16.0 - 0.5
)


def get_serif_font(size: int = 24) -> ImageFont.FreeTypeFont:
    for p in (r"C:\Windows\Fonts\GARABD.TTF", r"C:\Windows\Fonts\georgiab.ttf", r"C:\Windows\Fonts\timesbd.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()


def build_typewriter_events() -> list[dict]:
    """Export sample-accurate character-reveal timestamps across frames 1..288."""
    events = []
    for line in DIALOGUE_LINES:
        txt = line["text"]
        sf = line["start_f"]
        cps = line["cps"]
        prev_n = 0
        # Walk at sub-frame resolution so multiple fast chars get exact distinct timestamps
        max_chars = len(txt)
        for ci in range(max_chars):
            ch = txt[ci]
            reveal_f = sf + ci / cps
            if reveal_f <= line["end_f"] and ch not in (" ", "\n"):
                events.append({
                    "line_id": line["id"],
                    "char": ch,
                    "frame": reveal_f,
                    "time_sec": round((reveal_f - 1.0) / float(FPS), 4),
                    "is_red": line["is_red"],
                })
    (ASSETS / "typewriter_events.json").write_text(json.dumps(events, indent=2), encoding="utf-8")
    return events


def visible_text_at_frame(frame: int):
    for line in DIALOGUE_LINES:
        if line["start_f"] <= frame <= line["end_f"]:
            n_chars = min(len(line["text"]), int((frame - line["start_f"]) * line["cps"]) + 1)
            return line["text"][:n_chars], line["is_red"], line["id"]
    return "", False, 0


def render_pixel_dialogue_overlay(frame: int, font: ImageFont.FreeTypeFont) -> np.ndarray | None:
    """Render glowing pixelated serif text at 360x640 -> 3x NEAREST upscale onto 1080x1920."""
    vis_txt, is_red, _lid = visible_text_at_frame(frame)
    if not vis_txt:
        return None

    LW, LH = 360, 640
    layer = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    lines = vis_txt.split("\n")

    # Determine full line target dimensions so centered text doesn't wiggle horizontally as it types!
    full_lines = next(l["text"] for l in DIALOGUE_LINES if visible_text_at_frame(frame)[2] == l["id"]).split("\n")
    line_heights = []
    full_widths = []
    for fl in full_lines:
        bb = draw.textbbox((0, 0), fl, font=font)
        full_widths.append(bb[2] - bb[0])
        line_heights.append(bb[3] - bb[1] + 6)

    # Strictly inside Instagram safe zone: y around 82%–88% of frame height!
    y_start = int(LH * 0.835) - (len(full_lines) - 1) * 14
    main_col = (255, 24, 24, 255) if is_red else (248, 245, 236, 255)
    glow_col = (230, 12, 12, 230) if is_red else (240, 236, 224, 155)

    for li, partial in enumerate(lines):
        # Anchor each line cleanly from the left X where the full centered line begins!
        full_w = full_widths[li] if li < len(full_widths) else 100
        x0 = (LW - full_w) // 2
        y0 = y_start + li * 28
        # Subtle dark backdrop drop-shadow for guaranteed legibility
        draw.text((x0 + 1, y0 + 1), partial, font=font, fill=(6, 2, 2, 220))
        draw.text((x0, y0), partial, font=font, fill=main_col)

    # Low-res glow halo at 360x640 with subtle menacing Beat 3 crimson pulse
    glow_src = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_src, "RGBA")
    for li, partial in enumerate(lines):
        full_w = full_widths[li] if li < len(full_widths) else 100
        x0 = (LW - full_w) // 2
        y0 = y_start + li * 28
        gd.text((x0, y0), partial, font=font, fill=glow_col)
    pulse_r = (3.5 + 0.55 * math.sin(max(0, frame - 202) * 0.45)) if is_red else 2.2
    glow_blur = glow_src.filter(ImageFilter.GaussianBlur(radius=pulse_r))

    combined = Image.alpha_composite(glow_blur, layer)
    up = combined.resize((1080, 1920), Image.Resampling.NEAREST)
    arr_up = np.asarray(up, dtype=np.float32) / 255.0
    if is_red:
        pulse_gain = 1.0 + 0.12 * math.sin(max(0, frame - 202) * 0.45)
        arr_up[:, :, :3] = np.clip(arr_up[:, :, :3] * pulse_gain, 0.0, 1.0)
    return arr_up


def process_frame(src_path: Path, dst_path: Path, frame_idx: int, font: ImageFont.FreeTypeFont):
    im = Image.open(src_path).convert("RGB")
    # Ensure exact native 270x480 working resolution
    if im.size != (270, 480):
        im = im.resize((270, 480), Image.Resampling.NEAREST)
    arr = np.asarray(im, dtype=np.float32) / 255.0
    h, w, _ = arr.shape

    # 1. PSX Directional Fog-Glow Bloom (warm white in Beats 1-2, crimson in Beat 3)
    lin = np.power(np.clip(arr, 0.0, 1.0), 2.2)
    lum = 0.2126 * lin[:, :, 0] + 0.7152 * lin[:, :, 1] + 0.0722 * lin[:, :, 2]
    bright = np.clip(lum - 0.35, 0.0, 2.0)[:, :, None] * lin
    red_excess = np.clip(lin[:, :, 0] - 0.55 * (lin[:, :, 1] + lin[:, :, 2]), 0.0, 1.5)

    bloom = np.zeros_like(lin)
    for c in range(3):
        bloom[:, :, c] = gaussian_filter(bright[:, :, c], sigma=5.0) * 0.65 + gaussian_filter(bright[:, :, c], sigma=19.0) * 0.48
    bloom[:, :, 0] += gaussian_filter(red_excess, sigma=8.0) * 0.38
    lin = np.clip(lin + bloom, 0.0, 1.0)
    srgb = np.power(lin, 1.0 / 2.2)

    # 2. Authentic PS1 4x4 Bayer Ordered Dithering + RGB Quantization (attenuated near black for silky shadow ramps)
    bayer_tile = np.tile(BAYER_4X4, (h // 4 + 1, w // 4 + 1))[:h, :w, None]
    levels = 40.0
    dither_w = np.clip(srgb * 4.0, 0.20, 1.0)
    quant = np.floor(np.clip(srgb + bayer_tile * (0.45 / levels) * dither_w, 0.0, 1.0) * levels + 0.5) / levels

    # 3. 4x Nearest-Neighbor Upscale (270x480 -> 1080x1920 crisp stepped PS1 pixels!)
    up_im = Image.fromarray((np.clip(quant, 0.0, 1.0) * 255).astype(np.uint8), "RGB").resize((1080, 1920), Image.Resampling.NEAREST)
    hi = np.asarray(up_im, dtype=np.float32) / 255.0

    # 4. Subtle Chromatic Aberration (spikes on door slam f203-208 and ending tape glitch f280-286)
    ca_px = 2
    if 203 <= frame_idx <= 208 or 280 <= frame_idx <= 286:
        ca_px = 5
    hi[:, :, 0] = np.roll(hi[:, :, 0], -ca_px, axis=1)
    hi[:, :, 2] = np.roll(hi[:, :, 2], ca_px, axis=1)

    # Door-slam VHS tracking tear (f204-205) + ending micro horizontal tracking glitch (f282-f285)
    if frame_idx in (204, 205):
        y_b = 580 + (frame_idx - 204) * 340
        hi[y_b:y_b + 36, :, :] = np.roll(hi[y_b:y_b + 36, :, :], 22 * (1 if frame_idx == 204 else -1), axis=1)
    if 282 <= frame_idx <= 285:
        y_band0 = 420 + (frame_idx - 282) * 220
        hi[y_band0:y_band0 + 28, :, :] = np.roll(hi[y_band0:y_band0 + 28, :, :], 18 * (1 if frame_idx % 2 == 0 else -1), axis=1)

    # 5. Subtle CRT Scanlines (~4% modulation every 4px matching 4x pixel scale)
    yy = np.arange(1920, dtype=np.float32)[:, None, None]
    scan = 1.0 - 0.045 * (0.5 - 0.5 * np.cos(yy * math.pi * 0.5))
    hi *= scan

    # 6. Oppressive Deep Radial Vignette (keeps star-head, door, and safe-zone dialogue crisp)
    yn_g, xn_g = np.mgrid[0:1920, 0:1080].astype(np.float32)
    xn_g = (xn_g / 1080.0 - 0.50) / 0.62
    yn_g = (yn_g / 1920.0 - 0.48) / 0.65
    vig = np.clip(1.0 - 0.42 * ((xn_g ** 2 + yn_g ** 2) ** 1.45), 0.28, 1.0)
    hi *= vig[:, :, None]

    # 7. Composite Pixelated Glowing Serif Typewriter Dialogue cleanly on top
    ov = render_pixel_dialogue_overlay(frame_idx, font)
    if ov is not None:
        alpha = ov[:, :, 3:4]
        hi = np.clip(hi * (1.0 - alpha) + ov[:, :, :3] * alpha + ov[:, :, :3] * alpha * 0.25, 0.0, 1.0)

    Image.fromarray((hi * 255.0 + 0.5).astype(np.uint8), "RGB").save(dst_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    ap.add_argument("--total", type=int, default=TOTAL_FRAMES)
    args = ap.parse_args()

    build_typewriter_events()
    font = get_serif_font(23)

    src_dir = Path(args.src)
    dst_dir = Path(args.dst)
    dst_dir.mkdir(parents=True, exist_ok=True)

    frames = sorted(src_dir.glob("*.png"))
    if not frames:
        raise SystemExit(f"No PNG frames in {src_dir}")

    for p in frames:
        digits = "".join(c for c in p.stem if c.isdigit())
        fidx = int(digits) if digits else 1
        process_frame(p, dst_dir / p.name, fidx, font)

    print(f"PSX Composited {len(frames)} frames (1080x1920) -> {dst_dir} + exported typewriter_events.json")


if __name__ == "__main__":
    main()
