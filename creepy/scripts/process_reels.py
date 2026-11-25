import json
import re
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REELS = [
    {
        "dir": Path(r"c:\Users\cross\Downloads\xc\creepy\references\reel1_DeeVNnAu_C0"),
        "name": "reel1",
        "expected_dur": 11.6,
    },
    {
        "dir": Path(r"c:\Users\cross\Downloads\xc\creepy\references\reel2_DZC5NnpIwXe"),
        "name": "reel2",
        "expected_dur": 7.9,
    },
]


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def probe_json(path: Path) -> dict | None:
    if not path.exists() or path.stat().st_size < 1000:
        return None
    res = run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    if res.returncode != 0:
        return None
    try:
        return json.loads(res.stdout)
    except Exception:
        return None


def make_contact_sheet(frames_info: list[tuple[Path, str]], out_path: Path, cols: int = 5):
    if not frames_info:
        return
    thumbs = []
    thumb_w, thumb_h = 270, 480
    for p, label in frames_info:
        im = Image.open(p).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(im)
        # Draw dark pill at top-left for crisp timestamp legibility
        draw.rectangle([8, 8, 130, 38], fill=(0, 0, 0))
        draw.text((14, 14), label, fill=(255, 235, 120))
        thumbs.append(im)

    rows = (len(thumbs) + cols - 1) // cols
    pad = 8
    sheet = Image.new("RGB", (cols * thumb_w + (cols + 1) * pad, rows * thumb_h + (rows + 1) * pad), (18, 18, 22))
    for i, im in enumerate(thumbs):
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + pad)
        sheet.paste(im, (x, y))
    sheet.save(out_path)


def process_reel(cfg: dict):
    d = cfg["dir"]
    name = cfg["name"]
    final_mp4 = d / f"{name}.mp4"
    dash_v = d / "dash_video.mp4"
    dash_a = d / "dash_audio.mp4"
    prog = d / "progressive.mp4"

    # Remove corrupt fragment from earlier step if present
    if final_mp4.exists() and probe_json(final_mp4) is None:
        final_mp4.unlink()

    v_info = probe_json(dash_v)
    a_info = probe_json(dash_a)
    p_info = probe_json(prog)

    chosen_source = None
    if v_info and a_info:
        # Mux full 1080p VP9 + HE-AAC into clean H.264 + AAC MP4
        cmd = [
            "ffmpeg", "-y",
            "-i", str(dash_v),
            "-i", str(dash_a),
            "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            str(final_mp4),
        ]
        res = run(cmd)
        if res.returncode == 0 and probe_json(final_mp4):
            chosen_source = "dash_1080p_muxed"
    if chosen_source is None and p_info:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(prog),
            "-c", "copy",
            "-movflags", "+faststart",
            str(final_mp4),
        ]
        res = run(cmd)
        if res.returncode == 0 and probe_json(final_mp4):
            chosen_source = "progressive_720p"

    if chosen_source is None:
        raise RuntimeError(f"No valid video stream available for {name}")

    # Clean up temporary download artifacts once final_mp4 is verified
    for tmp in (dash_v, dash_a, prog):
        if tmp.exists():
            tmp.unlink()

    # Probe final mp4
    ffp_txt = run(["ffprobe", "-hide_banner", "-show_format", "-show_streams", str(final_mp4)]).stdout
    info = probe_json(final_mp4)
    duration = float(info["format"]["duration"])

    # Extract audio.mp3
    audio_mp3 = d / "audio.mp3"
    run(["ffmpeg", "-y", "-i", str(final_mp4), "-vn", "-c:a", "libmp3lame", "-b:a", "192k", str(audio_mp3)])

    # Audio profiling
    vol = run(["ffmpeg", "-i", str(final_mp4), "-af", "volumedetect", "-f", "null", "NUL"])
    ebur = run(["ffmpeg", "-i", str(final_mp4), "-af", "ebur128=peak=true", "-f", "null", "NUL"])
    sil = run(["ffmpeg", "-i", str(final_mp4), "-af", "silencedetect=noise=-35dB:d=0.25", "-f", "null", "NUL"])

    vol_lines = [ln for ln in vol.stderr.splitlines() if "Parsed_volumedetect" in ln]
    ebur_lines = [ln for ln in ebur.stderr.splitlines() if ("Summary:" in ln or "I:" in ln or "LRA:" in ln or "Peak:" in ln or "Threshold:" in ln)]
    sil_lines = [ln for ln in sil.stderr.splitlines() if "silence_" in ln]

    tech_report = [
        f"Source: {chosen_source}",
        "=== FFPROBE ===",
        ffp_txt.strip(),
        "",
        "=== VOLUMEDETECT ===",
        "\n".join(vol_lines),
        "",
        "=== EBUR128 ===",
        "\n".join(ebur_lines[-12:]),
        "",
        "=== SILENCEDETECT (-35dB, >=0.25s) ===",
        "\n".join(sil_lines) if sil_lines else "(none)",
        "",
    ]
    (d / "tech_specs.txt").write_text("\n".join(tech_report), encoding="utf-8")

    # Clear old frames
    frames_dir = d / "frames"
    for f in frames_dir.glob("*.png"):
        f.unlink()

    # Periodic sampling every 0.5s
    periodic_info = []
    t = 0.0
    idx = 1
    while t < duration - 0.05:
        out_f = frames_dir / f"t_{idx:03d}_{t:05.2f}s.png"
        run(["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", str(final_mp4), "-frames:v", "1", str(out_f)])
        if out_f.exists():
            periodic_info.append((out_f, f"{t:05.2f}s"))
        t += 0.5
        idx += 1

    # Exact final frame (duration - 0.04s)
    end_t = max(0.0, duration - 0.04)
    end_f = frames_dir / f"t_end_{end_t:05.2f}s.png"
    run(["ffmpeg", "-y", "-ss", f"{end_t:.3f}", "-i", str(final_mp4), "-frames:v", "1", str(end_f)])
    if end_f.exists():
        periodic_info.append((end_f, f"END {end_t:05.2f}s"))

    # Scene-change detection frames (gt(scene,0.18))
    sc_res = run([
        "ffmpeg", "-y", "-i", str(final_mp4),
        "-vf", "select='gt(scene,0.18)',showinfo",
        "-vsync", "vfr",
        str(frames_dir / "cut_%03d.png"),
    ])
    cut_times = re.findall(r"pts_time:([0-9.]+)", sc_res.stderr)

    # Contact sheet
    make_contact_sheet(periodic_info, d / "contact_sheet.png", cols=5)

    print(f"Processed {name}: source={chosen_source}, dur={duration:.3f}s, periodic_frames={len(periodic_info)}, scene_cuts={len(cut_times)} ({cut_times})")


def main():
    for cfg in REELS:
        process_reel(cfg)


if __name__ == "__main__":
    main()
