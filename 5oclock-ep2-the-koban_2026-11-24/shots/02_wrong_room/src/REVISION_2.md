# Revision 2 reproduction

Use the completed v1 render cache as input. Frames 1–72 are hard-linked from the locked v1 composites. Only the 24-frame phone insert is recomposited from the existing EEVEE and plane-reflection renders.

    python src/comp_wrong_room_v2.py qa/v1_cel qa/v2_frames 4 qa/v1_frames
    ffmpeg -n -framerate 24 -start_number 1 -i qa/v2_frames/%03d.png -frames:v 96 -an -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -movflags +faststart 02_wrong_room_v2.mp4
