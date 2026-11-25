"""Stable entry point: queued jobs keep their pinned builder while newer shots improve."""
import os,runpy
from pathlib import Path
version=os.environ.get('VERSION','v007')
builder='shot_builder_v006.py' if version=='v006' else 'shot_builder_v007.py' if version=='v007' else 'shot_builder_v008.py'
runpy.run_path(str(Path(__file__).resolve().with_name(builder)),run_name='__main__')
