# 5 O’CLOCK · The Reply

`5oclock-the-reply.mp4` is a 15-second vertical 2D proof of concept with stereo sound. Sam hears the ordinary town chime, stops, and sees night in the traffic mirror when the chime is answered. The mirror is a proposed visual beat for the story.

The art uses two original ImageGen plates. The shot timing, eyelines, eyelid cel, small character movements and mirror transition are composited locally. The chime melody and its reply are original synthesised sound, mixed with a constructed street ambience. The character uses limited animation.

To rebuild, run `python source/render.py 5oclock-the-reply-new.mp4` from this folder with Pillow, NumPy, SciPy and FFmpeg installed. The compositor uses the bundled street and reaction plates, timed cuts and 24 fps output. It exports H.264 and stereo AAC at 1080 × 1920. Use a new output filename for each render.
