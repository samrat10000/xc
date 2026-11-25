"""Ep1 dialogue stem: places trimmed ElevenLabs lines on the 53 s clock. Out: out/v6/dialogue_stem.wav"""
import subprocess, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vo'); OUT = os.path.join(os.path.dirname(D), 'out', 'v6', 'dialogue_stem.wav')
PHONE = 'highpass=f=450,lowpass=f=3200,acompressor=threshold=-20dB:ratio=4,volume=1.6'
CAM = 'highpass=f=110,lowpass=f=9500,aecho=0.8:0.5:23|41:0.18|0.10'
# (file, start s, max len s or None, filter, gain dB)
CUES = [('01.6_sam', 1.05, 1.15, CAM, -3), ('02.6_sam', 2.45, None, CAM, 0), ('02.9_akash', 3.55, None, PHONE, -2),
        ('03.2_sam', 7.65, None, CAM, -4), ('03.8_akash', 6.25, 1.75, PHONE, -3), ('04.6_sam', 9.15, None, CAM, 0),
        ('11.0_sam', 10.85, None, CAM, -2), ('13.2_sam', 13.25, None, CAM, 2), ('17.2_sam', 16.6, None, CAM, -2),
        ('18.6_sam', 18.45, None, CAM, 0), ('21.0_radio', 20.6, 3.35, PHONE + ',aecho=0.7:0.4:60:0.2', -6),
        ('22.5_sam', 24.0, None, CAM, 0), ('29.5_sam', 29.2, None, CAM, 0), ('31.2_sam', 31.2, 2.0, CAM, -2),
        ('33.0_sam', 33.2, 2.8, CAM, 0), ('44.5_akash_voicemail', 45.6, None, PHONE, -1)]
inp, fl = [], []
for i, (f, t, mx, flt, g) in enumerate(CUES):
    inp += ['-i', f'{D}/{f}.wav']; tr = f'atrim=0:{mx},afade=t=out:st={mx-.25:.2f}:d=0.25,' if mx else ''
    fl.append(f'[{i}:a]{tr}{flt},volume={g}dB,adelay={int(t*1000)}[a{i}]')
n = len(CUES)
# voicemail beep at 52.55
fl.append(f'sine=f=1000:d=0.35:sample_rate=48000,volume=-20dB,highpass=f=450,adelay=52550[bp]')
fl.append(''.join(f'[a{i}]' for i in range(n)) + f'[bp]amix=inputs={n+1}:normalize=0:duration=longest,apad=whole_dur=53,atrim=0:53,alimiter=limit=.9[o]')
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', *inp, '-filter_complex', ';'.join(fl), '-map', '[o]', '-ar', '48000', OUT], check=True)
print(OUT)
