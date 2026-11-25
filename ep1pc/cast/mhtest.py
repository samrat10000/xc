import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import bpy, castlib as L, mh
sc=L.reset(); C=L.collection('T')
mix={'universal-male-young-minmuscle-minweight':1.0}
o,V=mh.build('Body',C,mix,groups=('body',))
ao=mh.rig('Z',C,V,[o])
L.smooth(o); s=o.modifiers.new('s','SUBSURF'); s.levels=1
m=L.mat_flat('clay',L.lin('#b9b1a3'),rough=.7); L.setmat(o,m)
L.studio(sc)
P=eval(os.environ['POSE'])
mh.pose(ao,P)
for i,(az,el) in enumerate([(30,8),(90,4),(0,4)]):
    L.camera(sc,(0,0,.9),3.2,az,el,lens=50); L.render(sc,f'out/t{i}.png',540,675,10)
