from pathlib import Path
p=Path(__file__).resolve().parent
f=p/'street_v6.py'
s=f.read_text(encoding='utf-8-sig')
s=s.replace("[(-38,45,-11),(-38,-45,-11),(-38,-45,31),(-38,45,31)]","[(-38,63,-11),(-38,-176,-11),(-38,-176,34),(-38,63,34)]")
s='\n'.join(line for line in s.split('\n') if "card('Southern wrap" not in line)
f.write_text(s,encoding='utf-8')
f=p/'station_v6.py'
s=f.read_text(encoding='utf-8-sig')
old="            reader.blink(n,(18,))"
new="""            for side,sign in (('L',1),('R',-1)):
                palm=reader.b('Hand',side)
                palm.rotation_quaternion=palm.rotation_quaternion@Quaternion((0,1,0),sign*.76)
                for digit,amount in (('Index',.23),('Middle',.33),('Ring',.38),('Little',.44)):
                    for segment in (1,2,3):
                        bone=reader.bones.get(f'J_Bip_{side}_{digit}{segment}')
                        if bone is not None:
                            bone.rotation_quaternion=Quaternion((0,0,1),-sign*amount)
            reader.blink(n,(18,))"""
assert old in s
f.write_text(s.replace(old,new,1),encoding='utf-8')
