import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import castlib as L, mats as M, skull as SK
sc = L.reset(); C = L.collection('T')
d = SK.build(C)
for k in ('skull','jaw','teeth','antlers'): d[k].location.z = .45; L.apply_transform(d[k])
L.setmat(d['skull'], M.bone('Bone')); L.setmat(d['jaw'], d['skull'].data.materials[0])
L.setmat(d['teeth'], M.teeth_m('Teeth')); L.setmat(d['antlers'], M.flat('Antler', '#2a1e18') if hasattr(M,'flat') else d['skull'].data.materials[0])
for k in ('skull', 'jaw', 'antlers'): L.hull(d[k], C, t=.0015)
L.studio(sc)
for nm, az, el in (('a', 30, 10), ('b', 90, 5)):
    L.camera(sc, Vector((0, -.05, .62)), 1.2, az, el, lens=60)
    L.render(sc, f'out/skull_{nm}.png', w=500, h=600, samples=16)
