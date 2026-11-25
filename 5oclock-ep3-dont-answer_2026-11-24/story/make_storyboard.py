"""Generate 5x3 color-script storyboard strip (9:16 panels) for 5 O'CLOCK Ep3."""
import os
import math
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
PW, PH = 324, 576  # 9:16 panel
PAD = 22
HDR = 78
FTR = 104
COLS, ROWS = 5, 3
W = PAD + COLS * (PW + PAD)
H = HDR + ROWS * (PH + FTR + PAD) + 20

PANELS = [
    ("01", "The Handprint", "0.0-3.0s (72f)", "38mm push 3.2% + drift",
     "Fogged palm on glass; bolt grip; 5 crows snap", 'N: "Day three. He survived the knock."', "sunset_door"),
    ("02", "Eleven Marks", "3.0-6.0s (72f)", "40mm 3/4 MCU breath",
     "11+1 scratches on wood jamb; Sam 3/4 eyes", "-", "jamb_marks"),
    ("03", "Empty Crossing", "6.0-10.0s (96f)", "32mm wide horizon track",
     "Mirrored street, wider rift, footprint in field", 'N: "Sam is learning what each rule costs."', "horizon_walk"),
    ("04", "The Bus Stop", "10.0-14.5s (108f)", "35mm handheld track",
     "5 figures in line; Sam counts silently on fingers", "-", "busstop_5"),
    ("05", "Always One More", "14.5-18.5s (96f)", "45mm slow lateral glide",
     "6th is Mirror-Sam waving; Grandma shakes head", 'N: "Rule four. Never count the line..."', "busstop_6"),
    ("06", "Nothing Red", "18.5-22.0s (84f)", "50mm tight 3/4 CU",
     "Removes red glasses (4-finger+thumb) & pockets", 'S: "Nothing red..."', "glasses_off"),
    ("07", "16:59", "22.0-25.5s (84f)", "32mm low tilt up",
     "Clock clicks 16:59->17:00; ravens explode off wires", "-", "clock_crows"),
    ("08", "The Wrong Chime", "25.5-29.5s (96f)", "32mm side-on sprint",
     "Full sprint stride; 3 chime rings ripple clouds", "-", "sprint_rings"),
    ("09", "Her Voice", "29.5-34.0s (108f)", "38mm low horn -> Sam",
     "Showa horn swivels w/ overshoot; Mom's voice", 'Mom(PA): "Sam...? Where are you?"', "horn_voice"),
    ("10", "Don't Answer", "34.0-38.5s (108f)", "50mm tight 3/4 CU",
     "Hand clamps over mouth; trembling eyes, red tower", 'S: "Mom-"', "mouth_clamp"),
    ("11", "The Town Listens", "38.5-43.0s (108f)", "35mm whip-pan + smears",
     "All 6 stand across road, heads tilted 15 deg", "-", "town_stare"),
    ("12", "The Sky Breaks", "43.0-48.0s (120f)", "28mm scale wide + shake",
     "Listener 2x closer behind tower; arm slam; tiny Sam", 'N: "It was learning how to speak."', "kaiju_slam"),
    ("13", "4th Note Speaks", "48.0-52.0s (96f)", "32mm low OTS reverse",
     "Crown fills sky rift; central horn glows violet", "-", "horn_glow"),
    ("14", "The Real Voice", "52.0-56.5s (108f)", "42mm curve mirror UV",
     "In glass: Real Mom + Mirror-Sam hold hands", 'S: "Wait- that\'s not me! Mom!"', "mirror_mom"),
    ("15", "Rule Nine", "56.5-60.0s (84f)", "10f black -> top ECU",
     "Wet ink writes Japanese Rule 9 + 1964 smudge", 'N: "Rule nine... don\'t answer."', "notebook_9"),
]


def font(sz, bold=False):
    for p in (
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def sky_grad(w, h, dusk=False):
    im = Image.new("RGB", (w, h))
    px = im.load()
    stops = (
        [(0.0, (24, 18, 44)), (0.35, (68, 36, 78)), (0.62, (205, 96, 78)), (0.82, (252, 188, 112)), (1.0, (245, 210, 145))]
        if not dusk else
        [(0.0, (14, 12, 30)), (0.4, (45, 24, 62)), (0.72, (165, 68, 68)), (0.88, (242, 142, 86)), (1.0, (40, 26, 46))]
    )
    for y in range(h):
        v = y / max(h - 1, 1)
        c = stops[-1][1]
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= v <= p1:
                t = (v - p0) / max(p1 - p0, 1e-5)
                c = tuple(int(c0[i] * (1 - t) + c1[i] * t) for i in range(3))
                break
        for x in range(w):
            px[x, y] = c
    return im


def draw_scene(kind):
    dusk = kind in ("town_stare", "kaiju_slam", "horn_glow")
    if kind == "notebook_9":
        im = Image.new("RGB", (PW, PH), (16, 14, 20))
        d = ImageDraw.Draw(im)
        d.rectangle([28, 40, PW - 28, PH - 40], fill=(224, 208, 174), outline=(55, 42, 34), width=3)
        for y in range(110, PH - 80, 48):
            d.line([48, y, PW - 48, y], fill=(175, 162, 138), width=1)
        d.rectangle([58, 320, PW - 58, 336], fill=(120, 102, 82))
        d.line([62, 415, 245, 415], fill=(28, 22, 26), width=5)
        d.ellipse([232, 438, 256, 458], fill=(175, 36, 36))
        return im

    im = sky_grad(PW, PH, dusk=dusk)
    d = ImageDraw.Draw(im)
    # distant ridge + 1964 tower
    d.polygon([(0, 460), (85, 420), (175, 445), (260, 412), (PW, 450), (PW, PH), (0, PH)], fill=(54, 34, 58))
    d.polygon([(52, 432), (56, 378), (60, 432)], fill=(42, 26, 46))
    d.ellipse([53, 373, 59, 379], fill=(235, 50, 45))

    if kind == "sunset_door":
        d.ellipse([200, 275, 264, 339], fill=(255, 244, 200))
        # wire + 5 crows
        d.line([110, 150, PW, 175], fill=(24, 16, 24), width=3)
        for cx in (152, 182, 214, 246, 276):
            cy = 152 + int((cx - 110) * 0.11)
            d.ellipse([cx - 8, cy - 22, cx + 8, cy - 2], fill=(24, 18, 28))
            d.ellipse([cx - 5, cy - 30, cx + 6, cy - 20], fill=(24, 18, 28))
        # door mullion + fogged handprint + Sam 3/4 + bolt
        d.rectangle([0, 0, 128, PH], fill=(38, 28, 44))
        d.rectangle([128, 0, 144, PH], fill=(64, 48, 56))
        d.ellipse([198, 205, 244, 265], fill=(228, 226, 236))  # fogged palm
        for dx, dy in [(-18, -22), (-9, -32), (0, -36), (10, -31), (20, -14)]:
            d.ellipse([218 + dx - 4, 225 + dy - 10, 218 + dx + 4, 225 + dy + 2], fill=(228, 226, 236))
        # Sam silhouette left-front 3/4
        d.ellipse([36, 175, 114, 265], fill=(28, 22, 32))
        d.rectangle([42, 262, 116, 520], fill=(54, 56, 66))
        d.rectangle([82, 222, 108, 234], outline=(215, 42, 42), width=3)  # red glasses
        d.rectangle([118, 336, 154, 358], fill=(195, 160, 75))  # brass bolt
    elif kind == "jamb_marks":
        d.rectangle([0, 0, 115, PH], fill=(72, 52, 46))
        for k in range(11):
            y = 190 + k * 14
            d.line([36, y, 88, y - 5], fill=(24, 16, 14), width=3)
        d.line([36, 352, 92, 346], fill=(235, 195, 130), width=4)
        d.ellipse([160, 165, 278, 295], fill=(30, 24, 34))
        d.rectangle([175, 290, 275, 530], fill=(62, 64, 74))
        d.rectangle([162, 225, 192, 238], outline=(215, 42, 42), width=3)
    elif kind in ("horizon_walk", "sprint_rings"):
        d.polygon([(0, 470), (PW, 470), (PW, PH), (0, PH)], fill=(48, 42, 56))
        d.line([162, 470, 162, PH], fill=(215, 205, 190), width=3)
        if kind == "sprint_rings":
            for r in (65, 120, 175):
                d.arc([162 - r, 150 - r // 2, 162 + r, 150 + r // 2], 190, 350, fill=(255, 210, 140), width=3)
        d.ellipse([128, 325, 162, 365], fill=(26, 20, 30))
        d.polygon([(125, 366), (165, 366), (175, 490), (115, 490)], fill=(58, 60, 72))
    elif kind in ("busstop_5", "busstop_6", "town_stare"):
        d.polygon([(0, 460), (PW, 460), (PW, PH), (0, PH)], fill=(50, 44, 58))
        d.line([28, 240, 28, 480], fill=(34, 28, 36), width=5)
        d.ellipse([16, 220, 40, 248], fill=(210, 185, 140))
        cnt = 5 if kind == "busstop_5" else 6
        for i in range(cnt):
            x = 72 + i * 42
            h = 105 if i in (2, 3) else 135
            if i == 0:
                h = 115
            y0 = 468 - h
            d.ellipse([x - 11, y0 - 22, x + 11, y0], fill=(32, 24, 36))
            d.rectangle([x - 13, y0, x + 13, 468], fill=(58, 52, 68) if i < 5 else (34, 30, 42))
        if kind == "busstop_6":
            d.line([282, 355, 306, 315], fill=(235, 185, 145), width=6)  # wave
    elif kind in ("glasses_off", "mouth_clamp"):
        d.ellipse([170, 210, 290, 330], fill=(255, 220, 140))
        d.ellipse([78, 125, 246, 320], fill=(28, 22, 32))
        d.rectangle([86, 310, 240, 560], fill=(64, 66, 78))
        if kind == "glasses_off":
            d.rectangle([155, 250, 218, 272], outline=(225, 45, 45), width=4)
        else:
            d.ellipse([128, 248, 198, 296], fill=(235, 192, 165), outline=(30, 20, 25), width=2)
    elif kind in ("clock_crows", "horn_voice"):
        d.ellipse([180, 240, 280, 340], fill=(255, 215, 130))
        d.rectangle([148, 180, 168, PH], fill=(54, 48, 58))
        d.polygon([(95, 175), (155, 200), (155, 232), (95, 258)], fill=(128, 118, 112), outline=(26, 18, 24))
        if kind == "clock_crows":
            d.ellipse([130, 295, 188, 353], fill=(240, 235, 225), outline=(28, 22, 28), width=3)
            for bx, by in [(70, 120), (125, 95), (215, 110), (265, 145)]:
                d.arc([bx, by, bx + 36, by + 18], 180, 360, fill=(22, 16, 26), width=4)
        else:
            for r in (28, 52, 78):
                d.arc([95 - r, 216 - r, 95 + r, 216 + r], 125, 235, fill=(255, 230, 175), width=3)
    elif kind in ("kaiju_slam", "horn_glow"):
        # massive starry sky rift + giant Listener behind tower
        d.polygon([(0, 95), (120, 70), (240, 88), (PW, 65), (PW, 155), (210, 172), (90, 150), (0, 168)], fill=(12, 16, 36), outline=(170, 205, 255))
        cx, cy = 190, 245 if kind == "kaiju_slam" else 175
        d.rectangle([cx - 24, cy + 40, cx + 24, 455], fill=(32, 22, 34))
        for ang in range(0, 360, 24):
            rad = math.radians(ang)
            hx = cx + int(math.cos(rad) * 86)
            hy = cy + int(math.sin(rad) * 72)
            d.line([cx, cy, hx, hy], fill=(52, 38, 48), width=4)
            d.ellipse([hx - 14, hy - 14, hx + 14, hy + 14], fill=(22, 16, 22), outline=(195, 145, 95), width=2)
        if kind == "kaiju_slam":
            # giant arm slamming left
            d.polygon([(85, 155), (125, 155), (105, 445), (58, 445)], fill=(28, 20, 30))
            d.ellipse([36, 485, 50, 505], fill=(20, 16, 24))  # tiny Sam
        else:
            d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(210, 195, 255))
    elif kind == "mirror_mom":
        d.rectangle([0, 0, PW, PH], fill=(55, 46, 58))
        d.ellipse([36, 110, PW - 36, 410], fill=(250, 185, 115), outline=(205, 52, 42), width=10)
        # Mom + Mirror-Sam inside
        d.ellipse([105, 215, 138, 252], fill=(42, 32, 42))
        d.rectangle([100, 252, 144, 365], fill=(138, 108, 102))
        d.ellipse([178, 210, 212, 248], fill=(30, 24, 34))
        d.rectangle([174, 248, 218, 365], fill=(64, 66, 76))
        # Sam foreground palm on glass
        d.ellipse([190, 340, 255, 420], fill=(235, 195, 168), outline=(32, 22, 26), width=3)

    # camera arrow badge
    d.rectangle([8, 8, 96, 30], fill=(14, 12, 20))
    return im


def main():
    canvas = Image.new("RGB", (W, H), (18, 17, 24))
    d = ImageDraw.Draw(canvas)
    f_title = font(28, bold=True)
    f_sub = font(16, bold=False)
    f_card = font(16, bold=True)
    f_sm = font(13, bold=False)

    d.text((PAD, 16), "5 O'CLOCK  EPISODE 3 : DAY 3  -  DON'T ANSWER  (60.0s, 15 SHOTS, 1080x1920)", fill=(248, 232, 205), font=f_title)
    d.text((PAD, 50), "Rules 4, 5, 6 & 2  |  Style: toon-anime (01_speaker_v4 bar)  |  Audio added after picture lock", fill=(185, 172, 196), font=f_sub)

    for idx, (num, title, tm, cam, act, line, kind) in enumerate(PANELS):
        c = idx % COLS
        r = idx // COLS
        x0 = PAD + c * (PW + PAD)
        y0 = HDR + r * (PH + FTR + PAD)
        pan = draw_scene(kind)
        canvas.paste(pan, (x0, y0))
        d.rectangle([x0, y0, x0 + PW, y0 + PH], outline=(78, 70, 92), width=2)
        d.text((x0 + 14, y0 + 11), f"{num}  {tm}", fill=(255, 224, 152), font=f_sm)

        fy = y0 + PH + 6
        d.text((x0, fy), f"{num}. {title}", fill=(250, 242, 230), font=f_card)
        d.text((x0, fy + 22), f"Cam: {cam}", fill=(165, 196, 235), font=f_sm)
        d.text((x0, fy + 40), act[:46], fill=(214, 208, 222), font=f_sm)
        if len(act) > 46:
            d.text((x0, fy + 56), act[46:92], fill=(214, 208, 222), font=f_sm)
        d.text((x0, fy + 74), line[:48], fill=(255, 196, 132), font=f_sm)

    out_png = os.path.join(OUT_DIR, "storyboard_strip.png")
    canvas.save(out_png, quality=95)
    print("WROTE", out_png)


if __name__ == "__main__":
    main()
