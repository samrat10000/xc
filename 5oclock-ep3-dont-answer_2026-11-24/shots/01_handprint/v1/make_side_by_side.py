"""Build side-by-side PNG sample sheets comparing Ep1 v4 locked bar and Ep3 Shot 01 frames & crops."""
import os
from PIL import Image, ImageDraw, ImageFont

EP3 = r"C:\Users\cross\Downloads\xc\5oclock-ep3-dont-answer_2026-11-24"
P5C = os.path.join(EP3, "shots", "01_handprint", "src", "probe5_c")
P5QA = os.path.join(EP3, "shots", "01_handprint", "src", "probe5", "qa")
REF = os.path.join(EP3, "assets", "ref_s01_v4.png")
V1 = os.path.join(EP3, "shots", "01_handprint", "v1")
os.makedirs(V1, exist_ok=True)


def font(sz):
    for p in ("C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def build_frames_sheet():
    panels = [
        ("Ep1 Locked Bar (01_speaker_v4)", REF),
        ("Ep3 Shot 01 · f001 (Hook: Handprint + 5 Crows)", os.path.join(P5C, "001.png")),
        ("Ep3 Shot 01 · f034 (Brass Bolt Grip)", os.path.join(P5C, "034.png")),
        ("Ep3 Shot 01 · f056 (Door Cracks + Crows Snap)", os.path.join(P5C, "056.png")),
    ]
    PW, PH = 540, 960
    PAD, HDR = 16, 62
    W = PAD + len(panels) * (PW + PAD)
    H = HDR + PH + PAD
    out = Image.new("RGB", (W, H), (16, 15, 22))
    d = ImageDraw.Draw(out)
    f_hdr = font(20)
    for i, (label, path) in enumerate(panels):
        im = Image.open(path).convert("RGB").resize((PW, PH), Image.LANCZOS)
        x = PAD + i * (PW + PAD)
        out.paste(im, (x, HDR))
        d.rectangle([x, HDR, x + PW, HDR + PH], outline=(86, 78, 102), width=2)
        d.text((x + 4, 20), label, fill=(255, 228, 176), font=f_hdr)
    dst = os.path.join(V1, "ep3_shot01_side_by_side.png")
    out.save(dst)
    print("WROTE", dst)


def build_crops_sheet():
    crops = [
        ("Sam 3/4 Face + Glasses (f001)", os.path.join(P5QA, "crop_face_sam_001.png")),
        ("Right Hand Bolt Grip (f034)", os.path.join(P5QA, "crop_hand_bolt_003.png")),
        ("5 Crows Pre-Snap (f034)", os.path.join(P5QA, "crop_crows_wire_003.png")),
        ("5 Crows Snap Left (f056)", os.path.join(P5QA, "crop_crows_wire_005.png")),
    ]
    CW, CH = 460, 420
    PAD, HDR = 16, 56
    W = PAD + len(crops) * (CW + PAD)
    H = HDR + CH + PAD
    out = Image.new("RGB", (W, H), (16, 15, 22))
    d = ImageDraw.Draw(out)
    f_hdr = font(19)
    for i, (label, path) in enumerate(crops):
        im = Image.open(path).convert("RGB")
        scale = min(CW / im.width, CH / im.height)
        nw, nh = int(im.width * scale), int(im.height * scale)
        im_r = im.resize((nw, nh), Image.LANCZOS)
        x = PAD + i * (CW + PAD)
        ox = x + (CW - nw) // 2
        oy = HDR + (CH - nh) // 2
        out.paste(im_r, (ox, oy))
        d.rectangle([x, HDR, x + CW, HDR + CH], outline=(86, 78, 102), width=2)
        d.text((x + 4, 18), label, fill=(255, 228, 176), font=f_hdr)
    dst = os.path.join(V1, "ep3_shot01_crops_side_by_side.png")
    out.save(dst)
    print("WROTE", dst)


if __name__ == "__main__":
    build_frames_sheet()
    build_crops_sheet()
