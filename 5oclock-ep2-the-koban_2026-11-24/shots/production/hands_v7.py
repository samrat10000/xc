"""Anatomical palm orientation and coordinated finger posing on the existing VRM casts."""

DIGITS=('Index','Middle','Ring','Little')

def plane(forward,normal):
    y=Vector(forward).normalized()
    z=Vector(normal)-y*Vector(normal).dot(y)
    if z.length<.05:
        z=y.cross(Vector((1,0,0))) if abs(y.x)<.95 else y.cross(Vector((0,1,0)))
    z.normalize()
    x=y.cross(z).normalized()
    return Matrix((x,y,z)).transposed()

def hand_axes(actor,side):
    hand=actor.b('Hand',side).bone
    index=actor.b('Index1',side).bone.head_local
    middle=actor.b('Middle1',side).bone.head_local
    little=actor.b('Little1',side).bone.head_local
    forward=(middle-hand.head_local).normalized()
    inward=forward.cross(index-little)*(1 if side=='L' else -1)
    return plane(forward,inward)

def set_hand(actor,side,forward,palm,finger=.3,thumb=.3):
    hand=actor.b('Hand',side)
    original=hand_axes(actor,side)
    desired=plane(forward,palm)@original.transposed()@hand.bone.matrix_local.to_3x3()
    current=(actor.arm.matrix_world@hand.matrix).to_quaternion()
    hand.rotation_quaternion=hand.rotation_quaternion@(current.inverted()@desired.to_quaternion())
    inward=original.col[2]
    for i,digit in enumerate(DIGITS):
        for joint,relative in enumerate((.78,1,.59),1):
            bone=actor.b(f'{digit}{joint}',side)
            direction=bone.bone.tail_local-bone.bone.head_local
            axis=direction.cross(inward)
            local=bone.bone.matrix_local.to_quaternion().inverted()@axis.normalized()
            bone.rotation_quaternion=Quaternion(local,finger*relative*(.83+i*.11))
    for joint,relative in enumerate((.55,.61,.74),1):
        bone=actor.b(f'Thumb{joint}',side)
        direction=(bone.bone.tail_local-bone.bone.head_local).normalized()
        towards=(actor.b('Index2',side).bone.head_local-bone.bone.head_local).normalized()
        axis=direction.cross(towards).normalized()
        local=bone.bone.matrix_local.to_quaternion().inverted()@axis
        bone.rotation_quaternion=Quaternion(local,thumb*relative)
    bpy.context.view_layer.update()

def limb_diagnostics(actor,side,label,frame,target=None):
    wrist=actor.world('Hand',side)
    arm=(wrist-actor.world('LowerArm',side)).normalized()
    hand=(actor.world('Middle1',side)-wrist).normalized()
    xy=bpy_extras.object_utils.world_to_camera_view(sc,cam,wrist)
    gap='' if target is None else f' contact delta {(wrist-Vector(target)).length*1000:.1f} mm'
    print(f'{label} {frame} {side} wrist {math.degrees(arm.angle(hand)):.1f} deg '
          f'pixel ({round(xy.x*1080)},{round((1-xy.y)*1920)}){gap}',flush=True)

def forearm(actor,side):
    return (actor.world('Hand',side)-actor.world('LowerArm',side)).normalized()

def reach_hand(actor,side,wrist,pole,palm,curl,th=.3,direction=None):
    error=actor.chain(actor.b('UpperArm',side),actor.b('LowerArm',side),wrist,pole)
    set_hand(actor,side,forearm(actor,side) if direction is None else direction,palm,curl,th)
    return error
