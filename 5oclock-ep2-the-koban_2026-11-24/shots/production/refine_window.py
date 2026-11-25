from pathlib import Path
p=Path(__file__).resolve().parent/'station.py'
s=p.read_text(encoding='utf-8')
s=s.replace("shoulder=copy.world('UpperArm','L')+Vector((.088,-.040,.043))","shoulder=copy.world('UpperArm','L')+Vector((.103,-.164,.048))")
s=s.replace("mom.reach('R',shoulder,(.72,.31,-.52),(-.088,-.018,-.048))","""miss=mom.reach('R',shoulder,(.77,-.22,-.62),(-.096,.020,-.046))
            if f in (65,75,93):
                print(f'window frame {f}, right wrist error {miss:.4f} m, wrist {tuple(mom.world("Hand","R"))}, shoulder {tuple(shoulder)}',flush=True)""")
assert 'right wrist error' in s
p.write_text(s,encoding='utf-8')
