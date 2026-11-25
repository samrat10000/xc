"""Check the partial full-size PNGs before an explicit same-version resume."""
from pathlib import Path
import sys

from PIL import Image

directory=Path(sys.argv[1])
for cel in sorted(directory.glob('cel_*.png')):
    try:
        with Image.open(cel) as image:
            assert image.size==(1080,1920)
            image.verify()
    except (OSError, SyntaxError, ValueError, AssertionError):
        cel.rename(cel.with_suffix('.interrupted'))
        print('Restarting invalid cel',cel.name)
