from pathlib import Path
root=Path(__file__).resolve().parent

p=root/'stage.py'
s=p.read_text(encoding='utf-8')
old="        self.bones=self.arm.pose.bones\n        self.arm.data.pose_position='POSE'"
new="""        self.bones=self.arm.pose.bones
        self.arm.data.pose_position='POSE'
        for bone in self.bones:
            bone.rotation_mode='QUATERNION'
            for constraint in bone.constraints:
                if constraint.type=='IK':
                    constraint.influence=0
        self.cast_basis=None
        if asset not in ('sam','mom'):
            self.cast_basis={bone.name:bone.matrix_basis.copy() for bone in self.bones}
            if asset.startswith('kid'):
                for bone in self.arm.data.bones:
                    bone.inherit_scale='FIX_SHEAR'"""
assert old in s
s=s.replace(old,new)
old="""            b.rotation_quaternion=Quaternion()
            b.location=(0,0,0)
            b.scale=self.rest_scales[b.name]"""
new="""            if self.cast_basis is None:
                b.matrix_basis=Matrix.Diagonal((*self.rest_scales[b.name],1))
            else:
                b.matrix_basis=self.cast_basis[b.name]"""
assert old in s
s=s.replace(old,new)
old="""        b.rotation_quaternion=Quaternion(b.bone.matrix_local.to_quaternion().inverted()@Vector(axis),angle)"""
new="""        rotation=Quaternion(b.bone.matrix_local.to_quaternion().inverted()@Vector(axis),angle)
        if self.cast_basis is not None:
            rotation=self.cast_basis[b.name].to_quaternion()@rotation
        b.rotation_quaternion=rotation"""
assert old in s
s=s.replace(old,new).replace('for key in self.blink_keys: key.value=val',
                              "for key in self.blink_keys: key.value=max(val,.28 if self.name=='grandma' else 0)")
p.write_text(s,encoding='utf-8')

p=root/'street.py'
s=p.read_text(encoding='utf-8')
s=s.replace("person.primary(person.b('Spine'),(1,0,0),.122+.048*sinus)",
            "person.primary(person.b('Spine'),(1,0,0),(.020+.024*sinus) if lookat else (.105+.042*sinus))")
p.write_text(s,encoding='utf-8')
