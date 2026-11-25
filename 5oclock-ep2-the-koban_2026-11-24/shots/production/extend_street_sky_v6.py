from pathlib import Path
p=Path(__file__).resolve().parent
source=p/'street_v6.py'
s=source.read_text(encoding='utf-8')
old="    card('Western wrap for street tracking view',[(-38,63,-11),(-38,-176,-11),(-38,-176,34),(-38,63,34)],bmat)"
new="""    side_points=[(-38,y,z) for z in (-11,34,150) for y in (63,-176)]
    form('Western wrap and overheight sky',side_points,[(0,1,3,2),(2,3,5,4)],bmat,
         [(0,0),(1,0),(0,1),(1,1),(0,1),(1,1)])"""
assert old in s
source.write_text(s.replace(old,new,1),encoding='utf-8')
