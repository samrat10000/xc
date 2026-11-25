import base64
import json
import urllib.parse
import urllib.request
from pathlib import Path

REEL_DIRS = [
    Path(r"c:\Users\cross\Downloads\xc\creepy\references\reel1_DeeVNnAu_C0"),
    Path(r"c:\Users\cross\Downloads\xc\creepy\references\reel2_DZC5NnpIwXe"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://www.instagram.com/",
    "Origin": "https://www.instagram.com",
}


def strip_byte_range(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    qs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    filtered = [(k, v) for k, v in qs if k not in ("bytestart", "byteend")]
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(filtered), parsed.fragment))


def decode_efg(url: str) -> dict:
    parsed = urllib.parse.urlsplit(url)
    qs = dict(urllib.parse.parse_qsl(parsed.query))
    efg = qs.get("efg")
    if not efg:
        return {}
    try:
        pad = "=" * ((4 - len(efg) % 4) % 4)
        return json.loads(base64.urlsafe_b64decode(efg + pad).decode("utf-8"))
    except Exception:
        return {}


def download_file(url: str, dest: Path) -> tuple[bool, int, str]:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = resp.read()
            dest.write_bytes(data)
            return True, resp.status, f"{len(data)} bytes"
    except Exception as e:
        return False, 0, str(e)


def process_dir(d: Path):
    meta_path = d / "playwright_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    print(f"=== {d.name} ===")

    # 1. Progressive fallback from embed.videos[0].src
    embed_videos = (meta.get("embed") or {}).get("videos") or []
    if embed_videos and embed_videos[0].get("src"):
        prog_url = embed_videos[0]["src"]
        ok, status, info = download_file(prog_url, d / "progressive.mp4")
        print(f"  progressive.mp4: ok={ok} status={status} info={info}")

    # 2. Pick best DASH video and DASH audio from media_urls (stripped of byte-range params)
    video_candidates = []
    audio_candidates = []
    seen = set()
    for raw_url in meta.get("media_urls", []):
        clean_url = strip_byte_range(raw_url)
        if clean_url in seen:
            continue
        seen.add(clean_url)
        efg = decode_efg(clean_url)
        tag = (efg.get("vencode_tag") or "").lower()
        bitrate = int(efg.get("bitrate") or 0)
        if "audio" in tag:
            audio_candidates.append((bitrate, tag, clean_url))
        else:
            video_candidates.append((bitrate, tag, clean_url))

    video_candidates.sort(reverse=True, key=lambda x: x[0])
    audio_candidates.sort(reverse=True, key=lambda x: x[0])

    if video_candidates:
        br, tag, vurl = video_candidates[0]
        ok, status, info = download_file(vurl, d / "dash_video.mp4")
        print(f"  dash_video.mp4 ({tag}, br={br}): ok={ok} status={status} info={info}")
    if audio_candidates:
        br, tag, aurl = audio_candidates[0]
        ok, status, info = download_file(aurl, d / "dash_audio.mp4")
        print(f"  dash_audio.mp4 ({tag}, br={br}): ok={ok} status={status} info={info}")


def main():
    for d in REEL_DIRS:
        process_dir(d)


if __name__ == "__main__":
    main()
