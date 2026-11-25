"""Single-process render queue; caller explicitly selects CPU or GPU."""
import argparse,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--shots',default='1-19');p.add_argument('--device',choices=['CPU','GPU'],default='CPU');p.add_argument('--res',default='.25');p.add_argument('--samples',default='4');p.add_argument('--frames');p.add_argument('--anim',action='store_true');p.add_argument('--save-only',action='store_true');p.add_argument('--version',default='v001');a=p.parse_args()
shots=[]
for part in a.shots.split(','):
 if '-' in part:lo,hi=map(int,part.split('-'));shots.extend(range(lo,hi+1))
 else:shots.append(int(part))
assert shots and all(1<=n<=19 for n in shots)
logs=ROOT/'audit'/a.version;logs.mkdir(parents=True,exist_ok=True)
state=[]
for shot in shots:
 env=os.environ.copy();env.update(SHOT=str(shot),DEVICE=a.device,RES=a.res,SAMP=a.samples,VERSION=a.version)
 for name in ('ANIM','SAVE_ONLY','FRAMES','FORCE'):env.pop(name,None)
 if a.frames:env['FRAMES']=a.frames
 if a.anim:env['ANIM']='1'
 if a.save_only:env['SAVE_ONLY']='1'
 started=time.time();print(f'START shot {shot:02d} {a.device}',flush=True)
 with (logs/f'shot{shot:02d}.log').open('w',encoding='utf8') as log:
  process=subprocess.run([str(ROOT.parent/'blender501/blender.exe'),'-b','--factory-startup','--python-exit-code','1','--python',str(ROOT/'sc/ep3.py')],env=env,stdout=log,stderr=subprocess.STDOUT)
 item={'shot':shot,'returncode':process.returncode,'elapsed_s':round(time.time()-started,2),'device':a.device};state.append(item)
 (logs/'queue.json').write_text(json.dumps(state,indent=2),encoding='utf8');print('DONE',json.dumps(item),flush=True)
 if process.returncode:
  print((logs/f'shot{shot:02d}.log').read_text(encoding='utf8',errors='replace')[-3500:]);sys.exit(process.returncode)
