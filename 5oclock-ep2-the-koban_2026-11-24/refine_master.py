from pathlib import Path
root=Path(__file__).resolve().parent
p=root/'audio'/'assemble_episode.py'
s=p.read_text(encoding='utf-8-sig')
start=s.index('def normalize(track):')
end=s.index('def finish():',start)
s=s[:start]+"""def normalize(track):
    original=STEMS/'premaster.wav'
    initial=measure(original)
    gain=-14.85-float(initial['input_i'])
    attempt=track.with_name(track.stem+'_working.wav')
    for _ in range(3):
        filters=f'volume={gain:.4f}dB,aresample=192000,alimiter=limit=0.794:attack=3:release=80:level=false:latency=true,aresample=48000'
        run(['ffmpeg','-y','-v','error','-i',str(original),'-af',filters,'-c:a','pcm_s24le',str(attempt)])
        measured=measure(attempt)
        loudness=float(measured['input_i'])
        if -15.06<=loudness<=-14.64 and float(measured['input_tp'])<=-1.50:
            attempt.rename(track)
            return measured
        gain+=-14.85-loudness
    raise ValueError(f'Mix did not reach the broadcast loudness and peak targets: {measured}')
""" + s[end:]
s=s.replace('def finish():','def finish(version):')
s=s.replace("label='score_only_v1' if scored_only else 'v1'","label=f'score_only_v{version}' if scored_only else f'v{version}'")
s=s.replace("assert -16<=float(loud['input_i'])<=-14","assert -15.08<=float(loud['input_i'])<=-14.55")
s=s.replace("assert -16<=float(loud_final['input_i'])<=-14","assert -15.10<=float(loud_final['input_i'])<=-14.50")
s=s.replace("elif sys.argv[1]=='finish':finish()","elif sys.argv[1]=='finish':finish(int(sys.argv[2]) if len(sys.argv)>2 else 2)")
p.write_text(s,encoding='utf-8')
prod=root/'shots'/'production'
p=prod/'delivery_index.py'
s=p.read_text(encoding='utf-8-sig')
s=s.replace('import json\n','import json\nimport sys\n')
s=s.replace("label='score_only_v1' if pending else 'v1'","version=int(sys.argv[1]) if len(sys.argv)>1 else 2\nlabel=f'score_only_v{version}' if pending else f'v{version}'")
p.write_text(s,encoding='utf-8')
p=prod/'finish_episode.ps1'
s=p.read_text(encoding='utf-8-sig')
s=s.replace('param()','param([int]$Version = 2)')
s=s.replace('assemble_episode.py" finish }','assemble_episode.py" finish $Version }')
s=s.replace("{'score_only_v1'}else{'v1'}",'{"score_only_v$Version"}else{"v$Version"}')
s=s.replace('delivery_index.py" }','delivery_index.py" $Version }')
p.write_text(s,encoding='utf-8')
