"""Ep1 v6 full mix on the v5 Flow music clock (52 s): music + SFX stems from flow_mix5, new SFX, dialogue (ducks the music).
Out: out/v6/ep1_v6_mix.wav (+ dialogue_stem6.wav)"""
import os, subprocess
E = os.path.dirname(os.path.abspath(__file__)); M = os.path.join(E, '..', 'music', 'out'); SFX = os.path.join(E, '..', 'music', 'sfx')
VO = os.path.join(E, 'vo'); O = os.path.join(E, 'out', 'v6'); END = 52.0
PHONE = 'highpass=f=450,lowpass=f=3200,acompressor=threshold=-20dB:ratio=4,volume=1.6'
CAM = 'highpass=f=110,lowpass=f=9500,aecho=0.8:0.5:23|41:0.18|0.10'
# dialogue on the new clock: (file, start, max len, filter, dB)
DLG = [('01.6_sam', 0.75, 1.0, CAM, -4), ('02.6_sam', 1.95, None, CAM, 0), ('02.9_akash', 3.0, None, PHONE, -3),
       ('03.2_sam', 5.0, None, CAM, -2), ('03.8_akash', 7.0, 1.05, PHONE, -4), ('04.6_sam', 9.3, None, CAM, 0),
       ('11.0_sam', 10.8, None, CAM, -2), ('13.2_sam', 13.3, None, CAM, 2), ('17.2_sam', 15.95, None, CAM, -2),
       ('18.6_sam', 17.75, 0.95, CAM, 0), ('21.0_radio', 19.4, 3.35, PHONE + ',aecho=0.7:0.4:60:0.2', -2),
       ('22.5_sam', 22.8, None, CAM, 0), ('29.5_sam', 27.55, None, CAM, 0), ('31.2_sam', 29.95, 1.6, CAM, -2),
       ('33.0_sam', 34.75, 2.8, CAM, 0), ('44.5_akash_voicemail', 44.1, None, PHONE, -1)]
def run(inputs, graph, out):
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', *sum([['-i', i] for i in inputs], []), '-filter_complex', graph, '-map', '[o]', '-ar', '48000', '-ac', '2', out], check=True)
# 1) dialogue stem
ins, g = [], []
for i, (f, t, mx, flt, db) in enumerate(DLG):
    ins.append(f'{VO}/{f}.wav'); tr = f'atrim=0:{mx},afade=t=out:st={mx-.25:.2f}:d=0.25,' if mx else ''
    g.append(f'[{i}:a]{tr}{flt},loudnorm=I=-17:TP=-2,volume={db}dB,adelay={int(t*1000)},aformat=channel_layouts=stereo[a{i}]')
n = len(DLG)
g.append('sine=f=1000:d=0.35:sample_rate=48000,volume=-20dB,highpass=f=450,adelay=51150,aformat=channel_layouts=stereo[bp]')
g.append(''.join(f'[a{i}]' for i in range(n)) + f'[bp]amix=inputs={n+1}:normalize=0:duration=longest,apad=whole_dur={END},atrim=0:{END}[o]')
DS = f'{O}/dialogue_stem6.wav'; run(ins, ';'.join(g), DS)
# 2) music: flow_mix5 music stem to 45.5, then a low pad bed (stretched, lowpassed tail) to the end
g = ['[0:a]atrim=0:45.5,afade=t=out:st=44.0:d=1.5[m1]',
     '[1:a]atrim=40.5:44.5,asetpts=PTS-STARTPTS,rubberband=tempo=0.45,lowpass=f=520,volume=-5dB,afade=t=in:st=0:d=2.5,afade=t=out:st=5.5:d=3.3,adelay=43000|43000[m2]',
     '[m1][m2]amix=inputs=2:normalize=0:duration=longest,apad=whole_dur=52,atrim=0:52[o]']
MU = f'{O}/music6.wav'; run([f'{M}/flow_mix5_M.wav', f'{M}/flow_mix5_M.wav'], ';'.join(g), MU)
# 3) SFX: v5 stems only where the picture is the same as v5 (scream 8-10.7, 18.2-38.7), hits throughout, new spot effects
def seg(i, a, b, fi=.08): return f'[{i}:a]atrim={a}:{b},afade=t=in:st={a}:d={fi},afade=t=out:st={b-fi:.3f}:d={fi},asetpts=PTS-STARTPTS,adelay={int(a*1000)}|{int(a*1000)}'
ins = [f'{M}/flow_mix5_hit.wav', f'{M}/flow_mix5_vox.wav', f'{M}/flow_mix5_veh.wav', f'{M}/flow_mix5_fol.wav', f'{M}/flow_mix5_amb.wav',
       f'{SFX}/crawler_hiss_0.wav', f'{SFX}/engine_start_0.wav', f'{SFX}/rain_city_0.wav', f'{SFX}/horde_0.wav']
g = ['[0:a]atrim=0:46,volume=0dB[h]', seg(1, 7.8, 10.7) + '[v1]', seg(1, 19.3, 38.7) + '[v2]', seg(2, 18.6, 38.7) + '[ve]',
     seg(3, 19.3, 38.7) + '[fo]', seg(4, 19.3, 38.7, .5) + '[am]',
     '[5:a]volume=-2dB,adelay=13250|13250[cr]', '[6:a]atrim=0:2.5,volume=-3dB,adelay=17900|17900[en]',
     '[7:a]atrim=0:9,afade=t=in:d=1,afade=t=out:st=7.5:d=1.5,volume=-14dB,adelay=38667|38667[rn]',
     '[8:a]atrim=0:2.2,afade=t=in:d=0.3,afade=t=out:st=1.7:d=0.5,volume=-6dB,adelay=13850|13850[hd]']
# phone buzz bursts on the nightstand (wake-up, frame 30 -> 1.75 s) and on the seat (missed, 39.9-44.0)
bz = []
for k, t in enumerate([1.75, 2.75, 39.92, 41.92, 43.0]):
    g.append(f'sine=f=170:d=0.42:sample_rate=48000,volume=-16dB,tremolo=f=28:d=0.9,lowpass=f=900,adelay={int(t*1000)},aformat=channel_layouts=stereo[b{k}]'); bz.append(f'[b{k}]')
g.append('[h][v1][v2][ve][fo][am][cr][en][rn][hd]' + ''.join(bz) + f'amix=inputs={10+len(bz)}:normalize=0:duration=longest,apad=whole_dur={END},atrim=0:{END}[o]')
SX = f'{O}/sfx6.wav'; run(ins, ';'.join(g), SX)
# 4) final: music ducked under dialogue (gentle, slow release), + sfx + dialogue, limiter
g = ['[2:a]asplit=3[d1][d2][d3]', '[0:a][d1]sidechaincompress=threshold=0.006:ratio=4:attack=40:release=450:makeup=1[md]',
     '[1:a][d3]sidechaincompress=threshold=0.006:ratio=6:attack=30:release=400:makeup=1[sd]',
     '[md][sd][d2]amix=inputs=3:normalize=0:weights=1 0.75 1.3,alimiter=limit=0.89,loudnorm=I=-14:TP=-1:LRA=11[o]']
run([MU, SX, DS], ';'.join(g), f'{O}/ep1_v6_mix.wav'); print('ok')
