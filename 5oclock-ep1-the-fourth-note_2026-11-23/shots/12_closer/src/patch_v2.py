import ast, os
D = os.path.dirname(os.path.abspath(__file__)); p = os.path.join(D, 'build_s12.py'); t = open(p, encoding='utf-8').read()
street = '''
# ---------------- the real street the whip lands on (E1: never a bare plane) ----------------
import bmesh as _bm
ASPH = toon('asph12', (0.20, 0.18, 0.24), (0.40, 0.37, 0.42))
WHITE = toon('paint12', (0.62, 0.60, 0.62), (0.92, 0.90, 0.86))
WALL = toon('wall12', (0.38, 0.36, 0.42), (0.70, 0.68, 0.66), (1.0, 0.82, 0.6))
JOINT = toon('joint12', (0.26, 0.24, 0.30), (0.46, 0.44, 0.48))
HOUSE = toon('house12', (0.36, 0.30, 0.36), (0.72, 0.62, 0.56), (1.0, 0.8, 0.58))
ROOF = toon('roof12', (0.17, 0.17, 0.26), (0.34, 0.34, 0.46))
AX = SIDE.normalized(); AY = FWD.normalized(); Z = Vector((0, 0, 1))
BASIS = Matrix((AX, AY, Z)).transposed().to_4x4()


def sbox(name, c, size, mat, line=0.01):
    bm = _bm.new(); _bm.ops.create_cube(bm, size=1.0)
    _bm.ops.scale(bm, vec=size, verts=bm.verts)
    ob = mesh_obj(name, bm, mat, None, line); ob.matrix_world = Matrix.Translation(SPOS + AX * c[0] + AY * c[1] + Z * c[2]) @ BASIS
    return ob


sbox('road12', (22, 0.2, -0.02), (44, 7.0, 0.04), ASPH, 0)
for k in range(12):
    sbox('dash12_%d' % k, (3 + k * 3.6, 0.2, 0.005), (1.8, 0.12, 0.01), WHITE, 0)
for s_ in (-1, 1):
    sbox('kerb12_%d' % s_, (22, 0.2 + s_ * 3.55, 0.06), (44, 0.15, 0.14), WHITE, 0.006)
sbox('wall12', (22, 4.1, 0.75), (44, 0.16, 1.5), WALL, 0.01)
for k in range(44):
    sbox('wj12_%d' % k, (0.5 + k, 4.0, 0.75), (0.02, 0.02, 1.5), JOINT, 0)
for k in range(5):
    sbox('wjh12_%d' % k, (22, 4.0, 0.25 + k * 0.3), (44, 0.02, 0.02), JOINT, 0)
for k in range(6):
    x = 4 + k * 7.5; w = 6.0
    sbox('hs12_%d' % k, (x, 8.0, 2.6), (w, 6.0, 5.2), HOUSE, 0.02)
    sbox('hr12_%d' % k, (x, 8.0, 5.6), (w + 0.8, 6.6, 0.9), ROOF, 0.02)
    sbox('win12_%d' % k, (x - 1.2, 4.95, 3.4), (1.4, 0.05, 0.9), toon('win12', (0.30, 0.34, 0.44), (0.62, 0.70, 0.82)), 0.006)
for k in range(4):
    sbox('pole12_%d' % k, (3 + k * 11, -3.9, 4.0), (0.26, 0.26, 8.0), CONC, 0.012)
'''
reps = [("# the real street to the right of the mirror", street + "\n# the real street to the right of the mirror"),
        ("math.radians(66 * sg)", "math.radians(80 * sg)"),
        ("(('shopkeeper', SIDE * 4.2 + FWD * 0.6), ('grandma', SIDE * 5.6 - FWD * 0.4), ('kid_girl', SIDE * 3.2 - FWD * 1.1), ('kid_boy', SIDE * 6.8 + FWD * 1.5))",
         "(('shopkeeper', SIDE * 4.6 + FWD * 1.4), ('grandma', SIDE * 7.4 - FWD * 0.6), ('kid_girl', SIDE * 3.4 - FWD * 1.3), ('kid_boy', SIDE * 9.6 + FWD * 0.9))"),
        ("    p = P0 + Vector((0.004 * math.sin(f * 0.23), 0, 0.003 * math.sin(f * 0.37)))",
         "    p = P0.lerp(MPOS - FWD * 1.15, 0.55 * ease((f - 56) / 24.0)) + Vector((0.004 * math.sin(f * 0.23), 0, 0.003 * math.sin(f * 0.37)))   # past his head onto the glass")]
for x, y in reps:
    if x not in t: print('MISSING', x[:60])
    t = t.replace(x, y)
ast.parse(t); open(p, 'w', encoding='utf-8').write(t); print('ok')
