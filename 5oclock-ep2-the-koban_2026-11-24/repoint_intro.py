from pathlib import Path
root=Path(__file__).resolve().parent
p=root/'shots'/'02_wrong_room'/'src'/'build_wrong_room.py'
s=p.read_text(encoding='utf-8-sig')
old="HERE.parents[2]/'toon3d'/'sam_toon_003.blend'"
assert old in s
p.write_text(s.replace(old,"HERE.parents[1]/'production'/'assets'/'sam_intro_locked.blend'"),encoding='utf-8')
