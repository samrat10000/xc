"""Build selected shot cels. Invoke with shot, output directory, scale and frames."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:]
task=args[0]
exec(compile((ROOT/'stage.py').read_text(encoding='utf-8-sig'),'stage.py','exec'))
if task in ('04','other_side','feed_08','feed_09'):
    exec(compile((ROOT/'kitchen.py').read_text(encoding='utf-8-sig'),'kitchen.py','exec'))
    builders={'04':shot_04,'other_side':make_other_side,'feed_08':lambda:make_feed(False),'feed_09':lambda:make_feed(True)}
elif task in ('05','12'):
    exec(compile((ROOT/'street.py').read_text(encoding='utf-8-sig'),'street.py','exec'))
    builders={'05':shot_05,'12':shot_12}
elif task in ('08','09','11'):
    exec(compile((ROOT/'phone_inserts.py').read_text(encoding='utf-8-sig'),'phone_inserts.py','exec'))
    builders={'08':lambda:call_insert(False),'09':lambda:call_insert(True),'11':clock_insert}
else:
    exec(compile((ROOT/'station.py').read_text(encoding='utf-8-sig'),'station.py','exec'))
    builders={'06':shot_06,'07':shot_07,'10':shot_10,'13':shot_13,'14':shot_14,'15':shot_15}
duration,tick=builders[task]()
sc.frame_end=duration
frames=range(1,duration+1) if args[3]=='all' else [int(t) for t in args[3].split(',')]
for f in frames:
    sc.frame_set(f)
    tick(f)
    bpy.context.view_layer.update()
    render(OUT/f'cel_{f:03d}.png')

