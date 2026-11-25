"""Decode KHR_draco_mesh_compression in a GLB so Blender (without its draco bridge) can import it.
usage: python3 -I undraco.py in.glb out.glb"""
import sys, json, struct
import numpy as np
import DracoPy

src, dst = sys.argv[1], sys.argv[2]
raw = open(src, "rb").read()
jl = struct.unpack("<I", raw[12:16])[0]
j = json.loads(raw[20:20 + jl])
bo = 20 + jl
bl = struct.unpack("<I", raw[bo:bo + 4])[0]
binc = bytearray(raw[bo + 8:bo + 8 + bl])

def pad4(b):
    while len(b) % 4: b.append(0)

def add_view(arr, target=None):
    pad4(binc)
    off = len(binc); data = arr.tobytes(); binc.extend(data)
    v = {"buffer": 0, "byteOffset": off, "byteLength": len(data)}
    if target: v["target"] = target
    j["bufferViews"].append(v); return len(j["bufferViews"]) - 1

CT = {np.float32: 5126, np.uint32: 5125, np.uint16: 5123, np.uint8: 5121}
TYPE = {1: "SCALAR", 2: "VEC2", 3: "VEC3", 4: "VEC4"}

def add_acc(arr, target=None, normalized=False):
    arr = np.ascontiguousarray(arr)
    comps = 1 if arr.ndim == 1 else arr.shape[1]
    a = {"bufferView": add_view(arr, target), "componentType": CT[arr.dtype.type], "count": int(arr.shape[0]),
         "type": TYPE[comps]}
    if normalized: a["normalized"] = True
    if target == 34962 and comps == 3 and arr.dtype == np.float32 and "pos" in str(target):
        pass
    j["accessors"].append(a); return len(j["accessors"]) - 1

done = 0
for m in j["meshes"]:
    for p in m["primitives"]:
        ext = p.get("extensions", {}).get("KHR_draco_mesh_compression")
        if not ext: continue
        bv = j["bufferViews"][ext["bufferView"]]
        o = bv.get("byteOffset", 0)
        mesh = DracoPy.decode(bytes(binc[o:o + bv["byteLength"]]))
        newattr = {}
        for name, uid in ext["attributes"].items():
            att = mesh.get_attribute_by_unique_id(uid)
            old = j["accessors"][p["attributes"][name]]
            data = np.asarray(att["data"]) if isinstance(att, dict) else np.asarray(att.data if hasattr(att, "data") else att)
            n = old["count"]; comps = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[old["type"]]
            dt = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}[old["componentType"]]
            data = data.reshape(n, comps).astype(dt)
            idx = add_acc(data, 34962, old.get("normalized", False))
            if name == "POSITION":
                j["accessors"][idx]["min"] = data.min(0).tolist(); j["accessors"][idx]["max"] = data.max(0).tolist()
            newattr[name] = idx
        p["attributes"] = newattr
        faces = np.asarray(mesh.faces).reshape(-1).astype(np.uint32)
        p["indices"] = add_acc(faces, 34963)
        del p["extensions"]["KHR_draco_mesh_compression"]
        if not p["extensions"]: del p["extensions"]
        done += 1
for k in ("extensionsUsed", "extensionsRequired"):
    if k in j:
        j[k] = [e for e in j[k] if e != "KHR_draco_mesh_compression"]
        if not j[k]: del j[k]
pad4(binc)
j["buffers"][0]["byteLength"] = len(binc)
js = json.dumps(j, separators=(",", ":")).encode()
while len(js) % 4: js += b" "
out = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(binc))
out += struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(binc), 0x004E4942) + bytes(binc)
open(dst, "wb").write(out)
print("decoded primitives:", done, "size MB:", len(out) / 1e6)
