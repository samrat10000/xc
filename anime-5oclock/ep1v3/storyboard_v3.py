from PIL import Image, ImageDraw, ImageFont
import math
PW,PH=300,533
F=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",15);FB=ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf",16);FS=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",13)
INK=(40,36,50)
def grad(d,top,bot):
    for y in range(PH):
        t=y/PH;d.line([(0,y),(PW,y)],fill=tuple(int(top[i]*(1-t)+bot[i]*t) for i in range(3)))
def sky(d): grad(d,(120,125,165),(235,190,150))
def p1(d):
    sky(d);d.rectangle([0,380,PW,PH],fill=(150,140,160))
    d.polygon([(0,260),(70,300),(70,400),(0,380)],fill=(170,160,185),outline=INK)
    d.rectangle([232,215,246,PH],fill=(200,70,50),outline=INK)
    d.ellipse([40,70,250,280],fill=(210,80,55),outline=INK,width=3);d.ellipse([58,88,232,262],fill=(25,32,60),outline=INK,width=2)
    d.line([(100,230),(145,150),(190,230)],fill=(80,90,120),width=3);d.ellipse([136,140,154,158],fill=(230,230,255))
    d.polygon([(100,520),(135,400),(165,400),(215,520)],fill=(185,175,195))
def p2(d):
    sky(d);d.polygon([(110,PH),(130,120),(165,120),(190,PH)],fill=(150,145,170),outline=INK)
    for a in range(4):
        ang=a*math.pi/2+.8;cx,cy=150,105
        d.polygon([(cx,cy),(cx+math.cos(ang-.35)*85,cy+math.sin(ang-.35)*85),(cx+math.cos(ang+.35)*85,cy+math.sin(ang+.35)*85)],fill=(215,215,225),outline=INK)
    d.line([(0,150),(110,170)],fill=INK,width=2);d.line([(190,170),(PW,150)],fill=INK,width=2)
    for x in (30,60,235,262): d.polygon([(x,140),(x+8,128),(x+14,140)],fill=INK)
def p3(d):
    grad(d,(110,110,120),(70,70,85));d.line([(0,250),(PW,230)],fill=(90,90,100),width=3)
    d.polygon([(40,PH),(70,330),(130,330),(150,PH)],fill=(60,60,75),outline=INK,width=2)
    d.ellipse([20,470,170,520],fill=(30,30,40));
    d.polygon([(165,PH),(195,340),(255,345),(280,PH)],fill=(160,60,60),outline=INK,width=2)
    d.rectangle([60,300,125,335],fill=(235,205,185),outline=INK);d.rectangle([195,310,250,345],fill=(235,205,185),outline=INK)
def p4(d):
    sky(d);d.ellipse([20,100,200,330],fill=(60,52,60),outline=INK,width=3)
    d.ellipse([70,230,170,420],fill=(235,195,170),outline=INK,width=3)
    d.polygon([(10,PH),(40,380),(220,380),(260,PH)],fill=(70,70,78),outline=INK)
    d.ellipse([155,170,275,300],fill=(30,30,36),outline=INK,width=3);d.ellipse([175,190,255,280],fill=(50,50,58))
    d.polygon([(200,330),(235,300),(285,400),(245,430)],fill=(238,200,180),outline=INK,width=3)
def p5(d):
    grad(d,(140,150,150),(95,110,105));d.rectangle([0,150,PW,260],fill=(120,140,130))
    d.polygon([(0,PH),(0,330),(120,300),(300,360),(300,PH)],fill=(70,70,85),outline=INK)
    d.ellipse([70,110,200,260],fill=(40,34,50),outline=INK,width=3);d.polygon([(100,200),(150,215),(125,300)],fill=(236,196,172),outline=INK)
    d.line([(110,175),(145,170)],fill=INK,width=3)
    d.polygon([(215,0),(300,0),(300,PH),(235,PH),(250,200)],fill=(25,22,32))
def p6(d):
    sky(d);d.rectangle([0,360,PW,PH],fill=(160,150,170))
    d.polygon([(0,200),(100,320),(100,420),(0,420)],fill=(175,165,190),outline=INK);d.polygon([(PW,230),(210,320),(210,420),(PW,420)],fill=(225,215,185),outline=INK)
    d.polygon([(150,300),(60,PH),(240,PH)],fill=(150,145,160))
    for x,y,c in ((95,350,(150,120,150)),(155,345,(230,190,40)),(205,350,(40,45,70))):
        d.rectangle([x-8,y-14,x+8,y+34],fill=c,outline=INK)
    d.ellipse([150,300,166,316],fill=(240,240,240),outline=(200,50,40))
def p7(d):
    grad(d,(25,32,60),(12,16,30));d.ellipse([-60,60,360,480],fill=(30,40,75),outline=(200,80,55),width=6)
    d.ellipse([105,150,195,250],fill=(26,24,34),outline=INK,width=2);d.polygon([(95,260),(205,260),(215,PH),(85,PH)],fill=(30,30,40))
    d.ellipse([128,195,142,205],fill=(230,60,60));d.ellipse([158,195,172,205],fill=(230,60,60))
P=[(p1,"1 MIRROR  0-3.0s","Locked. Day lane, mirror shows night. Leaf drifts. Cut stamp 16:59:47. N1 voice.","\"In Kiriyama, the five o'clock song has four notes.\""),
(p2,"2 SPEAKER  3.0-6.5s","Crows leave the pole. Three notes, then silence. Hold on the dead horn.","N2: \"Until today.\""),
(p3,"3 FEET  6.5-8.5s","Close on shoes stopping in the lane. Cracked asphalt. A second pair, unseen owner.","(room tone, wire hum)"),
(p4,"4 HAND  8.5-11.5s","Close: his hand lifts the headphone off his ear. Hair moves. Held.","S1: \"...Three?\""),
(p5,"5 PROFILE  11.5-14.5s","Sam waist-up, eyes lower, listening. Foreground coat edge crosses frame.","(silence, breath)"),
(p6,"6 STREET  14.5-17.5s","Wide: everyone frozen mid-step, ball hanging in air. Tiny move: one leaf.","P1 speaker: \"Please stay where you are.\""),
(p7,"7 ANSWER  17.5-21.0s","Mirror close. Night-Sam looks out, red eyes. Black on 4th note.","S2: \"You weren't listening.\"")]
import textwrap
W=4*(PW+20)+20;H=2*(PH+175)+70
im=Image.new("RGB",(W,H),(24,24,30));d=ImageDraw.Draw(im)
d.text((20,15),"5 O'CLOCK Ep1 v3 storyboard (rough, 21 s, 7 shots). Close, short, one idea per shot.",font=FB,fill=(240,240,240))
for i,(fn,t,desc,line) in enumerate(P):
    r,c=divmod(i,4);x=20+c*(PW+20);y=50+r*(PH+175)
    pn=Image.new("RGB",(PW,PH));fn(ImageDraw.Draw(pn));im.paste(pn,(x,y));d.rectangle([x,y,x+PW,y+PH],outline=(200,200,200))
    d.text((x,y+PH+6),t,font=FB,fill=(255,210,120))
    yy=y+PH+28
    for l in textwrap.wrap(desc,38): d.text((x,yy),l,font=FS,fill=(220,220,220));yy+=16
    for l in textwrap.wrap(line,36): d.text((x,yy+4),l,font=FS,fill=(140,200,255));yy+=16
im.save("C:/Users/cross/Downloads/xc/anime-5oclock/ep1v3/storyboard_v3.png")
