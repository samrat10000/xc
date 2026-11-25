"""Single-process render queue; caller explicitly selects CPU or GPU."""
import argparse,json,os,re,subprocess,sys,time,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--shots',default='1-19');p.add_argument('--device',choices=['CPU','GPU'],default='CPU');p.add_argument('--res',default='.25');p.add_argument('--samples',default='4');p.add_argument('--frames');p.add_argument('--anim',action='store_true');p.add_argument('--save-only',action='store_true');p.add_argument('--version',default='v009');p.add_argument('--wait-gpu',action='store_true');a=p.parse_args()
shots=[]
for part in a.shots.split(','):
 if '-' in part:lo,hi=map(int,part.split('-'));shots.extend(range(lo,hi+1))
 else:shots.append(int(part))
assert shots and all(1<=n<=19 for n in shots)
logs=ROOT/'audit'/a.version;logs.mkdir(parents=True,exist_ok=True)
state=[]
for shot in shots:
 if a.device=='GPU' and not a.save_only:
  while True:
   probe=subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],capture_output=True,text=True,timeout=20)
   if probe.returncode:raise RuntimeError('Cannot check GPU render ownership: '+probe.stderr)
   busy=bool(re.search(r'blender(?:\.exe)?',probe.stdout,re.I));unknown='Insufficient Permissions' in probe.stdout
   if not busy and not unknown:break
   reason='another Blender GPU context' if busy else 'GPU process ownership is unreadable; run the queue from an authorized host shell'
   if not a.wait_gpu:raise SystemExit('GPU unavailable: '+reason)
   print('WAIT_GPU',reason,flush=True);time.sleep(30)
 env=os.environ.copy();env.update(SHOT=str(shot),DEVICE=a.device,RES=a.res,SAMP=a.samples,VERSION=a.version)
 for name in ('ANIM','SAVE_ONLY','FRAMES','FORCE'):env.pop(name,None)
 if a.frames:env['FRAMES']=a.frames
 if a.anim:env['ANIM']='1'
 if a.save_only:env['SAVE_ONLY']='1'
 started=time.time();print(f'START shot {shot:02d} {a.device}',flush=True)
 status_path=ROOT.parent/'SHARED_ASSETS/ep3/RENDER_STATUS.json'
 status_path.parent.mkdir(parents=True,exist_ok=True)
 status_path.write_text(json.dumps({'episode':3,'shot':shot,'device':a.device,'version':a.version,'status':'RENDERING','queue_pid':os.getpid(),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2),encoding='utf8')
 with (logs/f'shot{shot:02d}.log').open('w',encoding='utf8') as log:
  process=subprocess.run([str(ROOT.parent/'blender501/blender.exe'),'-b','--factory-startup','--python-exit-code','1','--python',str(ROOT/'sc/ep3.py')],env=env,stdout=log,stderr=subprocess.STDOUT)
 item={'shot':shot,'returncode':process.returncode,'elapsed_s':round(time.time()-started,2),'device':a.device};state.append(item)
 status_path.write_text(json.dumps({**item,'version':a.version,'status':'DONE' if process.returncode==0 else 'FAILED'},indent=2),encoding='utf8')
 (logs/'queue.json').write_text(json.dumps(state,indent=2),encoding='utf8');print('DONE',json.dumps(item),flush=True)
 if process.returncode:
  print((logs/f'shot{shot:02d}.log').read_text(encoding='utf8',errors='replace')[-3500:]);sys.exit(process.returncode)
