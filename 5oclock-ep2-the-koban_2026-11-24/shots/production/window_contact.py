from pathlib import Path
p=Path(__file__).resolve().parent/'station.py'
s=p.read_text(encoding='utf-8')
s=s.replace("mom.pose((.689,1.827,.091),2.63,.95)", "mom.pose((.718,1.861,.053),-.38,.96)")
s=s.replace("mom.arms_free(.048)\n            shoulder=", "mom.arms_free(.048)\n            mom.primary(mom.b('Head'),(0,0,1),-1.78)\n            shoulder=")
s=s.replace("shoulder=copy.world('UpperArm','L')+Vector((.060,-.042,.035))","shoulder=copy.world('UpperArm','L')+Vector((.088,-.040,.043))")
s=s.replace("mom.reach('L',shoulder,(.75,.19,-.64),(-.089,-.010,-.037))","mom.reach('R',shoulder,(.72,.31,-.52),(-.088,-.018,-.048))")
assert "mom.primary(mom.b('Head')" in s
p.write_text(s,encoding='utf-8')
