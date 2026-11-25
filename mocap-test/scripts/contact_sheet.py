"""Video frames (top) vs BVH skeleton side view (bottom) for a few frames."""
import json, sys, subprocess, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

video, bones_json, out_png, tmp = sys.argv[1:5]
B = json.load(open(bones_json))
frames = [1, 61, 121, 181, 241, 301]
fig, ax = plt.subplots(2, len(frames), figsize=(3 * len(frames), 6.5))
for i, f in enumerate(frames):
    jpg = os.path.join(tmp, f"f{f}.jpg")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf", f"select=eq(n\\,{f-1})",
                    "-frames:v", "1", jpg], check=True)
    ax[0, i].imshow(mpimg.imread(jpg)); ax[0, i].set_title(f"frame {f}"); ax[0, i].axis("off")
    bf = B[str(f)]
    xs = [p for h, t in bf.values() for p in (h[0], t[0])]
    cx = sum(xs) / len(xs)
    for name, (h, t) in bf.items():
        col = "tab:red" if name.startswith("Left") else "tab:blue" if name.startswith("Right") else "k"
        ax[1, i].plot([h[0] - cx, t[0] - cx], [h[2], t[2]], color=col, lw=2)
    ax[1, i].set_xlim(-1, 1); ax[1, i].set_ylim(-0.1, 2.0); ax[1, i].set_aspect("equal")
    ax[1, i].axhline(0, color="0.7", lw=0.5); ax[1, i].set_xticks([]); ax[1, i].set_yticks([])
plt.suptitle("MediaPipe → BVH (side view, red=left, blue=right)")
plt.tight_layout(); plt.savefig(out_png, dpi=80)
print("saved", out_png)
