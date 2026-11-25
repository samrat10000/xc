from pathlib import Path
p=Path(__file__).resolve().parent/'build_reel.py'
s=p.read_text(encoding='utf-8')
s=s.replace("sc.frame_end=duration", """sc.frame_end=duration
exec(compile((ROOT/'preflight_scene.py').read_text(encoding='utf-8'),'preflight_scene.py','exec'))
preflight=scene_report(sc,cam,duration,task)
preflight_frames={1,duration//4,duration//2,duration*3//4,duration}""")
s=s.replace("    render(OUT/f'cel_{f:03d}.png')", """    if args[3]!='all' or f in preflight_frames:
        record_pose(sc,cam,f,preflight)
        write_report(OUT,preflight)
    render(OUT/f'cel_{f:03d}.png')""")
p.write_text(s,encoding='utf-8')
