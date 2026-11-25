import ast, os
D = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(D, 'build_s05.py'); t = open(p, encoding='utf-8').read()
a = t.index("    gm, gmo, gb = load_char('grandma', (4.55, 4.40, 0.0), 180)"); b = t.index('# =============================== (b)')
t = t[:a] + open(os.path.join(D, 'cut_a_v2.txt'), encoding='utf-8').read() + '\n' + t[b:]
reps = [("kb_, kbo, kbb = load_char('kid_boy', (10.1, 1.4, 0.0), 0)", "kb_, kbo, kbb = load_char('kid_boy', (22.3, 1.7, 0.0), 0)"),
        ("kg_, kgo, kgb = load_char('kid_girl', (11.3, 2.0, 0.0), 0)", "kg_, kgo, kgb = load_char('kid_girl', (23.7, 2.3, 0.0), 0)"),
        ("(kb_, kbo, kbb, 10.1, 1.4, 0.0), (kg_, kgo, kgb, 11.3, 2.0, 1.3)", "(kb_, kbo, kbb, 22.3, 1.7, 0.0), (kg_, kgo, kgb, 23.7, 2.3, 1.3)"),
        ("y = K['y'] - 1.9 * ease((fp - 1) / (14.0 + K['ph'] * 2))", "y = K['y'] - 0.9 * ease((fp - 1) / (14.0 + K['ph'] * 2))              # stop ~3 m from the lens"),
        ("p = ROAD.matrix_world @ Vector((10.75, -1.55 + 0.06 * k, 0.78))", "p = ROAD.matrix_world @ Vector((23.0, -1.70 + 0.06 * k, 0.80))"),
        ("tgt = ROAD.matrix_world @ Vector((10.75, 4.0, 1.75))", "tgt = ROAD.matrix_world @ Vector((23.0, 6.0, 2.05))      # the bay and the low sun behind them"),
        ("SH.scale = (1, 1, L(0.18, 0.80, pull))", "SH.scale = (1, 1, L(0.18, 0.62, pull))                                    # ends at chest height: within reach"),
        ("R(sk, 'J_Bip_C_Spine', (1, 0, 0), L(-4, 10, pull)); R(sk, 'J_Bip_C_Chest', (1, 0, 0), L(-3, 6, pull))",
         "R(sk, 'J_Bip_C_Spine', (1, 0, 0), L(-4, 16, pull)); R(sk, 'J_Bip_C_Chest', (1, 0, 0), L(-3, 9, pull))")]
for x, y in reps:
    if x not in t: print('MISSING', x[:60])
    t = t.replace(x, y)
ast.parse(t); open(p, 'w', encoding='utf-8').write(t); print('patched, syntax ok')
