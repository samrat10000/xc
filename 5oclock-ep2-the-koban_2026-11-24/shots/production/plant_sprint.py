from pathlib import Path
root=Path(__file__).resolve().parent
p=root/'street.py'
s=p.read_text(encoding='utf-8')
old='        hip=actor.world("UpperLeg",side)'
s=s.replace('        hip=actor.world(\'UpperLeg\',side)\n        ankle=Vector((x-sign*.11,ty,.12+lift))',
'''        plant_frame=j*16-offset+2.8
        plant_x=-.28+.12*math.sin(plant_frame*.033)
        next_x=-.28+.12*math.sin((plant_frame+16)*.033)
        foot_x=plant_x+(next_x-plant_x)*ease(swing)
        ankle=Vector((foot_x-sign*.105,ty,.087+lift))''')
assert 'foot_x-sign' in s
p.write_text(s,encoding='utf-8')
