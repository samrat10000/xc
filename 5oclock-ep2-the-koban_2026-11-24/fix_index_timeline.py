from pathlib import Path
import sys
p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8-sig')
old="time(info['out_frame_exclusive'])"
assert old in s
p.write_text(s.replace(old,"time(info['out_frame'])"),encoding='utf-8')
