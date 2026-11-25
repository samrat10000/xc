"""Conform complete animated PNG sequences; never substitute held stills for shots."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--version',required=True);p.add_argument('--audio',type=Path);p.add_argument('--preview',action='store_true');a=p.parse_args()
plan=json.loads((ROOT/'SHOTS_BUILD.json').read_text());base=ROOT/'frames'/a.version;out=ROOT/'out';out.mkdir(exist_ok=True)
if not a.audio and not a.preview:raise SystemExit('Final encode requires an actual approved score+SFX WAV. Use --preview for an explicitly silent draft.')
if a.audio and not a.audio.is_file():raise SystemExit('Audio input missing')
missing=[]
for shot in plan['shots']:
 for f in range(1,shot['frames']+1):
  path=base/f'shot{shot["n"]:02d}'/f'f{f:04d}.png'
  if not path.exists() or path.stat().st_size<100:missing.append(str(path))
if missing:raise SystemExit(f'{len(missing)} animation frames missing. First: {missing[:3]}')
segments=out/'segments'/a.version;segments.mkdir(parents=True,exist_ok=True)
font="C\\:/Windows/Fonts/consolab.ttf"
def run(cmd):subprocess.run(cmd,check=True)
for shot in plan['shots']:
 n=shot['n'];target=segments/f'shot{n:02d}.mp4'
 filters=['scale=1080:1920:flags=lanczos','setsar=1']
 if shot['vhs']:
  filters=['scale=1080:810:flags=lanczos','setsar=1','gblur=sigma=0.55','eq=saturation=0.65:contrast=1.03','chromashift=cbh=2:crh=-2',f"drawtext=fontfile='{font}':text='REC  3\\:47 AM':fontsize=26:fontcolor=white:x=42:y=27",'drawbox=x=20:y=35:w=10:h=10:color=red:t=fill','pad=1080:1920:0:555:color=black']
 if n==1:filters.append(f"drawtext=fontfile='{font}':text='IT NEVER LANDED.':fontsize=64:fontcolor=white:shadowcolor=black:shadowx=3:shadowy=3:x=(w-tw)/2:y=220:enable='eq(n,0)'")
 run(['ffmpeg','-v','error','-y','-framerate','24','-start_number','1','-i',str(base/f'shot{n:02d}'/'f%04d.png'),'-frames:v',str(shot['frames']),'-vf',','.join(filters),'-an','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p',str(target)])
concat=segments/'concat.txt';concat.write_text(''.join("file '"+str((segments/f'shot{s["n"]:02d}.mp4').resolve()).replace('\\','/')+"'\n" for s in plan['shots']),encoding='utf8')
name=f'ep3-{a.version}-preview.mp4' if a.preview else 'ep3.mp4';target=out/name
cmd=['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(concat)]
if a.audio:cmd+=['-i',str(a.audio),'-map','0:v:0','-map','1:a:0','-af','apad,atrim=duration=48','-c:a','aac','-b:a','192k','-ar','48000']
else:cmd+=['-an']
cmd+=['-c:v','copy','-t','48','-movflags','+faststart',str(target)];run(cmd)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_entries','format=duration:stream=codec_type,width,height,r_frame_rate,nb_read_frames','-of','json',str(target)],text=True))
video=next(s for s in probe['streams'] if s['codec_type']=='video')
if (int(video['nb_read_frames']),video['width'],video['height'],video['r_frame_rate'])!=(1152,1080,1920,'24/1'):raise RuntimeError('Encode failed exact timeline/resolution check')
if abs(float(probe['format']['duration'])-48)>.05:raise RuntimeError('Encode runtime incorrect')
(out/(target.stem+'-verification.json')).write_text(json.dumps(probe,indent=2),encoding='utf8')
if not a.preview:
 run(['ffmpeg','-v','error','-y','-i',str(target),'-vf','scale=720:1280','-c:v','libx264','-crf','23','-preset','medium','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out/'ep3-phone.mp4')])
print('VERIFIED',target)
