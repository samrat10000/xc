"""Paint independent exterior depth planes at 10% overscan."""
from pathlib import Path
import math
import numpy as np
from scipy.ndimage import gaussian_filter, zoom
from PIL import Image,ImageDraw,ImageFilter

OUT=Path(__file__).resolve().parent/'plates'
OUT.mkdir(exist_ok=True)
W,H=1188,2112
X,Y=np.meshgrid(np.linspace(-.05,1.05,W,dtype=np.float32),
                np.linspace(-.05,1.05,H,dtype=np.float32))
def tone(h):
    return np.array([int(h[i:i+2],16) for i in (0,2,4)],dtype=np.float32)/255
def png(name,a):
    Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).save(OUT/(name+'.png'))
def lay(name,rgb,alpha):
    png(name,np.dstack((rgb,np.broadcast_to(alpha,(H,W)))))
def smooth(a,b,x):
    t=np.clip((x-a)/(b-a),0,1)
    return t*t*(3-2*t)
def noise(seed,ny,nx):
    rg=np.random.default_rng(seed)
    src=rg.normal(0,1,(ny,nx)).astype(np.float32)
    return zoom(src,(H/ny,W/nx),order=3)[:H,:W]
grain=noise(7,84,99)*.010+noise(5,203,193)*.006
stops=[(-.05,'4e5778'),(.18,'7b83a0'),(.31,'a79bb0'),(.43,'d3a8aa'),(.51,'f0bfab'),(.58,'ffd8a9'),(1.05,'d49a8c')]
colors=np.stack([tone(c) for _,c in stops])
grad=np.stack([np.interp(Y,[x for x,_ in stops],colors[:,j]) for j in range(3)],axis=-1)
sun=np.exp(-(((X-1.04)/.45)**2+((Y-.40)/.19)**2))
png('sky',grad+grain[...,None]+sun[...,None]*tone('ffd384')*.19)

def blank():
    image=Image.new('RGBA',(W,H))
    return image,ImageDraw.Draw(image)
def p(x,y):
    return ((x+.05)/1.1*W,(y+.05)/1.1*H)
def trace(d,points,color,width):
    d.line([p(x,y) for x,y in points],fill=color,width=width,joint='curve')
def poly(d,points,color):
    d.polygon([p(x,y) for x,y in points],fill=color)

def fissure_canvas():
    image=Image.new('RGBA',(W*2,H*2))
    return image,ImageDraw.Draw(image)
def fissure_line(d,points,color,width):
    d.line([(x*2,y*2) for x,y in (p(*point) for point in points)],
           fill=color,width=width*2,joint='curve')
crack,d=fissure_canvas()
path=[(.157,.343),(.258,.330),(.294,.344),(.360,.319),(.43,.323),(.48,.300),(.545,.314),(.620,.287),(.655,.294),(.715,.278),(.751,.285),(.801,.251),(.874,.265),(1.055,.224)]
fissure_line(d,path,'#f5bfab',18)
glow=crack.filter(ImageFilter.GaussianBlur(48))
crack,d=fissure_canvas()
fissure_line(d,path,'#604459',8)
fissure_line(d,[(x,y-.0013) for x,y in path],'#fdd5bc',4)
fissure_line(d,[(x,y-.0022) for x,y in path],'#ffe2ca',2)
for branch in [[(.36,.319),(.388,.292),(.417,.284),(.446,.263)],[(.620,.287),(.651,.257),(.677,.254),(.706,.223)],[(.801,.251),(.824,.223),(.823,.210),(.861,.184)],[(.75,.285),(.774,.295),(.814,.295)]]:
    fissure_line(d,branch,'#c98595',3)
    fissure_line(d,branch[1:],'#f5bead',1)
Image.alpha_composite(glow,crack).resize((W,H),Image.Resampling.LANCZOS).save(OUT/'fissure.png')

def mountain(name,outline,cold,lit,seed,alpha=1.0):
    rng=np.random.default_rng(seed)
    x=outline[0][0]+(X[0]-X[0,0])/(X[0,-1]-X[0,0])*(outline[-1][0]-outline[0][0])
    ridge=np.interp(x,[v[0] for v in outline],[v[1] for v in outline])
    for freq,amp in ((21,.007),(65,.0026),(168,.0010),(390,.00041)):
        ridge+=np.interp(x,np.linspace(-.05,1.05,freq),rng.standard_normal(freq))*amp
    a=smooth(-.0008,.0008,Y-ridge)*alpha
    high=np.exp(-np.maximum(Y-ridge,0)*15)*(.38+.62*smooth(.27,1,X))
    face=(.10*np.sin(X*49+(Y-ridge)*33)+.075*noise(seed+15,52,40)) * np.exp(-abs(Y-ridge)*4)
    col=tone(cold)+(tone(lit)-tone(cold))*(high+face)[...,None]+grain[...,None]*.64
    lay(name,col,a)

mountain('far',[(-.05,.573),(.05,.541),(.13,.531),(.20,.497),(.32,.530),(.43,.512),(.49,.465),(.54,.460),(.59,.491),(.71,.510),(.82,.492),(.92,.435),(1.05,.480)],'82879e','d0a7a7',32,.94)
mountain('ridge',[(-.05,.627),(.09,.597),(.19,.546),(.29,.531),(.36,.553),(.44,.566),(.58,.548),(.66,.505),(.74,.478),(.79,.480),(.90,.529),(1.05,.518)],'646b86','a199aa',44)
mountain('valley',[(-.05,.660),(.08,.623),(.14,.590),(.20,.600),(.30,.612),(.41,.650),(.54,.652),(.62,.624),(.74,.583),(.81,.575),(.89,.585),(1.05,.620)],'464d67','827c90',73)

def cloud(name,seed,bands,shadow,rim,opacity):
    f=(noise(seed,56,14)*.51+noise(seed+1,142,27)*.26+noise(seed+2,289,50)*.13)
    envelope=np.zeros_like(X)
    for y,width,amp,angle,x,rx in bands:
        line=y+angle*(X-x)+.005*np.sin(X*18+seed)
        if name=='crown_cloud':
            line+=.0061*np.sin(X*32+.5)+.005*np.sin(X*14)
        b=amp*np.exp(-((Y-line)/width)**2-((X-x)/rx)**6)
        envelope=np.maximum(envelope,b)
    a=smooth(.39,.76,envelope+.20*f)*opacity
    if name=='crown_cloud':
        a*=.91+.084*np.sin(X*11+.48)
    if name=='high_cloud':
        a*=.67
    under=np.clip(a-np.roll(a,-5,axis=0),0,1)
    hi=smooth(.15,.78,gaussian_filter(under*4,2.5))
    color=tone(shadow)+(tone(rim)-tone(shadow))*np.clip(.25+hi*.73+sun*.24+f*.07,0,1)[...,None]
    lay(name,color,a)

cloud('high_cloud',53,[(.201,.010,.89,-.040,.56,.48),(.239,.010,.80,-.030,.38,.55),(.408,.015,.92,-.039,.63,.53),(.478,.010,.79,-.018,.86,.63)],'8e86a0','f3bbad',.67)
cloud('crown_cloud',66,[(.342,.039,1.14,-.043,.718,.330),(.370,.018,.89,-.046,.63,.52),(.390,.013,.84,-.025,.47,.57)],'9b8fa5','e6b4ad',.92)
cloud('valley_mist',67,[(.542,.023,.89,-.065,.66,.68),(.614,.028,.98,-.006,.34,.55),(.668,.013,.82,-.04,.73,.78)],'ab98a3','ecc3ab',.43)

# The Listener's body stays hidden. Only fabricated horn silhouettes and their frame read.
crown,d=blank()
poly(d,[(.407,.534),(.429,.464),(.485,.427),(.509,.371),(.542,.339),(.558,.300),(.610,.288),(.656,.314),(.688,.324),(.717,.369),(.786,.422),(.833,.540)],'#5b526e')
poly(d,[(.541,.439),(.566,.358),(.554,.319),(.599,.285),(.653,.298),(.682,.341),(.72,.351),(.758,.422),(.806,.560),(.47,.560)],'#564e68')
rng=np.random.default_rng(566)
def horn(x,y,length,radius,a,front):
    dx,dy=math.cos(a),math.sin(a)
    sx,sy=-dy*.69,dx*.69
    tx,ty=x+dx*length,y+dy*length*.62
    def P(cx,cy,k):
        return (cx+sx*radius*k,cy+sy*radius*k)
    pal=('#625368','#756377','#483e57','#9d777b') if front else ('#73627a','#857084','#5c506b','#977d8b')
    poly(d,[P(x,y,-.26),P(x,y,.26),P(tx,ty,1),P(tx,ty,-1)],pal[0])
    poly(d,[P(x,y,-.05),P(x,y,-.35),P(tx,ty,-1),P(tx,ty,-.7)],pal[1])
    ox,oy=p(tx,ty)
    rr=max(2,radius*W*.60)
    rry=max(2,radius*H*.53)
    d.ellipse((ox-rr*.54,oy-rry*.73,ox+rr*.54,oy+rry*.73),fill=pal[2],outline=pal[1],width=max(1,int(rr*.17)))
    if front:
        trace(d,[P(x,y,-.28),P(tx,ty,-.98)],pal[3],1)
for row in range(3):
    for j in range(15):
        frac=j/14
        ang=math.radians(-157+133*frac+(row-1)*14+rng.uniform(-16,15))
        xx=.469+frac*.304+rng.uniform(-.018,.018)
        yy=.344+.083*abs(frac-.48)**1.3+row*.022+rng.uniform(-.009,.012)
        horn(xx,yy,rng.uniform(.032,.085)*(1 if row==0 else .79),rng.uniform(.008,.018),ang,row==0 or j%3==0)
trace(d,[(.46,.421),(.52,.382),(.58,.376),(.62,.361),(.66,.371),(.744,.398)],'#66596d',3)
crown.filter(ImageFilter.GaussianBlur(1.3)).save(OUT/'listener.png')

near,d=blank()
poly(d,[(-.05,.738),(.08,.730),(.12,.684),(.185,.710),(.28,.722),(.314,.701),(.38,.719),(.454,.749),(.59,.779),(.645,.743),(.74,.701),(.83,.666),(.94,.697),(1.05,.686),(1.05,1.05),(-.05,1.05)],'#35394f')
rng=np.random.default_rng(631)
for j in range(147):
    x=rng.uniform(-.04,1.04)
    y=np.interp(x,[-.05,.08,.12,.185,.28,.314,.38,.454,.59,.645,.74,.83,.94,1.05],
                  [.738,.730,.684,.710,.722,.701,.719,.749,.779,.743,.701,.666,.697,.686])
    ww=rng.uniform(.0026,.0084);hh=rng.uniform(.005,.023)
    poly(d,[(x-ww,y+.007),(x-.56*ww,y-.25*hh),(x-.23*ww,y-.53*hh),(x,y-hh),(x+.20*ww,y-.57*hh),(x+.63*ww,y-.22*hh),(x+ww,y+.009)],rng.choice(['#3c4156','#3a3e55','#35394f','#4a485f']))
near.save(OUT/'cedars.png')

