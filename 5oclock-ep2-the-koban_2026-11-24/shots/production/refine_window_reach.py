from pathlib import Path
p=Path(__file__).resolve().parent/'station.py'
s=p.read_text(encoding='utf-8')
old="mom.pose((.718,1.861,.053),-.38,.96)"
assert old in s
p.write_text(s.replace(old,"mom.pose((.721,1.602,.122),-.38,.96)"),encoding='utf-8')
