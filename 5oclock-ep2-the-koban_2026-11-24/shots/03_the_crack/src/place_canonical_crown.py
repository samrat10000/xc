"""Regrade a canonical Episode 1 crown cel for the distant morning silhouette."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np
root=Path(__file__).resolve().parent
master=Image.open(root.parent/'refs'/'listener_ep1_cel_108.png').convert('RGBA')
w,h=master.size
master=master.crop((int(w*.319),int(h*.172),int(w*.988),int(h*.502)))
w,h=master.size
a=np.asarray(master,dtype=np.float32)/255
yy=np.linspace(0,1,h,dtype=np.float32)[:,None]
base=np.array([.294,.265,.393],dtype=np.float32)
strength=np.clip((a[:,:,:3]-.06)*1.20,0,.29)
graded=base+strength*np.array([.68,.62,.75],dtype=np.float32)
fader=1-np.clip((yy-.70)/.29,0,1)**1.2
a=np.dstack((graded,a[:,:,3]*fader))
crop=Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5))
width=535
height=round(crop.height*width/crop.width)
crop=crop.resize((width,height),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(.65))
plate=Image.new('RGBA',(1188,2112))
plate.alpha_composite(crop,(round((.361+.05)/1.1*1188),round((.216+.05)/1.1*2112)))
plate.save(root/'plates'/'listener.png')

