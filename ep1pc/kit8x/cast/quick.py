import sys, os
sys.argv=[sys.argv[0]]
os.environ.setdefault('STAGE','body')
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'walker.py')).read())
import castlib as L, bpy
m=L.mat_flat('clay',L.lin('#b9b1a3'),rough=.7)
for o in bpy.data.objects:
    if o.type=='MESH' and not o.data.materials: L.setmat(o,m)
L.studio(sc)
views=os.environ.get('VIEWS','30:10:3.2:.95,0:5:3.2:.95,90:5:3.2:.95,25:3:.75:1.58').split(',')
for i,v in enumerate(views):
    az,el,d,tz=map(float,v.split(':'))
    L.camera(sc,(0,-.08,tz),d,az,el,lens=50 if d>1 else 70)
    L.render(sc,f'{OUT}/q{i}.png',w=540,h=675,samples=12)
