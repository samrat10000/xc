"""restore the Japanese text lines that a PowerShell 5.1 Get-Content (ANSI) re-save destroyed; reframe on the rules"""
import ast, os, re
D = os.path.dirname(os.path.abspath(__file__)); p = os.path.join(D, 'make_s18.py')
lines = open(p, encoding='utf-8').read().split('\n')
out = []
for ln in lines:
    s = ln.lstrip()
    if s.startswith("write_line(officer, MX + 30 * S, Y0 + 120 * S,"):
        ln = "write_line(officer, MX + 30 * S, Y0 + 120 * S, '霧山町 五時の規則', 64 * S, R, -2, FJB, ob)"
    elif s.startswith('RULES = ['):
        ln = "RULES = ['一、五時の歌が鳴ったら、外で動くな。', '二、鏡は壁に向けよ。', '三、耳をふさげ。', '四、名を呼ばれても、振り返るな。', '五、四つ目の音を数えるな。', '六、歌が三つで止まったら、家に入れ。']"
    elif s.startswith('fnt = ImageFont.truetype(FJB, 46 * S); dh.text('):
        ln = "fnt = ImageFont.truetype(FJB, 46 * S); dh.text((hx - 24 * S, hy - 54 * S), '田', font=fnt, fill=255); dh.text((hx - 24 * S, hy - 6 * S), '中', font=fnt, fill=255)"
    elif s.startswith("write_line(sam, MX + 34 * S,"):
        ln = "write_line(sam, MX + 34 * S, LINE0 + 6 * LH - 92 * S, '七、歌を終わらせるな。', 56 * S, RS, 4, FJB, sb)"
    elif s.startswith('k = ease((f - 1) / 84.0); s = 1.0 + 0.02 * k'):
        ln = "    k = ease((f - 1) / 84.0); s = 1.42 + 0.03 * k                          # framed on the rules + the torn line"
    elif s.startswith('cw, ch = PW / 1.12 / s, PH / 1.12 / s; cx = PW / 2'):
        ln = "    cw, ch = PW / 1.12 / s, PH / 1.12 / s; cx = PW / 2 + 40 * S + 6 * S * math.sin(f * 0.07); cy = (Y0 + LINE0 + 6 * LH) / 2 + 60 * S + 4 * S * math.sin(f * 0.05) + 30 * S * k"
    out.append(ln)
t = '\n'.join(out)
bad = [m.group(0) for m in re.finditer(r"[ÃÂâäåæçéèê][^\s']{0,3}", t)][:5]
print('possible mojibake left:', bad)
ast.parse(t); open(p, 'w', encoding='utf-8').write(t); print('ok')
