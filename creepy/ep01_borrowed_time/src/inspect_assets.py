import json
from pathlib import Path
import bpy
from mathutils import Vector

ASSETS = [
    ("kid_girl", r"C:\Users\cross\Downloads\xc\5oclock-ep1-the-fourth-note_2026-11-23\assets\cast_v2\kid_girl.blend"),
    ("sam_toon", r"C:\Users\cross\Downloads\xc\5oclock-ep1-the-fourth-note_2026-11-23\assets\toon_sam\sam_toon.blend"),
    ("shopkeeper", r"C:\Users\cross\Downloads\xc\5oclock-ep1-the-fourth-note_2026-11-23\assets\cast_v2\shopkeeper.blend"),
]

report = {}

for label, path in ASSETS:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(path, link=False) as (data_from, data_to):
        data_to.objects = list(data_from.objects)
    for obj in data_to.objects:
        bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.update()

    info = {"path": path, "meshes": [], "armatures": []}
    for obj in bpy.context.scene.objects:
        bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        zs = [p.z for p in bb]
        xs = [p.x for p in bb]
        ys = [p.y for p in bb]
        if obj.type == "MESH":
            mats = [m.name if m else None for m in obj.data.materials]
            vgs = [vg.name for vg in obj.vertex_groups]
            info["meshes"].append({
                "name": obj.name,
                "verts": len(obj.data.vertices),
                "materials": mats,
                "vertex_groups_count": len(vgs),
                "sample_vgs": vgs[:15],
                "bbox_x": [round(min(xs), 3), round(max(xs), 3)],
                "bbox_y": [round(min(ys), 3), round(max(ys), 3)],
                "bbox_z": [round(min(zs), 3), round(max(zs), 3)],
                "parent": obj.parent.name if obj.parent else None,
            })
        elif obj.type == "ARMATURE":
            bones = []
            for pb in obj.pose.bones:
                bones.append({
                    "name": pb.name,
                    "rot_mode": pb.rotation_mode,
                    "head_z": round((obj.matrix_world @ pb.head).z, 3),
                    "parent": pb.parent.name if pb.parent else None,
                })
            info["armatures"].append({
                "name": obj.name,
                "bone_count": len(bones),
                "bones": bones,
            })
    report[label] = info

out_path = Path(r"c:\Users\cross\Downloads\xc\creepy\ep01_borrowed_time\assets\asset_inspection.json")
out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
print("Wrote", out_path)
for k, v in report.items():
    print(f"{k}: meshes={[m['name'] for m in v['meshes']]}, armatures={[(a['name'], a['bone_count']) for a in v['armatures']]}")
