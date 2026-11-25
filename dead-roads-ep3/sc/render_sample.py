"""Render a genuine one-second motion sample from the baked rescue scene, CPU only."""
import bpy,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'out/rescue-motion-v001-frames';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/v012/shot06.blend'));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE'
if hasattr(s.cycles,'denoising_use_gpu'):s.cycles.denoising_use_gpu=False
s.render.use_persistent_data=True;s.render.threads_mode='FIXED';s.render.threads=4
s.render.resolution_x=1080;s.render.resolution_y=1920;s.render.resolution_percentage=25
started=time.time()
for output_frame,source_frame in enumerate(range(7,31),1):
 target=OUT/f'f{output_frame:04d}.png'
 if target.exists() and target.stat().st_size>100:continue
 s.frame_set(source_frame);s.render.filepath=str(target);bpy.ops.render.render(write_still=True);print('SAMPLE_FRAME',output_frame,'source',source_frame,flush=True)
movie=ROOT/'out/ep3-rescue-motion-sample-v001.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(OUT/'f%04d.png'),'-frames:v','24','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_entries','format=duration:stream=width,height,nb_read_frames,r_frame_rate','-of','json',str(movie)],text=True))
assert int(probe['streams'][0]['nb_read_frames'])==24
(ROOT/'out/rescue-motion-v001-verification.json').write_text(json.dumps({'stage':'Silent blocking preview','source_scene':'assets/v012/shot06.blend','source_frames':[7,30],'elapsed_s':time.time()-started,'probe':probe},indent=2),encoding='utf8')
print('SAMPLE_READY',movie,flush=True)
