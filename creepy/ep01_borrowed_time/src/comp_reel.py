import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT = Path(r"c:\Users\cross\Downloads\xc\creepy\ep01_borrowed_time")
ASSETS = ROOT / "assets"


def paint_charcoal_overlay(h: int, w: int, seed: int) -> np.ndarray:
    """Subtle organic paper/charcoal tooth pattern held on twos."""
    rng = np.random.default_rng(seed)
    coarse = rng.normal(0.0, 1.0, (h // 4, w // 4)).astype(np.float32)
    coarse_im = Image.fromarray(np.clip((coarse * 0.15 + 0.5) * 255, 0, 255).astype(np.uint8)).resize(
        (w, h), Image.Resampling.BILINEAR
    )
    fine = rng.normal(0.0, 1.0, (h, w)).astype(np.float32)
    tooth = (np.asarray(coarse_im, dtype=np.float32) / 255.0 - 0.5) * 0.7 + fine * 0.12
    # Add faint vertical scratch streaks
    for _ in range(45):
        x = int(rng.integers(0, w))
        y0 = int(rng.integers(0, h - 120))
        y1 = min(h, y0 + int(rng.integers(60, 240)))
        tooth[y0:y1, max(0, x - 1):min(w, x + 1)] -= 0.25
    return tooth


def make_dust_motes(h: int, w: int, n_motes: int = 34, seed: int = 77) -> list[tuple[float, float, float, float, float]]:
    rng = np.random.default_rng(seed)
    motes = []
    for _ in range(n_motes):
        # Focus motes in upper-to-mid crimson light cone (clear of girl's dark torso)
        x0 = float(rng.uniform(0.18, 0.85))
        y0 = float(rng.uniform(0.10, 0.56))
        vx = float(rng.choice([-1, 0, 1])) * 0.04
        vy = float(rng.choice([-1, 1])) * 0.06  # exact integer cycles over 9.0s -> seamless!
        r = float(rng.uniform(1.0, 2.2))
        amp = float(rng.uniform(0.020, 0.055))
        motes.append((x0, y0, vx, vy, r, amp))
    return motes


def process_frame(
    src_path: Path,
    dst_path: Path,
    frame_idx: int,
    total_frames: int,
    charcoal_a: np.ndarray,
    charcoal_b: np.ndarray,
    motes: list,
    clock_center: tuple[float, float],
) -> dict:
    im = Image.open(src_path).convert("RGB")
    arr = np.asarray(im, dtype=np.float32) / 255.0
    h, w, _ = arr.shape

    # Convert to working linear-ish energy for clean glow
    lin = np.power(np.clip(arr, 0.0, 1.0), 2.2)

    # 1. Crimson clock bloom + soft atmospheric halo
    # Emphasize red highlights (where R >> G, B) and pinpoint white eyes
    red_excess = np.clip(lin[:, :, 0] - 0.55 * (lin[:, :, 1] + lin[:, :, 2]), 0.0, 1.0)
    white_peak = np.clip(np.min(lin, axis=2) - 0.86, 0.0, 1.0)

    red_glow_tight = gaussian_filter(red_excess, sigma=max(4.0, w * 0.018))
    red_glow_wide = gaussian_filter(red_excess, sigma=max(12.0, w * 0.085))
    white_glow = gaussian_filter(white_peak, sigma=max(1.5, w * 0.005))

    lin[:, :, 0] += red_glow_tight * 0.52 + red_glow_wide * 0.34 + white_glow * 0.24
    lin[:, :, 1] += red_glow_tight * 0.03 + red_glow_wide * 0.015 + white_glow * 0.22
    lin[:, :, 2] += red_glow_tight * 0.02 + red_glow_wide * 0.015 + white_glow * 0.25

    # 2. Periodic seamless crimson dust motes inside the upper-to-mid clock light cone
    t_norm = ((frame_idx - 1) % total_frames) / float(total_frames)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xn = xx / float(w)
    yn = yy / float(h)
    cx, cy = clock_center
    cone_mask = np.exp(-(((xn - cx) / 0.34) ** 2 + ((yn - (cy + 0.06)) / 0.30) ** 2))

    dust_layer = np.zeros((h, w), dtype=np.float32)
    scale_r = w / 1080.0
    for idx_m, (x0, y0, vx, vy, r, amp) in enumerate(motes):
        # Periodic motion over t_norm in [0, 1) -> exact loop!
        mx = (x0 + 0.025 * np.sin(2.0 * np.pi * (t_norm + idx_m * 0.13)) + vx * np.sin(2.0 * np.pi * t_norm)) % 1.0
        my = (y0 - t_norm * (1.0 if idx_m % 2 == 0 else -1.0) * 0.08) % 1.0
        # Wait: linear wrap t_norm * 0.08 wouldn't match at 0 and 1 unless step is integer; use pure sinusoidal orbital drift for 100% seamlessness!
        mx = x0 + 0.030 * np.sin(2.0 * np.pi * (t_norm + idx_m * 0.17))
        my = y0 + 0.038 * np.cos(2.0 * np.pi * (t_norm + idx_m * 0.29))
        px = mx * w
        py = my * h
        rad = max(1.0, r * scale_r)
        x_lo, x_hi = max(0, int(px - rad * 3)), min(w, int(px + rad * 3) + 1)
        y_lo, y_hi = max(0, int(py - rad * 3)), min(h, int(py + rad * 3) + 1)
        if x_hi > x_lo and y_hi > y_lo:
            d2 = (xx[y_lo:y_hi, x_lo:x_hi] - px) ** 2 + (yy[y_lo:y_hi, x_lo:x_hi] - py) ** 2
            twinkle = 0.65 + 0.35 * np.sin(2.0 * np.pi * (2.0 * t_norm + idx_m * 0.37))
            dust_layer[y_lo:y_hi, x_lo:x_hi] += amp * twinkle * np.exp(-d2 / (2.0 * rad * rad))

    dust_vis = dust_layer * cone_mask
    lin[:, :, 0] += dust_vis * 0.85
    lin[:, :, 1] += dust_vis * 0.05
    lin[:, :, 2] += dust_vis * 0.04

    # Convert back to sRGB for grading, vignette, charcoal tooth, and grain
    srgb = np.power(np.clip(lin, 0.0, 1.0), 1.0 / 2.2)

    # 3. Subtle S-curve contrast keeping deep gothic blacks & rich midtones
    srgb = np.clip(srgb * 1.04 - 0.015 * np.sin(np.pi * np.clip(srgb, 0.0, 1.0) * 2.0) * 0.5, 0.0, 1.0)

    # 4. Hand-drawn charcoal tooth boil (held on twos, alternating smoothly)
    boil_idx = ((frame_idx - 1) // 2) % 2
    tooth = charcoal_a if boil_idx == 0 else charcoal_b
    # Apply mostly to midtones (not crushing shadows or white eyes)
    lum = 0.2126 * srgb[:, :, 0] + 0.7152 * srgb[:, :, 1] + 0.0722 * srgb[:, :, 2]
    mid_mask = np.clip(lum * 3.5, 0.0, 1.0) * np.clip(1.0 - lum * 0.9, 0.15, 1.0)
    srgb += (tooth[:, :, None] * 0.036) * mid_mask[:, :, None]

    # 5. Gothic radial vignette (keeps doorway & girl bottom-center clear, frames corners deeply)
    vx_n = (xn - 0.48) / 0.62
    vy_n = (yn - 0.44) / 0.68
    r2 = vx_n * vx_n + vy_n * vy_n
    vig = np.clip(1.0 - 0.40 * (r2 ** 1.35), 0.28, 1.0)
    srgb *= vig[:, :, None]

    # 6. Fine film grain (weighted slightly into shadows, velvety gothic finish)
    rng = np.random.default_rng(9000 + frame_idx)
    grain = rng.normal(0.0, 0.0075, (h, w, 1)).astype(np.float32)
    srgb = np.clip(srgb + grain, 0.0, 1.0)

    out_im = Image.fromarray((srgb * 255.0 + 0.5).astype(np.uint8), "RGB")
    out_im.save(dst_path)

    final_lum = 0.2126 * srgb[:, :, 0] + 0.7152 * srgb[:, :, 1] + 0.0722 * srgb[:, :, 2]
    return {
        "frame": frame_idx,
        "mean": float(final_lum.mean()),
        "p50": float(np.percentile(final_lum, 50)),
        "p95": float(np.percentile(final_lum, 95)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    ap.add_argument("--total", type=int, default=216)
    args = ap.parse_args()

    src_dir = Path(args.src)
    dst_dir = Path(args.dst)
    dst_dir.mkdir(parents=True, exist_ok=True)

    frames = sorted(src_dir.glob("*.png"))
    if not frames:
        raise SystemExit(f"No PNG frames in {src_dir}")

    sample_im = Image.open(frames[0])
    w, h = sample_im.size
    charcoal_a = paint_charcoal_overlay(h, w, seed=11)
    charcoal_b = paint_charcoal_overlay(h, w, seed=29)
    motes = make_dust_motes(h, w, n_motes=34, seed=77)
    clock_center = (0.52, 0.34)

    stats = []
    for p in frames:
        # Expect filename like f_0001.png or 0001.png
        digits = "".join(ch for ch in p.stem if ch.isdigit())
        fidx = int(digits) if digits else 1
        st = process_frame(p, dst_dir / p.name, fidx, args.total, charcoal_a, charcoal_b, motes, clock_center)
        stats.append(st)

    mean_avg = float(np.mean([s["mean"] for s in stats]))
    p95_avg = float(np.mean([s["p95"] for s in stats]))
    print(f"Composited {len(stats)} frames -> {dst_dir} | avg mean={mean_avg:.4f}, p95={p95_avg:.4f}")


if __name__ == "__main__":
    main()
