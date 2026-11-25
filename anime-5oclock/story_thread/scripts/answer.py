import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make import *
from chime import pole

def crack(x, y, s=1.0):
    return f'''<g transform="translate({x},{y}) scale({s})">
<path d="M0 -220 L-18 -140 L14 -90 L-26 -20 L10 40 L-14 120 L6 220 L30 120 L12 40 L44 -30 L8 -90 L34 -150 Z" fill="#c8f6ff" opacity="0.9"/>
<path d="M0 -220 L-18 -140 L14 -90 L-26 -20 L10 40 L-14 120 L6 220 L30 120 L12 40 L44 -30 L8 -90 L34 -150 Z" fill="#7fe8ff" opacity="0.6" filter="url(#blur12)" transform="scale(1.6)"/>
</g>'''

def answer():
    p1 = f'''<rect width="{PW}" height="{PH}" fill="#e2744a"/>
<rect width="{PW}" height="360" fill="#6a2d5a" opacity="0.7"/>
{crack(260, 230, 1.0)}
<path d="M0 470 L70 380 L150 420 L240 350 L330 410 L450 360 L450 520 L0 520 Z" fill="#4a2440" {ink(3)}/>
<rect x="0" y="520" width="{PW}" height="280" fill="#3a2a34"/>
{''.join(f'<path d="M{x} 800 L{225 + (x-225)*0.15:.0f} 520" stroke="#5a7a3a" stroke-width="3" opacity="0.7"/>' for x in range(-400, 900, 60))}
{pole(90, 140, 0.85)}
<path d="M150 170 Q130 190 150 210 M165 150 Q125 190 165 230" fill="none" stroke="#7fe8ff" stroke-width="4"/>
<text x="230" y="470" font-family="'JetBrains Mono', monospace" font-weight="800" font-size="30" fill="#7fe8ff" stroke="{INK}" stroke-width="5" paint-order="stroke">17:00:13</text>
{subtitle("13 seconds after the chime...", 640, 24)}
{subtitle("the sky plays it back.", 680, 24)}'''

    p2 = f'''<rect width="{PW}" height="{PH}" fill="#b8c4b0"/>
<rect width="{PW}" height="260" fill="#d8dcd0"/>
<path d="M0 260 L{PW} 260" stroke="#8a9a80" stroke-width="3"/>
<path d="M0 250 Q120 200 200 240 Q300 190 450 230 L450 262 L0 262 Z" fill="#9aa898"/>
<rect x="0" y="262" width="{PW}" height="538" fill="#6f8f6a"/>
{''.join(f'<path d="M0 {y} L{PW} {y+6}" stroke="#a8c0a0" stroke-width="3" opacity="0.8"/>' for y in range(290, 800, 34))}
<g transform="translate(225,560)">
<ellipse cx="0" cy="110" rx="120" ry="110" fill="#2f4a46" {ink(5)}/>
<ellipse cx="-120" cy="-60" rx="46" ry="90" transform="rotate(-25 -120 -60)" fill="#2f4a46" {ink(5)}/>
<ellipse cx="0" cy="-100" rx="46" ry="100" fill="#2f4a46" {ink(5)}/>
<ellipse cx="120" cy="-60" rx="46" ry="90" transform="rotate(25 120 -60)" fill="#2f4a46" {ink(5)}/>
<path d="M-170 -150 L-160 -190 L-140 -150 Z M-14 -200 L0 -250 L14 -200 Z M140 -150 L160 -190 L170 -150 Z" fill="#1a2a28" {ink(3)}/>
<ellipse cx="0" cy="110" rx="90" ry="70" fill="#7fe8ff" opacity="0.25"/>
<ellipse cx="0" cy="-100" rx="26" ry="60" fill="#7fe8ff" opacity="0.25"/>
</g>
{sam_back(390, 760, 0.3, hood="#2b3a55")}
<path d="M0 0 L{PW} 0 L{PW} 120 L0 120 Z" fill="#fff" opacity="0.2"/>
<text x="{PW/2}" y="120" text-anchor="middle" font-family="{FONT}" font-weight="800" font-size="22" fill="#fff" stroke="{INK}" stroke-width="5" paint-order="stroke">Day 13. Something walked through</text>
{subtitle("the rice fields last night.", 156, 22)}'''

    p3 = f'''<rect width="{PW}" height="{PH}" fill="#2a1430"/>
<rect width="{PW}" height="{PH}" fill="#e2744a" opacity="0.35"/>
<path d="M140 0 L120 120 L170 200 L110 320 L180 420 L150 560 L240 420 L210 320 L290 200 L240 120 L270 0 Z" fill="#0a0612" {ink(5)}/>
<path d="M140 0 L120 120 L170 200 L110 320 L180 420 L150 560" fill="none" stroke="#7fe8ff" stroke-width="8" filter="url(#blur3)"/>
<path d="M270 0 L240 120 L290 200 L210 320 L240 420 L150 560" fill="none" stroke="#7fe8ff" stroke-width="8" filter="url(#blur3)"/>
<ellipse cx="200" cy="250" rx="60" ry="26" fill="#ffd23a" opacity="0.4" filter="url(#blur6)"/>
<ellipse cx="200" cy="250" rx="42" ry="18" fill="#ffd23a" {ink(3)}/>
<ellipse cx="200" cy="250" rx="8" ry="17" fill="#121016"/>
<path d="M175 380 L190 400 L200 380 L212 402 L224 384" fill="none" stroke="#e8e2d0" stroke-width="4"/>
{skyline(800, "#120a18", seed=31, hmin=60, hmax=200)}
{pole(370, 420, 0.6)}
<text x="{PW/2}" y="640" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="44" fill="#ff3030" stroke="{INK}" stroke-width="7" paint-order="stroke">DAY 30</text>
{subtitle("Today the door is big enough.", 700, 24)}'''
    return strip("answer", "#7fe8ff", [p1, p2, p3], ["The answer", "The footprint", "The first kaiju"])

open(os.path.join(OUT, "7-answer.svg"), "w").write(answer())
