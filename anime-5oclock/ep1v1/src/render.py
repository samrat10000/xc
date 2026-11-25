import sys, importlib, os
from multiprocessing import Pool
mod = importlib.import_module(sys.argv[1]); n = int(sys.argv[2]); out = sys.argv[3]
os.makedirs(out, exist_ok=True)
import lib
def go(f):
    lib.save(mod.frame(f), f'{out}/{f:04d}.png')
if __name__ == '__main__':
    with Pool(4) as p: p.map(go, range(n), chunksize=2)
