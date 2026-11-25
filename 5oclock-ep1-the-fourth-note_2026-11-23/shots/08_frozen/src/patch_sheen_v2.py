"""v2: drop the screen-space sheen stripes from the shop-window comps. They were fixed to the screen, so they slid across
the glass as the camera moved and read as shutter-like stutter (Sam, 08 @24 s, 10 @32 s). Idempotent."""
import ast
from pathlib import Path

EP = Path(__file__).resolve().parents[3] / 'shots'
OLD = ("        sheen = (np.clip(np.sin((xx + yy * 0.55) / 38.0), 0, 1) ** 12 * 0.10)[..., None]\n"
       "        refl = refl + sheen\n")
NEW = "        # v2: no screen-space sheen (it slid over the glass = stutter); the glass is a clean, stable mirror\n"
for s in ('05_ritual/src/comp_s05.py', '06_phone/src/comp_s06.py', '08_frozen/src/comp_s08.py', '09_silence/src/comp_s09.py',
          '10_eyes/src/comp_s10.py', '16_welcome/src/comp_s16.py'):
    p = EP / s; t = p.read_text(encoding='utf-8')
    if NEW in t: print('already', p.name); continue
    if t.count(OLD) != 1: raise SystemExit(f'MISSING in {p.name}')
    t = t.replace(OLD, NEW); ast.parse(t); p.write_text(t, encoding='utf-8'); print('ok', p.name)
