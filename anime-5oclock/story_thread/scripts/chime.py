import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make import *

HAND = "'Liberation Serif', serif"

def pole(x, y, s=1.0):
    return f'''<g transform="translate({x},{y}) scale({s})">
<rect x="-7" y="0" width="14" height="700" fill="#2a2228" {ink(4)}/>
<path d="M-8 30 L-70 6 L-70 66 L-8 50 Z" fill="#9aa0a6" {ink(4)}/>
<path d="M8 30 L70 6 L70 66 L8 50 Z" fill="#9aa0a6" {ink(4)}/>
<path d="M-8 100 L-70 76 L-70 136 L-8 120 Z" fill="#9aa0a6" {ink(4)}/>
<path d="M8 100 L70 76 L70 136 L8 120 Z" fill="#9aa0a6" {ink(4)}/>
<rect x="-18" y="170" width="36" height="60" rx="4" fill="#d8d2c0" {ink(3)}/>
</g>'''

def clothes(x, y, col):
    return f'''<g transform="translate({x},{y})"><path d="M-40 0 Q-30 -26 0 -24 Q30 -26 40 0 Q0 10 -40 0 Z" fill="{col}" {ink(3)}/>
<path d="M30 -4 l26 6 l-4 8 l-24 -4 Z" fill="#f2f2ee" {ink(2)}/></g>'''

def chime():
    sunset = f'''<rect width="{PW}" height="{PH}" fill="#f08a4b"/>
<rect y="0" width="{PW}" height="300" fill="#c9506a" opacity="0.55"/>
<circle cx="300" cy="420" r="80" fill="#ffd9a0"/>
<circle cx="300" cy="420" r="150" fill="#ffb070" opacity="0.5" filter="url(#blur12)"/>
<path d="M0 430 L80 360 L160 400 L250 330 L340 390 L450 340 L450 470 L0 470 Z" fill="#8a3a50"/>'''
    p1 = f'''{sunset}
<path d="M0 470 L{PW} 470 L{PW} 800 L0 800 Z" fill="#5a3040"/>
<path d="M120 800 L200 470 L250 470 L330 800 Z" fill="#7a4a52" {ink(3)}/>
<path d="M225 480 L225 500 M225 540 L225 570 M225 620 L225 660 M225 720 L225 780" stroke="#f2e6d0" stroke-width="5"/>
<rect x="20" y="400" width="90" height="120" fill="#3a2030" {ink(3)}/><rect x="340" y="390" width="110" height="140" fill="#3a2030" {ink(3)}/>
<rect x="360" y="420" width="40" height="70" fill="#ff6a3a"/><rect x="360" y="420" width="40" height="70" fill="#ffe0a0" opacity="0.4"/>
{pole(80, 120, 0.9)}
<path d="M300 560 L340 520 L360 540 M330 580 a26 26 0 1 0 1 0 M400 600 a26 26 0 1 0 1 0" fill="none" {ink(4)}/>
{clothes(170, 640, "#2b4a7a")}{clothes(300, 700, "#7a2b3a")}{clothes(110, 740, "#e8e4da")}
<rect x="250" y="250" width="160" height="62" rx="10" fill="#121016" {ink(4)}/>
<text x="330" y="294" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-weight="800" font-size="36" fill="#ffd23a">16:59</text>
<text x="175" y="170" font-family="{FONT}" font-weight="900" font-size="27" fill="#fff" stroke="{INK}" stroke-width="6" paint-order="stroke" transform="rotate(-6 175 170)">♪ ding... dong...</text>
{subtitle("Everyone heard the chime.", 560, 26)}
{subtitle("Except me.", 600, 26)}'''

    rules = ["1. Be indoors, ears covered, at 5:00.",
             "2. If the speaker says your name,", "    do not answer.",
             "3. Never pick up a ringing phone", "    that belongs to the gone.",
             "4. Don't count the bus stop.", "    There is always one more.",
             "5. Nothing red outside.",
             "6. Don't wave back.",
             "7. ~~~~~~~~~~ (torn out)"]
    lines = ""
    for i, r in enumerate(rules):
        col = "#8a1a1a" if i == len(rules) - 1 else "#1c2440"
        lines += f'<text x="70" y="{230 + i*38}" font-family="{HAND}" font-style="italic" font-weight="700" font-size="24" fill="{col}">{r}</text>'
    p2 = f'''<rect width="{PW}" height="{PH}" fill="#2a2420"/>
<rect width="{PW}" height="{PH}" fill="#f0a060" opacity="0.12"/>
<g transform="rotate(-3 225 400)">
<rect x="30" y="110" width="400" height="600" rx="8" fill="#f3ecd8" {ink(5)}/>
{"".join(f'<path d="M30 {y} L430 {y}" stroke="#a8c0e0" stroke-width="1.5"/>' for y in range(200, 700, 38))}
<path d="M62 110 L62 710" stroke="#e08080" stroke-width="2"/>
<text x="70" y="166" font-family="{HAND}" font-weight="700" font-size="30" fill="#1c2440">RULES - Kiriyama Koban</text>
{lines}
<path d="M300 640 Q340 660 330 700 L430 710 L430 600 Z" fill="#2a2420"/>
<circle cx="380" cy="190" r="26" fill="#8a1a1a" opacity="0.5"/>
</g>
<path d="M330 800 L350 600 Q356 570 380 572 Q400 576 396 610 L392 800 Z" fill="#d9b49a" {ink(4)}/>
{subtitle("The policeman left me this.", 770, 24)}'''

    p3 = f'''<rect width="{PW}" height="{PH}" fill="#0e0d1a"/>
<rect width="{PW}" height="340" fill="#3a2a50"/>
<path d="M0 340 L{PW} 340" {ink(3)}/>
<rect x="0" y="340" width="{PW}" height="460" fill="#1a1626"/>
<rect x="40" y="380" width="160" height="120" rx="6" fill="#ffe7a8" {ink(4)}/>
<rect x="40" y="380" width="160" height="120" rx="6" fill="#ff9a5a" opacity="0.25"/>
<path d="M120 380 L120 500 M40 440 L200 440" {ink(3)}/>
<circle cx="120" cy="440" r="140" fill="#ffd27a" opacity="0.18" filter="url(#blur12)"/>
{sam_back(120, 800, 1.15, hood="#2b3a55")}
<path d="M66 470 Q60 440 90 430 L150 430 Q180 440 174 470" fill="none" stroke="#e9433b" stroke-width="10"/>
<rect x="56" y="456" width="22" height="40" rx="8" fill="#e9433b" {ink(3)}/><rect x="162" y="456" width="22" height="40" rx="8" fill="#e9433b" {ink(3)}/>
{pole(350, 60, 0.75)}
<path d="M300 120 Q270 140 300 160 M285 100 Q240 140 285 180 M410 120 Q440 140 410 160 M425 100 Q470 140 425 180" fill="none" stroke="#ffd23a" stroke-width="4"/>
<rect x="215" y="250" width="225" height="72" rx="14" fill="#f7f3ea" {ink(4)}/>
<path d="M330 250 L350 214 L360 250 Z" fill="#f7f3ea" {ink(4)}/>
<text x="327" y="282" text-anchor="middle" font-family="{JP}" font-size="22" fill="#121016">サムくん、</text>
<text x="327" y="310" text-anchor="middle" font-family="{JP}" font-size="22" fill="#121016">外においで。</text>
{subtitle("“Sam-kun, come outside.”", 650, 24, "#ffd9a0")}
{subtitle("It's my mother's voice.", 690, 24)}'''
    return strip("chime", "#ffb070", [p1, p2, p3], ["5 PM, day one", "The rules", "The speaker knows my name"])

svg = chime()
open(os.path.join(OUT, "6-chime.svg"), "w").write(svg)
