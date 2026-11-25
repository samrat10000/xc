import argparse
import json
import math
import sys
from pathlib import Path
import bmesh
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Euler, Matrix, Quaternion, Vector

ROOT = Path(r"c:\Users\cross\Downloads\xc\creepy\ep02_nobody_leaves")
ASSETS = ROOT / "assets"

TOTAL_FRAMES = 288
FPS = 24
PROBE_FRAMES = [1, 45, 93, 145, 175, 206, 245, 286]


def lin(c: float) -> float:
    return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92


def lin_rgb(r: float, g: float, b: float) -> tuple[float, float, float, float]:
    return (lin(r), lin(g), lin(b), 1.0)


def hex_lin(h: str) -> tuple[float, float, float, float]:
    h = h.lstrip("#")
    return lin_rgb(int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0)


def smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _attach_corridor_depth_fade(nt, src_socket, dst_socket):
    """Attach noise-free corridor Y-depth darkening node chain; returns Value control node (1.0=on, 0.15=flicker)."""
    geom = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.interpolation_type = "SMOOTHSTEP"
    mr.clamp = True
    mr.inputs["From Min"].default_value = 3.1
    mr.inputs["From Max"].default_value = 6.0
    mr.inputs["To Min"].default_value = 1.0
    mr.inputs["To Max"].default_value = 0.04

    val_node = nt.nodes.new("ShaderNodeValue")
    val_node.outputs[0].default_value = 1.0

    mix_f = nt.nodes.new("ShaderNodeMix")
    mix_f.data_type = "FLOAT"
    mix_f.inputs[2].default_value = 1.0  # A

    mul_c = nt.nodes.new("ShaderNodeMix")
    mul_c.data_type = "RGBA"
    mul_c.blend_type = "MULTIPLY"
    mul_c.inputs[0].default_value = 1.0

    nt.links.new(geom.outputs["Position"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["Y"], mr.inputs["Value"])
    nt.links.new(val_node.outputs[0], mix_f.inputs[0])
    nt.links.new(mr.outputs["Result"], mix_f.inputs[3])
    nt.links.new(src_socket, mul_c.inputs[6])
    nt.links.new(mix_f.outputs[0], mul_c.inputs[7])
    nt.links.new(mul_c.outputs[2], dst_socket)
    return val_node


def make_psx_image_mat(name: str, img_path: Path, roughness: float = 0.88, emission_strength: float = 0.0, spec_level: float = 0.45, depth_fade_list=None):
    """Load low-res texture with Closest (nearest-neighbor) PS1 filtering."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(img_path))
    tex.interpolation = "Closest"

    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Specular IOR Level"].default_value = spec_level
    bsdf.inputs["IOR"].default_value = 1.40
    if depth_fade_list is not None:
        depth_fade_list.append(_attach_corridor_depth_fade(nt, tex.outputs["Color"], bsdf.inputs["Base Color"]))
    else:
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if emission_strength > 0.0:
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_crisp_eye_mat(name: str, img_path: Path, emit_strength: float = 0.92):
    """Blowout-proof eye shader: 82% controlled emission + 18% matte diffuse so 200W lights never wash iris/veins."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(img_path))
    tex.interpolation = "Closest"

    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.25
    bsdf.inputs["Specular IOR Level"].default_value = 0.05

    emit = nt.nodes.new("ShaderNodeEmission")
    emit.inputs["Strength"].default_value = emit_strength

    mix_s = nt.nodes.new("ShaderNodeMixShader")
    mix_s.inputs["Fac"].default_value = 0.82

    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], emit.inputs["Color"])
    nt.links.new(bsdf.outputs["BSDF"], mix_s.inputs[1])
    nt.links.new(emit.outputs["Emission"], mix_s.inputs[2])
    nt.links.new(mix_s.outputs["Shader"], out.inputs["Surface"])
    return mat


def make_arm_rim_mat(name: str, rim_rgba, rim_power: float = 0.62, rim_strength: float = 0.45):
    """Charred matte void-black arm material with subtle blood-crimson grazing edge rim."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")

    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.002, 0.001, 0.001, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.72
    bsdf.inputs["Specular IOR Level"].default_value = 0.08

    rim = nt.nodes.new("ShaderNodeEmission")
    rim.inputs["Color"].default_value = rim_rgba
    rim.inputs["Strength"].default_value = rim_strength

    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = rim_power
    ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp.color_ramp.elements[1].position = min(0.96, rim_power + 0.18)
    ramp.color_ramp.elements[1].color = (1, 1, 1, 1)

    mix_s = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lw.outputs["Facing"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], mix_s.inputs["Fac"])
    nt.links.new(bsdf.outputs["BSDF"], mix_s.inputs[1])
    nt.links.new(rim.outputs["Emission"], mix_s.inputs[2])
    nt.links.new(mix_s.outputs["Shader"], out.inputs["Surface"])
    return mat


def make_mat_solid(name: str, rgba, roughness: float = 0.85, emission_rgba=None, emission_strength: float = 0.0, pure_emission: bool = False, spec_level: float = 0.4, depth_fade_list=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    if pure_emission and emission_rgba is not None:
        emit = nt.nodes.new("ShaderNodeEmission")
        emit.inputs["Color"].default_value = emission_rgba
        emit.inputs["Strength"].default_value = emission_strength
        nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    else:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Specular IOR Level"].default_value = spec_level
        if depth_fade_list is not None:
            rgb_src = nt.nodes.new("ShaderNodeRGB")
            rgb_src.outputs["Color"].default_value = rgba
            depth_fade_list.append(_attach_corridor_depth_fade(nt, rgb_src.outputs["Color"], bsdf.inputs["Base Color"]))
        if emission_rgba is not None and emission_strength > 0.0:
            bsdf.inputs["Emission Color"].default_value = emission_rgba
            bsdf.inputs["Emission Strength"].default_value = emission_strength
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def add_uv_plane(name: str, loc, width: float, height: float, mat, rot=(math.radians(90), 0, 0), repeat_xy=(1.0, 1.0)):
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (width, height, 1.0)
    obj.rotation_euler = rot
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()
    for f in bm.faces:
        for l in f.loops:
            u, v = l[uv_layer].uv
            l[uv_layer].uv = (u * repeat_xy[0], v * repeat_xy[1])
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.data.materials.append(mat)
    return obj


def add_box(name: str, loc, size, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    return obj


def _make_almond_lid(name: str, radius: float, is_upper: bool, mat):
    """Smooth almond-shaped fleshy eyelid cap hugging front of eyeball (-Y)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    n_az, n_el = 24, 6
    rings = []
    for ei in range(n_el):
        ef = ei / float(n_el - 1)
        ring = []
        for ai in range(n_az):
            az = (ai / float(n_az)) * 2.0 * math.pi - math.pi
            front = max(0.0, math.cos(az))
            if is_upper:
                el_rim = 0.25 * (front ** 1.2) - 0.16 * (1.0 - front)
                el = el_rim * (1.0 - ef) + (math.pi * 0.495) * ef
            else:
                el_rim = -0.30 * (front ** 1.2) + 0.16 * (1.0 - front)
                el = (-math.pi * 0.495) * (1.0 - ef) + el_rim * ef
            rc = radius * math.cos(el)
            ring.append(bm.verts.new((rc * math.sin(az), -rc * math.cos(az), radius * math.sin(el))))
        rings.append(ring)
    for ei in range(n_el - 1):
        for ai in range(n_az):
            na = (ai + 1) % n_az
            bm.faces.new([rings[ei][ai], rings[ei][na], rings[ei + 1][na], rings[ei + 1][ai]])
    pole = rings[-1] if is_upper else rings[0]
    bm.faces.new(pole if is_upper else list(reversed(pole)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    sol = obj.modifiers.new("Solidify", "SOLIDIFY")
    sol.thickness = radius * 0.14
    sol.offset = 1.0
    return obj


def _make_eyeball(name: str, radius: float, mat):
    """UV sphere with planar front-facing (-Y) UVs for psx_eye_seraph.png."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=radius, location=(0, 0, 0))
    eb = bpy.context.active_object
    eb.name = name
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(eb.data)
    uv_layer = bm.loops.layers.uv.verify()
    for f in bm.faces:
        f.smooth = True
        for l in f.loops:
            co = l.vert.co
            u = max(0.002, min(0.998, 0.5 + co.x / (2.0 * radius)))
            v = max(0.002, min(0.998, 0.5 + co.z / (2.0 * radius)))
            l[uv_layer].uv = (u, v)
    bmesh.update_edit_mesh(eb.data)
    bpy.ops.object.mode_set(mode="OBJECT")
    eb.data.materials.append(mat)
    return eb


def build_hallway():
    depth_fade_nodes = []
    wall_mat = make_psx_image_mat("PSX_Wall", ASSETS / "psx_wall_plaster.png", roughness=0.92, depth_fade_list=depth_fade_nodes)
    ceil_mat = make_psx_image_mat("PSX_Ceiling", ASSETS / "psx_ceiling_tile.png", roughness=0.95, depth_fade_list=depth_fade_nodes)
    carpet_mat = make_psx_image_mat("PSX_Carpet", ASSETS / "psx_carpet_crimson.png", roughness=0.88, depth_fade_list=depth_fade_nodes)
    door_mat = make_psx_image_mat("PSX_Door", ASSETS / "psx_door_grimy.png", roughness=0.82)
    note_mat = make_psx_image_mat("PSX_Note", ASSETS / "psx_note_wall.png", roughness=0.78)
    void_mat = make_mat_solid("Void_Dark", (0.002, 0.002, 0.003, 1.0), roughness=0.95)
    trim_mat = make_mat_solid("Trim_Grime", hex_lin("#232420"), roughness=0.85, depth_fade_list=depth_fade_nodes)
    brass_mat = make_mat_solid("Brass_Old", hex_lin("#8A6E34"), roughness=0.38)

    # Corridor dimensions: x in [-0.88, +0.88], y in [-1.8, +9.5], z in [0.0, 2.75]
    # Note plane facing +X is rot=(90 deg, 0, -90 deg)? Let's verify:
    # Default plane normal = +Z, local X=width, local Y=height.
    # Euler XYZ (-90 deg, 0, -90 deg) -> wait: use Euler((math.radians(90), 0, math.radians(-90))):
    # R_z(-90) * R_x(+90): R_x(90) maps +Z -> -Y, +Y -> +Z; R_z(-90) maps -Y -> -X! Normal becomes -X!
    # So rot=(math.radians(90), 0, math.radians(+90)) maps +Z -> -Y -> +X (facing into hallway from Left wall)!
    # And rot=(math.radians(90), 0, math.radians(-90)) maps +Z -> -Y -> -X (facing into hallway from Right wall)!
    add_uv_plane("Wall_Right", (0.88, 3.85, 1.375), 11.3, 2.75, wall_mat, rot=(math.radians(90), 0, math.radians(-90)), repeat_xy=(4.0, 1.0))

    # Left wall around Doorway y in [1.40, 2.35], z in [0.0, 2.13]:
    # Segment 1 (front): y in [-1.80, 1.40] (len 3.20, center -0.20)
    add_uv_plane("Wall_Left_Front", (-0.88, -0.20, 1.375), 3.20, 2.75, wall_mat, rot=(math.radians(90), 0, math.radians(90)), repeat_xy=(1.15, 1.0))
    # Segment 2 (header above door): y in [1.40, 2.35] (len 0.95, center 1.875), z in [2.13, 2.75] (h 0.62, cz 2.44)
    add_uv_plane("Wall_Left_Header", (-0.88, 1.875, 2.44), 0.95, 0.62, wall_mat, rot=(math.radians(90), 0, math.radians(90)), repeat_xy=(0.35, 0.25))
    # Segment 3 (back): y in [2.35, 9.50] (len 7.15, center 5.925)
    add_uv_plane("Wall_Left_Back", (-0.88, 5.925, 1.375), 7.15, 2.75, wall_mat, rot=(math.radians(90), 0, math.radians(90)), repeat_xy=(2.6, 1.0))

    # Floor & Ceiling
    add_uv_plane("Floor_Carpet", (0.0, 3.85, 0.0), 1.80, 11.3, carpet_mat, rot=(0.0, 0.0, 0.0), repeat_xy=(1.5, 8.0))
    add_uv_plane("Ceiling_Plaster", (0.0, 3.85, 2.75), 1.80, 11.3, ceil_mat, rot=(math.radians(180), 0.0, 0.0), repeat_xy=(1.2, 6.0))
    add_uv_plane("Wall_Back_Void", (0.0, 9.50, 1.375), 1.84, 2.80, void_mat, rot=(math.radians(90), 0.0, 0.0))

    # Baseboards & molding
    add_box("Baseboard_Right", (0.865, 3.85, 0.06), (0.03, 11.3, 0.12), trim_mat)
    add_box("Baseboard_Left_Front", (-0.865, -0.20, 0.06), (0.03, 3.20, 0.12), trim_mat)
    add_box("Baseboard_Left_Back", (-0.865, 5.925, 0.06), (0.03, 7.15, 0.12), trim_mat)

    # Recessed Doorframe Jambs + Pitch-Black Room behind x < -0.92
    add_box("Doorframe_L_Front", (-0.90, 1.385, 1.075), (0.09, 0.035, 2.15), trim_mat)
    add_box("Doorframe_L_Back", (-0.90, 2.365, 1.075), (0.09, 0.035, 2.15), trim_mat)
    add_box("Doorframe_L_Top", (-0.90, 1.875, 2.145), (0.09, 1.01, 0.04), trim_mat)
    add_box("DarkRoom_Back", (-2.10, 1.875, 1.30), (0.08, 2.20, 2.80), void_mat)
    add_box("DarkRoom_SideF", (-1.50, 0.85, 1.30), (1.30, 0.08, 2.80), void_mat)
    add_box("DarkRoom_SideB", (-1.50, 2.90, 1.30), (1.30, 0.08, 2.80), void_mat)
    add_box("DarkRoom_Floor", (-1.50, 1.875, -0.02), (1.30, 2.20, 0.04), void_mat)
    add_box("DarkRoom_Ceil", (-1.50, 1.875, 2.40), (1.30, 2.20, 0.04), void_mat)

    # Peeling 'DO NOT OPEN' warning slip beside left doorframe
    add_uv_plane("Wall_Note_Left", (-0.874, 1.18, 1.50), 0.15, 0.15, note_mat, rot=(math.radians(90), math.radians(-4.0), math.radians(90)))

    # Hinged 3D Door_Left pivoted at back hinge (-0.90, 2.35, 0.0); door leaf runs y_local in [-0.95, 0.0]
    me = bpy.data.meshes.new("Door_Left")
    bm = bmesh.new()
    v000 = bm.verts.new((-0.04, -0.95, 0.00))
    v100 = bm.verts.new((+0.00, -0.95, 0.00))
    v110 = bm.verts.new((+0.00,  0.00, 0.00))
    v010 = bm.verts.new((-0.04,  0.00, 0.00))
    v001 = bm.verts.new((-0.04, -0.95, 2.13))
    v101 = bm.verts.new((+0.00, -0.95, 2.13))
    v111 = bm.verts.new((+0.00,  0.00, 2.13))
    v011 = bm.verts.new((-0.04,  0.00, 2.13))
    f_front = bm.faces.new([v110, v100, v101, v111])  # +X corridor-facing
    bm.faces.new([v000, v010, v011, v001])             # -X back
    bm.faces.new([v000, v100, v101, v001])             # -Y latch edge
    bm.faces.new([v110, v010, v011, v111])             # +Y hinge edge
    bm.faces.new([v001, v101, v111, v011])             # +Z top
    bm.faces.new([v000, v010, v110, v100])             # -Z bottom
    uv_layer = bm.loops.layers.uv.verify()
    for l in f_front.loops:
        co = l.vert.co
        l[uv_layer].uv = (max(0.0, min(1.0, -co.y / 0.95)), max(0.0, min(1.0, co.z / 2.13)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()

    door_obj = bpy.data.objects.new("Door_Left", me)
    bpy.context.collection.objects.link(door_obj)
    door_obj.location = (-0.90, 2.35, 0.0)
    door_obj.rotation_mode = "XYZ"
    door_obj.data.materials.append(door_mat)

    # 3D Brass doorknob & deadbolt mounted directly on Door_Left
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.028, depth=0.045, location=(0.022, -0.85, 1.03), rotation=(0, math.radians(90), 0))
    knob = bpy.context.active_object
    knob.name = "Door_Brass_Knob"
    knob.data.materials.append(brass_mat)
    knob.parent = door_obj

    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.018, depth=0.025, location=(0.012, -0.85, 1.16), rotation=(0, math.radians(90), 0))
    bolt = bpy.context.active_object
    bolt.name = "Door_Deadbolt"
    bolt.data.materials.append(trim_mat)
    bolt.parent = door_obj

    # Distant ceiling light fixture cage at y=5.4, z=2.72
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.14, depth=0.06, location=(0.0, 5.40, 2.72))
    fixt = bpy.context.active_object
    fixt.name = "Hall_Ceiling_Fixture"
    fixt.data.materials.append(trim_mat)

    return door_obj, depth_fade_nodes


def build_door_lurker():
    """Peering dark-flesh hand & unmistakable bloodshot eye inside the -30 deg door crack (f130-f197)."""
    lurk_mat = make_mat_solid("DoorLurker_Flesh", (0.008, 0.007, 0.008, 1.0), roughness=0.58, spec_level=0.10)
    lid_mat = make_mat_solid("DoorLurker_Lid", (0.003, 0.002, 0.003, 1.0), roughness=0.65, spec_level=0.05)
    eye_mat = make_crisp_eye_mat("DoorLurker_EyeMat", ASSETS / "psx_eye_seraph.png", emit_strength=1.45)

    root = bpy.data.objects.new("DoorLurker_Root", None)
    bpy.context.collection.objects.link(root)
    root.location = (-1.30, 1.42, 0.0)

    # Dark torso mass behind doorway
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.18, 0.24, 0.98))
    body = bpy.context.active_object
    body.name = "DoorLurker_Body"
    body.scale = (0.30, 0.28, 1.92)
    body.data.materials.append(lurk_mat)
    body.parent = root

    # Heavy-lidded peering bloodshot eye clearly inside open crack behind jamb (world ~ (-0.885, 1.52, 1.52)), aiming at cam
    eye_piv = bpy.data.objects.new("DoorLurker_EyePivot", None)
    bpy.context.collection.objects.link(eye_piv)
    eye_piv.parent = root
    eye_piv.location = (0.065, 0.10, 1.52)
    eye_piv.rotation_mode = "XYZ"
    eye_piv.rotation_euler = (0.0, 0.0, math.radians(16.0))

    eb = _make_eyeball("DoorLurker_Eyeball", 0.044, eye_mat)
    eb.parent = eye_piv
    ul = _make_almond_lid("DoorLurker_UpperLid", 0.047, True, lid_mat)
    ul.parent = eye_piv
    ll = _make_almond_lid("DoorLurker_LowerLid", 0.047, False, lid_mat)
    ll.parent = eye_piv

    # 4 gaunt dark curved Bezier fingers reaching out around front jamb edge (-0.84, 1.38, 1.15)
    for fi, z_off in enumerate((0.032, 0.010, -0.010, -0.030)):
        fc = bpy.data.curves.new(name=f"DoorLurker_Claw_{fi}", type="CURVE")
        fc.dimensions = "3D"
        fc.resolution_u = 12
        fc.bevel_depth = 0.0075
        fc.bevel_resolution = 4
        fc.use_fill_caps = True
        sp = fc.splines.new("BEZIER")
        sp.bezier_points.add(3)
        pts = [
            ((-0.05, 0.02, 1.15 + z_off), 1.1),
            ((0.04, -0.03, 1.15 + z_off), 0.9),
            ((0.12, -0.06, 1.14 + z_off), 0.70),
            ((0.14, -0.04, 1.12 + z_off), 0.28),
        ]
        for pi, (pt, rr) in enumerate(pts):
            bp = sp.bezier_points[pi]
            bp.co = Vector(pt)
            bp.radius = rr
            bp.handle_left_type = "AUTO"
            bp.handle_right_type = "AUTO"
        fo = bpy.data.objects.new(f"DoorLurker_Claw_{fi}", fc)
        bpy.context.collection.objects.link(fo)
        fo.data.materials.append(lurk_mat)
        fo.parent = root

    return root


def _make_seraph_cloak(cloak_mat):
    """Tall looming tapered gothic shroud (zero chess-pawn mushroom bulge -> pure dread silhouette)."""
    me = bpy.data.meshes.new("Seraph_Cloak")
    bm = bmesh.new()
    n_seg = 28
    # Continuous ominously tapering tall cloaked silhouette with subtle draped shoulder folds
    z_list = [0.00, 0.35, 0.75, 1.15, 1.48, 1.70, 1.88, 2.00, 2.06]
    r_list = [0.62, 0.50, 0.40, 0.32, 0.27, 0.25, 0.19, 0.13, 0.09]
    rings = []
    for z, rad in zip(z_list, r_list):
        ring = []
        for si in range(n_seg):
            th = (si / float(n_seg)) * 2.0 * math.pi
            fold = (0.020 * (1.0 - z / 2.06) + 0.005) * math.cos(7.0 * th + 0.4)
            rx = rad + fold
            ry = (rad * 0.70) + fold * 0.7
            ring.append(bm.verts.new((rx * math.cos(th), ry * math.sin(th), z)))
        rings.append(ring)
    for ri in range(len(rings) - 1):
        for si in range(n_seg):
            ns = (si + 1) % n_seg
            bm.faces.new([rings[ri][si], rings[ri][ns], rings[ri + 1][ns], rings[ri + 1][si]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new("Seraph_Cloak", me)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(cloak_mat)
    sub = obj.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 1
    return obj


def _make_star_petal(name: str, mat):
    """Sculpt one curved tapering star-petal blade along +Z from z=0.0 to z=0.42."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    n_stations = 9
    n_radial = 8
    rings = []
    for i in range(n_stations):
        t = i / float(n_stations - 1)
        z = 0.09 + 0.36 * t
        # Taper softly at base, widest at t=0.22, sharp tapering blade tip at t=1.0
        w = 0.095 * math.sin(math.pow(t, 0.55) * math.pi * 0.92 + 0.18) * (1.0 - 0.85 * (t ** 2.2))
        d = 0.032 * (1.0 - 0.78 * t)
        y_arch = -0.025 * math.sin(t * math.pi)
        ring = []
        for s in range(n_radial):
            th = (s / float(n_radial)) * 2.0 * math.pi
            ring.append(bm.verts.new((w * math.cos(th), y_arch + d * math.sin(th), z)))
        rings.append(ring)
    for i in range(n_stations - 1):
        for s in range(n_radial):
            ns = (s + 1) % n_radial
            bm.faces.new([rings[i][s], rings[i][ns], rings[i + 1][ns], rings[i + 1][s]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    uv_layer = bm.loops.layers.uv.verify()
    for f in bm.faces:
        f.smooth = True
        for l in f.loops:
            co = l.vert.co
            l[uv_layer].uv = (max(0.0, min(1.0, 0.5 + co.x / 0.20)), max(0.0, min(1.0, (co.z - 0.09) / 0.36)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    sub = obj.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 1
    return obj


def build_seraph_entity():
    """Towering 6-petal Star-Eye Seraph with blowout-proof eyes, 6 calyx eyes & corridor-caging clawed arms."""
    cloak_mat = make_mat_solid("Seraph_Void_Cloak", (0.001, 0.001, 0.001, 1.0), roughness=0.95, spec_level=0.02)
    arm_mat = make_arm_rim_mat("Seraph_Arm_Claw_Mat", hex_lin("#A80A0A"), rim_power=0.62, rim_strength=0.45)
    eye_mat = make_crisp_eye_mat("Seraph_Eye_Mat", ASSETS / "psx_eye_seraph.png", emit_strength=0.92)
    mini_eye_mat = make_crisp_eye_mat("Seraph_MiniEye_Mat", ASSETS / "psx_eye_seraph.png", emit_strength=1.05)

    # Animated Star Petal Shader: psx_star_flesh.png tinted by Mix Color -> Emission Strength
    petal_mat = bpy.data.materials.new("Seraph_Star_Mat")
    petal_mat.use_nodes = True
    nt = petal_mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(ASSETS / "psx_star_flesh.png"))
    tex.interpolation = "Closest"
    tint_mul = nt.nodes.new("ShaderNodeMix")
    tint_mul.data_type = "RGBA"
    tint_mul.blend_type = "MULTIPLY"
    tint_mul.inputs["Factor"].default_value = 1.0
    tint_mul.inputs[7].default_value = hex_lin("#FFF7DF")
    emit = nt.nodes.new("ShaderNodeEmission")
    emit.inputs["Strength"].default_value = 6.2
    nt.links.new(tex.outputs["Color"], tint_mul.inputs[6])
    nt.links.new(tint_mul.outputs[2], emit.inputs["Color"])
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])

    root = bpy.data.objects.new("Seraph_Root", None)
    bpy.context.collection.objects.link(root)
    root.location = (0.18, 3.45, 0.0)
    root.rotation_mode = "XYZ"

    cloak = _make_seraph_cloak(cloak_mat)
    cloak.parent = root
    cloak.visible_shadow = False

    head_piv = bpy.data.objects.new("Seraph_HeadPivot", None)
    bpy.context.collection.objects.link(head_piv)
    head_piv.parent = root
    head_piv.location = (0.0, -0.02, 2.08)
    head_piv.rotation_mode = "XYZ"

    # Dark recessed central shadow calyx ring framing MainEye + concealing 6 closed MiniEyes in Beats 1-2
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=0.175, depth=0.06, location=(0.0, -0.018, 0.0), rotation=(math.radians(90), 0, 0))
    calyx = bpy.context.active_object
    calyx.name = "Seraph_ShadowCalyx"
    calyx.data.materials.append(cloak_mat)
    calyx.parent = head_piv
    calyx.visible_shadow = False

    # Central staring bloodshot eyeball + animated blinking eyelids
    main_eye = _make_eyeball("Seraph_MainEye", 0.088, eye_mat)
    main_eye.parent = head_piv
    main_eye.location = (0.0, -0.056, 0.0)
    main_eye.rotation_mode = "XYZ"
    main_eye.visible_shadow = False

    main_ul = _make_almond_lid("Seraph_UpperLid", 0.095, True, cloak_mat)
    main_ul.parent = head_piv
    main_ul.location = (0.0, -0.056, 0.0)
    main_ul.rotation_mode = "XYZ"
    main_ul.visible_shadow = False

    main_ll = _make_almond_lid("Seraph_LowerLid", 0.095, False, cloak_mat)
    main_ll.parent = head_piv
    main_ll.location = (0.0, -0.056, 0.0)
    main_ll.rotation_mode = "XYZ"
    main_ll.visible_shadow = False

    # Hidden secondary calyx eyes (0.042m radius at r=0.160m, y=-0.062m -> 7-eyed Seraph in Beat 3!)
    petals = []
    mini_eyes = []
    for k in range(6):
        ang_deg = k * 60.0
        ppiv = bpy.data.objects.new(f"Seraph_PetalPivot_{k}", None)
        bpy.context.collection.objects.link(ppiv)
        ppiv.parent = head_piv
        ppiv.rotation_mode = "XYZ"
        ppiv.rotation_euler = (0.0, math.radians(ang_deg), 0.0)

        pobj = _make_star_petal(f"Seraph_Petal_{k}", petal_mat)
        pobj.parent = ppiv
        pobj.rotation_mode = "XYZ"
        pobj.visible_shadow = False
        petals.append(pobj)

        m_ang = math.radians(k * 60.0 + 30.0)
        mx = 0.160 * math.sin(m_ang)
        mz = 0.160 * math.cos(m_ang)
        mpiv = bpy.data.objects.new(f"Seraph_MiniEyePivot_{k}", None)
        bpy.context.collection.objects.link(mpiv)
        mpiv.parent = head_piv
        mpiv.location = (mx, -0.062, mz)
        mpiv.rotation_mode = "XYZ"
        mpiv.rotation_euler = (0.0, m_ang, 0.0)

        m_eb = _make_eyeball(f"Seraph_MiniEye_{k}", 0.042, mini_eye_mat)
        m_eb.parent = mpiv
        m_eb.visible_shadow = False
        m_ul = _make_almond_lid(f"Seraph_MiniUpperLid_{k}", 0.045, True, cloak_mat)
        m_ul.parent = mpiv
        m_ul.rotation_mode = "XYZ"
        m_ul.visible_shadow = False
        m_ll = _make_almond_lid(f"Seraph_MiniLowerLid_{k}", 0.045, False, cloak_mat)
        m_ll.parent = mpiv
        m_ll.rotation_mode = "XYZ"
        m_ll.visible_shadow = False
        mini_eyes.append((mpiv, m_ul, m_ll))

    # 2 Anatomical Corridor-Caging Shadow-Arms (asymmetrical reach accounts for root.x=+0.18 -> ZERO wall clipping!)
    arms = []
    arm_configs = [
        ("L", -1.0, -0.76, -0.52, +0.06),  # root(+0.18) - 0.20 - 0.76 = -0.78 (10cm inside Wall_Left=-0.88)
        ("R", +1.0, +0.42, -0.48, +0.16),  # root(+0.18) + 0.20 + 0.42 = +0.80 (8cm inside Wall_Right=+0.88)
    ]
    for side, s_sign, palm_x, palm_y, palm_z in arm_configs:
        apiv = bpy.data.objects.new(f"Seraph_ArmPivot_{side}", None)
        bpy.context.collection.objects.link(apiv)
        apiv.parent = root
        apiv.location = (s_sign * 0.20, -0.02, 1.56)
        apiv.rotation_mode = "XYZ"

        ac = bpy.data.curves.new(name=f"Seraph_Arm_{side}", type="CURVE")
        ac.dimensions = "3D"
        ac.resolution_u = 20
        ac.bevel_depth = 0.048
        ac.bevel_resolution = 6
        ac.use_fill_caps = True
        sp = ac.splines.new("BEZIER")
        sp.bezier_points.add(3)
        a_pts = [
            ((0.0, 0.0, 0.0), 1.35),                                   # shoulder root inside mantle
            ((palm_x * 0.34, -0.08, -0.26), 0.85),                     # low gaunt bent elbow
            ((palm_x * 0.72, palm_y * 0.58, palm_z - 0.08), 0.65),     # rising forearm
            ((palm_x, palm_y, palm_z), 0.48),                          # bony wrist bracing near wall
        ]
        for pi, (pt, rr) in enumerate(a_pts):
            bp = sp.bezier_points[pi]
            bp.co = Vector(pt)
            bp.radius = rr
            bp.handle_left_type = "AUTO"
            bp.handle_right_type = "AUTO"
        aobj = bpy.data.objects.new(f"Seraph_Arm_{side}", ac)
        bpy.context.collection.objects.link(aobj)
        aobj.data.materials.append(arm_mat)
        aobj.parent = apiv

        # Sleek gaunt palm bridge
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=1.0, location=(palm_x, palm_y, palm_z))
        palm_obj = bpy.context.active_object
        palm_obj.name = f"Seraph_ArmPalm_{side}"
        palm_obj.scale = (0.028, 0.040, 0.044)
        palm_obj.data.materials.append(arm_mat)
        palm_obj.parent = apiv

        # 5 long curved talons (~14cm) bracing/clawing toward the wall without penetrating
        for ci, dz_c in enumerate((-0.036, -0.018, 0.0, 0.018, 0.036)):
            cc = bpy.data.curves.new(name=f"Seraph_ArmClaw_{side}_{ci}", type="CURVE")
            cc.dimensions = "3D"
            cc.resolution_u = 10
            cc.bevel_depth = 0.0085
            cc.bevel_resolution = 4
            cc.use_fill_caps = True
            csp = cc.splines.new("BEZIER")
            csp.bezier_points.add(2)
            base_w = Vector((palm_x, palm_y - 0.015, palm_z + dz_c))
            c_pts = [
                (base_w, 1.0),
                (base_w + Vector((s_sign * 0.055, -0.055, dz_c * 1.3 + 0.012)), 0.72),
                (base_w + Vector((s_sign * 0.075, -0.105, dz_c * 1.9 - 0.025)), 0.16),
            ]
            for pi, (pt, rr) in enumerate(c_pts):
                bp = csp.bezier_points[pi]
                bp.co = pt
                bp.radius = rr
                bp.handle_left_type = "AUTO"
                bp.handle_right_type = "AUTO"
            cobj = bpy.data.objects.new(f"Seraph_ArmClaw_{side}_{ci}", cc)
            bpy.context.collection.objects.link(cobj)
            cobj.data.materials.append(arm_mat)
            cobj.parent = apiv

        arms.append((apiv, s_sign))

    return {
        "root": root,
        "head_piv": head_piv,
        "main_eye": main_eye,
        "main_ul": main_ul,
        "main_ll": main_ll,
        "petals": petals,
        "mini_eyes": mini_eyes,
        "arms": arms,
        "tint_node": tint_mul.inputs[7],
        "emit_node": emit.inputs["Strength"],
    }


def build_hall_shadows():
    """3 distant shadowed corridor figures revealed briefly when the ceiling fixture flickers (f091-f096)."""
    void_mat = make_mat_solid("HallShadow_Body", (0.002, 0.002, 0.003, 1.0), roughness=0.92)
    eye_mat = make_mat_solid("HallShadow_Eye", hex_lin("#D8D8D0"), emission_rgba=hex_lin("#D8D8D0"), emission_strength=2.2, pure_emission=True)

    specs = [(-0.34, 5.20, 1.92), (0.30, 5.90, 2.08), (-0.06, 6.50, 2.18)]
    shadows = []
    for idx, (sx, sy, h) in enumerate(specs):
        sr = bpy.data.objects.new(f"HallShadow_{idx}", None)
        bpy.context.collection.objects.link(sr)
        sr.location = (sx, sy, 0.0)
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.22, radius2=0.07, depth=h * 0.86, location=(0, 0, h * 0.43))
        b = bpy.context.active_object
        b.name = f"HallShadow_Body_{idx}"
        b.data.materials.append(void_mat)
        b.parent = sr
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.09, location=(0, 0, h * 0.92))
        hd = bpy.context.active_object
        hd.name = f"HallShadow_Head_{idx}"
        hd.scale = (0.85, 0.95, 1.15)
        hd.data.materials.append(void_mat)
        hd.parent = sr
        for side, ex in (("L", -0.026), ("R", 0.026)):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.008, location=(ex, -0.078, h * 0.93))
            eo = bpy.context.active_object
            eo.name = f"HallShadow_Eye_{idx}_{side}"
            eo.data.materials.append(eye_mat)
            eo.parent = sr
        shadows.append(sr)

    # Beat 3 Distant Hallway Watcher Eyes Surge (f228-f288): 3 pairs of eerie staring eyes flanking the cloak deep down corridor
    back_eye_mat = make_mat_solid("BackWatcher_Eye_Mat", hex_lin("#D83838"), emission_rgba=hex_lin("#D83838"), emission_strength=0.0, pure_emission=True)
    back_eye_emit = [n for n in back_eye_mat.node_tree.nodes if n.type == "EMISSION"][0]
    bw_specs = [(-0.68, 4.30, 1.98), (0.72, 4.80, 1.72), (-0.64, 5.40, 1.24)]
    bw_roots = []
    for bi, (bx, by, bz) in enumerate(bw_specs):
        br = bpy.data.objects.new(f"BackWatcherEyes_{bi}", None)
        bpy.context.collection.objects.link(br)
        br.location = (bx, by, bz)
        for side, ex in (("L", -0.036), ("R", 0.036)):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.020, location=(ex, 0.0, 0.0))
            eo = bpy.context.active_object
            eo.name = f"BackWatcherEye_{bi}_{side}"
            eo.data.materials.append(back_eye_mat)
            eo.parent = br
        bw_roots.append(br)

    return shadows, (bw_roots, back_eye_emit)


def setup_lighting_and_camera(seraph_head_piv):
    world = bpy.data.worlds.new("PSX_Hall_World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = hex_lin("#030304")
    bg.inputs["Strength"].default_value = 0.04

    # Main blinding star-head point light slightly forward of body (+0.04 in Z, -0.24 in Y)
    bpy.ops.object.light_add(type="POINT", location=(0.0, -0.24, 0.04))
    star_pt = bpy.context.active_object
    star_pt.name = "Seraph_Head_Light"
    star_pt.parent = seraph_head_piv
    star_pt.data.color = (1.0, 0.94, 0.78)
    star_pt.data.energy = 140.0
    star_pt.data.shadow_soft_size = 0.05
    star_pt.data.use_shadow_jitter = False
    star_pt.data.shadow_filter_radius = 2.0
    star_pt.data.use_custom_distance = True
    star_pt.data.cutoff_distance = 5.4

    # Low POV corridor ambient near camera so grimy left door & carpet grain stay visible in deep shadow
    bpy.ops.object.light_add(type="AREA", location=(-0.10, -1.10, 1.60))
    pov_fill = bpy.context.active_object
    pov_fill.name = "POV_Dim_Ambient"
    pov_fill.data.color = (0.76, 0.78, 0.74)
    pov_fill.data.energy = 6.5
    pov_fill.data.size = 1.4
    pov_fill.data.use_shadow = False
    pov_fill.data.use_custom_distance = True
    pov_fill.data.cutoff_distance = 4.6
    pov_fill.rotation_euler = (math.radians(82), 0, 0)

    # Distant flickering ceiling fixture light at y=5.4
    bpy.ops.object.light_add(type="POINT", location=(0.0, 5.35, 2.52))
    back_pt = bpy.context.active_object
    back_pt.name = "Hall_Back_Light"
    back_pt.data.color = (0.78, 0.84, 0.72)
    back_pt.data.energy = 0.0
    back_pt.data.use_shadow_jitter = False
    back_pt.data.shadow_soft_size = 0.06
    back_pt.data.shadow_filter_radius = 1.8

    # First-person POV camera framing left grimy door + crimson carpet + towering right-center Seraph
    bpy.ops.object.camera_add(location=(-0.10, -1.25, 1.45))
    cam = bpy.context.active_object
    cam.name = "Main_Camera"
    cam.data.lens = 19.5
    cam.data.sensor_fit = "VERTICAL"
    cam.data.sensor_height = 24.0
    cam.rotation_mode = "XYZ"
    cam.rotation_euler = (math.radians(91.0), 0.0, 0.0)
    bpy.context.scene.camera = cam

    return cam, star_pt, back_pt


def _set_tree_hide(obj, hide: bool):
    obj.hide_render = hide
    for ch in obj.children:
        _set_tree_hide(ch, hide)


def apply_frame_state(frame: int, handles: dict):
    t = (frame - 1) / float(TOTAL_FRAMES)
    two_pi_t = 2.0 * math.pi * t
    stepped_f = ((frame - 1) // 2) * 2 + 1
    t2 = (stepped_f - 1) / float(TOTAL_FRAMES)

    # 1. POV Handheld Camera + Beat 2-3 backward tremble + f204 door-slam shock jolt
    cam = handles["cam"]
    back_drift = 0.0
    if 111 <= frame <= 288:
        back_drift = -0.17 * smoothstep((frame - 111) / 160.0)
    jolt_x, jolt_z, jolt_roll = 0.0, 0.0, 0.0
    if 203 <= frame <= 216:
        df = float(frame - 203)
        env = math.exp(-df / 2.8) * math.sin(df * 2.2)
        jolt_z = 0.022 * env
        jolt_x = 0.012 * math.exp(-df / 2.8) * math.cos(df * 2.4)
        jolt_roll = 0.75 * env

    # Subtle handheld PSX breathing/sway + Beat 3 trembling POV shudder
    shudder = 0.005 * math.sin(frame * 2.1) if frame >= 204 else 0.0
    sway_x = 0.018 * math.sin(two_pi_t * 2.0) + 0.006 * math.cos(two_pi_t * 5.0) + shudder
    sway_z = 0.014 * math.sin(two_pi_t * 3.0 + 0.6) + 0.004 * math.cos(frame * 2.6) * (1.0 if frame >= 204 else 0.0)
    cam.location = (-0.10 + sway_x + jolt_x, -1.25 + back_drift, 1.45 + sway_z + jolt_z)
    cam.rotation_euler = (math.radians(91.0 + 0.35 * math.sin(two_pi_t * 2.0)), math.radians(jolt_roll + 0.25 * math.sin(two_pi_t)), math.radians(-1.2 + 0.3 * math.cos(two_pi_t * 2.0)))

    # 2. Left Door Creak Wide Open (-30 deg, f122-f200) -> Slam Shut (f200-f204) & Door-Crack Lurker
    door = handles["door"]
    lurker = handles["lurker"]
    if frame < 122 or frame > 204:
        door_deg = 0.0
    elif frame <= 175:
        door_deg = 30.0 * smoothstep((frame - 122) / 48.0)
    elif frame <= 199:
        door_deg = 30.0
    else:
        door_deg = 30.0 * (1.0 - smoothstep((frame - 199) / 5.0))
    door.rotation_euler = (0.0, 0.0, math.radians(-door_deg))

    # Lurker emerges cleanly ONLY while door is cracked, retracts fully by f197 BEFORE slam at f200!
    if frame < 130 or frame > 197:
        _set_tree_hide(lurker, True)
        lurker.location = (-1.30, 1.42, 0.0)
    else:
        _set_tree_hide(lurker, False)
        if frame <= 152:
            ul = smoothstep((frame - 130) / 22.0)
        elif frame <= 180:
            ul = 1.0
        else:
            ul = 1.0 - smoothstep((frame - 180) / 17.0)
        lurker.location = (-1.28 * (1.0 - ul) + (-0.95) * ul, 1.42, 0.0)

    # 3. Distant Corridor Flicker Reveal (f091-f096) + Beat 3 Distant Watcher Eyes Surge (f228-f288)
    back_pt = handles["back_pt"]
    flicker_map = {91: 48.0, 92: 14.0, 93: 82.0, 94: 18.0, 95: 62.0, 96: 12.0}
    back_e = flicker_map.get(frame, 0.0)
    back_pt.data.energy = back_e
    for hs in handles["shadows"]:
        _set_tree_hide(hs, back_e <= 0.5)
    df_amt = 0.15 if back_e > 0.5 else 1.0
    for dfn in handles["depth_fade_nodes"]:
        dfn.outputs[0].default_value = df_amt

    bw_roots, bw_emit = handles["back_watchers"]
    if frame < 228:
        for br in bw_roots:
            _set_tree_hide(br, True)
        bw_emit.inputs["Strength"].default_value = 0.0
    else:
        bw_u = smoothstep((frame - 228) / 18.0)
        for br in bw_roots:
            _set_tree_hide(br, False)
        bw_emit.inputs["Strength"].default_value = 0.95 * bw_u

    # 4. Towering Star-Eye Seraph + Blood-Crimson Escalation (f202-f288)
    sr = handles["seraph"]
    s_root = sr["root"]
    s_head = sr["head_piv"]

    if frame <= 110:
        y_ser = 3.45
    elif frame <= 199:
        y_ser = 3.45 - 0.45 * smoothstep((frame - 110) / 89.0)  # 3.45 -> 3.00
    else:
        y_ser = 3.00 - 0.80 * smoothstep((frame - 199) / 89.0)  # 3.00 -> 2.20 closer loom!
    hover_z = 0.012 * math.sin(two_pi_t * 3.0)
    s_root.location = (0.18, y_ser, hover_z)

    # Beat 3 crimson & bloom shift (f202-f218)
    b3 = 0.0 if frame < 202 else smoothstep((frame - 202) / 16.0)
    white_col = Vector((lin(1.0), lin(0.968), lin(0.875)))
    red_col = Vector((lin(1.0), lin(0.08), lin(0.05)))
    cur_c = white_col.lerp(red_col, b3)
    sr["tint_node"].default_value = (cur_c.x, cur_c.y, cur_c.z, 1.0)
    sr["emit_node"].default_value = 6.2 + 2.4 * b3

    star_pt = handles["star_pt"]
    star_pt.data.color = (1.0, 0.94 * (1.0 - b3) + 0.06 * b3, 0.78 * (1.0 - b3) + 0.04 * b3)
    star_pt.data.energy = 140.0 + 60.0 * b3

    # Subtle head tilt & Beat 2+3 creeping star rotation
    head_roll = 4.0 * math.sin(two_pi_t * 2.0) + (14.0 * smoothstep((frame - 111) / 88.0) if frame >= 111 else 0.0)
    s_head.rotation_euler = (0.0, math.radians(head_roll), 0.0)

    # 6 Star petals flare wider forward in Beat 3
    flare_deg = 8.0 + 18.0 * b3
    for pobj in sr["petals"]:
        pobj.rotation_euler = (math.radians(flare_deg), 0.0, 0.0)

    # Central eyeball tracks slightly toward camera + pupil-lock Beat 3 zoom + wide-open lids
    sr["main_eye"].location = (0.0, -0.056 - 0.012 * b3, 0.0)
    sr["main_eye"].scale = (1.0 + 0.08 * b3, 1.0, 1.0 + 0.08 * b3)
    sr["main_eye"].rotation_euler = (math.radians(3.0 * math.sin(two_pi_t * 3.0)), 0.0, math.radians(-8.0 + 3.0 * math.cos(two_pi_t * 2.0)))
    blink = 1.0 if frame in (79, 80, 81) else (0.5 if frame in (78, 82) else 0.0)
    widen = b3
    sr["main_ul"].rotation_euler = (math.radians(42.0 * blink - 26.0 * widen), 0.0, 0.0)
    sr["main_ll"].rotation_euler = (math.radians(-32.0 * blink + 18.0 * widen), 0.0, 0.0)

    # 6 Hidden Secondary Calyx Eyes: SEALED SHUT during Beats 1-2, SNAP OPEN in Beat 3 (f205-f222)!
    mini_open = 0.0 if frame < 205 else smoothstep((frame - 205) / 16.0)
    for mpiv, m_ul, m_ll in sr["mini_eyes"]:
        _set_tree_hide(mpiv, mini_open <= 0.02)
        m_ul.rotation_euler = (math.radians(52.0 * (1.0 - mini_open) - 16.0 * mini_open), 0.0, 0.0)
        m_ll.rotation_euler = (math.radians(-42.0 * (1.0 - mini_open) + 12.0 * mini_open), 0.0, 0.0)

    # 2 Unfolding Gaunt Shadow-Arms (tucked invisible until f204, unfold wide across hallway f204-f274!)
    arm_u = 0.0 if frame < 204 else smoothstep((frame - 204) / 65.0)
    for apiv, s_sign in sr["arms"]:
        _set_tree_hide(apiv, arm_u <= 0.02)
        apiv.scale = (0.15 + 0.85 * arm_u, 0.15 + 0.85 * arm_u, 0.15 + 0.85 * arm_u)
        apiv.rotation_euler = (0.0, math.radians(s_sign * (42.0 * (1.0 - arm_u))), math.radians(-s_sign * 14.0 * arm_u))

    bpy.context.view_layer.update()


def configure_render(res_scale: float):
    """Render native PSX 270x480 (1/4 of 1080x1920) so Nearest-Neighbor upscale delivers real PS1 pixels."""
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = 48
    sc.eevee.shadow_resolution_scale = 1.0
    sc.eevee.shadow_ray_count = 2
    sc.eevee.shadow_step_count = 8
    sc.render.resolution_x = int(round(270 * res_scale))
    sc.render.resolution_y = int(round(480 * res_scale))
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0


def write_crop_meta(probe: bool, handles: dict):
    """Write crop coordinates at final 1080x1920 composited output scale."""
    sc = bpy.context.scene
    cam = handles["cam"]
    W, H = 1080, 1920

    def proj_box(world_pt: Vector, bw: int, bh: int):
        co = world_to_camera_view(sc, cam, world_pt)
        px = co.x * W
        py = (1.0 - co.y) * H
        x0 = max(0, min(W - bw, int(round(px - bw / 2))))
        y0 = max(0, min(H - bh, int(round(py - bh / 2))))
        return [x0, y0, min(bw, W - x0), min(bh, H - y0)]

    f_map = {f: str(i + 1) for i, f in enumerate(PROBE_FRAMES)} if probe else {k: str(k) for k in PROBE_FRAMES}

    apply_frame_state(245, handles)
    seraph_head_pt = handles["seraph"]["head_piv"].matrix_world.translation.copy()
    door_pt = Vector((-0.90, 1.48, 1.38))
    hall_pt = Vector((0.0, 5.2, 1.35))
    text_pt = Vector((0.0, 1.8, 0.15))

    apply_frame_state(93, handles)
    seraph_pt_1 = handles["seraph"]["head_piv"].matrix_world.translation.copy()

    crops = {
        "seraph_head": {f_map[1]: proj_box(seraph_pt_1, 460, 460), f_map[245]: proj_box(seraph_head_pt, 540, 540)},
        "door_lurker": {f_map[145]: proj_box(door_pt, 380, 680), f_map[175]: proj_box(door_pt, 380, 680), f_map[206]: proj_box(door_pt, 380, 680)},
        "hall_flicker": {f_map[93]: proj_box(hall_pt, 420, 620)},
        "text_safe": {f_map[45]: [140, 1460, 800, 320], f_map[245]: [140, 1460, 800, 320]},
    }
    tag = "probe_crops_meta.json" if probe else "full_crops_meta.json"
    (ROOT / "assets" / tag).write_text(json.dumps({"crops": crops}, indent=2), encoding="utf-8")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    door, depth_fade_nodes = build_hallway()
    lurker = build_door_lurker()
    seraph = build_seraph_entity()
    shadows, back_watchers = build_hall_shadows()
    cam, star_pt, back_pt = setup_lighting_and_camera(seraph["head_piv"])

    handles = {
        "cam": cam,
        "door": door,
        "depth_fade_nodes": depth_fade_nodes,
        "lurker": lurker,
        "seraph": seraph,
        "shadows": shadows,
        "back_watchers": back_watchers,
        "star_pt": star_pt,
        "back_pt": back_pt,
    }

    configure_render(args.scale)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_crop_meta(args.probe, handles)

    frames = PROBE_FRAMES if args.probe else list(range(1, TOTAL_FRAMES + 1))
    for f in frames:
        apply_frame_state(f, handles)
        bpy.context.scene.frame_set(f)
        bpy.context.scene.render.filepath = str(out_dir / f"f_{f:04d}.png")
        bpy.ops.render.render(write_still=True)

    print(f"Rendered {len(frames)} PSX frames ({bpy.context.scene.render.resolution_x}x{bpy.context.scene.render.resolution_y}) to {out_dir}")


if __name__ == "__main__":
    main()
