set -e
cd /tmp/claude-0/-home-user/292bd1a1-658e-59e9-b0d9-b1051e3e71a5/scratchpad/trike
python3 src/build_b.py -- out/a2.blend out/tex2 out/b2.blend > out/b2.log 2>&1
python3 src/build_c.py -- out/b2.blend out/c2.blend > out/c2.log 2>&1
python3 src/export.py -- out/c2.blend out/raw2.glb > out/e2.log 2>&1
cd gt && npx gltf-transform draco ../out/raw2.glb ../out/ivory-dead-roads-trike-v2.glb > d2.log 2>&1 && cd ..
RES=1080x1350 S=56 V='[[0.0,-0.1,2.0,-145,15,15,50]]' python3 src/render.py -- out/c2.blend out/hero2 > out/r2.log 2>&1
RES=720x720 S=24 V='[[-3.2,0,1.3,-120,25,4.2,50],[-0.5,0,1.2,-90,5,13,50],[0.6,0,1.9,-130,30,3.2,50],[1.2,0,1.2,30,20,8.5,50]]' python3 src/render.py -- out/c2.blend out/d2 > out/r3.log 2>&1
echo CHAIN_DONE
