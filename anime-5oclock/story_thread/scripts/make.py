import os, asyncio

OUT = os.path.dirname(os.path.abspath(__file__))
PW, PH, G = 450, 800, 18          # panel size (9:16) and gutter
W = PW * 3 + G * 4
H = PH + G * 2 + 56
INK = "#121016"
FONT = "Inter, 'Inter Display', sans-serif"
JP = "'IPAGothic', sans-serif"

def ink(w=4):
    return f'stroke="{INK}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'

def speed_lines(cx, cy, n=40, r0=160, r1=700, col="#fff", op=0.35, seed=1):
    import math, random
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.05, 0.05)
        a2 = a + rnd.uniform(0.008, 0.02)
        r = r0 + rnd.uniform(0, 80)
        p = [(cx + r * math.cos(a), cy + r * math.sin(a)),
             (cx + r1 * math.cos(a), cy + r1 * math.sin(a)),
             (cx + r1 * math.cos(a2), cy + r1 * math.sin(a2))]
        out.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in p)}" fill="{col}" opacity="{op}"/>')
    return "".join(out)

def hlines(x0, x1, y0, y1, n, col="#fff", op=0.4, seed=2):
    import random
    rnd = random.Random(seed)
    s = ""
    for i in range(n):
        y = rnd.uniform(y0, y1); a = rnd.uniform(x0, x1 - 60); L = rnd.uniform(60, 260)
        s += f'<rect x="{a:.0f}" y="{y:.0f}" width="{L:.0f}" height="{rnd.uniform(1.5,4):.1f}" fill="{col}" opacity="{op}"/>'
    return s

def subtitle(text, y=740, size=26, col="#fff"):
    return (f'<text x="{PW/2}" y="{y}" text-anchor="middle" font-family="{FONT}" font-weight="800" font-size="{size}" '
            f'fill="{col}" stroke="{INK}" stroke-width="5" paint-order="stroke">{text}</text>')

def skyline(y, col, seed=3, x0=0, x1=PW, hmin=80, hmax=320, windows=None):
    import random
    rnd = random.Random(seed)
    s = ""; x = x0 - 10
    while x < x1:
        w = rnd.uniform(34, 80); h = rnd.uniform(hmin, hmax)
        s += f'<rect x="{x:.0f}" y="{y-h:.0f}" width="{w:.0f}" height="{h+400:.0f}" fill="{col}"/>'
        if windows:
            for wy in range(int(y - h + 14), int(y), 22):
                for wx in range(int(x + 6), int(x + w - 8), 14):
                    if rnd.random() < 0.35:
                        s += f'<rect x="{wx}" y="{wy}" width="6" height="9" fill="{windows}" opacity="{rnd.uniform(.4,.95):.2f}"/>'
        x += w + rnd.uniform(0, 6)
    return s

def sam_back(x, y, s=1.0, hood="#2b3a55", hair="#17131c", rim=None):
    """Sam seen from behind / three-quarter: spiky hair, hoodie. (x,y)=feet centre."""
    r = f'stroke="{rim}" stroke-width="3"' if rim else ""
    return f'''<g transform="translate({x},{y}) scale({s})">
  <path d="M-34 0 L-30 -120 L30 -120 L34 0 Z" fill="#1b1d24" {ink(4)}/>
  <path d="M-62 -110 Q-66 -200 -40 -230 Q0 -250 40 -230 Q66 -200 62 -110 L48 -104 L44 -150 L-44 -150 L-48 -104 Z" fill="{hood}" {ink(4)}/>
  <path d="M-46 -150 Q-60 -170 -56 -200 M46 -150 Q60 -170 56 -200" fill="none" {ink(3)}/>
  <path d="M-30 -226 Q-40 -300 0 -306 Q40 -300 30 -226 Z" fill="#c98f6b" {ink(4)}/>
  <path d="M-36 -250 L-52 -262 L-36 -278 L-50 -300 L-24 -298 L-22 -326 L0 -306 L14 -332 L22 -302 L48 -310 L38 -284 L54 -270 L36 -256 Q20 -240 0 -244 Q-20 -240 -36 -250 Z" fill="{hair}" {ink(4)} />
  <path d="M-40 -236 Q0 -214 40 -236" fill="none" {ink(3)}/>
  {f'<path d="M62 -110 Q66 -200 40 -230" fill="none" {r}/>' if rim else ''}
</g>'''

def kaiju(x, y, s=1.0, body="#1c1626", eye="#ff3b2f", glow=True, seed=0):
    g = f'<circle cx="0" cy="-330" r="60" fill="{eye}" opacity="0.35" filter="url(#blur12)"/>' if glow else ""
    return f'''<g transform="translate({x},{y}) scale({s})">
  {g}
  <path d="M-260 0 Q-240 -160 -170 -230 L-190 -300 L-140 -260 Q-120 -330 -80 -360 L-90 -420 L-50 -380 Q-20 -410 20 -400 L30 -450 L60 -392 Q110 -380 130 -330 L180 -350 L160 -290 Q220 -240 240 -150 Q260 -80 280 0 Z" fill="{body}" {ink(5)}/>
  <path d="M-120 -250 Q-60 -280 -40 -200 M60 -300 Q120 -260 100 -180" fill="none" stroke="#3a2f4a" stroke-width="6"/>
  <path d="M-40 -340 L-6 -330 L-30 -318 Z" fill="{eye}"/>
  <path d="M40 -342 L74 -334 L50 -320 Z" fill="{eye}"/>
  <path d="M-30 -300 L-20 -284 L-8 -300 L4 -282 L16 -300 L28 -283 L40 -300 L52 -284 L62 -300" fill="none" stroke="#e8e2d0" stroke-width="4"/>
</g>'''

def mech(x, y, s=1.0, main="#f2a93b", dark="#b56d1a", box=True):
    """Chunky old construction mech, running pose. (x,y) = ground under feet."""
    return f'''<g transform="translate({x},{y}) scale({s})">
  <path d="M-30 -150 L-80 -40 L-60 0 L-10 0 L-20 -30 L10 -140 Z" fill="{dark}" {ink(5)}/>
  <path d="M30 -150 L90 -80 L120 -20 L150 -20 L140 -50 L70 -150 Z" fill="{main}" {ink(5)}/>
  <rect x="-70" y="-330" width="150" height="190" rx="26" fill="{main}" {ink(5)}/>
  <path d="M-70 -200 L80 -200" {ink(3)}/>
  <rect x="-50" y="-300" width="60" height="44" rx="6" fill="#2b2f3a" {ink(3)}/>
  <rect x="-44" y="-294" width="20" height="10" fill="#bfe8ff"/>
  <rect x="-40" y="-400" width="90" height="72" rx="18" fill="{main}" {ink(5)}/>
  <rect x="-26" y="-380" width="64" height="20" rx="8" fill="#6ff0ff" {ink(3)}/>
  <circle cx="-20" cy="-212" r="9" fill="#e94b3c" {ink(2)}/>
  <text x="18" y="-160" font-family="{FONT}" font-weight="900" font-size="22" fill="{INK}">HK-07</text>
  <path d="M-70 -300 L-140 -240 L-120 -200 L-60 -250 Z" fill="{dark}" {ink(5)}/>
  <path d="M80 -300 L150 -330 L190 -300 L170 -280 L130 -296 L90 -260 Z" fill="{dark}" {ink(5)}/>
  {('<g transform="translate(150,-370) rotate(-8)"><rect x="0" y="0" width="120" height="70" rx="6" fill="#e9433b" ' + ink(5) + '/><text x="60" y="44" text-anchor="middle" font-family="' + FONT + '" font-weight="900" font-size="24" fill="#fff">HAKOBU</text></g>') if box else ''}
  <path d="M-60 -330 L-90 -360 M60 -330 L40 -366" {ink(4)}/>
  <path d="M-30 -200 l16 12 M10 -200 l16 12 M50 -200 l16 12" stroke="{dark}" stroke-width="4"/>
</g>'''

DEFS = '''<defs>
<filter id="blur12"><feGaussianBlur stdDeviation="12"/></filter>
<filter id="blur6"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="blur3"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0.07 0"/></filter>
</defs>'''

def strip(name, label_col, panels, captions):
    body = ""
    for i, p in enumerate(panels):
        x = G + i * (PW + G); y = G + 56
        body += f'''<g transform="translate({x},{y})">
<clipPath id="c{name}{i}"><rect width="{PW}" height="{PH}" rx="10"/></clipPath>
<g clip-path="url(#c{name}{i})">{p}<rect width="{PW}" height="{PH}" filter="url(#grain)"/></g>
<rect width="{PW}" height="{PH}" rx="10" fill="none" stroke="{INK}" stroke-width="6"/>
</g>
<text x="{x+4}" y="{G+34}" font-family="{FONT}" font-weight="800" font-size="22" fill="{label_col}">REEL {i+1}</text>
<text x="{x+100}" y="{G+34}" font-family="{FONT}" font-weight="500" font-size="20" fill="#c9c3d6">{captions[i]}</text>'''
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{DEFS}<rect width="{W}" height="{H}" fill="#0d0b12"/>{body}</svg>'

# ---------------- SURGE ----------------
def surge():
    p1 = f'''<rect width="{PW}" height="{PH}" fill="#3a1630"/>
<rect width="{PW}" height="{PH}" fill="#ff5a3c" opacity="0.18"/>
<g filter="url(#blur6)">{skyline(520, "#1d0f22", seed=5, windows="#ffb24d")}</g>
<circle cx="360" cy="240" r="120" fill="#ff3b2f" opacity="0.35" filter="url(#blur12)"/>
<g opacity="0.85" filter="url(#blur3)">{kaiju(330, 520, 0.55, body="#120a18")}</g>
<path d="M60 900 L80 470 Q90 420 140 418 L330 418 Q380 420 384 470 L400 900 Z" fill="#e8d6c4" {ink(5)}/>
<rect x="96" y="250" width="262" height="470" rx="34" fill="#15131c" {ink(6)}/>
<rect x="110" y="268" width="234" height="434" rx="22" fill="#fff6ea"/>
<rect x="110" y="268" width="234" height="70" rx="22" fill="#e9433b"/>
<text x="227" y="314" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="30" fill="#fff">HAKOBU</text>
<text x="227" y="392" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="44" fill="#e9433b">SURGE x30</text>
<text x="227" y="432" text-anchor="middle" font-family="{FONT}" font-weight="700" font-size="20" fill="#3a2a2a">Kaiju "UME" in Namba</text>
<text x="227" y="460" text-anchor="middle" font-family="{FONT}" font-weight="500" font-size="18" fill="#6a5a5a">1 x Ramen · 2.1 km</text>
<text x="227" y="530" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="46" fill="#121016">¥30,000</text>
<rect x="134" y="590" width="186" height="64" rx="32" fill="#2fbf71" {ink(4)}/>
<text x="227" y="632" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="28" fill="#fff">ACCEPT</text>
<path d="M300 900 L290 700 Q286 640 250 630 Q214 626 220 670 L236 760 L250 900 Z" fill="#d9b49a" {ink(5)}/>
<path d="M248 640 Q232 646 230 664" fill="none" {ink(3)}/>
{subtitle("Rent is due. Pay triples.", 770)}'''

    p2 = f'''<rect width="{PW}" height="{PH}" fill="#ff8a3d"/>
<rect y="300" width="{PW}" height="500" fill="#ff5a3c" opacity="0.5"/>
<circle cx="300" cy="300" r="170" fill="#ffd36b" opacity="0.8" filter="url(#blur12)"/>
{kaiju(300, 600, 0.95, body="#2a1630")}
{skyline(620, "#3a1430", seed=9, hmin=60, hmax=200)}
{speed_lines(130, 520, n=46, r0=250, col="#fff", op=0.28)}
<rect y="600" width="{PW}" height="200" fill="#26101e"/>
{mech(150, 690, 0.95)}
<path d="M0 690 L{PW} 690" {ink(4)}/>
{hlines(0, PW, 640, 790, 14, col="#ffd9a8", op=0.5)}
<text x="290" y="150" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="52" fill="#fff" stroke="{INK}" stroke-width="8" paint-order="stroke" transform="rotate(8 290 150)">GRRAA!</text>
{subtitle("Obaachan, don't fail me now.", 770, 24)}'''

    p3 = f'''<rect width="{PW}" height="{PH}" fill="#2a2430"/>
<circle cx="225" cy="330" r="240" fill="#6b5a70" opacity="0.6" filter="url(#blur12)"/>
<circle cx="120" cy="250" r="110" fill="#8c7d8f" opacity="0.5" filter="url(#blur12)"/>
<circle cx="350" cy="420" r="130" fill="#8c7d8f" opacity="0.45" filter="url(#blur12)"/>
{speed_lines(225, 330, n=36, r0=120, col="#ffe1b0", op=0.35, seed=7)}
<g transform="translate(225,330) rotate(-20)">
  <rect x="-80" y="-60" width="170" height="120" rx="26" fill="#f2a93b" {ink(6)}/>
  <path d="M-80 -20 L90 -20 M-80 20 L90 20 M-30 -60 L-30 60 M30 -60 L30 60" {ink(4)}/>
  <rect x="90" y="-46" width="120" height="92" fill="#b56d1a" {ink(6)}/>
</g>
<text x="120" y="160" font-family="{FONT}" font-weight="900" font-size="64" fill="#ffe14a" stroke="{INK}" stroke-width="9" paint-order="stroke" transform="rotate(-10 120 160)">BOOM</text>
<rect x="30" y="510" width="390" height="190" rx="18" fill="#fff" {ink(5)}/>
<text x="56" y="562" font-family="{FONT}" font-size="40" fill="#f5b400">★<tspan fill="#cfcfcf">★★★★</tspan></text>
<text x="56" y="608" font-family="{FONT}" font-weight="700" font-size="22" fill="#121016">"Driver punched the monster.</text>
<text x="56" y="638" font-family="{FONT}" font-weight="700" font-size="22" fill="#121016">Food was cold."</text>
<text x="56" y="678" font-family="{FONT}" font-weight="500" font-size="17" fill="#777">Tip: ¥0 · Customer in Namba</text>
{subtitle("Saved Osaka. 1 star.", 770)}'''
    return strip("surge", "#ff8a3d", [p1, p2, p3], ["The surge alert", "The delivery", "The rating"])

# ---------------- KONBINI 24 ----------------
def konbini():
    p1 = f'''<rect width="{PW}" height="{PH}" fill="#0c1430"/>
<rect y="0" width="{PW}" height="120" fill="#1a1f3a"/>
<rect x="0" y="110" width="{PW}" height="40" fill="#2a2f4a" {ink(4)}/>
<rect x="30" y="150" width="26" height="420" fill="#2a2f4a" {ink(4)}/><rect x="394" y="150" width="26" height="420" fill="#2a2f4a" {ink(4)}/>
<rect x="60" y="80" width="330" height="30" fill="#4a5070" {ink(3)}/>
<rect x="66" y="56" width="90" height="30" rx="4" fill="#88d36b" {ink(3)}/><rect x="160" y="56" width="90" height="30" rx="4" fill="#88d36b" {ink(3)}/><rect x="254" y="56" width="90" height="30" rx="4" fill="#88d36b" {ink(3)}/>
<rect x="60" y="220" width="330" height="70" fill="#ffffff" {ink(4)}/>
<rect x="60" y="220" width="330" height="18" fill="#2fbf71"/><rect x="60" y="272" width="330" height="18" fill="#e9433b"/>
<text x="225" y="266" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="30" fill="#121016">KONBINI 24</text>
<rect x="60" y="290" width="330" height="290" fill="#e9fff2" {ink(4)}/>
<circle cx="225" cy="440" r="210" fill="#d6ffe4" opacity="0.6" filter="url(#blur12)"/>
<path d="M150 300 L150 580 M300 300 L300 580" {ink(3)}/>
<path d="M172 580 L170 470 Q160 420 190 390 L178 340 L200 372 Q224 360 248 372 L272 340 L258 392 Q290 420 280 470 L278 580 Z" fill="#0b0a12"/>
<circle cx="210" cy="402" r="5" fill="#ffd23a"/><circle cx="240" cy="402" r="5" fill="#ffd23a"/>
<rect x="0" y="580" width="{PW}" height="220" fill="#151a30"/>
<path d="M0 580 L{PW} 580" {ink(4)}/>
<rect x="60" y="590" width="330" height="40" fill="#d6ffe4" opacity="0.25"/>
<rect x="300" y="160" width="120" height="44" rx="8" fill="#121016" {ink(3)}/>
<text x="360" y="192" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-weight="800" font-size="26" fill="#ff5050">3:14</text>
<text x="70" y="200" font-family="{FONT}" font-weight="900" font-size="34" fill="#fff" stroke="{INK}" stroke-width="7" paint-order="stroke" transform="rotate(-8 70 200)">♪ pin-pon</text>
{subtitle("“Do you sell phone chargers?”", 700, 25)}'''

    p2 = f'''<rect width="{PW}" height="{PH}" fill="#d8efe0"/>
<rect width="{PW}" height="{PH}" fill="#9fd4b4" opacity="0.4"/>
<path d="M0 250 Q225 120 450 250 L450 0 L0 0 Z" fill="#1a1026"/>
<path d="M40 210 Q225 360 410 210 Q225 250 40 210 Z" fill="#7a1022" {ink(5)}/>
<path d="M60 214 L76 250 L92 218 L108 256 L124 222 L140 260 L156 224 L172 262 L188 226 L204 264 L220 226 L236 264 L252 226 L268 262 L284 224 L300 260 L316 222 L332 256 L348 218 L364 250 L380 214" fill="#f5f1e6" {ink(3)}/>
<circle cx="140" cy="130" r="18" fill="#ffd23a"/><circle cx="310" cy="130" r="18" fill="#ffd23a"/>
<circle cx="140" cy="130" r="40" fill="#ffd23a" opacity="0.35" filter="url(#blur6)"/><circle cx="310" cy="130" r="40" fill="#ffd23a" opacity="0.35" filter="url(#blur6)"/>
<rect x="40" y="420" width="370" height="230" rx="16" fill="#2a2f3a" {ink(6)}/>
<rect x="64" y="444" width="322" height="182" rx="8" fill="#0f2a1a"/>
<text x="86" y="500" font-family="'JetBrains Mono', monospace" font-weight="800" font-size="34" fill="#5dff9a">COFFEE  ¥150</text>
<text x="86" y="550" font-family="'JetBrains Mono', monospace" font-weight="800" font-size="24" fill="#ff5050">...or 1 YEAR</text>
<text x="86" y="586" font-family="'JetBrains Mono', monospace" font-weight="800" font-size="24" fill="#ff5050">OF YOUR LIFE</text>
<rect x="0" y="650" width="{PW}" height="150" fill="#b9c4bd" {ink(4)}/>
<rect x="290" y="600" width="70" height="90" rx="10" fill="#c78a3a" {ink(4)}/><rect x="290" y="624" width="70" height="30" fill="#f2e6d0"/>
{subtitle("Card or cash?", 760)}'''

    p3 = f'''<rect width="{PW}" height="{PH}" fill="#3a0a10"/>
<rect width="{PW}" height="{PH}" fill="#ff2a2a" opacity="0.25"/>
<path d="M0 0 L120 180 L120 620 L0 800 Z" fill="#5a1418" {ink(4)}/>
<path d="M450 0 L330 180 L330 620 L450 800 Z" fill="#5a1418" {ink(4)}/>
<path d="M0 120 L120 250 M0 300 L120 380 M0 480 L120 510 M450 120 L330 250 M450 300 L330 380 M450 480 L330 510" {ink(3)}/>
<rect x="120" y="180" width="210" height="440" fill="#2a0508"/>
<path d="M140 620 L150 300 L120 250 L180 270 L200 220 L215 280 L230 300 L222 620 Z" fill="#090408"/>
<path d="M230 620 L240 340 L290 260 L300 320 L330 300 L312 380 L322 620 Z" fill="#090408"/>
<circle cx="178" cy="300" r="6" fill="#ffd23a"/><circle cx="292" cy="320" r="6" fill="#58f0ff"/>
<rect x="0" y="620" width="{PW}" height="180" fill="#2a0a0e"/>
{sam_back(225, 800, 1.05, hood="#2f6b4a", rim="#ff5a5a")}
<path d="M300 520 L340 800" stroke="#c9a46a" stroke-width="10"/>
<rect x="200" y="20" width="50" height="16" fill="#ff3030" filter="url(#blur3)"/>
{subtitle("“Sir. Not in my store.”", 180, 28)}'''
    return strip("konbini", "#5dff9a", [p1, p2, p3], ["3:14 AM customer", "The price", "The one rule"])

# ---------------- LAST TRAIN ZERO ----------------
def train():
    p1 = f'''<rect width="{PW}" height="{PH}" fill="#1a2a2a"/>
<rect width="{PW}" height="{PH}" fill="#8fd3a6" opacity="0.08"/>
<path d="M0 0 L{PW} 0 L{PW} 90 L0 90 Z" fill="#cfd8d4" {ink(4)}/>
<rect x="60" y="120" width="330" height="110" rx="10" fill="#0a0a0a" {ink(5)}/>
<text x="225" y="166" text-anchor="middle" font-family="{FONT}" font-weight="800" font-size="20" fill="#ffb03a">NEXT</text>
<text x="225" y="212" text-anchor="middle" font-family="{JP}" font-size="40" fill="#ff4040">次は ... YOU</text>
<rect x="60" y="182" width="120" height="6" fill="#ff4040" opacity="0.6"/>
<path d="M90 90 L90 250 M180 90 L180 250 M270 90 L270 250 M360 90 L360 250" stroke="#9aa" stroke-width="3"/>
<g fill="none" {ink(4)}><circle cx="90" cy="270" r="20"/><circle cx="180" cy="270" r="20"/><circle cx="270" cy="270" r="20"/><circle cx="360" cy="270" r="20"/></g>
<rect x="0" y="330" width="{PW}" height="190" fill="#0b1416" {ink(4)}/>
<rect x="20" y="350" width="410" height="150" rx="8" fill="#14262a"/>
<circle cx="340" cy="420" r="40" fill="#8fd3a6" opacity="0.2" filter="url(#blur6)"/>
{hlines(20, 430, 360, 490, 10, col="#8fd3a6", op=0.35)}
<rect x="0" y="520" width="{PW}" height="120" fill="#2e7d4f" {ink(4)}/>
<rect x="0" y="520" width="{PW}" height="20" fill="#3fa067"/>
<rect x="0" y="640" width="{PW}" height="160" fill="#202826"/>
{subtitle("0:31 AM. Train keeps going.", 740, 24)}'''

    p2 = f'''<rect width="{PW}" height="{PH}" fill="#20302c"/>
<rect x="0" y="560" width="{PW}" height="240" fill="#2e7d4f" {ink(4)}/>
<path d="M120 800 L110 520 Q110 420 225 410 Q340 420 340 520 L330 800 Z" fill="#30333f" {ink(5)}/>
<path d="M225 410 L200 520 L225 560 L250 520 Z" fill="#e8e4da" {ink(3)}/>
<path d="M216 460 L225 560 L234 460 Z" fill="#7a1022"/>
<circle cx="225" cy="300" r="100" fill="#d9b49a" {ink(5)}/>
<path d="M128 280 Q140 190 225 186 Q310 190 322 280 Q300 230 225 232 Q150 230 128 280 Z" fill="#2a2a2a" {ink(4)}/>
<g {ink(4)}><circle cx="185" cy="300" r="30" fill="#f6f1df"/><circle cx="265" cy="300" r="30" fill="#f6f1df"/></g>
<path d="M185 300 L185 280 M185 300 L200 306 M265 300 L265 276 M265 300 L250 312" {ink(3)}/>
<circle cx="185" cy="300" r="50" fill="#f6f1df" opacity="0.25" filter="url(#blur6)"/><circle cx="265" cy="300" r="50" fill="#f6f1df" opacity="0.25" filter="url(#blur6)"/>
<path d="M200 360 Q225 372 250 360" fill="none" {ink(3)}/>
<path d="M450 470 Q380 470 340 500 L330 540 Q370 540 450 530 Z" fill="#2b3a55" {ink(5)}/>
<path d="M336 498 Q300 496 296 520 Q300 540 332 540 Z" fill="#c98f6b" {ink(4)}/>
{subtitle("“Sir... last stop.”", 720, 28)}'''

    p3 = f'''<rect width="{PW}" height="{PH}" fill="#0a0a12"/>
<ellipse cx="225" cy="330" rx="200" ry="230" fill="#050508" {ink(5)}/>
<ellipse cx="225" cy="330" rx="120" ry="60" fill="#ffcf3a" opacity="0.25" filter="url(#blur12)"/>
<ellipse cx="225" cy="330" rx="90" ry="36" fill="#ffcf3a" {ink(4)}/>
<ellipse cx="225" cy="330" rx="14" ry="34" fill="#121016"/>
<rect x="110" y="70" width="230" height="60" rx="6" fill="#f2f2ee" {ink(4)}/>
<circle cx="146" cy="100" r="20" fill="#2e7d4f" {ink(3)}/><text x="146" y="108" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="20" fill="#fff">31</text>
<text x="250" y="112" text-anchor="middle" font-family="{JP}" font-size="34" fill="#121016">？？？駅</text>
<path d="M0 560 L{PW} 560 L{PW} 800 L0 800 Z" fill="#30302e" {ink(4)}/>
<rect x="0" y="560" width="{PW}" height="16" fill="#ffd23a"/>
{sam_back(260, 770, 0.6, hood="#24465a")}
<circle cx="318" cy="640" r="40" fill="#ffcf6a" opacity="0.6" filter="url(#blur6)"/><rect x="306" y="626" width="24" height="30" rx="4" fill="#ffcf6a" {ink(3)}/>
<rect x="290" y="170" width="150" height="66" rx="10" fill="#121016" {ink(4)}/>
<text x="365" y="216" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-weight="800" font-size="40" fill="#ff5050">4:29</text>
{subtitle("First train in 60 seconds.", 520, 24)}'''
    return strip("train", "#3fa067", [p1, p2, p3], ["The wrong station", "The passenger", "The countdown"])

# ---------------- LIGHTS OUT ----------------
def lights():
    p1 = f'''<rect width="{PW}" height="{PH}" fill="#0d0a14"/>
<rect x="0" y="0" width="200" height="{PH}" fill="#1a1426"/>
<rect x="250" y="0" width="200" height="{PH}" fill="#16121f"/>
<path d="M200 0 L200 800 M250 0 L250 800" {ink(4)}/>
<rect x="20" y="80" width="60" height="140" rx="6" fill="#ff3d9a" opacity="0.8" filter="url(#blur3)"/>
<text x="50" y="130" text-anchor="middle" font-family="{JP}" font-size="34" fill="#fff">バ</text><text x="50" y="180" text-anchor="middle" font-family="{JP}" font-size="34" fill="#fff">ー</text>
<path d="M300 760 L260 360 Q262 260 330 220 L320 140 L350 200 Q370 190 390 200 L420 140 L410 220 Q470 270 460 360 L430 760 Z" fill="#050308" opacity="0.95"/>
<circle cx="352" cy="250" r="7" fill="#ff2a4a"/><circle cx="392" cy="252" r="7" fill="#ff2a4a"/>
<circle cx="372" cy="250" r="40" fill="#ff2a4a" opacity="0.35" filter="url(#blur6)"/>
{sam_back(160, 800, 1.15, hood="#3a2a55", rim="#58f0ff")}
<circle cx="250" cy="640" r="80" fill="#58f0ff" opacity="0.25" filter="url(#blur12)"/>
<rect x="212" y="580" width="76" height="130" rx="12" fill="#15131c" {ink(4)}/>
<rect x="219" y="588" width="62" height="114" rx="7" fill="#58f0ff" opacity="0.9"/>
<text x="250" y="656" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="28" fill="#e9433b">1%</text>
{subtitle("Don't look behind you.", 380, 26)}'''

    p2 = f'''<rect width="{PW}" height="{PH}" fill="#0a0b1c"/>
<circle cx="380" cy="120" r="40" fill="#e9e6ff" opacity="0.8"/>
<g>{skyline(560, "#1a1838", seed=21, hmin=120, hmax=380, windows="#ffe08a")}</g>
<rect x="0" y="0" width="230" height="560" fill="#000" opacity="0.88"/>
<path d="M230 0 L230 560" stroke="#58f0ff" stroke-width="3" opacity="0.6"/>
<rect x="0" y="560" width="{PW}" height="240" fill="#05050c"/>
<path d="M0 560 L{PW} 560" {ink(4)}/>
<text x="120" y="640" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="30" fill="#fff" stroke="{INK}" stroke-width="7" paint-order="stroke">BLACKOUT</text>
<path d="M160 330 L200 330 M150 360 L210 360" stroke="#58f0ff" stroke-width="5"/>
<path d="M196 318 L226 330 L196 342 Z M206 348 L236 360 L206 372 Z" fill="#58f0ff"/>
<rect x="300" y="590" width="120" height="70" rx="10" fill="#121016" {ink(4)}/>
<text x="360" y="640" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-weight="800" font-size="42" fill="#ff3d9a">0:08</text>
{subtitle("The dark is coming to his block.", 740, 22)}'''

    p3 = f'''<rect width="{PW}" height="{PH}" fill="#000"/>
<path d="M150 170 L180 160 L210 172 Q180 186 150 170 Z" fill="#ff2a4a"/>
<path d="M240 172 L270 160 L300 170 Q270 186 240 172 Z" fill="#ff2a4a"/>
<ellipse cx="225" cy="172" rx="120" ry="40" fill="#ff2a4a" opacity="0.3" filter="url(#blur12)"/>
<path d="M120 260 L140 300 L160 262 L180 304 L200 264 L225 306 L250 264 L270 304 L290 262 L310 300 L330 260" fill="none" stroke="#2a2a2a" stroke-width="5"/>
<ellipse cx="225" cy="760" rx="110" ry="20" fill="#ffffff" opacity="0.12"/>
{sam_back(225, 760, 0.55, hood="#1e1b26", rim="#ff2a4a")}
<rect x="268" y="660" width="36" height="46" fill="#f2f2ee" {ink(2)}/>
{subtitle("“Show us.”", 520, 34)}'''
    return strip("lights", "#ff3d9a", [p1, p2, p3], ["Battery 1%", "The blackout", "The contract"])

# ---------------- FORECAST ----------------
JAPAN = "M300 120 L330 110 L350 150 L330 200 L300 210 L290 240 L310 300 L300 360 L270 420 L230 470 L180 500 L130 520 L110 560 L80 570 L70 540 L100 500 L150 470 L200 440 L240 390 L260 330 L260 270 L280 220 L280 160 Z M60 580 L100 590 L110 640 L80 670 L50 640 Z"

def forecast():
    p1 = f'''<rect width="{PW}" height="{PH}" fill="#0b3a6a"/>
<rect width="{PW}" height="{PH}" fill="#1e70c9" opacity="0.4"/>
<path d="{JAPAN}" fill="#5fae6a" {ink(4)} transform="translate(30,0)"/>
<g transform="translate(345,300)"><circle r="44" fill="#ff3030" opacity="0.4" filter="url(#blur6)"/><circle r="26" fill="#ff3030" {ink(3)}/><text y="9" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="24" fill="#fff">K</text></g>
<path d="M400 340 Q380 360 336 350" fill="none" stroke="#ff3030" stroke-width="6" stroke-dasharray="10 6"/>
<text x="400" y="260" text-anchor="end" font-family="{FONT}" font-weight="800" font-size="20" fill="#fff">Matsushima</text>
{sam_back(120, 800, 1.2, hood="#2a2f3a")}
<path d="M170 560 L300 330" {ink(10)}/><path d="M170 560 L300 330" stroke="#2a2f3a" stroke-width="6"/>
<rect x="0" y="640" width="{PW}" height="110" fill="#e9433b"/>
<rect x="0" y="640" width="150" height="110" fill="#121016"/>
<text x="75" y="702" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="22" fill="#fff">LIVE</text>
<text x="170" y="684" font-family="{FONT}" font-weight="900" font-size="24" fill="#fff">KAIJU FORECAST</text>
<text x="170" y="722" font-family="{FONT}" font-weight="600" font-size="20" fill="#ffe0de">Landfall 6:12 AM · 120 m</text>
<text x="20" y="60" font-family="{FONT}" font-weight="900" font-size="26" fill="#fff">CH 9 SENDAI</text>'''

    p2 = f'''<rect width="{PW}" height="{PH}" fill="#101418"/>
<rect x="40" y="140" width="370" height="420" rx="10" fill="#050608" {ink(6)}/>
<text x="70" y="220" font-family="{FONT}" font-weight="600" font-size="24" fill="#9aa">...and clear skies</text>
<text x="70" y="256" font-family="{FONT}" font-weight="600" font-size="24" fill="#9aa">for the weekend.</text>
<text x="225" y="370" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="46" fill="#ff3030">STOP</text>
<text x="225" y="420" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="46" fill="#ff3030">TELLING</text>
<text x="225" y="470" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="46" fill="#ff3030">THEM.</text>
<rect x="40" y="380" width="370" height="6" fill="#ff3030" opacity="0.5"/>
<ellipse cx="225" cy="420" rx="170" ry="80" fill="#ff3030" opacity="0.18" filter="url(#blur12)"/>
<rect x="0" y="600" width="{PW}" height="200" fill="#1b2128"/>
<circle cx="90" cy="680" r="30" fill="#ff3030" {ink(3)}/><text x="140" y="690" font-family="{FONT}" font-weight="800" font-size="24" fill="#ff8080">ON AIR</text>
{subtitle("He keeps reading.", 770)}'''

    import random
    rnd = random.Random(12)
    icons = ""
    pts = [(150,200),(80,300),(380,180),(360,420),(60,460),(400,560),(120,640),(330,640),(250,110),(420,320),(30,220)]
    for (x, y) in pts:
        icons += f'<g transform="translate({x},{y})"><circle r="17" fill="#ff3030" {ink(3)}/><path d="M{rnd.choice([-1,1])*14} 14 l{rnd.choice([-1,1])*22} {rnd.choice([-1,1])*18}" stroke="#ff3030" stroke-width="4"/></g>'
    p3 = f'''<rect width="{PW}" height="{PH}" fill="#0b3a6a"/>
<rect width="{PW}" height="{PH}" fill="#1e70c9" opacity="0.35"/>
<path d="{JAPAN}" fill="#5fae6a" {ink(4)} transform="translate(30,40)"/>
{icons}
<g transform="translate(240,420)"><circle r="70" fill="#ff3030" opacity="0.35" filter="url(#blur12)"/><circle r="46" fill="#ff3030" {ink(5)}/>
<ellipse rx="30" ry="16" fill="#fff6c0" {ink(3)}/><ellipse rx="7" ry="15" fill="#121016"/></g>
<text x="225" y="80" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="28" fill="#fff" stroke="{INK}" stroke-width="7" paint-order="stroke">12 ACTIVE</text>
{subtitle("One of them is looking back.", 760, 24)}'''
    return strip("forecast", "#4fb0ff", [p1, p2, p3], ["Live on air", "The teleprompter", "The map"])

STRIPS = {"1-surge": surge, "2-konbini": konbini, "3-train": train, "4-lights": lights, "5-forecast": forecast}


for k,f in STRIPS.items():
    open(os.path.join(OUT,k+'.svg'),'w').write(f())
print(W,H)
