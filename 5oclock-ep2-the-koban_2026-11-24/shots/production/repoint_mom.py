from pathlib import Path
p=Path(__file__).resolve().parent/'build_mom.py'
s=p.read_text(encoding='utf-8-sig')
s=s.replace("r'C:/Users/cross/Downloads/xc/anime-5oclock/assets/vroid_cc0/dl/base_female'",
            "os.path.join(HERE, 'assets', 'source_mom')")
s=s.replace("r'C:/Users/cross/Downloads/xc/anime-5oclock/toon3d/scripts/build_sam.py'",
            "os.path.join(HERE, 'assets', 'source_mom', 'build_sam.py')")
p.write_text(s,encoding='utf-8')
