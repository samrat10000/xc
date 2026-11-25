"""Copy this project's working sources into a new, versioned shared snapshot."""
import argparse,csv,datetime,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SHARED=ROOT.parent/'SHARED_ASSETS';p=argparse.ArgumentParser();p.add_argument('--snapshot',default='build-v006');a=p.parse_args();dest=SHARED/'ep3'/a.snapshot
if dest.exists():raise RuntimeError('Snapshot already exists; use a new version')
dest.mkdir(parents=True)
files=[]
for filename in ('RESEARCH.md','BUILD_NOTES.md','SHOTS.json','CREDITS.md'):
 shutil.copy2(ROOT/filename,dest/filename);files.append(filename)
shutil.copytree(ROOT/'sc',dest/'sc',ignore=shutil.ignore_patterns('__pycache__'));shutil.copytree(ROOT/'audio',dest/'audio');shutil.copytree(ROOT/'audit',dest/'audit',ignore=shutil.ignore_patterns('*.log'))
plan=json.loads((ROOT/'SHOTS.json').read_text());plan['source']='EP3_STORYBOARD.html';plan['adaptation_authorized']='Sam: use the buggy and adapt the cabin/roof sequence; make needed modifications and build'
changes={4:'Open-cockpit crossbar camera; Sam jolts on impact. No windscreen. Cage and antlers scrape past.',5:'Damaged nose, radiator steam, dead LEFT lamp, wrecked trike; Sam climbs out through the cage opening.',13:'Stalker hooks claws around and buckles upper roll-cage bars; rider fires upward three times through the open gap.',14:'Tunnel concrete lip catches raised antlers and tears Stalker off the cage; anatomical LEFT antler snaps.',16:'Open cockpit, camera facing both occupants. Reload, shaking driver hands, wind past bent cage.',17:'Over Sam shoulder between cage bars; the single headlight reveals occupied abandoned cars.'}
for s in plan['shots']:
 if s['n'] in changes:s['original_action']=s['action'];s['action']=changes[s['n']]
(ROOT/'SHOTS_BUILD.json').write_text(json.dumps(plan,indent=2),encoding='utf8');shutil.copy2(ROOT/'SHOTS_BUILD.json',dest/'SHOTS_BUILD.json')
with (ROOT/'audio/CUE_SHEET.csv').open('w',newline='',encoding='utf8') as f:
 w=csv.writer(f);w.writerow(['shot','start_s','end_s','event','source_status'])
 for s in plan['shots']:w.writerow([s['n'],s['start_s'],s['end_s'],s['sound'],'Pending exact isolated source and sync'])
shutil.copy2(ROOT/'audio/CUE_SHEET.csv',dest/'audio/CUE_SHEET.csv')
hashes={str(f.relative_to(dest)):hashlib.sha256(f.read_bytes()).hexdigest() for f in dest.rglob('*') if f.is_file()}
(dest/'MANIFEST.json').write_text(json.dumps(hashes,indent=2),encoding='utf8')
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5,minutes=30))).strftime('%Y-%m-%d %H:%M IST')
with (SHARED/'README.md').open('a',encoding='utf8') as f:
 f.write(f'\n- {stamp} Codex: Episode 3 source snapshot `{dest.relative_to(SHARED)}`; research, adapted shot plan, scripts, credits, cue sheet and audit.\n')
 f.write(f'- {stamp} Codex: `ep3/v001/assets/` contains versioned original-buggy import, optimized assemblies, GLB-derived trike wreck, Husk/Runner/Screamer rigs, and licensed Khronos car sources/prepared props; source originals unchanged.\n')
 f.write(f'- {stamp} Codex: `ep3/v001/references/camera-shakify/` contains official CC0 recorded shake data, license and download hashes. Internal pose photo references remain in the Ep3 working folder and are not publication assets.\n')
print('SHARED SNAPSHOT',dest)
