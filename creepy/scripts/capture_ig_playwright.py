import json
from pathlib import Path
from playwright.sync_api import sync_playwright

REELS = [
    {
        "id": "DeeVNnAu_C0",
        "url": "https://www.instagram.com/reel/DeeVNnAu_C0/?jplx=aHF6ZzhqdHBrdm1p",
        "embed_url": "https://www.instagram.com/reel/DeeVNnAu_C0/embed/",
        "out_dir": r"c:\Users\cross\Downloads\xc\creepy\references\reel1_DeeVNnAu_C0",
        "prefix": "reel1",
    },
    {
        "id": "DZC5NnpIwXe",
        "url": "https://www.instagram.com/reel/DZC5NnpIwXe/?bqrl=emV5Y2lyanhwcTdy",
        "embed_url": "https://www.instagram.com/reel/DZC5NnpIwXe/embed/",
        "out_dir": r"c:\Users\cross\Downloads\xc\creepy\references\reel2_DZC5NnpIwXe",
        "prefix": "reel2",
    },
]


def launch_browser(p):
    for kwargs in [
        {"headless": True},
        {"headless": True, "channel": "chrome"},
        {"headless": True, "channel": "msedge"},
    ]:
        try:
            return p.chromium.launch(**kwargs)
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Could not launch Chromium/Chrome/Edge: {last_err}")


def dismiss_overlays(page):
    selectors = [
        'button:has-text("Allow all cookies")',
        'button:has-text("Accept All")',
        'button:has-text("Decline optional cookies")',
        'button:has-text("Only allow essential cookies")',
        'button:has-text("Not Now")',
        'button:has-text("Not now")',
        'div[role="dialog"] button[aria-label="Close"]',
        'svg[aria-label="Close"]',
        'button[aria-label="Close"]',
    ]
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=800):
                loc.click(timeout=1500)
                page.wait_for_timeout(600)
        except Exception:
            pass


def extract_page_info(page):
    return page.evaluate("""() => {
        const title = document.title || "";
        const url = window.location.href;
        const bodyText = document.body ? document.body.innerText : "";
        const videos = Array.from(document.querySelectorAll("video")).map(v => ({
            src: v.currentSrc || v.src || null,
            duration: Number.isFinite(v.duration) ? v.duration : null,
            videoWidth: v.videoWidth,
            videoHeight: v.videoHeight,
            poster: v.poster || null,
            paused: v.paused
        }));
        const meta = {};
        for (const m of document.querySelectorAll("meta")) {
            const k = m.getAttribute("property") || m.getAttribute("name");
            const v = m.getAttribute("content");
            if (k && v) meta[k] = v;
        }
        const links = Array.from(document.querySelectorAll("a"))
            .map(a => ({ text: (a.innerText || "").trim(), href: a.href }))
            .filter(a => a.text || a.href.includes("/audio/") || a.href.includes("/reel/"));
        return {
            url,
            title,
            meta,
            videos,
            links: links.slice(0, 80),
            bodyText: bodyText.slice(0, 12000)
        };
    }""")


def capture_reel(context, reel):
    out_dir = Path(reel["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    result = {"id": reel["id"], "main": None, "embed": None, "media_urls": []}

    def attach_media_listener(p):
        def on_response(resp):
            try:
                ct = (resp.headers.get("content-type") or "").lower()
                u = resp.url
                if ("video/" in ct or ".mp4" in u) and resp.status in (200, 206):
                    if u not in result["media_urls"]:
                        result["media_urls"].append(u)
            except Exception:
                pass
        p.on("response", on_response)

    page = context.new_page()
    page.set_viewport_size({"width": 1440, "height": 960})
    attach_media_listener(page)

    try:
        page.goto(reel["url"], wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        dismiss_overlays(page)
        page.wait_for_timeout(2000)
        page.screenshot(path=str(out_dir / "page_screenshot.png"), full_page=False)
        result["main"] = extract_page_info(page)
    except Exception as e:
        result["main_error"] = str(e)

    embed_page = context.new_page()
    embed_page.set_viewport_size({"width": 900, "height": 1100})
    attach_media_listener(embed_page)
    try:
        embed_page.goto(reel["embed_url"], wait_until="domcontentloaded", timeout=30000)
        embed_page.wait_for_timeout(4000)
        dismiss_overlays(embed_page)
        embed_page.wait_for_timeout(2000)
        embed_page.screenshot(path=str(out_dir / "embed_screenshot.png"), full_page=False)
        embed_info = extract_page_info(embed_page)
        result["embed"] = embed_info

        # Try clicking play on embed if paused, to trigger video load
        try:
            if embed_page.locator("video").count() > 0:
                embed_page.locator("video").first.click(timeout=1500)
                embed_page.wait_for_timeout(2000)
                embed_info = extract_page_info(embed_page)
                result["embed"] = embed_info
        except Exception:
            pass

        mp4_path = out_dir / f"{reel['prefix']}.mp4"
        # Try downloading direct mp4 if a public CDN URL was served to the unauthenticated player
        candidate_urls = list(result["media_urls"])
        for src_info in (result.get("main") or {}).get("videos", []) + (result.get("embed") or {}).get("videos", []):
            if src_info.get("src") and not src_info["src"].startswith("blob:") and src_info["src"] not in candidate_urls:
                candidate_urls.append(src_info["src"])

        for u in candidate_urls:
            if not mp4_path.exists():
                try:
                    resp = context.request.get(u, timeout=30000)
                    if resp.ok and len(resp.body()) > 50000:
                        mp4_path.write_bytes(resp.body())
                        result["downloaded_mp4_from"] = u
                        break
                except Exception as de:
                    result["download_err"] = str(de)

        if not mp4_path.exists():
            target_page = embed_page if (result.get("embed") or {}).get("videos") else page
            if target_page.locator("video").count() > 0:
                target_page.evaluate("() => { const v = document.querySelector('video'); if (v) { v.muted = true; v.pause(); } }")
                dur = target_page.evaluate("() => { const v = document.querySelector('video'); return v && Number.isFinite(v.duration) ? v.duration : 0; }")
                if dur and dur > 0:
                    step = 1.0 if dur > 15 else 0.5
                    t = 0.0
                    idx = 1
                    while t <= dur + 0.01 and idx <= 60:
                        target_page.evaluate(f"() => {{ const v = document.querySelector('video'); if (v) v.currentTime = {min(t, max(0, dur - 0.05))}; }}")
                        target_page.wait_for_timeout(350)
                        target_page.locator("video").first.screenshot(path=str(frames_dir / f"pw_t_{idx:03d}_{t:.1f}s.png"))
                        t += step
                        idx += 1
    except Exception as e:
        result["embed_error"] = str(e)
    finally:
        page.close()
        embed_page.close()

    with open(out_dir / "playwright_meta.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Captured {reel['id']}: main_videos={len((result.get('main') or {}).get('videos', []))}, embed_videos={len((result.get('embed') or {}).get('videos', []))}, media_urls={len(result['media_urls'])}, mp4_saved={(out_dir / (reel['prefix'] + '.mp4')).exists()}")


def main():
    with sync_playwright() as p:
        browser = launch_browser(p)
        context = browser.new_context(
            viewport={"width": 1440, "height": 960},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            locale="en-US",
        )
        for reel in REELS:
            capture_reel(context, reel)
        browser.close()


if __name__ == "__main__":
    main()
