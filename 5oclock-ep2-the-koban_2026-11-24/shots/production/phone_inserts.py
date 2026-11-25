"""Close shots of the established handset and the time-skip shadow sweep."""
import math

def close_desk():
    surface=mapped('Desk plank texture',ASSETS/'counter.png','917d9f','e4c9ac')
    dark=paint('Quiet wood edge','3c2e3f','836354')
    card('Desk surface',[(-1.6,-1.5,-.002),(1.6,-1.5,-.002),(1.6,1.5,-.002),(-1.6,1.5,-.002)],surface)
    ledger=box('Book backdrop',(-.181,.18,.004),(.207,.30,.014),dark,.003)
    ledger.rotation_euler.z=.29
    lamp('Small upper bounce',2.65,'#e5a98c',(-.58,.59,.36))
    lamp('Cool fill',.31,'#cacdeb',(.24,-.63,.74))
    return surface

def call_insert(reveal):
    close_desk()
    task='09' if reveal else '08'
    init=ASSETS/f'call_{task}'/'001.png'
    ring=bpy.data.images.load(str(ASSETS/'phone_ring.png'),check_existing=True)
    phone,texture,objs=handset(init,(0,0,.0006),(0,0,-.12))
    def mode(f):
        if not reveal and f<=22:
            return ring
        sample=f-(f-1)%2
        return bpy.data.images.load(str(ASSETS/f'call_{task}'/f'{sample:03d}.png'),check_existing=True)
    def frame(f):
        n=f-(f-1)%2
        ringing=1-interval(n,9,24)
        phone.location.x=.002*math.sin(n*2.2)*ringing+.0024*interval(n,1,22)
        phone.rotation_euler.z=-.145+.034*math.sin(n*1.9)*ringing
        texture.image=mode(f)
        k=interval(f,1,96)
        if reveal:
            # Start at the same phone angle, then put the small reflection near picture centre.
            look((.044-.036*k,-.181+.062*k,.255-.105*k),(.012+.014*k,.014+.032*k,.003),65)
        else:
            look((.056-.014*k,-.258+.039*k,.271-.013*k),(-.009,.012,.003),55)
    return 96,frame

def clock_insert():
    surface=close_desk()
    m,tex=handset(ASSETS/'clock_712.png',(0,0,.0006),(0,0,-.18))[:2]
    morning=bpy.data.images.load(str(ASSETS/'clock_712.png'),check_existing=True)
    evening=bpy.data.images.load(str(ASSETS/'clock_1659.png'),check_existing=True)
    mat=bpy.data.materials.new('Physical window shadow')
    mat.use_nodes=True
    mat.surface_render_method='BLENDED'
    nt=mat.node_tree
    nodes=nt.nodes
    links=nt.links
    nodes.clear()
    out=nodes.new('ShaderNodeOutputMaterial')
    transparent=nodes.new('ShaderNodeBsdfTransparent')
    dark=nodes.new('ShaderNodeEmission')
    dark.inputs[0].default_value=(.009,.007,.018,1)
    mix=nodes.new('ShaderNodeMixShader')
    mix.inputs[0].default_value=.62
    links.new(transparent.outputs[0],mix.inputs[1])
    links.new(dark.outputs[0],mix.inputs[2])
    links.new(mix.outputs[0],out.inputs[0])
    strips=[]
    for i in range(4):
        strips.append(card('Window shadow ribbon',[(i*.06-.20,-.26,.0089),(i*.06-.171,-.26,.0089),
                       (i*.06-.275,.26,.0089),(i*.06-.308,.26,.0089)],mat))
    day=area('Before time jump',(.2,-.14,.45),(0,0,0),26,'#e5c9b1',.38)
    dusk=area('After time jump',(-.40,.22,.52),(0,0,0),14,'#e0815e',.54)
    def frame(f):
        n=f-(f-1)%2
        phase=interval(n,41,53)
        tex.image=evening if f>=47 else morning
        mix.inputs[0].default_value=.42+phase*.11
        for i,ob in enumerate(strips):
            ob.location.x=phase*.27
        day.data.energy=26*(1-phase)
        dusk.data.energy=12+phase*21
        k=interval(f,1,96)
        look((.038-.014*k,-.144+.024*k,.259-.015*k),(0,.011,.002),61)
    return 96,frame


