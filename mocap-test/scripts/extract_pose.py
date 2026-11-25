"""MediaPipe Pose extraction (same engine PosePipe uses), headless.
Writes per-frame world landmarks (metres, hip-centred) + image landmarks to JSON.
Usage: python extract_pose.py <video> <out.json> [model_complexity 0|1|2]
"""
import json, sys, time
import cv2
import mediapipe as mp

video, out = sys.argv[1], sys.argv[2]
mc = int(sys.argv[3]) if len(sys.argv) > 3 else 2

cap = cv2.VideoCapture(video)
fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frames = []
t0 = time.time()
with mp.solutions.pose.Pose(static_image_mode=False, model_complexity=mc,
                            smooth_landmarks=True, min_detection_confidence=0.5,
                            min_tracking_confidence=0.5) as pose:
    while True:
        ok, img = cap.read()
        if not ok:
            break
        r = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if r.pose_world_landmarks:
            frames.append({
                "world": [[l.x, l.y, l.z, l.visibility] for l in r.pose_world_landmarks.landmark],
                "img": [[l.x, l.y, l.z] for l in r.pose_landmarks.landmark],
            })
        else:
            frames.append(None)
dt = time.time() - t0
n = len(frames); hit = sum(f is not None for f in frames)
json.dump({"fps": fps, "w": W, "h": H, "frames": frames}, open(out, "w"))
print(f"frames={n} detected={hit} time={dt:.1f}s proc_fps={n/dt:.1f} video_fps={fps:.1f} res={W}x{H}")
