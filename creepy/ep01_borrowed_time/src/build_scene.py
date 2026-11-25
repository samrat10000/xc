import argparse
import json
import math
import sys
from pathlib import Path
import bmesh
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Euler, Matrix, Quaternion, Vector

ROOT = Path(r"c:\Users\cross\Downloads\xc\creepy\ep01_borrowed_time")
ASSETS = ROOT / "assets"
KID_GIRL_BLEND = r"C:\Users\cross\Downloads\xc\5oclock-ep1-the-fourth-note_2026-11-23\assets\cast_v2\kid_girl.blend"
SAM_BLEND = r"C:\Users\cross\Downloads\xc\5oclock-ep1-the-fourth-note_2026-11-23\assets\toon_sam\sam_toon.blend"

TOTAL_FRAMES = 216
FPS = 24
PROBE_FRAMES = [1, 56, 86, 108, 118, 154, 182, 216]


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


def make_mat_image(name: str, img_path: Path, emission_strength: float = 0.0, roughness: float = 0.85, diffuse_weight: float = 1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(img_path))
    if diffuse_weight <= 0.01 and emission_strength > 0.0:
        # Pure clean emissive surface (zero EEVEE shadow-noise speckles on glowing dials!)
        emit = nt.nodes.new("ShaderNodeEmission")
        emit.inputs["Strength"].default_value = emission_strength
        nt.links.new(tex.outputs["Color"], emit.inputs["Color"])
        nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    else:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Roughness"].default_value = roughness
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        if emission_strength > 0.0:
            nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
            bsdf.inputs["Emission Strength"].default_value = emission_strength
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_mat_solid(name: str, rgba, roughness: float = 0.75, emission_rgba=None, emission_strength: float = 0.0, pure_emission: bool = False):
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
        if emission_rgba is not None and emission_strength > 0.0:
            bsdf.inputs["Emission Color"].default_value = emission_rgba
            bsdf.inputs["Emission Strength"].default_value = emission_strength
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_silhouette_rim_mat(name: str, rim_rgba, rim_power: float = 0.56, rim_strength: float = 1.65, wet_specular: bool = False, wet_roughness: float = 0.45):
    """Deep void-black silhouette with crisp crimson backlit rim on edges facing the clock (+Y/+Z)."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")

    if wet_specular:
        dark_bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        dark_bsdf.inputs["Base Color"].default_value = (0.005, 0.002, 0.002, 1.0)
        dark_bsdf.inputs["Roughness"].default_value = wet_roughness
        dark_bsdf.inputs["IOR"].default_value = 1.48
        dark_out = dark_bsdf.outputs["BSDF"]
    else:
        dark_bsdf = nt.nodes.new("ShaderNodeEmission")
        dark_bsdf.inputs["Color"].default_value = (0.0015, 0.0008, 0.001, 1.0)
        dark_bsdf.inputs["Strength"].default_value = 1.0
        dark_out = dark_bsdf.outputs["Emission"]

    rim_emit = nt.nodes.new("ShaderNodeEmission")
    rim_emit.inputs["Color"].default_value = rim_rgba
    rim_emit.inputs["Strength"].default_value = rim_strength

    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.32

    geom = nt.nodes.new("ShaderNodeNewGeometry")
    dot = nt.nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = (0.0, 0.60, 0.80)

    ramp_lw = nt.nodes.new("ShaderNodeValToRGB")
    ramp_lw.color_ramp.elements[0].position = rim_power
    ramp_lw.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp_lw.color_ramp.elements[1].position = min(0.95, rim_power + 0.16)
    ramp_lw.color_ramp.elements[1].color = (1, 1, 1, 1)

    ramp_dir = nt.nodes.new("ShaderNodeValToRGB")
    ramp_dir.color_ramp.elements[0].position = 0.12
    ramp_dir.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp_dir.color_ramp.elements[1].position = 0.50
    ramp_dir.color_ramp.elements[1].color = (1, 1, 1, 1)

    mult = nt.nodes.new("ShaderNodeMath")
    mult.operation = "MULTIPLY"

    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lw.outputs["Facing"], ramp_lw.inputs["Fac"])
    nt.links.new(geom.outputs["Normal"], dot.inputs[0])
    nt.links.new(dot.outputs["Value"], ramp_dir.inputs["Fac"])
    nt.links.new(ramp_lw.outputs["Color"], mult.inputs[0])
    nt.links.new(ramp_dir.outputs["Color"], mult.inputs[1])
    nt.links.new(mult.outputs["Value"], mix.inputs["Fac"])
    nt.links.new(dark_out, mix.inputs[1])
    nt.links.new(rim_emit.outputs["Emission"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return mat


def add_box(name: str, loc, size, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    return obj


def add_uv_plane(name: str, loc, width: float, height: float, mat, rot=(math.radians(90), 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (width, height, 1.0)
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    return obj


def add_upright_disk_uv(name: str, loc, radius: float, mat, tilt_deg: float = 0.0, scale_xy=(1.0, 1.0)):
    """Create a thin disk facing -Y with upright [0,1]x[0,1] UVs so top of image = +Z."""
    bpy.ops.mesh.primitive_circle_add(vertices=48, radius=radius, fill_type="NGON", location=loc)
    obj = bpy.context.active_object
    obj.name = name
    # Rotate +90 deg about X so local +Y becomes world +Z and disk normal faces -Y
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (math.radians(90.0), math.radians(tilt_deg), 0.0)
    obj.scale = (scale_xy[0], scale_xy[1], 1.0)

    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()
    for f in bm.faces:
        for l in f.loops:
            co = l.vert.co  # local XY before rotation: +X is right, +Y is top (+Z after 90 X rot)
            u = (co.x / (2.0 * radius)) + 0.5
            v = (co.y / (2.0 * radius)) + 0.5
            l[uv_layer].uv = (u, v)
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.data.materials.append(mat)
    return obj


def make_crimson_wood_mat(name: str):
    """Procedural dark crimson-stained gothic wood grain material."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.48
    bsdf.inputs["Emission Color"].default_value = hex_lin("#300202")
    bsdf.inputs["Emission Strength"].default_value = 0.12

    geom = nt.nodes.new("ShaderNodeNewGeometry")
    mapping = nt.nodes.new("ShaderNodeMapping")
    # High X/Y scale, low Z scale -> long vertical wood grain on upright jambs
    mapping.inputs["Scale"].default_value = (28.0, 28.0, 2.0)

    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3.5
    noise.inputs["Detail"].default_value = 8.0
    noise.inputs["Roughness"].default_value = 0.65

    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.30
    ramp.color_ramp.elements[0].color = hex_lin("#3A0404")
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = hex_lin("#7D0909")

    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.14
    bump.inputs["Distance"].default_value = 0.01

    nt.links.new(geom.outputs["Position"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_hall_fog_mat(name: str):
    """Smooth radial+vertical procedural mist gradient fading seamlessly to pitch black at all plane edges."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")

    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")

    # Vertical offset: (Y - 0.48) * 3.8
    y_sub = nt.nodes.new("ShaderNodeMath")
    y_sub.operation = "SUBTRACT"
    y_sub.inputs[1].default_value = 0.48
    y_mul = nt.nodes.new("ShaderNodeMath")
    y_mul.operation = "MULTIPLY"
    y_mul.inputs[1].default_value = 3.8
    y_sq = nt.nodes.new("ShaderNodeMath")
    y_sq.operation = "MULTIPLY"

    # Horizontal offset: (X - 0.50) * 3.0
    x_sub = nt.nodes.new("ShaderNodeMath")
    x_sub.operation = "SUBTRACT"
    x_sub.inputs[1].default_value = 0.50
    x_mul = nt.nodes.new("ShaderNodeMath")
    x_mul.operation = "MULTIPLY"
    x_mul.inputs[1].default_value = 3.0
    x_sq = nt.nodes.new("ShaderNodeMath")
    x_sq.operation = "MULTIPLY"

    sum_d2 = nt.nodes.new("ShaderNodeMath")
    sum_d2.operation = "ADD"
    neg_d2 = nt.nodes.new("ShaderNodeMath")
    neg_d2.operation = "MULTIPLY"
    neg_d2.inputs[1].default_value = -1.0
    gauss = nt.nodes.new("ShaderNodeMath")
    gauss.operation = "EXPONENT"

    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.clamp_factor = True
    mix.inputs[6].default_value = (0.001, 0.001, 0.002, 1.0)
    mix.inputs[7].default_value = hex_lin("#222836")

    emit = nt.nodes.new("ShaderNodeEmission")
    emit.inputs["Strength"].default_value = 0.28

    nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["Y"], y_sub.inputs[0])
    nt.links.new(y_sub.outputs["Value"], y_mul.inputs[0])
    nt.links.new(y_mul.outputs["Value"], y_sq.inputs[0])
    nt.links.new(y_mul.outputs["Value"], y_sq.inputs[1])

    nt.links.new(sep.outputs["X"], x_sub.inputs[0])
    nt.links.new(x_sub.outputs["Value"], x_mul.inputs[0])
    nt.links.new(x_mul.outputs["Value"], x_sq.inputs[0])
    nt.links.new(x_mul.outputs["Value"], x_sq.inputs[1])

    nt.links.new(x_sq.outputs["Value"], sum_d2.inputs[0])
    nt.links.new(y_sq.outputs["Value"], sum_d2.inputs[1])
    nt.links.new(sum_d2.outputs["Value"], neg_d2.inputs[0])
    nt.links.new(neg_d2.outputs["Value"], gauss.inputs[0])
    nt.links.new(gauss.outputs["Value"], mix.inputs["Factor"])
    nt.links.new(mix.outputs[2], emit.inputs["Color"])
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    return mat


def build_room():
    wall_mat = make_mat_image("Wall_Charcoal", ASSETS / "wall_charcoal.png", emission_strength=0.015, roughness=0.92)
    floor_mat = make_mat_image("Floor_Wood", ASSETS / "floor_wood.png", emission_strength=0.0, roughness=0.72)
    door_red = make_crimson_wood_mat("Door_Crimson_Wood")
    void_dark = make_mat_solid("Hallway_Void", (0.002, 0.002, 0.003, 1.0), roughness=0.95)
    trim_dark = make_mat_solid("Trim_Charcoal", hex_lin("#121012"), roughness=0.80)

    # Doorway opening: x in [-1.06, -0.46], z in [0.0, 2.34]
    # Right main wall: x in [-0.46, +2.60], z in [0.0, 4.0]
    add_uv_plane("Wall_Right", (1.07, 0.0, 2.0), 3.06, 4.0, wall_mat)
    # Upper header above doorway: x in [-1.06, -0.46], z in [2.34, 4.0]
    add_uv_plane("Wall_Header", (-0.76, 0.0, 3.17), 0.60, 1.66, wall_mat)
    # Left wall beside doorway: x in [-2.60, -1.06], z in [0.0, 4.0]
    add_uv_plane("Wall_Left", (-1.83, 0.0, 2.0), 1.54, 4.0, wall_mat)

    # Floor
    add_uv_plane("Floor_Main", (0.0, -1.8, 0.0), 5.6, 5.2, floor_mat, rot=(0.0, 0.0, 0.0))

    # Baseboard along right wall
    add_box("Baseboard_Right", (1.07, -0.018, 0.055), (3.06, 0.036, 0.11), trim_dark)

    # Real recessed 2.4m dark hallway strictly behind y = +0.06 (never poking in front of back wall!)
    add_box("Hall_Wall_Back", (-1.10, 2.55, 1.35), (2.40, 0.10, 3.20), void_dark)
    add_box("Hall_Wall_Right", (-0.42, 1.28, 1.35), (0.06, 2.40, 2.70), trim_dark)
    add_box("Hall_Wall_Left", (-2.15, 1.28, 1.35), (0.06, 2.40, 3.20), void_dark)
    add_box("Hall_Floor", (-1.10, 1.28, -0.01), (2.20, 2.40, 0.02), void_dark)
    add_box("Hall_Ceil", (-1.10, 1.28, 2.45), (2.20, 2.40, 0.06), void_dark)

    # Tall full-coverage hallway mist plane with smooth radial gradient fading to zero at all edges
    hall_fog_mat = make_hall_fog_mat("Hall_Fog")
    add_uv_plane("Hall_Interior_Glow", (-1.10, 2.25, 1.30), 2.40, 3.20, hall_fog_mat)

    # Crimson-lacquered wooden doorframe jamb & casing (front face at y = -0.055)
    add_box("Doorframe_Right_Jamb", (-0.45, -0.018, 1.17), (0.055, 0.075, 2.34), door_red)
    add_box("Doorframe_Left_Jamb", (-1.07, -0.018, 1.17), (0.055, 0.075, 2.34), door_red)
    add_box("Doorframe_Top", (-0.76, -0.018, 2.35), (0.675, 0.075, 0.055), door_red)

    # Metallic hinge knuckles on inside jamb
    hinge_mat = make_mat_solid("Iron_Hinge", hex_lin("#1D191B"), roughness=0.35)
    for hz in (0.45, 1.18, 1.90):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.010, depth=0.065, location=(-0.48, -0.025, hz))
        h = bpy.context.active_object
        h.name = f"Hinge_{hz}"
        h.data.materials.append(hinge_mat)

    # Right side table + props (moved cleanly into visible right third: x ~ 0.62)
    wood_dark = make_mat_solid("Table_Wood", hex_lin("#1D1618"), roughness=0.72)
    add_box("Table_Top", (0.65, -0.26, 0.72), (0.48, 0.34, 0.035), wood_dark)
    for lx, ly in ((0.44, -0.12), (0.86, -0.12), (0.44, -0.40), (0.86, -0.40)):
        add_box(f"Table_Leg_{lx}_{ly}", (lx, ly, 0.36), (0.035, 0.035, 0.72), wood_dark)

    bottle_mat = make_mat_solid("Glass_Bottle", hex_lin("#1A2633"), roughness=0.18)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.036, depth=0.19, location=(0.54, -0.22, 0.83))
    b = bpy.context.active_object
    b.name = "Table_Bottle"
    b.data.materials.append(bottle_mat)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.014, depth=0.06, location=(0.54, -0.22, 0.955))
    bn = bpy.context.active_object
    bn.name = "Table_Bottle_Neck"
    bn.data.materials.append(bottle_mat)

    bowl_mat = make_mat_solid("Bowl_Red", hex_lin("#7A0A0A"), roughness=0.35)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, location=(0.72, -0.27, 0.775))
    bw = bpy.context.active_object
    bw.name = "Table_Bowl"
    bw.scale = (1.0, 1.0, 0.45)
    bw.data.materials.append(bowl_mat)

    brass_mat = make_mat_solid("Brass_Old", hex_lin("#6E542B"), roughness=0.35)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.028, depth=0.012, location=(0.60, -0.34, 0.743))
    pw = bpy.context.active_object
    pw.name = "Table_PocketWatch"
    pw.data.materials.append(brass_mat)


def build_giant_clock():
    cx, cy, cz = 0.08, -0.024, 2.22
    rad = 0.43

    # Pure emissive dial (no shadow-speckle noise, razor-sharp Roman numerals!)
    dial_mat = make_mat_image("Clock_Main_Dial", ASSETS / "clock_main_dial.png", emission_strength=1.45, diffuse_weight=0.0)
    dial_emit = [n for n in dial_mat.node_tree.nodes if n.type == "EMISSION"][0]
    bezel_mat = make_mat_solid("Clock_Iron_Bezel", hex_lin("#190404"), roughness=0.40)
    hand_mat = make_mat_solid("Clock_Iron_Hands", (0.002, 0.001, 0.001, 1.0), roughness=0.35, emission_rgba=(0.002, 0.001, 0.001, 1.0), emission_strength=1.0, pure_emission=True)

    # Upright UV disk facing -Y
    add_upright_disk_uv("MainClock_Dial", (cx, cy, cz), rad, dial_mat)

    # 3D carved bezel torus surrounding dial
    bpy.ops.mesh.primitive_torus_add(
        major_radius=rad + 0.015,
        minor_radius=0.028,
        major_segments=64,
        minor_segments=16,
        location=(cx, cy - 0.010, cz),
        rotation=(math.radians(90), 0, 0),
    )
    bez = bpy.context.active_object
    bez.name = "MainClock_Bezel"
    bez.data.materials.append(bezel_mat)

    # Ornate 3D gothic lance/spade hands cleanly in front of dial (y = -0.040..-0.056)
    def make_gothic_hand(hname: str, length: float, width: float, y_pos: float, is_second: bool = False):
        me = bpy.data.meshes.new(hname)
        bm = bmesh.new()
        w = width
        if is_second:
            profile = [
                (-length * 0.22, -w * 0.70),
                (-length * 0.22, +w * 0.70),
                (length * 0.05, +w * 0.55),
                (length * 0.86, +w * 0.25),
                (length * 0.90, 0.0),
                (length * 0.86, -w * 0.25),
                (length * 0.05, -w * 0.55),
            ]
        else:
            profile = [
                (-length * 0.22, -w * 0.48),
                (-length * 0.14, -w * 0.75),
                (0.0, -w * 0.72),
                (length * 0.56, -w * 0.34),
                (length * 0.67, -w * 1.15),
                (length * 0.88, 0.0),
                (length * 0.67, +w * 1.15),
                (length * 0.56, +w * 0.34),
                (0.0, +w * 0.72),
                (-length * 0.14, +w * 0.75),
                (-length * 0.22, +w * 0.48),
            ]
        front_verts = [bm.verts.new((px, -0.0045, pz)) for (pz, px) in profile]
        back_verts = [bm.verts.new((px, +0.0045, pz)) for (pz, px) in profile]
        bm.faces.new(front_verts)
        bm.faces.new(list(reversed(back_verts)))
        n_v = len(profile)
        for i in range(n_v):
            ni = (i + 1) % n_v
            bm.faces.new([front_verts[i], front_verts[ni], back_verts[ni], back_verts[i]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me)
        bm.free()

        obj = bpy.data.objects.new(hname, me)
        bpy.context.collection.objects.link(obj)
        obj.location = (cx, y_pos, cz)
        obj.rotation_mode = "XYZ"
        obj.data.materials.append(hand_mat)
        return obj

    hour_h = make_gothic_hand("MainClock_HourHand", 0.24, 0.015, cy - 0.016, is_second=False)
    min_h = make_gothic_hand("MainClock_MinuteHand", 0.35, 0.011, cy - 0.023, is_second=False)
    sec_h = make_gothic_hand("MainClock_SecondHand", 0.37, 0.005, cy - 0.030, is_second=True)

    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.028, depth=0.028, location=(cx, cy - 0.024, cz), rotation=(math.radians(90), 0, 0))
    cap = bpy.context.active_object
    cap.name = "MainClock_CenterCap"
    cap.data.materials.append(hand_mat)

    return hour_h, min_h, sec_h, dial_emit


def build_word_clocks():
    frame_mat = make_mat_solid("SmallClock_Frame", hex_lin("#580707"), roughness=0.55)
    hand_mat = make_mat_solid("SmallClock_Hand", (0.002, 0.001, 0.001, 1.0), roughness=0.45, emission_rgba=(0.002, 0.001, 0.001, 1.0), emission_strength=1.0, pure_emission=True)

    # All 10 word-clocks placed cleanly inside visible x in [-0.36, +0.76], z in [1.05, 2.86], clear of doorway & main clock!
    specs = [
        ("LOST", -0.30, 2.78, 0.110, "round", 8.0, (1.0, 1.0)),
        ("FADE", -0.28, 1.62, 0.100, "round", -10.0, (1.0, 1.0)),
        ("WAIT", 0.65, 2.52, 0.100, "square", -6.0, (1.0, 1.0)),
        ("EMPTY", 0.64, 2.06, 0.110, "oval", 3.0, (0.78, 1.18)),
        ("STILL", 0.74, 2.84, 0.085, "square", 5.0, (1.0, 1.0)),
        ("ALONE", 0.56, 1.54, 0.092, "square", 45.0, (1.0, 1.0)),
        ("LATE", 0.80, 1.54, 0.108, "round", -4.0, (1.0, 1.0)),
        ("OFF", 0.50, 1.05, 0.075, "square", 4.0, (1.0, 1.0)),
        ("HUSH", -0.28, 1.24, 0.088, "round", 11.0, (1.0, 1.0)),
        ("STAY", 0.34, 2.82, 0.082, "square", -7.0, (1.0, 1.0)),
    ]

    created = {}
    for word, x, z, r, shape, tilt_deg, (sx, sz) in specs:
        mat = make_mat_image(f"Dial_{word}", ASSETS / "clocks" / f"clock_{word}.png", emission_strength=0.13, roughness=0.65)
        if word == "ALONE":
            nt = mat.node_tree
            bsdf = [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"][0]
            tex_orig = [n for n in nt.nodes if n.type == "TEX_IMAGE"][0]
            tex_alt = nt.nodes.new("ShaderNodeTexImage")
            tex_alt.image = bpy.data.images.load(str(ASSETS / "clocks" / "clock_DONT_TURN.png"))
            mix_rgb = nt.nodes.new("ShaderNodeMix")
            mix_rgb.data_type = "RGBA"
            mix_rgb.inputs["Factor"].default_value = 0.0
            nt.links.new(tex_orig.outputs["Color"], mix_rgb.inputs[6])
            nt.links.new(tex_alt.outputs["Color"], mix_rgb.inputs[7])
            nt.links.new(mix_rgb.outputs[2], bsdf.inputs["Base Color"])
            nt.links.new(mix_rgb.outputs[2], bsdf.inputs["Emission Color"])
            created["ALONE_MIX"] = mix_rgb
            created["ALONE_BSDF"] = bsdf

        if shape in ("round", "oval"):
            # Dial cleanly in front of deeper 3D backing frame!
            add_upright_disk_uv(f"WordClock_{word}", (x, -0.026, z), r, mat, tilt_deg=tilt_deg, scale_xy=(sx, sz))
            bpy.ops.mesh.primitive_torus_add(
                major_radius=r + 0.006, minor_radius=0.014, major_segments=36, minor_segments=10,
                location=(x, -0.018, z), rotation=(math.radians(90), math.radians(tilt_deg), 0)
            )
            fr = bpy.context.active_object
            fr.name = f"WordClockFrame_{word}"
            fr.scale = (sx, sz, 1.0)
            fr.data.materials.append(frame_mat)
        else:
            # Square/diamond dial plane at y = -0.026; deeper 3D backing box strictly behind at y = -0.014 (front at y = -0.025)!
            add_uv_plane(f"WordClock_{word}", (x, -0.026, z), r * 2.0, r * 2.0, mat, rot=(math.radians(90), math.radians(tilt_deg), 0))
            add_box(f"WordClockFrame_{word}", (x, -0.014, z), (r * 2.06, 0.022, r * 2.06), frame_mat, rot=(0, math.radians(tilt_deg), 0))

        hands = []
        for idx_h, hl in enumerate((r * 0.42, r * 0.28)):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, hl * 0.45))
            ho = bpy.context.active_object
            ho.name = f"WordClock_{word}_Hand{idx_h}"
            ho.scale = (0.0038, 0.003, hl)
            bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
            ho.location = (x, -0.032 - idx_h * 0.003, z)
            ho.rotation_mode = "XYZ"
            ho.data.materials.append(hand_mat)
            hands.append(ho)
        created[word] = hands

    # Loose clock hands mounted directly on wall near side table
    loose_hands = []
    for idx_h, hl in enumerate((0.065, 0.045)):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, hl * 0.45))
        ho = bpy.context.active_object
        ho.name = f"LooseWallHand_{idx_h}"
        ho.scale = (0.006, 0.005, hl)
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
        ho.location = (0.36, -0.024 - idx_h * 0.003, 1.24)
        ho.rotation_mode = "XYZ"
        ho.data.materials.append(hand_mat)
        loose_hands.append(ho)
    created["LOOSE"] = loose_hands
    return created


def _rot_arm(rig, name: str, axis, deg: float):
    pb = rig.pose.bones[name]
    bpy.context.view_layer.update()
    R = Matrix.Rotation(math.radians(deg), 4, Vector(axis))
    pb.matrix = Matrix.Translation(pb.head) @ R @ Matrix.Translation(-pb.head) @ pb.matrix
    bpy.context.view_layer.update()


def build_girl_silhouette():
    with bpy.data.libraries.load(KID_GIRL_BLEND, link=False) as (src, dst):
        dst.objects = list(src.objects)
    rig = None
    girl_meshes = []
    for o in dst.objects:
        if o is None or o.type in ("LIGHT", "CAMERA"):
            continue
        if o.name in ("Kid_girl_yellow_cap", "Kid_girl_randoseru"):
            bpy.data.objects.remove(o, do_unlink=True)
            continue
        bpy.context.collection.objects.link(o)
        if o.type == "ARMATURE":
            rig = o
        elif o.type == "MESH":
            girl_meshes.append(o)

    girl_mat = make_silhouette_rim_mat("Girl_Silhouette_CrimsonRim", hex_lin("#E81010"), rim_power=0.58, rim_strength=1.55)
    for m in girl_meshes:
        m.data.materials.clear()
        m.data.materials.append(girl_mat)

    rig.rotation_mode = "XYZ"
    rig.rotation_euler = (0.0, 0.0, math.radians(184.0))
    rig.location = (0.06, -1.48, 0.0)
    rig.data.pose_position = "POSE"
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    bpy.context.view_layer.update()

    # Ground feet cleanly to z = 0.0
    min_z = min((m.matrix_world @ v.co).z for m in girl_meshes for v in m.data.vertices)
    rig.location.z -= min_z
    bpy.context.view_layer.update()

    # Natural relaxed standing pose: drop arms 79 deg from T-pose (hanging comfortably ~11 deg from sides!),
    # slight elbow bend 16 deg, gentle finger curl, subtle head pitch up toward the giant clock
    _rot_arm(rig, "J_Bip_L_UpperArm", (0, 1, 0), 79.0)
    _rot_arm(rig, "J_Bip_R_UpperArm", (0, 1, 0), -79.0)
    _rot_arm(rig, "J_Bip_L_UpperArm", (1, 0, 0), -4.0)
    _rot_arm(rig, "J_Bip_R_UpperArm", (1, 0, 0), -4.0)
    _rot_arm(rig, "J_Bip_L_LowerArm", (1, 0, 0), 16.0)
    _rot_arm(rig, "J_Bip_R_LowerArm", (1, 0, 0), 16.0)
    _rot_arm(rig, "J_Bip_C_Neck", (1, 0, 0), -6.0)
    _rot_arm(rig, "J_Bip_C_Head", (1, 0, 0), -8.0)

    base_quats = {
        "J_Bip_C_Chest": rig.pose.bones["J_Bip_C_Chest"].rotation_quaternion.copy(),
        "J_Bip_C_UpperChest": rig.pose.bones["J_Bip_C_UpperChest"].rotation_quaternion.copy(),
        "J_Bip_C_Head": rig.pose.bones["J_Bip_C_Head"].rotation_quaternion.copy(),
        "J_Bip_L_Shoulder": rig.pose.bones["J_Bip_L_Shoulder"].rotation_quaternion.copy(),
        "J_Bip_R_Shoulder": rig.pose.bones["J_Bip_R_Shoulder"].rotation_quaternion.copy(),
    }
    hair_bones = [pb for pb in rig.pose.bones if pb.name.startswith("HairJoint-") and pb.parent and pb.parent.name == "J_Bip_C_Head"]
    for hb in hair_bones:
        base_quats[hb.name] = hb.rotation_quaternion.copy()
    skirt_bones = [pb for pb in rig.pose.bones if "Skirt" in pb.name and not pb.name.endswith("_end")]
    for sb in skirt_bones:
        base_quats[sb.name] = sb.rotation_quaternion.copy()

    return rig, girl_meshes, base_quats, hair_bones, skirt_bones


def _make_stalker_torso(stalker_mat):
    """Sculpt tall (~1.95m) emaciated humanoid shadow coat with broad hunched shoulders & sharp shoulder shelf."""
    me = bpy.data.meshes.new("Stalker_Torso")
    bm = bmesh.new()

    n_rings = 34
    n_seg = 24
    # Explicit heights capturing column coat -> emaciated waist -> inverted-V ribcage -> broad shoulder shelf -> slim neck
    z_levels = [
        0.00, 0.20, 0.45, 0.72, 1.00, 1.12, 1.25, 1.38,
        1.48, 1.58, 1.66, 1.72, 1.75, 1.78, 1.80, 1.825, 1.85, 1.90, 1.95,
    ]
    # Add intermediate dense samples along [0..1.95] so Subsurf preserves the crisp shoulder shelf
    z_samples = []
    for i in range(n_rings):
        u = i / float(n_rings - 1)
        # Map higher density around shoulder shelf 1.66..1.88
        if u < 0.45:
            z = (u / 0.45) * 1.38
        elif u < 0.85:
            z = 1.38 + ((u - 0.45) / 0.40) * 0.48
        else:
            z = 1.86 + ((u - 0.85) / 0.15) * 0.09
        z_samples.append(z)

    rings = []
    for z in z_samples:
        if z < 1.00:
            k = z / 1.00
            rx = 0.145 * (1.0 - k) + 0.122 * k
            ry = 0.105 * (1.0 - k) + 0.088 * k
        elif z < 1.38:
            k = (z - 1.00) / 0.38
            # Emaciated narrow waist dipping around z=1.25
            waist_dip = math.sin(k * math.pi)
            rx = 0.122 * (1.0 - k) + 0.108 * k - 0.010 * waist_dip
            ry = 0.088 * (1.0 - k) + 0.078 * k - 0.006 * waist_dip
        elif z < 1.72:
            k = smoothstep((z - 1.38) / 0.34)
            rx = 0.108 * (1.0 - k) + 0.240 * k
            ry = 0.078 * (1.0 - k) + 0.125 * k
        elif z <= 1.78:
            rx = 0.240
            ry = 0.125
        elif z < 1.85:
            # SHARP HUMANOID SHOULDER SHELF (24cm -> 5.2cm over 7cm height!)
            k = smoothstep((z - 1.78) / 0.07)
            rx = 0.240 * (1.0 - k) + 0.052 * k
            ry = 0.125 * (1.0 - k) + 0.058 * k
        else:
            k = (z - 1.85) / 0.10
            rx = 0.052 * (1.0 - k) + 0.046 * k
            ry = 0.058 * (1.0 - k) + 0.048 * k

        # Forward predatory lean in upper back & neck (-Y)
        hunch_t = smoothstep((z - 1.45) / 0.50) if z > 1.45 else 0.0
        cy = -0.075 * hunch_t

        ring_verts = []
        for si in range(n_seg):
            th = (si / float(n_seg)) * 2.0 * math.pi
            u_h = z / 1.95
            fold_amp = 0.012 * (1.0 - smoothstep(z / 1.20)) + 0.004 * math.sin(u_h * math.pi)
            fold = fold_amp * math.cos(7.0 * th + 0.5)
            hem_jag = 0.022 * math.sin(5.0 * th + 0.4) * max(0.0, 1.0 - z * 12.0)
            # Subtle asymmetrical raised left (+X) hunched shoulder
            sh_asym = 0.025 * max(0.0, math.cos(th)) * smoothstep((z - 1.55) / 0.22) * (1.0 - smoothstep((z - 1.79) / 0.06))
            vx = (rx + fold) * math.cos(th)
            vy = cy + (ry + fold * 0.65) * math.sin(th)
            vz = max(0.0, z + hem_jag + sh_asym)
            ring_verts.append(bm.verts.new((vx, vy, vz)))
        rings.append(ring_verts)

    for ri in range(len(rings) - 1):
        for si in range(n_seg):
            ns = (si + 1) % n_seg
            bm.faces.new([rings[ri][si], rings[ri][ns], rings[ri + 1][ns], rings[ri + 1][si]])

    # Cap neck top & hem bottom
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new("Stalker_Torso", me)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(stalker_mat)
    sub = obj.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = 2
    sub.render_levels = 2
    return obj


def _make_stalker_skull(stalker_mat):
    """Sculpt elongated gaunt skull with physically recessed orbital eye sockets & brow ridge."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=1.0, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = "Stalker_Skull"
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)
    for v in bm.verts:
        nx, ny, nz = v.co.x, v.co.y, v.co.z
        # Elongated gaunt horror skull: height ~0.26m, narrow cheekbones & brow
        jaw_taper = 0.65 + 0.35 * smoothstep((nz + 0.7) / 1.4)
        vx = nx * 0.080 * jaw_taper
        vy = ny * 0.098 * (0.88 + 0.14 * nz)
        vz = (nz + 1.0) * 0.130

        # Sunken cheekbones below sockets
        if ny < -0.25 and 0.045 < vz < 0.115 and abs(vx) > 0.026:
            vy += 0.014 * (1.0 - abs(vz - 0.082) / 0.038)

        # Physically recessed dark orbital eye hollows at (+-0.029, -0.080, 0.138)
        if ny < -0.2:
            for ex in (-0.029, 0.029):
                d_eye = math.hypot(vx - ex, vz - 0.138)
                if d_eye < 0.024:
                    push = smoothstep(1.0 - d_eye / 0.024)
                    vy += 0.026 * push
            # Subtle overhanging brow ridge above eyes
            if 0.155 < vz < 0.185 and abs(vx) < 0.058:
                brow = smoothstep(1.0 - abs(vz - 0.170) / 0.016) * (1.0 - abs(vx) / 0.058)
                vy -= 0.012 * brow

        v.co = Vector((vx, vy, vz))
    for f in bm.faces:
        f.smooth = True
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.data.materials.append(stalker_mat)
    sub = obj.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = 2
    sub.render_levels = 2
    return obj


def build_stalker():
    """Towering hunched gaunt humanoid horror silhouette (~2.17m) with razor-slit eyes & curved gripping claws."""
    stalker_mat = make_silhouette_rim_mat("Stalker_Void_Silhouette", hex_lin("#C40B0B"), rim_power=0.54, rim_strength=0.78)
    eye_mat = make_mat_solid("Stalker_Eye_Ivory", hex_lin("#EFECE4"), emission_rgba=hex_lin("#EFECE4"), emission_strength=4.8, pure_emission=True)

    root = bpy.data.objects.new("Stalker_Root", None)
    bpy.context.collection.objects.link(root)
    root.location = (-1.60, 0.32, 0.0)

    torso = _make_stalker_torso(stalker_mat)
    torso.parent = root
    torso.rotation_mode = "XYZ"

    # Passive hanging right shadow-arm descending from right shoulder (-0.18, -0.02, 1.72) along hip
    rc_data = bpy.data.curves.new(name="Stalker_RightArm", type="CURVE")
    rc_data.dimensions = "3D"
    rc_data.resolution_u = 16
    rc_data.bevel_depth = 0.030
    rc_data.bevel_resolution = 6
    rc_data.use_fill_caps = False
    r_sp = rc_data.splines.new("BEZIER")
    r_sp.bezier_points.add(2)
    r_pts = [
        ((-0.18, -0.02, 1.72), 1.15),
        ((-0.20, 0.01, 1.38), 0.78),
        ((-0.20, 0.02, 1.05), 0.55),
    ]
    for pi, (pt, rad) in enumerate(r_pts):
        bp = r_sp.bezier_points[pi]
        bp.co = Vector(pt)
        bp.radius = rad
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    r_arm = bpy.data.objects.new("Stalker_RightArm", rc_data)
    bpy.context.collection.objects.link(r_arm)
    r_arm.data.materials.append(stalker_mat)
    r_arm.parent = torso

    # Head pivot rigidly seated inside torso's hunched neck (zero neck gap)
    head_pivot = bpy.data.objects.new("Stalker_HeadPivot", None)
    bpy.context.collection.objects.link(head_pivot)
    head_pivot.parent = torso
    head_pivot.location = (0.0, -0.075, 1.91)
    head_pivot.rotation_mode = "XYZ"

    skull = _make_stalker_skull(stalker_mat)
    skull.parent = head_pivot

    # Narrow sunken razor-slit ivory eyes + blinking eyelid caps (DIRECT children of HeadPivot -> zero detach!)
    lids = []
    for side, sx in (("L", 0.029), ("R", -0.029)):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=1.0, location=(0, 0, 0))
        eo = bpy.context.active_object
        eo.name = f"Stalker_Eye_{side}"
        eo.scale = (0.0095, 0.0050, 0.0038)
        eo.location = (sx, -0.070, 0.138)
        eo.data.materials.append(eye_mat)
        eo.parent = head_pivot

        # Dark eyelid shutter pivoting directly over the sunken eye for creepy slow blinks
        bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=8, radius=1.0, location=(0, 0, 0))
        lid = bpy.context.active_object
        lid.name = f"Stalker_Lid_{side}"
        lid.scale = (0.0125, 0.0075, 0.0065)
        lid.location = (sx, -0.071, 0.145)
        lid.data.materials.append(stalker_mat)
        lid.parent = head_pivot
        lids.append(lid)

    # Seamless tapered 3D Bezier left arm rooted high inside broad left shoulder (0.17, -0.03, 1.72)
    cdata = bpy.data.curves.new(name="Stalker_Arm", type="CURVE")
    cdata.dimensions = "3D"
    cdata.resolution_u = 24
    cdata.bevel_depth = 0.033
    cdata.bevel_resolution = 8
    cdata.use_fill_caps = False
    arm_spline = cdata.splines.new("BEZIER")
    arm_spline.bezier_points.add(3)
    arm_pts_init = [
        ((0.17, -0.03, 1.72), 1.25),
        ((0.28, 0.04, 1.48), 0.78),
        ((0.30, -0.06, 1.40), 0.56),
        ((0.32, -0.17, 1.38), 0.44),
    ]
    for pi, (pt, rad) in enumerate(arm_pts_init):
        bp = arm_spline.bezier_points[pi]
        bp.co = Vector(pt)
        bp.radius = rad
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    arm_obj = bpy.data.objects.new("Stalker_Arm", cdata)
    bpy.context.collection.objects.link(arm_obj)
    arm_obj.data.materials.append(stalker_mat)
    arm_obj.parent = torso

    # Hidden wrist-palm + 4 smoothly curved 3D Bezier gripping fingers wrapping around Doorframe_Right_Jamb corner
    hand_pivot = bpy.data.objects.new("Stalker_HandPivot", None)
    bpy.context.collection.objects.link(hand_pivot)
    hand_pivot.parent = torso
    hand_pivot.location = arm_pts_init[-1][0]
    hand_pivot.rotation_mode = "XYZ"

    # Sleek hidden wrist-knuckle bridge connecting Bezier wrist to finger bases
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=1.0, location=(0.002, -0.005, 0.0))
    palm = bpy.context.active_object
    palm.name = "Stalker_Palm"
    palm.scale = (0.016, 0.015, 0.034)
    for f in palm.data.polygons:
        f.use_smooth = True
    palm.data.materials.append(stalker_mat)
    palm.parent = hand_pivot

    finger_z_offsets = [0.028, 0.010, -0.008, -0.024]
    finger_scales = [0.95, 1.06, 1.00, 0.85]
    for fi, (z_off, f_sc) in enumerate(zip(finger_z_offsets, finger_scales)):
        fc = bpy.data.curves.new(name=f"Stalker_Claw_{fi}", type="CURVE")
        fc.dimensions = "3D"
        fc.resolution_u = 14
        fc.bevel_depth = 0.0055
        fc.bevel_resolution = 5
        fc.use_fill_caps = True
        fsp = fc.splines.new("BEZIER")
        fsp.bezier_points.add(3)
        # Hook smoothly forward (-Y) around jamb inside corner, then curve rightward & down onto front red face!
        f_pts = [
            ((0.0, 0.0, z_off), 1.00),
            ((0.012 * f_sc, -0.032, z_off - 0.004), 0.85),
            ((0.036 * f_sc, -0.035, z_off - 0.014), 0.60),
            ((0.052 * f_sc, -0.028, z_off - 0.026), 0.28),
        ]
        for pi, (pt, rad) in enumerate(f_pts):
            bp = fsp.bezier_points[pi]
            bp.co = Vector(pt)
            bp.radius = rad
            bp.handle_left_type = "AUTO"
            bp.handle_right_type = "AUTO"
        fobj = bpy.data.objects.new(f"Stalker_Claw_{fi}", fc)
        bpy.context.collection.objects.link(fobj)
        fobj.data.materials.append(stalker_mat)
        fobj.parent = hand_pivot

    return {
        "root": root,
        "torso": torso,
        "head_pivot": head_pivot,
        "lids": lids,
        "arm_spline": arm_spline,
        "hand_pivot": hand_pivot,
    }


def _entity_spine(idx: int, t: float):
    """Analytical centerline (x_local, y_local, z_local) & body radii along creeping entity t in [0,1]."""
    phases = (0.2, 1.8, 3.3, 4.9)
    ph = phases[idx]
    x = -0.68 + 1.04 * t
    y = 0.035 * math.sin(t * 2.1 * math.pi + ph)
    z = 0.038 * math.sin(t * 2.4 * math.pi + ph * 1.4)

    # Stalk -> swollen asymmetrical bulbous shadow-head around t in [0.58..0.94] -> smooth rounded dome snout
    bulb_peak = 0.165 if idx == 1 else 0.148
    bulb = math.exp(-((t - 0.80) / 0.16) ** 2) * (bulb_peak - 0.082)
    undul = 0.012 * math.sin(t * 14.0 + ph)
    if t < 0.88:
        tip_taper = 1.0
    else:
        u_cap = min(1.0, (t - 0.88) / 0.12)
        tip_taper = max(0.12, math.sqrt(max(0.0, 1.0 - (u_cap ** 2) * 0.94)))
    r_y = (0.082 + bulb + undul) * tip_taper
    r_z = (0.088 + bulb * 1.15 + undul) * tip_taper
    return Vector((x, y, z)), r_y, r_z


def _make_entity_body(idx: int, mat):
    """Build organic lumpy bulbous shadow-head + creeping stalk mesh + smooth shading."""
    name = f"Entity_{idx}_Body"
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()

    n_rings = 32
    n_seg = 24
    phases = (0.2, 1.8, 3.3, 4.9)
    ph = phases[idx]
    rings = []
    for ri in range(n_rings):
        t = ri / float(n_rings - 1)
        center, r_y, r_z = _entity_spine(idx, t)
        ring_v = []
        for si in range(n_seg):
            th = (si / float(n_seg)) * 2.0 * math.pi
            lump = (
                0.013 * math.sin(4.0 * th + 9.0 * t + ph)
                + 0.008 * math.cos(7.0 * th - 13.0 * t)
            ) * (0.4 + 0.6 * math.sin(t * math.pi))
            vy = center.y + (r_y + lump) * math.cos(th)
            vz = center.z + (r_z + lump) * math.sin(th)
            ring_v.append(bm.verts.new((center.x, vy, vz)))
        rings.append(ring_v)

    for ri in range(n_rings - 1):
        for si in range(n_seg):
            ns = (si + 1) % n_seg
            bm.faces.new([rings[ri][si], rings[ri + 1][si], rings[ri + 1][ns], rings[ri][ns]])

    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    sub = obj.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = 2
    sub.render_levels = 2
    return obj


def _make_almond_lid(name: str, radius: float, is_upper: bool, mat):
    """Smooth parametric curved almond-shaped fleshy eyelid shell hugging eyeball front."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    n_az = 28
    n_el = 7
    rings = []
    # Upper lid covers from rim border up to +pi/2; Lower lid from -pi/2 up to rim border
    for ei in range(n_el):
        ef = ei / float(n_el - 1)
        ring = []
        for ai in range(n_az):
            az = (ai / float(n_az)) * 2.0 * math.pi - math.pi  # az=0 -> front -Y
            front = max(0.0, math.cos(az))
            if is_upper:
                # Hoods top ~32% in middle front (sin(0.28)=0.28), wraps low around back (+Y)
                el_rim = 0.28 * (front ** 1.25) - 0.18 * (1.0 - front)
                el = el_rim * (1.0 - ef) + (math.pi * 0.495) * ef
            else:
                # Hoods bottom ~34% in middle front, wraps up around back
                el_rim = -0.34 * (front ** 1.25) + 0.16 * (1.0 - front)
                el = (-math.pi * 0.495) * (1.0 - ef) + el_rim * ef
            rc = radius * math.cos(el)
            vx = rc * math.sin(az)
            vy = -rc * math.cos(az)
            vz = radius * math.sin(el)
            ring.append(bm.verts.new((vx, vy, vz)))
        rings.append(ring)

    for ei in range(n_el - 1):
        for ai in range(n_az):
            na = (ai + 1) % n_az
            bm.faces.new([rings[ei][ai], rings[ei][na], rings[ei + 1][na], rings[ei + 1][ai]])

    pole_ring = rings[-1] if is_upper else rings[0]
    bm.faces.new(pole_ring if is_upper else list(reversed(pole_ring)))
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
    sub = obj.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 1
    return obj


def build_eldritch_entities():
    """4 organic bulbous creeping shadow-entities studded with 7 heavy-lidded bloodshot horror eyes."""
    body_mat = make_silhouette_rim_mat("Tendril_Void_Mat", hex_lin("#9E0909"), rim_power=0.62, rim_strength=0.48, wet_specular=True, wet_roughness=0.62)
    lid_mat = make_mat_solid("Horror_Eyelid_Flesh", (0.003, 0.001, 0.002, 1.0), roughness=0.45)

    # Wet bloodshot horror eyeball shader using painted assets/horror_eye.png (restrained emission -> zero cartoon bloom)
    eye_mat = bpy.data.materials.new("Horror_Eye_Mat")
    eye_mat.use_nodes = True
    nt = eye_mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(ASSETS / "horror_eye.png"))
    tex.extension = "EXTEND"
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.08
    bsdf.inputs["Emission Strength"].default_value = 0.42
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # (z_base, x_emerged, delay_frames, eye_specs: [(t_spine, z_offset_fac, er)])
    entity_specs = [
        (1.90, -0.90, 0, [(0.81, +0.10, 0.042), (0.68, -0.25, 0.026)]),
        (1.40, -0.85, 3, [(0.83, +0.14, 0.040), (0.72, -0.24, 0.031)]),
        (0.92, -0.89, 1, [(0.82, -0.10, 0.036), (0.69, +0.28, 0.028)]),
        (0.48, -0.94, 4, [(0.81, +0.08, 0.038)]),
    ]

    entities = []
    for idx, (z_base, x_emerged, delay, eye_list) in enumerate(entity_specs):
        root = bpy.data.objects.new(f"Entity_{idx}_Root", None)
        bpy.context.collection.objects.link(root)
        root.location = (-1.66, 0.08, z_base)
        root.rotation_mode = "XYZ"

        _body = _make_entity_body(idx, body_mat)
        _body.parent = root

        # 2 organic S-curved wispy shadow tendrils curling softly off each silhouette (no rigid straight sticks!)
        for wi, w_sign in enumerate((1.0, -1.0)):
            wc_data = bpy.data.curves.new(name=f"Entity_{idx}_Wisp_{wi}", type="CURVE")
            wc_data.dimensions = "3D"
            wc_data.resolution_u = 18
            wc_data.bevel_depth = 0.011
            wc_data.bevel_resolution = 5
            ws = wc_data.splines.new("BEZIER")
            ws.bezier_points.add(4)
            base_c, _ry, rz = _entity_spine(idx, 0.68 + 0.08 * wi)
            w_pts = [
                (base_c + Vector((-0.02, 0.02, w_sign * rz * 0.55)), 1.0),
                (base_c + Vector((0.06, 0.01, w_sign * (rz * 0.92 + 0.03))), 0.68),
                (base_c + Vector((0.14, -0.01, w_sign * (rz * 1.15 + 0.06))), 0.42),
                (base_c + Vector((0.09, -0.02, w_sign * (rz * 1.32 + 0.09))), 0.20),
                (base_c + Vector((0.16, -0.01, w_sign * (rz * 1.44 + 0.12))), 0.04),
            ]
            for pi, (pt, rr) in enumerate(w_pts):
                bp = ws.bezier_points[pi]
                bp.co = pt
                bp.radius = rr
                bp.handle_left_type = "AUTO"
                bp.handle_right_type = "AUTO"
            wobj = bpy.data.objects.new(f"Entity_{idx}_Wisp_{wi}", wc_data)
            bpy.context.collection.objects.link(wobj)
            wobj.data.materials.append(body_mat)
            wobj.parent = root

        eyes_info = []
        for ei, (t_eye, z_fac, er) in enumerate(eye_list):
            spine_c, r_y, r_z = _entity_spine(idx, t_eye)
            # Embed eyeball center +0.46*er deeper (+Y) than front surface so it sits physically INSIDE the flesh
            pivot_loc = Vector((spine_c.x, spine_c.y - r_y + er * 0.46, spine_c.z + z_fac * r_z))
            epiv = bpy.data.objects.new(f"Entity_{idx}_EyePivot_{ei}", None)
            bpy.context.collection.objects.link(epiv)
            epiv.parent = root
            epiv.location = pivot_loc
            epiv.rotation_mode = "XYZ"

            # Eyeball with planar front-facing (-Y) UV mapping & smooth shading
            bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=er, location=(0, 0, 0))
            eb = bpy.context.active_object
            eb.name = f"Entity_{idx}_Eyeball_{ei}"
            bpy.ops.object.mode_set(mode="EDIT")
            bm = bmesh.from_edit_mesh(eb.data)
            uv_layer = bm.loops.layers.uv.verify()
            for f in bm.faces:
                f.smooth = True
                for l in f.loops:
                    co = l.vert.co
                    u = max(0.002, min(0.998, 0.5 + co.x / (2.0 * er)))
                    v = max(0.002, min(0.998, 0.5 + co.z / (2.0 * er)))
                    l[uv_layer].uv = (u, v)
            bmesh.update_edit_mesh(eb.data)
            bpy.ops.object.mode_set(mode="OBJECT")
            eb.data.materials.append(eye_mat)
            eb.parent = epiv
            eb.rotation_mode = "XYZ"

            # Sculpted dark fleshy almond upper & lower eyelids framing a sinister horizontal slit
            u_lid = _make_almond_lid(f"Entity_{idx}_UpperLid_{ei}", er * 1.07, True, lid_mat)
            u_lid.parent = epiv
            u_lid.rotation_mode = "XYZ"
            l_lid = _make_almond_lid(f"Entity_{idx}_LowerLid_{ei}", er * 1.07, False, lid_mat)
            l_lid.parent = epiv
            l_lid.rotation_mode = "XYZ"

            eyes_info.append((epiv, eb, u_lid, l_lid, er))

        entities.append({
            "idx": idx,
            "root": root,
            "z_base": z_base,
            "x_emerged": x_emerged,
            "delay": delay,
            "eyes": eyes_info,
        })

    return entities


def setup_lighting_and_camera():
    world = bpy.data.worlds.new("Gothic_World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = hex_lin("#080709")
    bg.inputs["Strength"].default_value = 0.12

    # Soft crimson room light at clock face (higher soft size -> silky smooth illumination)
    bpy.ops.object.light_add(type="POINT", location=(0.08, -0.45, 2.20))
    red_pt = bpy.context.active_object
    red_pt.name = "Clock_Crimson_Point"
    red_pt.data.color = (1.0, 0.032, 0.032)
    red_pt.data.energy = 125.0
    red_pt.data.shadow_soft_size = 0.55

    # Dedicated subtle red rim light behind girl
    bpy.ops.object.light_add(type="AREA", location=(0.06, -0.88, 1.55))
    rim_area = bpy.context.active_object
    rim_area.name = "Girl_Back_Crimson_Area"
    rim_area.data.color = (1.0, 0.035, 0.035)
    rim_area.data.energy = 55.0
    rim_area.data.size = 0.85
    rim_area.rotation_euler = (math.radians(52), 0, math.radians(180))

    # Cool gothic wall fill (desaturated slate corners contrasting with crimson core)
    bpy.ops.object.light_add(type="AREA", location=(-0.10, -2.75, 2.25))
    cool_fill = bpy.context.active_object
    cool_fill.name = "Wall_Cool_Fill"
    cool_fill.data.color = (0.62, 0.68, 0.80)
    cool_fill.data.energy = 22.0
    cool_fill.data.size = 2.6
    cool_fill.rotation_euler = (math.radians(78), 0, 0)

    # Wider vertical-fit camera (lens=24.5mm, sensor_height=24mm -> half_h=1.71m, half_w=0.96m at y=0)
    # Frames full doorway [-1.06..-0.46], main clock, all 10 word-clocks, side table, and girl silhouette!
    bpy.ops.object.camera_add(location=(-0.06, -3.50, 1.38))
    cam = bpy.context.active_object
    cam.name = "Main_Camera"
    cam.data.lens = 24.5
    cam.data.sensor_fit = "VERTICAL"
    cam.data.sensor_height = 24.0
    cam.rotation_mode = "XYZ"
    cam.rotation_euler = (math.radians(92.0), 0.0, 0.0)
    bpy.context.scene.camera = cam

    return cam, red_pt


def apply_frame_state(frame: int, handles: dict):
    t = (frame - 1) / float(TOTAL_FRAMES)
    two_pi_t = 2.0 * math.pi * t
    stepped_f = ((frame - 1) // 2) * 2 + 1
    t2 = (stepped_f - 1) / float(TOTAL_FRAMES)
    two_pi_t2 = 2.0 * math.pi * t2

    # 1. Camera (on ones, seamless breathing push + sway + III:00 slam shockwave recoil f116-f130)
    cam = handles["cam"]
    push = 0.5 - 0.5 * math.cos(two_pi_t)
    jolt_x, jolt_z, jolt_roll = 0.0, 0.0, 0.0
    if 116 <= frame <= 130:
        df = float(frame - 116)
        env = math.exp(-df / 3.5) * math.sin(df * 1.8)
        jolt_z = 0.015 * env
        jolt_x = 0.008 * math.exp(-df / 3.5) * math.cos(df * 2.1)
        jolt_roll = 0.28 * env
    cam.location = (
        -0.06 + 0.010 * math.sin(two_pi_t) + jolt_x,
        -3.50 + 0.075 * push,
        1.38 + 0.008 * math.sin(two_pi_t * 2.0) + jolt_z,
    )
    cam.rotation_euler = (math.radians(92.0), math.radians(jolt_roll), 0.0)

    # 2. Main Giant Clock Hands + Dial Slam Flare
    hour_h, min_h, sec_h, dial_emit = handles["main_clock"]
    if frame <= 43:
        sec_idx = (frame - 1) // 24
        sub = ((frame - 1) % 24) / 24.0
        overshoot = math.exp(-sub * 10.0) * math.sin(sub * 18.0) * 0.08 if sub < 0.35 else 0.0
        sec_deg = (sec_idx * 6.0) + overshoot * 6.0
        min_deg = 60.0 + sec_idx * 0.5
        hour_deg = 300.0
    elif frame <= 115:
        u = (frame - 43) / 72.0
        burst = u + 0.06 * math.sin(u * 18.0 * math.pi)
        sec_deg = 6.0 - burst * 720.0
        min_deg = 60.5 - burst * 330.5
        hour_deg = 300.0 - burst * 210.0
    elif frame <= 130:
        sec_deg = -714.0
        min_deg = -270.0
        hour_deg = 90.0
    elif frame <= 187:
        u = (frame - 130) / 57.0
        sec_deg = -714.0 + u * 540.0 + 18.0 * math.sin(u * 14.0 * math.pi)
        min_deg = -270.0 + u * 240.0
        hour_deg = 90.0 - u * 120.0
    else:
        u = smoothstep((frame - 187) / float(TOTAL_FRAMES - 187))
        sec_deg = (-174.0) * (1.0 - u) + 0.0 * u
        min_deg = (-30.0) * (1.0 - u) + 60.0 * u
        hour_deg = (-30.0) * (1.0 - u) + (-60.0) * u

    hour_h.rotation_euler = (0.0, math.radians(hour_deg), 0.0)
    min_h.rotation_euler = (0.0, math.radians(min_deg), 0.0)
    sec_h.rotation_euler = (0.0, math.radians(sec_deg), 0.0)

    red_pt = handles["red_pt"]
    slam_gauss = math.exp(-((frame - 120) / 4.5) ** 2) if 112 <= frame <= 135 else 0.0
    red_pt.data.energy = 125.0 + 12.0 * math.sin(two_pi_t * 4.0) + 115.0 * slam_gauss
    dial_emit.inputs["Strength"].default_value = 1.45 + 0.70 * slam_gauss

    # 3. Word-Clocks + Hidden "DON'T TURN" flicker
    wc = handles["word_clocks"]
    for idx_w, (wname, hlist) in enumerate(wc.items()):
        if wname in ("ALONE_MIX", "ALONE_BSDF"):
            continue
        for hi, ho in enumerate(hlist):
            ang = 360.0 * math.sin(two_pi_t2 * (1 + (idx_w % 2)) + idx_w * 0.9 + hi * 1.4)
            ho.rotation_euler = (0.0, math.radians(ang), 0.0)

    if "ALONE_MIX" in wc:
        if frame in (125, 166):
            fac = 0.65
        elif 126 <= frame <= 165:
            fac = 1.0
        else:
            fac = 0.0
        wc["ALONE_MIX"].inputs["Factor"].default_value = fac
        wc["ALONE_BSDF"].inputs["Emission Strength"].default_value = 0.13 + 1.15 * fac

    # 4. Foreground Girl (breathing + III:00 slam startled flinch & cold draft gust + eerie doorway head tilt)
    g_rig, _g_meshes, g_base, g_hair, g_skirt = handles["girl"]
    breath = math.sin(two_pi_t2 * 2.0)

    gust = 0.0
    flinch = 0.0
    if 116 <= frame <= 136:
        df2 = float(stepped_f - 116)
        if df2 >= 0.0:
            gust = math.exp(-df2 / 5.5) * math.sin(df2 * 0.85)
            flinch = math.exp(-df2 / 3.8)

    g_rig.pose.bones["J_Bip_C_Chest"].rotation_quaternion = g_base["J_Bip_C_Chest"] @ Quaternion((1, 0, 0), math.radians(1.6 * breath))
    g_rig.pose.bones["J_Bip_C_UpperChest"].rotation_quaternion = g_base["J_Bip_C_UpperChest"] @ Quaternion((1, 0, 0), math.radians(1.2 * breath + 2.2 * flinch))
    g_rig.pose.bones["J_Bip_L_Shoulder"].rotation_quaternion = g_base["J_Bip_L_Shoulder"] @ Quaternion((0, 0, 1), math.radians(2.2 * flinch))
    g_rig.pose.bones["J_Bip_R_Shoulder"].rotation_quaternion = g_base["J_Bip_R_Shoulder"] @ Quaternion((0, 0, 1), math.radians(-2.2 * flinch))

    tilt = 0.0
    if 146 <= frame <= 190:
        if frame < 160:
            tilt = smoothstep((frame - 146) / 14.0)
        elif frame <= 174:
            tilt = 1.0
        else:
            tilt = 1.0 - smoothstep((frame - 174) / 16.0)
    g_rig.pose.bones["J_Bip_C_Head"].rotation_quaternion = g_base["J_Bip_C_Head"] @ Quaternion((0, 1, 0), math.radians(-5.0 * tilt)) @ Quaternion((0, 0, 1), math.radians(3.5 * tilt))

    for hi, hb in enumerate(g_hair):
        sway = 1.8 * math.sin(two_pi_t2 * 2.0 + hi * 0.55) + 7.5 * gust * math.cos(hi * 0.7)
        hb.rotation_quaternion = g_base[hb.name] @ Quaternion((0, 0, 1), math.radians(sway))
    for si, sb in enumerate(g_skirt):
        sk_sway = 5.0 * gust * (1.0 if si % 2 == 0 else 0.75)
        sb.rotation_quaternion = g_base[sb.name] @ Quaternion((1, 0, 0), math.radians(sk_sway))

    # 5. Doorway Intrusion 1: Hunched Towering Humanoid Figure + Curved Gripping Claws (f038-f116)
    st = handles["stalker"]
    s_root = st["root"]
    s_torso = st["torso"]
    s_head = st["head_pivot"]
    s_lids = st["lids"]
    s_arm_sp = st["arm_spline"]
    s_hand = st["hand_pivot"]

    def set_tree_hide(obj, hide: bool):
        obj.hide_render = hide
        for ch in obj.children:
            set_tree_hide(ch, hide)

    if frame < 38 or frame > 116:
        s_root.location = (-1.62, 0.34, 0.0)
        set_tree_hide(s_root, True)
    else:
        set_tree_hide(s_root, False)
        if frame < 62:
            u_hand = smoothstep((frame - 38) / 18.0)
            u_body = smoothstep((frame - 40) / 22.0)
            u_curl = smoothstep((frame - 44) / 14.0)
        elif frame <= 101:
            u_hand = 1.0
            u_body = 1.0
            u_curl = 1.0
        else:
            # Synchronized grip release FIRST, then unified root+arm retreat completely behind Wall_Left by f116!
            u_curl = 1.0 - smoothstep((frame - 101) / 6.0)
            u_hand = 1.0 - smoothstep((frame - 101) / 11.0)
            u_body = 1.0 - smoothstep((frame - 102) / 14.0)

        s_root.location = (-1.58 + 0.78 * u_body, 0.32 - 0.18 * u_body, 0.0)  # glides to (-0.80, 0.14)
        loom_sway = 1.5 * math.sin(two_pi_t2 * 3.0) * u_body
        s_torso.rotation_euler = (math.radians(loom_sway), 0.0, 0.0)

        # Predatory head tilt (f091-f101) + rigid almond eyelids (zero hide_render lag on eyes!)
        extra_tilt = 0.0
        if 91 <= frame <= 105:
            if frame < 96:
                extra_tilt = smoothstep((frame - 91) / 5.0)
            elif frame <= 101:
                extra_tilt = 1.0
            else:
                extra_tilt = 1.0 - smoothstep((frame - 101) / 4.0)
        s_head.rotation_euler = (math.radians(7.0 * u_body + 2.0 * extra_tilt), math.radians(11.0 * extra_tilt * u_body), 0.0)

        blink_t = 1.0 if frame in (88, 89, 90) else 0.0
        for lid in s_lids:
            lid.location.z = 0.145 - 0.006 * blink_t
            lid.scale.z = 0.0065 + 0.0025 * blink_t

        bpy.context.view_layer.update()

        # Seamless wrist tucked behind/inside crimson jamb corner (-0.482, -0.028, 1.38) -> pulls cleanly back inside doorway
        wrist_tucked = Vector((0.22, -0.02, 1.24))
        wrist_emerged = s_torso.matrix_world.inverted() @ Vector((-0.482, -0.028, 1.38))
        wrist_local = wrist_tucked.lerp(wrist_emerged, u_hand)

        s_arm_sp.bezier_points[0].co = Vector((0.17, -0.03, 1.72))
        s_arm_sp.bezier_points[1].co = Vector((0.26 + 0.04 * u_hand, 0.04 - 0.02 * u_hand, 1.48))
        s_arm_sp.bezier_points[2].co = Vector((wrist_local.x * 0.68 + 0.10, wrist_local.y * 0.62 - 0.02, 1.40))
        s_arm_sp.bezier_points[3].co = wrist_local

        s_hand.location = wrist_local
        s_hand.rotation_euler = (0.0, 0.0, math.radians(-5.0 * u_hand))
        grip_sc = 0.35 + 0.65 * u_curl
        s_hand.scale = (grip_sc, grip_sc, 1.0)

    # 6. Doorway Intrusion 2: 4 Bulbous Creeping Shadow-Entities + 7 Locked Heavy-Lidded Horror Eyes (f128-f194)
    for ent in handles["entities"]:
        idx_e = ent["idx"]
        e_root = ent["root"]
        delay = ent["delay"]
        f_start = 128 + delay
        f_emerge = 150 + delay
        f_retreat_start = 170 + delay
        f_end = 190 + delay

        if frame < f_start or frame > f_end:
            p = 0.0
        elif frame <= f_emerge:
            p = smoothstep((frame - f_start) / float(f_emerge - f_start))
        elif frame <= f_retreat_start:
            p = 1.0
        else:
            p = 1.0 - smoothstep((frame - f_retreat_start) / float(f_end - f_retreat_start))

        # CRITICAL EYE-BODY LOCK: Hide entire entity tree ONLY together when p <= 0.001 behind Wall_Left!
        if p <= 0.001:
            e_root.location = (-1.66, 0.08, ent["z_base"])
            set_tree_hide(e_root, True)
            continue

        set_tree_hide(e_root, False)
        x_cur = -1.66 * (1.0 - p) + ent["x_emerged"] * p
        z_writhe = 0.024 * math.sin(two_pi_t2 * 4.0 + idx_e * 1.4) * p
        roll_writhe = 3.5 * math.cos(two_pi_t2 * 3.0 + idx_e * 1.1) * p
        e_root.location = (x_cur, 0.08, ent["z_base"] + z_writhe)
        e_root.rotation_euler = (0.0, math.radians(roll_writhe), 0.0)

        for ei, (epiv, eb, u_lid, _l_lid, _er) in enumerate(ent["eyes"]):
            # Eerie slow saccadic glances aimed generally toward girl (on twos)
            glance_z = -24.0 + 7.0 * math.sin(two_pi_t2 * 5.0 + idx_e * 1.9 + ei * 1.3)
            glance_x = 12.0 + 5.0 * math.cos(two_pi_t2 * 4.0 + idx_e * 2.3 + ei * 0.9)
            eb.rotation_euler = (math.radians(glance_x), 0.0, math.radians(glance_z))

            # Asynchronous sinister eyelid blinks
            lid_close = 0.0
            if idx_e == 1 and ei == 0 and 160 <= frame <= 163:
                lid_close = 1.0 if frame in (161, 162) else 0.55
            elif idx_e == 0 and ei == 0 and 165 <= frame <= 169:
                lid_close = 0.65 if frame in (166, 167, 168) else 0.35
            u_lid.rotation_euler = (math.radians(38.0 * lid_close), 0.0, 0.0)

    bpy.context.view_layer.update()


def configure_render(res_scale: float):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = 48
    sc.render.resolution_x = int(round(1080 * res_scale))
    sc.render.resolution_y = int(round(1920 * res_scale))
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0


def write_crop_meta(res_scale: float, probe: bool, handles: dict):
    sc = bpy.context.scene
    cam = handles["cam"]
    W = int(round(1080 * res_scale))
    H = int(round(1920 * res_scale))

    def proj_box(world_pt: Vector, bw: int, bh: int):
        co = world_to_camera_view(sc, cam, world_pt)
        px = co.x * W
        py = (1.0 - co.y) * H
        x0 = max(0, min(W - bw, int(round(px - bw / 2))))
        y0 = max(0, min(H - bh, int(round(py - bh / 2))))
        return [x0, y0, min(bw, W - x0), min(bh, H - y0)]

    bw_s, bh_s = int(380 * res_scale), int(860 * res_scale)
    bw_h, bh_h = int(280 * res_scale), int(320 * res_scale)
    bw_t, bh_t = int(440 * res_scale), int(820 * res_scale)
    bw_g, bh_g = int(520 * res_scale), int(760 * res_scale)
    bw_c, bh_c = int(260 * res_scale), int(260 * res_scale)

    f_map = {1: "1", 56: "2", 86: "3", 108: "4", 118: "5", 154: "6", 182: "7", 216: "8"} if probe else {k: str(k) for k in PROBE_FRAMES}

    apply_frame_state(1, handles)
    girl_pt = Vector((0.06, -1.48, 0.92))
    alone_pt = Vector((0.56, -0.02, 1.54))
    stalker_pt = Vector((-0.76, 0.10, 1.35))
    hand_pt = Vector((-0.46, -0.04, 1.32))
    tendril_pt = Vector((-0.76, 0.05, 1.25))

    crops = {
        "stalker_full": {f_map[86]: proj_box(stalker_pt, bw_s, bh_s), f_map[108]: proj_box(stalker_pt, bw_s, bh_s)},
        "doorway_claws": {f_map[56]: proj_box(hand_pt, bw_h, bh_h), f_map[86]: proj_box(hand_pt, bw_h, bh_h)},
        "eldritch_eyes": {f_map[154]: proj_box(tendril_pt, bw_t, bh_t), f_map[182]: proj_box(tendril_pt, bw_t, bh_t)},
        "girl_slam": {f_map[1]: proj_box(girl_pt, bw_g, bh_g), f_map[118]: proj_box(girl_pt, bw_g, bh_g)},
        "clock_flip": {f_map[1]: proj_box(alone_pt, bw_c, bh_c), f_map[154]: proj_box(alone_pt, bw_c, bh_c)},
    }
    meta = {"crops": crops}
    tag = "probe_crops_meta.json" if probe else "full_crops_meta.json"
    (ROOT / "assets" / tag).write_text(json.dumps(meta, indent=2), encoding="utf-8")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    build_room()
    main_clock = build_giant_clock()
    word_clocks = build_word_clocks()
    girl = build_girl_silhouette()
    stalker = build_stalker()
    entities = build_eldritch_entities()
    cam, red_pt = setup_lighting_and_camera()

    handles = {
        "cam": cam,
        "red_pt": red_pt,
        "main_clock": main_clock,
        "word_clocks": word_clocks,
        "girl": girl,
        "stalker": stalker,
        "entities": entities,
    }

    configure_render(args.scale)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_crop_meta(args.scale, args.probe, handles)

    frames = PROBE_FRAMES if args.probe else list(range(1, TOTAL_FRAMES + 1))
    for f in frames:
        apply_frame_state(f, handles)
        bpy.context.scene.frame_set(f)
        bpy.context.scene.render.filepath = str(out_dir / f"f_{f:04d}.png")
        bpy.ops.render.render(write_still=True)

    print(f"Rendered {len(frames)} frames to {out_dir} at scale={args.scale}")


if __name__ == "__main__":
    main()
