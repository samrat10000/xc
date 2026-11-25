"""Build selected shot cels. Invoke with shot, output directory, scale and frames."""
from pathlib import Path
import sys
import os

ROOT=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:]
task=args[0]
revision=os.environ.get('KOBAN_PICTURE_REVISION')
revision_scene=revision in ('6','7')
suffix='_v6' if revision_scene else ''
exec(compile((ROOT/'stage.py').read_text(encoding='utf-8-sig'),'stage.py','exec'))
if task in ('04','other_side','feed_08','feed_09'):
    exec(compile((ROOT/f'kitchen{suffix}.py').read_text(encoding='utf-8-sig'),'kitchen.py','exec'))
    builders={'04':shot_04,'other_side':make_other_side,'feed_08':lambda:make_feed(False),'feed_09':lambda:make_feed(True)}
elif task in ('05','12'):
    exec(compile((ROOT/f'street{suffix}.py').read_text(encoding='utf-8-sig'),'street.py','exec'))
    builders={'05':shot_05,'12':shot_12}
elif task in ('08','09','11'):
    exec(compile((ROOT/f'phone_inserts{suffix}.py').read_text(encoding='utf-8-sig'),'phone_inserts.py','exec'))
    builders={'08':lambda:call_insert(False),'09':lambda:call_insert(True),'11':clock_insert}
else:
    exec(compile((ROOT/f'station{suffix}.py').read_text(encoding='utf-8-sig'),'station.py','exec'))
    builders={'06':shot_06,'07':shot_07,'10':shot_10,'13':shot_13,'14':shot_14,'15':shot_15}
if revision=='7':
    import bpy_extras.object_utils
    for source in ('hands_v7.py','motion_v7.py'):
        exec(compile((ROOT/source).read_text(encoding='utf-8'),source,'exec'))
    if task=='05':
        builders['05']=street_walk_v7
duration,tick=builders[task]()
sc.frame_end=duration
exec(compile((ROOT/'preflight_scene.py').read_text(encoding='utf-8'),'preflight_scene.py','exec'))
preflight=scene_report(sc,cam,duration,task)
preflight_frames={1,duration//4,duration//2,duration*3//4,duration}
frames=range(1,duration+1) if args[3] in ('all','resume') else [int(t) for t in args[3].split(',')]
for f in frames:
    sc.frame_set(f)
    tick(f)
    bpy.context.view_layer.update()
    if args[3] not in ('all','resume') or f in preflight_frames:
        record_pose(sc,cam,f,preflight)
        write_report(OUT,preflight)
    path=OUT/f'cel_{f:03d}.png'
    if args[3]!='resume' or not path.exists():
        render(path)

