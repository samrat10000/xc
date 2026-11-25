# 5 O’CLOCK · The Reply, v2

`5oclock-the-reply-v2.mp4` is a continuous 15-second shot at 1080 × 1920, 24 fps, with stereo audio. Sam reaches toward the rail, raises his head at the town chime, then draws his arm down and away when the chime answers. The reflection changes from daylight to night inside a fixed traffic mirror.

The character cel and background are original generated artwork. The 2D mesh rig is keyed by hand and animated mostly on twos, with separate motion for the body, head, elbow, wrist, hair and eyelids. The camera and background are locked. The mirror has its own matte and animated exposure. This is a rigged 2D animation study. It uses the motion principles of [the Granite Waves clip](https://www.instagram.com/reel/DeZlMh5M1jI/) and [the night-road reference](https://www.instagram.com/reel/DeS2sH9MjFX/).

`source/animate.py` contains the editable timing and pose keys. To rebuild from this folder, run `python source/animate.py 5oclock-the-reply-v2-new.mp4` with Pillow, NumPy, SciPy and FFmpeg installed. Keep the sibling `reel-v1` folder available for the original sound synthesis script. The v2 render adds a rail contact sound.
